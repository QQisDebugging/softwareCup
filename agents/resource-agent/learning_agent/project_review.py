import re

from learning_agent.config import AgentSettings
from learning_agent.resource_templates import compact
from learning_agent.schemas import (
    KnowledgeMatch,
    ProfileDimensionUpdate,
    ProjectArchitectureIssue,
    ProjectFileInput,
    ProjectKnowledgeMapping,
    ProjectRefactorTask,
    ProjectReviewRequest,
    ProjectReviewResponse,
    ProjectTestGap,
)
from learning_agent.vector_store import InMemoryVectorStore


class ProjectReviewAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store

    def review(self, request: ProjectReviewRequest) -> ProjectReviewResponse:
        citations = self.vector_store.search(self._query(request), top_k=max(8, self.settings.retrieval_top_k))
        issues = self._architecture_issues(request.files)
        test_gaps = self._test_gaps(request.files, issues)
        security_notes = self._security_notes(request.files)
        mapping = self._knowledge_mapping(request, issues, test_gaps)
        tasks = self._refactor_tasks(issues, test_gaps, security_notes)
        score = self._score(issues, test_gaps, security_notes)
        summary = (
            f"`{request.projectTitle}` 项目级审查完成：工程质量 {score}/100，"
            f"发现 {len(issues)} 个结构/实现问题、{len(test_gaps)} 个测试缺口、"
            f"{len(security_notes)} 条安全提示。"
        )
        return ProjectReviewResponse(
            overallScore=score,
            architectureIssues=issues,
            testGaps=test_gaps,
            securityNotes=security_notes,
            knowledgeMapping=mapping,
            refactorTasks=tasks,
            citations=citations,
            summary=summary,
            profileDimensionUpdates=self._profile_updates(request, score, issues, test_gaps, summary),
        )

    def _query(self, request: ProjectReviewRequest) -> str:
        code_summary = "\n".join(f"{item.path}\n{compact(item.content, 600)}" for item in request.files[:8])
        return "\n".join([
            request.courseTitle,
            request.projectTitle,
            request.targetTopic,
            request.studentProfileSummary,
            " ".join(request.reviewFocus),
            code_summary,
            "代码审查 分层 Controller Service Repository 测试 安全",
        ])

    def _architecture_issues(self, files: list[ProjectFileInput]) -> list[ProjectArchitectureIssue]:
        issues: list[ProjectArchitectureIssue] = []
        for file in files:
            content = file.content
            lower_path = file.path.lower()
            controller_like = "controller" in lower_path or "@RestController" in content or "@Controller" in content
            if controller_like and re.search(r"\b\w*Repository\b|\.save\(|\.findBy|\.delete", content):
                issues.append(self._issue(
                    "分层职责",
                    file,
                    "Controller 直接访问 Repository 或数据操作",
                    "高",
                    "Controller 层出现 Repository 调用或持久化方法。",
                    "把业务规则和数据访问下沉到 Service，Controller 只负责请求响应和 DTO 转换。",
                    "Controller/Service/Repository 职责边界",
                ))
            if controller_like and self._method_complexity(content) >= 4:
                issues.append(self._issue(
                    "业务逻辑下沉",
                    file,
                    "Controller 方法分支过多",
                    "中",
                    "Controller 中出现较多 if/for/while/switch 分支。",
                    "将校验、业务规则和状态流转提取到 Service，并补充单元测试。",
                    "业务逻辑分层",
                ))
            if re.search(r"catch\s*\([^)]*\)\s*\{\s*(e\.printStackTrace\(\);)?\s*\}", content, flags=re.S):
                issues.append(self._issue(
                    "异常处理",
                    file,
                    "空 catch 或仅打印堆栈",
                    "中",
                    "异常被吞掉或只调用 printStackTrace。",
                    "返回明确错误响应，记录结构化日志，并让调用方能感知失败原因。",
                    "异常响应与可观测性",
                ))
            if re.search(r"SELECT\s+.*\+|WHERE\s+.*\+", content, flags=re.I | re.S):
                issues.append(self._issue(
                    "数据访问安全",
                    file,
                    "SQL 字符串拼接",
                    "高",
                    "SQL 片段和变量直接拼接。",
                    "使用参数化查询、Repository 方法或 ORM 条件构造，避免注入风险。",
                    "SQL 注入防护",
                ))
            if re.search(r"TODO|FIXME|临时|随便", content, flags=re.I):
                issues.append(self._issue(
                    "代码完成度",
                    file,
                    "遗留 TODO/FIXME",
                    "低",
                    "代码中仍有未完成标记。",
                    "把 TODO 转为明确任务，补齐验收标准后再提交。",
                    "工程交付规范",
                ))
        return issues[:12]

    def _issue(
        self,
        category: str,
        file: ProjectFileInput,
        line_hint: str,
        severity: str,
        evidence: str,
        suggestion: str,
        knowledge_point: str,
    ) -> ProjectArchitectureIssue:
        return ProjectArchitectureIssue(
            category=category,
            path=file.path,
            lineHint=line_hint,
            severity=severity,
            evidence=evidence,
            suggestion=suggestion,
            knowledgePoint=knowledge_point,
        )

    def _method_complexity(self, content: str) -> int:
        return len(re.findall(r"\b(if|for|while|switch|catch)\b", content))

    def _test_gaps(self, files: list[ProjectFileInput], issues: list[ProjectArchitectureIssue]) -> list[ProjectTestGap]:
        test_files = [file for file in files if "test" in file.path.lower() or "@Test" in file.content]
        gaps: list[ProjectTestGap] = []
        if not test_files:
            gaps.append(ProjectTestGap(
                target="项目测试基线",
                reason="未发现测试文件或 @Test 标记。",
                suggestedTest="至少补充 Controller 接口测试、Service 单元测试和异常场景测试各 1 个。",
            ))
        issue_points = {issue.knowledgePoint for issue in issues}
        if "Controller/Service/Repository 职责边界" in issue_points:
            gaps.append(ProjectTestGap(
                target="分层调用链",
                reason="存在 Controller 直接访问 Repository 的结构问题。",
                suggestedTest="构造 Mock Repository，验证 Controller 只调用 Service，不直接访问数据层。",
            ))
        if "异常响应与可观测性" in issue_points:
            gaps.append(ProjectTestGap(
                target="异常响应",
                reason="存在异常吞掉或只打印堆栈的问题。",
                suggestedTest="提交非法参数，断言 HTTP 状态码、错误码和错误消息符合接口契约。",
            ))
        if "SQL 注入防护" in issue_points:
            gaps.append(ProjectTestGap(
                target="数据访问安全",
                reason="存在 SQL 字符串拼接。",
                suggestedTest="用包含引号和条件拼接的输入验证查询不会改变语义。",
            ))
        return gaps[:8]

    def _security_notes(self, files: list[ProjectFileInput]) -> list[str]:
        notes: list[str] = []
        for file in files:
            if re.search(r"(api[_-]?key|secret|token|password)\s*=\s*['\"][^'\"]{6,}", file.content, flags=re.I):
                notes.append(f"{file.path}: 发现疑似硬编码密钥或密码，必须改为环境变量/配置中心。")
            if re.search(r"@CrossOrigin\s*\(\s*origins\s*=\s*['\"]\*['\"]", file.content):
                notes.append(f"{file.path}: CORS 放开到 *，演示环境可用，生产需要限制域名。")
            if "System.out.println" in file.content:
                notes.append(f"{file.path}: 使用 System.out.println 输出运行信息，建议改为结构化日志。")
        if not notes:
            notes.append("未发现明显硬编码密钥、开放 CORS 或控制台日志风险。")
        return notes[:8]

    def _knowledge_mapping(
        self,
        request: ProjectReviewRequest,
        issues: list[ProjectArchitectureIssue],
        test_gaps: list[ProjectTestGap],
    ) -> list[ProjectKnowledgeMapping]:
        points = list(dict.fromkeys([issue.knowledgePoint for issue in issues]))
        if test_gaps:
            points.append("测试设计与质量保障")
        if not points:
            points = [request.targetTopic, "工程交付规范"]
        return [
            ProjectKnowledgeMapping(
                knowledgePoint=point,
                evidence=self._mapping_evidence(point, issues, test_gaps),
                masterySignal="需要补救" if any(issue.knowledgePoint == point and issue.severity == "高" for issue in issues) else "可巩固提升",
            )
            for point in list(dict.fromkeys(points))[:8]
        ]

    def _mapping_evidence(
        self,
        point: str,
        issues: list[ProjectArchitectureIssue],
        test_gaps: list[ProjectTestGap],
    ) -> str:
        matched = [issue for issue in issues if issue.knowledgePoint == point]
        if matched:
            return "；".join(f"{issue.path}: {issue.lineHint}" for issue in matched[:3])
        if point == "测试设计与质量保障" and test_gaps:
            return "；".join(gap.target for gap in test_gaps[:3])
        return "未发现严重问题，建议用变式任务继续验证。"

    def _refactor_tasks(
        self,
        issues: list[ProjectArchitectureIssue],
        test_gaps: list[ProjectTestGap],
        security_notes: list[str],
    ) -> list[ProjectRefactorTask]:
        tasks: list[ProjectRefactorTask] = []
        for index, issue in enumerate(issues[:5], start=1):
            tasks.append(ProjectRefactorTask(
                priority=index,
                title=f"修复 {issue.category}: {issue.lineHint}",
                action=issue.suggestion,
                estimatedMinutes=25 if issue.severity == "高" else 15,
                relatedFiles=[issue.path],
            ))
        if test_gaps:
            tasks.append(ProjectRefactorTask(
                priority=len(tasks) + 1,
                title="补齐项目测试基线",
                action="按测试缺口补充接口、Service、异常和安全场景测试。",
                estimatedMinutes=35,
                relatedFiles=[],
            ))
        if security_notes and "未发现明显" not in security_notes[0]:
            tasks.append(ProjectRefactorTask(
                priority=len(tasks) + 1,
                title="处理安全配置风险",
                action="移除硬编码敏感信息，收紧 CORS，替换控制台日志。",
                estimatedMinutes=20,
                relatedFiles=[],
            ))
        return tasks[:8]

    def _score(
        self,
        issues: list[ProjectArchitectureIssue],
        test_gaps: list[ProjectTestGap],
        security_notes: list[str],
    ) -> int:
        penalty = 0
        severity_penalty = {"高": 18, "中": 10, "低": 5}
        penalty += sum(severity_penalty.get(issue.severity, 8) for issue in issues)
        penalty += len(test_gaps) * 7
        if security_notes and "未发现明显" not in security_notes[0]:
            penalty += min(18, len(security_notes) * 6)
        return max(20, min(96, 100 - penalty))

    def _profile_updates(
        self,
        request: ProjectReviewRequest,
        score: int,
        issues: list[ProjectArchitectureIssue],
        test_gaps: list[ProjectTestGap],
        evidence: str,
    ) -> list[ProfileDimensionUpdate]:
        weak_points = list(dict.fromkeys([issue.knowledgePoint for issue in issues]))
        if test_gaps:
            weak_points.append("测试设计与质量保障")
        return [
            ProfileDimensionUpdate(
                dimensionKey="PROJECT_ENGINEERING_QUALITY",
                dimensionName="项目工程质量",
                value=f"{request.projectTitle}: {score}/100",
                evidence=evidence,
                confidenceScore=0.8,
                source="project_review_agent",
            ),
            ProfileDimensionUpdate(
                dimensionKey="CODE_REVIEW_WEAKNESS",
                dimensionName="代码审查薄弱点",
                value="、".join(weak_points[:6]) if weak_points else "暂无明显项目级薄弱点",
                evidence=evidence,
                confidenceScore=0.76,
                source="project_review_agent",
            ),
        ]
