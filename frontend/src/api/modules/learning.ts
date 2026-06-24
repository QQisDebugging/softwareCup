import { asApiRecord, asArray, asObject, del, get, patch, post } from '@/api/http'
import type {
  CreateLearningConversationRequest,
  EvaluationReport,
  KnowledgeMastery,
  LearningConversation,
  LearningConversationMessage,
  LearningEvent,
  QuizAttempt,
  RecordLearningEventRequest,
  SendLearningConversationMessageRequest,
  SendLearningConversationMessageResponse,
} from '@/types/api'

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

function normalizeConversation(value: unknown, index: number): LearningConversation {
  const conversation = asObject<LearningConversation>(value, {
    id: `conversation-${index + 1}`,
    studentProfileId: '',
    courseId: '',
    title: `会话 ${index + 1}`,
    archived: false,
    archivedAt: null,
    lastMessagePreview: '',
    lastMessageAt: null,
    createdAt: '',
    updatedAt: '',
  })
  return {
    ...conversation,
    id: conversation.id || `conversation-${index + 1}`,
    title: conversation.title || `会话 ${index + 1}`,
    archived: Boolean(conversation.archived),
    createdAt: conversation.createdAt || '',
    updatedAt: conversation.updatedAt || '',
  }
}

function normalizeConversationMessage(value: unknown, index: number): LearningConversationMessage {
  const message = asObject<LearningConversationMessage>(value, {
    id: `message-${index + 1}`,
    conversationId: '',
    role: 'assistant',
    content: '',
    citations: [],
    followUpQuestions: [],
    learningActions: [],
    profileSignals: [],
    mermaidDiagram: null,
    provider: null,
    fallbackUsed: false,
    createdAt: '',
  })
  return {
    ...message,
    id: message.id || `message-${index + 1}`,
    role: message.role || 'assistant',
    content: message.content || '',
    citations: Array.isArray(message.citations) ? message.citations : [],
    followUpQuestions: Array.isArray(message.followUpQuestions) ? message.followUpQuestions : [],
    learningActions: Array.isArray(message.learningActions) ? message.learningActions : [],
    profileSignals: Array.isArray(message.profileSignals) ? message.profileSignals : [],
    fallbackUsed: Boolean(message.fallbackUsed),
    createdAt: message.createdAt || '',
  }
}

function normalizeSendConversationMessageResponse(value: unknown): SendLearningConversationMessageResponse {
  const record = asObject<Record<string, unknown>>(value, {})
  return {
    conversation: normalizeConversation(record.conversation, 0),
    userMessage: normalizeConversationMessage(record.userMessage, 0),
    assistantMessage: normalizeConversationMessage(record.assistantMessage, 1),
  }
}

export const learningApi = {
  tutoring: async (body: unknown) => asApiRecord(await post<unknown, unknown>('/learning/tutoring', body)),
  conversations: async (params: { studentProfileId: string; courseId?: string; archived?: boolean }) =>
    asArray<unknown>(await get<unknown>('/learning/conversations', params)).map(normalizeConversation),
  createConversation: async (body: CreateLearningConversationRequest) =>
    normalizeConversation(await post<unknown, CreateLearningConversationRequest>('/learning/conversations', body), 0),
  updateConversation: async (conversationId: string, body: { title?: string; archived?: boolean }) =>
    normalizeConversation(await patch<unknown, { title?: string; archived?: boolean }>(`/learning/conversations/${conversationId}`, body), 0),
  deleteConversation: async (conversationId: string) =>
    del<void>(`/learning/conversations/${conversationId}`),
  conversationMessages: async (conversationId: string) =>
    asArray<unknown>(await get<unknown>(`/learning/conversations/${conversationId}/messages`)).map(normalizeConversationMessage),
  sendConversationMessage: async (conversationId: string, body: SendLearningConversationMessageRequest) =>
    normalizeSendConversationMessageResponse(
      await post<unknown, SendLearningConversationMessageRequest>(`/learning/conversations/${conversationId}/messages`, body),
    ),
  generateAssessment: async (body: unknown) => asApiRecord(await post<unknown, unknown>('/learning/assessments/generate', body)),
  gradeAssessment: async (body: unknown) => asApiRecord(await post<unknown, unknown>('/learning/assessments/grade', body)),
  recordEvent: async (body: RecordLearningEventRequest) =>
    normalizeLearningEvent(await post<unknown, RecordLearningEventRequest>('/learning/events', body), 0),
  recordQuizAttempt: async (body: unknown) => normalizeAttempt(await post<unknown, unknown>('/learning/quiz-attempts', body), 0),
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
