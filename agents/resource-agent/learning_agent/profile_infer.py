from learning_agent.config import AgentSettings
from learning_agent.llm import ProviderRouter
from learning_agent.resource_templates import compact
from learning_agent.schemas import (
    KnowledgeMatch,
    ProfileContradiction,
    ProfileDimensionUpdate,
    ProfileInferRequest,
    ProfileInferResponse,
)
from learning_agent.structured_output import as_float, as_list, as_text, complete_json
from learning_agent.vector_store import InMemoryVectorStore


class ProfileInferenceAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store
        self.provider_router = ProviderRouter(settings)

    def infer(self, request: ProfileInferRequest) -> ProfileInferResponse:
        citations = self.vector_store.search(self._query(request), top_k=self.settings.retrieval_top_k)
        plan = self._llm_profile(request, citations)
        dimensions = self._dimensions(plan)
        if len(dimensions) < 3:
            raise RuntimeError("Profile inference agent returned fewer than 3 dimensions.")
        return ProfileInferResponse(
            studentProfileId=request.studentProfileId,
            dimensions=dimensions,
            extractedSignals=self._strings(plan.get("extractedSignals"))[:16],
            contradictions=self._contradictions(plan),
            followUpQuestions=self._strings(plan.get("followUpQuestions"))[:8],
            citations=citations,
            summary=as_text(
                plan.get("summary"),
                f"Profile inference completed with {len(dimensions)} evidence-backed dimensions.",
            ),
            provider=as_text(plan.get("_provider"), self.provider_router.active_name),
            model=self.settings.openai_model
            if as_text(plan.get("_provider"), self.provider_router.active_name) == "openai_compatible"
            else self.settings.xfyun_model,
            executionMode=as_text(plan.get("_executionMode"), "LLM"),
            fallbackUsed=bool(plan.get("_fallbackUsed", False)),
        )

    def _llm_profile(self, request: ProfileInferRequest, citations: list[KnowledgeMatch]) -> dict:
        evidence = "\n\n".join(
            f"[{index}] {item.title} ({item.source}, score={item.score}): {compact(item.text, 700)}"
            for index, item in enumerate(citations[:6], start=1)
        )
        system_prompt = (
            "You are a learner-profile inference agent for a Chinese education platform. "
            "Infer only from the supplied learner evidence and retrieved course evidence. "
            "Return strict JSON only. Do not use Markdown."
        )
        user_prompt = f"""
Return one JSON object in Chinese with this shape:
{{
  "dimensions": [
    {{
      "dimensionKey": "KNOWLEDGE_FOUNDATION",
      "dimensionName": "知识基础",
      "value": "specific inferred value",
      "evidence": "direct evidence from dialogue/records",
      "confidenceScore": 0.78,
      "source": "profile_inference_agent"
    }}
  ],
  "extractedSignals": ["signal grounded in evidence"],
  "contradictions": [
    {{"field": "string", "evidenceA": "string", "evidenceB": "string", "resolutionQuestion": "string"}}
  ],
  "followUpQuestions": ["question that would reduce uncertainty"],
  "summary": "short operational summary for teacher/student"
}}

Rules:
- Produce 5-9 profile dimensions. Required dimensions if evidence allows:
  KNOWLEDGE_FOUNDATION, COGNITIVE_STYLE, LEARNING_GOAL, INTEREST_DIRECTION,
  ERROR_PRONE_POINTS, TIME_CONSTRAINT, RESOURCE_PREFERENCE, MASTERY_WEAKNESS.
- Every dimension must include concrete evidence; if evidence is weak, say what is missing.
- Do not invent personal attributes, diagnoses, grades, or private facts.
- Confidence must reflect evidence strength, not optimism.
- Contradictions are optional, but if present they must compare two explicit evidence snippets.

Course title: {request.courseTitle}
Declared major: {request.declaredMajor}
Current level: {request.currentLevel}
Learning goal: {request.learningGoal}
Preferences: {request.preferences}
Constraints: {request.constraintsText}

Dialogue turns:
{self._bullets(request.dialogueTurns)}

Learning records:
{self._bullets(request.learningRecords)}

Assessment summaries:
{self._bullets(request.assessmentSummaries)}

Tutoring summaries:
{self._bullets(request.tutoringSummaries)}

Retrieved course/profile evidence:
{evidence or "No retrieved evidence."}
"""
        return complete_json(self.provider_router, system_prompt, user_prompt, "profile inference")

    def _dimensions(self, plan: dict) -> list[ProfileDimensionUpdate]:
        items = [item for item in as_list(plan.get("dimensions")) if isinstance(item, dict)]
        dimensions: list[ProfileDimensionUpdate] = []
        for item in items[:12]:
            dimensions.append(ProfileDimensionUpdate(
                dimensionKey=as_text(item.get("dimensionKey"), "INFERRED_DIMENSION"),
                dimensionName=as_text(item.get("dimensionName"), "画像维度"),
                value=as_text(item.get("value"), "证据不足，待补充"),
                evidence=as_text(item.get("evidence"), "模型未返回证据"),
                confidenceScore=as_float(item.get("confidenceScore"), 0.5, 0.0, 1.0),
                source=as_text(item.get("source"), "profile_inference_agent"),
            ))
        return dimensions

    def _contradictions(self, plan: dict) -> list[ProfileContradiction]:
        items = [item for item in as_list(plan.get("contradictions")) if isinstance(item, dict)]
        contradictions: list[ProfileContradiction] = []
        for item in items[:6]:
            field = as_text(item.get("field"))
            evidence_a = as_text(item.get("evidenceA"))
            evidence_b = as_text(item.get("evidenceB"))
            question = as_text(item.get("resolutionQuestion"))
            if field and evidence_a and evidence_b and question:
                contradictions.append(ProfileContradiction(
                    field=field,
                    evidenceA=evidence_a,
                    evidenceB=evidence_b,
                    resolutionQuestion=question,
                ))
        return contradictions

    def _strings(self, value: object) -> list[str]:
        return [as_text(item) for item in as_list(value) if as_text(item)]

    def _query(self, request: ProfileInferRequest) -> str:
        return "\n".join([
            request.courseTitle,
            request.declaredMajor,
            request.currentLevel,
            request.learningGoal,
            request.preferences,
            request.constraintsText,
            *request.dialogueTurns,
            *request.learningRecords,
            *request.assessmentSummaries,
            *request.tutoringSummaries,
        ])

    def _bullets(self, values: list[str]) -> str:
        if not values:
            return "- No evidence supplied."
        return "\n".join(f"- {compact(value, 600)}" for value in values[:20] if value)
