import json

from learning_agent.config import AgentSettings
from learning_agent.llm import ProviderRouter
from learning_agent.resource_templates import compact
from learning_agent.schemas import (
    DemoRiskPlan,
    DemoScenarioRequest,
    DemoScenarioResponse,
    DemoScene,
    KnowledgeMatch,
)
from learning_agent.structured_output import as_int, as_list, as_text, complete_json
from learning_agent.vector_store import InMemoryVectorStore


class DemoScenarioPlannerAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store
        self.provider_router = ProviderRouter(settings)

    def plan(self, request: DemoScenarioRequest) -> DemoScenarioResponse:
        citations = self.vector_store.search(self._query(request), top_k=max(6, self.settings.retrieval_top_k))
        plan = self._llm_plan(request, citations)
        provider = as_text(plan.get("_provider"), self.provider_router.active_name)
        scenes = self._with_timeline(self._scenes_from_model(plan.get("scenes"), request))
        if not scenes:
            raise RuntimeError("Teaching scenario agent returned no scenes.")
        return DemoScenarioResponse(
            demoTitle=as_text(plan.get("demoTitle"), request.scenarioTitle),
            totalEstimatedMinutes=as_int(
                plan.get("totalEstimatedMinutes"),
                max(1, (sum(scene.estimatedSeconds for scene in scenes) + 59) // 60),
                1,
                60,
            ),
            scenes=scenes,
            timelineMarkdown=as_text(plan.get("timelineMarkdown"), self._timeline_markdown(scenes)),
            judgeHighlights=self._require_strings(plan.get("judgeHighlights"), "judgeHighlights", limit=8),
            prepChecklist=self._require_strings(plan.get("prepChecklist"), "prepChecklist", limit=10),
            riskPlaybook=self._risk_playbook_from_model(plan.get("riskPlaybook"), request),
            successMetrics=self._require_strings(plan.get("successMetrics"), "successMetrics", limit=8),
            citations=citations,
            summary=as_text(plan.get("summary"), f"Teaching scenario plan generated with {len(scenes)} scenes."),
            provider=provider,
            model=self._model_name(provider),
            executionMode=as_text(plan.get("_executionMode"), "LLM"),
            fallbackUsed=bool(plan.get("_fallbackUsed", False)),
        )

    def _llm_plan(self, request: DemoScenarioRequest, citations: list[KnowledgeMatch]) -> dict:
        endpoints = request.coreEndpoints or self._default_endpoints()
        evidence = "\n\n".join(
            f"[{index}] {item.title} ({item.source}, score={item.score}): {compact(item.text, 700)}"
            for index, item in enumerate(citations[:8], start=1)
        )
        system_prompt = (
            "You are a teaching-scenario orchestration agent for a Chinese teaching platform. "
            "Create a practical teacher-facing runbook that can be executed from backend API endpoints. "
            "Return strict JSON only. Do not use Markdown."
        )
        user_prompt = f"""
Return one JSON object in Chinese with this exact shape:
{{
  "demoTitle": "string",
  "totalEstimatedMinutes": 8,
  "scenes": [
    {{
      "order": 1,
      "title": "scene title",
      "endpoint": "/agents/course/diagnose",
      "inputSetup": "what payload/context to prepare",
      "expectedOutput": "what the teacher should see",
      "talkingPoint": "what to explain",
      "fallbackPlan": "contingency plan if this scene cannot be shown live; not an API fallback",
      "estimatedSeconds": 45
    }}
  ],
  "timelineMarkdown": "| time | scene | endpoint | talking point | ...",
  "judgeHighlights": ["why this proves real orchestration"],
  "prepChecklist": ["concrete preparation item"],
  "riskPlaybook": [
    {{
      "concern": "risk",
      "mitigation": "mitigation",
      "fallbackArtifact": "pre-recorded evidence or artifact to show if live demo cannot proceed"
    }}
  ],
  "successMetrics": ["measurable success criterion"],
  "summary": "short conclusion"
}}

Rules:
- Prefer real endpoints from the endpoint list below.
- Scenes must form an orchestration story, not isolated feature descriptions.
- Include evidence handoff between scenes: profile -> diagnosis -> resource generation -> assessment/review -> publication/trace.
- Do not claim a local template is a model call.
- fallbackPlan/fallbackArtifact means demo contingency only. It must not say the backend silently falls back to local generation.
- estimatedSeconds must be at least 10 and fit within the time limit as much as possible.

Scenario title: {request.scenarioTitle}
Audience: {request.audience}
Course title: {request.courseTitle}
Student/profile context:
{compact(request.studentProfileSummary, 2500)}

Time limit minutes: {request.timeLimitMinutes}
Available endpoints:
{json.dumps(endpoints, ensure_ascii=False)}

Available artifacts:
{json.dumps(request.availableArtifacts, ensure_ascii=False)}

Risk concerns:
{json.dumps(request.riskConcerns, ensure_ascii=False)}

Retrieved evidence:
{evidence or "No retrieved evidence."}
"""
        return complete_json(self.provider_router, system_prompt, user_prompt, "teaching scenario planning")

    def _default_endpoints(self) -> list[str]:
        return [
            "/agents/course/structure",
            "/agents/course/diagnose",
            "/agents/class/analytics",
            "/agents/path/plan",
            "/agents/resource-generation",
            "/agents/assessment/item-analysis",
            "/agents/safety/audit",
            "/agents/trace/explain",
        ]

    def _query(self, request: DemoScenarioRequest) -> str:
        return "\n".join([
            request.scenarioTitle,
            request.audience,
            request.courseTitle,
            request.studentProfileSummary,
            " ".join(request.coreEndpoints),
            " ".join(request.availableArtifacts),
            " ".join(request.riskConcerns),
            "teaching scenario orchestration agent API evidence",
        ])

    def _scenes_from_model(self, value: object, request: DemoScenarioRequest) -> list[DemoScene]:
        scenes: list[DemoScene] = []
        endpoints = set(request.coreEndpoints or self._default_endpoints())
        for index, item in enumerate(as_list(value)[:12], start=1):
            if not isinstance(item, dict):
                continue
            endpoint = as_text(item.get("endpoint"), next(iter(endpoints), "/agents/course/diagnose"))
            scenes.append(DemoScene(
                order=as_int(item.get("order"), index, 1, 99),
                title=as_text(item.get("title"), f"Scene {index}"),
                endpoint=endpoint,
                inputSetup=as_text(item.get("inputSetup"), "Prepare course, profile, and evidence payload."),
                expectedOutput=as_text(item.get("expectedOutput"), "Structured agent output with citations."),
                talkingPoint=as_text(item.get("talkingPoint"), "Explain the backend orchestration and evidence handoff."),
                fallbackPlan=as_text(
                    item.get("fallbackPlan"),
                    "Show the saved artifact and request/response trace; do not replace it with local generation.",
                ),
                estimatedSeconds=as_int(item.get("estimatedSeconds"), max(20, request.timeLimitMinutes * 60 // 6), 10, 300),
            ))
        scenes.sort(key=lambda item: item.order)
        return scenes

    def _risk_playbook_from_model(self, value: object, request: DemoScenarioRequest) -> list[DemoRiskPlan]:
        risks: list[DemoRiskPlan] = []
        for item in as_list(value)[:8]:
            if not isinstance(item, dict):
                continue
            risks.append(DemoRiskPlan(
                concern=as_text(item.get("concern"), "Live endpoint risk"),
                mitigation=as_text(item.get("mitigation"), "Show saved request/response and artifact metadata."),
                fallbackArtifact=as_text(item.get("fallbackArtifact"), "Saved artifact plus provider status evidence."),
            ))
        if not risks and request.riskConcerns:
            raise RuntimeError("Teaching scenario agent did not address requested risk concerns.")
        if not risks:
            raise RuntimeError("Teaching scenario agent returned no risk playbook.")
        return risks

    def _with_timeline(self, scenes: list[DemoScene]) -> list[DemoScene]:
        current = 0
        timeline: list[DemoScene] = []
        for scene in scenes:
            start = current
            end = start + scene.estimatedSeconds
            timeline.append(scene.model_copy(update={"startSecond": start, "endSecond": end}))
            current = end
        return timeline

    def _timeline_markdown(self, scenes: list[DemoScene]) -> str:
        lines = ["| Time | Scene | Endpoint | Talking point |", "| --- | --- | --- | --- |"]
        for scene in scenes:
            lines.append(
                f"| {self._format_time(scene.startSecond)}-{self._format_time(scene.endSecond)} "
                f"| {scene.title} | `{scene.endpoint}` | {scene.talkingPoint} |"
            )
        return "\n".join(lines)

    def _format_time(self, second: int) -> str:
        minutes, seconds = divmod(second, 60)
        return f"{minutes:02d}:{seconds:02d}"

    def _require_strings(self, value: object, field_name: str, *, limit: int) -> list[str]:
        strings = [as_text(item) for item in as_list(value) if as_text(item)][:limit]
        if not strings:
            raise RuntimeError(f"Teaching scenario agent returned empty {field_name}.")
        return strings

    def _model_name(self, provider: str) -> str:
        return self.settings.openai_model if provider == "openai_compatible" else self.settings.xfyun_model
