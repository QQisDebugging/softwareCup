import { get, post } from '@/api/http'
import type {
  CreateResourceTaskRequest,
  GenerationAudit,
  GenerationTask,
  ModelInvocation,
  TaskStep,
} from '@/types/api'

export const tasksApi = {
  createResourceGeneration: (body: CreateResourceTaskRequest) =>
    post<GenerationTask, CreateResourceTaskRequest>('/tasks/resource-generation', body),
  list: () => get<GenerationTask[]>('/tasks'),
  get: (taskId: string) => get<GenerationTask>(`/tasks/${taskId}`),
  steps: (taskId: string) => get<TaskStep[]>(`/tasks/${taskId}/steps`),
  modelInvocations: (taskId: string) => get<ModelInvocation[]>(`/tasks/${taskId}/model-invocations`),
  audits: (taskId: string) => get<GenerationAudit[]>(`/tasks/${taskId}/audits`),
}
