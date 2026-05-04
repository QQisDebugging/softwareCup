import re

from learning_agent.config import AgentSettings
from learning_agent.resource_templates import compact
from learning_agent.schemas import (
    AgentCallRecommendation,
    KnowledgeMatch,
    LearningEventAnalysisRequest,
    LearningEventAnalysisResponse,
    LearningRiskSignal,
    ProfileDimensionUpdate,
)
from learning_agent.vector_store import InMemoryVectorStore


class LearningEventAnalysisAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store

    def analyze(self, request: LearningEventAnalysisRequest) -> LearningEventAnalysisResponse:
        citations = self.vector_store.search(self._query(request), top_k=self.settings.retrieval_top_k)
        engagement = self._engagement_score(request)
        trend = self._mastery_trend(request)
        risks = self._risk_signals(request, engagement, trend)
        calls = self._agent_calls(request, risks, trend)
        actions = self._next_actions(request, risks, calls)
        summary = (
            f"{request.timeRange} `{request.targetTopic}` 学习事件分析完成："
            f"参与度 {engagement}/100，趋势 `{trend}`，风险 {len(risks)} 条。"
        )
        return LearningEventAnalysisResponse(
            engagementScore=engagement,
            masteryTrend=trend,
            riskSignals=risks,
            nextActions=actions,
            recommendedAgentCalls=calls,
            profileDimensionUpdates=self._profile_updates(request, engagement, trend, risks, summary),
            citations=citations,
            summary=summary,
        )

    def _query(self, request: LearningEventAnalysisRequest) -> str:
        return "\n".join([
            request.courseTitle,
            request.targetTopic,
            request.studentProfileSummary,
            *request.learningEvents,
            *request.resourceUsage,
            *request.assessmentSummaries,
            *request.tutoringSummaries,
            *request.codePracticeSummaries,
        ])

    def _engagement_score(self, request: LearningEventAnalysisRequest) -> int:
        score = 35
        score += min(20, len(request.learningEvents) * 4)
        score += min(18, len(request.resourceUsage) * 6)
        score += min(16, len(request.tutoringSummaries) * 8)
        score += min(16, len(request.codePracticeSummaries) * 8)
        if any("复盘" in item or "总结" in item for item in request.learningEvents):
            score += 8
        return min(96, score)

    def _mastery_trend(self, request: LearningEventAnalysisRequest) -> str:
        text = " ".join(request.assessmentSummaries)
        scores = [int(item) for item in re.findall(r"(?<!\d)(\d{1,3})(?:/100|分|%)", text) if 0 <= int(item) <= 100]
        if len(scores) >= 2:
            delta = scores[-1] - scores[0]
            if delta >= 10:
                return "明显提升"
            if delta >= 3:
                return "小幅提升"
            if delta <= -8:
                return "下降"
            return "基本稳定"
        if scores and scores[-1] >= 75:
            return "当前较稳"
        if scores and scores[-1] < 60:
            return "需要补救"
        return "证据不足"

    def _risk_signals(
        self,
        request: LearningEventAnalysisRequest,
        engagement: int,
        trend: str,
    ) -> list[LearningRiskSignal]:
        risks: list[LearningRiskSignal] = []
        if engagement < 55:
            risks.append(LearningRiskSignal(
                riskType="参与度不足",
                severity="高",
                evidence=f"事件数量偏少，参与度 {engagement}/100。",
                recommendedAgent="/agents/resources/curate",
            ))
        if trend in {"下降", "需要补救"}:
            risks.append(LearningRiskSignal(
                riskType="掌握度风险",
                severity="高" if trend == "下降" else "中",
                evidence=f"测评趋势：{trend}。{compact(' '.join(request.assessmentSummaries), 160)}",
                recommendedAgent="/agents/prerequisite/diagnose",
            ))
        if not request.tutoringSummaries:
            risks.append(LearningRiskSignal(
                riskType="缺少主动提问",
                severity="中",
                evidence="当前周期没有答疑记录，可能只是被动刷资源。",
                recommendedAgent="/agents/tutoring",
            ))
        if not request.codePracticeSummaries and any(keyword in request.targetTopic for keyword in ["代码", "Spring", "REST", "算法"]):
            risks.append(LearningRiskSignal(
                riskType="实操不足",
                severity="中",
                evidence="目标主题需要实践验证，但没有代码/项目练习记录。",
                recommendedAgent="/agents/code/practice/generate",
            ))
        if any("重复错" in item or "同一错误" in item for item in request.learningEvents + request.assessmentSummaries):
            risks.append(LearningRiskSignal(
                riskType="错因固化",
                severity="高",
                evidence="学习记录出现重复错误描述。",
                recommendedAgent="/agents/report/portfolio",
            ))
        return risks[:6]

    def _agent_calls(
        self,
        request: LearningEventAnalysisRequest,
        risks: list[LearningRiskSignal],
        trend: str,
    ) -> list[AgentCallRecommendation]:
        calls: list[AgentCallRecommendation] = []
        for index, risk in enumerate(risks[:4], start=1):
            calls.append(AgentCallRecommendation(
                priority=index,
                agentEndpoint=risk.recommendedAgent,
                reason=f"处理风险 `{risk.riskType}`：{risk.evidence}",
                payloadHint={
                    "studentProfileId": request.studentProfileId,
                    "courseId": request.courseId,
                    "topic": request.targetTopic,
                },
            ))
        calls.append(AgentCallRecommendation(
            priority=len(calls) + 1,
            agentEndpoint="/agents/report/portfolio",
            reason=f"将 `{trend}` 趋势、风险和下一步动作沉淀为学习档案。",
            payloadHint={"timeRange": request.timeRange, "targetTopic": request.targetTopic},
        ))
        return calls[:5]

    def _next_actions(
        self,
        request: LearningEventAnalysisRequest,
        risks: list[LearningRiskSignal],
        calls: list[AgentCallRecommendation],
    ) -> list[str]:
        actions = [
            f"围绕 `{request.targetTopic}` 选择优先级最高的 Agent 调用：{calls[0].agentEndpoint if calls else '/agents/resources/curate'}。",
            "把本轮分析结果写入学习事件，下一次测评后重新分析趋势。",
        ]
        actions.extend(f"{risk.riskType}：{risk.recommendedAgent}" for risk in risks[:3])
        return actions[:6]

    def _profile_updates(
        self,
        request: LearningEventAnalysisRequest,
        engagement: int,
        trend: str,
        risks: list[LearningRiskSignal],
        evidence: str,
    ) -> list[ProfileDimensionUpdate]:
        return [
            ProfileDimensionUpdate(
                dimensionKey="LEARNING_ENGAGEMENT",
                dimensionName="学习参与度",
                value=f"{request.timeRange} 参与度 {engagement}/100，趋势 {trend}",
                evidence=evidence,
                confidenceScore=0.77,
                source="learning_event_analysis_agent",
            ),
            ProfileDimensionUpdate(
                dimensionKey="LEARNING_RISK",
                dimensionName="学习风险",
                value="、".join(risk.riskType for risk in risks) if risks else "暂无明显风险",
                evidence=evidence,
                confidenceScore=0.74,
                source="learning_event_analysis_agent",
            ),
        ]
