from typing import Any, TypedDict

from learning_agent.config import AgentSettings
from learning_agent.llm import ProviderRouter
from learning_agent.resource_templates import (
    build_query,
    citations_markdown,
    compact,
    estimate_minutes,
    exercise_block,
    infer_target_level,
    limit_text,
    mermaid_map,
    project_case,
    video_script,
)
from learning_agent.safety import ContentSafetyReview
from learning_agent.schemas import KnowledgeMatch, ResourceAgentRequest, ResourceAgentResponse
from learning_agent.vector_store import InMemoryVectorStore

try:
    from langgraph.graph import END, StateGraph
except Exception:  # pragma: no cover - exercised when optional package is absent
    END = "__end__"
    StateGraph = None  # type: ignore[assignment]


class GenerationState(TypedDict, total=False):
    request: ResourceAgentRequest
    retrieved: list[KnowledgeMatch]
    target_level: str
    learning_gaps: list[str]
    resource_plan: list[str]
    generated_sections: list[str]
    provider_used: str
    fallback_used: bool
    safety_issues: list[str]
    quality_checks: list[str]
    final_response: ResourceAgentResponse


class ResourceGenerationWorkflow:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store
        self.provider_router = ProviderRouter(settings)
        self.safety = ContentSafetyReview()
        self._graph = self._build_graph()

    @property
    def runtime_name(self) -> str:
        return "langgraph" if self._graph is not None else "sequential-fallback"

    def generate(self, request: ResourceAgentRequest) -> ResourceAgentResponse:
        state: GenerationState = {"request": request}
        if self._graph is not None:
            final_state = self._graph.invoke(state)
        else:
            final_state = self._run_sequential(state)
        return final_state["final_response"]

    def _build_graph(self) -> Any:
        if StateGraph is None:
            return None
        graph = StateGraph(GenerationState)
        graph.add_node("retrieve_context", self._retrieve_context)
        graph.add_node("profile_analyst", self._profile_analyst)
        graph.add_node("resource_planner", self._resource_planner)
        graph.add_node("resource_writers", self._resource_writers)
        graph.add_node("safety_reviewer", self._safety_reviewer)
        graph.add_node("assembler", self._assembler)
        graph.set_entry_point("retrieve_context")
        graph.add_edge("retrieve_context", "profile_analyst")
        graph.add_edge("profile_analyst", "resource_planner")
        graph.add_edge("resource_planner", "resource_writers")
        graph.add_edge("resource_writers", "safety_reviewer")
        graph.add_edge("safety_reviewer", "assembler")
        graph.add_edge("assembler", END)
        return graph.compile()

    def _run_sequential(self, state: GenerationState) -> GenerationState:
        for node in [
            self._retrieve_context,
            self._profile_analyst,
            self._resource_planner,
            self._resource_writers,
            self._safety_reviewer,
            self._assembler,
        ]:
            state.update(node(state))
        return state

    def _retrieve_context(self, state: GenerationState) -> GenerationState:
        request = state["request"]
        query = build_query(request)
        matches = self.vector_store.search(query, top_k=self.settings.retrieval_top_k)
        return {"retrieved": matches}

    def _profile_analyst(self, state: GenerationState) -> GenerationState:
        request = state["request"]
        profile_text = request.studentProfileSummary
        target_level = infer_target_level(profile_text)
        gaps = []
        if any(keyword in profile_text for keyword in ["弱", "薄弱", "不熟", "不会"]):
            gaps.append("基础概念和先修知识需要先补齐")
        if any(keyword in profile_text for keyword in ["项目", "案例", "实操"]):
            gaps.append("需要把知识点迁移到项目任务")
        if any(keyword in profile_text for keyword in ["图", "视频", "动画"]):
            gaps.append("适合用图解脚本和短视频脚本降低理解门槛")
        if not gaps:
            gaps.append("需通过练习反馈继续识别易错点")
        return {"target_level": target_level, "learning_gaps": gaps}

    def _resource_planner(self, state: GenerationState) -> GenerationState:
        request = state["request"]
        requested = request.targetResourceTypes or [request.resourceType]
        defaults = [
            "专业课程讲解文档",
            "知识点思维导图",
            "分层练习题",
            "拓展阅读材料",
            "代码/项目实操案例",
            "多模态视频或动画脚本",
        ]
        plan = []
        for item in requested + defaults:
            if item not in plan:
                plan.append(item)
        return {"resource_plan": plan[:6]}

    def _resource_writers(self, state: GenerationState) -> GenerationState:
        request = state["request"]
        retrieved = state.get("retrieved", [])
        target_level = state.get("target_level", "根据学习画像自适应")
        context = "\n\n".join(f"[{match.title}] {compact(match.text, 360)}" for match in retrieved[:4])
        system_prompt = "你是高校课程个性化学习资源生成智能体，必须依据资料片段、学习画像和课程目标生成可复核内容。"
        user_prompt = (
            f"课程：{request.courseTitle}\n"
            f"主题：{request.topic}\n"
            f"学生画像：{request.studentProfileSummary}\n"
            f"资源要求：{request.resourceType} / {request.modality}\n"
            f"教师补充要求：{request.prompt}\n"
            f"RAG资料片段：{context or '无命中资料'}\n"
            "请生成简洁、可执行、面向比赛演示的学习资源。"
        )
        llm_text, provider_used, fallback_used = self.provider_router.complete(system_prompt, user_prompt)
        sections = [
            self._overview_section(request, target_level, state.get("learning_gaps", []), retrieved),
            self._personalized_explanation(request, llm_text, retrieved),
            self._resource_package(request, target_level),
            self._learning_path(request, target_level),
        ]
        return {
            "generated_sections": sections,
            "provider_used": provider_used,
            "fallback_used": fallback_used,
        }

    def _safety_reviewer(self, state: GenerationState) -> GenerationState:
        content = "\n\n".join(state.get("generated_sections", []))
        sanitized, safety_issues = self.safety.sanitize(content)
        quality_checks = self.safety.hallucination_checks(sanitized, len(state.get("retrieved", [])))
        return {
            "generated_sections": [sanitized],
            "safety_issues": safety_issues,
            "quality_checks": quality_checks,
        }

    def _assembler(self, state: GenerationState) -> GenerationState:
        request = state["request"]
        retrieved = state.get("retrieved", [])
        target_level = state.get("target_level", "根据学习画像自适应")
        sections = "\n\n".join(state.get("generated_sections", []))
        quality_checks = state.get("quality_checks", [])
        safety_issues = state.get("safety_issues", [])
        resource_plan = state.get("resource_plan", [])
        provider_used = state.get("provider_used", "offline")
        fallback_used = state.get("fallback_used", False)
        content = f"""# {request.topic} - 个性化学习资源包

课程：{request.courseTitle}
资源请求：{request.resourceType} / {request.modality}
目标层级：{target_level}
多智能体流程：画像分析 Agent -> RAG 检索 Agent -> 资源规划 Agent -> 资源生成 Agent -> 安全审查 Agent
模型提供方：{provider_used}{"（已降级）" if fallback_used else ""}

{sections}

## 资料来源
{citations_markdown(retrieved)}

## 质量与安全检查
{chr(10).join("- " + item for item in quality_checks)}
{("- 安全处理：" + "；".join(safety_issues)) if safety_issues else "- 未发现需要移除的敏感内容。"}

## 后续资源推送建议
{self._recommendations(resource_plan)}
"""
        response = ResourceAgentResponse(
            title=limit_text(f"{request.topic} - 个性化{request.resourceType}", 180),
            resourceType=limit_text(request.resourceType, 60),
            modality=limit_text(request.modality, 60),
            targetLevel=limit_text(target_level, 80),
            estimatedMinutes=estimate_minutes(request.resourceType, request.modality, len(resource_plan)),
            content=content,
            summary=f"已基于画像、RAG资料和多智能体流程生成 {len(resource_plan)} 类学习资源。Provider={provider_used}。",
        )
        return {"final_response": response}

    def _overview_section(
        self,
        request: ResourceAgentRequest,
        target_level: str,
        learning_gaps: list[str],
        retrieved: list[KnowledgeMatch],
    ) -> str:
        evidence = "；".join(compact(match.text, 70) for match in retrieved[:3]) or "暂无命中资料，使用课程通用知识模板。"
        return f"""## 学情诊断与生成目标
- 学习画像摘要：{compact(request.studentProfileSummary, 260)}
- 识别到的学习断点：{"；".join(learning_gaps)}
- 本次资源目标：围绕 `{request.topic}` 形成“讲解 -> 图解 -> 练习 -> 实操 -> 反馈”的闭环。
- 适配层级：{target_level}
- RAG 依据摘要：{evidence}"""

    def _personalized_explanation(
        self,
        request: ResourceAgentRequest,
        llm_text: str,
        retrieved: list[KnowledgeMatch],
    ) -> str:
        grounding = "\n".join(f"- {compact(match.text, 120)}" for match in retrieved[:3])
        return f"""## 专业课程讲解文档
### 核心解释
`{request.topic}` 应先放在 `{request.courseTitle}` 的课程任务中理解：它不是孤立概念，而是连接需求、设计、实现和测试的关键环节。

### 个性化讲解
{compact(llm_text, 900)}

### 关键依据
{grounding or "- 当前知识库未命中强相关片段，请补充教材、讲义或项目文档后重新生成。"}"""

    def _resource_package(self, request: ResourceAgentRequest, target_level: str) -> str:
        return f"""## 知识点思维导图
{mermaid_map(request.topic)}

## 分层练习题
{exercise_block(request.topic, target_level)}

## 拓展阅读材料
- 先读课程讲义中与 `{request.topic}` 直接相关的概念页，标出不理解的术语。
- 再读一个工程案例，观察该知识点如何影响代码结构、接口设计或数据流。
- 最后阅读官方文档或教材章节，补齐概念边界和常见误区。

## 代码/项目实操案例
{project_case(request.topic, request.courseTitle)}

## 多模态视频或动画脚本
{video_script(request.topic, request.modality)}"""

    def _learning_path(self, request: ResourceAgentRequest, target_level: str) -> str:
        return f"""## 个性化学习路径
1. **诊断预习（10 分钟）**：用 3 个问题检查 `{request.topic}` 的先修基础。
2. **概念讲解（15 分钟）**：阅读上方讲义，记录 2 个仍然模糊的术语。
3. **图解复述（10 分钟）**：按 Mermaid 思维导图口头复述流程。
4. **分层练习（20 分钟）**：完成选择、判断、简答和纠错题。
5. **项目迁移（30 分钟）**：完成实操案例，提交结果和遇到的问题。
6. **画像更新（5 分钟）**：把错题、耗时和自评反馈给系统，动态调整 `{target_level}` 学习策略。"""

    def _recommendations(self, resource_plan: list[str]) -> str:
        if not resource_plan:
            return "- 推荐先生成讲解文档、练习题和实操案例。"
        return "\n".join(f"- {item}：生成后按学习路径顺序推送，并结合完成情况更新画像。" for item in resource_plan)
