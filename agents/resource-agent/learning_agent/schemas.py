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


class LearningPathPlanRequest(BaseModel):
    studentProfileId: str
    courseId: str
    studentProfileSummary: str
    courseTitle: str
    topic: str
    goal: str = "补齐薄弱点并完成一次可验证实践"
    timeframeDays: int = Field(default=7, ge=1, le=30)
    dailyMinutes: int = Field(default=45, ge=10, le=240)
    weaknessSignals: list[str] = Field(default_factory=list)
    completedResources: list[str] = Field(default_factory=list)
    recentScores: list[int] = Field(default_factory=list)
    knowledgeBasePaths: list[str] = Field(default_factory=list)
    documentTexts: list[str] = Field(default_factory=list)


class LearningPathStage(BaseModel):
    day: int
    title: str
    objective: str
    learningActions: list[str]
    resourceTypes: list[str]
    practiceTask: str
    checkpoint: str
    estimatedMinutes: int = Field(ge=1)


class ResourceRecommendation(BaseModel):
    priority: int
    resourceType: str
    title: str
    reason: str
    estimatedMinutes: int = Field(ge=1)


class ReviewCheckpoint(BaseModel):
    day: int
    method: str
    successCriteria: str


class LearningPathPlanResponse(BaseModel):
    planTitle: str
    studentProfileId: str
    courseId: str
    topic: str
    targetLevel: str
    stages: list[LearningPathStage]
    resourceRecommendations: list[ResourceRecommendation]
    reviewCheckpoints: list[ReviewCheckpoint]
    mermaidRoadmap: str
    citations: list[KnowledgeMatch]
    summary: str
    profileDimensionUpdates: list[ProfileDimensionUpdate]


class KnowledgeGraphRequest(BaseModel):
    studentProfileId: str | None = None
    courseId: str
    courseTitle: str
    topic: str
    weaknessSignals: list[str] = Field(default_factory=list)
    knowledgeBasePaths: list[str] = Field(default_factory=list)
    documentTexts: list[str] = Field(default_factory=list)


class KnowledgeGraphNode(BaseModel):
    id: str
    label: str
    type: str
    importance: float = Field(ge=0, le=1)
    evidence: str
    weakPoint: bool = False


class KnowledgeGraphEdge(BaseModel):
    source: str
    target: str
    relation: str
    evidence: str


class KnowledgeGraphResponse(BaseModel):
    graphTitle: str
    courseId: str
    topic: str
    nodes: list[KnowledgeGraphNode]
    edges: list[KnowledgeGraphEdge]
    weakPointHighlights: list[str]
    mermaidDiagram: str
    citations: list[KnowledgeMatch]
    summary: str


class ContentAuditRequest(BaseModel):
    studentProfileId: str | None = None
    courseId: str | None = None
    courseTitle: str = "未指定课程"
    topic: str = "待审计内容"
    content: str
    citations: list[KnowledgeMatch] = Field(default_factory=list)
    knowledgeBasePaths: list[str] = Field(default_factory=list)
    documentTexts: list[str] = Field(default_factory=list)


class UnsupportedClaim(BaseModel):
    claim: str
    reason: str
    suggestedEvidenceQuery: str


class RiskyClaim(BaseModel):
    claim: str
    riskType: str
    mitigation: str


class ContentAuditResponse(BaseModel):
    overallScore: int = Field(ge=0, le=100)
    citationCoverage: float = Field(ge=0, le=1)
    unsupportedClaims: list[UnsupportedClaim]
    riskyClaims: list[RiskyClaim]
    revisedContent: str
    recommendations: list[str]
    citations: list[KnowledgeMatch]
    summary: str


class CourseDiagnosisRequest(BaseModel):
    courseId: str
    courseTitle: str
    courseDescription: str = ""
    syllabusText: str = ""
    targetStudentProfile: str = ""
    knowledgeBasePaths: list[str] = Field(default_factory=list)
    documentTexts: list[str] = Field(default_factory=list)


class AssessmentBlueprintItem(BaseModel):
    knowledgePoint: str
    questionTypes: list[str]
    suggestedCount: int = Field(ge=1)
    reason: str


class CourseDiagnosisResponse(BaseModel):
    courseId: str
    courseTitle: str
    coverageScore: int = Field(ge=0, le=100)
    coveredKnowledgePoints: list[str]
    missingKnowledgePoints: list[str]
    missingResourceTypes: list[str]
    assessmentBlueprint: list[AssessmentBlueprintItem]
    recommendedTasks: list[str]
    citations: list[KnowledgeMatch]
    summary: str


class CodePracticeGenerateRequest(BaseModel):
    studentProfileId: str
    courseId: str
    studentProfileSummary: str
    courseTitle: str
    topic: str
    difficulty: str = "自适应"
    language: str = "Java"
    practiceType: str = "代码纠错"
    knowledgeBasePaths: list[str] = Field(default_factory=list)
    documentTexts: list[str] = Field(default_factory=list)


class CodePracticeExercise(BaseModel):
    id: str
    title: str
    scenario: str
    language: str
    starterCode: str
    referenceSolution: str
    rubric: list[str]
    testCases: list[str]
    estimatedMinutes: int = Field(ge=1)


class CodePracticeGenerateResponse(BaseModel):
    exercise: CodePracticeExercise
    citations: list[KnowledgeMatch]
    profileDimensionUpdates: list[ProfileDimensionUpdate]
    summary: str


class CodePracticeGradeRequest(BaseModel):
    studentProfileId: str
    courseId: str
    studentProfileSummary: str
    courseTitle: str
    topic: str
    exercise: CodePracticeExercise
    submissionCode: str
    explanation: str = ""


class CodeDefect(BaseModel):
    defectType: str
    location: str
    feedback: str
    severity: str


class CodePracticeGradeResponse(BaseModel):
    score: int = Field(ge=0)
    maxScore: int = Field(ge=1)
    feedback: str
    defects: list[CodeDefect]
    correctedCode: str
    nextActions: list[str]
    profileDimensionUpdates: list[ProfileDimensionUpdate]


class StoryboardRequest(BaseModel):
    studentProfileId: str | None = None
    courseId: str
    studentProfileSummary: str = ""
    courseTitle: str
    topic: str
    targetDurationMinutes: int = Field(default=5, ge=1, le=20)
    modality: str = "PPT+短视频"
    knowledgeBasePaths: list[str] = Field(default_factory=list)
    documentTexts: list[str] = Field(default_factory=list)


class PPTSlide(BaseModel):
    slideNo: int
    title: str
    bullets: list[str]
    visualHint: str
    speakerNote: str


class StoryboardScene(BaseModel):
    sceneNo: int
    durationSeconds: int = Field(ge=1)
    visual: str
    narration: str
    interaction: str


class AssetPrompt(BaseModel):
    assetType: str
    prompt: str
    usage: str


class StoryboardResponse(BaseModel):
    title: str
    pptOutline: list[PPTSlide]
    videoStoryboard: list[StoryboardScene]
    narrationScript: str
    assetPrompts: list[AssetPrompt]
    interactionQuestions: list[str]
    citations: list[KnowledgeMatch]
    summary: str


class PrerequisiteDiagnosisRequest(BaseModel):
    studentProfileId: str
    courseId: str
    studentProfileSummary: str
    courseTitle: str
    targetTopic: str
    completedTopics: list[str] = Field(default_factory=list)
    assessmentWeaknesses: list[str] = Field(default_factory=list)
    knowledgeBasePaths: list[str] = Field(default_factory=list)
    documentTexts: list[str] = Field(default_factory=list)


class PrerequisiteItem(BaseModel):
    name: str
    status: Literal["已掌握", "部分掌握", "未掌握", "待诊断"]
    importance: float = Field(ge=0, le=1)
    evidence: str
    remediationAction: str


class DiagnosticQuestion(BaseModel):
    id: str
    prerequisite: str
    question: str
    expectedAnswer: str
    questionType: str
    score: int = Field(ge=1)


class PrerequisiteDiagnosisResponse(BaseModel):
    targetTopic: str
    readinessScore: int = Field(ge=0, le=100)
    readinessLevel: str
    prerequisites: list[PrerequisiteItem]
    diagnosticQuestions: list[DiagnosticQuestion]
    gapSummary: str
    recommendedWarmups: list[str]
    citations: list[KnowledgeMatch]
    profileDimensionUpdates: list[ProfileDimensionUpdate]


class ResourceCurationRequest(BaseModel):
    studentProfileId: str
    courseId: str
    studentProfileSummary: str
    courseTitle: str
    topic: str
    targetLevel: str = "自适应"
    resourceTypes: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    timeBudgetMinutes: int = Field(default=90, ge=10, le=480)
    candidateResources: list[str] = Field(default_factory=list)
    knowledgeBasePaths: list[str] = Field(default_factory=list)
    documentTexts: list[str] = Field(default_factory=list)


class CuratedResource(BaseModel):
    rank: int = Field(ge=1)
    title: str
    resourceType: str
    difficulty: str
    estimatedMinutes: int = Field(ge=1)
    sourceTitle: str
    reason: str
    usageOrder: str
    citationIds: list[str] = Field(default_factory=list)


class CoverageMapItem(BaseModel):
    knowledgePoint: str
    coveredBy: list[str]
    gapLevel: str
    recommendation: str


class ResourceCurationResponse(BaseModel):
    bundleTitle: str
    targetLevel: str
    curatedResources: list[CuratedResource]
    coverageMap: list[CoverageMapItem]
    usagePlan: list[str]
    citations: list[KnowledgeMatch]
    summary: str
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
