import { asApiRecord, asArray, asObject, get, post } from '@/api/http'
import type { AgentArtifact, AgentDefinition } from '@/types/api'

function normalizeDefinition(value: unknown, index: number): AgentDefinition {
  const definition = asObject<AgentDefinition>(value, {
    id: `agent-${index + 1}`,
    agentKey: `agent_${index + 1}`,
    displayName: `智能体 ${index + 1}`,
    responsibility: '',
    inputContract: '',
    outputContract: '',
    sortOrder: index + 1,
  })
  return {
    ...definition,
    id: definition.id || `agent-${index + 1}`,
    agentKey: definition.agentKey || `agent_${index + 1}`,
    displayName: definition.displayName || definition.agentKey || `智能体 ${index + 1}`,
    sortOrder: Number(definition.sortOrder || index + 1),
  }
}

function normalizeArtifact(value: unknown, index: number): AgentArtifact {
  const artifact = asObject<AgentArtifact>(value, {
    id: `artifact-${index + 1}`,
    studentProfileId: '',
    courseId: '',
    artifactType: 'AGENT_ARTIFACT',
    agentEndpoint: '',
    topic: '',
    status: 'UNKNOWN',
    requestSummary: '',
    payloadJson: '',
    citationsJson: '',
    safetySummary: '',
    traceId: '',
    latencyMs: 0,
    errorMessage: null,
    createdAt: '',
  })
  return {
    ...artifact,
    id: artifact.id || `artifact-${index + 1}`,
    artifactType: artifact.artifactType || 'AGENT_ARTIFACT',
    status: artifact.status || 'UNKNOWN',
    latencyMs: Number(artifact.latencyMs || 0),
  }
}

export const agentsApi = {
  definitions: async () => asArray<unknown>(await get<unknown>('/agents')).map(normalizeDefinition),
  artifacts: async (params: { studentProfileId?: string; courseId?: string }) =>
    asArray<unknown>(await get<unknown>('/agent-artifacts', params)).map(normalizeArtifact),
  invoke: async (endpoint: string, body: unknown) => asApiRecord(await post<unknown, unknown>(endpoint, body)),
}
