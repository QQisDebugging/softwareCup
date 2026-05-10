import { get, post } from '@/api/http'
import type { ContestReadinessReport } from '@/types/api'

export const demoApi = {
  readinessReport: (params: { studentProfileId?: string; courseId?: string; taskId?: string }) =>
    get<ContestReadinessReport>('/demo/readiness-report', params),
  scenarioPlan: (body: unknown) => post<Record<string, unknown>, unknown>('/demo/scenario-plans', body),
}
