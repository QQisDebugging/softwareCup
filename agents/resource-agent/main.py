from datetime import datetime, timezone
from typing import Iterable

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from learning_agent.config import AgentSettings
from learning_agent.documents import DocumentLoader
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.graph import ResourceGenerationWorkflow
from learning_agent.schemas import (
    HealthResponse,
    KnowledgeIngestRequest,
    KnowledgeIngestResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    ResourceAgentRequest,
    ResourceAgentResponse,
)
from learning_agent.vector_store import InMemoryVectorStore


settings = AgentSettings.from_env()
document_loader = DocumentLoader(project_root=settings.project_root)
embedding_model = HashingEmbeddingModel(dimensions=settings.embedding_dimensions)
vector_store = InMemoryVectorStore(embedding_model=embedding_model)
workflow = ResourceGenerationWorkflow(settings=settings, vector_store=vector_store)

app = FastAPI(
    title="Software Cup AI Resource Agent",
    version="1.0.0",
    description="LangGraph/LangChain powered RAG service for personalized learning resources.",
)


@app.on_event("startup")
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
    return workflow.generate(request)


@app.post("/agents/resource-generation/stream")
def stream_resource(request: ResourceAgentRequest) -> StreamingResponse:
    response = workflow.generate(request)

    def chunks() -> Iterable[str]:
        for line in response.content.splitlines():
            yield line + "\n"

    return StreamingResponse(chunks(), media_type="text/markdown; charset=utf-8")


@app.get("/agents/providers/status")
def provider_status() -> dict:
    return {
        "configuredProvider": settings.provider,
        "activeProvider": workflow.provider_router.active_name,
        "xfyunConfigured": bool(settings.xfyun_api_key and settings.xfyun_api_secret),
        "fallbackProvider": "offline",
    }


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


@app.post("/agents/knowledge/query", response_model=KnowledgeSearchResponse)
@app.post("/knowledge/search", response_model=KnowledgeSearchResponse)
def search_knowledge(request: KnowledgeSearchRequest) -> KnowledgeSearchResponse:
    matches = vector_store.search(
        query=request.query,
        top_k=request.topK,
        filters=request.filters,
    )
    return KnowledgeSearchResponse(query=request.query, matches=matches)
