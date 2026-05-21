import { asObject, get } from '@/api/http'
import type { HealthResponse } from '@/types/api'

export const healthApi = {
  getHealth: async () => asObject<HealthResponse>(await get<unknown>('/health'), { service: 'software-cup-learning-backend', status: 'UNKNOWN' }),
}
