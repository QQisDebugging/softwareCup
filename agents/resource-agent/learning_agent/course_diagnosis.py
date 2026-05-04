import re

from learning_agent.config import AgentSettings
from learning_agent.resource_templates import compact
from learning_agent.schemas import (
    AssessmentBlueprintItem,
    CourseDiagnosisRequest,
    CourseDiagnosisResponse,
    KnowledgeMatch,
)
from learning_agent.vector_store import InMemoryVectorStore


class CourseDiagnosisAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store

    def diagnose(self, request: CourseDiagnosisRequest) -> CourseDiagnosisResponse:
        citations = self.vector_store.search(self._query(request), top_k=max(8, self.settings.retrieval_top_k))
        covered = self._covered_points(request, citations)
        missing = self._missing_points(covered)
        missing_types = self._missing_resource_types(citations)
        coverage_score = min(96, max(35, 55 + len(covered) * 4 - len(missing) * 3 - len(missing_types) * 2))
        return CourseDiagnosisResponse(
            courseId=request.courseId,
            courseTitle=request.courseTitle,
            coverageScore=coverage_score,
            coveredKnowledgePoints=covered,
            missingKnowledgePoints=missing,
            missingResourceTypes=missing_types,
            assessmentBlueprint=self._blueprint(covered, missing),
            recommendedTasks=self._tasks(missing, missing_types),
            citations=citations,
            summary=f"`{request.courseTitle}` 课程诊断完成：覆盖度 {coverage_score}/100，建议补齐 {len(missing)} 个知识点和 {len(missing_types)} 类资源。",
        )

    def _query(self, request: CourseDiagnosisRequest) -> str:
        return "\n".join([
            request.courseTitle,
            request.courseDescription,
            request.syllabusText,
            request.targetStudentProfile,
        ])

    def _covered_points(self, request: CourseDiagnosisRequest, citations: list[KnowledgeMatch]) -> list[str]:
        text = "\n".join([request.courseTitle, request.courseDescription, request.syllabusText, *(item.text for item in citations)])
        points: list[str] = []
        for pattern in [
            r"weeks\.topic:\s*([^\n]+)",
            r"topic:\s*([^\n]+)",
            r"([\u4e00-\u9fa5A-Za-z0-9 ]{2,24}(?:基础|结构|设计|建模|迁移|上传|任务|画像|路径|测评|答疑|部署))",
        ]:
            for match in re.findall(pattern, text):
                point = " ".join(str(match).split()).strip("：:;；,.，。")
                if 2 <= len(point) <= 36:
                    points.append(point)
        defaults = ["课程导论", "HTTP 基础", "REST API 设计", "数据库建模", "学习画像", "智能辅导", "学习效果评估"]
        points.extend(defaults)
        return list(dict.fromkeys(points))[:14]

    def _missing_points(self, covered: list[str]) -> list[str]:
        required = ["先修知识诊断", "知识图谱", "代码实操", "错题复盘", "多模态脚本", "闭环复测"]
        covered_text = " ".join(covered)
        return [item for item in required if item not in covered_text]

    def _missing_resource_types(self, citations: list[KnowledgeMatch]) -> list[str]:
        text = "\n".join(item.text for item in citations)
        required = ["讲解文档", "知识点思维导图", "练习题", "实操案例", "短视频脚本", "拓展阅读"]
        return [item for item in required if item not in text]

    def _blueprint(self, covered: list[str], missing: list[str]) -> list[AssessmentBlueprintItem]:
        points = (covered[:4] + missing[:3]) or ["课程核心概念"]
        return [
            AssessmentBlueprintItem(
                knowledgePoint=point,
                questionTypes=["选择题", "判断题"] if index < 2 else ["简答题", "代码纠错题"],
                suggestedCount=4 if index < 2 else 3,
                reason="覆盖课程基础诊断、迁移表达和实操验证。",
            )
            for index, point in enumerate(points[:6])
        ]

    def _tasks(self, missing: list[str], missing_types: list[str]) -> list[str]:
        tasks = [f"补充 `{item}` 教学节点，并为其添加引用依据。" for item in missing[:4]]
        tasks.extend(f"新增 `{item}` 资源模板，接入资源生成 Agent。" for item in missing_types[:4])
        tasks.append("用一次测评批改结果反向验证课程建设是否真的覆盖薄弱点。")
        return tasks
