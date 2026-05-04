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


class KnowledgeMatch(BaseModel):
    id: str
    score: float
    text: str
    source: str
    title: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class TutoringRequest(BaseModel):
    sessionId: str | None = None
    studentProfileId: str
    courseId: str
    studentProfileSummary: str
    courseTitle: str
    question: str
    conversationHistory: list[str] = Field(default_factory=list)
    modality: str = "文本+图解"
    knowledgeBasePaths: list[str] = Field(default_factory=list)
    documentTexts: list[str] = Field(default_factory=list)


class TutoringResponse(BaseModel):
    answer: str
    citations: list[KnowledgeMatch]
    followUpQuestions: list[str]
    learningActions: list[str]
    profileSignals: list[str]
    mermaidDiagram: str
    provider: str
    fallbackUsed: bool = False


class AssessmentQuestion(BaseModel):
    id: str
    type: str
    stem: str
    options: list[str] = Field(default_factory=list)
    answer: str
    rubric: str
    explanation: str
    difficulty: str
    knowledgePoints: list[str] = Field(default_factory=list)
    score: int = Field(default=10, ge=1)


class AssessmentGenerateRequest(BaseModel):
    studentProfileId: str
    courseId: str
    studentProfileSummary: str
    courseTitle: str
    topic: str
    difficulty: str = "自适应"
    questionTypes: list[str] = Field(default_factory=lambda: ["选择题", "判断题", "简答题", "代码纠错题"])
    count: int = Field(default=6, ge=1, le=12)
    knowledgeBasePaths: list[str] = Field(default_factory=list)
    documentTexts: list[str] = Field(default_factory=list)


class AssessmentGenerateResponse(BaseModel):
    title: str
    topic: str
    questions: list[AssessmentQuestion]
    citations: list[KnowledgeMatch]
    summary: str


class AssessmentAnswer(BaseModel):
    questionId: str
    answer: str


class QuestionGradeResult(BaseModel):
    questionId: str
    score: int = Field(ge=0)
    maxScore: int = Field(ge=1)
    correct: bool
    feedback: str
    knowledgePoint: str


class ProfileDimensionUpdate(BaseModel):
    dimensionKey: str
    dimensionName: str
    value: str
    evidence: str
    confidenceScore: float = Field(ge=0, le=1)
    source: str


class AssessmentGradeRequest(BaseModel):
    studentProfileId: str
    courseId: str
    studentProfileSummary: str
    courseTitle: str
    topic: str
    questions: list[AssessmentQuestion]
    answers: list[AssessmentAnswer]


class AssessmentGradeResponse(BaseModel):
    score: int = Field(ge=0)
    maxScore: int = Field(ge=1)
    masteryLevel: str
    feedback: str
    questionResults: list[QuestionGradeResult]
    weaknessSignals: list[str]
    nextResourceTypes: list[str]
    profileDimensionUpdates: list[ProfileDimensionUpdate]


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


class KnowledgeSearchResponse(BaseModel):
    query: str
    matches: list[KnowledgeMatch]
