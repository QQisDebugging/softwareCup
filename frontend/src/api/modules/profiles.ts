import { get, post, put } from '@/api/http'
import type { BuildProfileRequest, ProfileDetail, ProfileDimension, ProfileHistory, ProfileResponse } from '@/types/api'

export const profilesApi = {
  createFromDialogue: (body: BuildProfileRequest) => post<ProfileDetail, BuildProfileRequest>('/profiles/dialogue', body),
  list: () => get<ProfileResponse[]>('/profiles'),
  get: (profileId: string) => get<ProfileResponse>(`/profiles/${profileId}`),
  detail: (profileId: string) => get<ProfileDetail>(`/profiles/${profileId}/detail`),
  dimensions: (profileId: string) => get<ProfileDimension[]>(`/profiles/${profileId}/dimensions`),
  updateDimensions: (profileId: string, body: unknown) => put<ProfileDetail, unknown>(`/profiles/${profileId}/dimensions`, body),
  history: (profileId: string) => get<ProfileHistory[]>(`/profiles/${profileId}/history`),
}
