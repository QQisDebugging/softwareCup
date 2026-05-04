from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


ProviderName = Literal["offline", "xfyun_spark"]


class ResourceAgentRequest(BaseModel):
    taskId: str
    studentProfileId: str
    courseId: str
    studentProfileSummary: str
    courseTitle: str
    topic: str
    resourceType: str
    modality: str
    prompt: str
    knowledgeBasePaths: list[str] = Field(default_factory=list)
    documentTexts: list[str] = Field(default_factory=list)
    targetResourceTypes: list[str] = Field(default_factory=list)


class ResourceAgentResponse(BaseModel):
    title: str
    resourceType: str
    modality: str
    targetLevel: str
    estimatedMinutes: int = Field(ge=1)
    content: str
    summary: str


class HealthResponse(BaseModel):
    service: str
    status: Literal["UP", "DEGRADED"]
    provider: ProviderName
    graph_runtime: str
    vector_documents: int
    vector_chunks: int
    timestamp: datetime


class KnowledgeDocumentInput(BaseModel):
    id: str | None = None
    title: str | None = None
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeIngestRequest(BaseModel):
    paths: list[str] = Field(default_factory=list)
    documents: list[KnowledgeDocumentInput] = Field(default_factory=list)


class KnowledgeIngestResponse(BaseModel):
    addedDocuments: int
    addedChunks: int
    totalDocuments: int
    totalChunks: int


class KnowledgeSearchRequest(BaseModel):
    query: str
    topK: int = Field(default=6, ge=1, le=20)
    filters: dict[str, str] = Field(default_factory=dict)


class KnowledgeMatch(BaseModel):
    id: str
    score: float
    text: str
    source: str
    title: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeSearchResponse(BaseModel):
    query: str
    matches: list[KnowledgeMatch]

