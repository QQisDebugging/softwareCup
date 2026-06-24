import { asObject, get } from '@/api/http'
import type { ContestReadinessMetrics, ContestReadinessReport, ContestRequirementEvidence } from '@/types/api'

function normalizeReadinessMetric(value: unknown): ContestReadinessMetrics {
  const fallback: ContestReadinessMetrics = {
    courseCount: 0,
    studentProfileCount: 0,
    profileDimensionCount: 0,
    profileHistoryCount: 0,
    enabledAgentCount: 0,
    resourceTypeCount: 0,
    taskCount: 0,
    successfulTaskCount: 0,
    taskStepCount: 0,
    modelInvocationCount: 0,
    generationAuditCount: 0,
    reviewRequiredAuditCount: 0,
    humanReviewGateCount: 0,
    learningPathCount: 0,
    learningPathNodeCount: 0,
    resourceRecommendationCount: 0,
    learningEventCount: 0,
    tutoringSessionCount: 0,
    quizAttemptCount: 0,
    knowledgeMasteryCount: 0,
    evaluationReportCount: 0,
    agentArtifactCount: 0,
  }
  const item = asObject(value, fallback)
  return {
    ...fallback,
    courseCount: Number(item.courseCount || 0),
    studentProfileCount: Number(item.studentProfileCount || 0),
    profileDimensionCount: Number(item.profileDimensionCount || 0),
    profileHistoryCount: Number(item.profileHistoryCount || 0),
    enabledAgentCount: Number(item.enabledAgentCount || 0),
    resourceTypeCount: Number(item.resourceTypeCount || 0),
    taskCount: Number(item.taskCount || 0),
    successfulTaskCount: Number(item.successfulTaskCount || 0),
    taskStepCount: Number(item.taskStepCount || 0),
    modelInvocationCount: Number(item.modelInvocationCount || 0),
    generationAuditCount: Number(item.generationAuditCount || 0),
    reviewRequiredAuditCount: Number(item.reviewRequiredAuditCount || 0),
    humanReviewGateCount: Number(item.humanReviewGateCount || 0),
    learningPathCount: Number(item.learningPathCount || 0),
    learningPathNodeCount: Number(item.learningPathNodeCount || 0),
    resourceRecommendationCount: Number(item.resourceRecommendationCount || 0),
    learningEventCount: Number(item.learningEventCount || 0),
    tutoringSessionCount: Number(item.tutoringSessionCount || 0),
    quizAttemptCount: Number(item.quizAttemptCount || 0),
    knowledgeMasteryCount: Number(item.knowledgeMasteryCount || 0),
    evaluationReportCount: Number(item.evaluationReportCount || 0),
    agentArtifactCount: Number(item.agentArtifactCount || 0),
  }
}

function normalizeRequirement(value: unknown): ContestRequirementEvidence {
  const fallback: ContestRequirementEvidence = {
    requirementCode: `REQ-${Math.random().toString(16).slice(2, 8)}`,
    category: 'Core',
    title: 'Unknown Requirement',
    status: 'PENDING',
    score: 0,
    target: '-',
    actual: '-',
    evidenceEndpoints: [],
    evidenceNotes: [],
  }
  const item = asObject(value, fallback)
  const endpoints = Array.isArray(item.evidenceEndpoints)
    ? item.evidenceEndpoints.filter((entry): entry is string => typeof entry === 'string')
    : []
  const notes = Array.isArray(item.evidenceNotes)
    ? item.evidenceNotes.filter((entry): entry is string => typeof entry === 'string')
    : []
  return {
    ...fallback,
    ...item,
    requirementCode: String(item.requirementCode || fallback.requirementCode),
    category: String(item.category || fallback.category),
    title: String(item.title || fallback.title),
    status: String(item.status || fallback.status),
    score: Number(item.score || 0),
    target: String(item.target || fallback.target),
    actual: String(item.actual || fallback.actual),
    evidenceEndpoints: endpoints.length ? endpoints : fallback.evidenceEndpoints,
    evidenceNotes: notes.length ? notes : fallback.evidenceNotes,
  }
}

function normalizeReport(value: unknown): ContestReadinessReport {
  const fallback: ContestReadinessReport = {
    generatedAt: '',
    scope: '-',
    overallScore: 0,
    summary: '',
    metrics: {
      courseCount: 0,
      studentProfileCount: 0,
      profileDimensionCount: 0,
      profileHistoryCount: 0,
      enabledAgentCount: 0,
      resourceTypeCount: 0,
      taskCount: 0,
      successfulTaskCount: 0,
      taskStepCount: 0,
      modelInvocationCount: 0,
      generationAuditCount: 0,
      reviewRequiredAuditCount: 0,
      humanReviewGateCount: 0,
      learningPathCount: 0,
      learningPathNodeCount: 0,
      resourceRecommendationCount: 0,
      learningEventCount: 0,
      tutoringSessionCount: 0,
      quizAttemptCount: 0,
      knowledgeMasteryCount: 0,
      evaluationReportCount: 0,
      agentArtifactCount: 0,
    },
    requirements: [],
    demoHighlights: [],
    recommendedDemoFlow: [],
  }
  const raw = asObject(value, fallback)
  return {
    ...fallback,
    ...raw,
    generatedAt: String(raw.generatedAt || fallback.generatedAt),
    scope: String(raw.scope || fallback.scope),
    overallScore: Number(raw.overallScore || 0),
    summary: String(raw.summary || ''),
    metrics: normalizeReadinessMetric(raw.metrics),
    requirements: Array.isArray(raw.requirements) ? raw.requirements.map(normalizeRequirement) : [],
    demoHighlights: Array.isArray(raw.demoHighlights)
      ? raw.demoHighlights.filter((item): item is string => typeof item === 'string')
      : [],
    recommendedDemoFlow: Array.isArray(raw.recommendedDemoFlow)
      ? raw.recommendedDemoFlow.filter((item): item is string => typeof item === 'string')
      : [],
  }
}

type QualityQuery = {
  studentProfileId?: string
  courseId?: string
  taskId?: string
}

export const qualityApi = {
  getReadinessReport: async (query?: QualityQuery) => normalizeReport(await get<unknown>('/demo/readiness-report', query || {})),
}

