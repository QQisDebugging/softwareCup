import { get, post } from '@/api/http'
import type { EvaluationReport, KnowledgeMastery, LearningEvent, QuizAttempt } from '@/types/api'

export const learningApi = {
  tutoring: (body: unknown) => post<Record<string, unknown>, unknown>('/learning/tutoring', body),
  generateAssessment: (body: unknown) => post<Record<string, unknown>, unknown>('/learning/assessments/generate', body),
  gradeAssessment: (body: unknown) => post<Record<string, unknown>, unknown>('/learning/assessments/grade', body),
  events: (studentProfileId: string) => get<LearningEvent[]>('/learning/events', { studentProfileId }),
  tutoringHistory: (studentProfileId: string) => get<Record<string, unknown>[]>('/learning/tutoring', { studentProfileId }),
  attempts: (studentProfileId: string) => get<QuizAttempt[]>('/learning/attempts', { studentProfileId }),
  mastery: (studentProfileId: string, courseId: string) =>
    get<KnowledgeMastery[]>('/learning/mastery', { studentProfileId, courseId }),
  evaluationReports: (studentProfileId: string, courseId: string) =>
    get<EvaluationReport[]>('/learning/evaluation-reports', { studentProfileId, courseId }),
  paths: (studentProfileId: string) => get<Record<string, unknown>[]>('/learning/paths', { studentProfileId }),
  recommendations: (studentProfileId: string) => get<Record<string, unknown>[]>('/learning/recommendations', { studentProfileId }),
}
