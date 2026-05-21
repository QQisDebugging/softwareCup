export type ApiRecord = Record<string, unknown>

export interface HealthResponse {
  service?: string
  status?: string
  timestamp?: string
  [key: string]: unknown
}

export interface ProfileResponse {
  id: string
  studentName: string
  major: string
  currentLevel: string
  learningGoal: string
  preferences: string
  constraintsText: string
  dialogueSummary: string
  createdAt: string
  updatedAt: string
}

export interface ProfileDimension {
  id: string
  profileId: string
  dimensionKey: string
  dimensionName: string
  value: string
  evidence: string
  confidenceScore: number | string
  source: string
  createdAt: string
  updatedAt: string
}

export interface ProfileHistory {
  id: string
  profileId: string
  eventType: string
  dimensionKey: string
  previousValue: string
  newValue: string
  evidence: string
  source: string
  createdAt: string
}

export interface ProfileDetail {
  profile: ProfileResponse
  dimensions: ProfileDimension[]
  recentHistory: ProfileHistory[]
}

export interface BuildProfileRequest {
  studentName: string
  major: string
  currentLevel: string
  learningGoal: string
  preferences: string
  constraintsText: string
  dialogueTurns: string[]
  dimensions?: Array<{
    dimensionKey: string
    value: string
    evidence?: string
    confidenceScore?: number
    source?: string
  }>
}

export interface Course {
  id: string
  title: string
  department: string
  description: string
  creditHours: number
  syllabusJson: string
  createdAt: string
  updatedAt: string
}

export interface CreateCourseRequest {
  title: string
  department: string
  description: string
  creditHours: number
  syllabusJson: string
}

export interface LearningResource {
  id: string
  courseId: string
  sourceTaskId: string
  title: string
  resourceType: string
  resourceTypeName: string
  modality: string
  targetLevel: string
  estimatedMinutes: number
  content: string
  createdAt: string
  updatedAt: string
}

export interface ResourceType {
  code: string
  displayName: string
}

export interface GenerationTask {
  id: string
  studentProfileId: string
  courseId: string
  taskType: string
  status: string
  topic: string
  prompt: string
  resultSummary: string
  errorMessage: string | null
  createdResourceId: string | null
  progressPercent: number
  currentStep: string
  createdAt: string
  updatedAt: string
}

export interface CreateResourceTaskRequest {
  studentProfileId: string
  courseId: string
  topic: string
  resourceType: string
  modality: string
  prompt: string
}

export interface TaskStep {
  id: string
  taskId: string
  agentKey: string
  stepOrder: number
  stepName: string
  status: string
  inputSummary: string
  outputSummary: string
  progressPercent: number
  startedAt: string | null
  finishedAt: string | null
  durationMs: number | null
  errorMessage: string | null
  updatedAt: string
}

export interface ModelInvocation {
  id: string
  taskId: string
  stepId: string
  provider: string
  modelName: string
  promptHash: string
  promptSummary: string
  latencyMs: number
  status: string
  fallbackUsed: boolean
  errorMessage: string | null
  createdAt: string
}

export interface GenerationAudit {
  id: string
  taskId: string
  resourceId: string
  auditType: string
  status: string
  evidenceSummary: string
  reviewerRequired: boolean
  createdAt: string
}

export interface AgentDefinition {
  id: string
  agentKey: string
  displayName: string
  responsibility: string
  inputContract: string
  outputContract: string
  sortOrder: number
}

export interface AgentArtifact {
  id: string
  studentProfileId: string
  courseId: string
  artifactType: string
  agentEndpoint: string
  topic: string
  status: string
  requestSummary: string
  payloadJson: string
  citationsJson: string
  safetySummary: string
  traceId: string
  latencyMs: number
  errorMessage: string | null
  createdAt: string
}

export interface LearningEvent {
  id: string
  studentProfileId: string
  courseId: string
  resourceId?: string
  eventType: string
  durationSeconds?: number
  feedbackScore?: number
  eventPayload?: string
  createdAt: string
  [key: string]: unknown
}

export interface QuizAttempt {
  id: string
  studentProfileId: string
  courseId: string
  topic: string
  score: number
  maxScore: number
  weaknessSignals?: string
  createdAt: string
  [key: string]: unknown
}

export interface KnowledgeMastery {
  id?: string
  knowledgePoint: string
  masteryScore: number
  evidence?: string
  updatedAt?: string
  [key: string]: unknown
}

export interface EvaluationReport {
  id: string
  title?: string
  summary?: string
  reportJson?: string
  createdAt: string
  [key: string]: unknown
}

export interface ContestReadinessMetrics {
  [key: string]: number | string | null
}

export interface ContestRequirementEvidence {
  requirementCode: string
  category: string
  title: string
  status: string
  score: number
  target: string
  actual: string
  evidenceEndpoints: string[]
  evidenceNotes: string[]
}

export interface ContestReadinessReport {
  generatedAt: string
  scope: string
  overallScore: number
  summary: string
  metrics: ContestReadinessMetrics
  requirements: ContestRequirementEvidence[]
  demoHighlights: string[]
  recommendedDemoFlow: string[]
}

export interface AgentTool {
  key: string
  title: string
  endpoint: string
  category: string
  description?: string
  proxyTarget?: string
  samplePayload: ApiRecord
}
