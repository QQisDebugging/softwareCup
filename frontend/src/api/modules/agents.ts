import { get, post } from '@/api/http'
import type { AgentArtifact, AgentDefinition } from '@/types/api'

export const agentsApi = {
  definitions: () => get<AgentDefinition[]>('/agents'),
  artifacts: (params: { studentProfileId?: string; courseId?: string }) => get<AgentArtifact[]>('/agent-artifacts', params),
  invoke: (endpoint: string, body: unknown) => post<Record<string, unknown>, unknown>(endpoint, body),
}
