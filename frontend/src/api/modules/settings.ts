import { get, post } from '@/api/http'

export interface ProviderStatus {
  serviceOnline?: boolean
  configuredProvider?: string
  activeProvider?: string
  xfyunConfigured?: boolean
  xfyunModel?: string
  openaiConfigured?: boolean
  openaiBaseUrl?: string
  openaiModel?: string
  lastError?: string
  [key: string]: unknown
}

export interface ProviderConfigRequest {
  provider?: string
  openaiApiKey?: string
  openaiBaseUrl?: string
  openaiModel?: string
  xfyunApiPassword?: string
  xfyunModel?: string
}

export const settingsApi = {
  providerStatus: async () => (await get<ProviderStatus>('/agents/providers/status')) ?? {},
  updateProviderConfig: async (body: ProviderConfigRequest) =>
    (await post<ProviderStatus, ProviderConfigRequest>('/agents/providers/config', body)) ?? {},
}
