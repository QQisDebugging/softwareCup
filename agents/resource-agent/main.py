from datetime import datetime, timezone
from contextlib import asynccontextmanager
from dataclasses import replace as dataclass_replace
from typing import Iterable

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from learning_agent.agent_trace import AgentTraceAgent
from learning_agent.assessment_item_analysis import AssessmentItemAnalysisAgent
from learning_agent.class_analytics import ClassAnalyticsAgent
from learning_agent.config import AgentSettings, RuntimeConfigError, runtime_config_path, save_runtime_overrides
from learning_agent.llm import ProviderRouter
from learning_agent.competition_enhancements import (
    AgentRunStore,
    CourseCoverageAgent,
    DefensePackAgent,
    ErrorBookAgent,
    GraphRagQueryAgent,
    HumanReviewAgent,
    OcrQuestionAgent,
    RagEvaluationAgent,
    VoicePackageAgent,
)
from learning_agent.demo_planner import DemoScenarioPlannerAgent
from learning_agent.documents import DocumentLoader
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.graph import ResourceGenerationWorkflow
from learning_agent.assessment import AssessmentAgent
from learning_agent.code_practice import CodePracticeAgent
from learning_agent.content_audit import ContentAuditAgent
from learning_agent.course_diagnosis import CourseDiagnosisAgent
from learning_agent.course_structure import CourseStructureAgent
from learning_agent.knowledge_graph import KnowledgeGraphAgent
from learning_agent.path_planner import PathPlannerAgent
from learning_agent.prerequisite import PrerequisiteDiagnosisAgent
from learning_agent.project_review import ProjectReviewAgent
from learning_agent.resource_curation import ResourceCurationAgent
from learning_agent.schemas import (
    AssessmentGenerateRequest,
    AssessmentGenerateResponse,
    AssessmentGradeRequest,
    AssessmentGradeResponse,
    AgentTraceRequest,
    AgentTraceResponse,
    AgentRunRecordRequest,
    AgentRunRecordResponse,
    AssessmentItemAnalysisRequest,
    AssessmentItemAnalysisResponse,
    ClassAnalyticsRequest,
    ClassAnalyticsResponse,
    CodePracticeGenerateRequest,
    CodePracticeGenerateResponse,
    CodePracticeGradeRequest,
    CodePracticeGradeResponse,
    ContentAuditRequest,
    ContentAuditResponse,
    CourseDiagnosisRequest,
    CourseDiagnosisResponse,
    CourseStructureRequest,
    CourseStructureResponse,
    CourseCoverageRequest,
    CourseCoverageResponse,
    DemoScenarioRequest,
    DemoScenarioResponse,
    DefensePackRequest,
    DefensePackResponse,
    ErrorBookRequest,
    ErrorBookResponse,
    GraphRagQueryRequest,
    GraphRagQueryResponse,
    HealthResponse,
    HumanReviewRequest,
    HumanReviewResponse,
    KnowledgeGraphRequest,
    KnowledgeGraphResponse,
    KnowledgeIngestRequest,
    KnowledgeIngestResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    OcrQuestionRequest,
    OcrQuestionResponse,
    LearningPathPlanRequest,
    LearningPathPlanResponse,
    LearningEventAnalysisRequest,
    LearningEventAnalysisResponse,
    PortfolioReportRequest,
    PortfolioReportResponse,
    ProfileInferRequest,
    ProfileInferResponse,
    PrerequisiteDiagnosisRequest,
    PrerequisiteDiagnosisResponse,
    ProjectReviewRequest,
    ProjectReviewResponse,
    RagEvaluationRequest,
    RagEvaluationResponse,
    ResourceAgentRequest,
    ResourceAgentResponse,
    ResourceCurationRequest,
    ResourceCurationResponse,
    StoryboardRequest,
    StoryboardResponse,
    TutoringRequest,
    TutoringResponse,
    VoicePackageRequest,
    VoicePackageResponse,
)
from learning_agent.storyboard import StoryboardAgent
from learning_agent.tutoring import TutoringAgent
from learning_agent.vector_store import InMemoryVectorStore
from learning_agent.learning_event_analysis import LearningEventAnalysisAgent
from learning_agent.portfolio_report import PortfolioReportAgent
from learning_agent.profile_infer import ProfileInferenceAgent


settings = AgentSettings.from_env()
document_loader = DocumentLoader(project_root=settings.project_root)
embedding_model = HashingEmbeddingModel(dimensions=settings.embedding_dimensions)
vector_store = InMemoryVectorStore(embedding_model=embedding_model, project_root=settings.project_root)
workflow = ResourceGenerationWorkflow(settings=settings, vector_store=vector_store)
tutoring_agent = TutoringAgent(settings=settings, vector_store=vector_store)
assessment_agent = AssessmentAgent(settings=settings, vector_store=vector_store)
path_planner_agent = PathPlannerAgent(settings=settings, vector_store=vector_store)
knowledge_graph_agent = KnowledgeGraphAgent(settings=settings, vector_store=vector_store)
content_audit_agent = ContentAuditAgent(settings=settings, vector_store=vector_store)
course_diagnosis_agent = CourseDiagnosisAgent(settings=settings, vector_store=vector_store)
course_structure_agent = CourseStructureAgent(settings=settings, vector_store=vector_store)
code_practice_agent = CodePracticeAgent(settings=settings, vector_store=vector_store)
storyboard_agent = StoryboardAgent(settings=settings, vector_store=vector_store)
prerequisite_agent = PrerequisiteDiagnosisAgent(settings=settings, vector_store=vector_store)
resource_curation_agent = ResourceCurationAgent(settings=settings, vector_store=vector_store)
portfolio_report_agent = PortfolioReportAgent(settings=settings, vector_store=vector_store)
agent_trace_agent = AgentTraceAgent(settings=settings)
profile_inference_agent = ProfileInferenceAgent(settings=settings, vector_store=vector_store)
learning_event_analysis_agent = LearningEventAnalysisAgent(settings=settings, vector_store=vector_store)
assessment_item_analysis_agent = AssessmentItemAnalysisAgent(settings=settings, vector_store=vector_store)
project_review_agent = ProjectReviewAgent(settings=settings, vector_store=vector_store)
class_analytics_agent = ClassAnalyticsAgent(settings=settings, vector_store=vector_store)
demo_scenario_planner_agent = DemoScenarioPlannerAgent(settings=settings, vector_store=vector_store)
rag_evaluation_agent = RagEvaluationAgent(settings=settings, vector_store=vector_store)
agent_run_store = AgentRunStore(settings=settings)
human_review_agent = HumanReviewAgent(settings=settings, vector_store=vector_store)
voice_package_agent = VoicePackageAgent(settings=settings, vector_store=vector_store)
ocr_question_agent = OcrQuestionAgent(settings=settings, vector_store=vector_store)
graphrag_query_agent = GraphRagQueryAgent(settings=settings, vector_store=vector_store)
error_book_agent = ErrorBookAgent(settings=settings, vector_store=vector_store)
course_coverage_agent = CourseCoverageAgent(settings=settings, vector_store=vector_store)
defense_pack_agent = DefensePackAgent(settings=settings, vector_store=vector_store)


# 所有持有 settings/provider_router 的智能体集合，用于运行时热切换模型供应商。
_RECONFIGURABLE_AGENTS = [
    workflow,
    tutoring_agent,
    assessment_agent,
    path_planner_agent,
    knowledge_graph_agent,
    content_audit_agent,
    course_diagnosis_agent,
    course_structure_agent,
    code_practice_agent,
    storyboard_agent,
    prerequisite_agent,
    resource_curation_agent,
    portfolio_report_agent,
    agent_trace_agent,
    profile_inference_agent,
    learning_event_analysis_agent,
    assessment_item_analysis_agent,
    project_review_agent,
    class_analytics_agent,
    demo_scenario_planner_agent,
    rag_evaluation_agent,
    human_review_agent,
    voice_package_agent,
    ocr_question_agent,
    graphrag_query_agent,
    error_book_agent,
    course_coverage_agent,
    defense_pack_agent,
]


def _rebind_settings(new_settings: "AgentSettings") -> None:
    """把新 settings 应用到所有智能体，并重建其 ProviderRouter，实现运行时热切换。"""
    global settings
    settings = new_settings
    for agent in _RECONFIGURABLE_AGENTS:
        if hasattr(agent, "settings"):
            agent.settings = new_settings
        if hasattr(agent, "provider_router"):
            agent.provider_router = ProviderRouter(new_settings)



@asynccontextmanager
async def lifespan(app: FastAPI):
    load_default_knowledge_base()
    yield


app = FastAPI(
    title="Software Cup AI Resource Agent",
    version="1.0.0",
    description="LangGraph/LangChain powered RAG service for personalized learning resources.",
    lifespan=lifespan,
)


def load_default_knowledge_base() -> None:
    documents = document_loader.load_seed_documents(settings.seed_knowledge_paths)
    vector_store.add_documents(documents)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        service="resource-agent",
        status="UP",
        provider=settings.provider,
        graph_runtime=workflow.runtime_name,
        vector_documents=vector_store.document_count,
        vector_chunks=vector_store.chunk_count,
        timestamp=datetime.now(timezone.utc),
    )


@app.post("/agents/resource-generation", response_model=ResourceAgentResponse)
def generate_resource(request: ResourceAgentRequest) -> ResourceAgentResponse:
    ingest_generation_request_knowledge(request)
    return workflow.generate(request)


@app.post("/agents/resource-generation/stream")
def stream_resource(request: ResourceAgentRequest) -> StreamingResponse:
    ingest_generation_request_knowledge(request)
    response = workflow.generate(request)

    def chunks() -> Iterable[str]:
        for line in response.content.splitlines():
            yield line + "\n"

    return StreamingResponse(chunks(), media_type="text/markdown; charset=utf-8")


@app.post("/agents/tutoring", response_model=TutoringResponse)
def tutoring(request: TutoringRequest) -> TutoringResponse:
    ingest_context_knowledge(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts,
        source="request.tutoring.documentTexts",
        title_prefix=f"tutoring-{request.sessionId or request.studentProfileId}-inline",
        metadata={"studentProfileId": request.studentProfileId, "courseId": request.courseId},
    )
    return tutoring_agent.answer(request)


@app.post("/agents/assessment/generate", response_model=AssessmentGenerateResponse)
def generate_assessment(request: AssessmentGenerateRequest) -> AssessmentGenerateResponse:
    ingest_context_knowledge(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts,
        source="request.assessment.documentTexts",
        title_prefix=f"assessment-{request.studentProfileId}-inline",
        metadata={"studentProfileId": request.studentProfileId, "courseId": request.courseId},
    )
    return assessment_agent.generate(request)


@app.post("/agents/assessment/grade", response_model=AssessmentGradeResponse)
def grade_assessment(request: AssessmentGradeRequest) -> AssessmentGradeResponse:
    return assessment_agent.grade(request)


@app.post("/agents/path/plan", response_model=LearningPathPlanResponse)
def plan_learning_path(request: LearningPathPlanRequest) -> LearningPathPlanResponse:
    ingest_context_knowledge(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts,
        source="request.path.documentTexts",
        title_prefix=f"path-{request.studentProfileId}-inline",
        metadata={"studentProfileId": request.studentProfileId, "courseId": request.courseId},
    )
    return path_planner_agent.plan(request)


@app.post("/agents/knowledge/graph", response_model=KnowledgeGraphResponse)
def build_knowledge_graph(request: KnowledgeGraphRequest) -> KnowledgeGraphResponse:
    ingest_context_knowledge(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts,
        source="request.graph.documentTexts",
        title_prefix=f"graph-{request.courseId}-inline",
        metadata={"studentProfileId": request.studentProfileId or "", "courseId": request.courseId},
    )
    return knowledge_graph_agent.build(request)


@app.post("/agents/safety/audit", response_model=ContentAuditResponse)
def audit_content(request: ContentAuditRequest) -> ContentAuditResponse:
    ingest_context_knowledge(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts,
        source="request.audit.documentTexts",
        title_prefix=f"audit-{request.courseId or 'course'}-inline",
        metadata={"studentProfileId": request.studentProfileId or "", "courseId": request.courseId or ""},
    )
    return content_audit_agent.audit(request)


@app.post("/agents/course/diagnose", response_model=CourseDiagnosisResponse)
def diagnose_course(request: CourseDiagnosisRequest) -> CourseDiagnosisResponse:
    ingest_context_knowledge(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts + ([request.syllabusText] if request.syllabusText.strip() else []),
        source="request.course_diagnosis.documentTexts",
        title_prefix=f"diagnosis-{request.courseId}-inline",
        metadata={"courseId": request.courseId},
    )
    return course_diagnosis_agent.diagnose(request)


@app.post("/agents/course/structure", response_model=CourseStructureResponse)
def build_course_structure(request: CourseStructureRequest) -> CourseStructureResponse:
    ingest_context_knowledge(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts + [request.extractedText, *request.knownKnowledgePoints],
        source="request.course_structure.documentTexts",
        title_prefix=f"course-structure-{request.courseId or 'draft'}-inline",
        metadata={"courseId": request.courseId or "", "sourceFile": request.sourceFile},
    )
    return course_structure_agent.build(request)


@app.post("/agents/code/practice/generate", response_model=CodePracticeGenerateResponse)
def generate_code_practice(request: CodePracticeGenerateRequest) -> CodePracticeGenerateResponse:
    ingest_context_knowledge(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts,
        source="request.code_practice.documentTexts",
        title_prefix=f"code-{request.studentProfileId}-inline",
        metadata={"studentProfileId": request.studentProfileId, "courseId": request.courseId},
    )
    return code_practice_agent.generate(request)


@app.post("/agents/code/practice/grade", response_model=CodePracticeGradeResponse)
def grade_code_practice(request: CodePracticeGradeRequest) -> CodePracticeGradeResponse:
    return code_practice_agent.grade(request)


@app.post("/agents/multimodal/storyboard", response_model=StoryboardResponse)
def create_storyboard(request: StoryboardRequest) -> StoryboardResponse:
    ingest_context_knowledge(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts,
        source="request.storyboard.documentTexts",
        title_prefix=f"storyboard-{request.courseId}-inline",
        metadata={"studentProfileId": request.studentProfileId or "", "courseId": request.courseId},
    )
    return storyboard_agent.create(request)


@app.post("/agents/prerequisite/diagnose", response_model=PrerequisiteDiagnosisResponse)
def diagnose_prerequisites(request: PrerequisiteDiagnosisRequest) -> PrerequisiteDiagnosisResponse:
    ingest_context_knowledge(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts,
        source="request.prerequisite.documentTexts",
        title_prefix=f"prerequisite-{request.studentProfileId}-inline",
        metadata={"studentProfileId": request.studentProfileId, "courseId": request.courseId},
    )
    return prerequisite_agent.diagnose(request)


@app.post("/agents/resources/curate", response_model=ResourceCurationResponse)
def curate_resources(request: ResourceCurationRequest) -> ResourceCurationResponse:
    ingest_context_knowledge(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts + request.candidateResources,
        source="request.resource_curation.documentTexts",
        title_prefix=f"curation-{request.studentProfileId}-inline",
        metadata={"studentProfileId": request.studentProfileId, "courseId": request.courseId},
    )
    return resource_curation_agent.curate(request)


@app.post("/agents/report/portfolio", response_model=PortfolioReportResponse)
def build_portfolio_report(request: PortfolioReportRequest) -> PortfolioReportResponse:
    ingest_context_knowledge(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts + request.completedResources + request.assessmentSummaries
        + request.tutoringSummaries + request.codePracticeSummaries + request.learningEvents,
        source="request.portfolio.documentTexts",
        title_prefix=f"portfolio-{request.studentProfileId}-inline",
        metadata={"studentProfileId": request.studentProfileId, "courseId": request.courseId},
    )
    return portfolio_report_agent.build(request)


@app.post("/agents/trace/explain", response_model=AgentTraceResponse)
def explain_agent_trace(request: AgentTraceRequest) -> AgentTraceResponse:
    return agent_trace_agent.explain(request)


@app.post("/agents/profile/infer", response_model=ProfileInferResponse)
def infer_profile(request: ProfileInferRequest) -> ProfileInferResponse:
    ingest_context_knowledge(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts + request.dialogueTurns + request.learningRecords
        + request.assessmentSummaries + request.tutoringSummaries,
        source="request.profile_infer.documentTexts",
        title_prefix=f"profile-{request.studentProfileId or 'anonymous'}-inline",
        metadata={"studentProfileId": request.studentProfileId or "", "courseId": request.courseId or ""},
    )
    return profile_inference_agent.infer(request)


@app.post("/agents/learning/events/analyze", response_model=LearningEventAnalysisResponse)
def analyze_learning_events(request: LearningEventAnalysisRequest) -> LearningEventAnalysisResponse:
    ingest_context_knowledge(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts + request.learningEvents + request.resourceUsage
        + request.assessmentSummaries + request.tutoringSummaries + request.codePracticeSummaries,
        source="request.learning_event_analysis.documentTexts",
        title_prefix=f"events-{request.studentProfileId}-inline",
        metadata={"studentProfileId": request.studentProfileId, "courseId": request.courseId},
    )
    return learning_event_analysis_agent.analyze(request)


@app.post("/agents/assessment/item-analysis", response_model=AssessmentItemAnalysisResponse)
def analyze_assessment_items(request: AssessmentItemAnalysisRequest) -> AssessmentItemAnalysisResponse:
    ingest_context_knowledge(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts + [
            f"{attempt.knowledgePoint} {attempt.questionType} {attempt.score}/{attempt.maxScore} "
            f"{attempt.answerSummary} {attempt.feedback}"
            for attempt in request.attempts
        ],
        source="request.assessment_item_analysis.documentTexts",
        title_prefix=f"item-analysis-{request.courseId}-inline",
        metadata={"studentProfileId": request.studentProfileId or "", "courseId": request.courseId},
    )
    return assessment_item_analysis_agent.analyze(request)


@app.post("/agents/code/project-review", response_model=ProjectReviewResponse)
def review_project_code(request: ProjectReviewRequest) -> ProjectReviewResponse:
    ingest_context_knowledge(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts + [
            f"{file.path}\n{file.content}"
            for file in request.files
        ],
        source="request.project_review.documentTexts",
        title_prefix=f"project-review-{request.studentProfileId}-inline",
        metadata={"studentProfileId": request.studentProfileId, "courseId": request.courseId},
    )
    return project_review_agent.review(request)


@app.post("/agents/class/analytics", response_model=ClassAnalyticsResponse)
def analyze_class_learning(request: ClassAnalyticsRequest) -> ClassAnalyticsResponse:
    ingest_context_knowledge(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts + [
            f"{snapshot.studentName} {snapshot.profileSummary} {' '.join(snapshot.weaknessSignals)} "
            f"{' '.join(snapshot.learningEvents)}"
            for snapshot in request.snapshots
        ],
        source="request.class_analytics.documentTexts",
        title_prefix=f"class-analytics-{request.courseId}-inline",
        metadata={"courseId": request.courseId},
    )
    return class_analytics_agent.analyze(request)


@app.post("/agents/teaching/scenario-plan", response_model=DemoScenarioResponse)
@app.post("/agents/demo/scenario-plan", response_model=DemoScenarioResponse)
def plan_teaching_scenario(request: DemoScenarioRequest) -> DemoScenarioResponse:
    ingest_context_knowledge(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts + request.coreEndpoints + request.availableArtifacts + request.riskConcerns,
        source="request.teaching_scenario.documentTexts",
        title_prefix="teaching-scenario-inline",
        metadata={"courseTitle": request.courseTitle},
    )
    return demo_scenario_planner_agent.plan(request)


@app.post("/agents/evaluation/rag-quality", response_model=RagEvaluationResponse)
def evaluate_rag_quality(request: RagEvaluationRequest) -> RagEvaluationResponse:
    ingest_context_knowledge(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts + request.contexts + [request.question, request.answer, request.expectedAnswer],
        source="request.rag_evaluation.documentTexts",
        title_prefix=f"rag-eval-{request.courseId or 'course'}-inline",
        metadata={"courseId": request.courseId or ""},
    )
    return rag_evaluation_agent.evaluate(request)


@app.post("/agents/runs/record", response_model=AgentRunRecordResponse)
def record_agent_run(request: AgentRunRecordRequest) -> AgentRunRecordResponse:
    return agent_run_store.record(request)


@app.get("/agents/runs/recent", response_model=list[AgentRunRecordResponse])
def recent_agent_runs(limit: int = 20) -> list[AgentRunRecordResponse]:
    return agent_run_store.recent(limit=max(1, min(100, limit)))


@app.get("/agents/runs/{run_id}", response_model=AgentRunRecordResponse)
def get_agent_run(run_id: str) -> AgentRunRecordResponse:
    run = agent_run_store.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Agent run `{run_id}` not found.")
    return run


@app.post("/agents/review/human-gate", response_model=HumanReviewResponse)
def human_review_gate(request: HumanReviewRequest) -> HumanReviewResponse:
    ingest_context_knowledge(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts + [request.content, *request.rubric],
        source="request.human_review.documentTexts",
        title_prefix=f"human-review-{request.courseId or 'course'}-inline",
        metadata={"courseId": request.courseId or ""},
    )
    return human_review_agent.review(request)


@app.post("/agents/multimodal/voice-package", response_model=VoicePackageResponse)
def build_voice_package(request: VoicePackageRequest) -> VoicePackageResponse:
    ingest_context_knowledge(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts + [request.script],
        source="request.voice_package.documentTexts",
        title_prefix=f"voice-package-{request.courseId or 'course'}-inline",
        metadata={"courseId": request.courseId or ""},
    )
    return voice_package_agent.build(request)


@app.post("/agents/document/ocr-question", response_model=OcrQuestionResponse)
def parse_ocr_question(request: OcrQuestionRequest) -> OcrQuestionResponse:
    ingest_context_knowledge(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts + [request.ocrText, request.studentProfileSummary],
        source="request.ocr_question.documentTexts",
        title_prefix=f"ocr-question-{request.courseId or 'course'}-inline",
        metadata={"courseId": request.courseId or "", "imageName": request.imageName},
    )
    return ocr_question_agent.extract(request)


@app.post("/agents/knowledge/graphrag-query", response_model=GraphRagQueryResponse)
def graphrag_query(request: GraphRagQueryRequest) -> GraphRagQueryResponse:
    ingest_context_knowledge(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts + [request.query, *request.weaknessSignals],
        source="request.graphrag.documentTexts",
        title_prefix=f"graphrag-{request.courseId or 'course'}-inline",
        metadata={"courseId": request.courseId or ""},
    )
    return graphrag_query_agent.query(request)


@app.post("/agents/assessment/error-book", response_model=ErrorBookResponse)
def analyze_error_book(request: ErrorBookRequest) -> ErrorBookResponse:
    ingest_context_knowledge(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts + [
            f"{attempt.questionId} {attempt.knowledgePoint} {attempt.answerSummary} {attempt.feedback}"
            for attempt in request.attempts
        ],
        source="request.error_book.documentTexts",
        title_prefix=f"error-book-{request.studentProfileId}-inline",
        metadata={"studentProfileId": request.studentProfileId, "courseId": request.courseId},
    )
    return error_book_agent.analyze(request)


@app.post("/agents/course/coverage", response_model=CourseCoverageResponse)
def analyze_course_coverage(request: CourseCoverageRequest) -> CourseCoverageResponse:
    ingest_context_knowledge(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts + request.chapters
        + [
            f"{item.title} {item.resourceType} {' '.join(item.knowledgePoints)}"
            for item in request.resourceInventory
        ]
        + [
            f"{item.title} {item.questionType} {' '.join(item.knowledgePoints)}"
            for item in request.assessmentInventory
        ],
        source="request.course_coverage.documentTexts",
        title_prefix=f"coverage-{request.courseId}-inline",
        metadata={"courseId": request.courseId},
    )
    return course_coverage_agent.analyze(request)


@app.post("/agents/demo/defense-pack", response_model=DefensePackResponse)
def build_defense_pack(request: DefensePackRequest) -> DefensePackResponse:
    ingest_context_knowledge(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts + request.implementedFeatures + request.techStack
        + request.innovationPoints + request.riskConcerns,
        source="request.defense_pack.documentTexts",
        title_prefix="defense-pack-inline",
        metadata={"projectName": request.projectName},
    )
    return defense_pack_agent.build(request)


@app.get("/agents/providers/status")
def provider_status() -> dict:
    status = workflow.provider_router.status()
    status["vectorDocuments"] = vector_store.document_count
    status["vectorChunks"] = vector_store.chunk_count
    status["xfyunAppIdConfigured"] = bool(settings.xfyun_app_id)
    config_path = runtime_config_path()
    status["runtimeConfigPersisted"] = config_path.exists()
    status["runtimeConfigPath"] = str(config_path)
    return status


class ProviderConfigRequest(BaseModel):
    provider: str | None = None
    openaiApiKey: str | None = None
    openaiBaseUrl: str | None = None
    openaiModel: str | None = None
    apiKey: str | None = None
    baseUrl: str | None = None
    model: str | None = None
    modelName: str | None = None
    deepseekApiKey: str | None = None
    xfyunApiPassword: str | None = None
    xfyunModel: str | None = None


@app.post("/agents/providers/config")
def update_provider_config(request: ProviderConfigRequest) -> dict:
    """运行时热切换模型供应商。空字段保持原值，便于只更新部分配置。"""
    provider = _normalize_provider(request)
    if provider not in {"offline", "xfyun_spark", "openai_compatible"}:
        raise HTTPException(status_code=400, detail=f"Unsupported provider '{provider}'.")
    openai_api_key = _first_text(request.openaiApiKey, request.apiKey, request.deepseekApiKey, settings.openai_api_key)
    openai_base_url = _first_text(request.openaiBaseUrl, request.baseUrl, settings.openai_base_url).rstrip("/")
    openai_model = _first_text(request.openaiModel, request.modelName, request.model, settings.openai_model)
    if provider == "openai_compatible":
        missing = [
            name
            for name, value in {
                "openaiApiKey": openai_api_key,
                "openaiBaseUrl": openai_base_url,
                "openaiModel": openai_model,
            }.items()
            if not value
        ]
        if missing:
            raise HTTPException(
                status_code=400,
                detail="OpenAI-compatible provider requires " + ", ".join(missing) + ".",
            )
    new_settings = dataclass_replace(
        settings,
        provider=provider,  # type: ignore[arg-type]
        openai_api_key=openai_api_key,
        openai_base_url=openai_base_url,
        openai_model=openai_model,
        xfyun_api_password=request.xfyunApiPassword if request.xfyunApiPassword is not None else settings.xfyun_api_password,
        xfyun_model=request.xfyunModel or settings.xfyun_model,
    )
    try:
        save_runtime_overrides({
            "provider": new_settings.provider,
            "openai_api_key": new_settings.openai_api_key,
            "openai_base_url": new_settings.openai_base_url,
            "openai_model": new_settings.openai_model,
            "xfyun_api_password": new_settings.xfyun_api_password,
            "xfyun_model": new_settings.xfyun_model,
        })
    except RuntimeConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    _rebind_settings(new_settings)
    # 持久化到本地文件，重启服务后自动恢复用户切换的供应商配置
    status = workflow.provider_router.status()
    status["applied"] = True
    config_path = runtime_config_path()
    status["runtimeConfigPersisted"] = config_path.exists()
    status["runtimeConfigPath"] = str(config_path)
    return status


def _normalize_provider(request: ProviderConfigRequest) -> str:
    raw_provider = (request.provider or "").strip().lower()
    aliases = {
        "deepseek": "openai_compatible",
        "qwen": "openai_compatible",
        "dashscope": "openai_compatible",
        "zhipu": "openai_compatible",
        "kimi": "openai_compatible",
        "moonshot": "openai_compatible",
        "openai": "openai_compatible",
        "openai-compatible": "openai_compatible",
        "openai_compatible": "openai_compatible",
        "xfyun": "xfyun_spark",
        "spark": "xfyun_spark",
        "xfyun_spark": "xfyun_spark",
        "offline": "offline",
    }
    if raw_provider:
        return aliases.get(raw_provider, raw_provider)
    if _first_text(
        request.openaiApiKey,
        request.apiKey,
        request.deepseekApiKey,
        request.openaiBaseUrl,
        request.baseUrl,
        request.openaiModel,
        request.modelName,
        request.model,
    ):
        return "openai_compatible"
    return settings.provider


def _first_text(*values: str | None) -> str:
    for value in values:
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""




def ingest_generation_request_knowledge(request: ResourceAgentRequest) -> int:
    try:
        return vector_store.add_documents(document_loader.load_generation_request_documents(request))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def ingest_context_knowledge(
    paths: list[str],
    texts: list[str],
    source: str,
    title_prefix: str,
    metadata: dict,
) -> int:
    try:
        documents = document_loader.load_context_documents(paths, texts, source, title_prefix, metadata)
        return vector_store.add_documents(documents)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/agents/knowledge/ingest", response_model=KnowledgeIngestResponse)
@app.post("/knowledge/ingest", response_model=KnowledgeIngestResponse)
def ingest_knowledge(request: KnowledgeIngestRequest) -> KnowledgeIngestResponse:
    try:
        documents = document_loader.load_request_documents(request)
        added_chunks = vector_store.add_documents(documents)
        return KnowledgeIngestResponse(
            addedDocuments=len(documents),
            addedChunks=added_chunks,
            totalDocuments=vector_store.document_count,
            totalChunks=vector_store.chunk_count,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/agents/knowledge/search", response_model=KnowledgeSearchResponse)
@app.post("/agents/knowledge/query", response_model=KnowledgeSearchResponse)
@app.post("/knowledge/search", response_model=KnowledgeSearchResponse)
def search_knowledge(request: KnowledgeSearchRequest) -> KnowledgeSearchResponse:
    matches = vector_store.search(
        query=request.query,
        top_k=request.topK,
        filters=request.filters,
    )
    return KnowledgeSearchResponse(query=request.query, matches=matches)
