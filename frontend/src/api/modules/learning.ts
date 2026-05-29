import { asApiRecord, asArray, asObject, get, post } from '@/api/http'
import type { EvaluationReport, KnowledgeMastery, LearningEvent, QuizAttempt } from '@/types/api'

function normalizeLearningEvent(value: unknown, index: number): LearningEvent {
  const event = asObject<LearningEvent>(value, {
    id: `event-${index + 1}`,
    studentProfileId: '',
    courseId: '',
    eventType: 'LEARNING_EVENT',
    durationSeconds: 0,
    feedbackScore: undefined,
    eventPayload: '',
    createdAt: '',
  })
  return {
    ...event,
    id: event.id || `event-${index + 1}`,
    eventType: event.eventType || 'LEARNING_EVENT',
    durationSeconds: Number(event.durationSeconds || 0),
    createdAt: event.createdAt || '',
  }
}

function normalizeAttempt(value: unknown, index: number): QuizAttempt {
  const attempt = asObject<QuizAttempt>(value, {
    id: `attempt-${index + 1}`,
    studentProfileId: '',
    courseId: '',
    topic: `测评 ${index + 1}`,
    score: 0,
    maxScore: 100,
    weaknessSignals: '',
    createdAt: '',
  })
  return {
    ...attempt,
    id: attempt.id || `attempt-${index + 1}`,
    topic: attempt.topic || `测评 ${index + 1}`,
    score: Number(attempt.score || 0),
    maxScore: Number(attempt.maxScore || 100),
    createdAt: attempt.createdAt || '',
  }
}

function normalizeMastery(value: unknown, index: number): KnowledgeMastery {
  const mastery = asObject<KnowledgeMastery>(value, {
    id: `mastery-${index + 1}`,
    knowledgePoint: `知识点 ${index + 1}`,
    masteryScore: 0,
    evidence: '',
    updatedAt: '',
  })
  return {
    ...mastery,
    id: mastery.id || `mastery-${index + 1}`,
    knowledgePoint: mastery.knowledgePoint || `知识点 ${index + 1}`,
    masteryScore: Number(mastery.masteryScore || 0),
  }
}

function normalizeReport(value: unknown, index: number): EvaluationReport {
  const report = asObject<EvaluationReport>(value, {
    id: `report-${index + 1}`,
    title: `学习报告 ${index + 1}`,
    summary: '',
    reportJson: '',
    createdAt: '',
  })
  return {
    ...report,
    id: report.id || `report-${index + 1}`,
    title: report.title || `学习报告 ${index + 1}`,
    summary: report.summary || '',
    createdAt: report.createdAt || '',
  }
}

export const learningApi = {
  tutoring: async (body: unknown) => asApiRecord(await post<unknown, unknown>('/learning/tutoring', body)),
  generateAssessment: async (body: unknown) => asApiRecord(await post<unknown, unknown>('/learning/assessments/generate', body)),
  gradeAssessment: async (body: unknown) => asApiRecord(await post<unknown, unknown>('/learning/assessments/grade', body)),
  events: async (studentProfileId: string) =>
    asArray<unknown>(await get<unknown>('/learning/events', { studentProfileId })).map(normalizeLearningEvent),
  tutoringHistory: async (studentProfileId: string) => asArray<Record<string, unknown>>(await get<unknown>('/learning/tutoring', { studentProfileId })),
  attempts: async (studentProfileId: string) =>
    asArray<unknown>(await get<unknown>('/learning/attempts', { studentProfileId })).map(normalizeAttempt),
  mastery: (studentProfileId: string, courseId: string) =>
    get<unknown>('/learning/mastery', { studentProfileId, courseId }).then((value) => asArray<unknown>(value).map(normalizeMastery)),
  evaluationReports: (studentProfileId: string, courseId: string) =>
    get<unknown>('/learning/evaluation-reports', { studentProfileId, courseId }).then((value) => asArray<unknown>(value).map(normalizeReport)),
  paths: async (studentProfileId: string) => asArray<Record<string, unknown>>(await get<unknown>('/learning/paths', { studentProfileId })),
  recommendations: async (studentProfileId: string) =>
    asArray<Record<string, unknown>>(await get<unknown>('/learning/recommendations', { studentProfileId })),
}
