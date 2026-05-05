from collections import defaultdict

from learning_agent.config import AgentSettings
from learning_agent.resource_templates import compact
from learning_agent.schemas import (
    AssessmentAttemptRecord,
    AssessmentItemAnalysisRequest,
    AssessmentItemAnalysisResponse,
    HardItem,
    KnowledgeMatch,
    KnowledgePointMastery,
    MisconceptionCluster,
)
from learning_agent.vector_store import InMemoryVectorStore


class AssessmentItemAnalysisAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store

    def analyze(self, request: AssessmentItemAnalysisRequest) -> AssessmentItemAnalysisResponse:
        citations = self.vector_store.search(self._query(request), top_k=self.settings.retrieval_top_k)
        mastery = self._mastery(request.attempts)
        hard_items = self._hard_items(request.attempts)
        clusters = self._clusters(request.attempts, mastery)
        plan = self._remediation_plan(request, mastery, hard_items, clusters)
        summary = (
            f"`{request.topic}` 题目分析完成：覆盖 {len(mastery)} 个知识点，"
            f"发现 {len(hard_items)} 个高错题和 {len(clusters)} 类误区。"
        )
        return AssessmentItemAnalysisResponse(
            topic=request.topic,
            knowledgePointMastery=mastery,
            hardItems=hard_items,
            misconceptionClusters=clusters,
            remediationPlan=plan,
            citations=citations,
            summary=summary,
        )

    def _query(self, request: AssessmentItemAnalysisRequest) -> str:
        attempt_text = "\n".join(
            f"{item.knowledgePoint} {item.questionType} {item.feedback} {item.answerSummary}"
            for item in request.attempts
        )
        return "\n".join([request.courseTitle, request.topic, attempt_text])

    def _mastery(self, attempts: list[AssessmentAttemptRecord]) -> list[KnowledgePointMastery]:
        grouped: dict[str, list[AssessmentAttemptRecord]] = defaultdict(list)
        for attempt in attempts:
            grouped[attempt.knowledgePoint or "未标注知识点"].append(attempt)
        result: list[KnowledgePointMastery] = []
        for point, records in grouped.items():
            score = sum(item.score for item in records)
            max_score = sum(item.maxScore for item in records) or 1
            accuracy = round(score / max_score, 2)
            result.append(KnowledgePointMastery(
                knowledgePoint=point,
                accuracy=accuracy,
                attempts=len(records),
                masteryLevel=self._level(accuracy),
            ))
        result.sort(key=lambda item: item.accuracy)
        return result[:12]

    def _level(self, accuracy: float) -> str:
        if accuracy >= 0.85:
            return "掌握稳定"
        if accuracy >= 0.65:
            return "基本掌握"
        if accuracy >= 0.45:
            return "部分掌握"
        return "需要补救"

    def _hard_items(self, attempts: list[AssessmentAttemptRecord]) -> list[HardItem]:
        hard: list[HardItem] = []
        for attempt in attempts:
            wrong_rate = 1 - (attempt.score / max(1, attempt.maxScore))
            if wrong_rate >= 0.35 or not attempt.correct:
                hard.append(HardItem(
                    questionId=attempt.questionId,
                    knowledgePoint=attempt.knowledgePoint,
                    wrongRate=round(min(1.0, wrong_rate), 2),
                    reason=compact(attempt.feedback or attempt.answerSummary or "得分偏低，需要教师复核题目与知识点映射。", 140),
                ))
        hard.sort(key=lambda item: item.wrongRate, reverse=True)
        return hard[:8]

    def _clusters(
        self,
        attempts: list[AssessmentAttemptRecord],
        mastery: list[KnowledgePointMastery],
    ) -> list[MisconceptionCluster]:
        text = " ".join([attempt.feedback + " " + attempt.answerSummary for attempt in attempts])
        clusters: list[MisconceptionCluster] = []
        if any(keyword in text for keyword in ["分层", "Controller", "Service", "Repository"]):
            clusters.append(MisconceptionCluster(
                name="工程分层职责混淆",
                knowledgePoints=[item.knowledgePoint for item in mastery if "分层" in item.knowledgePoint or "Controller" in item.knowledgePoint][:4],
                evidence=compact(text, 180),
                remediation="生成分层调用链图、反例改错题和一个 Controller -> Service -> Repository 最小项目。",
            ))
        if any(keyword in text for keyword in ["状态码", "HTTP", "REST", "接口"]):
            clusters.append(MisconceptionCluster(
                name="接口契约理解不稳",
                knowledgePoints=[item.knowledgePoint for item in mastery if any(key in item.knowledgePoint for key in ["HTTP", "REST", "接口"])][:4],
                evidence=compact(text, 180),
                remediation="补充 HTTP 状态码、请求响应、DTO 和异常响应的入口诊断题。",
            ))
        weak_points = [item.knowledgePoint for item in mastery if item.accuracy < 0.55]
        if weak_points and not clusters:
            clusters.append(MisconceptionCluster(
                name="低掌握知识点集中",
                knowledgePoints=weak_points[:4],
                evidence=f"低掌握知识点：{'、'.join(weak_points[:4])}",
                remediation="先调用资源策展生成基础补救资源，再进行闭环复测。",
            ))
        return clusters[:5]

    def _remediation_plan(
        self,
        request: AssessmentItemAnalysisRequest,
        mastery: list[KnowledgePointMastery],
        hard_items: list[HardItem],
        clusters: list[MisconceptionCluster],
    ) -> list[str]:
        weak = [item.knowledgePoint for item in mastery if item.accuracy < 0.65]
        plan = [
            f"针对 `{point}` 调用 `/agents/resources/curate` 生成补救资源包。"
            for point in weak[:4]
        ]
        if hard_items:
            plan.append("把高错题改写为同知识点的变式题，避免学生只记住答案。")
        if clusters:
            plan.append(f"围绕 `{clusters[0].name}` 生成一次 10 分钟微课和 3 道入口题。")
        plan.append(f"完成 `{request.topic}` 复测后再次运行本接口，比较知识点正确率变化。")
        return plan[:6]
