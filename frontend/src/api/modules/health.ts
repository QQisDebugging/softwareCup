import { get } from '@/api/http'
import type { HealthResponse } from '@/types/api'

export const healthApi = {
  getHealth: () => get<HealthResponse>('/health'),
}
