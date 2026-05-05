from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import Iterable

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from learning_agent.agent_trace import AgentTraceAgent
from learning_agent.assessment_item_analysis import AssessmentItemAnalysisAgent
from learning_agent.class_analytics import ClassAnalyticsAgent
from learning_agent.config import AgentSettings
from learning_agent.demo_planner import DemoScenarioPlannerAgent
from learning_agent.documents import DocumentLoader
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.graph import ResourceGenerationWorkflow
from learning_agent.assessment import AssessmentAgent
from learning_agent.code_practice import CodePracticeAgent
from learning_agent.content_audit import ContentAuditAgent
from learning_agent.course_diagnosis import CourseDiagnosisAgent
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
    DemoScenarioRequest,
    DemoScenarioResponse,
    HealthResponse,
    KnowledgeGraphRequest,
    KnowledgeGraphResponse,
    KnowledgeIngestRequest,
    KnowledgeIngestResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
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
    ResourceAgentRequest,
    ResourceAgentResponse,
    ResourceCurationRequest,
    ResourceCurationResponse,
    StoryboardRequest,
    StoryboardResponse,
    TutoringRequest,
    TutoringResponse,
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


@app.post("/agents/demo/scenario-plan", response_model=DemoScenarioResponse)
def plan_demo_scenario(request: DemoScenarioRequest) -> DemoScenarioResponse:
    ingest_context_knowledge(
        paths=request.knowledgeBasePaths,
        texts=request.documentTexts + request.coreEndpoints + request.availableArtifacts + request.riskConcerns,
        source="request.demo_scenario.documentTexts",
        title_prefix="demo-scenario-inline",
        metadata={"courseTitle": request.courseTitle},
    )
    return demo_scenario_planner_agent.plan(request)


@app.get("/agents/providers/status")
def provider_status() -> dict:
    return {
        "configuredProvider": settings.provider,
        "activeProvider": workflow.provider_router.active_name,
        "xfyunConfigured": bool(settings.xfyun_api_key and settings.xfyun_api_secret),
        "fallbackProvider": "offline",
    }


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
