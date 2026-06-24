<script setup lang="ts">
import {
  ArrowUp,
  BookOpenCheck,
  BrainCircuit,
  CalendarCheck,
  CheckCircle2,
  Clock3,
  FileUp,
  GraduationCap,
  Layers3,
  LibraryBig,
  LineChart,
  Loader2,
  MessageCircleQuestion,
  PlusCircle,
  Route,
  Send,
  Sparkles,
  Target,
  UploadCloud,
} from 'lucide-vue-next'
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { agentsApi, coursesApi, healthApi, learningApi, profilesApi, tasksApi } from '@/api'
import ErrorNotice from '@/components/ErrorNotice.vue'
import LoadingBlock from '@/components/LoadingBlock.vue'
import StatusPill from '@/components/StatusPill.vue'
import { useAppStore } from '@/stores/app'
import { useResizablePanels } from '@/composables/useResizablePanels'
import type {
  Course,
  EvaluationReport,
  GenerationTask,
  HealthResponse,
  KnowledgeMastery,
  LearningResource,
  ProfileResponse,
} from '@/types/api'
import { cleanDisplayText, formatResourceType } from '@/utils/format'

interface LearningPathNodeRecord {
  id?: string
  nodeOrder?: number
  knowledgePoint?: string
  resourceId?: string | null
  estimatedMinutes?: number
  status?: string
}

interface LearningPathRecord {
  id?: string
  title?: string
  status?: string
  nodes?: LearningPathNodeRecord[]
  createdAt?: string
}

interface PortalCourseCard {
  id: string
  title: string
  department: string
  creditHours: number
  source: '班级发放' | '我的自建'
  sourceKey: 'class' | 'self'
  progress: number
  nextTask: string
  signal: string
  active: boolean
}

interface PlannerMessage {
  id: string
  role: 'assistant' | 'user'
  title?: string
  body: string
  chips?: string[]
}

interface TodayTaskActionItem {
  id?: string
  title: string
  course?: string
  source?: string
  desc?: string
  status?: string
  to?: string
  tab?: 'chat' | 'generate' | 'progress' | 'history'
  courseTab?: 'tasks' | 'path' | 'resources'
  priority?: number
  minutes?: number
  action?: string
}

interface ReflectionResult {
  status: 'ai' | 'fallback' | 'pending'
  source: string
  answer: string
  actions: string[]
  signals: string[]
  citations: string[]
}

type DashboardTaskState = 'active' | 'planned' | 'deferred'
type PlanningWeightKey = 'deadline' | 'weakness' | 'course'

const loading = ref(false)
const app = useAppStore()
const router = useRouter()

// 今日学习主区两栏（任务队列 / 可调计划）列宽可拖拽并记忆
const {
  gridStyle: todayGridStyle,
  startResize: todayStartResize,
  resetLayout: todayResetLayout,
} = useResizablePanels({
  storageKey: 'today-workbench',
  defaultWeights: [1.43, 1],
  minWidths: [420, 320],
  spacing: 24,
})
const error = ref('')
const health = ref<HealthResponse | null>(null)
const tasks = ref<GenerationTask[]>([])
const profiles = ref<ProfileResponse[]>([])
const courses = ref<Course[]>([])
const resources = ref<LearningResource[]>([])
const learningPaths = ref<LearningPathRecord[]>([])
const recommendations = ref<Record<string, unknown>[]>([])
const mastery = ref<KnowledgeMastery[]>([])
const reports = ref<EvaluationReport[]>([])
const events = ref<Record<string, unknown>[]>([])
const courseBoardMode = ref<'all' | 'class' | 'self'>('all')
const plannerInput = ref('')
const plannerHistory = ref<PlannerMessage[]>([])
const dashboardTaskStates = ref<Record<string, DashboardTaskState>>({})
const dashboardFeedback = ref('')

function briefText(value?: string | null, maxLength = 42) {
  const text = cleanDisplayText(value || '')
  return text.length > maxLength ? `${text.slice(0, maxLength)}...` : text
}

function studentFacingText(value?: string | null) {
  const text = cleanDisplayText(value || '')
  if (!text) return ''
  return text
    .replaceAll(app.currentUser.name, '我')
    .replace(/张同学/g, '我')
    .replace(/李同学/g, '我')
    .replace(/学生(?=希望|需要|已经|已|完成|可以|应该|仍|偏好|目前)/g, '我')
}

function courseTopicHint(course?: Course | null) {
  const title = course?.title || ''
  const department = course?.department || ''
  const description = briefText(course?.description, 34)
  if (title.includes('Java') || title.includes('Web') || description.includes('接口')) return '完成接口分层练习'
  if (title.includes('AI') || title.includes('智能') || description.includes('智能')) return '梳理模型任务与提示词实验'
  if (title.includes('项目') || title.includes('工程') || department.includes('项目')) return '拆解需求并提交任务计划'
  if (title.includes('通识') || title.includes('素养') || title.includes('数字')) return '完成数字素养情境练习'
  return description || '选择一个知识点开始学习'
}

function matchesCourseId(item: Record<string, unknown>, courseId?: string) {
  if (!courseId) return true
  const itemCourseId = String(item.courseId || '')
  return !itemCourseId || itemCourseId === courseId
}

const studentProfiles = computed(() => profiles.value.filter((profile) => profile.studentName === app.currentUser.name))
const activeProfile = computed(() => studentProfiles.value[0] || null)
const activeCourse = computed(() => courses.value.find((course) => course.id === app.activeCourseId) || courses.value[0])
const activeCourseId = computed(() => activeCourse.value?.id || '')
const courseTasks = computed(() =>
  activeCourseId.value ? tasks.value.filter((task) => task.courseId === activeCourseId.value) : tasks.value,
)
const latestCourseTask = computed(() => courseTasks.value[0] || null)
const courseResourceIds = computed(() => new Set(resources.value.map((resource) => resource.id)))
const activePath = computed(() => {
  const resourceIds = courseResourceIds.value
  const courseId = activeCourseId.value
  return (
    learningPaths.value.find((path) => {
      const pathCourseId = String((path as unknown as Record<string, unknown>).courseId || '')
      if (courseId && pathCourseId && pathCourseId === courseId) return true
      return path.nodes?.some((node) => node.resourceId && resourceIds.has(node.resourceId))
    }) || null
  )
})
const pathNodes = computed(() => activePath.value?.nodes?.length ? activePath.value.nodes : defaultPathNodes.value)
const latestReport = computed(() => reports.value[0])
const activeCourseDescription = computed(() => cleanDisplayText(activeCourse.value?.description || '请选择课程后开始学习。'))
const latestReportSummary = computed(() => {
  const report = latestReport.value as (EvaluationReport & Record<string, unknown>) | undefined
  return studentFacingText(String(report?.reportSummary || report?.summary || ''))
})
const weakMasteryTopic = computed(() => {
  const weakItem = mastery.value
    .slice()
    .sort((a, b) => Number(a.masteryScore || 0) - Number(b.masteryScore || 0))[0]
  return briefText(weakItem?.knowledgePoint || '', 32)
})
const courseFocusBase = computed(() =>
  latestCourseTask.value?.topic ||
  weakMasteryTopic.value ||
  briefText(resources.value[0]?.title || '', 32) ||
  courseTopicHint(activeCourse.value),
)

const defaultPathNodes = computed<LearningPathNodeRecord[]>(() => [
  { nodeOrder: 1, knowledgePoint: `${courseFocusBase.value} · 先修梳理`, estimatedMinutes: 15, status: resources.value.length ? 'READY' : 'WAITING' },
  { nodeOrder: 2, knowledgePoint: `${courseFocusBase.value} · 精讲资源`, estimatedMinutes: 25, status: latestCourseTask.value || resources.value.length ? 'READY' : 'WAITING' },
  { nodeOrder: 3, knowledgePoint: `${courseFocusBase.value} · 练习测评`, estimatedMinutes: 20, status: events.value.length ? 'READY' : 'WAITING' },
  { nodeOrder: 4, knowledgePoint: `${courseFocusBase.value} · 实操巩固`, estimatedMinutes: 35, status: recommendations.value.length ? 'READY' : 'WAITING' },
])

const focusTopic = computed(() => latestCourseTask.value?.topic || pathNodes.value[0]?.knowledgePoint || courseFocusBase.value)
const roleActions = computed(() => [
  { title: '上传资料建课', desc: '上传 PPT、教材或讲义，整理个人课程草稿。', to: '/course-builder', icon: LibraryBig },
  { title: 'AI 辅导答疑', desc: '围绕课程知识点获得讲解、图解和练习。', to: '/learning', icon: MessageCircleQuestion },
  { title: '生成个性资源', desc: '按画像生成讲解文档、题库、思维导图和实操案例。', to: '/learning?tab=generate', icon: Sparkles },
])

const reportScore = computed(() => {
  const raw = Number((latestReport.value as Record<string, unknown> | undefined)?.overallScore ?? 0)
  if (!Number.isFinite(raw) || raw <= 0) return latestCourseTask.value?.progressPercent || 0
  return Math.round(raw <= 1 ? raw * 100 : raw)
})

const masteryAverage = computed(() => {
  if (!mastery.value.length) return reportScore.value
  const total = mastery.value.reduce((sum, item) => sum + Number(item.masteryScore || 0), 0)
  const avg = total / mastery.value.length
  return Math.round(avg <= 1 ? avg * 100 : avg)
})

const studyMinutes = computed(() =>
  events.value.reduce((sum, item) => sum + Number(item.durationSeconds || item.duration || 0), 0),
)

const weakSignalCount = computed(() => {
  const weakSignals = mastery.value.filter((item) => Number(item.masteryScore || 0) < 0.65).length
  return Math.max(weakSignals, latestReport.value ? 1 : 0)
})

const studyStateTitle = computed(() => {
  if (!activeProfile.value) return '先补齐我的学习画像'
  if (events.value.length) return '学习记录已同步'
  if (resources.value.length) return '可以开始学习'
  return '等待课程资源'
})

const studyStateDetail = computed(() => {
  if (!activeProfile.value) return '补齐基础、目标和偏好后，学习路径会更准。'
  if (events.value.length) {
    const minutes = studyMinutes.value ? `，累计 ${Math.round(studyMinutes.value / 60)} 分钟` : ''
    return `已沉淀 ${events.value.length} 条学习记录${minutes}。`
  }
  if (resources.value.length) return '先完成一个资源，再进入答疑或短测。'
  return '上传资料或生成资源后，学习路径会自动补全。'
})

const courseNextDetail = computed(() => {
  if (latestCourseTask.value?.currentStep) return `课程内生成进度：${taskStepLabel(latestCourseTask.value.currentStep)}`
  if (weakMasteryTopic.value) return `优先补齐「${weakMasteryTopic.value}」，再进入短测。`
  if (resources.value[0]?.title) return `先完成「${briefText(resources.value[0].title, 28)}」，再让 AI 助教出题。`
  return activeCourseDescription.value
})

const progressEvidenceText = computed(
  () =>
    latestReportSummary.value ||
    (latestCourseTask.value?.currentStep ? `课程内生成进度：${taskStepLabel(latestCourseTask.value.currentStep)}` : '完成测评和生成任务后持续更新。'),
)

const homeMission = computed(() => ({
  courseTitle: activeCourse.value?.title || '请选择课程',
  courseMeta: activeCourse.value ? `${activeCourse.value.department} · ${activeCourse.value.creditHours} 学时` : '进入课程空间选择学习课程',
  focus: focusTopic.value,
  resourceCount: resources.value.length,
  progress: masteryAverage.value || latestCourseTask.value?.progressPercent || 0,
  nextAction: latestCourseTask.value ? '继续学习与测评' : resources.value.length ? '进入 AI 助教' : '生成课程资源',
}))

const learningWorkItems = computed(() => [
  { label: '课程', value: homeMission.value.courseTitle, detail: homeMission.value.courseMeta },
  { label: '学习资源', value: `${resources.value.length} 个`, detail: resources.value[0]?.title || '生成资源后进入课程书架' },
  { label: '掌握度', value: `${homeMission.value.progress || '-'}%`, detail: latestReportSummary.value || '完成测评后持续更新' },
  { label: '学习记录', value: events.value.length ? `${events.value.length} 条` : '待记录', detail: studyMinutes.value ? `累计 ${Math.round(studyMinutes.value / 60)} 分钟` : '阅读、答疑、测评会沉淀为记录' },
])

const resourceShelf = computed(() =>
  resources.value.slice(0, 6).map((resource) => ({
    ...resource,
    title: cleanDisplayText(resource.title),
    typeName: formatResourceType(resource.resourceTypeName, resource.resourceType),
    meta: `${resource.modality} · ${resource.estimatedMinutes || 0} 分钟`,
  })),
)

const courseModules = computed(() =>
  pathNodes.value.map((node, index) => {
    const matchedResource =
      resources.value.find((resource) => resource.id === node.resourceId) ||
      (resources.value.length ? resources.value[index % resources.value.length] : null)
    const labels = ['导学', '讲解', '练习', '项目']
    return {
      key: `${node.nodeOrder || index + 1}-${node.knowledgePoint || index}`,
      order: node.nodeOrder || index + 1,
      label: labels[index] || '拓展',
      title: node.knowledgePoint || `课程模块 ${index + 1}`,
      minutes: node.estimatedMinutes || matchedResource?.estimatedMinutes || 20,
      resourceTitle: cleanDisplayText(matchedResource?.title) || '等待资源匹配',
      resourceType: formatResourceType(matchedResource?.resourceTypeName, matchedResource?.resourceType),
      status: node.status || (matchedResource ? 'READY' : 'WAITING'),
    }
  }),
)

const todayQueue = computed(() =>
  [
    {
      title: '继续学习路径',
      desc: pathNodes.value[0]?.knowledgePoint || '进入 AI 助教完成今日学习',
      to: '/learning',
      icon: Route,
      status: 'READY',
    },
    {
      title: '生成缺口资源',
      desc: focusTopic.value || '基于画像生成讲解、题库和导图',
      to: '/learning',
      tab: 'generate' as const,
      icon: Sparkles,
      status: resources.value.length ? 'READY' : 'WAITING',
    },
    {
      title: '记录学习反馈',
      desc: activeProfile.value ? '完成资源后记录行为和测评' : '先创建我的学习画像',
      to: activeProfile.value ? '/learning' : '/profiles',
      icon: LineChart,
      status: events.value.length ? 'READY' : 'PENDING',
    },
  ],
)

const learningEvidenceFlow = computed(() => [
  {
    label: '画像',
    title: activeProfile.value ? '我的画像已建立' : '等待我的画像',
    detail: activeProfile.value ? studentFacingText(activeProfile.value.learningGoal) || activeProfile.value.major : '对话生成画像后进入个性推荐',
    status: activeProfile.value ? 'READY' : 'WAITING',
  },
  {
    label: '课程',
    title: activeCourse.value?.title || '等待课程',
    detail: courseModules.value.length ? `${courseModules.value.length} 个模块` : '选择课程后生成结构',
    status: activeCourse.value ? 'READY' : 'WAITING',
  },
  {
    label: '资源',
    title: `${resources.value.length} 个资源`,
    detail: resourceShelf.value[0]?.title || '生成后进入课程书架',
    status: resources.value.length ? 'READY' : 'WAITING',
  },
  {
    label: '评估',
    title: latestReport.value ? '报告已生成' : '等待评估',
    detail: latestReportSummary.value || '测评后形成学习效果评估',
    status: latestReport.value ? 'READY' : 'PENDING',
  },
])

const learningSignals = computed(() => [
  {
    label: '个人薄弱点',
    value: focusTopic.value,
    detail: '建议先看图解讲解，再完成短测和实操任务。',
    tone: 'warn' as const,
  },
  {
    label: '学习行为反馈',
    value: events.value.length ? `${events.value.length} 条学习记录` : '待补充学习记录',
    detail: studyMinutes.value ? `已累计 ${Math.round(studyMinutes.value / 60)} 分钟学习行为。` : '完成资源浏览、测评或答疑后会自动沉淀。',
    tone: events.value.length ? 'ok' as const : 'muted' as const,
  },
    {
      label: '待补任务',
      value: `${weakSignalCount.value} 项需关注`,
      detail: '结合掌握度、测评结果和资源反馈生成学习建议。',
      tone: weakSignalCount.value ? 'warn' as const : 'ok' as const,
    },
  ])




function inferCourseSource(course: Course, _index: number): Pick<PortalCourseCard, 'source' | 'sourceKey'> {
  const titleAndDepartment = `${course.title} ${course.department}`
  const isSelfBuilt =
    titleAndDepartment.includes('自建') ||
    titleAndDepartment.includes('自定义') ||
    titleAndDepartment.includes('个人课程') ||
    course.title.includes('AI 个性化学习智能体实践')
  if (isSelfBuilt) return { source: '我的自建', sourceKey: 'self' }
  return { source: '班级发放', sourceKey: 'class' }
}

function progressForCourse(course: Course, index: number) {
  const matchedTask = tasks.value.find((task) => task.courseId === course.id)
  if (matchedTask?.progressPercent) return Math.max(18, Math.min(96, matchedTask.progressPercent))
  const title = course.title
  if (title.includes('Java') || title.includes('Web')) return 72
  if (title.includes('智能') || title.includes('AI')) return 61
  if (title.includes('工程') || title.includes('项目')) return 54
  if (title.includes('通识') || title.includes('基础') || title.includes('数字')) return 38
  return [66, 58, 45, 34][index % 4]
}

function nextTaskForCourse(course: Pick<Course, 'title' | 'department' | 'description'>) {
  const text = `${course.title} ${course.department} ${course.description}`
  if (text.includes('Java') || text.includes('Web') || text.includes('接口')) return 'REST API 分层短测'
  if (text.includes('智能') || text.includes('AI') || text.includes('Agent')) return '多智能体任务编排复盘'
  if (text.includes('工程') || text.includes('项目')) return '核心概念关系梳理'
  if (text.includes('通识') || text.includes('基础') || text.includes('数字')) return '数字素养情境练习'
  return courseTopicHint(course as Course)
}

function signalForCourse(course: Pick<Course, 'title' | 'department' | 'description'>, source: PortalCourseCard['source']) {
  if (source === '我的自建') return '由我的资料生成课程，AI 会继续补全章节、练习和资源。'
  const text = `${course.title} ${course.department} ${course.description}`
  if (text.includes('Java') || text.includes('Web')) return '班级资源已同步，建议先完成章节短测再进入答疑。'
  if (text.includes('工程') || text.includes('项目')) return '按老师发布的项目节奏推进，优先补齐任务背景。'
  return '来自班级发放课程，学习记录会回流到我的画像。'
}

const portalCourseCards = computed<PortalCourseCard[]>(() => {
  // 仅使用真实后端课程，无课程时显示空状态，不再用本地写死课程补位
  return courses.value.map((course, index) => {
    const source = inferCourseSource(course, index)
    return {
      id: course.id,
      title: course.title,
      department: course.department,
      creditHours: course.creditHours,
      source: source.source,
      sourceKey: source.sourceKey,
      progress: progressForCourse(course, index),
      nextTask: nextTaskForCourse(course),
      signal: signalForCourse(course, source.source),
      active: course.id === activeCourseId.value,
    }
  }).slice(0, 6)
})

const classCourseCount = computed(() => portalCourseCards.value.filter((course) => course.sourceKey === 'class').length)
const selfCourseCount = computed(() => portalCourseCards.value.filter((course) => course.sourceKey === 'self').length)
const visiblePortalCourses = computed(() => {
  if (courseBoardMode.value === 'all') return portalCourseCards.value
  return portalCourseCards.value.filter((course) => course.sourceKey === courseBoardMode.value)
})

const courseBoardTabs = computed(() => [
  { key: 'all' as const, label: '全部课程', count: portalCourseCards.value.length },
  { key: 'class' as const, label: '班级发放', count: classCourseCount.value },
  { key: 'self' as const, label: '我的自建', count: selfCourseCount.value },
])

const todayStudyMinutes = computed(() => Math.max(21, Math.round(studyMinutes.value / 60) || 21))
const portalMetrics = computed(() => [
  { label: '待办任务', value: `${globalTodayTasks.value.length}`, detail: '按优先级排好', icon: CalendarCheck, prompt: '把今天待办按时间顺序排一下' },
  { label: '学习课程', value: `${portalCourseCards.value.length}`, detail: `${classCourseCount.value} 门班级课 · ${selfCourseCount.value} 门自建`, icon: Layers3, prompt: '帮我按课程来源整理今天学习入口' },
  { label: '薄弱点', value: `${weakSignalCount.value}`, detail: '等待 AI 解释和练习', icon: Target, prompt: '解释我今天最需要补的薄弱点' },
  { label: '今日学习', value: `${todayStudyMinutes.value} 分钟`, detail: '学习记录持续回流', icon: Clock3, prompt: '按 45 分钟重新安排今天学习' },
])

const globalTodayTasks = computed(() => {
  const javaCourse =
    portalCourseCards.value.find((course) => course.title.includes('Java') || course.title.includes('Web')) ||
    portalCourseCards.value[0]
  const digitalCourse =
    portalCourseCards.value.find((course) => course.title.includes('通识') || course.title.includes('基础') || course.title.includes('数字')) ||
    portalCourseCards.value[2] ||
    javaCourse
  const selfCourse = portalCourseCards.value.find((course) => course.sourceKey === 'self') || portalCourseCards.value[1] || javaCourse

  return [
    {
      title: javaCourse?.nextTask || '完成章节短测',
      course: javaCourse?.title || '我的课程',
      source: javaCourse?.source || '班级发放',
      desc: '老师发布的章节短测，进入课程任务作答并自动评分。',
      status: 'READY',
      to: '/courses',
      courseTab: 'tasks' as const,
      icon: CalendarCheck,
    },
    {
      title: digitalCourse?.nextTask || '情境练习',
      course: digitalCourse?.title || '通识训练',
      source: digitalCourse?.source || '班级发放',
      desc: '老师发布的练习任务，进入课程任务完成后自动更新掌握度。',
      status: 'READY',
      to: '/courses',
      courseTab: 'tasks' as const,
      icon: LineChart,
    },
    {
      title: '上传资料生成自建课程',
      course: selfCourse?.title || '我的自建课程',
      source: '我的自建',
      desc: '上传 PPT、教材或讲义，生成章节结构、练习和学习资源。',
      status: selfCourse ? 'READY' : 'WAITING',
      to: '/course-builder',
      icon: UploadCloud,
    },
  ]
})


const selectedBudget = ref(65)
const reflectionInput = ref('')
const reflectionLoading = ref(false)
const reflectionResult = ref<ReflectionResult | null>(null)
const reflectionError = ref('')
const plannerLoading = ref(false)
const planningWeights = ref<Record<PlanningWeightKey, number>>({
  deadline: 82,
  weakness: 68,
  course: 56,
})
const timeBudgetOptions = [30, 45, 65, 90]
const weeklyStudyBars = [28, 44, 58, 82, 45, 48, 38]
const weekdayLabels = ['\u4e00', '\u4e8c', '\u4e09', '\u56db', '\u4e94', '\u516d', '\u65e5']

const todayPlanSlots = computed(() => {
  const times = ['09:00', '14:30', '20:00']
  const minutes = [20, 15, Math.max(20, selectedBudget.value - 35)]
  return weightedTodayQueue.value.slice(0, 3).map((item, index) => ({
    ...item,
    time: times[index] || '20:30',
    minutes: minutes[index] || 20,
    action: index === 0 ? '\u5f00\u59cb' : index === 1 ? '\u52a0\u5165\u8ba1\u5212' : '\u665a\u95f4\u590d\u76d8',
  }))
})

const todayPriorityQueue = computed(() => {
  const base = globalTodayTasks.value.map((item, index) => ({
    ...item,
    priority: index + 1,
    reason: index === 0 ? '\u622a\u6b62\u65f6\u95f4\u548c\u638c\u63e1\u5ea6\u540c\u65f6\u63d0\u9192' : index === 1 ? '\u9002\u5408\u77ed\u65f6\u95f4\u8865\u5f31' : '\u4e0e\u81ea\u5efa\u8bfe\u7a0b\u8d44\u6599\u8fde\u7eed',
    minutes: index === 0 ? 20 : index === 1 ? 15 : 30,
  }))
  const extras = [
    {
      title: '\u8bb0\u5f55\u4eca\u65e5\u590d\u76d8',
      course: '\u8de8\u8bfe\u7a0b\u753b\u50cf',
      source: 'AI \u63a8\u8350',
      desc: '\u628a\u4eca\u5929\u7684\u9519\u56e0\u3001\u5361\u70b9\u548c\u5b8c\u6210\u60c5\u51b5\u5199\u56de\u5b66\u4e60\u753b\u50cf\u3002',
      status: 'PENDING',
      to: '/profiles',
      icon: LineChart,
      priority: 4,
      reason: '\u7528\u4e8e\u66f4\u65b0\u8de8\u8bfe\u7a0b\u753b\u50cf',
      minutes: 8,
    },
    {
      title: '\u9884\u7ea6\u4e0b\u4e00\u6b21\u7b54\u7591',
      course: activeCourse.value?.title || '\u6211\u7684\u8bfe\u7a0b',
      source: '\u5b66\u4e60\u884c\u4e3a',
      desc: '\u5982\u679c\u672c\u8282\u9519\u9898\u8d85\u8fc7 2 \u4e2a\uff0c\u5efa\u8bae\u76f4\u63a5\u5f00\u4e00\u4e2a\u8bfe\u7a0b AI \u5bf9\u8bdd\u3002',
      status: 'WAITING',
      to: '/learning',
      icon: MessageCircleQuestion,
      priority: 5,
      reason: '\u4f5c\u4e3a\u5907\u9009\u4efb\u52a1',
      minutes: 12,
    },
    {
      title: '\u9519\u9898\u590d\u76d8\uff08\u7b2c 2 \u7ae0\uff09',
      course: activeCourse.value?.title || '\u6211\u7684\u8bfe\u7a0b',
      source: 'AI \u63a8\u8350',
      desc: '\u56de\u6536\u8fd1\u671f\u77ed\u6d4b\u9519\u56e0\uff0c\u628a\u91cd\u590d\u9519\u8bef\u5199\u56de\u5b66\u4e60\u753b\u50cf\u3002',
      status: 'WAITING',
      to: '/profiles',
      icon: CheckCircle2,
      priority: 6,
      reason: '\u7a0d\u540e\u590d\u76d8',
      minutes: 10,
    },
  ]
  return [...base, ...extras]
})

const todayTargetTotal = computed(() => 4)
const todayActionDoneCount = computed(
  () => Object.values(dashboardTaskStates.value).filter((state) => state === 'active' || state === 'planned').length,
)
const todayPendingTaskCount = computed(() => Math.min(4, todayPriorityQueue.value.length))
const todayTargetDone = computed(() => Math.min(todayTargetTotal.value, Math.max(2, todayActionDoneCount.value)))
const todayTargetPercent = computed(() => Math.round((todayTargetDone.value / todayTargetTotal.value) * 100))

const planningFactors = computed(() => [
  {
    key: 'deadline' as const,
    label: '\u622a\u6b62\u65f6\u95f4',
    value: planningWeights.value.deadline,
    desc: '\u8001\u5e08\u53d1\u5e03\u548c\u5f85\u63d0\u4ea4\u4efb\u52a1\u4f18\u5148',
  },
  {
    key: 'weakness' as const,
    label: '\u8584\u5f31\u77e5\u8bc6',
    value: planningWeights.value.weakness,
    desc: weakMasteryTopic.value || '\u6839\u636e\u6d4b\u8bc4\u548c\u5bf9\u8bdd\u5b9a\u4f4d\u5361\u70b9',
  },
  {
    key: 'course' as const,
    label: '\u8bfe\u7a0b\u6743\u91cd',
    value: planningWeights.value.course,
    desc: '\u73ed\u7ea7\u8bfe\u7a0b\u4f18\u5148\uff0c\u81ea\u5efa\u8bfe\u7a0b\u8865\u8d44\u6599\u7f3a\u53e3',
  },
])

const todayStateCards = computed(() => [
  {
    label: '\u5269\u4f59\u53ef\u7528\u65f6\u95f4',
    value: String(selectedBudget.value),
    suffix: '\u5206\u949f',
    detail: '\u5efa\u8bae\u4e13\u6ce8\u65f6\u6bb5\uff1a2 \u6bb5',
    icon: Clock3,
    prompt: '\u6309\u6211\u5269\u4f59\u65f6\u95f4\u91cd\u65b0\u5b89\u6392\u4eca\u65e5\u8ba1\u5212',
  },
  {
    label: '\u5f85\u5904\u7406\u4efb\u52a1',
    value: String(todayPendingTaskCount.value),
    suffix: '\u9879',
    detail: '\u542b 2 \u9879\u622a\u6b62\u4eca\u5929',
    icon: Layers3,
    prompt: '\u628a\u4eca\u5929\u5f85\u5904\u7406\u4efb\u52a1\u91cd\u65b0\u6392\u5e8f',
  },
  {
    label: '\u8fde\u7eed\u5b66\u4e60',
    value: '6',
    suffix: '\u5929',
    detail: '\u8f83\u4e0a\u6b21 +1 \u5929',
    icon: CalendarCheck,
    prompt: '\u5e2e\u6211\u4fdd\u6301\u8fde\u7eed\u5b66\u4e60\u8282\u594f',
  },
  {
    label: '\u753b\u50cf\u63d0\u9192',
    value: String(Math.max(weakSignalCount.value, 1)),
    suffix: '\u6761',
    detail: '\u5f85\u67e5\u770b',
    icon: BrainCircuit,
    prompt: '\u89e3\u91ca\u4eca\u5929\u753b\u50cf\u63d0\u9192\u7684\u91cd\u70b9',
  },
])

const plannedPreviewCount = computed(() => {
  if (selectedBudget.value <= 30) return 2
  if (selectedBudget.value <= 45) return 3
  if (selectedBudget.value <= 65) return 4
  return 5
})
function taskWeightScore(item: TodayTaskActionItem, index: number) {
  const queueSize = Math.max(todayPriorityQueue.value.length, 1)
  const deadlineRank = ((queueSize - index) / queueSize) * 100
  const text = `${item.title}${item.desc}${item.source}${item.course}`
  const deadlineSignal = /截止|提交|老师|班级|短测/.test(text) ? 100 : deadlineRank
  const weaknessSignal = /薄弱|错题|测评|复盘|练习|卡点|答疑/.test(text) ? 100 : /画像|资源/.test(text) ? 62 : 25
  const courseSignal = /班级|老师|Java Web/.test(text) ? 100 : /自建|上传|资料/.test(text) ? 70 : 45
  const budgetWindow = Math.max(8, selectedBudget.value / Math.max(plannedPreviewCount.value, 1))
  const itemMinutes = Number(item.minutes || 0)
  const fitScore = itemMinutes <= budgetWindow + 4 ? 18 : itemMinutes <= budgetWindow + 12 ? 8 : -12
  return (
    deadlineSignal * (planningWeights.value.deadline / 100) +
    weaknessSignal * (planningWeights.value.weakness / 100) +
    courseSignal * (planningWeights.value.course / 100) +
    fitScore
  )
}

const weightedTodayQueue = computed(() =>
  todayPriorityQueue.value
    .map((item, index) => ({ item, index, score: taskWeightScore(item, index) }))
    .sort((a, b) => b.score - a.score || a.index - b.index)
    .map(({ item }, index) => ({ ...item, priority: index + 1 })),
)
const reorderedPreview = computed(() => weightedTodayQueue.value.slice(0, plannedPreviewCount.value))
const quickCourseEntries = computed(() => portalCourseCards.value.slice(0, 3))
const deferredTaskCount = computed(() => Math.max(todayPriorityQueue.value.length - plannedPreviewCount.value, 0))
const reflectionQuickPrompts = computed(() => [
  {
    label: `${selectedBudget.value} 分钟重排`,
    prompt: `我今天只剩 ${selectedBudget.value} 分钟，请根据当前任务帮我重新排一下先后顺序。`,
  },
  {
    label: '复盘薄弱点',
    prompt: `我今天在「${weakMasteryTopic.value || focusTopic.value || '当前知识点'}」这里卡住了，请帮我拆成下一步练习。`,
  },
  {
    label: '晚间收尾',
    prompt: '我想做一个晚间复盘，请告诉我应该记录哪些错因和学习证据。',
  },
])
const canSubmitReflection = computed(() => Boolean(reflectionInput.value.trim()) && !reflectionLoading.value)

function dashboardEventCourseId(courseId?: string) {
  return courseId || activeCourse.value?.id || app.activeCourseId || courses.value[0]?.id || ''
}

async function recordDashboardEvent(
  eventType: string,
  payload: Record<string, unknown>,
  options: { courseId?: string; durationSeconds?: number; feedbackScore?: number; resourceId?: string | null } = {},
) {
  const studentProfileId = activeProfile.value?.id
  const courseId = dashboardEventCourseId(options.courseId)
  if (!studentProfileId || !courseId) return false
  try {
    await learningApi.recordEvent({
      studentProfileId,
      courseId,
      resourceId: options.resourceId ?? resources.value[0]?.id ?? null,
      eventType,
      durationSeconds: Math.max(0, Number(options.durationSeconds || 0)),
      feedbackScore: options.feedbackScore,
      eventPayload: JSON.stringify({
        source: 'student-dashboard',
        ...payload,
      }),
    })
    await loadLearningContext(studentProfileId, courseId)
    return true
  } catch (err) {
    dashboardFeedback.value = err instanceof Error ? err.message : '学习行为写入失败，请稍后刷新重试。'
    return false
  }
}

async function updateBudget(minutes: number) {
  selectedBudget.value = minutes
  dashboardFeedback.value = `已切换为 ${minutes} 分钟预算，右侧 AI 重排预览已按可用时间收缩。`
  await recordDashboardEvent(
    'TODAY_BUDGET_UPDATED',
    {
      budgetMinutes: minutes,
      previewCount: plannedPreviewCount.value,
      action: 'update-budget',
    },
    { durationSeconds: minutes * 60 },
  )
}

function setPlanningWeight(key: PlanningWeightKey, value: number | string) {
  planningWeights.value = {
    ...planningWeights.value,
    [key]: Math.max(0, Math.min(100, Number(value) || 0)),
  }
}

function readInputValue(event: Event) {
  return event.target instanceof HTMLInputElement ? event.target.value : 0
}

async function updatePlanningWeight(key: PlanningWeightKey, value: number | string) {
  const nextValue = Math.max(0, Math.min(100, Number(value) || 0))
  setPlanningWeight(key, nextValue)
  const factor = planningFactors.value.find((item) => item.key === key)
  dashboardFeedback.value = `已把「${factor?.label || '排序权重'}」调整为 ${nextValue}%，AI 重排预览已更新。`
  await recordDashboardEvent(
    'TODAY_PLANNING_WEIGHT_CHANGED',
    {
      weightKey: key,
      weightLabel: factor?.label || key,
      weightValue: nextValue,
      weights: planningWeights.value,
      action: 'change-planning-weight',
    },
    { feedbackScore: Math.round(nextValue / 20) },
  )
}

function taskActionKey(item: TodayTaskActionItem) {
  return `${item.priority || 0}:${item.course || 'global'}:${item.title}`
}

function taskActionState(item: TodayTaskActionItem) {
  return dashboardTaskStates.value[taskActionKey(item)] || ''
}

function setTaskActionState(item: TodayTaskActionItem, state: DashboardTaskState) {
  dashboardTaskStates.value = {
    ...dashboardTaskStates.value,
    [taskActionKey(item)]: state,
  }
}

function taskStateClass(item: TodayTaskActionItem) {
  const state = taskActionState(item)
  return {
    'is-active-task': state === 'active',
    'is-planned-task': state === 'planned',
    'is-deferred-task': state === 'deferred',
  }
}

function taskStatusLabel(item: TodayTaskActionItem) {
  const state = taskActionState(item)
  if (state === 'active') return '进行中'
  if (state === 'planned') return '已加入'
  if (state === 'deferred') return '稍后'
  return statusLabel(item.status)
}

function taskStatusTone(item: TodayTaskActionItem) {
  const state = taskActionState(item)
  if (state === 'active' || state === 'planned') return 'ok'
  if (state === 'deferred') return 'warn'
  return statusTone(item.status)
}

function isReflectionRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value && typeof value === 'object' && !Array.isArray(value))
}

function parseReflectionJson<T>(value: string, fallback: T): T {
  try {
    return JSON.parse(value) as T
  } catch {
    return fallback
  }
}

function asReflectionStringArray(value: unknown): string[] {
  const parsed = typeof value === 'string' ? parseReflectionJson<unknown>(value, value) : value
  if (Array.isArray(parsed)) {
    return parsed
      .map((item) => {
        if (typeof item === 'string') return item
        if (isReflectionRecord(item)) {
          return String(item.title || item.text || item.label || item.action || item.name || JSON.stringify(item))
        }
        return String(item)
      })
      .map((item) => cleanDisplayText(item))
      .filter(Boolean)
  }
  if (typeof parsed === 'string' && parsed.trim()) {
    return parsed
      .split(/\n|；|;/)
      .map((item) => cleanDisplayText(item))
      .filter(Boolean)
  }
  return []
}

function pickReflectionText(value: Record<string, unknown>, fallback: string) {
  const text = String(value.answer || value.content || value.summary || value.message || value.result || '').trim()
  return cleanDisplayText(text || fallback)
}

function buildReflectionContext() {
  const queueLines = weightedTodayQueue.value
    .slice(0, 6)
    .map((item) => `${item.priority}. ${item.title}｜${item.course || '跨课程'}｜${item.minutes || 0} 分钟｜${item.status || 'READY'}`)
  const masteryLines = mastery.value
    .slice()
    .sort((a, b) => Number(a.masteryScore || 0) - Number(b.masteryScore || 0))
    .slice(0, 4)
    .map((item) => `${item.knowledgePoint}: ${Math.round(Number(item.masteryScore || 0) * 100)}%`)

  return [
    `当前课程：${activeCourse.value?.title || '未选择课程'}`,
    `学生画像：${activeProfile.value?.studentName || app.currentUser.name}`,
    `今日可用时间：${selectedBudget.value} 分钟`,
    `当前聚焦：${focusTopic.value || '未定位'}`,
    `薄弱点：${weakMasteryTopic.value || '暂无明确薄弱点'}`,
    `任务队列：\n${queueLines.join('\n') || '暂无任务队列'}`,
    `掌握度证据：\n${masteryLines.join('\n') || '暂无掌握度证据'}`,
    `最近学习记录：${events.value.length} 条`,
  ]
}

function buildReflectionPrompt(note: string) {
  return [
    '你是学习规划助教。请基于学生今日复盘、画像、任务队列和时间预算，输出可执行的下一步安排。',
    '要求：回答简洁；先处理最该做的任务；给出 2-4 个具体行动；如果时间不足，明确哪些任务延后。',
    '',
    `学生输入：${note}`,
    '',
    buildReflectionContext().join('\n'),
  ].join('\n')
}

function buildFallbackReflection(note: string): ReflectionResult {
  const first = weightedTodayQueue.value[0]
  const second = weightedTodayQueue.value[1]
  const third = weightedTodayQueue.value[2]
  const minutes = selectedBudget.value
  const core = first?.title || focusTopic.value || '当前最重要任务'
  const support = second?.title || weakMasteryTopic.value || '薄弱点练习'
  const final = third?.title || '学习反馈记录'
  const answer = note.includes('30') || minutes <= 30
    ? `先把今天压缩成两段：前 ${Math.min(18, Math.max(12, minutes - 10))} 分钟处理「${core}」，最后 8-10 分钟记录错因和卡点。其余任务先进入稍后队列，避免把复盘时间挤没。`
    : `建议保留三段节奏：先完成「${core}」，再用一小段时间处理「${support}」，最后把「${final}」沉淀为学习画像证据。不要把所有任务平均分配，今天优先保证前两项闭环。`
  return {
    status: 'fallback',
    source: '离线建议',
    answer,
    actions: [
      `先做「${core}」，限定 ${Math.min(20, Math.max(12, Math.round(minutes * 0.45)))} 分钟。`,
      `再处理「${support}」，只保留一个最小练习或一个错因。`,
      `收尾记录 1 条卡点、1 条错因、1 个明天继续的问题。`,
    ],
    signals: [weakMasteryTopic.value || focusTopic.value || '今日复盘', `${minutes} 分钟预算`].filter(Boolean),
    citations: [],
  }
}

function withReflectionTimeout<T>(promise: Promise<T>, ms = 12000): Promise<T> {
  let timer: ReturnType<typeof setTimeout>
  return Promise.race([
    promise,
    new Promise<never>((_, reject) => {
      timer = setTimeout(() => reject(new Error('AI 响应超过 12 秒，已先给出可执行建议。')), ms)
    }),
  ]).finally(() => clearTimeout(timer))
}

function applyReflectionPrompt(prompt: string) {
  reflectionInput.value = prompt
  reflectionError.value = ''
}

function appendPlannerExchange(text: string, answer: string, title = '规划助手') {
  const stamp = Date.now()
  plannerHistory.value = [
    ...plannerHistory.value,
    { id: `user-${stamp}`, role: 'user' as const, body: text },
    { id: `assistant-${stamp}`, role: 'assistant' as const, title, body: answer },
  ].slice(-7)
}

async function applyReflectionPlan() {
  if (!reflectionResult.value) return
  const nextStates: Record<string, DashboardTaskState> = { ...dashboardTaskStates.value }
  weightedTodayQueue.value.forEach((item, index) => {
    nextStates[taskActionKey(item)] = index < plannedPreviewCount.value ? 'planned' : 'deferred'
  })
  dashboardTaskStates.value = nextStates
  dashboardFeedback.value = '已按复盘建议更新今日计划，前置任务已保留到当前队列。'
  await recordDashboardEvent(
    'TODAY_REFLECTION_APPLIED',
    {
      source: reflectionResult.value.source,
      answer: reflectionResult.value.answer,
      actions: reflectionResult.value.actions,
      action: 'apply-reflection-plan',
    },
    { durationSeconds: selectedBudget.value * 60, feedbackScore: 5 },
  )
}

function dismissReflectionResult() {
  reflectionResult.value = null
  reflectionError.value = ''
}

function findBackendCourseForTask(item: TodayTaskActionItem) {
  const taskCourse = cleanDisplayText(item.course || '')
  if (!taskCourse) return null
  return (
    courses.value.find((course) => course.title === taskCourse) ||
    courses.value.find((course) => taskCourse.includes(course.title) || course.title.includes(taskCourse)) ||
    null
  )
}

function activateCourseForTask(item: TodayTaskActionItem) {
  const matchedCourse = findBackendCourseForTask(item)
  if (matchedCourse?.id) app.setActiveCourse(matchedCourse.id)
  return matchedCourse
}

async function openTaskTarget(item: TodayTaskActionItem, fallback = '/learning') {
  const course = activateCourseForTask(item)
  const target = item.to || fallback
  // 老师发布的作业/测试：进入对应课程的「课程任务」tab 去完成，而不是跳 AI 助手
  if (item.courseTab && course?.id) {
    await router.push({ path: `/courses/${course.id}`, query: { tab: item.courseTab } })
    return
  }
  if (target === '/courses' && course?.id) {
    await router.push(`/courses/${course.id}`)
    return
  }
  await router.push({
    path: target,
    query: target === '/learning' ? { task: item.title, tab: item.tab || 'chat', courseId: course?.id || app.activeCourseId || undefined } : undefined,
  })
}

async function startTask(item: TodayTaskActionItem) {
  const course = activateCourseForTask(item)
  setTaskActionState(item, 'active')
  await recordDashboardEvent(
    'TODAY_TASK_STARTED',
    {
      title: item.title,
      course: item.course,
      source: item.source,
      priority: item.priority,
      action: 'start',
    },
    { courseId: course?.id, durationSeconds: Number(item.minutes || 0) * 60 },
  )
  dashboardFeedback.value = `已开始「${item.title}」${course ? `，当前课程已切换到「${course.title}」` : ''}。`
  askPlanner(`我准备开始「${item.title}」，请给我可执行步骤`)
  await openTaskTarget(item, '/learning')
}

async function addTaskToPlan(item: TodayTaskActionItem) {
  const course = activateCourseForTask(item)
  setTaskActionState(item, 'planned')
  await recordDashboardEvent(
    'TODAY_TASK_PLANNED',
    {
      title: item.title,
      course: item.course,
      source: item.source,
      priority: item.priority,
      action: 'plan',
    },
    { courseId: course?.id, durationSeconds: Number(item.minutes || 0) * 60 },
  )
  dashboardFeedback.value = `已把「${item.title}」加入今日计划${course ? `，关联课程为「${course.title}」` : ''}。`
  askPlanner(`把「${item.title}」加入今天规划，并告诉我先后顺序`)
}

async function deferTask(item: TodayTaskActionItem) {
  const course = activateCourseForTask(item)
  setTaskActionState(item, 'deferred')
  await recordDashboardEvent(
    'TODAY_TASK_DEFERRED',
    {
      title: item.title,
      course: item.course,
      source: item.source,
      priority: item.priority,
      action: 'defer',
    },
    { courseId: course?.id },
  )
  dashboardFeedback.value = `已把「${item.title}」移到稍后队列，今日优先级会让给前置任务。`
  askPlanner(`把「${item.title}」暂时放到稍后，给我调整后的今日顺序`)
}

async function scheduleReflection(item: TodayTaskActionItem) {
  const course = activateCourseForTask(item)
  setTaskActionState(item, 'planned')
  await recordDashboardEvent(
    'TODAY_REFLECTION_SCHEDULED',
    {
      title: item.title,
      course: item.course,
      source: item.source,
      priority: item.priority,
      action: 'schedule-reflection',
    },
    { courseId: course?.id },
  )
  reflectionInput.value = `复盘：${item.title}`
  dashboardFeedback.value = `已安排「${item.title}」作为晚间复盘，底部复盘框已带入标题。`
  askPlanner(`把「${item.title}」安排到晚间复盘，并说明复盘要记录什么`)
}

function runTimelineAction(item: TodayTaskActionItem) {
  if (item.action === '开始') {
    void startTask(item)
    return
  }
  if (item.action === '晚间复盘') {
    void scheduleReflection(item)
    return
  }
  void addTaskToPlan(item)
}

async function submitReflection() {
  const text = reflectionInput.value.trim()
  if (!text || reflectionLoading.value) return
  reflectionLoading.value = true
  reflectionError.value = ''
  reflectionResult.value = null
  dashboardFeedback.value = '正在调用 AI 结合画像与任务队列生成复盘建议。'
  await recordDashboardEvent(
    'TODAY_REFLECTION_SUBMITTED',
    {
      note: text,
      course: activeCourse.value?.title || '',
      action: 'submit-reflection',
    },
    { durationSeconds: 5 * 60, feedbackScore: 4 },
  )
  try {
    const studentProfileId = activeProfile.value?.id
    const courseId = dashboardEventCourseId()
    if (!studentProfileId || !courseId) {
      throw new Error('缺少学生画像或课程上下文。')
    }
    const aiResult = await learningApi.tutoring({
      studentProfileId,
      courseId,
      question: text,
      conversationHistory: buildReflectionContext(),
      modality: '今日复盘与任务重排',
      documentTexts: [buildReflectionPrompt(text)],
    })
    if (Boolean(aiResult.fallbackUsed)) {
      throw new Error('AI 复盘返回了降级结果，本次不采用。')
    }
    const answer = pickReflectionText(aiResult, '')
    if (!answer) {
      throw new Error('AI 复盘没有返回可用建议。')
    }
    const actions = asReflectionStringArray(aiResult.learningActions || aiResult.actions || aiResult.nextActions)
    const signals = asReflectionStringArray(aiResult.profileSignals || aiResult.signals)
    const citations = asReflectionStringArray(aiResult.citations || aiResult.references)
    reflectionResult.value = {
      status: 'ai',
      source: 'AI 已返回',
      answer,
      actions: actions.slice(0, 4),
      signals: signals.slice(0, 3),
      citations: citations.slice(0, 3),
    }
    appendPlannerExchange(text, answer, '今日复盘')
    reflectionInput.value = ''
    dashboardFeedback.value = 'AI 已生成复盘建议，可在下方查看并采纳到今日计划。'
  } catch (err) {
    reflectionResult.value = null
    reflectionError.value = err instanceof Error ? err.message : 'AI 复盘失败，请稍后重试。'
    dashboardFeedback.value = 'AI 复盘失败，本次没有生成本地替代建议。'
  } finally {
    reflectionLoading.value = false
  }
}

const portalAgentSteps = computed(() => [
  { label: '课程汇总', status: portalCourseCards.value.length ? 'READY' : 'WAITING' },
  { label: '画像匹配', status: activeProfile.value ? 'READY' : 'WAITING' },
  { label: '任务排序', status: globalTodayTasks.value.length ? 'READY' : 'PENDING' },
  { label: '资源生成', status: resources.value.length || tasks.value.length ? 'READY' : 'WAITING' },
])

const agentQuickActions = computed(() => [
  { title: '安排今天学习', desc: '把所有课程待办排成可执行顺序', prompt: '请给我一份今天学习安排', icon: CalendarCheck },
  { title: '解释薄弱点', desc: weakMasteryTopic.value || '结合测评和画像定位卡点', prompt: '解释我当前薄弱点并给练习顺序', icon: BrainCircuit },
  { title: '生成练习', desc: '按当前薄弱点生成短测与讲解', prompt: '围绕薄弱点给我三道练习题', icon: Sparkles },
  { title: '整理课程资源', desc: '把班级资料和自建资料归档到课程空间', prompt: '帮我整理课程资源和下一步入口', icon: LibraryBig },
])

const defaultPlannerMessage = computed<PlannerMessage>(() => ({
  id: 'default-plan',
  role: 'assistant',
  title: '等待 AI 规划',
  body: '点击重新规划或发送问题后，会调用后端 AI 接口结合画像、课程和任务队列生成今日安排。',
  chips: ['重新规划', '解释薄弱点', '整理课程'],
}))

const plannerMessages = computed(() => [defaultPlannerMessage.value, ...plannerHistory.value])

function plannerAnswerFromAgent(response: Record<string, unknown>) {
  const summary = cleanDisplayText(response.summary)
  const title = cleanDisplayText(response.planTitle || response.title)
  const stages = Array.isArray(response.stages) ? response.stages : []
  const stageLines = stages
    .slice(0, 3)
    .map((item, index) => {
      if (!item || typeof item !== 'object') return ''
      const record = item as Record<string, unknown>
      const stageTitle = cleanDisplayText(record.title || `阶段 ${index + 1}`)
      const objective = cleanDisplayText(record.objective)
      const minutes = Number(record.estimatedMinutes || 0)
      return `${index + 1}. ${stageTitle}${minutes ? `（${minutes} 分钟）` : ''}${objective ? `：${objective}` : ''}`
    })
    .filter(Boolean)
  const resources = Array.isArray(response.resourceRecommendations) ? response.resourceRecommendations : []
  const resourceLines = resources
    .slice(0, 2)
    .map((item) => {
      if (!item || typeof item !== 'object') return ''
      const record = item as Record<string, unknown>
      const resourceTitle = cleanDisplayText(record.title || record.resourceType)
      const reason = cleanDisplayText(record.reason)
      return resourceTitle ? `资源：${resourceTitle}${reason ? `，${reason}` : ''}` : ''
    })
    .filter(Boolean)
  return [title || summary || 'AI 已生成今日规划。', ...stageLines, ...resourceLines].join('\n')
}

async function askPlanner(prompt?: string) {
  const text = (prompt || plannerInput.value).trim()
  if (!text || plannerLoading.value) return
  const studentProfileId = activeProfile.value?.id
  const courseId = dashboardEventCourseId()
  if (!studentProfileId || !courseId) {
    dashboardFeedback.value = '缺少学生画像或课程上下文，无法调用 AI 规划。'
    return
  }
  plannerLoading.value = true
  dashboardFeedback.value = '正在调用 AI 规划今日任务。'
  try {
    const response = await agentsApi.invoke('/learning/path-plans', {
      studentProfileId,
      courseId,
      topic: text,
      goal: text,
      dailyMinutes: selectedBudget.value,
      timeframeDays: 1,
      weaknessSignals: [weakMasteryTopic.value, focusTopic.value].filter(Boolean),
      recentScores: mastery.value.slice(0, 6).map((item) => Math.round(Number(item.masteryScore) || 0)),
      completedResources: resources.value.slice(0, 6).map((item) => item.title),
      documentTexts: buildReflectionContext(),
    })
    if (Boolean(response.fallbackUsed)) {
      throw new Error('AI 规划返回了降级结果，本次不采用。')
    }
    appendPlannerExchange(text, plannerAnswerFromAgent(response), 'AI 今日规划')
    plannerInput.value = ''
    dashboardFeedback.value = `AI 已返回今日规划${response.artifactId ? `，产物 ${response.artifactId}` : ''}。`
  } catch (err) {
    dashboardFeedback.value = err instanceof Error ? err.message : 'AI 规划失败，本次没有生成本地替代建议。'
  } finally {
    plannerLoading.value = false
  }
}

function selectTaskForPlanner(title: string) {
  askPlanner(`把「${title}」加入今天规划，并告诉我先后顺序`)
}

function priorityActionLabel(item: TodayTaskActionItem) {
  const state = taskActionState(item)
  if (state === 'active') return '继续'
  if (state === 'planned') return '开始'
  if (state === 'deferred') return '恢复'
  const priority = item.priority || 0
  if (priority === 1) return '开始'
  if (priority <= 3) return '加入计划'
  return '稍后'
}

function timelineActionLabel(item: TodayTaskActionItem) {
  const state = taskActionState(item)
  if (state === 'active') return '继续'
  if (state === 'planned') return item.action === '晚间复盘' ? '已安排' : '已加入'
  if (state === 'deferred') return '已稍后'
  return item.action || '处理'
}

function runPriorityAction(item: TodayTaskActionItem) {
  const state = taskActionState(item)
  if (state === 'active' || state === 'planned' || state === 'deferred' || item.priority === 1) {
    void startTask(item)
    return
  }
  if ((item.priority || 0) <= 3) {
    addTaskToPlan(item)
    return
  }
  deferTask(item)
}

async function openPriorityTask(item: TodayTaskActionItem) {
  setTaskActionState(item, 'active')
  dashboardFeedback.value = `正在打开「${item.title}」的工作空间。`
  await openTaskTarget(item, item.to || '/learning')
}

async function replanToday() {
  const nextStates: Record<string, DashboardTaskState> = {}
  weightedTodayQueue.value.forEach((item, index) => {
    nextStates[taskActionKey(item)] = index < plannedPreviewCount.value ? 'planned' : 'deferred'
  })
  dashboardTaskStates.value = nextStates
  dashboardFeedback.value = `已按 ${selectedBudget.value} 分钟预算重排，前 ${plannedPreviewCount.value} 项进入今日计划。`
  await recordDashboardEvent(
    'TODAY_REPLANNED',
    {
      budgetMinutes: selectedBudget.value,
      plannedCount: plannedPreviewCount.value,
      weights: planningWeights.value,
      tasks: weightedTodayQueue.value.map((item) => ({ title: item.title, course: item.course, priority: item.priority })),
      action: 'replan',
    },
    { durationSeconds: selectedBudget.value * 60 },
  )
  await askPlanner('按当前时间预算重新规划今日任务')
}

function selectPortalCourse(course: PortalCourseCard) {
  if (courses.value.some((item) => item.id === course.id)) app.setActiveCourse(course.id)
  askPlanner(`围绕「${course.title}」安排下一步学习`)
}

async function openQuickCourse(course: PortalCourseCard) {
  selectPortalCourse(course)
  dashboardFeedback.value = `已切换到「${course.title}」，正在进入我的课程。`
  await router.push(`/courses/${course.id}`)
}

const courseSourceActions = computed(() => [
  {
    title: '加入班级课程',
    desc: '输入班级码或由老师邀请后，课程会出现在我的课程中。',
    to: '/courses',
    icon: PlusCircle,
    tone: 'class',
  },
  {
    title: '上传资料生成课程',
    desc: '上传 PPT、教材、讲义或题库，AI 生成个人课程结构。',
    to: '/course-builder',
    icon: FileUp,
    tone: 'self',
  },
])

const recentLearningRecords = computed(() => [
  {
    title: '继续上次答疑',
    desc: focusTopic.value || '围绕当前薄弱点继续提问',
    meta: 'AI 助教',
    to: '/learning',
  },
  {
    title: '查看课程资料',
    desc: resourceShelf.value[0]?.title || '进入课程空间查看老师发放与自建资源',
    meta: '课程空间',
    to: '/courses',
  },
  {
    title: '更新学习画像',
    desc: latestReportSummary.value || '把测评、对话和学习行为沉淀为画像',
    meta: '学习画像',
    to: '/profiles',
  },
])

function statusTone(status?: string): 'ok' | 'warn' | 'danger' | 'info' | 'muted' {
  const value = String(status || '').toUpperCase()
  if (['SUCCEEDED', 'READY', 'ACTIVE', 'DONE', 'COMPLETED'].includes(value)) return 'ok'
  if (['PUBLISHED', 'READY_TO_PUBLISH'].includes(value)) return 'ok'
  if (['FAILED', 'BLOCKED'].includes(value)) return 'danger'
  if (['LOCKED', 'WAITING', 'PENDING'].includes(value)) return 'warn'
  if (['REVIEW_REQUIRED', 'REVIEWING'].includes(value)) return 'warn'
  return 'info'
}

function statusLabel(status?: string) {
  const value = String(status || '').toUpperCase()
  const labels: Record<string, string> = {
    SUCCEEDED: '已完成',
    COMPLETED: '已完成',
    DONE: '已完成',
    READY: '可学习',
    ACTIVE: '进行中',
    RUNNING: '生成中',
    PROCESSING: '处理中',
    PENDING: '等待中',
    WAITING: '等待中',
    LOCKED: '待解锁',
    PUBLISHED: '已发布',
    READY_TO_PUBLISH: '可发布',
    REVIEW_REQUIRED: '待复核',
    REVIEWING: '审核中',
    FAILED: '未完成',
    BLOCKED: '需处理',
  }
  return labels[value] || '进行中'
}

function taskStepLabel(value?: string) {
  const text = cleanDisplayText(String(value || ''))
  const lower = text.toLowerCase()
  if (!text) return '等待处理'
  if (lower.includes('profile') || text.includes('画像')) return '画像匹配'
  if (lower.includes('diagnos') || lower.includes('knowledge') || text.includes('诊断')) return '知识诊断'
  if (lower.includes('plan') || lower.includes('path') || text.includes('规划')) return '路径规划'
  if (lower.includes('audit') || lower.includes('review') || text.includes('审核')) return '内容审核'
  if (lower.includes('generate') || lower.includes('resource') || lower.includes('document') || lower.includes('quiz') || text.includes('生成')) return '资源生成'
  return text
}

async function loadLearningContext(profileId?: string, courseId?: string) {
  if (!profileId) {
    learningPaths.value = []
    recommendations.value = []
    mastery.value = []
    reports.value = []
    events.value = []
    return
  }
  const [pathResult, recommendationResult, eventResult, masteryResult, reportResult] = await Promise.allSettled([
    learningApi.paths(profileId),
    learningApi.recommendations(profileId),
    learningApi.events(profileId),
    courseId ? learningApi.mastery(profileId, courseId) : Promise.resolve([]),
    courseId ? learningApi.evaluationReports(profileId, courseId) : Promise.resolve([]),
  ])
  learningPaths.value = pathResult.status === 'fulfilled' ? (pathResult.value as LearningPathRecord[]) : []
  recommendations.value = recommendationResult.status === 'fulfilled' ? recommendationResult.value : []
  const loadedEvents = eventResult.status === 'fulfilled' ? eventResult.value : []
  events.value = loadedEvents.filter((item) => matchesCourseId(item, courseId))
  mastery.value = masteryResult.status === 'fulfilled' ? masteryResult.value : []
  reports.value = reportResult.status === 'fulfilled' ? reportResult.value : []
}

async function loadCourseScopedData(courseId?: string) {
  const targetCourseId = courseId || activeCourse.value?.id
  resources.value = targetCourseId ? await coursesApi.resources(targetCourseId, { publishedOnly: true }).catch(() => []) : []
  await loadLearningContext(activeProfile.value?.id, targetCourseId)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [healthResult, tasksResult, profilesResult, coursesResult] = await Promise.allSettled([
      healthApi.getHealth(),
      tasksApi.list(),
      profilesApi.list(),
      coursesApi.list(),
    ])
    health.value = healthResult.status === 'fulfilled' ? healthResult.value : null
    tasks.value = tasksResult.status === 'fulfilled' ? tasksResult.value : []
    profiles.value = profilesResult.status === 'fulfilled' ? profilesResult.value : []
    courses.value = coursesResult.status === 'fulfilled' ? coursesResult.value : []
    if (courses.value[0]?.id && !app.activeCourseId) app.setActiveCourse(courses.value[0].id)

    await loadCourseScopedData(activeCourse.value?.id)

    const failures = [healthResult, tasksResult, profilesResult, coursesResult].filter(
      (item) => item.status === 'rejected',
    ).length
    if (failures === 4) error.value = '学习数据加载失败，请稍后刷新。'
  } finally {
    loading.value = false
  }
}

onMounted(load)

watch(
  () => app.activeCourseId,
  (courseId, previousCourseId) => {
    if (!courseId || courseId === previousCourseId || !courses.value.some((course) => course.id === courseId)) return
    void loadCourseScopedData(courseId)
  },
)
</script>


<template>
  <div class="page-grid learning-home student-portal-home today-learning-workbench" :style="todayGridStyle">
    <ErrorNotice class="span-12" :message="error" />
    <LoadingBlock :show="loading" class="span-12" />

    <section class="today-hero span-12" aria-label="&#x4eca;&#x65e5;&#x5b66;&#x4e60;&#x8ba1;&#x5212;">
      <div class="today-plan-stage">
        <div class="today-plan-header">
          <div>
            <div class="today-plan-label-row">
              <span class="portal-eyebrow">&#x4eca;&#x65e5;&#x5b66;&#x4e60;&#x8ba1;&#x5212;</span>
              <span class="today-ai-chip">&#x70b9;&#x51fb;&#x91cd;&#x65b0;&#x89c4;&#x5212;&#x540e;&#x7531; AI &#x751f;&#x6210;</span>
            </div>
            <h2>今天建议投入 <em>{{ selectedBudget }}</em> 分钟</h2>
          </div>
          <div class="today-plan-visual" aria-hidden="true">
            <span class="plan-visual-calendar"></span>
            <span class="plan-visual-node primary"></span>
            <span class="plan-visual-node secondary"></span>
            <span class="plan-visual-node tertiary"></span>
          </div>
        </div>

        <div class="today-timeline" aria-label="&#x4eca;&#x65e5;&#x65f6;&#x95f4;&#x7ebf;">
          <span class="today-timeline-rail" aria-hidden="true"></span>
          <article v-for="slot in todayPlanSlots" :key="slot.title" class="today-timeblock" :class="taskStateClass(slot)">
            <div class="today-time-meta">
              <span class="today-time">{{ slot.time }}</span>
              <b>{{ slot.minutes }} &#x5206;&#x949f;</b>
            </div>
            <div>
              <strong>{{ slot.title }}</strong>
              <small>{{ slot.course }}</small>
            </div>
            <button type="button" data-testid="today-timeline-action" @click="runTimelineAction(slot)">{{ timelineActionLabel(slot) }}</button>
          </article>
        </div>

        <p v-if="dashboardFeedback" class="today-action-feedback" data-testid="dashboard-action-feedback">
          {{ dashboardFeedback }}
        </p>
      </div>

      <aside class="today-state-panel" aria-label="&#x4eca;&#x65e5;&#x72b6;&#x6001;">
        <div class="today-state-title">
          <div>
            <h2>&#x4eca;&#x65e5;&#x72b6;&#x6001;</h2>
          </div>
          <RouterLink to="/profiles">&#x67e5;&#x770b;&#x8be6;&#x60c5;</RouterLink>
        </div>

        <div class="today-state-cards">
          <button v-for="item in todayStateCards" :key="item.label" type="button" @click="askPlanner(item.prompt)">
            <component :is="item.icon" :size="20" :stroke-width="1.85" />
            <span>{{ item.label }}</span>
            <strong>{{ item.value }}<small>{{ item.suffix }}</small></strong>
            <em>{{ item.detail }}</em>
          </button>
        </div>

        <div class="today-state-analytics">
          <div class="today-weekly-chart">
            <div class="today-chart-head">
              <span>&#x4eca;&#x65e5;&#x5b66;&#x4e60;&#x65f6;&#x957f;&#xff08;&#x5206;&#x949f;&#xff09;</span>
              <strong>&#x672c;&#x5468; {{ weeklyStudyBars.reduce((sum, item) => sum + item, 0) }} &#x5206;&#x949f;</strong>
            </div>
            <div class="today-week-bars" aria-hidden="true">
              <i v-for="(value, index) in weeklyStudyBars" :key="weekdayLabels[index]" :style="{ height: value + '%' }">
                <em>{{ value }}</em>
                <b>{{ weekdayLabels[index] }}</b>
              </i>
            </div>
          </div>
          <div class="today-target-progress" :style="{ '--target-progress': todayTargetPercent + '%' }">
            <span>&#x4eca;&#x65e5;&#x76ee;&#x6807;&#x8fdb;&#x5ea6;</span>
            <div class="today-donut">
              <strong>{{ todayTargetPercent }}%</strong>
            </div>
            <p>{{ todayTargetDone }} / {{ todayTargetTotal }} &#x9879;&#x5df2;&#x5b8c;&#x6210;</p>
            <div class="today-target-track"><i :style="{ width: todayTargetPercent + '%' }" /></div>
          </div>
        </div>
      </aside>
    </section>

    <section class="today-queue-panel span-8" aria-label="&#x4f18;&#x5148;&#x4efb;&#x52a1;&#x961f;&#x5217;">
      <div class="portal-section-head">
        <div>
          <h2>优先任务队列</h2>
        </div>
        <RouterLink class="ghost-button" to="/courses">
          <GraduationCap :size="17" :stroke-width="1.8" />&#x6211;&#x7684;&#x8bfe;&#x7a0b;
        </RouterLink>
      </div>

      <div class="today-priority-list">
        <div class="today-priority-head" aria-hidden="true">
          <span>&#x4f18;&#x5148;&#x7ea7;</span>
          <span>&#x4efb;&#x52a1;</span>
          <span>&#x6240;&#x5c5e;&#x8bfe;&#x7a0b;</span>
          <span>&#x6765;&#x6e90;</span>
          <span>&#x9884;&#x8ba1;&#x65f6;&#x95f4;</span>
          <span>&#x72b6;&#x6001;</span>
          <span>&#x64cd;&#x4f5c;</span>
        </div>
        <article v-for="item in weightedTodayQueue" :key="item.title" class="today-priority-row" :class="taskStateClass(item)">
          <span class="today-priority-index">{{ item.priority }}</span>
          <div class="today-priority-main">
            <strong>{{ item.title }}</strong>
          </div>
          <span class="today-priority-course">{{ item.course }}</span>
          <span class="today-priority-source">{{ item.source }}</span>
          <span class="today-priority-time">{{ item.minutes }} &#x5206;&#x949f;</span>
          <StatusPill :status="taskStatusLabel(item)" :tone="taskStatusTone(item)" />
          <div class="portal-today-actions">
            <button type="button" data-testid="today-priority-primary" @click="runPriorityAction(item)">{{ priorityActionLabel(item) }}</button>
            <button type="button" class="ghost-action" data-testid="today-priority-open" @click="openPriorityTask(item)">&#x6253;&#x5f00;</button>
          </div>
        </article>
        <footer class="today-priority-footer">
          <span>&#x5171; {{ weightedTodayQueue.length }} &#x9879;&#x8ba1;&#x5212;&#x4e2d;&#xff0c;{{ deferredTaskCount }} &#x9879;&#x7a0d;&#x540e;</span>
          <RouterLink to="/courses">&#x67e5;&#x770b;&#x5168;&#x90e8;&#x4efb;&#x52a1;</RouterLink>
        </footer>
      </div>

      <div class="today-queue-summary" aria-label="&#x961f;&#x5217;&#x6458;&#x8981;">
        <article>
          <Clock3 :size="19" :stroke-width="1.9" />
          <div>
            <span>今日预算</span>
            <strong>{{ selectedBudget }} 分钟</strong>
          </div>
        </article>
        <article>
          <BrainCircuit :size="19" :stroke-width="1.9" />
          <div>
            <span>排序依据</span>
            <strong>截止 / 掌握 / 来源</strong>
          </div>
        </article>
        <article>
          <Target :size="19" :stroke-width="1.9" />
          <div>
            <span>执行状态</span>
            <strong>{{ weightedTodayQueue.length - deferredTaskCount }} 项前置</strong>
          </div>
        </article>
      </div>
    </section>

    <div
      class="panel-resizer today-panel-resizer"
      role="separator"
      aria-orientation="vertical"
      title="拖动调整宽度，双击恢复默认"
      @pointerdown="todayStartResize(0, $event)"
      @dblclick="todayResetLayout()"
    ></div>

    <aside class="today-tuner-panel span-4" aria-label="&#x53ef;&#x8c03;&#x8ba1;&#x5212;">
      <div class="portal-section-head compact">
        <div>
          <h2>&#x53ef;&#x8c03;&#x8ba1;&#x5212;</h2>
        </div>
      </div>

      <div class="today-budget-switch" aria-label="&#x65f6;&#x95f4;&#x9884;&#x7b97;">
        <button
          v-for="minutes in timeBudgetOptions"
          :key="minutes"
          type="button"
          :class="{ active: selectedBudget === minutes }"
          @click="updateBudget(minutes)"
        >
          {{ minutes }}min
        </button>
      </div>

      <div class="today-factor-list">
        <article v-for="factor in planningFactors" :key="factor.label" class="today-factor-row">
          <div class="today-factor-label-group">
            <strong>{{ factor.label }}</strong>
          </div>
          <div class="today-factor-control-group">
            <label class="today-factor-slider">
              <i :style="{ width: factor.value + '%' }" />
              <b :style="{ left: factor.value + '%' }" />
              <input
                type="range"
                min="0"
                max="100"
                step="1"
                :value="factor.value"
                :aria-label="factor.label + '权重'"
                @input="setPlanningWeight(factor.key, readInputValue($event))"
                @change="updatePlanningWeight(factor.key, readInputValue($event))"
              />
            </label>
            <span>{{ factor.value }}%</span>
          </div>
        </article>
      </div>

      <div class="today-preview-queue">
        <span class="portal-eyebrow">AI &#x91cd;&#x6392;&#x9884;&#x89c8;</span>
        <article v-for="item in reorderedPreview" :key="item.title">
          <span>{{ item.priority }}</span>
          <strong>{{ item.title }}</strong>
          <small>{{ item.minutes }} &#x5206;&#x949f; / {{ item.course }}</small>
        </article>
      </div>

      <button class="today-replan-button" type="button" data-testid="today-replan-button" @click="replanToday">
        <Sparkles :size="17" :stroke-width="1.9" />&#x91cd;&#x65b0;&#x89c4;&#x5212;&#x4eca;&#x65e5;&#x4efb;&#x52a1;
      </button>
    </aside>

    <section class="today-bottom-panel span-12" aria-label="&#x5feb;&#x901f;&#x8fdb;&#x5165;&#x548c;&#x4eca;&#x65e5;&#x590d;&#x76d8;">
      <div class="quick-course-strip">
        <div class="portal-section-head compact">
          <div>
            <h2>&#x5feb;&#x901f;&#x8fdb;&#x5165;&#x8bfe;&#x7a0b;</h2>
          </div>
        </div>
        <div class="quick-course-list">
          <article v-for="course in quickCourseEntries" :key="course.id" class="quick-course-card">
            <span>{{ course.source }}</span>
            <strong>{{ course.title }}</strong>
            <small>{{ course.department }} &#x00b7; {{ course.progress }}%</small>
            <div class="progress-track"><div class="progress-fill" :style="{ width: course.progress + '%' }" /></div>
            <button type="button" data-testid="quick-course-open" @click="openQuickCourse(course)">&#x8fdb;&#x8bfe;&#x7a0b;</button>
          </article>
        </div>
      </div>

      <form class="today-reflection-box" aria-label="&#x4eca;&#x65e5;&#x590d;&#x76d8;" @submit.prevent="submitReflection">
        <header class="today-reflection-head">
          <h2>&#x628a;&#x4eca;&#x5929;&#x7684;&#x95ee;&#x9898;&#x4ea4;&#x7ed9; AI &#x91cd;&#x6392;</h2>
        </header>

        <div class="today-reflection-composer" :class="{ 'is-busy': reflectionLoading }">
          <textarea
            v-model="reflectionInput"
            :disabled="reflectionLoading"
            rows="2"
            placeholder="&#x4f8b;&#x5982;&#xff1a;&#x6211;&#x4eca;&#x5929;&#x53ea;&#x5269; 30 &#x5206;&#x949f;&#xff0c;&#x5e2e;&#x6211;&#x91cd;&#x65b0;&#x6392;&#x4e00;&#x4e0b;"
            @keydown.enter.exact.prevent="submitReflection"
          />
          <button type="submit" :disabled="!canSubmitReflection" class="today-reflection-submit-icon" aria-label="发送">
            <Loader2 v-if="reflectionLoading" class="today-reflection-spinner" :size="20" :stroke-width="2" />
            <ArrowUp v-else :size="20" :stroke-width="2" />
          </button>
        </div>

        <div class="today-reflection-prompts" aria-label="&#x5feb;&#x901f;&#x590d;&#x76d8;&#x95ee;&#x9898;">
          <button
            v-for="item in reflectionQuickPrompts"
            :key="item.label"
            type="button"
            :disabled="reflectionLoading"
            @click="applyReflectionPrompt(item.prompt)"
          >
            {{ item.label }}
          </button>
        </div>

        <p v-if="reflectionError" class="today-reflection-error">{{ reflectionError }}</p>

        <article
          v-if="reflectionResult"
          class="today-reflection-result"
          :class="reflectionResult.status === 'ai' ? 'is-ai' : reflectionResult.status === 'pending' ? 'is-pending' : 'is-fallback'"
          data-testid="today-reflection-result"
        >
          <header>
            <span>
              <CheckCircle2 :size="16" :stroke-width="2" />
              {{ reflectionResult.source }}
            </span>
            <small>
              {{
                reflectionResult.status === 'ai'
                  ? '已写入规划上下文'
                  : reflectionResult.status === 'pending'
                    ? 'AI 校准中，可先采纳'
                    : '保留输入，稍后可重试'
              }}
            </small>
          </header>
          <p>{{ reflectionResult.answer }}</p>
          <div class="today-reflection-actions" v-if="reflectionResult.actions.length">
            <span v-for="item in reflectionResult.actions" :key="item">{{ item }}</span>
          </div>
          <footer>
            <button type="button" @click="applyReflectionPlan">&#x91c7;&#x7eb3;&#x5230;&#x4eca;&#x65e5;&#x8ba1;&#x5212;</button>
            <button type="button" class="ghost-action" @click="dismissReflectionResult">&#x6536;&#x8d77;</button>
          </footer>
        </article>
      </form>
    </section>
  </div>
</template>

<style scoped>
:global(html body .app-shell.is-student .today-factor-row) {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  padding: 0 !important;
}

:global(html body .app-shell.is-student .today-factor-label-group) {
  display: flex !important;
  flex-direction: column !important;
  gap: 2px !important;
  width: 110px !important;
}

:global(html body .app-shell.is-student .today-factor-control-group) {
  display: flex !important;
  align-items: center !important;
  gap: 16px !important;
  flex: 1 !important;
}

:global(html body .app-shell.is-student .today-factor-slider) {
  cursor: pointer;
  display: block;
  flex: 1 !important;
  position: relative;
}

:global(html body .app-shell.is-student .today-factor-slider input[type='range']) {
  position: absolute;
  inset: -12px 0;
  z-index: 2;
  width: 100%;
  cursor: pointer;
  opacity: 0;
}
</style>
