<script setup lang="ts">
import { BrainCircuit, CheckCircle2, Clock, Download, FileText, Radio, RefreshCw, Route, ShieldCheck, UploadCloud, X } from 'lucide-vue-next'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiBaseUrl, coursesApi, learningApi, tasksApi, uploadsApi } from '@/api'
import ErrorNotice from '@/components/ErrorNotice.vue'
import LoadingBlock from '@/components/LoadingBlock.vue'
import MarkdownView from '@/components/MarkdownView.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import StatusPill from '@/components/StatusPill.vue'
import { useAppStore } from '@/stores/app'
import type { GenerationAudit, GenerationTask, LearningResource, ModelInvocation, TaskStep, UploadAsset } from '@/types/api'
import { downloadJson, downloadText, safeFilePart } from '@/utils/download'
import { cleanDisplayText, compact, formatDate, percent } from '@/utils/format'

const route = useRoute()
const router = useRouter()
const app = useAppStore()
const taskId = computed(() => String(route.params.taskId || ''))
const isTeacher = computed(() => app.role === 'teacher')
const isStudent = computed(() => app.role === 'student')
const loading = ref(false)
const publishing = ref(false)
const actionBusy = ref('')
const error = ref('')
const task = ref<GenerationTask | null>(null)
const steps = ref<TaskStep[]>([])
const invocations = ref<ModelInvocation[]>([])
const audits = ref<GenerationAudit[]>([])
const resources = ref<LearningResource[]>([])
const eventLog = ref<string[]>([])
const sseStatus = ref<'connecting' | 'connected' | 'closed'>('closed')
const sseMessage = ref('')
let eventSource: EventSource | null = null

// --- 提交实验报告 ---
const reportModalOpen = ref(false)
const reportFile = ref<File | null>(null)
const reportNote = ref('')
const reportSubmitting = ref(false)
const reportSuccess = ref(false)
const reportError = ref('')
const reportFileInput = ref<HTMLInputElement | null>(null)
const submittedReports = ref<UploadAsset[]>([])

function openReportModal() {
  reportModalOpen.value = true
  reportFile.value = null
  reportNote.value = ''
  reportSuccess.value = false
  reportError.value = ''
}

function closeReportModal() {
  reportModalOpen.value = false
}

function onReportFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  reportFile.value = input.files?.[0] ?? null
}

async function submitReport() {
  if (!reportFile.value) {
    reportError.value = '请先选择要上传的实验报告文件。'
    return
  }
  if (!task.value?.courseId) {
    reportError.value = '无法提交：当前任务没有绑定课程。'
    return
  }
  reportSubmitting.value = true
  reportError.value = ''
  try {
    const uploaded = await uploadsApi.uploadCourseMaterial(reportFile.value, {
      courseId: task.value.courseId,
      role: 'student',
    })
    submittedReports.value = [uploaded, ...submittedReports.value]
    // Record a learning event for the submission
    if (task.value.studentProfileId) {
      await learningApi.recordEvent({
        studentProfileId: task.value.studentProfileId,
        courseId: task.value.courseId,
        resourceId: task.value.createdResourceId || null,
        eventType: 'ASSIGNMENT_SUBMIT',
        durationSeconds: 60,
        feedbackScore: 5,
        eventPayload: JSON.stringify({
          taskId: task.value.id,
          taskTopic: task.value.topic,
          reportFilename: reportFile.value.name,
          note: reportNote.value,
          uploadId: uploaded.id,
          source: 'task-report-submit',
        }),
      })
    }
    reportSuccess.value = true
    reportFile.value = null
    reportNote.value = ''
    if (reportFileInput.value) reportFileInput.value.value = ''
  } catch (err) {
    reportError.value = err instanceof Error ? err.message : '上传失败，请重试。'
  } finally {
    reportSubmitting.value = false
  }
}

const createdResource = computed(() =>
  resources.value.find((item) => item.id === task.value?.createdResourceId || item.sourceTaskId === task.value?.id),
)
const taskResources = computed(() => resources.value.filter((item) => item.sourceTaskId === task.value?.id))
const unpublishedTaskResources = computed(() => taskResources.value.filter((item) => item.reviewStatus !== 'PUBLISHED'))
const publishedTaskResources = computed(() => taskResources.value.filter((item) => item.reviewStatus === 'PUBLISHED'))
const visibleTaskResources = computed(() => (isTeacher.value ? taskResources.value : publishedTaskResources.value))
const resourceMarkdown = computed(() => createdResource.value?.content || task.value?.resultSummary || '')
const resourcePreviewTitle = computed(() => createdResource.value?.title || task.value?.topic || '等待学习资源')
const resourcePreviewBody = computed(() =>
  displayText(resourceMarkdown.value || task.value?.resultSummary || '任务完成后会在这里预览生成正文，完整内容仍保留在页面下方。', 420),
)
const deliveryResourceList = computed(() => {
  if (visibleTaskResources.value.length) return visibleTaskResources.value.slice(0, 4)
  if (isStudent.value && taskResources.value.length) return taskResources.value.slice(0, 2)
  if (!createdResource.value && task.value?.createdResourceId) {
    return [
      {
        id: task.value.createdResourceId,
        title: task.value.topic || '生成资源',
        resourceType: task.value.taskType || 'RESOURCE',
        resourceTypeName: '生成资源',
        estimatedMinutes: 0,
        reviewStatus: task.value.status === 'SUCCEEDED' ? 'READY_TO_PUBLISH' : 'REVIEWING',
      } as LearningResource,
    ]
  }
  return []
})
const taskProgress = computed(() => Math.round(percent(task.value?.progressPercent || 0)))
const currentProductionStage = computed(() => displayProductionStage(task.value?.currentStep || steps.value.find((item) => statusTone(item.status) === 'warn')?.stepName))
const canDownloadAudit = computed(() => isTeacher.value && audits.value.length > 0)
const canPublishResources = computed(
  () => isTeacher.value && task.value?.status === 'SUCCEEDED' && unpublishedTaskResources.value.length > 0 && !publishing.value,
)
const completedStepCount = computed(() => steps.value.filter((item) => statusTone(item.status) === 'ok').length)
const passedAuditCount = computed(() => audits.value.filter((item) => statusTone(item.status) === 'ok').length)
const reviewAuditCount = computed(() => audits.value.filter((item) => item.reviewerRequired).length)
const averageLatency = computed(() => {
  if (!invocations.value.length) return 0
  const total = invocations.value.reduce((sum, item) => sum + Number(item.latencyMs || 0), 0)
  return Math.round(total / invocations.value.length)
})
const evidenceMetrics = computed(() => {
  if (isStudent.value) {
    return [
      { label: '生成进度', value: `${taskProgress.value}%`, detail: currentProductionStage.value || '等待资源生成', icon: Route },
      {
        label: '学习资源',
        value: publishedTaskResources.value.length ? `${publishedTaskResources.value.length}` : '待开放',
        detail: publishedTaskResources.value.length ? '已进入课程空间' : '等待教师确认后开放学习',
        icon: FileText,
      },
      { label: '正文状态', value: resourceMarkdown.value ? '已生成' : '等待中', detail: resourceMarkdown.value ? '可阅读或下载学习资料' : '资源生成完成后显示正文', icon: BrainCircuit },
      {
        label: '课程状态',
        value: publishedTaskResources.value.length ? '可学习' : '待开放',
        detail: publishedTaskResources.value.length ? '可回到课程继续学习' : '当前仅展示生成进度',
        icon: Clock,
      },
    ]
  }
  return [
    { label: '生成进度', value: `${taskProgress.value}%`, detail: currentProductionStage.value || '等待资源生成', icon: Route },
    { label: '处理进度', value: `${completedStepCount.value}/${steps.value.length || 0}`, detail: '已完成 / 总阶段', icon: BrainCircuit },
    { label: '审核记录', value: `${passedAuditCount.value}/${audits.value.length || 0}`, detail: reviewAuditCount.value ? `${reviewAuditCount.value} 项需教师复核` : '安全审核信息', icon: ShieldCheck },
    { label: '处理记录', value: `${invocations.value.length}`, detail: averageLatency.value ? `平均约 ${averageLatency.value} 毫秒` : '等待处理信息', icon: Clock },
  ]
})
const evidenceCards = computed(() => [
  {
    title: '生成进度',
    value: `${steps.value.length || 0} 个阶段`,
    detail: steps.value.length ? steps.value.map((item) => displayProductionStage(item.stepName || item.agentKey || item.status)).slice(0, 3).join('、') : '等待任务进度',
    icon: Route,
  },
  {
    title: '审核要求',
    value: `${audits.value.length || 0} 条记录`,
    detail: reviewAuditCount.value ? `${reviewAuditCount.value} 条需要教师复核` : '内容安全、准确性和适配度检查',
    icon: ShieldCheck,
  },
  {
    title: '资源交付',
    value: taskResources.value.length ? `${taskResources.value.length} 个资源` : '等待资源',
    detail: createdResource.value?.title || task.value?.topic || '任务完成后生成学习资源',
    icon: FileText,
  },
  {
    title: '处理记录',
    value: `${invocations.value.length || 0} 条记录`,
    detail: averageLatency.value ? `平均响应约 ${averageLatency.value} 毫秒` : '等待处理信息',
    icon: Radio,
  },
])
const teacherReadinessItems = computed(() => [
  {
    label: '任务完成',
    title: task.value?.status === 'SUCCEEDED' ? '生成任务已完成' : '等待任务完成',
    detail: currentProductionStage.value || '资源生成完成后才能进入发布确认。',
    ready: task.value?.status === 'SUCCEEDED',
  },
  {
    label: '资源正文',
    title: taskResources.value.length ? `${taskResources.value.length} 个资源待确认` : '等待资源正文',
    detail: createdResource.value?.title || '资源生成后会形成可预览、可下载、可发布的正文。',
    ready: taskResources.value.length > 0 || Boolean(resourceMarkdown.value),
  },
  {
    label: '审核证据',
    title: audits.value.length ? `${passedAuditCount.value}/${audits.value.length} 项通过` : '等待审核证据',
    detail: reviewAuditCount.value ? `${reviewAuditCount.value} 项需要教师确认。` : '内容安全、学术准确性和课程证据将作为发布依据。',
    ready: audits.value.length > 0 && reviewAuditCount.value === 0,
  },
  {
    label: '学生可见',
    title: unpublishedTaskResources.value.length ? `${unpublishedTaskResources.value.length} 个资源未发布` : taskResources.value.length ? '已进入课程空间' : '等待发布',
    detail: '教师确认后学生端课程空间才能看到资源。',
    ready: taskResources.value.length > 0 && unpublishedTaskResources.value.length === 0,
  },
])
const studentLearningItems = computed(() => [
  {
    label: '学习资源',
    title: publishedTaskResources.value.length ? `${publishedTaskResources.value.length} 个资源可学习` : taskResources.value.length ? '等待教师开放' : '资源生成中',
    detail: publishedTaskResources.value.length ? '资源已进入课程空间，可以继续学习和下载正文。' : '生成结果需要教师复核后才会进入学生课程空间。',
    ready: publishedTaskResources.value.length > 0,
  },
  {
    label: '正文内容',
    title: resourceMarkdown.value ? '正文已生成' : '等待正文生成',
    detail: resourceMarkdown.value ? '可以阅读或下载当前资源正文。' : '资源生成完成后会展示学习正文。',
    ready: Boolean(resourceMarkdown.value),
  },
  {
    label: '学习进度',
    title: task.value?.status === 'SUCCEEDED' ? '生成流程已完成' : currentProductionStage.value || '生成流程进行中',
    detail: '这里展示学习资源的生成进度，不提供教师工作台操作。',
    ready: task.value?.status === 'SUCCEEDED',
  },
  {
    label: '课程空间',
    title: publishedTaskResources.value.length ? '可在课程中学习' : '暂未进入课程空间',
    detail: '开放后的资源会在我的课程中持续可见。',
    ready: publishedTaskResources.value.length > 0,
  },
])
const roleReadinessItems = computed(() => (isTeacher.value ? teacherReadinessItems.value : studentLearningItems.value))
const taskNextActions = computed(() => {
  if (!task.value) return ['从资源生成页创建任务', '等待任务记录同步']
  if (task.value.status !== 'SUCCEEDED') return ['等待资源生成完成', '查看实时进度或刷新任务详情']
  if (isStudent.value) {
    if (publishedTaskResources.value.length) return ['阅读或下载学习资源正文', '进入课程空间继续学习并记录反馈']
    return ['等待教师确认并开放资源', '可先查看生成进度和资源正文预览']
  }
  if (reviewAuditCount.value) return ['逐项复核审核提示', '确认事实、引用和课程适配性']
  if (unpublishedTaskResources.value.length) return ['发布资源给学生', '发布后在课程空间检查可见性']
  return ['进入课程空间查看资源', '让学生学习并记录反馈']
})
const resourceStageBlueprint = [
  {
    key: 'profile-match',
    title: '画像匹配',
    desc: '读取学生基础、目标、偏好和薄弱点',
    icon: BrainCircuit,
    matchers: ['profile', '画像', 'student'],
  },
  {
    key: 'knowledge-diagnosis',
    title: '知识诊断',
    desc: '对齐课程知识点、主题和已有掌握证据',
    icon: BrainCircuit,
    matchers: ['diagnos', 'prereq', '诊断', '分析'],
  },
  {
    key: 'learning-path',
    title: '路径规划',
    desc: '规划学习顺序、资源组合和时间预算',
    icon: Route,
    matchers: ['plan', 'path', 'route', '规划', '路径'],
  },
  {
    key: 'resource-package',
    title: '多资源生成',
    desc: '协作产出讲解文档、导图、练习、阅读、脚本和案例',
    icon: FileText,
    matchers: ['resource', 'generate', 'quiz', 'mind', 'document', '生成', '资源'],
  },
  {
    key: 'content-verification',
    title: '事实与安全核验',
    desc: '校验引用覆盖、学术准确性和内容安全',
    icon: ShieldCheck,
    matchers: ['audit', 'safety', 'review', '审核', '安全'],
  },
  {
    key: 'publish-ready',
    title: '推送评估',
    desc: '形成资源正文、学习记录和后续推荐证据',
    icon: CheckCircle2,
    matchers: ['evaluate', 'push', 'report', 'finish', '评估', '报告', '完成'],
  },
]
const resourceProcessingStages = computed(() =>
  resourceStageBlueprint.map((item, index) => {
    const step =
      steps.value.find((candidate) => {
        const text = `${candidate.agentKey} ${candidate.stepName}`.toLowerCase()
        return item.matchers.some((matcher) => text.includes(matcher))
      }) || steps.value[index]
    const status = step?.status || (task.value ? 'WAITING' : 'PENDING')
    return {
      ...item,
      title: isStudent.value && item.key === 'content-verification' ? '质量检查' : isStudent.value && item.key === 'publish-ready' ? '学习资料整理' : item.title,
      desc: isStudent.value && item.key === 'content-verification' ? '检查学习资料的准确性、适配度和可读性' : isStudent.value && item.key === 'publish-ready' ? '整理资源正文、学习记录和后续推荐' : item.desc,
      status,
      progress: Math.round(percent(step?.progressPercent || 0)),
      summary: displayText(step?.outputSummary || step?.inputSummary || item.desc, 130),
      stepName: step?.stepName || item.title,
      durationMs: step?.durationMs,
      tone: statusTone(status),
    }
  }),
)

function statusTone(status?: string | null): 'ok' | 'warn' | 'danger' | 'info' | 'muted' {
  const value = String(status || '').toUpperCase()
  if (['SUCCEEDED', 'SUCCESS', 'PASSED', 'UP', 'COMPLETED'].includes(value)) return 'ok'
  if (['FAILED', 'ERROR', 'REJECTED', 'BLOCKED'].includes(value)) return 'danger'
  if (['RUNNING', 'PENDING', 'PROCESSING', 'UNKNOWN'].includes(value)) return 'warn'
  return 'info'
}

function displayText(value: unknown, maxLength?: number) {
  const text = cleanDisplayText(String(value || ''))
  return maxLength ? compact(text, maxLength) : text
}

function statusLabel(status?: string | null) {
  const value = String(status || '').toUpperCase()
  const labels: Record<string, string> = {
    SUCCEEDED: '已完成',
    SUCCESS: '已完成',
    PASSED: '已通过',
    COMPLETED: '已完成',
    RUNNING: '进行中',
    PROCESSING: '生成中',
    PENDING: '等待中',
    WAITING: '等待中',
    UNKNOWN: '确认中',
    FAILED: '未完成',
    ERROR: '处理失败',
    REJECTED: '未通过',
    REVIEW_REQUIRED: '需复核',
    BLOCKED: '已暂停',
  }
  return labels[value] || status || '确认中'
}

function displayProductionStage(value?: string | null) {
  const text = String(value || '').toLowerCase()
  if (!text) return '等待资源生成'
  if (text.includes('profile') || text.includes('画像') || text.includes('student')) return '画像与需求匹配'
  if (text.includes('diagnos') || text.includes('knowledge') || text.includes('prereq') || text.includes('诊断') || text.includes('分析')) return '知识点诊断'
  if (text.includes('plan') || text.includes('path') || text.includes('route') || text.includes('规划') || text.includes('路径')) return '学习路径规划'
  if (text.includes('quiz') || text.includes('mind') || text.includes('document') || text.includes('ppt') || text.includes('resource') || text.includes('generate') || text.includes('生成') || text.includes('资源')) return '多类型资源生成'
  if (text.includes('audit') || text.includes('safety') || text.includes('review') || text.includes('审核') || text.includes('安全')) return isStudent.value ? '质量检查' : '内容审核'
  if (text.includes('evaluate') || text.includes('push') || text.includes('report') || text.includes('finish') || text.includes('评估') || text.includes('报告') || text.includes('完成')) return isStudent.value ? '学习资料整理' : '交付与发布准备'
  return compact(String(value), 42)
}

function auditTypeLabel(type?: string | null) {
  const value = String(type || '').toUpperCase()
  const labels: Record<string, string> = {
    CONTENT_SAFETY: '内容安全审核',
    ACADEMIC_ACCURACY: '学术准确性审核',
    COURSE_EVIDENCE: '课程证据审核',
    HUMAN_REVIEW_GATE: '教师复核要求',
  }
  return labels[value] || type || '审核记录'
}

function reviewStatusLabel(status?: string | null) {
  const value = String(status || '').toUpperCase()
  if (value === 'PUBLISHED') return '已发布'
  if (value === 'READY_TO_PUBLISH') return '可发布'
  if (value === 'REVIEW_REQUIRED') return '需复核'
  if (value === 'REVIEWING') return '审核中'
  return value || '待审核'
}

function learnerResourceStatusLabel(status?: string | null) {
  const value = String(status || '').toUpperCase()
  if (value === 'PUBLISHED') return '可学习'
  if (value === 'READY_TO_PUBLISH') return '待教师开放'
  if (value === 'REVIEW_REQUIRED') return '教师复核中'
  if (value === 'REVIEWING') return '生成检查中'
  return value || '处理中'
}

function roleResourceStatusLabel(status?: string | null) {
  return isTeacher.value ? reviewStatusLabel(status) : learnerResourceStatusLabel(status)
}

function reviewStatusTone(status?: string | null): 'ok' | 'warn' | 'danger' | 'info' | 'muted' {
  const value = String(status || '').toUpperCase()
  if (value === 'PUBLISHED') return 'ok'
  if (value === 'READY_TO_PUBLISH') return 'info'
  if (value === 'REVIEW_REQUIRED') return 'warn'
  if (value === 'REVIEWING') return 'muted'
  return 'muted'
}

async function loadAll() {
  if (!taskId.value) {
    error.value = '任务 ID 为空，请从资源生成页面重新进入任务详情。'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const taskResult = await tasksApi.get(taskId.value)
    task.value = taskResult
    const [stepResult, invocationResult, auditResult] = await Promise.allSettled([
      tasksApi.steps(taskId.value),
      isTeacher.value ? tasksApi.modelInvocations(taskId.value) : Promise.resolve([]),
      isTeacher.value ? tasksApi.audits(taskId.value) : Promise.resolve([]),
    ])
    steps.value = stepResult.status === 'fulfilled' ? stepResult.value : []
    invocations.value = invocationResult.status === 'fulfilled' ? invocationResult.value : []
    audits.value = auditResult.status === 'fulfilled' ? auditResult.value : []
    if (taskResult.courseId) {
      try {
        resources.value = await coursesApi.resources(taskResult.courseId, { publishedOnly: !isTeacher.value })
      } catch {
        resources.value = []
      }
    }
    const failures = [stepResult, invocationResult, auditResult].filter((item) => item.status === 'rejected').length
    if (failures) error.value = `任务主体已加载，但有 ${failures} 个明细暂未同步，可稍后刷新。`
  } catch (err) {
    error.value = err instanceof Error ? err.message : '任务加载失败'
  } finally {
    loading.value = false
  }
}

function connectSse() {
  if (!taskId.value) return
  eventSource?.close()
  sseStatus.value = 'connecting'
  sseMessage.value = ''
  try {
    eventSource = new EventSource(`${apiBaseUrl}/tasks/${taskId.value}/events`)
  } catch {
    sseStatus.value = 'closed'
    sseMessage.value = '实时连接创建失败，可手动刷新任务详情。'
    return
  }
  eventSource.onopen = () => {
    sseStatus.value = 'connected'
  }
  eventSource.onmessage = (event) => {
    eventLog.value.unshift(event.data)
    if (eventLog.value.length > 8) eventLog.value.pop()
    void loadAll()
  }
  eventSource.onerror = () => {
    eventSource?.close()
    eventSource = null
    sseStatus.value = 'closed'
    sseMessage.value = '实时连接已断开，可手动刷新任务详情。'
  }
}

function downloadTaskJson() {
  downloadJson(`${safeFilePart(task.value?.topic || 'task')}-task.json`, {
    task: task.value,
    steps: steps.value,
    invocations: invocations.value,
    audits: audits.value,
    resource: createdResource.value,
  })
}

function downloadAuditJson() {
  if (!canDownloadAudit.value) return
  downloadJson(`${safeFilePart(task.value?.topic || 'task')}-audit.json`, audits.value)
}

function downloadMarkdown() {
  if (!resourceMarkdown.value) {
    error.value = '当前任务还没有可下载的资源正文，请刷新或等待资源生成完成。'
    return
  }
  downloadText(`${safeFilePart(createdResource.value?.title || task.value?.topic || 'resource')}.md`, resourceMarkdown.value, 'text/markdown;charset=utf-8')
}

function downloadLearningResources() {
  if (visibleTaskResources.value.length) {
    visibleTaskResources.value.forEach((resource) => {
      if (resource.content) {
        downloadText(`${safeFilePart(resource.title || 'learning-resource')}.md`, resource.content, 'text/markdown;charset=utf-8')
      }
    })
    if (!visibleTaskResources.value.some((resource) => resource.content)) {
      error.value = '资源已开放，但当前资源没有正文内容可下载。'
    }
    return
  }
  downloadMarkdown()
}

async function continueLearning() {
  if (!task.value?.courseId) {
    error.value = '无法继续学习：当前任务没有绑定课程。'
    return
  }
  if (!task.value.studentProfileId) {
    error.value = '无法继续学习：当前任务没有绑定学生画像。'
    return
  }
  if (isStudent.value && !publishedTaskResources.value.length && !resourceMarkdown.value) {
    error.value = '资源尚未开放或正文未生成，暂时不能继续学习。'
    return
  }
  const resource = createdResource.value || publishedTaskResources.value[0] || visibleTaskResources.value[0]
  actionBusy.value = 'continue'
  error.value = ''
  try {
    await learningApi.recordEvent({
      studentProfileId: task.value.studentProfileId,
      courseId: task.value.courseId,
      resourceId: resource?.id || task.value.createdResourceId || null,
      eventType: 'TASK_CONTINUE_LEARNING',
      durationSeconds: 30,
      feedbackScore: 4,
      eventPayload: JSON.stringify({
        taskId: task.value.id,
        taskTopic: task.value.topic,
        resourceTitle: resource?.title || resourcePreviewTitle.value,
      }),
    })
    await router.push({
      path: '/learning',
      query: {
        tab: 'chat',
        courseId: task.value.courseId,
        taskId: task.value.id,
        resourceId: resource?.id || undefined,
        question: task.value.topic ? `请带我继续学习「${task.value.topic}」，并记录我完成后的反馈。` : undefined,
      },
    })
  } catch (err) {
    error.value = err instanceof Error ? err.message : '继续学习事件写回失败。'
  } finally {
    actionBusy.value = ''
  }
}

function backToCourse() {
  if (!task.value?.courseId) {
    error.value = '无法回到课程：当前任务没有绑定课程。'
    return
  }
  void router.push(`/courses/${task.value.courseId}`)
}

async function markResourceComplete() {
  if (!task.value) {
    error.value = '任务尚未加载，不能标记完成。'
    return
  }
  if (!task.value.studentProfileId || !task.value.courseId) {
    error.value = '无法标记完成：缺少学生画像或课程 ID。'
    return
  }
  const resource = createdResource.value || publishedTaskResources.value[0] || visibleTaskResources.value[0]
  actionBusy.value = 'complete'
  error.value = ''
  try {
    await learningApi.recordEvent({
      studentProfileId: task.value.studentProfileId,
      courseId: task.value.courseId,
      resourceId: resource?.id || task.value.createdResourceId || null,
      eventType: 'RESOURCE_COMPLETE',
      durationSeconds: Math.max(60, Number(resource?.estimatedMinutes || 10) * 60),
      feedbackScore: 5,
      eventPayload: JSON.stringify({
        taskId: task.value.id,
        taskTopic: task.value.topic,
        resourceTitle: resource?.title || resourcePreviewTitle.value,
        source: 'task-detail',
      }),
    })
    await loadAll()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '标记完成失败，请确认学习事件接口可用。'
  } finally {
    actionBusy.value = ''
  }
}

async function publishResources() {
  if (!task.value || !canPublishResources.value) return
  publishing.value = true
  error.value = ''
  try {
    await tasksApi.publish(task.value.id, {
      publisherName: app.currentUser.name,
      publishNote: reviewAuditCount.value
        ? `教师已复核 ${reviewAuditCount.value} 项审核提示，并确认可进入学生课程空间。`
        : '教师确认自动审核证据，通过后发布给学生。',
    })
    await loadAll()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '资源发布失败'
  } finally {
    publishing.value = false
  }
}

onMounted(() => {
  void loadAll()
  connectSse()
})

onBeforeUnmount(() => eventSource?.close())
</script>

<template>
  <div class="page-grid">
    <section class="dashboard-workbench task-workbench span-12">
      <div class="dashboard-workbench-head">
        <div>
          <h2>{{ displayText(task?.topic) || (isTeacher ? '资源包审核与发布' : '学习资源详情') }}</h2>
        </div>
        <div class="home-action-row">
          <button class="button" @click="loadAll"><RefreshCw :size="17" />刷新</button>
          <button v-if="isStudent" class="button" type="button" @click="continueLearning"><Route :size="17" />继续学习</button>
          <button v-if="isStudent" class="button" type="button" @click="openReportModal"><UploadCloud :size="17" />提交实验报告</button>
          <button v-if="isStudent" class="ghost-button" type="button" :disabled="actionBusy === 'complete'" @click="markResourceComplete">
            <CheckCircle2 :size="17" />标记完成
          </button>
          <button v-if="isStudent" class="ghost-button" type="button" @click="backToCourse"><FileText :size="17" />回到课程</button>
          <button v-if="isTeacher" class="ghost-button" :disabled="!task" @click="downloadTaskJson"><Download :size="17" />证据包</button>
          <button v-if="isTeacher" class="ghost-button" :disabled="!canDownloadAudit" @click="downloadAuditJson"><Download :size="17" />审核证据</button>
          <button class="ghost-button" @click="downloadLearningResources"><Download :size="17" />{{ isTeacher ? '下载资源正文' : '下载学习资料' }}</button>
          <button v-if="isTeacher" class="button" :disabled="!canPublishResources" @click="publishResources"><CheckCircle2 :size="17" />发布给学生</button>
        </div>
      </div>
      <ErrorNotice :message="error" />
      <LoadingBlock :show="loading" />
      <div v-if="!task && !loading" class="empty-guide">
        <strong>任务暂未加载</strong>
      </div>
      <div v-if="task" class="task-command-panel">
        <div class="task-command-copy">
          <div class="button-row">
            <StatusPill :status="statusLabel(task.status)" :tone="statusTone(task.status)" />
            <StatusPill :status="currentProductionStage || '等待资源生成'" tone="info" />
          </div>
          <h3>{{ displayText(task.topic) }}</h3>
          <small>创建 {{ formatDate(task.createdAt) }} / 更新 {{ formatDate(task.updatedAt) }}</small>
          <div v-if="taskResources.length || publishedTaskResources.length" class="button-row">
            <StatusPill :status="`${visibleTaskResources.length || taskResources.length} 个资源`" tone="info" />
            <StatusPill v-if="isTeacher" :status="`${unpublishedTaskResources.length} 个待发布`" :tone="unpublishedTaskResources.length ? 'warn' : 'ok'" />
            <StatusPill v-else :status="publishedTaskResources.length ? '已开放到课程' : '等待教师开放'" :tone="publishedTaskResources.length ? 'ok' : 'warn'" />
          </div>
        </div>
        <div class="task-resource-preview-card">
          <div class="task-resource-preview-head">
            <div>
              <span>{{ isTeacher ? '生成资源预览' : '学习资源预览' }}</span>
              <strong>{{ displayText(resourcePreviewTitle, 64) }}</strong>
            </div>
            <StatusPill :status="roleResourceStatusLabel(createdResource?.reviewStatus || (task.status === 'SUCCEEDED' ? 'READY_TO_PUBLISH' : 'REVIEWING'))" :tone="reviewStatusTone(createdResource?.reviewStatus || (task.status === 'SUCCEEDED' ? 'READY_TO_PUBLISH' : 'REVIEWING'))" />
          </div>
          <p>{{ resourcePreviewBody }}</p>
          <div v-if="deliveryResourceList.length" class="task-delivery-list">
            <div v-for="resource in deliveryResourceList" :key="resource.id">
              <FileText :size="16" />
              <span>{{ displayText(resource.title, 42) }}</span>
              <StatusPill :status="roleResourceStatusLabel(resource.reviewStatus)" :tone="reviewStatusTone(resource.reviewStatus)" />
            </div>
          </div>
          <div v-else class="task-delivery-empty">
            <FileText :size="16" />
          </div>
        </div>
        <div class="task-progress-card">
          <strong>{{ taskProgress }}%</strong>
          <span>资源生成进度</span>
          <div class="progress-track"><div class="progress-fill" :style="{ width: `${taskProgress}%` }" /></div>
          <small>{{ isTeacher ? `${steps.length || 0} 个阶段 · ${audits.length || 0} 条审核 · ${invocations.length || 0} 条处理记录` : `${steps.length || 0} 个阶段 · ${visibleTaskResources.length || 0} 个可学资源 · ${invocations.length || 0} 条生成记录` }}</small>
          <p v-if="task.errorMessage" class="field-error">{{ task.errorMessage }}</p>
          <LoadingBlock v-if="isTeacher" :show="publishing" text="正在发布资源给学生" />
        </div>
      </div>
      <div v-if="task" class="task-publish-board" :aria-label="isTeacher ? '发布准备' : '学习状态'">
        <div v-for="item in roleReadinessItems" :key="item.label" :class="{ ready: item.ready }">
          <StatusPill :status="item.label" :tone="item.ready ? 'ok' : 'warn'" />
          <strong>{{ item.title }}</strong>
        </div>
      </div>
      <div v-if="task" class="task-next-actions" aria-label="下一步动作">
        <strong>下一步</strong>
        <span v-for="item in taskNextActions" :key="item">{{ item }}</span>
      </div>
    </section>

    <div class="task-evidence-grid span-12">
      <article v-for="item in evidenceMetrics" :key="item.label" class="metric-tile">
        <component :is="item.icon" :size="20" />
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
        <small>{{ item.detail }}</small>
      </article>
    </div>

    <SectionPanel class="span-12" title="资源处理进度" :subtitle="isTeacher ? '按画像匹配、知识诊断、路径规划、资源生成、内容审核和发布准备追踪进度' : '按画像匹配、知识诊断、路径规划和资源生成追踪学习资料进度'">
      <div class="task-stage-lane">
        <article v-for="item in resourceProcessingStages" :key="item.key" class="task-stage-card">
          <div class="task-stage-top">
            <component :is="item.icon" :size="19" />
            <StatusPill :status="statusLabel(item.status)" :tone="item.tone" />
          </div>
          <strong>{{ item.title }}</strong>
          <small>{{ displayProductionStage(item.stepName) }}</small>
          <p>{{ item.summary }}</p>
          <div class="progress-track"><div class="progress-fill" :style="{ width: `${item.progress}%` }" /></div>
          <small>{{ statusLabel(item.status) }}<span v-if="item.durationMs"> / {{ item.durationMs }} 毫秒</span></small>
        </article>
      </div>
    </SectionPanel>

    <SectionPanel class="span-7" title="处理记录">
      <div v-if="!steps.length" class="empty-state">暂无处理记录</div>
      <div v-else class="timeline">
        <div v-for="step in steps" :key="step.id" class="timeline-item">
          <span class="timeline-index">{{ step.stepOrder }}</span>
          <div class="timeline-body">
            <div class="section-head">
              <div>
                <h3>{{ displayProductionStage(step.stepName || step.agentKey) }}</h3>
                <p>已记录本阶段输入、输出摘要和处理状态</p>
              </div>
              <StatusPill :status="statusLabel(step.status)" :tone="statusTone(step.status)" />
            </div>
            <p>{{ displayText(step.outputSummary || step.inputSummary, 180) }}</p>
            <p v-if="step.errorMessage" class="field-error">{{ step.errorMessage }}</p>
            <div class="progress-track"><div class="progress-fill" :style="{ width: `${Math.round(percent(step.progressPercent))}%` }" /></div>
          </div>
        </div>
      </div>
    </SectionPanel>

    <SectionPanel class="span-5" title="实时进度">
      <template #actions>
        <StatusPill
          :status="sseStatus === 'connected' ? '已连接' : sseStatus === 'connecting' ? '连接中' : '已断开'"
          :tone="sseStatus === 'connected' ? 'ok' : sseStatus === 'connecting' ? 'warn' : 'muted'"
        />
        <button class="ghost-button" :disabled="sseStatus === 'connecting'" @click="connectSse"><Radio :size="16" />重连进度</button>
      </template>
      <div v-if="sseMessage" class="notice warn-notice"><span>{{ sseMessage }}</span></div>
        <div v-if="!eventLog.length" class="empty-guide">
          <strong>等待实时进度</strong>
      </div>
      <div v-else class="timeline">
        <div v-for="(event, index) in eventLog" :key="index" class="timeline-body">{{ event }}</div>
      </div>
    </SectionPanel>

    <SectionPanel v-if="isTeacher" class="span-6" title="内容安全与事实核验">
      <div v-if="!audits.length" class="empty-state">暂无审核记录</div>
      <div v-else class="timeline">
        <div v-for="audit in audits" :key="audit.id" class="timeline-body">
          <div class="section-head">
            <strong>{{ auditTypeLabel(audit.auditType) }}</strong>
            <StatusPill :status="audit.reviewerRequired ? `${statusLabel(audit.status)} / 需复核` : statusLabel(audit.status)" :tone="audit.reviewerRequired ? 'warn' : statusTone(audit.status)" />
          </div>
          <p>{{ displayText(audit.evidenceSummary) }}</p>
          <small>{{ formatDate(audit.createdAt) }}</small>
        </div>
      </div>
    </SectionPanel>

    <SectionPanel v-if="isTeacher" class="span-6" title="处理证据">
      <div v-if="!invocations.length" class="empty-state">暂无处理证据</div>
      <div v-else class="task-processing-list">
        <article v-for="item in invocations" :key="item.id">
          <div>
            <strong>{{ displayText(item.promptSummary || item.promptHash, 80) }}</strong>
            <StatusPill :status="statusLabel(item.status)" :tone="statusTone(item.status)" />
          </div>
          <p>处理过程已记录</p>
          <small>响应时长约 {{ item.latencyMs }} 毫秒</small>
        </article>
      </div>
    </SectionPanel>

    <SectionPanel class="span-12" title="生成资源正文">
      <div v-if="!resourceMarkdown" class="empty-guide">
        <strong>任务完成后显示资源正文</strong>
      </div>
      <div v-if="visibleTaskResources.length" class="resource-publish-strip">
        <div v-for="resource in visibleTaskResources" :key="resource.id">
          <strong>{{ displayText(resource.title) }}</strong>
          <span>{{ resource.resourceTypeName || resource.resourceType }} / {{ resource.estimatedMinutes }} 分钟</span>
          <StatusPill :status="roleResourceStatusLabel(resource.reviewStatus)" :tone="reviewStatusTone(resource.reviewStatus)" />
        </div>
      </div>
      <MarkdownView v-if="resourceMarkdown" :content="displayText(resourceMarkdown)" />
    </SectionPanel>

    <SectionPanel v-if="isTeacher" class="span-12" title="审核证据包">
      <div class="task-evidence-grid">
        <article v-for="item in evidenceCards" :key="item.title">
          <component :is="item.icon" :size="18" />
          <span>{{ item.title }}</span>
          <strong>{{ item.value }}</strong>
          <p>{{ item.detail }}</p>
        </article>
      </div>
    </SectionPanel>
  </div>

  <!-- 提交实验报告 Modal -->
  <Teleport to="body">
    <div v-if="reportModalOpen" class="task-report-modal-overlay" @click.self="closeReportModal">
      <div class="task-report-modal">
        <header>
          <div>
            <strong>提交实验报告</strong>
            <small>{{ task?.topic || '当前任务' }}</small>
          </div>
          <button type="button" class="task-report-close" @click="closeReportModal"><X :size="18" /></button>
        </header>

        <div v-if="reportSuccess" class="task-report-success">
          <CheckCircle2 :size="36" />
          <strong>提交成功！</strong>
          <span>你的实验报告已成功上传，教师可在课程资料中查看。</span>
          <button class="button" type="button" @click="closeReportModal">关闭</button>
        </div>

        <form v-else class="task-report-form" @submit.prevent="submitReport">
          <label class="task-report-file-area" :class="{ 'has-file': reportFile }">
            <input
              ref="reportFileInput"
              type="file"
              accept=".pdf,.doc,.docx,.md,.txt,.zip"
              style="display:none"
              @change="onReportFileChange"
            />
            <UploadCloud :size="28" />
            <strong v-if="!reportFile">点击选择实验报告文件</strong>
            <strong v-else>{{ reportFile.name }}</strong>
            <small v-if="!reportFile">支持 PDF、Word、Markdown、TXT、ZIP</small>
            <small v-else>{{ (reportFile.size / 1024).toFixed(1) }} KB · 点击重新选择</small>
            <button type="button" class="ghost-button" @click="reportFileInput?.click()">{{ reportFile ? '重新选择' : '选择文件' }}</button>
          </label>
          <div class="task-report-note">
            <label>备注说明 <em>（可选）</em></label>
            <textarea v-model="reportNote" placeholder="例如：本次实验完成了第三章的数据库连接实验，遇到了连接池配置问题……" rows="3" />
          </div>
          <div v-if="reportError" class="notice error">{{ reportError }}</div>
          <div class="task-report-actions">
            <button type="button" class="ghost-button" @click="closeReportModal">取消</button>
            <button class="button" type="submit" :disabled="!reportFile || reportSubmitting">
              <UploadCloud :size="16" />
              {{ reportSubmitting ? '提交中…' : '确认提交' }}
            </button>
          </div>
        </form>

        <div v-if="submittedReports.length" class="task-report-history">
          <strong>本次会话已提交</strong>
          <div v-for="r in submittedReports" :key="r.id">
            <CheckCircle2 :size="14" />
            <span>{{ r.originalFilename }}</span>
            <small>{{ (r.sizeBytes / 1024).toFixed(1) }} KB</small>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
