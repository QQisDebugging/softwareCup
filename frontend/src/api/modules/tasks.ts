import { asArray, asObject, get, post } from '@/api/http'
import type {
  CreateResourceTaskRequest,
  GenerationAudit,
  GenerationTask,
  LearningResource,
  ModelInvocation,
  TaskStep,
} from '@/types/api'

function normalizeTask(value: unknown, fallback: GenerationTask): GenerationTask {
  const task = asObject<GenerationTask>(value, fallback)
  return {
    ...fallback,
    ...task,
    id: task.id || fallback.id,
    taskType: task.taskType || fallback.taskType || 'RESOURCE_GENERATION',
    status: task.status || fallback.status || 'UNKNOWN',
    topic: task.topic || fallback.topic || '未命名任务',
    prompt: task.prompt || fallback.prompt || '',
    resultSummary: task.resultSummary || fallback.resultSummary || '',
    progressPercent: Number(task.progressPercent ?? fallback.progressPercent ?? 0),
    currentStep: task.currentStep || fallback.currentStep || '',
    createdAt: task.createdAt || fallback.createdAt || '',
    updatedAt: task.updatedAt || fallback.updatedAt || '',
  }
}

function normalizeStep(value: unknown, index: number): TaskStep {
  const step = asObject<TaskStep>(value, {
    id: `step-${index + 1}`,
    taskId: '',
    agentKey: '',
    stepOrder: index + 1,
    stepName: `步骤 ${index + 1}`,
    status: 'UNKNOWN',
    inputSummary: '',
    outputSummary: '',
    progressPercent: 0,
    startedAt: null,
    finishedAt: null,
    durationMs: null,
    errorMessage: null,
    updatedAt: '',
  })
  return {
    ...step,
    id: step.id || `step-${index + 1}`,
    stepOrder: Number(step.stepOrder || index + 1),
    stepName: step.stepName || `步骤 ${index + 1}`,
    agentKey: step.agentKey || 'agent',
    status: step.status || 'UNKNOWN',
    progressPercent: Number(step.progressPercent || 0),
  }
}

function normalizeInvocation(value: unknown, index: number): ModelInvocation {
  const record = asObject<Record<string, unknown>>(value, {})
  const invocation = asObject<ModelInvocation>(value, {
    id: `invocation-${index + 1}`,
    taskId: '',
    stepId: '',
    serviceName: '-',
    modelName: '-',
    promptHash: '',
    promptSummary: '',
    latencyMs: 0,
    status: 'UNKNOWN',
    recoveryUsed: false,
    errorMessage: null,
    createdAt: '',
  })
  return {
    ...invocation,
    id: invocation.id || `invocation-${index + 1}`,
    serviceName: invocation.serviceName || String(record['provider'] || '-'),
    modelName: invocation.modelName || '-',
    latencyMs: Number(invocation.latencyMs || 0),
    status: invocation.status || 'UNKNOWN',
    recoveryUsed: Boolean(invocation.recoveryUsed || record['fallbackUsed']),
  }
}

function normalizeAudit(value: unknown, index: number): GenerationAudit {
  const audit = asObject<GenerationAudit>(value, {
    id: `audit-${index + 1}`,
    taskId: '',
    resourceId: '',
    auditType: `审核 ${index + 1}`,
    status: 'UNKNOWN',
    evidenceSummary: '暂无审核证据',
    reviewerRequired: false,
    createdAt: '',
  })
  return {
    ...audit,
    id: audit.id || `audit-${index + 1}`,
    auditType: audit.auditType || `审核 ${index + 1}`,
    status: audit.status || 'UNKNOWN',
    evidenceSummary: audit.evidenceSummary || '暂无审核证据',
    reviewerRequired: Boolean(audit.reviewerRequired),
  }
}

function normalizePublishedResource(value: unknown, index: number): LearningResource {
  const resource = asObject<LearningResource>(value, {
    id: `resource-${index + 1}`,
    courseId: '',
    sourceTaskId: '',
    title: `学习资源 ${index + 1}`,
    resourceType: '',
    resourceTypeName: '',
    modality: '',
    targetLevel: '',
    estimatedMinutes: 0,
    content: '',
    reviewStatus: '',
    publishedAt: null,
    publishedBy: null,
    publishNote: null,
    createdAt: '',
    updatedAt: '',
  })
  return {
    ...resource,
    id: resource.id || `resource-${index + 1}`,
    title: resource.title || `学习资源 ${index + 1}`,
    resourceTypeName: resource.resourceTypeName || resource.resourceType || '资源',
    modality: resource.modality || '文本',
    targetLevel: resource.targetLevel || '-',
    estimatedMinutes: Number(resource.estimatedMinutes || 0),
    content: resource.content || '',
    reviewStatus: resource.reviewStatus || '',
    publishedAt: resource.publishedAt || null,
    publishedBy: resource.publishedBy || null,
    publishNote: resource.publishNote || null,
  }
}

export const tasksApi = {
  createResourceGeneration: async (body: CreateResourceTaskRequest) =>
    normalizeTask(await post<unknown, CreateResourceTaskRequest>('/tasks/resource-generation', body), {
      id: '',
      taskType: 'RESOURCE_GENERATION',
      status: 'UNKNOWN',
      resultSummary: '',
      errorMessage: null,
      createdResourceId: null,
      progressPercent: 0,
      currentStep: '',
      createdAt: '',
      updatedAt: '',
      ...body,
    }),
  list: async () =>
    asArray<unknown>(await get<unknown>('/tasks')).map((item, index) =>
      normalizeTask(item, {
        id: `task-${index + 1}`,
        studentProfileId: '',
        courseId: '',
        taskType: 'RESOURCE_GENERATION',
        status: 'UNKNOWN',
        topic: `任务 ${index + 1}`,
        prompt: '',
        resultSummary: '',
        errorMessage: null,
        createdResourceId: null,
        progressPercent: 0,
        currentStep: '',
        createdAt: '',
        updatedAt: '',
      }),
    ),
  get: async (taskId: string) =>
    normalizeTask(await get<unknown>(`/tasks/${taskId}`), {
      id: taskId,
      studentProfileId: '',
      courseId: '',
      taskType: '',
      status: 'UNKNOWN',
      topic: '',
      prompt: '',
      resultSummary: '',
      errorMessage: null,
      createdResourceId: null,
      progressPercent: 0,
      currentStep: '',
      createdAt: '',
      updatedAt: '',
    }),
  steps: async (taskId: string) => asArray<unknown>(await get<unknown>(`/tasks/${taskId}/steps`)).map(normalizeStep),
  modelInvocations: async (taskId: string) =>
    asArray<unknown>(await get<unknown>(`/tasks/${taskId}/model-invocations`)).map(normalizeInvocation),
  audits: async (taskId: string) => asArray<unknown>(await get<unknown>(`/tasks/${taskId}/audits`)).map(normalizeAudit),
  reviewDecision: async (
    taskId: string,
    body: { decision: 'APPROVED' | 'REJECTED' | 'CHANGES_REQUIRED'; reviewer?: string; note?: string },
  ) => post<unknown, typeof body>(`/tasks/${taskId}/review-decision`, body),
  publish: async (taskId: string, body: { publisherName?: string; publishNote?: string }) =>
    asArray<unknown>(await post<unknown, typeof body>(`/tasks/${taskId}/publish`, body)).map(normalizePublishedResource),
}
