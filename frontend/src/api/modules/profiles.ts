import { asArray, asObject, get, post, put } from '@/api/http'
import type { BuildProfileRequest, ProfileDetail, ProfileDimension, ProfileHistory, ProfileResponse } from '@/types/api'

function emptyProfile(profileId = '', overrides: Partial<ProfileResponse> = {}): ProfileResponse {
  return {
    id: profileId,
    studentName: '',
    major: '',
    currentLevel: '',
    learningGoal: '',
    preferences: '',
    constraintsText: '',
    dialogueSummary: '',
    createdAt: '',
    updatedAt: '',
    ...overrides,
  }
}

function normalizeProfile(value: unknown, fallback: ProfileResponse): ProfileResponse {
  const profile = asObject<ProfileResponse>(value, fallback)
  return {
    ...fallback,
    ...profile,
    id: profile.id || fallback.id,
    studentName: profile.studentName || fallback.studentName || '未命名学生',
    major: profile.major || fallback.major || '-',
    currentLevel: profile.currentLevel || fallback.currentLevel || '-',
    learningGoal: profile.learningGoal || fallback.learningGoal || '-',
    preferences: profile.preferences || fallback.preferences || '-',
    constraintsText: profile.constraintsText || fallback.constraintsText || '-',
    dialogueSummary: profile.dialogueSummary || fallback.dialogueSummary || '暂无画像摘要',
    createdAt: profile.createdAt || fallback.createdAt || '',
    updatedAt: profile.updatedAt || fallback.updatedAt || '',
  }
}

function normalizeDimension(value: unknown, index: number): ProfileDimension {
  const dimension = asObject<ProfileDimension>(value, {
    id: `dimension-${index + 1}`,
    profileId: '',
    dimensionKey: `dimension_${index + 1}`,
    dimensionName: `画像维度 ${index + 1}`,
    value: '-',
    evidence: '暂无证据',
    confidenceScore: 0,
    source: 'backend',
    createdAt: '',
    updatedAt: '',
  })
  return {
    ...dimension,
    id: dimension.id || `dimension-${index + 1}`,
    dimensionKey: dimension.dimensionKey || `dimension_${index + 1}`,
    dimensionName: dimension.dimensionName || dimension.dimensionKey || `画像维度 ${index + 1}`,
    value: dimension.value || '-',
    evidence: dimension.evidence || '暂无证据',
    confidenceScore: dimension.confidenceScore ?? 0,
    source: dimension.source || 'backend',
  }
}

function normalizeHistory(value: unknown, index: number): ProfileHistory {
  const history = asObject<ProfileHistory>(value, {
    id: `history-${index + 1}`,
    profileId: '',
    eventType: 'UPDATE',
    dimensionKey: `dimension_${index + 1}`,
    previousValue: '',
    newValue: '-',
    evidence: '暂无证据',
    source: 'backend',
    createdAt: '',
  })
  return {
    ...history,
    id: history.id || `history-${index + 1}`,
    eventType: history.eventType || 'UPDATE',
    dimensionKey: history.dimensionKey || `dimension_${index + 1}`,
    newValue: history.newValue || '-',
    evidence: history.evidence || history.source || '暂无证据',
    source: history.source || 'backend',
  }
}

function normalizeProfileDetail(value: unknown, fallbackProfile: ProfileResponse): ProfileDetail {
  const record = asObject<Record<string, unknown>>(value, {})
  const profile = normalizeProfile(record.profile || record.studentProfile || record, fallbackProfile)
  return {
    profile,
    dimensions: asArray<unknown>(record.dimensions).map(normalizeDimension),
    recentHistory: asArray<unknown>(record.recentHistory || record.history).map(normalizeHistory),
  }
}

export const profilesApi = {
  createFromDialogue: async (body: BuildProfileRequest) =>
    normalizeProfileDetail(
      await post<unknown, BuildProfileRequest>('/profiles/dialogue', body),
      emptyProfile('', {
        studentName: body.studentName,
        major: body.major,
        currentLevel: body.currentLevel,
        learningGoal: body.learningGoal,
        preferences: body.preferences,
        constraintsText: body.constraintsText,
      }),
    ),
  list: async () =>
    asArray<unknown>(await get<unknown>('/profiles')).map((item, index) =>
      normalizeProfile(item, emptyProfile(`profile-${index + 1}`, { studentName: `学生 ${index + 1}` })),
    ),
  get: async (profileId: string) => normalizeProfile(await get<unknown>(`/profiles/${profileId}`), emptyProfile(profileId)),
  detail: async (profileId: string) => normalizeProfileDetail(await get<unknown>(`/profiles/${profileId}/detail`), emptyProfile(profileId)),
  dimensions: async (profileId: string) => asArray<unknown>(await get<unknown>(`/profiles/${profileId}/dimensions`)).map(normalizeDimension),
  updateDimensions: async (profileId: string, body: unknown) =>
    normalizeProfileDetail(await put<unknown, unknown>(`/profiles/${profileId}/dimensions`, body), emptyProfile(profileId)),
  history: async (profileId: string) => asArray<unknown>(await get<unknown>(`/profiles/${profileId}/history`)).map(normalizeHistory),
}
