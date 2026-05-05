from uuid import uuid4

from learning_agent.config import AgentSettings
from learning_agent.resource_templates import compact
from learning_agent.schemas import (
    AgentQualityGate,
    AgentTraceRequest,
    AgentTraceResponse,
    AgentTraceStep,
)


class AgentTraceAgent:
    def __init__(self, settings: AgentSettings) -> None:
        self.settings = settings

    def explain(self, request: AgentTraceRequest) -> AgentTraceResponse:
        trace_id = request.traceId or f"trace-{uuid4().hex[:12]}"
        agents = request.involvedAgents or self._default_agents(request.taskName)
        steps = self._steps(request, agents)
        gates = self._quality_gates(request, steps)
        reproducibility = self._reproducibility_notes(request)
        summary = (
            f"`{request.taskName}` 调用链已生成可解释追踪：{len(steps)} 个步骤、"
            f"{len(gates)} 个质量门禁、{len(request.fallbackEvents)} 个降级事件。"
        )
        return AgentTraceResponse(
            traceId=trace_id,
            taskName=request.taskName,
            traceSteps=steps,
            qualityGates=gates,
            fallbackEvents=request.fallbackEvents or ["未记录模型降级或工具失败。"],
            reproducibilityNotes=reproducibility,
            summary=summary,
        )

    def _default_agents(self, task_name: str) -> list[str]:
        text = task_name.lower()
        if "资源" in task_name or "resource" in text:
            return ["profile_agent", "rag_retrieval_agent", "resource_planner_agent", "resource_generator_agent", "content_audit_agent"]
        if "测评" in task_name or "assessment" in text:
            return ["profile_agent", "assessment_generator_agent", "assessment_grader_agent", "profile_update_agent"]
        if "报告" in task_name or "portfolio" in text:
            return ["evidence_collector_agent", "portfolio_report_agent", "risk_intervention_agent", "profile_update_agent"]
        return ["intent_router_agent", "rag_retrieval_agent", "task_agent", "content_audit_agent"]

    def _steps(self, request: AgentTraceRequest, agents: list[str]) -> list[AgentTraceStep]:
        payload_summary = compact(str(request.requestPayload or {}), 180)
        response_summary = compact(request.responseSummary or "等待业务 Agent 返回结构化结果。", 180)
        evidence_refs = [item.id for item in request.citations[:4]]
        steps: list[AgentTraceStep] = []
        for index, agent_name in enumerate(agents, start=1):
            steps.append(AgentTraceStep(
                order=index,
                agentName=agent_name,
                role=self._role(agent_name),
                inputSummary=self._input_summary(index, request, payload_summary),
                outputSummary=self._output_summary(index, len(agents), agent_name, response_summary, request),
                evidenceRefs=evidence_refs if "rag" in agent_name.lower() or "audit" in agent_name.lower() else [],
                status="ok",
            ))
        return steps

    def _role(self, agent_name: str) -> str:
        mapping = [
            ("profile", "读取画像与过程数据，形成个性化约束。"),
            ("rag", "检索课程知识库，返回引用证据。"),
            ("planner", "拆分资源或学习步骤。"),
            ("generator", "生成结构化学习资源。"),
            ("audit", "执行防幻觉、安全与引用覆盖检查。"),
            ("assessment", "生成或批改测评题。"),
            ("portfolio", "汇总学习证据并形成报告。"),
            ("risk", "识别学习风险并给出干预策略。"),
            ("update", "输出画像维度更新建议。"),
            ("router", "识别用户意图并选择智能体。"),
        ]
        lower_name = agent_name.lower()
        for keyword, role in mapping:
            if keyword in lower_name:
                return role
        return "执行当前任务的专用智能体步骤。"

    def _input_summary(self, index: int, request: AgentTraceRequest, payload_summary: str) -> str:
        if index == 1:
            return compact(f"用户意图：{request.userIntent}；请求摘要：{payload_summary}", 220)
        return "接收上一步结构化输出、画像约束和必要的引用证据。"

    def _output_summary(
        self,
        index: int,
        total_steps: int,
        agent_name: str,
        response_summary: str,
        request: AgentTraceRequest,
    ) -> str:
        if index == total_steps:
            return response_summary
        if "rag" in agent_name.lower():
            return f"返回 {len(request.citations)} 条候选引用，供后续生成和审计使用。"
        if "audit" in agent_name.lower():
            issue_text = "；".join(request.safetyIssues[:3]) if request.safetyIssues else "未发现高风险内容。"
            return f"完成安全和引用检查：{issue_text}"
        return "输出结构化中间结果，不暴露模型内部推理文本。"

    def _quality_gates(self, request: AgentTraceRequest, steps: list[AgentTraceStep]) -> list[AgentQualityGate]:
        gates = [
            AgentQualityGate(
                name="输入完整性",
                status="passed" if request.userIntent.strip() and request.taskName.strip() else "warning",
                details="检查 taskName、userIntent、画像/课程字段是否足以路由。",
            ),
            AgentQualityGate(
                name="证据链",
                status="passed" if request.citations else "warning",
                details=f"本次追踪包含 {len(request.citations)} 条引用；无引用时前端应提示教师复核。",
            ),
            AgentQualityGate(
                name="安全审计",
                status="warning" if request.safetyIssues else "passed",
                details="; ".join(request.safetyIssues[:3]) if request.safetyIssues else "未记录安全问题。",
            ),
            AgentQualityGate(
                name="降级可见性",
                status="warning" if request.fallbackEvents else "passed",
                details="; ".join(request.fallbackEvents[:3]) if request.fallbackEvents else "未记录 provider 或工具降级。",
            ),
            AgentQualityGate(
                name="步骤完整性",
                status="passed" if len(steps) >= 3 else "warning",
                details=f"当前链路包含 {len(steps)} 个 Agent 步骤。",
            ),
        ]
        return gates

    def _reproducibility_notes(self, request: AgentTraceRequest) -> list[str]:
        return [
            f"Provider 配置：{self.settings.provider}；实际业务响应由对应 Agent 产生，追踪接口只记录摘要。",
            "不返回模型隐藏推理，只记录输入摘要、输出摘要、证据编号、质量门禁和降级事件。",
            "Java 后端建议把 traceId、taskName、requestPayload 摘要、citations 和 safetyIssues 落库。",
            "Vue3 前端可把 traceSteps 渲染成时间线，把 qualityGates 渲染成可展开审计面板。",
            f"课程/学生范围：courseId={request.courseId or '未提供'}，studentProfileId={request.studentProfileId or '未提供'}。",
        ]
