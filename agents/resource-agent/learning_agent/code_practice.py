import hashlib

from learning_agent.config import AgentSettings
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.resource_templates import compact, infer_target_level
from learning_agent.schemas import (
    CodeDefect,
    CodePracticeExercise,
    CodePracticeGenerateRequest,
    CodePracticeGenerateResponse,
    CodePracticeGradeRequest,
    CodePracticeGradeResponse,
    KnowledgeMatch,
    ProfileDimensionUpdate,
)
from learning_agent.vector_store import InMemoryVectorStore


class CodePracticeAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store
        self.embedding_model = HashingEmbeddingModel(settings.embedding_dimensions)

    def generate(self, request: CodePracticeGenerateRequest) -> CodePracticeGenerateResponse:
        citations = self.vector_store.search(self._query(request), top_k=self.settings.retrieval_top_k)
        target_level = infer_target_level(request.studentProfileSummary)
        exercise = self._exercise(request, citations, target_level)
        summary = f"已生成 `{request.topic}` {request.practiceType} 实操题，难度定位 `{target_level}`。"
        return CodePracticeGenerateResponse(
            exercise=exercise,
            citations=citations,
            profileDimensionUpdates=[
                ProfileDimensionUpdate(
                    dimensionKey="RESOURCE_PREFERENCE",
                    dimensionName="资源偏好",
                    value=f"适合通过 `{request.language}` 实操题巩固 `{request.topic}`。",
                    evidence=summary,
                    confidenceScore=0.7,
                    source="code_practice_agent",
                )
            ],
            summary=summary,
        )

    def grade(self, request: CodePracticeGradeRequest) -> CodePracticeGradeResponse:
        defects = self._defects(request)
        max_score = 100
        score = max(0, max_score - sum(25 if defect.severity == "high" else 14 for defect in defects))
        if not request.submissionCode.strip():
            score = 0
        feedback = f"`{request.topic}` 代码实操得分 {score}/{max_score}，主要问题 {len(defects)} 个。"
        return CodePracticeGradeResponse(
            score=score,
            maxScore=max_score,
            feedback=feedback,
            defects=defects,
            correctedCode=request.exercise.referenceSolution,
            nextActions=self._next_actions(score, request.topic),
            profileDimensionUpdates=self._profile_updates(request, feedback, score, defects),
        )

    def _query(self, request: CodePracticeGenerateRequest) -> str:
        return "\n".join([request.courseTitle, request.topic, request.practiceType, request.studentProfileSummary])

    def _exercise(
        self,
        request: CodePracticeGenerateRequest,
        citations: list[KnowledgeMatch],
        target_level: str,
    ) -> CodePracticeExercise:
        evidence = compact(citations[0].text, 120) if citations else request.topic
        exercise_id = hashlib.sha1((request.courseId + request.topic + request.practiceType).encode("utf-8")).hexdigest()[:12]
        starter = """@RestController
class CourseController {
    private final CourseRepository repository;

    @PostMapping("/courses")
    Course create(@RequestBody CourseRequest request) {
        Course course = new Course(request.title());
        return repository.save(course);
    }
}"""
        solution = """@RestController
class CourseController {
    private final CourseService courseService;

    @PostMapping("/courses")
    CourseResponse create(@Valid @RequestBody CourseRequest request) {
        return courseService.createCourse(request);
    }
}

@Service
class CourseService {
    private final CourseRepository repository;

    @Transactional
    CourseResponse createCourse(CourseRequest request) {
        Course saved = repository.save(new Course(request.title()));
        return CourseResponse.from(saved);
    }
}"""
        return CodePracticeExercise(
            id=f"code-{exercise_id}",
            title=f"{request.topic} 分层改造实操",
            scenario=f"依据资料：{evidence}。请把直接访问 Repository 的 Controller 改造成 Controller -> Service -> Repository。",
            language=request.language,
            starterCode=starter,
            referenceSolution=solution,
            rubric=[
                "Controller 只负责请求校验和响应返回。",
                "业务规则下沉到 Service，并标注事务边界。",
                "Repository 只负责数据访问。",
                "返回 DTO/Response，不直接暴露不必要实体细节。",
            ],
            testCases=[
                "提交合法课程标题时应返回 CourseResponse。",
                "Controller 中不应直接出现 repository.save。",
                "Service 方法应体现事务边界。",
            ],
            estimatedMinutes=45 if target_level == "基础补强型" else 35,
        )

    def _defects(self, request: CodePracticeGradeRequest) -> list[CodeDefect]:
        code = request.submissionCode
        defects: list[CodeDefect] = []
        if not code.strip():
            return [CodeDefect(defectType="empty_submission", location="submission", feedback="未提交代码。", severity="high")]
        if "repository.save" in code and "Controller" in code:
            defects.append(CodeDefect(
                defectType="layering",
                location="Controller",
                feedback="Controller 仍直接访问 Repository，职责边界没有拆开。",
                severity="high",
            ))
        if "Service" not in code:
            defects.append(CodeDefect(
                defectType="missing_service",
                location="service layer",
                feedback="缺少 Service 层，无法承载业务规则和事务边界。",
                severity="high",
            ))
        if "@Transactional" not in code:
            defects.append(CodeDefect(
                defectType="transaction_boundary",
                location="Service",
                feedback="没有体现事务边界，真实工程中容易出现一致性问题。",
                severity="medium",
            ))
        if "Response" not in code and "DTO" not in code:
            defects.append(CodeDefect(
                defectType="api_contract",
                location="return type",
                feedback="建议返回 Response/DTO，减少实体泄露。",
                severity="medium",
            ))
        return defects

    def _next_actions(self, score: int, topic: str) -> list[str]:
        if score >= 85:
            return [f"把 `{topic}` 实操迁移到一个真实课程资源接口。", "补一组异常场景测试。"]
        if score >= 60:
            return ["先修复高优先级缺陷，再重做一次静态批改。", "画出 Controller -> Service -> Repository 调用链。"]
        return ["回看分层职责讲解文档。", "完成一个填空式 Service 层练习。", "重新提交代码并说明每层职责。"]

    def _profile_updates(
        self,
        request: CodePracticeGradeRequest,
        feedback: str,
        score: int,
        defects: list[CodeDefect],
    ) -> list[ProfileDimensionUpdate]:
        defect_names = "、".join(dict.fromkeys(defect.defectType for defect in defects)) or "暂无明显代码缺陷"
        return [
            ProfileDimensionUpdate(
                dimensionKey="MASTERY_WEAKNESS",
                dimensionName="掌握度/薄弱点",
                value=f"{request.topic} 代码实操得分 {score}/100；缺陷：{defect_names}",
                evidence=feedback,
                confidenceScore=0.82,
                source="code_practice_agent",
            ),
            ProfileDimensionUpdate(
                dimensionKey="ERROR_PRONE_POINTS",
                dimensionName="易错点",
                value=f"代码实操暴露问题：{defect_names}",
                evidence=feedback,
                confidenceScore=0.78,
                source="code_practice_agent",
            ),
        ]
