from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import Iterable

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from learning_agent.config import AgentSettings
from learning_agent.documents import DocumentLoader
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.graph import ResourceGenerationWorkflow
from learning_agent.assessment import AssessmentAgent
from learning_agent.schemas import (
    AssessmentGenerateRequest,
    AssessmentGenerateResponse,
    AssessmentGradeRequest,
    AssessmentGradeResponse,
    HealthResponse,
    KnowledgeIngestRequest,
    KnowledgeIngestResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    ResourceAgentRequest,
    ResourceAgentResponse,
    TutoringRequest,
    TutoringResponse,
)
from learning_agent.tutoring import TutoringAgent
from learning_agent.vector_store import InMemoryVectorStore


settings = AgentSettings.from_env()
document_loader = DocumentLoader(project_root=settings.project_root)
embedding_model = HashingEmbeddingModel(dimensions=settings.embedding_dimensions)
vector_store = InMemoryVectorStore(embedding_model=embedding_model, project_root=settings.project_root)
workflow = ResourceGenerationWorkflow(settings=settings, vector_store=vector_store)
tutoring_agent = TutoringAgent(settings=settings, vector_store=vector_store)
assessment_agent = AssessmentAgent(settings=settings, vector_store=vector_store)


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
