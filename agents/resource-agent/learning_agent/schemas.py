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


class PortfolioReportRequest(BaseModel):
    studentProfileId: str
    courseId: str
    studentName: str = "匿名学生"
    studentProfileSummary: str
    courseTitle: str
    topic: str = "综合学习表现"
    timeRange: str = "最近 7 天"
    completedResources: list[str] = Field(default_factory=list)
    assessmentSummaries: list[str] = Field(default_factory=list)
    tutoringSummaries: list[str] = Field(default_factory=list)
    codePracticeSummaries: list[str] = Field(default_factory=list)
    learningEvents: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    knowledgeBasePaths: list[str] = Field(default_factory=list)
    documentTexts: list[str] = Field(default_factory=list)


class PortfolioEvidenceItem(BaseModel):
    category: str
    title: str
    evidence: str
    source: str
    confidenceScore: float = Field(ge=0, le=1)


class MasteryRadarItem(BaseModel):
    dimension: str
    score: int = Field(ge=0, le=100)
    evidence: str


class LearningRiskFlag(BaseModel):
    riskType: str
    severity: str
    evidence: str
    intervention: str


class PortfolioMilestone(BaseModel):
    day: int
    title: str
    successCriteria: str
    recommendedAgent: str


class PortfolioReportResponse(BaseModel):
    reportTitle: str
    executiveSummary: str
    evidenceItems: list[PortfolioEvidenceItem]
    masteryRadar: list[MasteryRadarItem]
    riskFlags: list[LearningRiskFlag]
    nextMilestones: list[PortfolioMilestone]
    teacherCommentsDraft: str
    citations: list[KnowledgeMatch]
    summary: str
    profileDimensionUpdates: list[ProfileDimensionUpdate]


class AgentTraceRequest(BaseModel):
    traceId: str | None = None
    taskName: str
    userIntent: str
    studentProfileId: str | None = None
    courseId: str | None = None
    involvedAgents: list[str] = Field(default_factory=list)
    requestPayload: dict[str, Any] = Field(default_factory=dict)
    responseSummary: str = ""
    citations: list[KnowledgeMatch] = Field(default_factory=list)
    fallbackEvents: list[str] = Field(default_factory=list)
    safetyIssues: list[str] = Field(default_factory=list)


class AgentTraceStep(BaseModel):
    order: int = Field(ge=1)
    agentName: str
    role: str
    inputSummary: str
    outputSummary: str
    evidenceRefs: list[str] = Field(default_factory=list)
    status: str


class AgentQualityGate(BaseModel):
    name: str
    status: str
    details: str


class AgentTraceResponse(BaseModel):
    traceId: str
    taskName: str
    traceSteps: list[AgentTraceStep]
    qualityGates: list[AgentQualityGate]
    fallbackEvents: list[str]
    reproducibilityNotes: list[str]
    summary: str


class ProfileInferRequest(BaseModel):
    studentProfileId: str | None = None
    courseId: str | None = None
    courseTitle: str = ""
    declaredMajor: str = ""
    currentLevel: str = ""
    learningGoal: str = ""
    preferences: str = ""
    constraintsText: str = ""
    dialogueTurns: list[str] = Field(default_factory=list)
    learningRecords: list[str] = Field(default_factory=list)
    assessmentSummaries: list[str] = Field(default_factory=list)
    tutoringSummaries: list[str] = Field(default_factory=list)
    knowledgeBasePaths: list[str] = Field(default_factory=list)
    documentTexts: list[str] = Field(default_factory=list)


class ProfileContradiction(BaseModel):
    field: str
    evidenceA: str
    evidenceB: str
    resolutionQuestion: str


class ProfileInferResponse(BaseModel):
    studentProfileId: str | None = None
    dimensions: list[ProfileDimensionUpdate]
    extractedSignals: list[str]
    contradictions: list[ProfileContradiction]
    followUpQuestions: list[str]
    citations: list[KnowledgeMatch]
    summary: str


class LearningEventAnalysisRequest(BaseModel):
    studentProfileId: str
    courseId: str
    studentProfileSummary: str
    courseTitle: str
    targetTopic: str = "综合学习表现"
    timeRange: str = "最近 7 天"
    learningEvents: list[str] = Field(default_factory=list)
    resourceUsage: list[str] = Field(default_factory=list)
    assessmentSummaries: list[str] = Field(default_factory=list)
    tutoringSummaries: list[str] = Field(default_factory=list)
    codePracticeSummaries: list[str] = Field(default_factory=list)
    knowledgeBasePaths: list[str] = Field(default_factory=list)
    documentTexts: list[str] = Field(default_factory=list)


class LearningRiskSignal(BaseModel):
    riskType: str
    severity: str
    evidence: str
    recommendedAgent: str


class AgentCallRecommendation(BaseModel):
    priority: int = Field(ge=1)
    agentEndpoint: str
    reason: str
    payloadHint: dict[str, Any] = Field(default_factory=dict)


class LearningEventAnalysisResponse(BaseModel):
    engagementScore: int = Field(ge=0, le=100)
    masteryTrend: str
    riskSignals: list[LearningRiskSignal]
    nextActions: list[str]
    recommendedAgentCalls: list[AgentCallRecommendation]
    profileDimensionUpdates: list[ProfileDimensionUpdate]
    citations: list[KnowledgeMatch]
    summary: str


class AssessmentAttemptRecord(BaseModel):
    questionId: str
    knowledgePoint: str
    questionType: str
    score: int = Field(ge=0)
    maxScore: int = Field(ge=1)
    correct: bool
    answerSummary: str = ""
    feedback: str = ""


class AssessmentItemAnalysisRequest(BaseModel):
    courseId: str
    courseTitle: str
    topic: str
    studentProfileId: str | None = None
    attempts: list[AssessmentAttemptRecord]
    knowledgeBasePaths: list[str] = Field(default_factory=list)
    documentTexts: list[str] = Field(default_factory=list)


class KnowledgePointMastery(BaseModel):
    knowledgePoint: str
    accuracy: float = Field(ge=0, le=1)
    attempts: int = Field(ge=0)
    masteryLevel: str


class HardItem(BaseModel):
    questionId: str
    knowledgePoint: str
    wrongRate: float = Field(ge=0, le=1)
    reason: str


class MisconceptionCluster(BaseModel):
    name: str
    knowledgePoints: list[str]
    evidence: str
    remediation: str


class AssessmentItemAnalysisResponse(BaseModel):
    topic: str
    knowledgePointMastery: list[KnowledgePointMastery]
    hardItems: list[HardItem]
    misconceptionClusters: list[MisconceptionCluster]
    remediationPlan: list[str]
    citations: list[KnowledgeMatch]
    summary: str


class ProjectFileInput(BaseModel):
    path: str
    language: str = "Java"
    content: str


class ProjectReviewRequest(BaseModel):
    studentProfileId: str
    courseId: str
    studentProfileSummary: str
    courseTitle: str
    projectTitle: str
    targetTopic: str = "项目级代码审查"
    files: list[ProjectFileInput]
    reviewFocus: list[str] = Field(default_factory=list)
    knowledgeBasePaths: list[str] = Field(default_factory=list)
    documentTexts: list[str] = Field(default_factory=list)


class ProjectArchitectureIssue(BaseModel):
    category: str
    path: str
    lineHint: str
    severity: str
    evidence: str
    suggestion: str
    knowledgePoint: str


class ProjectTestGap(BaseModel):
    target: str
    reason: str
    suggestedTest: str


class ProjectKnowledgeMapping(BaseModel):
    knowledgePoint: str
    evidence: str
    masterySignal: str


class ProjectRefactorTask(BaseModel):
    priority: int = Field(ge=1)
    title: str
    action: str
    estimatedMinutes: int = Field(ge=1)
    relatedFiles: list[str] = Field(default_factory=list)


class ProjectReviewResponse(BaseModel):
    overallScore: int = Field(ge=0, le=100)
    architectureIssues: list[ProjectArchitectureIssue]
    testGaps: list[ProjectTestGap]
    securityNotes: list[str]
    knowledgeMapping: list[ProjectKnowledgeMapping]
    refactorTasks: list[ProjectRefactorTask]
    citations: list[KnowledgeMatch]
    summary: str
    profileDimensionUpdates: list[ProfileDimensionUpdate]


class StudentLearningSnapshot(BaseModel):
    studentProfileId: str
    studentName: str = "匿名学生"
    profileSummary: str = ""
    recentScores: list[int] = Field(default_factory=list)
    completedResources: int = Field(default=0, ge=0)
    tutoringCount: int = Field(default=0, ge=0)
    codePracticeCount: int = Field(default=0, ge=0)
    weaknessSignals: list[str] = Field(default_factory=list)
    learningEvents: list[str] = Field(default_factory=list)


class ClassInterventionGroup(BaseModel):
    name: str
    criteria: str
    studentProfileIds: list[str]
    recommendedAgent: str
    action: str


class ClassResourceGap(BaseModel):
    knowledgePoint: str
    affectedStudents: int = Field(ge=0)
    missingResourceType: str
    suggestedAction: str


class ClassAnalyticsRequest(BaseModel):
    courseId: str
    courseTitle: str
    topic: str = "班级学习表现"
    timeRange: str = "最近 7 天"
    snapshots: list[StudentLearningSnapshot]
    knowledgeBasePaths: list[str] = Field(default_factory=list)
    documentTexts: list[str] = Field(default_factory=list)


class ClassAnalyticsResponse(BaseModel):
    classMasteryAverage: int = Field(ge=0, le=100)
    engagementAverage: int = Field(ge=0, le=100)
    topWeaknesses: list[str]
    interventionGroups: list[ClassInterventionGroup]
    resourceGaps: list[ClassResourceGap]
    teacherActions: list[str]
    citations: list[KnowledgeMatch]
    summary: str


class DemoScenarioRequest(BaseModel):
    scenarioTitle: str = "软件杯智能学习系统演示"
    audience: str = "评委"
    courseTitle: str
    studentProfileSummary: str
    timeLimitMinutes: int = Field(default=7, ge=3, le=20)
    coreEndpoints: list[str] = Field(default_factory=list)
    availableArtifacts: list[str] = Field(default_factory=list)
    riskConcerns: list[str] = Field(default_factory=list)
    knowledgeBasePaths: list[str] = Field(default_factory=list)
    documentTexts: list[str] = Field(default_factory=list)


class DemoScene(BaseModel):
    order: int = Field(ge=1)
    title: str
    endpoint: str
    inputSetup: str
    expectedOutput: str
    talkingPoint: str
    fallbackPlan: str
    estimatedSeconds: int = Field(ge=10)


class DemoScenarioResponse(BaseModel):
    demoTitle: str
    totalEstimatedMinutes: int = Field(ge=1)
    scenes: list[DemoScene]
    judgeHighlights: list[str]
    prepChecklist: list[str]
    successMetrics: list[str]
    citations: list[KnowledgeMatch]
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


class KnowledgeSearchResponse(BaseModel):
    query: str
    matches: list[KnowledgeMatch]
