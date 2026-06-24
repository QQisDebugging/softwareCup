from learning_agent.config import AgentSettings
from learning_agent.llm import ProviderRouter
from learning_agent.resource_templates import compact
from learning_agent.schemas import (
    CourseStructureChapter,
    CourseStructureKnowledgePoint,
    CourseStructurePublishCheck,
    CourseStructureRequest,
    CourseStructureResourceSlot,
    CourseStructureResponse,
    CourseStructureWeek,
    KnowledgeMatch,
)
from learning_agent.structured_output import as_int, as_list, as_text, complete_json
from learning_agent.vector_store import InMemoryVectorStore


class CourseStructureAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store
        self.provider_router = ProviderRouter(settings)

    def build(self, request: CourseStructureRequest) -> CourseStructureResponse:
        citations = self.vector_store.search(self._query(request), top_k=max(6, self.settings.retrieval_top_k))
        plan = self._llm_structure(request, citations)
        chapters = self._chapters(plan)
        knowledge_points = self._knowledge_points(plan, chapters)
        if not chapters:
            raise RuntimeError("Course structure agent returned no chapters.")
        if not knowledge_points:
            raise RuntimeError("Course structure agent returned no knowledge points.")
        return CourseStructureResponse(
            suggestedTitle=as_text(plan.get("suggestedTitle"), self._default_title(request)),
            suggestedDepartment=as_text(
                plan.get("suggestedDepartment"),
                "课程教师导入" if request.uploaderRole == "teacher" else "学生个人课程",
            ),
            suggestedCreditHours=as_int(plan.get("suggestedCreditHours"), max(16, len(chapters) * 8), 1, 320),
            suggestedDescription=as_text(
                plan.get("suggestedDescription"),
                f"基于《{request.sourceFile or request.courseTitle}》构建课程结构，支持画像诊断、路径规划、资源生成和学习评估。",
            ),
            learningObjectives=self._strings(plan.get("learningObjectives"))[:8],
            chapters=chapters,
            knowledgePoints=knowledge_points,
            resourceSlots=self._resource_slots(plan, chapters, knowledge_points),
            publishChecks=self._publish_checks(plan),
            weeks=self._weeks(plan, chapters, request.desiredWeeks),
            citations=citations,
            summary=as_text(
                plan.get("summary"),
                f"课程结构智能体已生成 {len(chapters)} 个章节、{len(knowledge_points)} 个知识点和资源槽位建议。",
            ),
            provider=as_text(plan.get("_provider"), self.provider_router.active_name),
            model=self.settings.openai_model
            if as_text(plan.get("_provider"), self.provider_router.active_name) == "openai_compatible"
            else self.settings.xfyun_model,
            executionMode=as_text(plan.get("_executionMode"), "LLM"),
            fallbackUsed=bool(plan.get("_fallbackUsed", False)),
        )

    def _llm_structure(self, request: CourseStructureRequest, citations: list[KnowledgeMatch]) -> dict:
        evidence = "\n\n".join(
            f"[{index}] {item.title} ({item.source}, score={item.score}): {compact(item.text, 700)}"
            for index, item in enumerate(citations[:6], start=1)
        )
        system_prompt = (
            "You are a course-construction agent for a Chinese teaching platform. "
            "Build a concrete course structure from uploaded materials. "
            "Return strict JSON only. Do not use Markdown."
        )
        user_prompt = f"""
Return one JSON object in Chinese with this shape:
{{
  "suggestedTitle": "string",
  "suggestedDepartment": "string",
  "suggestedCreditHours": 32,
  "suggestedDescription": "string",
  "learningObjectives": ["4-8 measurable course objectives"],
  "chapters": [
    {{"id": "chapter-1", "title": "第 1 章 ...", "order": 1, "objective": "string", "sections": ["1.1 ..."]}}
  ],
  "knowledgePoints": [
    {{"id": "kp-1", "chapterId": "chapter-1", "name": "string", "objective": "string", "hours": "1"}}
  ],
  "resourceSlots": [
    {{"resourceType": "讲解文档", "targetChapterId": "chapter-1", "knowledgePoints": ["string"], "purpose": "string", "priority": 1, "estimatedMinutes": 20}}
  ],
  "publishChecks": [
    {{"label": "章节结构完整性", "status": "通过/部分未通过/待检查", "issueCount": 0, "suggestion": "string"}}
  ],
  "weeks": [
    {{"week": 1, "topic": "string", "objective": "string"}}
  ],
  "summary": "string"
}}

Rules:
- Generate 3-8 chapters unless the source material clearly needs fewer.
- Generate 6-24 knowledge points, each linked to an existing chapterId.
- Resource slots must cover documents, practice, mind map, project/case, and assessment where suitable.
- Do not invent external facts, URLs, schools, or unsupported claims.
- If the material is thin, explicitly mark publishChecks as 待检查 instead of fabricating certainty.

Course id: {request.courseId or ""}
Existing course title: {request.courseTitle or ""}
Source file: {request.sourceFile}
Material type: {request.materialType}
Uploader role: {request.uploaderRole}
Target learners: {request.targetLearners}
Known local points: {request.knownKnowledgePoints}
Learning objectives already provided: {request.learningObjectives}
Existing chapters: {request.existingChapters}
Desired weeks: {request.desiredWeeks}

Uploaded material text:
{compact(request.extractedText, 5000) or "No stable extracted text; infer only from filename and metadata."}

Retrieved course evidence:
{evidence or "No retrieved evidence."}
"""
        return complete_json(self.provider_router, system_prompt, user_prompt, "course structure building")

    def _chapters(self, plan: dict) -> list[CourseStructureChapter]:
        items = [item for item in as_list(plan.get("chapters")) if isinstance(item, dict)]
        chapters: list[CourseStructureChapter] = []
        for index, item in enumerate(items[:10], start=1):
            chapter_id = as_text(item.get("id"), f"chapter-{index}")
            chapters.append(CourseStructureChapter(
                id=chapter_id,
                title=as_text(item.get("title"), f"第 {index} 章 课程主题"),
                order=as_int(item.get("order"), index, 1, 99),
                objective=as_text(item.get("objective"), "明确本章学习目标和可验证产出。"),
                sections=self._strings(item.get("sections"))[:8],
            ))
        return sorted(chapters, key=lambda item: item.order)

    def _knowledge_points(
        self,
        plan: dict,
        chapters: list[CourseStructureChapter],
    ) -> list[CourseStructureKnowledgePoint]:
        valid_chapter_ids = {chapter.id for chapter in chapters}
        default_chapter_id = chapters[0].id if chapters else "chapter-1"
        items = [item for item in as_list(plan.get("knowledgePoints")) if isinstance(item, dict)]
        points: list[CourseStructureKnowledgePoint] = []
        for index, item in enumerate(items[:32], start=1):
            chapter_id = as_text(item.get("chapterId"), default_chapter_id)
            if chapter_id not in valid_chapter_ids:
                chapter_id = default_chapter_id
            points.append(CourseStructureKnowledgePoint(
                id=as_text(item.get("id"), f"kp-{index}"),
                chapterId=chapter_id,
                name=as_text(item.get("name"), f"知识点 {index}"),
                objective=as_text(item.get("objective"), "能说明概念、场景和实践步骤。"),
                hours=as_text(item.get("hours"), "1"),
            ))
        return points

    def _resource_slots(
        self,
        plan: dict,
        chapters: list[CourseStructureChapter],
        points: list[CourseStructureKnowledgePoint],
    ) -> list[CourseStructureResourceSlot]:
        default_chapter_id = chapters[0].id if chapters else ""
        default_points = [point.name for point in points[:3]]
        items = [item for item in as_list(plan.get("resourceSlots")) if isinstance(item, dict)]
        slots: list[CourseStructureResourceSlot] = []
        for index, item in enumerate(items[:20], start=1):
            slots.append(CourseStructureResourceSlot(
                resourceType=as_text(item.get("resourceType"), "讲解文档"),
                targetChapterId=as_text(item.get("targetChapterId"), default_chapter_id),
                knowledgePoints=self._strings(item.get("knowledgePoints"))[:8] or default_points,
                purpose=as_text(item.get("purpose"), "支撑课程学习、练习和复盘。"),
                priority=as_int(item.get("priority"), index, 1, 99),
                estimatedMinutes=as_int(item.get("estimatedMinutes"), 20, 1, 240),
            ))
        return slots

    def _publish_checks(self, plan: dict) -> list[CourseStructurePublishCheck]:
        items = [item for item in as_list(plan.get("publishChecks")) if isinstance(item, dict)]
        checks: list[CourseStructurePublishCheck] = []
        for item in items[:10]:
            checks.append(CourseStructurePublishCheck(
                label=as_text(item.get("label"), "发布检查"),
                status=as_text(item.get("status"), "待检查"),
                issueCount=as_int(item.get("issueCount"), 0, 0, 999),
                suggestion=as_text(item.get("suggestion"), ""),
            ))
        return checks

    def _weeks(
        self,
        plan: dict,
        chapters: list[CourseStructureChapter],
        desired_weeks: int,
    ) -> list[CourseStructureWeek]:
        items = [item for item in as_list(plan.get("weeks")) if isinstance(item, dict)]
        weeks: list[CourseStructureWeek] = []
        for index, item in enumerate(items[:desired_weeks], start=1):
            weeks.append(CourseStructureWeek(
                week=as_int(item.get("week"), index, 1, desired_weeks),
                topic=as_text(item.get("topic"), chapters[min(index - 1, len(chapters) - 1)].title if chapters else f"第 {index} 周"),
                objective=as_text(item.get("objective"), ""),
            ))
        return weeks

    def _strings(self, value: object) -> list[str]:
        return [as_text(item) for item in as_list(value) if as_text(item)]

    def _query(self, request: CourseStructureRequest) -> str:
        return "\n".join([
            request.courseTitle,
            request.sourceFile,
            request.materialType,
            " ".join(request.knownKnowledgePoints),
            request.extractedText,
        ])

    def _default_title(self, request: CourseStructureRequest) -> str:
        source = request.sourceFile.rsplit(".", 1)[0] if request.sourceFile else request.courseTitle
        return f"{source or '资料导入'} 自建课程"
