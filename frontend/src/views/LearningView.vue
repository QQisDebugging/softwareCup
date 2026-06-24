<script setup lang="ts">
import type { EChartsOption } from 'echarts'
import { CheckCircle2, Download, RefreshCw, Send, ShieldCheck, Sparkles, Plus, UploadCloud, Paperclip, AtSign, ChevronLeft, MoreHorizontal, Pencil, Trash2, Check, X } from 'lucide-vue-next'
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { coursesApi, learningApi, profilesApi, tasksApi, uploadsApi } from '@/api'
import ChartPanel from '@/components/ChartPanel.vue'
import ErrorNotice from '@/components/ErrorNotice.vue'
import LoadingBlock from '@/components/LoadingBlock.vue'
import MarkdownView from '@/components/MarkdownView.vue'
import MermaidDiagram from '@/components/MermaidDiagram.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import StatusPill from '@/components/StatusPill.vue'
import { useAppStore } from '@/stores/app'
import { useResizablePanels } from '@/composables/useResizablePanels'
import type {
  Course,
  EvaluationReport,
  GenerationTask,
  KnowledgeMastery,
  LearningConversation,
  LearningConversationMessage,
  LearningEvent,
  LearningResource,
  UploadAsset,
  ProfileResponse,
  QuizAttempt,
  ResourceType,
} from '@/types/api'
import { downloadJson, downloadText, safeFilePart } from '@/utils/download'
import { cleanDisplayText, compact, formatDate, isRecord, parseMaybeJson, percent } from '@/utils/format'

interface AssessmentQuestion {
  id: string
  type: string
  stem: string
  options: string[]
  answer: string
  rubric: string
  explanation: string
  difficulty: string
  knowledgePoints: string[]
  score: number
}

type AssistantTab = 'chat' | 'generate' | 'progress' | 'history'

const questionTypeOptions = ['选择题', '判断题', '简答题', '代码纠错题']

const loading = ref(false)
const showCourseList = ref(true)
const app = useAppStore()
const route = useRoute()
const router = useRouter()

// AI 助手工作区两栏（会话列表 / 聊天区）列宽可拖拽并记忆
const {
  gridStyle: chatGridStyle,
  startResize: chatStartResize,
  resetLayout: chatResetLayout,
} = useResizablePanels({
  storageKey: 'learning-chat-v2',
  defaultWeights: [0.18, 0.82],
  minWidths: [280, 640],
  spacing: 16,
})
const historyLoading = ref(false)
const actionLoading = ref('')
const error = ref('')
const profiles = ref<ProfileResponse[]>([])
const courses = ref<Course[]>([])
const resources = ref<LearningResource[]>([])
const tutoringResult = ref<Record<string, unknown> | null>(null)
const assessmentResult = ref<Record<string, unknown> | null>(null)
const gradeResult = ref<Record<string, unknown> | null>(null)
const events = ref<LearningEvent[]>([])
const tutoringHistory = ref<Record<string, unknown>[]>([])
const attempts = ref<QuizAttempt[]>([])
const mastery = ref<KnowledgeMastery[]>([])
const reports = ref<EvaluationReport[]>([])
const resourceTypes = ref<ResourceType[]>([])
const generationTasks = ref<GenerationTask[]>([])
let taskPollTimer: number | null = null
const conversations = ref<LearningConversation[]>([])
const conversationMessages = ref<LearningConversationMessage[]>([])
const activeConversationId = ref('')
const conversationLoading = ref(false)
const conversationApiAvailable = ref(true)
const archivedConversationsVisible = ref(false)
const assistantTab = ref<AssistantTab>('chat')
const referencePanelOpen = ref(false)
const attachmentInput = ref<HTMLInputElement | null>(null)
const uploadingAttachment = ref(false)
const uploadedAttachments = ref<UploadAsset[]>([])
const selectedReferenceResourceIds = ref<string[]>([])
const lastSubmittedQuestion = ref('')

const form = reactive({
  studentProfileId: '',
  courseId: '',
  question: '这个知识点和前后章节有什么关系？我应该先掌握哪一步？',
  modality: '文本+图解',
  topic: '当前章节核心知识点',
  difficulty: '自适应',
  count: 4,
  questionTypes: ['选择题', '判断题', '简答题', '应用题'],
  documentText: '当前课程资料包含核心概念、步骤方法、典型例题和练习反馈，答疑需要结合课程上下文给出可执行建议。',
})

const generationForm = reactive({
  resourceType: 'COURSE_EXPLANATION_DOCUMENT',
  topic: '当前章节速学包',
  modality: '文档+导图+练习',
  prompt: '基于当前课程资料和我的学习画像，生成一份可直接学习的讲义、练习题和知识结构图。',
})

const fallbackResourceTypes: ResourceType[] = [
  { code: 'COURSE_EXPLANATION_DOCUMENT', displayName: '课程讲义' },
  { code: 'QUIZ_PRACTICE', displayName: '练习题' },
  { code: 'KNOWLEDGE_MIND_MAP', displayName: '知识导图' },
  { code: 'PRACTICE_CASE', displayName: '实操案例' },
]

const answers = ref<Record<string, string>>({})

const eventForm = reactive({
  resourceId: '',
  eventType: 'RESOURCE_COMPLETE',
  durationMinutes: 18,
  feedbackScore: 4,
  eventPayload: '完成当前资源学习，仍需要巩固概念关系、步骤迁移和综合应用。',
})

const quizForm = reactive({
  resourceId: '',
  score: 72,
  maxScore: 100,
  correctCount: 6,
  totalCount: 8,
  weakPoints: '核心概念辨析、步骤迁移与综合题表达',
})

const selectedProfile = computed(() => profiles.value.find((item) => item.id === form.studentProfileId))
const selectedCourse = computed(() => courses.value.find((item) => item.id === form.courseId))
const selectedCourseDescription = computed(() => cleanDisplayText(selectedCourse.value?.description || '请选择课程后开始答疑、测评和学习效果评估。'))
const selectedEventResource = computed(() => resources.value.find((item) => item.id === eventForm.resourceId))
const courseSwitchCards = computed(() =>
  courses.value.map((course) => ({
    ...course,
    active: course.id === form.courseId,
    descriptionText: cleanDisplayText(course.description),
  })),
)
const hasContext = computed(() => Boolean(form.studentProfileId && form.courseId))
const contextHint = computed(() => {
  if (!profiles.value.length || !courses.value.length) return '请先创建学生画像和课程，学习记录需要完整上下文。'
  if (!form.studentProfileId) return '请选择学生画像。'
  if (!form.courseId) return '请选择课程。'
  return ''
})
const canRunTutoring = computed(() => !actionLoading.value && hasContext.value && Boolean(form.question.trim()))
const canGenerateAssessment = computed(
  () => !actionLoading.value && hasContext.value && Boolean(form.topic.trim()) && form.count > 0 && form.questionTypes.length > 0,
)
const canGrade = computed(
  () => !actionLoading.value && hasContext.value && questions.value.length > 0 && questions.value.every((item) => answers.value[item.id]?.trim()),
)
const canRecordEvent = computed(() => !actionLoading.value && hasContext.value && Boolean(eventForm.eventType.trim()))
const canRecordQuiz = computed(() => !actionLoading.value && hasContext.value && quizForm.maxScore > 0 && quizForm.totalCount > 0)
const hasLearningData = computed(
  () =>
    Boolean(tutoringResult.value || assessmentResult.value || gradeResult.value) ||
    events.value.length > 0 ||
    tutoringHistory.value.length > 0 ||
    attempts.value.length > 0 ||
    mastery.value.length > 0 ||
    reports.value.length > 0,
)
const courseEvents = computed(() =>
  events.value.filter((item) => !form.courseId || !item.courseId || item.courseId === form.courseId),
)
const courseTutoringHistory = computed(() =>
  tutoringHistory.value.filter((item) => {
    const courseId = String(item.courseId || '')
    return !form.courseId || !courseId || courseId === form.courseId
  }),
)
const courseAttempts = computed(() =>
  attempts.value.filter((item) => !form.courseId || !item.courseId || item.courseId === form.courseId),
)
const historyTotal = computed(() => courseEvents.value.length + courseTutoringHistory.value.length + courseAttempts.value.length + mastery.value.length + reports.value.length)
const assistantTabs = computed(() => [
  { key: 'chat' as const, label: '对话', count: tutoringHistory.value.length + (tutoringResult.value ? 1 : 0) },
  { key: 'generate' as const, label: '生成资源', count: resourceTypes.value.length || fallbackResourceTypes.length },
  { key: 'progress' as const, label: '任务进度', count: visibleGenerationTasks.value.length },
  { key: 'history' as const, label: '历史记录', count: historyTotal.value },
])
const activeConversation = computed(() => conversations.value.find((item) => item.id === activeConversationId.value))
const activeConversationMessages = computed(() => conversationMessages.value.filter((item) => item.conversationId === activeConversationId.value))
const latestAssistantMessage = computed(() => [...activeConversationMessages.value].reverse().find((item) => item.role === 'assistant'))
const latestUserMessage = computed(() => [...activeConversationMessages.value].reverse().find((item) => item.role === 'user'))
const hasConversationMessages = computed(() => activeConversationMessages.value.length > 0)
const hasPendingAssistantMessage = computed(() => activeConversationMessages.value.some((message) => message.id.startsWith('pending-assistant-')))
const recentConversationList = computed(() => conversations.value.slice(0, 4))
const visibleGenerationTasks = computed(() =>
  generationTasks.value
    .filter((task) => !form.courseId || task.courseId === form.courseId)
    .filter((task) => !form.studentProfileId || !task.studentProfileId || task.studentProfileId === form.studentProfileId)
    .sort((a, b) => {
      const rankDiff = taskDisplayRank(a) - taskDisplayRank(b)
      if (rankDiff) return rankDiff
      return new Date(b.updatedAt || b.createdAt).getTime() - new Date(a.updatedAt || a.createdAt).getTime()
    })
    .slice(0, 8),
)
const hasActiveGenerationTasks = computed(() => visibleGenerationTasks.value.some((task) => isTaskInFlight(task.status)))
const selectedGenerationType = computed(() =>
  (resourceTypes.value.length ? resourceTypes.value : fallbackResourceTypes).find((item) => item.code === generationForm.resourceType),
)
const resourceTypeOptions = computed(() => (resourceTypes.value.length ? resourceTypes.value : fallbackResourceTypes))
const canSubmitGeneration = computed(
  () =>
    !actionLoading.value &&
    Boolean(form.studentProfileId && form.courseId && generationForm.resourceType && generationForm.topic.trim() && generationForm.prompt.trim()),
)
const recentResources = computed(() => resources.value.slice(0, 6))
const selectedReferenceResources = computed(() =>
  resources.value.filter((resource) => selectedReferenceResourceIds.value.includes(resource.id)),
)
const contextDocumentTexts = computed(() => {
  const texts = [
    form.documentText,
    ...uploadedAttachments.value.map(attachmentContextText),
    ...selectedReferenceResources.value.map((resource) => `${resource.title}\n${resource.content || ''}`),
  ]
  return texts.map((item) => item.trim()).filter(Boolean)
})
const contextMasteryRows = computed(() => [
  { label: '基础概念', value: mastery.value[0] ? `${Math.round(percent(mastery.value[0].masteryScore))}%` : '中等' },
  { label: '实践应用', value: mastery.value[1] ? `${Math.round(percent(mastery.value[1].masteryScore))}%` : '中等' },
  { label: '问题解决', value: courseAttempts.value.length ? '待提升' : '待评估' },
  { label: '表达复盘', value: reports.value.length ? '中等' : '需加强' },
  { label: '学习策略', value: hasLearningData.value ? '需加强' : '待生成' },
])
const activeCoursePosition = computed(() => Math.max(0, courses.value.findIndex((course) => course.id === form.courseId)) + 1)
const activeCourseProgress = computed(() => Math.min(95, Math.max(24, 45 + courseEvents.value.length * 4 + courseAttempts.value.length * 8 + visibleGenerationTasks.value.length * 3)))
const chatHistoryPreview = computed(() => courseTutoringHistory.value.slice(0, 2))
const fallbackChatHistoryPreview = computed(() => (hasConversationMessages.value ? [] : chatHistoryPreview.value))
const recentGeneratedResources = computed(() =>
  [
    ...resources.value.map((resource) => ({
      id: resource.id,
      title: resource.title,
      meta: resource.publishedAt ? `${formatDate(resource.publishedAt)} 发布` : resource.resourceTypeName || resource.resourceType || '学习资源',
      status: resource.modality || 'PDF',
    })),
    ...visibleGenerationTasks.value.map((task) => ({
      id: task.id,
      title: task.topic,
      meta: `${formatDate(task.createdAt)} 生成`,
      status: generationStatusLabel(task.status),
    })),
  ].slice(0, 5),
)
const conversationDoubtSummary = computed(() => {
  const question = latestUserMessage.value?.content || currentLearningMission.value.question || ''
  const answer = latestAssistantMessage.value?.content || answerMarkdown.value || ''
  const actions = learningActions.value.slice(0, 3)
  const signals = profileSignals.value.slice(0, 3)
  const references = citations.value.slice(0, 2)
  const summary = answer
    ? compact(answer.replace(/^#+\s*/gm, '').replace(/\*\*/g, ''), 130)
    : ''
  return {
    question: compact(question || '等待提问', 72),
    summary,
    actions,
    signals,
    references,
  }
})
const hasConversationSummary = computed(() => Boolean(latestAssistantMessage.value || tutoringResult.value))

function taskProgressPercent(task: GenerationTask) {
  return Math.min(100, Math.max(0, Number(task.progressPercent || 0)))
}

async function loadGenerationTasks(silent = false) {
  if (!silent) {
    actionLoading.value = 'task-refresh'
    error.value = ''
  }
  try {
    generationTasks.value = await tasksApi.list()
  } catch (err) {
    if (!silent) error.value = err instanceof Error ? err.message : '任务进度同步失败'
  } finally {
    if (!silent) actionLoading.value = ''
  }
}

async function refreshGenerationTasks() {
  await loadGenerationTasks(false)
}

function isTaskInFlight(status?: string) {
  return ['CREATED', 'PENDING', 'QUEUED', 'RUNNING', 'PROCESSING'].includes(String(status || '').toUpperCase())
}

function isTaskFailed(status?: string) {
  return String(status || '').toUpperCase() === 'FAILED'
}

function isTaskRecoverableFailure(task: GenerationTask) {
  if (!isTaskFailed(task.status)) return false
  const message = `${task.errorMessage || ''} ${task.currentStep || ''} ${task.resultSummary || ''}`
  return message.includes('非标准格式') || message.includes('ResourceAgentResponse') || message.includes('application/octet-stream')
}

function isTaskHardFailed(task: GenerationTask) {
  return isTaskFailed(task.status) && !isTaskRecoverableFailure(task)
}

function taskDisplayRank(task: GenerationTask) {
  if (isTaskInFlight(task.status)) return 0
  if (String(task.status || '').toUpperCase() === 'SUCCEEDED' || task.createdResourceId) return 1
  if (isTaskRecoverableFailure(task)) return 2
  if (isTaskFailed(task.status)) return 3
  return 1
}

function taskFailureMessage(task: GenerationTask) {
  const message = String(task.errorMessage || '').trim()
  if (!message) return '任务执行失败，请查看任务详情。'
  if (message.includes('application/octet-stream') || message.includes('ResourceAgentResponse')) {
    return '这是修复前的旧任务，资源服务当时返回了非标准格式。现在已启用兜底解析，点击“用此主题重试”即可继续生成，不需要停在异常页。'
  }
  if (message.toLowerCase().includes('timed out') || message.includes('timeout') || message.includes('超时')) {
    return '模型服务响应超时，请稍后重新生成，或检查资源智能体服务状态。'
  }
  return message
}

function taskDisplayMessage(task: GenerationTask) {
  if (isTaskFailed(task.status)) return taskFailureMessage(task)
  return task.currentStep || task.resultSummary || task.prompt || '正在根据课程资料、学习画像和资源类型生成内容。'
}

function generationTaskStatusLabel(task: GenerationTask) {
  return isTaskRecoverableFailure(task) ? '可重试' : generationStatusLabel(task.status)
}

function generationTaskTone(task: GenerationTask): 'ok' | 'warn' | 'danger' | 'info' | 'muted' {
  return isTaskRecoverableFailure(task) ? 'warn' : generationTone(task.status)
}

function prefillGenerationFromTask(task: GenerationTask) {
  generationForm.resourceType = task.taskType || generationForm.resourceType
  generationForm.topic = task.topic || generationForm.topic
  generationForm.prompt = task.prompt || taskFailureMessage(task)
  setAssistantTab('generate')
}

function startTaskPolling() {
  if (taskPollTimer) return
  taskPollTimer = window.setInterval(() => {
    if (assistantTab.value === 'progress' || hasActiveGenerationTasks.value) {
      void loadGenerationTasks(true)
    }
  }, 3000)
}

function stopTaskPolling() {
  if (!taskPollTimer) return
  window.clearInterval(taskPollTimer)
  taskPollTimer = null
}

async function loadConversations(preferredConversationId = '') {
  if (!hasContext.value) {
    conversations.value = []
    conversationMessages.value = []
    activeConversationId.value = ''
    return
  }
  conversationLoading.value = true
  try {
    const rows = await learningApi.conversations({
      studentProfileId: form.studentProfileId,
      courseId: form.courseId,
      archived: archivedConversationsVisible.value,
    })
    conversationApiAvailable.value = true
    conversations.value = rows
    const hasDraftQuestion = Boolean(String(route.query.question || route.query.task || '').trim()) && !preferredConversationId
    const nextId = hasDraftQuestion
      ? ''
      : preferredConversationId ||
        (activeConversationId.value && rows.some((item) => item.id === activeConversationId.value) ? activeConversationId.value : '') ||
        rows[0]?.id ||
        ''
    if (nextId) {
      await selectConversation(nextId, false)
    } else {
      activeConversationId.value = ''
      conversationMessages.value = []
    }
  } catch {
    conversationApiAvailable.value = false
    conversations.value = []
    conversationMessages.value = []
    activeConversationId.value = ''
  } finally {
    conversationLoading.value = false
  }
}

async function toggleArchivedConversations() {
  archivedConversationsVisible.value = !archivedConversationsVisible.value
  activeConversationId.value = ''
  conversationMessages.value = []
  await loadConversations('')
}

async function updateConversationArchived(conversationId: string, archived: boolean) {
  if (!conversationId) return
  conversationLoading.value = true
  try {
    await learningApi.updateConversation(conversationId, { archived })
    conversationApiAvailable.value = true
    if (activeConversationId.value === conversationId) {
      activeConversationId.value = ''
      conversationMessages.value = []
    }
    await loadConversations('')
  } catch (err) {
    conversationApiAvailable.value = false
    error.value = err instanceof Error ? err.message : '会话状态更新失败，请稍后重试。'
  } finally {
    conversationLoading.value = false
  }
}

// 会话项操作菜单 / 内联重命名状态
const conversationMenuId = ref('')
const renamingConversationId = ref('')
const renameDraft = ref('')

function toggleConversationMenu(conversationId: string) {
  conversationMenuId.value = conversationMenuId.value === conversationId ? '' : conversationId
}

function closeConversationMenu() {
  conversationMenuId.value = ''
}

function beginRenameConversation(conversation: LearningConversation) {
  renamingConversationId.value = conversation.id
  renameDraft.value = conversation.title || ''
  conversationMenuId.value = ''
}

function cancelRenameConversation() {
  renamingConversationId.value = ''
  renameDraft.value = ''
}

async function commitRenameConversation(conversationId: string) {
  const title = renameDraft.value.trim()
  if (!conversationId || !title) {
    cancelRenameConversation()
    return
  }
  conversationLoading.value = true
  try {
    await learningApi.updateConversation(conversationId, { title })
    conversationApiAvailable.value = true
    await loadConversations('')
  } catch (err) {
    conversationApiAvailable.value = false
    error.value = err instanceof Error ? err.message : '会话重命名失败，请稍后重试。'
  } finally {
    conversationLoading.value = false
    cancelRenameConversation()
  }
}

async function deleteConversation(conversationId: string) {
  if (!conversationId) return
  if (typeof window !== 'undefined' && !window.confirm('确定删除这个会话吗？删除后聊天记录无法恢复。')) return
  conversationMenuId.value = ''
  conversationLoading.value = true
  try {
    await learningApi.deleteConversation(conversationId)
    conversationApiAvailable.value = true
    if (activeConversationId.value === conversationId) {
      activeConversationId.value = ''
      conversationMessages.value = []
    }
    await loadConversations('')
  } catch (err) {
    conversationApiAvailable.value = false
    error.value = err instanceof Error ? err.message : '会话删除失败，请稍后重试。'
  } finally {
    conversationLoading.value = false
  }
}

async function selectConversation(conversationId: string, updateRoute = true) {
  if (!conversationId) return
  activeConversationId.value = conversationId
  conversationLoading.value = true
  try {
    conversationMessages.value = await learningApi.conversationMessages(conversationId)
    conversationApiAvailable.value = true
    if (updateRoute) {
      void router.replace({
        path: '/learning',
        query: {
          ...route.query,
          tab: 'chat',
          courseId: form.courseId || undefined,
          conversationId,
        },
      })
    }
  } catch (err) {
    conversationApiAvailable.value = false
    error.value = err instanceof Error ? err.message : '会话消息暂未同步，已保留旧答疑兼容模式。'
  } finally {
    conversationLoading.value = false
  }
}

async function ensureActiveConversation() {
  if (activeConversationId.value) return activeConversationId.value
  const title = (form.question.trim() || form.topic || selectedCourse.value?.title || 'AI 助手会话').slice(0, 80)
  const conversation = await learningApi.createConversation({
    studentProfileId: form.studentProfileId,
    courseId: form.courseId,
    title,
  })
  conversations.value = [conversation, ...conversations.value.filter((item) => item.id !== conversation.id)]
  activeConversationId.value = conversation.id
  conversationMessages.value = []
  return conversation.id
}

function makeLocalConversationMessage(
  conversationId: string,
  role: 'user' | 'assistant',
  content: string,
  idPrefix = 'pending',
): LearningConversationMessage {
  return {
    id: `${idPrefix}-${role}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    conversationId,
    role,
    content,
    createdAt: new Date().toISOString(),
    fallbackUsed: idPrefix === 'fallback',
  }
}

function setConversationMessagesForConversation(conversationId: string, messages: LearningConversationMessage[]) {
  conversationMessages.value = [
    ...conversationMessages.value.filter((message) => message.conversationId !== conversationId),
    ...messages,
  ]
}

function newConversationRouteQuery() {
  const query = { ...route.query }
  delete query.conversationId
  delete query.question
  delete query.task
  return {
    ...query,
    tab: 'chat',
    courseId: form.courseId || undefined,
  }
}

function normalizeAssistantTab(value: unknown): AssistantTab {
  const tab = String(value || '')
  return tab === 'generate' || tab === 'progress' || tab === 'history' ? tab : 'chat'
}

function syncAssistantContextFromRoute() {
  assistantTab.value = normalizeAssistantTab(route.query.tab)
  const queryCourseId = String(route.query.courseId || '')
  if (queryCourseId && courses.value.some((course) => course.id === queryCourseId)) {
    form.courseId = queryCourseId
    app.setActiveCourse(queryCourseId)
  }
  const queryQuestion = String(route.query.question || route.query.task || '')
  if (queryQuestion.trim()) form.question = queryQuestion.trim()
  const queryGenerateTopic = String(route.query.generateTopic || '')
  if (queryGenerateTopic.trim()) {
    assistantTab.value = 'generate'
    generationForm.topic = queryGenerateTopic.trim()
  }
  const queryGeneratePrompt = String(route.query.generatePrompt || '')
  if (queryGeneratePrompt.trim()) generationForm.prompt = queryGeneratePrompt.trim()
  const queryResourceId = String(route.query.resourceId || '')
  if (queryResourceId) {
    eventForm.resourceId = queryResourceId
    if (!selectedReferenceResourceIds.value.includes(queryResourceId)) {
      selectedReferenceResourceIds.value = [queryResourceId, ...selectedReferenceResourceIds.value]
    }
  }
  const queryConversationId = String(route.query.conversationId || '')
  if (queryConversationId) activeConversationId.value = queryConversationId
}

function setAssistantTab(tab: AssistantTab) {
  assistantTab.value = tab
  void router.replace({
    path: '/learning',
    query: {
      ...route.query,
      tab,
      courseId: form.courseId || undefined,
    },
  })
}

async function startNewChat() {
  tutoringResult.value = null
  assessmentResult.value = null
  gradeResult.value = null
  answers.value = {}
  form.question = ''
  uploadedAttachments.value = []
  selectedReferenceResourceIds.value = []
  referencePanelOpen.value = false
  archivedConversationsVisible.value = false
  setAssistantTab('chat')
  activeConversationId.value = ''
  conversationMessages.value = []
  error.value = ''
  void router.replace({ path: '/learning', query: newConversationRouteQuery() })
}

function toggleReferenceResource(resourceId: string) {
  selectedReferenceResourceIds.value = selectedReferenceResourceIds.value.includes(resourceId)
    ? selectedReferenceResourceIds.value.filter((id) => id !== resourceId)
    : [...selectedReferenceResourceIds.value, resourceId]
}

function formatAttachmentSize(sizeBytes: number) {
  if (!Number.isFinite(sizeBytes) || sizeBytes <= 0) return '0 KB'
  if (sizeBytes < 1024 * 1024) return `${Math.max(1, Math.round(sizeBytes / 1024))} KB`
  return `${(sizeBytes / 1024 / 1024).toFixed(1)} MB`
}

function conversationPreviewText(value?: unknown) {
  return cleanDisplayText(value)
    .replace(/```[\s\S]*?```/g, '代码片段')
    .replace(/`([^`]+)`/g, '$1')
    .replace(/!\[[^\]]*]\([^)]*\)/g, '')
    .replace(/\[([^\]]+)]\([^)]*\)/g, '$1')
    .replace(/^#{1,6}\s*/gm, '')
    .replace(/[*_>~|-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

function attachmentStatusLabel(status: string) {
  const labels: Record<string, string> = {
    ANALYZED: '已解析',
    METADATA_ONLY: '已保存',
    STORED: '已上传',
    FAILED: '解析失败',
  }
  return labels[status] || status || '已上传'
}

function attachmentContextText(asset: UploadAsset) {
  const preview = asset.extractedTextPreview?.trim()
  const meta = [
    `附件：${asset.originalFilename}`,
    `类型：${asset.contentType || asset.materialType || 'FILE'}`,
    `大小：${formatAttachmentSize(asset.sizeBytes)}`,
    `状态：${attachmentStatusLabel(asset.parseStatus)}`,
    asset.parseMessage ? `解析说明：${asset.parseMessage}` : '',
    preview ? `解析预览：${preview}` : '',
  ]
  return meta.filter(Boolean).join('\n')
}

function openAttachmentPicker() {
  referencePanelOpen.value = false
  attachmentInput.value?.click()
}

function toggleReferencePanel() {
  referencePanelOpen.value = !referencePanelOpen.value
}

function closeComposerPanels() {
  referencePanelOpen.value = false
}

function clearComposerContext() {
  uploadedAttachments.value = []
  selectedReferenceResourceIds.value = []
  closeComposerPanels()
}

async function uploadAttachmentFiles(files: File[]) {
  if (!files.length) return
  uploadingAttachment.value = true
  error.value = ''
  try {
    const results = await Promise.allSettled(
      files.map((file) =>
        uploadsApi.uploadCourseMaterial(file, {
          courseId: form.courseId || selectedCourse.value?.id,
          role: app.role,
        }),
      ),
    )
    const uploaded = results
      .filter((result): result is PromiseFulfilledResult<UploadAsset> => result.status === 'fulfilled')
      .map((result) => result.value)
    const failed = results.filter((result) => result.status === 'rejected')
    const existingIds = new Set(uploadedAttachments.value.map((item) => item.id))
    uploadedAttachments.value = [
      ...uploadedAttachments.value,
      ...uploaded.filter((item) => !existingIds.has(item.id)),
    ]
    if (failed.length) {
      error.value = `${failed.length} 个附件上传失败，已保留成功上传的附件。`
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '附件上传失败'
  } finally {
    uploadingAttachment.value = false
  }
}

async function handleAttachmentFiles(event: Event) {
  const input = event.target as HTMLInputElement
  const files = Array.from(input.files || [])
  await uploadAttachmentFiles(files)
  input.value = ''
}

async function handleComposerPaste(event: ClipboardEvent) {
  const clipboard = event.clipboardData
  if (!clipboard) return
  const files = Array.from(clipboard.files || []).filter((file) => file.type.startsWith('image/'))
  if (!files.length) return
  if (!clipboard.getData('text/plain')) event.preventDefault()
  await uploadAttachmentFiles(files)
}

function removeUploadedAttachment(assetId: string) {
  uploadedAttachments.value = uploadedAttachments.value.filter((item) => item.id !== assetId)
}

function applyReferenceResources() {
  referencePanelOpen.value = false
}

function asStringArray(value: unknown): string[] {
  const parsed = typeof value === 'string' ? parseMaybeJson<unknown>(value, value) : value
  if (Array.isArray(parsed)) {
    return parsed
      .map((item) => {
        if (typeof item === 'string') return item
        if (isRecord(item)) return String(item.title || item.text || item.url || item.label || JSON.stringify(item))
        return String(item)
      })
      .filter(Boolean)
  }
  if (typeof parsed === 'string' && parsed.trim()) return parsed.split(/\n|；|;/).map((item) => item.trim()).filter(Boolean)
  return []
}

function asRecordArray(value: unknown): Record<string, unknown>[] {
  const parsed = typeof value === 'string' ? parseMaybeJson<unknown>(value, []) : value
  return Array.isArray(parsed) ? parsed.filter(isRecord) : []
}

function normalizeQuestion(value: unknown, index: number): AssessmentQuestion {
  const record = isRecord(value) ? value : {}
  return {
    id: String(record.id || record.questionId || `q-${index + 1}`),
    type: String(record.type || record.questionType || '题目'),
    stem: String(record.stem || record.question || record.title || `题目 ${index + 1}`),
    options: asStringArray(record.options),
    answer: String(record.answer || record.referenceAnswer || ''),
    rubric: String(record.rubric || record.scoringRubric || ''),
    explanation: String(record.explanation || record.analysis || ''),
    difficulty: String(record.difficulty || form.difficulty),
    knowledgePoints: asStringArray(record.knowledgePoints || record.knowledgePoint),
    score: Number(record.score || record.maxScore || 10),
  }
}

const questions = computed<AssessmentQuestion[]>(() => {
  const raw =
    assessmentResult.value?.questions ||
    assessmentResult.value?.items ||
    assessmentResult.value?.assessmentQuestions ||
    assessmentResult.value?.questionList
  return Array.isArray(raw) ? raw.map(normalizeQuestion) : []
})

const answerMarkdown = computed(() =>
  String(
    latestAssistantMessage.value?.content ||
      tutoringResult.value?.answer ||
      tutoringResult.value?.content ||
      tutoringResult.value?.summary ||
      tutoringResult.value?.message ||
      '',
  ),
)
const answerMermaid = computed(() =>
  String(latestAssistantMessage.value?.mermaidDiagram || tutoringResult.value?.mermaidDiagram || ''),
)
const citations = computed(() => asStringArray(latestAssistantMessage.value?.citations || tutoringResult.value?.citations || tutoringResult.value?.references))
const followUpQuestions = computed(() => asStringArray(latestAssistantMessage.value?.followUpQuestions || tutoringResult.value?.followUpQuestions || tutoringResult.value?.followUps))
const learningActions = computed(() => asStringArray(latestAssistantMessage.value?.learningActions || tutoringResult.value?.learningActions || tutoringResult.value?.actions))
const profileSignals = computed(() => asStringArray(latestAssistantMessage.value?.profileSignals || tutoringResult.value?.profileSignals || tutoringResult.value?.signals))

const quickTutoringPrompts = [
  {
    title: '概念关系',
    question: '这个知识点和前置内容之间是什么关系？',
    topic: '当前章节核心知识点',
    modality: '文本+结构图',
  },
  {
    title: '错题讲解',
    question: '这类题我总是步骤选错，应该怎么拆解？',
    topic: '步骤迁移与错因复盘',
    modality: '文字讲解+例题拆解',
  },
  {
    title: '考前复盘',
    question: '请根据我的薄弱点给我一份 30 分钟复盘计划。',
    topic: '阶段复盘与补弱计划',
    modality: '行动清单+练习建议',
  },
]

const learningStats = computed(() => [
  { label: '学习事件', value: courseEvents.value.length, detail: '资源浏览、答疑、测评记录' },
  { label: '答疑记录', value: courseTutoringHistory.value.length + (tutoringResult.value ? 1 : 0), detail: '可回溯的辅导证据' },
  { label: '测评次数', value: courseAttempts.value.length + (gradeResult.value ? 1 : 0), detail: '用于学习效果评估' },
  { label: '掌握点', value: mastery.value.length, detail: '随测评动态更新' },
])

const activeResource = computed(() => resources.value.find((item) => item.id === eventForm.resourceId) || resources.value[0])
const currentLearningMission = computed(() => ({
  title: form.topic || selectedCourse.value?.title || '今日学习任务',
  course: selectedCourse.value?.title || '请选择课程',
  profile: selectedProfile.value?.studentName || '请选择学习画像',
  resource: activeResource.value?.title || '等待课程资源',
  question: form.question,
}))
const learningPathStages = computed(() => [
  {
    label: '先学',
    title: activeResource.value?.title || selectedCourse.value?.title || '课程资源',
    detail: activeResource.value
      ? `${activeResource.value.resourceTypeName || activeResource.value.resourceType || '学习资源'} · ${compact(activeResource.value.content || '', 34)}`
      : '选择课程后加载可学习资源',
  },
  {
    label: '再问',
    title: '智能答疑',
    detail: compact(form.question || '围绕当前卡点发起追问', 46),
  },
  {
    label: '再测',
    title: `${form.count} 题自适应测评`,
    detail: `${form.difficulty} · ${form.questionTypes.slice(0, 3).join('、')}`,
  },
  {
    label: '沉淀',
    title: attempts.value.length || gradeResult.value ? '更新掌握度' : '等待测评证据',
    detail: attempts.value.length
      ? `${attempts.value.length} 次测评记录会影响资源推荐`
      : '完成测评后调整学习路径和画像信号',
  },
])
const learningCycleStats = computed(() => [
  { label: '今日上下文', value: hasContext.value ? '已就绪' : '待选择', detail: currentLearningMission.value.course },
  { label: '资源池', value: resources.value.length, detail: activeResource.value?.title || '课程资源待同步' },
  { label: '学习证据', value: events.value.length + attempts.value.length, detail: '行为、测评和反馈记录' },
  { label: '路径调整', value: mastery.value.length, detail: '掌握度驱动下一步推荐' },
])
const learningAgentSteps = computed(() => [
  {
    label: '证据检索',
    title: activeResource.value?.title || '课程资源待同步',
    detail: activeResource.value ? '已绑定当前课程资源，可作为答疑引用来源。' : '选择课程后自动加载已发布资源。',
    status: activeResource.value ? '已就绪' : '待资源',
    tone: activeResource.value ? 'ok' : 'warn',
  },
  {
    label: '辅导生成',
    title: form.question || '等待学生问题',
    detail: tutoringResult.value ? '已形成回答、引用、追问和画像信号。' : '提交问题后生成可追溯辅导回答。',
    status: actionLoading.value === 'tutoring' ? '生成中' : tutoringResult.value ? '已回答' : '待提问',
    tone: tutoringResult.value ? 'ok' : actionLoading.value === 'tutoring' ? 'info' : 'muted',
  },
  {
    label: '随堂测评',
    title: `${form.count} 题 · ${form.difficulty}`,
    detail: questions.value.length ? '题单已生成，可提交答案进入自动批改。' : '按当前主题生成自适应题单。',
    status: questions.value.length ? '题单就绪' : '待生成',
    tone: questions.value.length ? 'ok' : 'muted',
  },
  {
    label: '画像更新',
    title: mastery.value.length ? `${mastery.value.length} 个掌握点` : '等待学习证据',
    detail: gradeResult.value ? '批改结果已可用于更新薄弱点和资源推荐。' : '学习事件和测评记录会沉淀为画像信号。',
    status: gradeResult.value ? '可更新' : mastery.value.length ? '有证据' : '待沉淀',
    tone: gradeResult.value || mastery.value.length ? 'ok' : 'muted',
  },
] as Array<{ label: string; title: string; detail: string; status: string; tone: 'ok' | 'warn' | 'danger' | 'info' | 'muted' }>)

const gradeScore = computed(() => Number(gradeResult.value?.score || gradeResult.value?.totalScore || 0))
const gradeMaxScore = computed(() => Number(gradeResult.value?.maxScore || gradeResult.value?.totalMaxScore || 100))
const gradePercent = computed(() => Math.round((gradeScore.value / Math.max(1, gradeMaxScore.value)) * 100))
const gradeFeedback = computed(() => String(gradeResult.value?.feedback || gradeResult.value?.summary || '暂无总评'))
const weaknessSignals = computed(() => asStringArray(gradeResult.value?.weaknessSignals || gradeResult.value?.weaknesses))
const nextResourceTypes = computed(() => asStringArray(gradeResult.value?.nextResourceTypes || gradeResult.value?.recommendedResources))
const profileUpdateSuggestions = computed(() =>
  asStringArray(gradeResult.value?.profileUpdateSuggestions || gradeResult.value?.profileSignals || gradeResult.value?.profileUpdates),
)
const itemFeedback = computed(() =>
  asRecordArray(gradeResult.value?.itemFeedback || gradeResult.value?.questionFeedback || gradeResult.value?.questionResults),
)

function applyTutoringPrompt(prompt: (typeof quickTutoringPrompts)[number]) {
  form.question = prompt.question
  form.topic = prompt.topic
  form.modality = prompt.modality
}

function eventTypeLabel(type?: string) {
  const labels: Record<string, string> = {
    RESOURCE_OPEN: '打开资源',
    RESOURCE_VIEW: '浏览资源',
    RESOURCE_COMPLETE: '完成学习',
    RESOURCE_FEEDBACK: '提交反馈',
    PRACTICE_FINISH: '完成实操',
    TUTORING_QUESTION: '发起答疑',
    QUIZ_SUBMIT: '提交测评',
  }
  return labels[type || ''] || '学习事件'
}

function learningEventSummary(value: unknown) {
  const parsed = typeof value === 'string' ? parseMaybeJson<unknown>(value, value) : value
  if (isRecord(parsed)) {
    const readable = [
      parsed.note,
      parsed.question ? `问题：${parsed.question}` : '',
      parsed.topic ? `主题：${parsed.topic}` : '',
      parsed.score && parsed.maxScore ? `得分：${parsed.score}/${parsed.maxScore}` : '',
      parsed.feedback,
    ]
      .filter(Boolean)
      .join('；')
    return compact(readable || JSON.stringify(parsed), 120)
  }
  return compact(String(parsed || '-'), 120)
}

const scoreOption = computed<EChartsOption>(() => ({
  tooltip: {},
  graphic: attempts.value.length
    ? undefined
    : { type: 'text', left: 'center', top: 'middle', style: { text: '暂无测评趋势', fill: '#61708a' } },
  grid: { left: 38, right: 18, top: 24, bottom: 34 },
  xAxis: { type: 'category', data: attempts.value.map((item, index) => item.topic || `第${index + 1}次`) },
  yAxis: { type: 'value', max: 100 },
  series: [
    {
      type: 'line',
      smooth: true,
      data: attempts.value.map((item) => Math.round((Number(item.score || 0) / Math.max(1, Number(item.maxScore || 1))) * 100)),
      itemStyle: { color: '#2f6fef' },
      areaStyle: { opacity: 0.14 },
    },
  ],
}))

const masteryOption = computed<EChartsOption>(() => ({
  tooltip: {},
  graphic: mastery.value.length
    ? undefined
    : { type: 'text', left: 'center', top: 'middle', style: { text: '暂无掌握度数据', fill: '#61708a' } },
  grid: { left: 120, right: 18, top: 20, bottom: 30 },
  xAxis: { type: 'value', max: 100 },
  yAxis: { type: 'category', data: mastery.value.map((item) => item.knowledgePoint || '-') },
  series: [
    {
      type: 'bar',
      data: mastery.value.map((item) => Math.round(percent(item.masteryScore))),
      itemStyle: { color: '#0f8a55', borderRadius: [0, 4, 4, 0] },
    },
  ],
}))

async function loadOptions() {
  loading.value = true
  error.value = ''
  try {
    const [profileResult, courseResult, resourceTypeResult, taskResult] = await Promise.allSettled([
      profilesApi.list(),
      coursesApi.list(),
      coursesApi.resourceTypes(),
      tasksApi.list(),
    ])
    profiles.value = profileResult.status === 'fulfilled' ? profileResult.value : []
    courses.value = courseResult.status === 'fulfilled' ? courseResult.value : []
    resourceTypes.value = resourceTypeResult.status === 'fulfilled' && resourceTypeResult.value.length ? resourceTypeResult.value : fallbackResourceTypes
    generationTasks.value = taskResult.status === 'fulfilled' ? taskResult.value : []
    syncAssistantContextFromRoute()
    form.studentProfileId ||= profiles.value[0]?.id || ''
    const queryCourseId = String(route.query.courseId || '')
    const preferredCourse = courses.value.find((course) => course.id === queryCourseId) || courses.value.find((course) => course.id === app.activeCourseId) || courses.value[0]
    form.courseId ||= preferredCourse?.id || ''
    if (form.courseId) app.setActiveCourse(form.courseId)
    if (profileResult.status === 'rejected' || courseResult.status === 'rejected' || resourceTypeResult.status === 'rejected' || taskResult.status === 'rejected') {
      error.value = '学生画像或课程列表暂未同步，请稍后刷新。'
    }
    await loadHistory()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '学习闭环选项加载失败'
  } finally {
    loading.value = false
  }
}

async function loadHistory() {
  if (!hasContext.value) {
    resources.value = []
    events.value = []
    tutoringHistory.value = []
    attempts.value = []
    mastery.value = []
    reports.value = []
    conversations.value = []
    conversationMessages.value = []
    activeConversationId.value = ''
    return
  }
  historyLoading.value = true
  error.value = ''
  const [resourceResult, eventResult, tutoringResultList, attemptResult, masteryResult, reportResult] = await Promise.allSettled([
    coursesApi.resources(form.courseId, { publishedOnly: app.role !== 'teacher' }),
    learningApi.events(form.studentProfileId),
    learningApi.tutoringHistory(form.studentProfileId),
    learningApi.attempts(form.studentProfileId),
    learningApi.mastery(form.studentProfileId, form.courseId),
    learningApi.evaluationReports(form.studentProfileId, form.courseId),
  ])
  resources.value = resourceResult.status === 'fulfilled' ? resourceResult.value : []
  if (resources.value.length && !resources.value.some((item) => item.id === eventForm.resourceId)) {
    eventForm.resourceId = resources.value[0].id
  }
  if (resources.value.length && !resources.value.some((item) => item.id === quizForm.resourceId)) {
    quizForm.resourceId = resources.value[0].id
  }
  events.value = eventResult.status === 'fulfilled' ? eventResult.value : []
  tutoringHistory.value = tutoringResultList.status === 'fulfilled' ? tutoringResultList.value : []
  attempts.value = attemptResult.status === 'fulfilled' ? attemptResult.value : []
  mastery.value = masteryResult.status === 'fulfilled' ? masteryResult.value : []
  reports.value = reportResult.status === 'fulfilled' ? reportResult.value : []
  await loadConversations(String(route.query.conversationId || activeConversationId.value || ''))
  const failures = [resourceResult, eventResult, tutoringResultList, attemptResult, masteryResult, reportResult].filter((item) => item.status === 'rejected').length
  if (failures === 6) error.value = '学习记录暂未同步，请稍后刷新。'
  historyLoading.value = false
}

async function runTutoring() {
  if (!canRunTutoring.value) {
    error.value = contextHint.value || '请输入答疑问题。'
    return
  }
  actionLoading.value = 'tutoring'
  error.value = ''
  const question = form.question.trim()
  const documentTexts = contextDocumentTexts.value
  lastSubmittedQuestion.value = question
  try {
    let pendingConversationId = ''
    let confirmedMessagesBeforeSend: LearningConversationMessage[] = []
    let pendingUserMessage: LearningConversationMessage | null = null
    let pendingAssistantMessage: LearningConversationMessage | null = null
    try {
      const conversationId = await ensureActiveConversation()
      pendingConversationId = conversationId
      confirmedMessagesBeforeSend = conversationMessages.value.filter(
        (message) => message.conversationId === conversationId && !message.id.startsWith('pending-'),
      )
      pendingUserMessage = makeLocalConversationMessage(conversationId, 'user', question, 'pending')
      pendingAssistantMessage = makeLocalConversationMessage(
        conversationId,
        'assistant',
        '正在结合本课资料、学习画像和本轮上下文组织回答...',
        'pending',
      )
      setConversationMessagesForConversation(conversationId, [
        ...confirmedMessagesBeforeSend,
        pendingUserMessage,
        pendingAssistantMessage,
      ])
      form.question = ''
      closeComposerPanels()
      const response = await learningApi.sendConversationMessage(conversationId, {
        content: question,
        message: question,
        modality: form.modality.trim(),
        documentTexts,
      })
      conversationApiAvailable.value = true
      conversations.value = [response.conversation, ...conversations.value.filter((item) => item.id !== response.conversation.id)]
      activeConversationId.value = response.conversation.id
      setConversationMessagesForConversation(response.conversation.id, [
        ...confirmedMessagesBeforeSend,
        response.userMessage,
        response.assistantMessage,
      ])
      tutoringResult.value = {
        answer: response.assistantMessage.content,
        citations: response.assistantMessage.citations || [],
        followUpQuestions: response.assistantMessage.followUpQuestions || [],
        learningActions: response.assistantMessage.learningActions || [],
        profileSignals: response.assistantMessage.profileSignals || [],
      }
    } catch (conversationErr) {
      conversationApiAvailable.value = false
      tutoringResult.value = await learningApi.tutoring({
        studentProfileId: form.studentProfileId,
        courseId: form.courseId,
        question,
        modality: form.modality.trim(),
        documentTexts,
      })
      error.value =
        conversationErr instanceof Error
          ? `会话接口暂不可用，已使用旧答疑接口完成本次回答：${conversationErr.message}`
          : '会话接口暂不可用，已使用旧答疑接口完成本次回答。'
      if (pendingConversationId && pendingUserMessage) {
        setConversationMessagesForConversation(pendingConversationId, [
          ...confirmedMessagesBeforeSend,
          pendingUserMessage,
          makeLocalConversationMessage(
            pendingConversationId,
            'assistant',
            answerMarkdown.value || '旧答疑接口已返回结果，可继续追问。',
            'fallback',
          ),
        ])
      }
    }
    if (form.question.trim() === question) form.question = ''
    clearComposerContext()
    actionLoading.value = ''
    await loadHistory()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '智能答疑失败'
  } finally {
    actionLoading.value = ''
  }
}

async function generateAssessment() {
  if (!canGenerateAssessment.value) {
    error.value = contextHint.value || '请补全测评主题、题量和题型。'
    return
  }
  actionLoading.value = 'assessment'
  error.value = ''
  try {
    assessmentResult.value = await learningApi.generateAssessment({
      studentProfileId: form.studentProfileId,
      courseId: form.courseId,
      topic: form.topic.trim(),
      difficulty: form.difficulty.trim(),
      count: Number(form.count),
      questionTypes: form.questionTypes,
      documentTexts: contextDocumentTexts.value,
    })
    answers.value = Object.fromEntries(questions.value.map((item) => [item.id, '']))
  } catch (err) {
    error.value = err instanceof Error ? err.message : '测评生成失败'
  } finally {
    actionLoading.value = ''
  }
}

async function gradeAssessment() {
  if (!canGrade.value) {
    error.value = contextHint.value || '请为每道题填写答案后再提交批改。'
    return
  }
  actionLoading.value = 'grade'
  error.value = ''
  try {
    gradeResult.value = await learningApi.gradeAssessment({
      studentProfileId: form.studentProfileId,
      courseId: form.courseId,
      topic: form.topic.trim(),
      questions: questions.value,
      answers: questions.value.map((item) => ({ questionId: item.id, answer: answers.value[item.id] || '' })),
    })
    await loadHistory()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '测评批改失败'
  } finally {
    actionLoading.value = ''
  }
}

async function recordLearningEvent() {
  if (!canRecordEvent.value) {
    error.value = contextHint.value || '请补全学习行为类型。'
    return
  }
  actionLoading.value = 'event'
  error.value = ''
  try {
    await learningApi.recordEvent({
      studentProfileId: form.studentProfileId,
      courseId: form.courseId,
      resourceId: eventForm.resourceId || null,
      eventType: eventForm.eventType.trim(),
      durationSeconds: Math.max(0, Number(eventForm.durationMinutes || 0)) * 60,
      feedbackScore: Number(eventForm.feedbackScore || 0),
      eventPayload: JSON.stringify({
        topic: form.topic,
        note: eventForm.eventPayload,
        resourceTitle: selectedEventResource.value?.title || '',
        source: 'learning-workbench',
      }),
    })
    await loadHistory()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '学习行为记录失败'
  } finally {
    actionLoading.value = ''
  }
}

async function recordQuizAttempt() {
  if (!canRecordQuiz.value) {
    error.value = contextHint.value || '请补全测评分数、题量和薄弱点。'
    return
  }
  actionLoading.value = 'quiz-record'
  error.value = ''
  try {
    await learningApi.recordQuizAttempt({
      studentProfileId: form.studentProfileId,
      courseId: form.courseId,
      resourceId: quizForm.resourceId || null,
      score: Number(quizForm.score || 0),
      maxScore: Number(quizForm.maxScore || 100),
      correctCount: Number(quizForm.correctCount || 0),
      totalCount: Number(quizForm.totalCount || 1),
      weakPoints: quizForm.weakPoints.trim() || form.topic,
    })
    await loadHistory()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '测评记录沉淀失败'
  } finally {
    actionLoading.value = ''
  }
}

function generationStatusLabel(status?: string) {
  const value = String(status || '').toUpperCase()
  const labels: Record<string, string> = {
    SUCCEEDED: '已完成',
    RUNNING: '生成中',
    PROCESSING: '处理中',
    PENDING: '排队中',
    QUEUED: '排队中',
    CREATED: '已创建',
    FAILED: '生成异常',
    REVIEW_REQUIRED: '待复核',
    READY_TO_PUBLISH: '可发布',
  }
  return labels[value] || value || '等待中'
}

function generationTone(status?: string): 'ok' | 'warn' | 'danger' | 'info' | 'muted' {
  const value = String(status || '').toUpperCase()
  if (value === 'SUCCEEDED' || value === 'READY_TO_PUBLISH') return 'ok'
  if (value === 'FAILED') return 'danger'
  if (value === 'PENDING' || value === 'QUEUED' || value === 'CREATED' || value === 'REVIEW_REQUIRED') return 'warn'
  if (value === 'RUNNING' || value === 'PROCESSING') return 'info'
  return 'muted'
}

async function submitResourceGeneration() {
  if (!canSubmitGeneration.value) {
    error.value = contextHint.value || '请补齐课程、资源类型、主题和生成要求。'
    return
  }
  actionLoading.value = 'generation'
  error.value = ''
  try {
    const task = await tasksApi.createResourceGeneration({
      studentProfileId: form.studentProfileId,
      courseId: form.courseId,
      topic: generationForm.topic.trim(),
      resourceType: generationForm.resourceType,
      modality: generationForm.modality.trim(),
      prompt: generationForm.prompt.trim(),
    })
    generationTasks.value = [task, ...generationTasks.value.filter((item) => item.id !== task.id)]
    assistantTab.value = 'progress'
    void router.replace({
      path: '/learning',
      query: {
        tab: 'progress',
        courseId: form.courseId,
        taskId: task.id,
      },
    })
    await loadHistory()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '资源生成任务创建失败'
  } finally {
    actionLoading.value = ''
  }
}

function downloadLearningJson() {
  downloadJson(`${safeFilePart(form.topic)}-learning-loop.json`, {
    tutoringResult: tutoringResult.value,
    assessmentResult: assessmentResult.value,
    gradeResult: gradeResult.value,
    events: events.value,
    tutoringHistory: tutoringHistory.value,
    attempts: attempts.value,
    mastery: mastery.value,
    reports: reports.value,
  })
}

function downloadTutoringMarkdown() {
  const exportedQuestion = lastSubmittedQuestion.value || latestUserMessage.value?.content || form.question || '-'
  const lines = [
    `# ${form.topic} 智能答疑记录`,
    '',
    `- 学生画像：${selectedProfile.value?.studentName || form.studentProfileId || '-'}`,
    `- 课程：${selectedCourse.value?.title || form.courseId || '-'}`,
    `- 问题：${exportedQuestion}`,
    '',
    '## 回答',
    answerMarkdown.value || '暂无回答',
    '',
    '## 引用',
    ...(citations.value.length ? citations.value.map((item) => `- ${item}`) : ['暂无引用']),
    '',
    '## 后续问题',
    ...(followUpQuestions.value.length ? followUpQuestions.value.map((item) => `- ${item}`) : ['暂无后续问题']),
    '',
    '## 学习行动',
    ...(learningActions.value.length ? learningActions.value.map((item) => `- ${item}`) : ['暂无学习行动']),
    '',
    '## 画像信号',
    ...(profileSignals.value.length ? profileSignals.value.map((item) => `- ${item}`) : ['暂无画像信号']),
  ]
  downloadText(`${safeFilePart(form.topic)}-tutoring.md`, lines.join('\n'), 'text/markdown;charset=utf-8')
}

function downloadAssessmentJson() {
  downloadJson(`${safeFilePart(form.topic)}-assessment.json`, {
    assessmentResult: assessmentResult.value,
    questions: questions.value,
    answers: answers.value,
    gradeResult: gradeResult.value,
  })
}

function switchCourse(courseId: string) {
  if (!courseId) return
  if (courseId !== form.courseId) {
    form.courseId = courseId
    void loadHistory()
  }
  showCourseList.value = false
}

function downloadLearningMarkdown() {
  const lines = [
    `# ${form.topic} 学习闭环报告`,
    '',
    `- 学生：${selectedProfile.value?.studentName || '-'}`,
    `- 课程：${selectedCourse.value?.title || '-'}`,
    `- 最近测评：${attempts.value.length} 次`,
    `- 掌握度记录：${mastery.value.length} 条`,
    `- 学习事件：${events.value.length} 条`,
    '',
    '## 智能答疑',
    answerMarkdown.value || '暂无答疑结果',
    '',
    '## 批改结果',
    gradeResult.value ? `得分：${gradeScore.value} / ${gradeMaxScore.value}\n\n${gradeFeedback.value}` : '暂无批改结果',
    '',
    '## 薄弱点',
    ...(weaknessSignals.value.length ? weaknessSignals.value.map((item) => `- ${item}`) : ['暂无薄弱点']),
    '',
    '## 下一步资源建议',
    ...(nextResourceTypes.value.length ? nextResourceTypes.value.map((item) => `- ${item}`) : ['暂无资源建议']),
  ]
  downloadText(`${safeFilePart(form.topic)}-learning-report.md`, lines.join('\n'), 'text/markdown;charset=utf-8')
}

watch(
  () => form.courseId,
  (courseId) => {
    if (courseId) app.setActiveCourse(courseId)
  },
)

watch(
  () => app.activeCourseId,
  (courseId) => {
    if (courseId && courses.value.some((course) => course.id === courseId)) {
      form.courseId = courseId
      void loadHistory()
    }
  },
)

watch(
  () =>
    `${route.query.tab || ''}:${route.query.courseId || ''}:${route.query.taskId || ''}:${route.query.conversationId || ''}:${route.query.question || ''}:${route.query.generateTopic || ''}:${route.query.generatePrompt || ''}`,
  () => {
    const previousCourseId = form.courseId
    syncAssistantContextFromRoute()
    if (form.courseId && form.courseId !== previousCourseId) void loadHistory()
  },
)

onMounted(() => {
  startTaskPolling()
  void loadOptions()
})
onUnmounted(stopTaskPolling)
</script>

<template>
  <div class="page-grid" :class="{ 'is-learning-chat-page': assistantTab === 'chat' }">
    <section class="dashboard-workbench learning-workbench span-12" :class="{ 'is-chat-mode': assistantTab === 'chat' }">
      <div v-if="assistantTab !== 'chat'" class="dashboard-workbench-head">
        <div>
          <h2>{{ selectedCourse?.title || 'AI 助手项目空间' }}</h2>
        </div>
        <div class="profile-workbench-actions">
          <button class="ghost-button" type="button" @click="startNewChat">新建聊天</button>
          <button class="ghost-button" type="button" @click="setAssistantTab('progress')">任务进度</button>
          <button class="button" type="button" @click="setAssistantTab('generate')"><Sparkles :size="17" />生成资源</button>
        </div>
      </div>

      <nav v-if="assistantTab !== 'chat'" class="assistant-section-tabs" aria-label="AI 助手功能分区">
        <button
          v-for="tab in assistantTabs"
          :key="tab.key"
          type="button"
          :class="{ active: assistantTab === tab.key }"
          @click="setAssistantTab(tab.key)"
        >
          <span>{{ tab.label }}</span>
          <small>{{ tab.count }}</small>
        </button>
      </nav>

      <ErrorNotice :message="error" />

      <div v-if="assistantTab === 'generate'" class="assistant-generate-workspace">
        <section class="assistant-generate-form" aria-label="生成资源">
          <div class="learning-console-head">
            <span>生成资源</span>
            <StatusPill :status="selectedGenerationType?.displayName || '资源类型'" tone="info" />
          </div>
          <div class="assistant-context-strip">
            <label>
              <span>课程</span>
              <select v-model="form.courseId" @change="loadHistory">
                <option value="" disabled>请选择课程</option>
                <option v-for="course in courses" :key="course.id" :value="course.id">{{ course.title }}</option>
              </select>
            </label>
            <label>
              <span>资源类型</span>
              <select v-model="generationForm.resourceType">
                <option v-for="type in resourceTypeOptions" :key="type.code" :value="type.code">{{ type.displayName }}</option>
              </select>
            </label>
            <label>
              <span>形态</span>
              <input v-model="generationForm.modality" />
            </label>
          </div>
          <label class="assistant-topic-field">
            <span>生成主题</span>
            <input v-model="generationForm.topic" placeholder="例如：第 3 章 HTTP 协议速学包" />
          </label>
          <label class="assistant-prompt-field">
            <span>生成要求</span>
            <textarea v-model="generationForm.prompt" />
          </label>
          <div class="assistant-generate-footer">
            <div>
              <strong>{{ selectedCourse?.title || '请选择课程' }}</strong>
            </div>
            <button class="button" type="button" :disabled="!canSubmitGeneration" @click="submitResourceGeneration">
              <Sparkles :size="17" />创建生成任务
            </button>
          </div>
          <LoadingBlock :show="actionLoading === 'generation'" text="正在创建生成任务" />
        </section>

        <aside class="assistant-generate-aside">
          <div class="learning-console-head">
            <span>项目空间</span>
            <strong>{{ visibleGenerationTasks.length }} 个任务</strong>
          </div>
          <article v-for="task in visibleGenerationTasks.slice(0, 4)" :key="task.id" :class="{ recoverable: isTaskRecoverableFailure(task) }">
            <StatusPill :status="generationTaskStatusLabel(task)" :tone="generationTaskTone(task)" />
            <strong>{{ task.topic }}</strong>
            <p>{{ isTaskRecoverableFailure(task) ? '旧任务可重试，资源服务解析兜底已启用。' : taskDisplayMessage(task) }}</p>
            <button v-if="isTaskRecoverableFailure(task)" type="button" class="inline-retry-button" @click="prefillGenerationFromTask(task)">用此主题重试</button>
          </article>
          <div v-if="!visibleGenerationTasks.length" class="empty-guide compact-empty">
            <strong>本课程暂无生成任务</strong>
          </div>
        </aside>
      </div>

      <div v-else-if="assistantTab === 'progress'" class="assistant-progress-workspace">
        <div class="learning-console-head">
          <div>
            <span>任务进度</span>
            <strong>{{ selectedCourse?.title || '当前课程' }}</strong>
          </div>
          <button class="ghost-button" type="button" :disabled="actionLoading === 'task-refresh'" @click="refreshGenerationTasks">
            <RefreshCw :size="17" />同步任务
          </button>
        </div>
        <div v-if="!visibleGenerationTasks.length" class="assistant-empty-panel assistant-progress-empty">
          <div class="assistant-empty-copy">
            <span>运行队列为空</span>
            <strong>还没有生成任务</strong>
          </div>
          <div class="assistant-empty-steps" aria-label="生成任务步骤">
            <article>
              <span>01</span>
              <strong>选择资源类型</strong>
            </article>
            <article>
              <span>02</span>
              <strong>填写生成要求</strong>
            </article>
            <article>
              <span>03</span>
              <strong>回到任务进度</strong>
            </article>
          </div>
          <button class="button" type="button" @click="setAssistantTab('generate')"><Sparkles :size="17" />去生成资源</button>
        </div>
        <div v-else class="assistant-task-board">
          <article
            v-for="task in visibleGenerationTasks"
            :key="task.id"
            :class="{
              spotlight: String(route.query.taskId || '') === task.id,
              failed: isTaskHardFailed(task),
              recoverable: isTaskRecoverableFailure(task),
            }"
          >
            <div class="assistant-task-head">
              <div>
                <span>{{ task.currentStep || '智能体任务' }}</span>
                <strong>{{ task.topic }}</strong>
              </div>
              <StatusPill :status="generationTaskStatusLabel(task)" :tone="generationTaskTone(task)" />
            </div>
            <p>{{ taskDisplayMessage(task) }}</p>
            <div class="assistant-task-progress">
              <span :style="{ width: `${taskProgressPercent(task)}%` }" />
            </div>
            <small>{{ taskProgressPercent(task) }}% · 更新于 {{ formatDate(task.updatedAt || task.createdAt) }}</small>
            <div class="assistant-task-actions">
              <button v-if="isTaskRecoverableFailure(task)" type="button" class="inline-retry-button" @click="prefillGenerationFromTask(task)">用此主题重试</button>
              <RouterLink :to="`/tasks/${task.id}`">查看任务详情</RouterLink>
            </div>
          </article>
        </div>
      </div>

      <div v-else-if="assistantTab === 'history'" class="assistant-history-workspace">
        <div class="learning-console-head">
          <div>
            <span>历史记录</span>
            <strong>{{ historyTotal }} 条</strong>
          </div>
          <button class="ghost-button" type="button" @click="loadHistory"><RefreshCw :size="17" />刷新记录</button>
        </div>
        <div class="assistant-history-summary">
          <article v-for="item in learningStats" :key="item.label">
            <span>{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
            <small>{{ item.detail }}</small>
          </article>
        </div>
        <div v-if="historyTotal === 0" class="assistant-empty-panel assistant-history-empty">
          <div class="assistant-empty-copy">
            <span>等待学习证据</span>
            <strong>还没有可回放的历史记录</strong>
          </div>
          <div class="assistant-empty-steps" aria-label="历史记录来源">
            <article>
              <span>问</span>
              <strong>发起一次答疑</strong>
            </article>
            <article>
              <span>生</span>
              <strong>生成学习资源</strong>
            </article>
            <article>
              <span>测</span>
              <strong>记录测评结果</strong>
            </article>
          </div>
          <div class="assistant-empty-actions">
            <button class="ghost-button" type="button" @click="startNewChat">新建聊天</button>
            <button class="button" type="button" @click="setAssistantTab('generate')"><Sparkles :size="17" />生成资源</button>
          </div>
        </div>
        <div v-else class="assistant-history-detail">
          <section>
            <h3>学习事件</h3>
            <div v-if="!courseEvents.length" class="assistant-context-empty">暂无学习事件。</div>
            <article v-for="item in courseEvents.slice(0, 6)" :key="item.id">
              <strong>{{ eventTypeLabel(item.eventType) }}</strong>
              <p>{{ learningEventSummary(item.eventPayload || item.resourceId || '-') }}</p>
              <small>{{ formatDate(item.createdAt) }}</small>
            </article>
          </section>
          <section>
            <h3>答疑记录</h3>
            <div v-if="!courseTutoringHistory.length" class="assistant-context-empty">暂无答疑记录。</div>
            <article v-for="(item, index) in courseTutoringHistory.slice(0, 6)" :key="index">
              <strong>{{ item.question || item.topic || `答疑 ${index + 1}` }}</strong>
              <p>{{ compact(item.answer || item.summary || item.content || '-', 140) }}</p>
              <small>{{ formatDate(String(item.createdAt || '')) }}</small>
            </article>
          </section>
          <section>
            <h3>测评与报告</h3>
            <div v-if="!courseAttempts.length && !reports.length" class="assistant-context-empty">暂无测评或报告。</div>
            <article v-for="item in courseAttempts.slice(0, 4)" :key="item.id">
              <strong>{{ item.topic }}</strong>
              <p>{{ compact(item.weaknessSignals, 120) }}</p>
              <small>{{ item.score }}/{{ item.maxScore }} · {{ formatDate(item.createdAt) }}</small>
            </article>
            <article v-for="item in reports.slice(0, 2)" :key="item.id">
              <strong>{{ item.title || item.id }}</strong>
              <p>{{ compact(item.summary || item.reportJson, 140) }}</p>
              <small>{{ formatDate(item.createdAt) }}</small>
            </article>
          </section>
        </div>
      </div>

      <div v-else class="learning-command-band is-chat-direct" :style="chatGridStyle">
        <div class="learning-course-rail" aria-label="学习课程切换">
          <template v-if="showCourseList">
            <div class="assistant-project-head">
              <strong>课程项目空间</strong>
              <button type="button" @click="startNewChat">+ 新建空间</button>
            </div>
            <button
              v-for="course in courseSwitchCards"
              :key="course.id"
              type="button"
              class="course-space-item"
              :class="{ active: course.active }"
              @click="switchCourse(course.id)"
            >
              <span>{{ course.department }}</span>
              <strong>{{ course.title }}</strong>
              <small>{{ course.creditHours }} 学时</small>
            </button>
          </template>
          <template v-else>
            <div class="assistant-project-head">
              <button type="button" class="back-to-projects" style="display: inline-flex; align-items: center; gap: 4px;" @click="showCourseList = true">
                <ChevronLeft :size="16" /> 返回项目列表
              </button>
            </div>
            <div class="assistant-project-head session-head">
              <strong>{{ archivedConversationsVisible ? '已关闭空间' : '会话记录' }}</strong>
              <div class="assistant-session-actions">
                <button type="button" :disabled="conversationLoading" @click="toggleArchivedConversations">
                  {{ archivedConversationsVisible ? '返回当前' : '已关闭' }}
                </button>
                <button v-if="!archivedConversationsVisible" type="button" :disabled="conversationLoading" @click="startNewChat">+ 新建</button>
              </div>
            </div>
            <div v-if="conversationLoading" class="assistant-context-empty">正在同步会话...</div>
            <div
              v-for="conversation in conversations"
              :key="conversation.id"
              class="chat-space-item"
              :class="{ active: conversation.id === activeConversationId, renaming: conversation.id === renamingConversationId }"
            >
              <template v-if="conversation.id === renamingConversationId">
                <input
                  v-model="renameDraft"
                  class="chat-space-rename-input"
                  type="text"
                  :placeholder="conversation.title"
                  @keyup.enter="commitRenameConversation(conversation.id)"
                  @keyup.esc="cancelRenameConversation()"
                />
                <div class="chat-space-rename-actions">
                  <button type="button" title="保存" @click="commitRenameConversation(conversation.id)"><Check :size="15" /></button>
                  <button type="button" title="取消" @click="cancelRenameConversation()"><X :size="15" /></button>
                </div>
              </template>
              <template v-else>
                <button type="button" class="chat-space-main" @click="selectConversation(conversation.id)">
                  <strong>{{ conversation.title }}</strong>
                  <small v-if="conversation.lastMessagePreview">{{ compact(conversationPreviewText(conversation.lastMessagePreview), 42) }}</small>
                  <span>{{ formatDate(conversation.lastMessageAt || conversation.updatedAt || conversation.createdAt) }}</span>
                </button>
                <button
                  type="button"
                  class="chat-space-action"
                  :aria-expanded="conversationMenuId === conversation.id"
                  title="更多操作"
                  @click.stop="toggleConversationMenu(conversation.id)"
                >
                  <MoreHorizontal :size="16" />
                </button>
                <div v-if="conversationMenuId === conversation.id" class="chat-space-menu" role="menu">
                  <button type="button" @click="beginRenameConversation(conversation)"><Pencil :size="14" /> 重命名</button>
                  <button type="button" @click="updateConversationArchived(conversation.id, !archivedConversationsVisible)">
                    <Download :size="14" /> {{ archivedConversationsVisible ? '恢复会话' : '归档会话' }}
                  </button>
                  <button type="button" class="is-danger" @click="deleteConversation(conversation.id)"><Trash2 :size="14" /> 删除</button>
                </div>
              </template>
            </div>
            <div v-if="!conversationApiAvailable" class="assistant-context-empty">会话接口暂不可用，本页会兼容旧答疑记录。</div>
            <div v-else-if="!conversations.length && !conversationLoading" class="assistant-context-empty">
              {{ archivedConversationsVisible ? '暂无已关闭空间。' : '暂无会话，点击新建或直接提问。' }}
            </div>

          </template>
        </div>

        <div v-if="false" class="learning-session-board" aria-label="当前学习会话">
          <div class="learning-session-main">
            <span>当前学习会话</span>
            <h3>{{ currentLearningMission.title }}</h3>
            <p>{{ selectedCourseDescription }}</p>
            <div class="home-stage-actions">
              <button class="button" :disabled="!canRunTutoring" @click="runTutoring"><Send :size="17" />发起答疑</button>
              <button class="ghost-button" :disabled="!canGenerateAssessment" @click="generateAssessment">
                <ShieldCheck :size="17" />生成测评
              </button>
            </div>
          </div>
          <div class="learning-session-stats">
            <div v-for="item in learningCycleStats" :key="item.label">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
              <small>{{ item.detail }}</small>
            </div>
          </div>
        </div>

        <div
          class="panel-resizer"
          role="separator"
          aria-orientation="vertical"
          title="拖动调整宽度，双击恢复默认"
          @pointerdown="chatStartResize(0, $event)"
          @dblclick="chatResetLayout()"
        ></div>

        <div class="learning-agent-console" aria-label="课程 AI 助手项目空间">
          <section class="assistant-chat-stage" aria-label="课程 AI 助手对话">
            <header class="assistant-chat-header">
              <div>
                <h3>{{ selectedCourse?.title || 'Java Web 应用开发与软件工程实践' }}</h3>
              </div>
              <div class="assistant-chat-actions">
                <button class="ghost-button" type="button" @click="startNewChat"><Plus :size="15" /> 新建聊天</button>
                <button class="ghost-button" type="button" @click="openAttachmentPicker"><UploadCloud :size="15" /> 上传资料</button>
                <button class="ghost-button" type="button" @click="setAssistantTab('generate')"><Sparkles :size="15" /> 生成资源</button>
              </div>
            </header>



            <div class="assistant-thread-scroll">
              <article
                v-for="message in activeConversationMessages"
                :key="message.id"
                class="assistant-turn"
                :class="message.role === 'user' ? 'is-user' : 'is-ai'"
              >
                <div v-if="message.role !== 'user'" class="assistant-avatar">AI</div>
                <div>
                  <div class="assistant-turn-meta">
                    <strong>{{ message.role === 'user' ? '你' : 'AI 助手' }}</strong>
                    <span>{{ formatDate(message.createdAt) }}</span>
                  </div>
                  <div class="assistant-bubble">
                    <MarkdownView v-if="message.role !== 'user'" :content="message.content" />
                    <template v-else>{{ message.content }}</template>
                    <MermaidDiagram
                      v-if="message.role !== 'user' && message.mermaidDiagram"
                      :code="message.mermaidDiagram"
                      class="assistant-bubble-diagram"
                    />
                    <small v-if="message.role !== 'user' && message.fallbackUsed" class="assistant-fallback-note">
                      模型服务超时，已使用本地降级建议
                    </small>
                    <div v-if="message.role !== 'user' && (message.citations?.length || message.learningActions?.length)" class="assistant-answer-evidence">
                      <span v-for="(item, index) in asStringArray(message.citations).slice(0, 3)" :key="`citation-${message.id}-${index}`">引用：{{ item }}</span>
                      <span v-for="(item, index) in asStringArray(message.learningActions).slice(0, 3)" :key="`action-${message.id}-${index}`">行动：{{ item }}</span>
                    </div>
                  </div>
                </div>
                <div v-if="message.role === 'user'" class="assistant-user-avatar">{{ selectedProfile?.studentName?.slice(0, 1) || '我' }}</div>
              </article>

              <article v-if="!hasConversationMessages && !tutoringResult && actionLoading !== 'tutoring'" class="assistant-chat-empty">
                <strong>直接向本课程 AI 助教提问</strong>
                <div>
                  <button v-for="prompt in quickTutoringPrompts" :key="prompt.title" type="button" @click="applyTutoringPrompt(prompt)">
                    {{ prompt.title }}
                  </button>
                </div>
              </article>

              <article v-if="actionLoading === 'tutoring' && !tutoringResult && !hasPendingAssistantMessage" class="assistant-turn is-ai">
                <div class="assistant-avatar">AI</div>
                <div>
                  <div class="assistant-turn-meta"><strong>AI 助手</strong><span>正在生成</span></div>
                  <div class="assistant-bubble">
                    <LoadingBlock :show="true" text="正在生成辅导回答" />
                  </div>
                </div>
              </article>

              <article v-if="!hasConversationMessages && tutoringResult" class="assistant-turn is-ai">
                <div class="assistant-avatar">AI</div>
                <div>
                  <div class="assistant-turn-meta"><strong>AI 助手</strong><span>刚刚</span></div>
                  <div class="assistant-bubble">
                    <MarkdownView :content="answerMarkdown" />
                    <MermaidDiagram v-if="answerMermaid" :code="answerMermaid" class="assistant-bubble-diagram" />
                    <div class="assistant-answer-evidence">
                      <span v-for="item in citations.slice(0, 3)" :key="item">引用：{{ item }}</span>
                      <span v-for="item in learningActions.slice(0, 3)" :key="item">行动：{{ item }}</span>
                    </div>
                  </div>
                </div>
              </article>

              <article v-for="(item, index) in fallbackChatHistoryPreview" :key="index" class="assistant-turn is-ai is-history">
                <div class="assistant-avatar">AI</div>
                <div>
                  <div class="assistant-turn-meta"><strong>历史答疑</strong><span>{{ formatDate(String(item.createdAt || '')) }}</span></div>
                  <div class="assistant-bubble">
                    <p>{{ compact(item.answer || item.summary || item.content || item.question || '-', 170) }}</p>
                  </div>
                </div>
              </article>
            </div>

            <footer class="assistant-main-composer">
              <input
                ref="attachmentInput"
                class="assistant-attachment-input"
                type="file"
                accept="image/*,.pdf,.ppt,.pptx,.doc,.docx,.txt,.md,.zip"
                multiple
                @change="handleAttachmentFiles"
              />
              <textarea
                v-model="form.question"
                aria-label="向本课程 AI 助手提问"
                placeholder="向本课程 AI 助手提问，粘贴图片也会作为附件发送"
                @paste="handleComposerPaste"
                @keydown.enter.exact.prevent="runTutoring"
              />
              <div v-if="referencePanelOpen" class="assistant-reference-popover">
                <div class="assistant-reference-popover-head">
                  <strong>引用到本条消息</strong>
                  <button type="button" aria-label="关闭引用选择" @click="applyReferenceResources">
                    <X :size="14" />
                  </button>
                </div>
                <div v-if="recentResources.length" class="assistant-reference-options">
                  <button
                    v-for="resource in recentResources"
                    :key="resource.id"
                    type="button"
                    :class="{ active: selectedReferenceResourceIds.includes(resource.id) }"
                    @click="toggleReferenceResource(resource.id)"
                  >
                    <span>{{ resource.resourceTypeName || resource.resourceType || '资料' }}</span>
                    <strong>{{ resource.title }}</strong>
                    <Check v-if="selectedReferenceResourceIds.includes(resource.id)" :size="14" />
                  </button>
                </div>
                <div v-else class="assistant-context-empty">当前课程暂无可引用资料。</div>
              </div>
              <div v-if="uploadingAttachment || uploadedAttachments.length || selectedReferenceResources.length" class="assistant-composer-context">
                <span v-if="uploadingAttachment" class="assistant-upload-chip">附件上传中...</span>
                <button v-for="asset in uploadedAttachments" :key="asset.id" class="assistant-context-chip" type="button" @click="removeUploadedAttachment(asset.id)">
                  <span>附件</span>
                  <strong>{{ asset.originalFilename }}</strong>
                  <X :size="12" />
                </button>
                <button v-for="resource in selectedReferenceResources" :key="resource.id" class="assistant-context-chip" type="button" @click="toggleReferenceResource(resource.id)">
                  <span>引用</span>
                  <strong>{{ resource.title }}</strong>
                  <X :size="12" />
                </button>
              </div>
              <div class="assistant-composer-tools">
                <div>
                  <button type="button" :disabled="uploadingAttachment" @click="openAttachmentPicker">
                    <Paperclip :size="15" /> {{ uploadingAttachment ? '上传中' : '附件' }}
                  </button>
                  <button type="button" @click="toggleReferencePanel"><AtSign :size="15" /> 引用</button>
                </div>
                <button class="assistant-send-button" type="button" :disabled="!canRunTutoring" @click="runTutoring">
                  <Send :size="18" />
                </button>
              </div>
            </footer>
          </section>

          <aside class="assistant-course-context" aria-label="课程上下文">
            <div v-if="recentConversationList.length" class="assistant-context-card assistant-session-card">
              <div class="assistant-context-head">
                <strong>最近会话</strong>
                <button type="button" @click="startNewChat">新对话</button>
              </div>
              <button
                v-for="conversation in recentConversationList"
                :key="conversation.id"
                type="button"
                :class="{ active: conversation.id === activeConversationId }"
                @click="selectConversation(conversation.id)"
              >
                <strong>{{ conversation.title }}</strong>
                <small v-if="conversation.lastMessagePreview">{{ compact(conversationPreviewText(conversation.lastMessagePreview), 44) }}</small>
              </button>
            </div>

            <div class="assistant-context-card">
              <div class="assistant-context-head">
                <strong>可引用资料</strong>
                <span>{{ recentResources.length || resources.length }}</span>
              </div>
              <article v-for="resource in recentResources" :key="resource.id" class="assistant-file-row">
                <span>{{ resource.resourceTypeName || resource.resourceType || '资料' }}</span>
                <div>
                  <strong>{{ resource.title }}</strong>
                  <small>{{ resource.modality || '学习资源' }} · {{ resource.estimatedMinutes || 8 }} 分钟</small>
                </div>
              </article>
              <div v-if="!recentResources.length" class="assistant-context-empty">当前课程暂无可引用资料。</div>
            </div>

            <div class="assistant-context-card">
              <div class="assistant-context-head">
                <strong>当前章节</strong>
                <StatusPill status="学习中" tone="ok" />
              </div>
              <h4>第 {{ activeCoursePosition }} 章 {{ form.topic }}</h4>
              <div class="assistant-context-progress"><span :style="{ width: `${activeCourseProgress}%` }" /></div>
              <small>进度 {{ activeCourseProgress }}%</small>
            </div>

            <div class="assistant-context-card">
              <div class="assistant-context-head">
                <strong>本课画像摘要</strong>
                <button type="button" @click="setAssistantTab('history')">查看详情</button>
              </div>
              <dl class="assistant-profile-grid">
                <template v-for="row in contextMasteryRows" :key="row.label">
                  <dt>{{ row.label }}</dt>
                  <dd>{{ row.value }}</dd>
                </template>
              </dl>
            </div>

            <div class="assistant-context-card">
              <div class="assistant-context-head">
                <strong>最近生成资源</strong>
                <button type="button" @click="setAssistantTab('progress')">查看全部</button>
              </div>
              <article v-for="item in recentGeneratedResources.slice(0, 3)" :key="item.id" class="assistant-resource-row">
                <div>
                  <strong>{{ item.title }}</strong>
                  <small>{{ item.meta }}</small>
                </div>
                <span>{{ item.status }}</span>
              </article>
              <div v-if="!recentGeneratedResources.length" class="assistant-context-empty">暂无资源</div>
            </div>
          </aside>
        </div>

      </div>
    </section>

    <section v-if="false && assistantTab === 'chat'" class="home-panel learning-work-panel learning-flow-panel span-12">
      <div class="section-head">
        <div>
          <p>学习闭环</p>
          <h2>按课程资源推进，而不是和 AI 空聊</h2>
        </div>
        <StatusPill :status="hasContext ? '上下文已就绪' : '待选择上下文'" :tone="hasContext ? 'ok' : 'warn'" />
      </div>
      <div class="learning-path-runway">
        <article v-for="stage in learningPathStages" :key="stage.label">
          <span>{{ stage.label }}</span>
          <strong>{{ stage.title }}</strong>
          <p>{{ stage.detail }}</p>
        </article>
      </div>
    </section>

    <SectionPanel v-if="false && assistantTab === 'chat'" class="span-12 learning-context-panel" title="学习设置" subtitle="切换画像和课程，调整本次答疑与测评范围">
      <template #actions>
        <button class="ghost-button" @click="loadOptions"><RefreshCw :size="17" />刷新</button>
        <button class="ghost-button" :disabled="!hasLearningData" @click="downloadLearningJson">
          <Download :size="17" />导出学习数据
        </button>
        <button class="ghost-button" :disabled="!hasLearningData" @click="downloadLearningMarkdown">
          <Download :size="17" />导出学习报告
        </button>
      </template>
      <ErrorNotice :message="error" />
      <LoadingBlock :show="loading" />
      <div class="split-row">
        <div class="field">
          <label>学生画像 <span class="required-mark">*</span></label>
          <select v-model="form.studentProfileId" @change="loadHistory">
            <option value="" disabled>请选择学生画像</option>
            <option v-for="profile in profiles" :key="profile.id" :value="profile.id">{{ profile.studentName }} - {{ profile.learningGoal }}</option>
          </select>
        </div>
        <div class="field">
          <label>课程 <span class="required-mark">*</span></label>
          <select v-model="form.courseId" @change="loadHistory">
            <option value="" disabled>请选择课程</option>
            <option v-for="course in courses" :key="course.id" :value="course.id">{{ course.title }}</option>
          </select>
        </div>
      </div>
      <div v-if="contextHint" class="notice warn-notice">
        <span>{{ contextHint }}</span>
      </div>
      <LoadingBlock :show="historyLoading" text="正在同步学习记录" />
    </SectionPanel>

    <SectionPanel v-if="false && assistantTab === 'chat'" class="span-12 learning-evidence-panel" title="学习证据补充" subtitle="记录资源完成情况和测评结果，用于更新画像、掌握度和后续推荐">
      <div class="record-action-grid">
        <div class="record-action-card">
          <div class="section-head">
            <div>
              <p>学习事件</p>
              <h3>资源使用反馈</h3>
            </div>
            <StatusPill status="画像更新触发点" tone="info" />
          </div>
          <div class="form-grid">
            <div class="field">
              <label>绑定资源</label>
              <select v-model="eventForm.resourceId">
                <option value="">不绑定具体资源</option>
                <option v-for="resource in resources" :key="resource.id" :value="resource.id">
                  {{ resource.title }} - {{ resource.resourceTypeName || resource.resourceType }}
                </option>
              </select>
            </div>
            <div class="split-row">
              <div class="field">
                <label>事件类型</label>
                <select v-model="eventForm.eventType">
                  <option value="RESOURCE_OPEN">打开资源</option>
                  <option value="RESOURCE_COMPLETE">完成学习</option>
                  <option value="RESOURCE_FEEDBACK">提交反馈</option>
                  <option value="PRACTICE_FINISH">完成实操</option>
                </select>
              </div>
              <div class="field">
                <label>停留分钟</label>
                <input v-model.number="eventForm.durationMinutes" type="number" min="0" />
              </div>
            </div>
            <div class="field">
              <label>反馈分</label>
              <input v-model.number="eventForm.feedbackScore" type="range" min="1" max="5" />
              <small class="field-help">当前 {{ eventForm.feedbackScore }} 分；低分会触发薄弱点画像更新。</small>
            </div>
            <div class="field">
              <label>学习备注</label>
              <textarea v-model="eventForm.eventPayload" />
            </div>
            <button class="button" :disabled="!canRecordEvent" @click="recordLearningEvent">
              <Send :size="17" />记录学习行为
            </button>
            <LoadingBlock :show="actionLoading === 'event'" text="正在写入学习行为" />
          </div>
        </div>

        <div class="record-action-card">
          <div class="section-head">
            <div>
              <p>效果评估</p>
              <h3>测评结果记录</h3>
            </div>
            <StatusPill status="掌握度更新触发点" tone="ok" />
          </div>
          <div class="form-grid">
            <div class="field">
              <label>关联资源</label>
              <select v-model="quizForm.resourceId">
                <option value="">不绑定具体资源</option>
                <option v-for="resource in resources" :key="resource.id" :value="resource.id">
                  {{ resource.title }} - {{ resource.resourceTypeName || resource.resourceType }}
                </option>
              </select>
            </div>
            <div class="split-row">
              <div class="field">
                <label>得分</label>
                <input v-model.number="quizForm.score" type="number" min="0" />
              </div>
              <div class="field">
                <label>满分</label>
                <input v-model.number="quizForm.maxScore" type="number" min="1" />
              </div>
            </div>
            <div class="split-row">
              <div class="field">
                <label>正确题数</label>
                <input v-model.number="quizForm.correctCount" type="number" min="0" />
              </div>
              <div class="field">
                <label>总题数</label>
                <input v-model.number="quizForm.totalCount" type="number" min="1" />
              </div>
            </div>
            <div class="field">
              <label>薄弱点</label>
              <textarea v-model="quizForm.weakPoints" />
            </div>
            <button class="button" :disabled="!canRecordQuiz" @click="recordQuizAttempt">
              <CheckCircle2 :size="17" />保存测评结果
            </button>
            <LoadingBlock :show="actionLoading === 'quiz-record'" text="正在更新掌握度和评估报告" />
          </div>
        </div>
      </div>
    </SectionPanel>

    <SectionPanel v-if="false && assistantTab === 'chat'" class="span-7 learning-tutor-panel" title="学习会话" subtitle="围绕课程、画像和当前问题生成可追溯辅导回答">
      <template #actions>
        <button class="ghost-button" :disabled="!tutoringResult" @click="downloadTutoringMarkdown"><Download :size="17" />导出答疑</button>
      </template>
      <div class="learning-chat-shell">
        <div class="tutor-prompt-dock" aria-label="常用学习问题">
          <button
            v-for="item in quickTutoringPrompts"
            :key="item.title"
            type="button"
            @click="applyTutoringPrompt(item)"
          >
            <span>{{ item.title }}</span>
            <small>{{ item.modality }}</small>
          </button>
        </div>

        <div class="tutor-thread">
          <article class="tutor-message tutor-message-user">
            <div class="tutor-avatar">我</div>
            <div class="tutor-bubble">
              <span>{{ selectedProfile?.studentName || '当前学生' }} · {{ selectedCourse?.title || '当前课程' }}</span>
              <p>{{ form.question || '输入问题后，AI 助教会结合课程资料和学生画像回答。' }}</p>
            </div>
          </article>

          <article class="tutor-message tutor-message-assistant">
            <div class="chat-bubble user" v-if="actionLoading === 'tutoring' || tutoringResult"><p>{{ form.question }}</p></div>
            <div class="tutor-avatar">AI</div>
            <div class="chat-bubble">
              <div class="tutor-answer-head">
                <div>
                  <span>课程证据驱动回答</span>
                  <strong>{{ form.modality || '文本辅导' }}</strong>
                </div>
                <StatusPill :status="hasContext ? '已选上下文' : '待选上下文'" :tone="hasContext ? 'ok' : 'warn'" />
              </div>
              <LoadingBlock :show="actionLoading === 'tutoring' && !tutoringResult" text="正在生成辅导回答" />
              <div v-if="!tutoringResult" class="tutor-answer-empty">
                <strong>提交后在这里进入连续答疑。</strong>
                <span>回答会同步输出引用、追问、学习行动和画像信号，便于学生继续学习。</span>
              </div>
              <template v-else>
                <MarkdownView :content="answerMarkdown" />
                <div class="learning-chip-grid tutor-evidence-grid">
                  <div>
                    <strong>引用</strong>
                    <span v-for="item in citations" :key="item">{{ item }}</span>
                    <small v-if="!citations.length">暂无引用</small>
                  </div>
                  <div>
                    <strong>追问</strong>
                    <span v-for="item in followUpQuestions" :key="item">{{ item }}</span>
                    <small v-if="!followUpQuestions.length">暂无追问</small>
                  </div>
                  <div>
                    <strong>学习行动</strong>
                    <span v-for="item in learningActions" :key="item">{{ item }}</span>
                    <small v-if="!learningActions.length">暂无学习行动</small>
                  </div>
                  <div>
                    <strong>画像信号</strong>
                    <span v-for="item in profileSignals" :key="item">{{ item }}</span>
                    <small v-if="!profileSignals.length">暂无画像信号</small>
                  </div>
                </div>
              </template>
            </div>
          </article>
        </div>

        <div class="tutor-composer">
          <div class="field tutor-composer-question">
            <label>输入问题 <span class="required-mark">*</span></label>
            <textarea v-model="form.question" />
            <small v-if="!form.question.trim()" class="field-error">请输入答疑问题。</small>
          </div>
          <div class="tutor-context-drawer">
            <div class="field">
              <label>回答形态</label>
              <input v-model="form.modality" />
            </div>
            <div class="field">
              <label>补充资料</label>
              <textarea v-model="form.documentText" />
            </div>
          </div>
          <button class="button tutor-send-button" :disabled="!canRunTutoring" @click="runTutoring">
            <Send :size="17" />发送问题
          </button>
        </div>
      </div>
    </SectionPanel>

    <SectionPanel v-if="false && assistantTab === 'chat'" class="span-5 learning-assessment-panel" title="随堂测评" subtitle="生成小测、记录作答、输出错因和下一步学习建议">
      <template #actions>
        <button class="ghost-button" :disabled="!assessmentResult && !gradeResult" @click="downloadAssessmentJson">
          <Download :size="17" />导出测评
        </button>
      </template>
      <div class="assessment-workbench">
        <div class="assessment-config-bar">
          <div class="field">
            <label>测评主题 <span class="required-mark">*</span></label>
            <input v-model="form.topic" />
          </div>
          <div class="field assessment-count-field">
            <label>题量</label>
            <input v-model.number="form.count" type="number" min="1" max="12" />
          </div>
          <div class="field">
            <label>难度</label>
            <select v-model="form.difficulty">
              <option value="入门">入门</option>
              <option value="自适应">自适应</option>
              <option value="进阶">进阶</option>
              <option value="挑战">挑战</option>
            </select>
          </div>
          <button class="button assessment-generate-button" :disabled="!canGenerateAssessment" @click="generateAssessment">
            <Send :size="17" />生成题单
          </button>
        </div>

        <div class="assessment-type-strip" aria-label="题型选择">
          <label v-for="type in questionTypeOptions" :key="type">
            <input v-model="form.questionTypes" type="checkbox" :value="type" />
            <span>{{ type }}</span>
          </label>
        </div>
        <small v-if="!form.questionTypes.length" class="field-error">请至少选择一种题型。</small>

        <LoadingBlock :show="actionLoading === 'assessment' || actionLoading === 'grade'" />
        <div v-if="!questions.length" class="assessment-empty-state">
          <strong>等待题单生成</strong>
          <span>系统会依据当前课程、学生画像和薄弱点生成题目，学生作答后进入自动批改。</span>
        </div>
        <div v-else class="assessment-question-stack">
          <article v-for="(question, index) in questions" :key="question.id" class="assessment-question-card">
            <div class="assessment-question-head">
              <div>
                <span>第 {{ index + 1 }} 题 · {{ question.knowledgePoints.join(' / ') || question.difficulty }}</span>
                <strong>{{ question.stem }}</strong>
              </div>
              <StatusPill :status="question.type" tone="info" />
            </div>
            <p v-if="question.options.length" class="assessment-options">{{ question.options.join(' / ') }}</p>
            <small v-if="question.rubric" class="assessment-rubric">评分标准：{{ question.rubric }}</small>
            <div class="field assessment-answer-field">
              <label>学生答案 <span class="required-mark">*</span></label>
              <textarea v-model="answers[question.id]" />
            </div>
          </article>

          <div class="assessment-submit-bar">
            <div>
              <strong>{{ questions.length }} 题待批改</strong>
              <span>批改后会写入错因、掌握度和画像更新建议。</span>
            </div>
            <button class="button" :disabled="!canGrade" @click="gradeAssessment">提交批改</button>
          </div>
          <small v-if="questions.length && !canGrade" class="field-error">请补齐所有学生答案后再批改。</small>
        </div>
      </div>
    </SectionPanel>

    <SectionPanel v-if="false && assistantTab === 'chat'" class="span-6 learning-grade-panel" title="批改结果">
      <div v-if="!gradeResult" class="empty-guide">
        <strong>等待批改结果</strong>
        <span>自动批改后给出总分、逐题反馈、薄弱点、资源建议和画像更新建议。</span>
      </div>
      <template v-else>
        <div class="grade-hero">
          <strong>{{ gradeScore }} / {{ gradeMaxScore }}</strong>
          <StatusPill :status="`${gradePercent}%`" :tone="gradePercent >= 80 ? 'ok' : gradePercent >= 60 ? 'warn' : 'danger'" />
          <p>{{ gradeFeedback }}</p>
        </div>
        <div class="learning-chip-grid">
          <div>
            <strong>薄弱点</strong>
            <span v-for="item in weaknessSignals" :key="item">{{ item }}</span>
            <small v-if="!weaknessSignals.length">暂无薄弱点</small>
          </div>
          <div>
            <strong>下一步资源</strong>
            <span v-for="item in nextResourceTypes" :key="item">{{ item }}</span>
            <small v-if="!nextResourceTypes.length">暂无资源建议</small>
          </div>
          <div>
            <strong>画像更新建议</strong>
            <span v-for="item in profileUpdateSuggestions" :key="item">{{ item }}</span>
            <small v-if="!profileUpdateSuggestions.length">暂无画像更新建议</small>
          </div>
        </div>
        <div v-if="itemFeedback.length" class="timeline">
          <div v-for="(item, index) in itemFeedback" :key="index" class="timeline-body">
            <strong>{{ item.questionId || item.stem || `题目 ${index + 1}` }}</strong>
            <p>{{ item.feedback || item.comment || item.analysis || '-' }}</p>
          </div>
        </div>
      </template>
    </SectionPanel>

    <SectionPanel v-if="false && assistantTab === 'chat'" class="span-6 learning-effect-panel" title="学习效果可视化">
      <ChartPanel :option="scoreOption" :height="240" />
      <ChartPanel :option="masteryOption" :height="260" />
    </SectionPanel>

    <SectionPanel v-if="false && assistantTab === 'history'" class="span-12 learning-records-panel" title="学习记录">
      <LoadingBlock :show="historyLoading" />
      <div class="record-grid">
        <div>
          <h3>学习事件</h3>
          <div v-if="!events.length" class="empty-guide"><strong>暂无学习事件</strong><span>当前还没有同步到学习行为记录。</span></div>
          <div v-else class="timeline">
            <div v-for="item in events.slice(0, 6)" :key="item.id" class="timeline-body">
              <div class="section-head">
                <strong>{{ eventTypeLabel(item.eventType) }}</strong>
                <StatusPill :status="formatDate(item.createdAt)" tone="muted" />
              </div>
              <p>{{ learningEventSummary(item.eventPayload || item.resourceId || '-') }}</p>
            </div>
          </div>
        </div>
        <div>
          <h3>答疑记录</h3>
          <div v-if="!tutoringHistory.length" class="empty-guide"><strong>暂无答疑记录</strong><span>学生提交问题后会在这里沉淀答疑记录。</span></div>
          <div v-else class="timeline">
            <div v-for="(item, index) in tutoringHistory.slice(0, 6)" :key="index" class="timeline-body">
              <strong>{{ item.question || item.topic || `答疑 ${index + 1}` }}</strong>
              <p>{{ compact(item.answer || item.summary || item.content || '-', 140) }}</p>
            </div>
          </div>
        </div>
        <div>
          <h3>测评记录</h3>
          <div v-if="!attempts.length" class="empty-guide"><strong>暂无测评记录</strong><span>完成测评后会形成分数、错因和反馈记录。</span></div>
          <div v-else class="timeline">
            <div v-for="item in attempts.slice(0, 6)" :key="item.id" class="timeline-body">
              <div class="section-head">
                <strong>{{ item.topic }}</strong>
                <StatusPill :status="`${item.score}/${item.maxScore}`" tone="info" />
              </div>
              <p>{{ compact(item.weaknessSignals, 120) }}</p>
              <small>{{ formatDate(item.createdAt) }}</small>
            </div>
          </div>
        </div>
        <div>
          <h3>知识掌握度</h3>
          <div v-if="!mastery.length" class="empty-guide"><strong>暂无掌握度</strong><span>系统会根据学习事件和测评结果更新知识掌握度。</span></div>
          <div v-else class="timeline">
            <div v-for="item in mastery.slice(0, 6)" :key="item.id || item.knowledgePoint" class="timeline-body">
              <div class="section-head">
                <strong>{{ item.knowledgePoint }}</strong>
                <StatusPill :status="`${Math.round(percent(item.masteryScore))}%`" tone="ok" />
              </div>
              <p>{{ compact(item.evidence, 120) }}</p>
            </div>
          </div>
        </div>
        <div>
          <h3>评估报告</h3>
          <div v-if="!reports.length" class="empty-guide"><strong>暂无评估报告</strong><span>形成阶段学习证据后会生成评估报告。</span></div>
          <div v-else class="timeline">
            <div v-for="item in reports.slice(0, 6)" :key="item.id" class="timeline-body">
              <strong>{{ item.title || item.id }}</strong>
              <p>{{ compact(item.summary || item.reportJson, 150) }}</p>
              <small>{{ formatDate(item.createdAt) }}</small>
            </div>
          </div>
        </div>
      </div>
    </SectionPanel>
  </div>
</template>
