from learning_agent.config import AgentSettings
from learning_agent.llm import ProviderRouter
from learning_agent.resource_templates import compact
from learning_agent.schemas import (
    AssessmentBlueprintItem,
    CourseDiagnosisRequest,
    CourseDiagnosisResponse,
    KnowledgeMatch,
)
from learning_agent.structured_output import as_int, as_list, as_text, complete_json
from learning_agent.vector_store import InMemoryVectorStore


class CourseDiagnosisAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store
        self.provider_router = ProviderRouter(settings)

    def diagnose(self, request: CourseDiagnosisRequest) -> CourseDiagnosisResponse:
        citations = self.vector_store.search(self._query(request), top_k=max(8, self.settings.retrieval_top_k))
        diagnosis = self._llm_diagnosis(request, citations)
        covered = self._strings(diagnosis.get("coveredKnowledgePoints"))[:24]
        missing = self._strings(diagnosis.get("missingKnowledgePoints"))[:24]
        missing_types = self._strings(diagnosis.get("missingResourceTypes"))[:16]
        blueprint = self._blueprint(diagnosis)
        if not covered and not missing:
            raise RuntimeError("Course diagnosis agent returned no coverage or gap analysis.")
        if not blueprint:
            raise RuntimeError("Course diagnosis agent returned no assessment blueprint.")
        return CourseDiagnosisResponse(
            courseId=request.courseId,
            courseTitle=request.courseTitle,
            coverageScore=as_int(diagnosis.get("coverageScore"), 50, 0, 100),
            coveredKnowledgePoints=covered,
            missingKnowledgePoints=missing,
            missingResourceTypes=missing_types,
            assessmentBlueprint=blueprint,
            recommendedTasks=self._strings(diagnosis.get("recommendedTasks"))[:12],
            citations=citations,
            summary=as_text(
                diagnosis.get("summary"),
                f"Course diagnosis completed with {len(covered)} covered points and {len(missing)} gaps.",
            ),
            provider=as_text(diagnosis.get("_provider"), self.provider_router.active_name),
            model=self.settings.openai_model
            if as_text(diagnosis.get("_provider"), self.provider_router.active_name) == "openai_compatible"
            else self.settings.xfyun_model,
            executionMode=as_text(diagnosis.get("_executionMode"), "LLM"),
            fallbackUsed=bool(diagnosis.get("_fallbackUsed", False)),
        )

    def _llm_diagnosis(self, request: CourseDiagnosisRequest, citations: list[KnowledgeMatch]) -> dict:
        evidence = "\n\n".join(
            f"[{index}] {item.title} ({item.source}, score={item.score}): {compact(item.text, 800)}"
            for index, item in enumerate(citations[:8], start=1)
        )
        system_prompt = (
            "You are a course-diagnosis agent for a Chinese teaching platform. "
            "Evaluate course coverage, missing knowledge points, missing resource types, "
            "and assessment blueprint using only supplied syllabus/material evidence. "
            "Return strict JSON only. Do not use Markdown."
        )
        user_prompt = f"""
Return one JSON object in Chinese with this shape:
{{
  "coverageScore": 72,
  "coveredKnowledgePoints": ["knowledge point already supported by syllabus/material"],
  "missingKnowledgePoints": ["specific gap that should be built before publishing"],
  "missingResourceTypes": ["讲解文档/练习题/实训案例/导图/短视频脚本/测评"],
  "assessmentBlueprint": [
    {{
      "knowledgePoint": "string",
      "questionTypes": ["选择题", "简答题"],
      "suggestedCount": 3,
      "reason": "why this point must be assessed"
    }}
  ],
  "recommendedTasks": ["teacher-facing build task"],
  "summary": "short diagnostic conclusion"
}}

Rules:
- coverageScore must be evidence-based, 0-100.
- coveredKnowledgePoints must cite what the current course appears to cover.
- missingKnowledgePoints must be actionable; do not add generic filler.
- recommendedTasks must be backend/action oriented: what to build, review, assess, or supplement.
- If evidence is thin, lower confidence through a lower score and more verification tasks.
- Do not invent URLs, institutions, or facts outside the provided course evidence.

Course id: {request.courseId}
Course title: {request.courseTitle}
Course description:
{compact(request.courseDescription, 2500)}

Syllabus:
{compact(request.syllabusText, 5000)}

Target student profile:
{compact(request.targetStudentProfile, 1600)}

Retrieved evidence:
{evidence or "No retrieved evidence."}
"""
        return complete_json(self.provider_router, system_prompt, user_prompt, "course diagnosis")

    def _blueprint(self, diagnosis: dict) -> list[AssessmentBlueprintItem]:
        items = [item for item in as_list(diagnosis.get("assessmentBlueprint")) if isinstance(item, dict)]
        blueprint: list[AssessmentBlueprintItem] = []
        for item in items[:12]:
            question_types = self._strings(item.get("questionTypes"))[:6] or ["简答题"]
            blueprint.append(AssessmentBlueprintItem(
                knowledgePoint=as_text(item.get("knowledgePoint"), "课程核心知识点"),
                questionTypes=question_types,
                suggestedCount=as_int(item.get("suggestedCount"), 3, 1, 20),
                reason=as_text(item.get("reason"), "用于验证学生是否真正掌握该知识点。"),
            ))
        return blueprint

    def _strings(self, value: object) -> list[str]:
        return [as_text(item) for item in as_list(value) if as_text(item)]

    def _query(self, request: CourseDiagnosisRequest) -> str:
        return "\n".join([
            request.courseTitle,
            request.courseDescription,
            request.syllabusText,
            request.targetStudentProfile,
        ])
