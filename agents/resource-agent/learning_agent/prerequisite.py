from learning_agent.config import AgentSettings
from learning_agent.resource_templates import compact
from learning_agent.schemas import (
    DiagnosticQuestion,
    KnowledgeMatch,
    PrerequisiteDiagnosisRequest,
    PrerequisiteDiagnosisResponse,
    PrerequisiteItem,
    ProfileDimensionUpdate,
)
from learning_agent.vector_store import InMemoryVectorStore


class PrerequisiteDiagnosisAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store

    def diagnose(self, request: PrerequisiteDiagnosisRequest) -> PrerequisiteDiagnosisResponse:
        citations = self.vector_store.search(self._query(request), top_k=max(8, self.settings.retrieval_top_k))
        prerequisites = self._prerequisites(request, citations)
        readiness_score = self._readiness_score(prerequisites)
        readiness_level = self._readiness_level(readiness_score)
        gaps = [item.name for item in prerequisites if item.status in {"未掌握", "部分掌握", "待诊断"}]
        gap_summary = (
            f"`{request.targetTopic}` 学习入口诊断完成：准备度 {readiness_score}/100。"
            f"优先补齐：{'、'.join(gaps[:4]) if gaps else '暂无明显先修缺口'}。"
        )
        return PrerequisiteDiagnosisResponse(
            targetTopic=request.targetTopic,
            readinessScore=readiness_score,
            readinessLevel=readiness_level,
            prerequisites=prerequisites,
            diagnosticQuestions=self._diagnostic_questions(request, prerequisites),
            gapSummary=gap_summary,
            recommendedWarmups=self._warmups(request, gaps),
            citations=citations,
            profileDimensionUpdates=self._profile_updates(request, readiness_level, gaps, gap_summary),
        )

    def _query(self, request: PrerequisiteDiagnosisRequest) -> str:
        return "\n".join([
            request.courseTitle,
            request.targetTopic,
            request.studentProfileSummary,
            " ".join(request.completedTopics),
            " ".join(request.assessmentWeaknesses),
            "先修 知识 基础 prerequisite dependency",
        ])

    def _prerequisites(
        self,
        request: PrerequisiteDiagnosisRequest,
        citations: list[KnowledgeMatch],
    ) -> list[PrerequisiteItem]:
        names = self._candidate_names(request, citations)
        completed = " ".join(request.completedTopics).lower()
        weaknesses = " ".join(request.assessmentWeaknesses + [request.studentProfileSummary]).lower()
        result: list[PrerequisiteItem] = []
        for index, name in enumerate(names[:8]):
            normalized = name.lower()
            if normalized and normalized in completed:
                status = "已掌握"
            elif any(token and token in weaknesses for token in self._tokens(name)):
                status = "未掌握" if index < 4 else "部分掌握"
            elif any(keyword in weaknesses for keyword in ["基础弱", "较弱", "不熟", "weak", "beginner"]):
                status = "部分掌握" if index < 5 else "待诊断"
            elif index < 2:
                status = "部分掌握"
            else:
                status = "待诊断"
            citation = citations[index % len(citations)] if citations else None
            evidence = compact(citation.text, 120) if citation else f"根据 `{request.targetTopic}` 的常见课程依赖推断。"
            result.append(PrerequisiteItem(
                name=name,
                status=status,
                importance=round(max(0.45, 0.95 - index * 0.07), 2),
                evidence=evidence,
                remediationAction=self._remediation(name, status),
            ))
        return result

    def _candidate_names(self, request: PrerequisiteDiagnosisRequest, citations: list[KnowledgeMatch]) -> list[str]:
        text = "\n".join([request.courseTitle, request.targetTopic, *(item.text for item in citations)])
        candidates: list[str] = []
        rules = [
            ("Spring" in text or "Controller" in text or "REST" in text, ["HTTP 请求响应", "Java 面向对象基础", "MVC 分层职责", "JSON 与 REST 规范", "数据库访问基础", "接口调试与异常处理"]),
            ("SQL" in text or "数据库" in text, ["关系模型", "SQL 基础查询", "表结构设计", "事务与约束", "索引与性能", "数据安全边界"]),
            ("算法" in text or "数据结构" in text, ["复杂度分析", "数组与链表", "递归与迭代", "排序查找", "调试边界条件", "题解表达"]),
            ("大模型" in text or "RAG" in text or "Embedding" in text, ["向量检索", "Prompt 结构", "引用证据", "内容安全", "评测闭环", "服务接口调用"]),
        ]
        for matched, names in rules:
            if matched:
                candidates.extend(names)
        candidates.extend([
            "课程核心术语",
            "先修概念边界",
            "最小案例复现",
            "错因复盘表达",
        ])
        return list(dict.fromkeys(candidates))

    def _tokens(self, name: str) -> list[str]:
        return [token.lower() for token in name.replace("与", " ").replace("/", " ").split() if len(token) >= 2]

    def _remediation(self, name: str, status: str) -> str:
        if status == "已掌握":
            return f"保留 `{name}` 作为复习检查点，直接进入迁移题。"
        if status == "部分掌握":
            return f"用 10 分钟图解复习 `{name}`，再完成 1 道判断题和 1 道简答题。"
        if status == "未掌握":
            return f"先生成 `{name}` 基础讲解文档和错题复盘卡，不建议直接进入项目实操。"
        return f"用入口诊断题确认 `{name}` 是否需要补救。"

    def _readiness_score(self, prerequisites: list[PrerequisiteItem]) -> int:
        weights = {"已掌握": 1.0, "部分掌握": 0.66, "待诊断": 0.48, "未掌握": 0.25}
        if not prerequisites:
            return 60
        score = sum(item.importance * weights[item.status] for item in prerequisites)
        total = sum(item.importance for item in prerequisites)
        return min(96, max(25, round(score / max(total, 1) * 100)))

    def _readiness_level(self, score: int) -> str:
        if score >= 82:
            return "可直接进入新课"
        if score >= 65:
            return "边学边补"
        if score >= 45:
            return "需要先修补救"
        return "暂缓新课，先做基础重建"

    def _diagnostic_questions(
        self,
        request: PrerequisiteDiagnosisRequest,
        prerequisites: list[PrerequisiteItem],
    ) -> list[DiagnosticQuestion]:
        questions: list[DiagnosticQuestion] = []
        for index, item in enumerate(prerequisites[:6], start=1):
            qtype = "简答题" if index % 2 else "判断题"
            question = (
                f"请用自己的话说明 `{item.name}` 与 `{request.targetTopic}` 的关系，并给出一个项目例子。"
                if qtype == "简答题"
                else f"`{request.targetTopic}` 可以不理解 `{item.name}` 就直接做项目实操。请判断并说明理由。"
            )
            expected = (
                f"能够说明 `{item.name}` 是学习 `{request.targetTopic}` 的前置支撑，并能映射到具体场景。"
                if qtype == "简答题"
                else "错误。需要先理解前置概念，否则实操容易只会照抄。"
            )
            questions.append(DiagnosticQuestion(
                id=f"preq{index}",
                prerequisite=item.name,
                question=question,
                expectedAnswer=expected,
                questionType=qtype,
                score=10,
            ))
        return questions

    def _warmups(self, request: PrerequisiteDiagnosisRequest, gaps: list[str]) -> list[str]:
        selected = gaps[:5] or [request.targetTopic]
        warmups = [
            f"生成 `{name}` 5 分钟微课卡：定义、反例、项目位置各 1 条。"
            for name in selected
        ]
        warmups.append(f"做一次 `{request.targetTopic}` 入口小测，错题自动写回画像。")
        return warmups

    def _profile_updates(
        self,
        request: PrerequisiteDiagnosisRequest,
        readiness_level: str,
        gaps: list[str],
        evidence: str,
    ) -> list[ProfileDimensionUpdate]:
        return [
            ProfileDimensionUpdate(
                dimensionKey="PREREQUISITE_READINESS",
                dimensionName="先修准备度",
                value=f"{request.targetTopic}：{readiness_level}",
                evidence=evidence,
                confidenceScore=0.76,
                source="prerequisite_diagnosis_agent",
            ),
            ProfileDimensionUpdate(
                dimensionKey="PREREQUISITE_GAPS",
                dimensionName="先修缺口",
                value="、".join(gaps[:6]) if gaps else "暂无明显先修缺口",
                evidence=evidence,
                confidenceScore=0.72,
                source="prerequisite_diagnosis_agent",
            ),
        ]
