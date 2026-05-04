import re

from learning_agent.config import AgentSettings
from learning_agent.resource_templates import compact
from learning_agent.schemas import (
    KnowledgeMatch,
    LearningRiskFlag,
    MasteryRadarItem,
    PortfolioEvidenceItem,
    PortfolioMilestone,
    PortfolioReportRequest,
    PortfolioReportResponse,
    ProfileDimensionUpdate,
)
from learning_agent.vector_store import InMemoryVectorStore


class PortfolioReportAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store

    def build(self, request: PortfolioReportRequest) -> PortfolioReportResponse:
        citations = self.vector_store.search(self._query(request), top_k=max(8, self.settings.retrieval_top_k))
        evidence_items = self._evidence_items(request, citations)
        radar = self._mastery_radar(request, evidence_items)
        risks = self._risk_flags(request, radar, evidence_items, citations)
        milestones = self._milestones(request, risks, radar)
        average_score = round(sum(item.score for item in radar) / max(1, len(radar)))
        executive_summary = (
            f"{request.studentName} 在 `{request.courseTitle}` 的 `{request.topic}` 学习档案已形成。"
            f"综合掌握度 {average_score}/100，证据项 {len(evidence_items)} 条，"
            f"风险提示 {len(risks)} 条，下一阶段建议按 {len(milestones)} 个里程碑推进。"
        )
        return PortfolioReportResponse(
            reportTitle=f"{request.studentName} - {request.topic} 学习档案报告",
            executiveSummary=executive_summary,
            evidenceItems=evidence_items,
            masteryRadar=radar,
            riskFlags=risks,
            nextMilestones=milestones,
            teacherCommentsDraft=self._teacher_comment(request, average_score, risks),
            citations=citations,
            summary=executive_summary,
            profileDimensionUpdates=self._profile_updates(request, average_score, risks, executive_summary),
        )

    def _query(self, request: PortfolioReportRequest) -> str:
        return "\n".join([
            request.courseTitle,
            request.topic,
            request.studentProfileSummary,
            " ".join(request.completedResources),
            " ".join(request.assessmentSummaries),
            " ".join(request.tutoringSummaries),
            " ".join(request.codePracticeSummaries),
            " ".join(request.learningEvents),
            " ".join(request.weaknesses),
            " ".join(request.improvements),
        ])

    def _evidence_items(
        self,
        request: PortfolioReportRequest,
        citations: list[KnowledgeMatch],
    ) -> list[PortfolioEvidenceItem]:
        evidence: list[PortfolioEvidenceItem] = []
        evidence.extend(self._from_list("资源完成", request.completedResources, "completedResources", 0.72))
        evidence.extend(self._from_list("测评表现", request.assessmentSummaries, "assessmentSummaries", 0.78))
        evidence.extend(self._from_list("答疑互动", request.tutoringSummaries, "tutoringSummaries", 0.7))
        evidence.extend(self._from_list("代码实操", request.codePracticeSummaries, "codePracticeSummaries", 0.76))
        evidence.extend(self._from_list("学习行为", request.learningEvents, "learningEvents", 0.66))
        for index, citation in enumerate(citations[:4], start=1):
            evidence.append(PortfolioEvidenceItem(
                category="RAG 依据",
                title=f"课程证据 {index}: {citation.title}",
                evidence=compact(citation.text, 160),
                source=citation.source,
                confidenceScore=min(0.9, max(0.45, citation.score)),
            ))
        if not evidence:
            evidence.append(PortfolioEvidenceItem(
                category="待补充",
                title="缺少学习证据",
                evidence="当前请求未提供测评、答疑、代码练习或资源完成记录。",
                source="portfolio_report_agent",
                confidenceScore=0.35,
            ))
        return evidence[:18]

    def _from_list(
        self,
        category: str,
        values: list[str],
        source: str,
        confidence: float,
    ) -> list[PortfolioEvidenceItem]:
        return [
            PortfolioEvidenceItem(
                category=category,
                title=f"{category} {index}",
                evidence=compact(value, 180),
                source=source,
                confidenceScore=confidence,
            )
            for index, value in enumerate(values[:5], start=1)
            if value.strip()
        ]

    def _mastery_radar(
        self,
        request: PortfolioReportRequest,
        evidence_items: list[PortfolioEvidenceItem],
    ) -> list[MasteryRadarItem]:
        assessment_text = " ".join(request.assessmentSummaries)
        scores = [int(item) for item in re.findall(r"(?<!\d)(\d{1,3})(?:/100|分|%)", assessment_text)]
        normalized_scores = [score for score in scores if 0 <= score <= 100]
        assessment_score = round(sum(normalized_scores) / len(normalized_scores)) if normalized_scores else 62
        resource_score = min(96, 45 + len(request.completedResources) * 10)
        tutoring_score = min(95, 50 + len(request.tutoringSummaries) * 12)
        practice_score = min(94, 46 + len(request.codePracticeSummaries) * 15)
        reflection_hits = sum(1 for item in request.learningEvents if any(key in item for key in ["复盘", "错题", "反思", "总结"]))
        reflection_score = min(92, 50 + reflection_hits * 14 + len(request.improvements) * 5)
        weakness_penalty = min(24, len(request.weaknesses) * 5)
        return [
            MasteryRadarItem(
                dimension="知识掌握",
                score=max(20, assessment_score - weakness_penalty),
                evidence=compact(assessment_text or "暂无测评结果，使用保守估计。", 140),
            ),
            MasteryRadarItem(
                dimension="资源利用",
                score=resource_score,
                evidence=f"完成资源 {len(request.completedResources)} 项。",
            ),
            MasteryRadarItem(
                dimension="主动提问",
                score=tutoring_score,
                evidence=f"答疑互动 {len(request.tutoringSummaries)} 次。",
            ),
            MasteryRadarItem(
                dimension="实操迁移",
                score=practice_score,
                evidence=f"代码/项目练习 {len(request.codePracticeSummaries)} 次。",
            ),
            MasteryRadarItem(
                dimension="复盘能力",
                score=reflection_score,
                evidence=f"学习事件 {len(request.learningEvents)} 条，改进记录 {len(request.improvements)} 条。",
            ),
        ]

    def _risk_flags(
        self,
        request: PortfolioReportRequest,
        radar: list[MasteryRadarItem],
        evidence_items: list[PortfolioEvidenceItem],
        citations: list[KnowledgeMatch],
    ) -> list[LearningRiskFlag]:
        risks: list[LearningRiskFlag] = []
        low_dimensions = [item for item in radar if item.score < 60]
        for item in low_dimensions[:4]:
            risks.append(LearningRiskFlag(
                riskType=f"{item.dimension}不足",
                severity="高" if item.score < 45 else "中",
                evidence=f"{item.dimension} 当前 {item.score}/100。{item.evidence}",
                intervention=f"调用对应 Agent 生成 `{item.dimension}` 补救任务，并在 24 小时内复测。",
            ))
        if request.weaknesses:
            risks.append(LearningRiskFlag(
                riskType="薄弱点集中",
                severity="中",
                evidence=f"薄弱点：{'、'.join(request.weaknesses[:6])}",
                intervention="优先调用先修诊断和资源策展，减少一次性推送过多高阶资源。",
            ))
        if len(evidence_items) < 4 or not citations:
            risks.append(LearningRiskFlag(
                riskType="证据不足",
                severity="中",
                evidence="学习档案缺少足够 RAG 证据或过程记录。",
                intervention="让 Java 后端补齐学习事件、测评尝试、资源使用和引用来源落库。",
            ))
        return risks[:6]

    def _milestones(
        self,
        request: PortfolioReportRequest,
        risks: list[LearningRiskFlag],
        radar: list[MasteryRadarItem],
    ) -> list[PortfolioMilestone]:
        weakest = min(radar, key=lambda item: item.score).dimension if radar else "知识掌握"
        first_agent = "prerequisite_diagnosis_agent" if risks else "resource_curation_agent"
        return [
            PortfolioMilestone(
                day=1,
                title=f"定位 `{weakest}` 的具体缺口",
                successCriteria="完成入口诊断题并生成 2 条画像更新证据。",
                recommendedAgent=first_agent,
            ),
            PortfolioMilestone(
                day=2,
                title=f"围绕 `{request.topic}` 重排资源包",
                successCriteria="完成至少 3 个资源卡，并留下学习笔记或截图。",
                recommendedAgent="resource_curation_agent",
            ),
            PortfolioMilestone(
                day=4,
                title="完成一次实操迁移",
                successCriteria="提交代码/项目练习，批改结果达到 70 分以上。",
                recommendedAgent="code_practice_agent",
            ),
            PortfolioMilestone(
                day=7,
                title="闭环复测与档案刷新",
                successCriteria="复测分数提升或薄弱点数量下降，并生成新学习档案。",
                recommendedAgent="assessment_agent + portfolio_report_agent",
            ),
        ]

    def _teacher_comment(self, request: PortfolioReportRequest, average_score: int, risks: list[LearningRiskFlag]) -> str:
        risk_text = "；".join(item.riskType for item in risks[:3]) if risks else "暂无明显风险"
        return (
            f"{request.studentName} 在 {request.timeRange} 对 `{request.topic}` 的学习已有过程证据。"
            f"当前综合表现约 {average_score}/100，主要风险为：{risk_text}。"
            "建议继续按智能体生成的里程碑推进，并在下一次测评后更新画像。"
        )

    def _profile_updates(
        self,
        request: PortfolioReportRequest,
        average_score: int,
        risks: list[LearningRiskFlag],
        evidence: str,
    ) -> list[ProfileDimensionUpdate]:
        return [
            ProfileDimensionUpdate(
                dimensionKey="LEARNING_PORTFOLIO",
                dimensionName="学习档案",
                value=f"{request.topic} 综合掌握度 {average_score}/100，风险 {len(risks)} 条",
                evidence=evidence,
                confidenceScore=0.79,
                source="portfolio_report_agent",
            )
        ]
