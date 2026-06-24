<script setup lang="ts">
import {
  ArrowRight,
  BookOpenCheck,
  Bot,
  Calendar,
  CheckCircle2,
  Clock,
  ClipboardList,
  Download,
  FileText,
  FolderOpen,
  MoreVertical,
  Play,
  Plus,
  RefreshCw,
  Search,
  Send,
  Sparkles,
  UploadCloud,
} from 'lucide-vue-next'
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { agentsApi, assignmentsApi, coursesApi, learningApi, profilesApi, tasksApi } from '@/api'
import type { CourseAssignment } from '@/api'
import ErrorNotice from '@/components/ErrorNotice.vue'
import LoadingBlock from '@/components/LoadingBlock.vue'
import MarkdownView from '@/components/MarkdownView.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import StatusPill from '@/components/StatusPill.vue'
import { useAppStore } from '@/stores/app'
import { useResizablePanels } from '@/composables/useResizablePanels'
import type { Course, GenerationTask, LearningConversation, LearningConversationMessage, LearningResource, ProfileResponse } from '@/types/api'
import { downloadText, safeFilePart } from '@/utils/download'
import { cleanDisplayText, compact, formatDate, parseMaybeJson } from '@/utils/format'
import moduleCourseCover from '@/assets/module-course.png'

const app = useAppStore()
const route = useRoute()
const router = useRouter()

// 学习路径三栏：章节列表 / 推荐资源 / 画像摘要，列宽可拖拽并记忆
const {
  gridStyle: pathGridStyle,
  startResize: pathStartResize,
  resetLayout: pathResetLayout,
} = useResizablePanels({
  storageKey: 'course-overview',
  defaultWeights: [1.05, 1, 1],
  minWidths: [280, 360, 280],
})
const loading = ref(false)
const error = ref('')
const courses = ref<Course[]>([])
const selectedCourse = ref<Course | null>(null)
const resources = ref<LearningResource[]>([])
const selectedResource = ref<LearningResource | null>(null)
const selectedPathKey = ref('')
const generationTasks = ref<GenerationTask[]>([])
const profiles = ref<ProfileResponse[]>([])
const activeCourseTab = ref<'overview' | 'resources' | 'path' | 'tasks' | 'assistant' | 'records'>('overview')
const courseFilter = ref<'all' | 'classroom' | 'self' | 'recent' | 'archived'>('all')
const courseSearchKeyword = ref('')
const joinDialogOpen = ref(false)
const classCodeInput = ref('')
const activeMoreCourseId = ref('')
const courseActionFeedback = ref('')
const courseAssistantDraft = ref('')
const courseAssistantConversation = ref<LearningConversation | null>(null)
const courseAssistantMessages = ref<LearningConversationMessage[]>([])
const courseAssistantLoading = ref(false)
const courseAssistantError = ref('')
const courseAssistantLastQuestion = ref('')
const storage = typeof window === 'undefined' ? null : window.localStorage
const recentCourseKey = 'student-recent-course-ids'
const recentClearedKey = 'student-recent-courses-cleared'
const joinedCourseKey = 'student-joined-course-ids'
const pathResourceKey = 'student-path-resource-ids'
const readActivityDismissedKey = 'student-course-read-activity-dismissed'

interface ResourcePreviewItem {
  id: string
  title: string
  subtitle: string
  source: string
  minutes: number
  action: string
  status: 'published' | 'suggested'
  target?: 'external' | 'generate'
  url?: string
  prompt?: string
  resource?: LearningResource | null
}

interface CourseOutlineItem {
  key: string
  title: string
  subtitle: string
  status: string
  resource: LearningResource | null
}

function readStoredIds(key: string) {
  if (!storage) return []
  try {
    const parsed = JSON.parse(storage.getItem(key) || '[]')
    return Array.isArray(parsed) ? parsed.map(String).filter(Boolean) : []
  } catch {
    return []
  }
}

const recentCourseIds = ref<string[]>(readStoredIds(recentCourseKey))
const recentCoursesCleared = ref(storage?.getItem(recentClearedKey) === '1')
const joinedCourseIds = ref<string[]>(readStoredIds(joinedCourseKey))
const pathResourceIds = ref<string[]>(readStoredIds(pathResourceKey))
const dismissedReadActivityGroups = ref<string[]>(readStoredIds(readActivityDismissedKey))

const isTeacher = computed(() => app.role === 'teacher')
const isCourseIndex = computed(() => !isTeacher.value && !routeCourseId.value)
const isStudentCourseDetail = computed(() => !isTeacher.value && Boolean(routeCourseId.value))
const activeStudentProfile = computed(() =>
  profiles.value.find((profile) => profile.studentName === app.currentUser.name) || profiles.value[0] || null,
)
const selectedCourseDescription = computed(() => cleanDisplayText(selectedCourse.value?.description || '请选择一门已有课程。'))
const selectedKnowledgePoints = computed(() => {
  const syllabus = parseMaybeJson<Record<string, unknown>>(selectedCourse.value?.syllabusJson, {})
  const points = syllabus.knowledgePoints
  return Array.isArray(points) ? points.map((item) => String(item)).filter(Boolean) : []
})
const courseSwitchCards = computed(() =>
  courses.value.map((course) => ({
    ...course,
    active: course.id === selectedCourse.value?.id,
    descriptionText: cleanDisplayText(course.description),
  })),
)
const courseHeaderTitle = computed(() => (isTeacher.value ? '课程空间' : '我的课程'))
const courseHeaderSubtitle = computed(() =>
  isTeacher.value
    ? '维护班级课程、资源生产、发布审核与学生可见内容。'
    : '切换课程、阅读资源、进入课程答疑与测评。'
)
const selectedCourseLine = computed(() =>
  selectedCourse.value
    ? `${selectedCourse.value.department} · ${selectedCourse.value.creditHours} 学时 · ${resources.value.length} 个资源`
    : '选择课程后进入资源区'
)
const courseWorkItems = computed(() =>
  isTeacher.value
    ? [
        { label: '当前课程', value: selectedCourse.value?.title || '未选择', detail: selectedCourseLine.value },
        { label: '资源生产', value: `${resources.value.length} 个`, detail: '生成后进入审核与发布' },
        { label: '知识点', value: `${selectedKnowledgePoints.value.length} 个`, detail: '来自课程大纲与资料解析' },
      ]
    : [
        { label: '当前课程', value: selectedCourse.value?.title || '未选择', detail: selectedCourseLine.value },
        { label: '可学资源', value: `${resources.value.length} 个`, detail: selectedResource.value?.title || '选择资源后阅读正文' },
        { label: '知识点', value: `${selectedKnowledgePoints.value.length} 个`, detail: '用于答疑、测评与路径推荐' },
      ],
)
const canDownloadCourse = computed(() => Boolean(selectedCourse.value?.title))
const routeCourseId = computed(() => String(route.params.courseId || ''))
const selectedCoursePath = computed(() => (selectedCourse.value?.id ? `/courses/${selectedCourse.value.id}` : '/courses'))
const courseAssistantRoute = computed(() => ({
  path: '/learning',
  query: { tab: 'chat', courseId: selectedCourse.value?.id || '' },
}))
const courseProjectRoute = computed(() => ({
  path: '/learning',
  query: { tab: 'chat', courseId: selectedCourse.value?.id || '', question: selectedCourseCardStats.value.nextLesson },
}))
const courseGenerateRoute = computed(() =>
  isTeacher.value
    ? { path: '/generation', query: selectedCourse.value?.id ? { courseId: selectedCourse.value.id } : undefined }
    : { path: '/learning', query: { tab: 'generate', courseId: selectedCourse.value?.id || '' } },
)
const resourceListTitle = computed(() => (isTeacher.value ? '课程空间与资源状态' : '我的课程与学习资源'))
const resourcePanelTitle = computed(() => (isTeacher.value ? '课程资源状态' : '已发布学习资源'))
const selectedResourceContent = computed(() => selectedResource.value?.content || '')
const selectedResourceTypeName = computed(() => selectedResource.value?.resourceTypeName || selectedResource.value?.resourceType || '学习资源')
const selectedResourceMeta = computed(() =>
  selectedResource.value ? `${selectedResource.value.modality} / ${selectedResource.value.estimatedMinutes} 分钟` : '',
)
const courseOutlineItems = computed<CourseOutlineItem[]>(() => {
  if (selectedKnowledgePoints.value.length) {
    return selectedKnowledgePoints.value.map((point, index) => {
      const resource = resources.value[index] || null
      return {
        key: `${point}-${index}`,
        title: point,
        subtitle: resource?.title || '等待资源生成后自动关联',
        resource,
        status: resource ? (resource.id === selectedResource.value?.id ? '正在学习' : '有资源') : '待补充',
      }
    })
  }
  return resources.value.map((resource, index) => ({
    key: resource.id,
    title: resource.title,
    subtitle: `${resource.resourceTypeName || resource.resourceType} · ${resource.estimatedMinutes || 0} 分钟`,
    resource,
    status: index === 0 ? '正在学习' : reviewStatusLabel(resource.reviewStatus),
  }))
})

// ===== 课程任务（老师发布的作业/测试，后端持久化） =====
const courseTasks = ref<CourseAssignment[]>([])
const courseTasksLoading = ref(false)
const activeCourseTaskId = ref('')
const taskAnswerDraft = ref('')
const taskQuizAnswers = ref<Record<string, number>>({})
const taskSubmitting = ref(false)

async function loadCourseTasks() {
  const courseId = selectedCourse.value?.id
  if (!courseId) {
    courseTasks.value = []
    return
  }
  courseTasksLoading.value = true
  try {
    courseTasks.value = await assignmentsApi.list(courseId, activeStudentProfile.value?.id)
  } catch (err) {
    courseTasks.value = []
  } finally {
    courseTasksLoading.value = false
  }
}

const courseProgressPercent = computed(() => {
  if (!courseOutlineItems.value.length) return 0
  const readyCount = courseOutlineItems.value.filter((item) => item.resource).length
  return Math.round((readyCount / courseOutlineItems.value.length) * 100)
})
const courseGenerationRecords = computed(() =>
  generationTasks.value
    .filter((task) => !selectedCourse.value?.id || task.courseId === selectedCourse.value.id)
    .slice(0, 6),
)
const coursePathModuleCount = computed(() => Math.max(6, courseOutlineItems.value.length))

const activeCourseTask = computed(() => courseTasks.value.find((t) => t.id === activeCourseTaskId.value) || null)

function taskSubmission(taskId: string) {
  return courseTasks.value.find((t) => t.id === taskId)?.submission || null
}

function openCourseTask(task: CourseAssignment) {
  activeCourseTaskId.value = task.id
  const existing = task.submission
  taskAnswerDraft.value = existing?.content || ''
  taskQuizAnswers.value = { ...(existing?.answers || {}) }
}

function closeCourseTask() {
  activeCourseTaskId.value = ''
  taskAnswerDraft.value = ''
  taskQuizAnswers.value = {}
}

function selectQuizOption(questionId: string, optionIndex: number) {
  taskQuizAnswers.value = { ...taskQuizAnswers.value, [questionId]: optionIndex }
}

const canSubmitCourseTask = computed(() => {
  const task = activeCourseTask.value
  if (!task) return false
  if (task.type === 'homework') return taskAnswerDraft.value.trim().length > 0
  return (task.questions || []).every((q) => taskQuizAnswers.value[q.id] !== undefined)
})

async function submitCourseTask() {
  const task = activeCourseTask.value
  const studentProfileId = activeStudentProfile.value?.id
  if (!task || !canSubmitCourseTask.value) return
  if (!studentProfileId) {
    courseActionFeedback.value = '请先创建或选择学习画像后再提交。'
    return
  }
  taskSubmitting.value = true
  try {
    const updated =
      task.type === 'homework'
        ? await assignmentsApi.submit(task.id, { studentProfileId, content: taskAnswerDraft.value.trim() })
        : await assignmentsApi.submit(task.id, { studentProfileId, answers: { ...taskQuizAnswers.value } })
    const index = courseTasks.value.findIndex((t) => t.id === task.id)
    if (index >= 0) courseTasks.value.splice(index, 1, updated)
    const sub = updated.submission
    courseActionFeedback.value =
      task.type === 'quiz' && sub?.total
        ? `已提交「${task.title}」，得分 ${sub.score}/${sub.total}。`
        : `已提交「${task.title}」。`
    closeCourseTask()
  } catch (err) {
    courseActionFeedback.value = err instanceof Error ? err.message : '提交失败，请稍后重试。'
  } finally {
    taskSubmitting.value = false
  }
}
const courseDetailTabs = computed(() =>
  isStudentCourseDetail.value
    ? [
        { key: 'path' as const, label: '学习路径', count: coursePathModuleCount.value },
        { key: 'resources' as const, label: '章节资源', count: resources.value.length },
        { key: 'tasks' as const, label: '课程任务', count: courseTasks.value.length },
        { key: 'assistant' as const, label: '课程 AI 助教', count: 1 },
      ]
    : [
        { key: 'overview' as const, label: '课程概览', count: selectedCourse.value ? 1 : 0 },
        { key: 'resources' as const, label: '章节资源', count: resources.value.length },
        { key: 'path' as const, label: '学习路径', count: courseOutlineItems.value.length },
        { key: 'tasks' as const, label: '课程任务', count: courseTasks.value.length },
        { key: 'assistant' as const, label: 'AI 助教', count: 1 },
      ],
)
const courseFilters = [
  { key: 'all' as const, label: '全部课程' },
  { key: 'classroom' as const, label: '班级课程' },
  { key: 'self' as const, label: '自建课程' },
  { key: 'recent' as const, label: '最近学习' },
  { key: 'archived' as const, label: '已归档' },
]
const cardProgressSeeds = [72, 54, 61, 46, 68, 57]
const cardTotalSeeds = [12, 11, 12, 11, 10, 9]
const cardVisualTones = ['code', 'ai', 'project', 'basic', 'data', 'lab']
const filteredCourseCards = computed(() => {
  const keyword = courseSearchKeyword.value.trim().toLowerCase()
  const cards = courses.value.map((course, index) => {
    const progress = cardProgressSeeds[index % cardProgressSeeds.length]
    const totalModules = cardTotalSeeds[index % cardTotalSeeds.length]
    return {
      course,
      index,
      source: courseSourceKind(course),
      progress,
      completedModules: Math.max(1, Math.round((progress / 100) * totalModules)),
      totalModules,
      visualTone: cardVisualTones[index % cardVisualTones.length],
      nextTask: getCourseNextTask(course, index),
      recentLabel: getCourseRecentLabel(course, index),
    }
  })

  let nextCards = cards
  if (courseFilter.value === 'classroom') nextCards = nextCards.filter((item) => item.source === 'classroom')
  if (courseFilter.value === 'self') nextCards = nextCards.filter((item) => item.source === 'self')
  if (courseFilter.value === 'recent') {
    const recentOrder = new Map(recentCourseIds.value.map((id, index) => [id, index]))
    nextCards = nextCards
      .filter((item) => recentOrder.has(item.course.id))
      .sort((a, b) => Number(recentOrder.get(a.course.id)) - Number(recentOrder.get(b.course.id)))
  }
  if (courseFilter.value === 'archived') nextCards = []
  if (keyword) {
    nextCards = nextCards.filter((item) =>
      `${item.course.title} ${item.course.department} ${cleanDisplayText(item.course.description)}`.toLowerCase().includes(keyword),
    )
  }

  return nextCards.slice(0, 4)
})
const recentOpenCards = computed(() => {
  if (recentCoursesCleared.value && !recentCourseIds.value.length) return []
  const byId = new Map(courses.value.map((course) => [course.id, course]))
  const ordered = recentCourseIds.value.map((id) => byId.get(id)).filter((course): course is Course => Boolean(course))
  const fallback = [...courses.value]
    .filter((course) => !recentCourseIds.value.includes(course.id))
    .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
  return [...ordered, ...fallback]
    .slice(0, 4)
    .map((course, index) => ({
      course,
      index,
      label: getCourseRecentLabel(course, index),
      visualTone: cardVisualTones[index % cardVisualTones.length],
    }))
})
const selectedCourseCardStats = computed(() => {
  const index = Math.max(0, courses.value.findIndex((course) => course.id === selectedCourse.value?.id))
  const totalModules = Math.max(6, courseOutlineItems.value.length, resources.value.length)
  const completedModules = Math.min(totalModules, resources.value.length)
  const progress = totalModules ? Math.round((completedModules / totalModules) * 100) : 0
  const pendingTasks = courseGenerationRecords.value.filter((task) => {
    const status = String(task.status || '').toUpperCase()
    return !['SUCCEEDED', 'FAILED', 'CANCELLED'].includes(status)
  }).length
  return {
    index,
    progress,
    totalModules,
    completedModules,
    pendingTasks,
    lastStudy: selectedResource.value ? `${selectedResource.value.estimatedMinutes || 0} 分钟` : resources.value.length ? getCourseRecentLabel(selectedCourse.value, index) : '暂无记录',
    nextLesson: selectedKnowledgePoints.value[2] || selectedResource.value?.title || 'HTTP 协议与请求响应',
  }
})
const selectedCourseMetricLastStudy = computed(() => selectedCourseCardStats.value.lastStudy.split(' ')[0])
const selectedCourseDetailMetrics = computed(() => [
  {
    key: 'progress',
    label: '课程进度',
    value: `${selectedCourseCardStats.value.progress}%`,
    detail: resources.value.length ? `已接入 ${resources.value.length} 个资源` : '暂无学习证据',
    icon: 'progress',
  },
  {
    key: 'modules',
    label: '完成模块',
    value: `${selectedCourseCardStats.value.completedModules} / ${selectedCourseCardStats.value.totalModules}`,
    detail: '按资源完成度计算',
    icon: 'modules',
  },
  { key: 'todo', label: '进行中任务', value: `${selectedCourseCardStats.value.pendingTasks}`, detail: '来自生成队列', icon: 'todo' },
  { key: 'recent', label: '最近学习', value: selectedCourseMetricLastStudy.value, detail: resources.value.length ? '继续学习当前资源' : '暂无记录', icon: 'recent' },
])
const courseActivityRaw = ref<import('@/api').CourseActivityGroup[]>([])
const courseActivityLoading = ref(false)

async function loadCourseActivity() {
  const courseId = selectedCourse.value?.id
  if (!courseId) {
    courseActivityRaw.value = []
    return
  }
  courseActivityLoading.value = true
  try {
    courseActivityRaw.value = await coursesApi.activity(courseId)
  } catch {
    courseActivityRaw.value = []
  } finally {
    courseActivityLoading.value = false
  }
}

const activityToneByKey: Record<string, string> = { publish: 'teal', ai: 'violet', todo: 'orange', self: 'blue' }
const courseActivityGroups = computed(() =>
  courseActivityRaw.value
    .filter((group) => !dismissedReadActivityGroups.value.includes(group.key))
    .map((group) => ({
      key: group.key,
      tone: activityToneByKey[group.key] || 'teal',
      title: group.title,
      badge: group.key === 'todo' && group.items.length ? String(group.items.length) : '',
      items: group.items.map((item) => ({
        title: item.title,
        course: item.courseTitle,
        time: item.time ? formatDate(item.time) : '',
        courseId: item.courseId,
      })),
    })),
)

const hasReadableCourseActivities = computed(() => courseActivityGroups.value.some((group) => group.key !== 'todo'))

function clearReadCourseActivities() {
  dismissedReadActivityGroups.value = ['publish', 'ai']
  storage?.setItem(readActivityDismissedKey, JSON.stringify(dismissedReadActivityGroups.value))
}

function getActivityRoute(activity: any, group: any) {
  if (group.key === 'todo' && activity.courseId) {
    return {
      path: `/courses/${activity.courseId}`,
      query: { tab: 'tasks' },
    }
  }
  if (!activity.courseId) {
    return '/courses'
  }
  return `/courses/${activity.courseId}`
}
const detailPathItems = computed(() => {
  // 仅使用真实大纲（来自知识点/已生成资源）；无大纲则为空，由模板提示生成学习路径
  return courseOutlineItems.value.map((item, index) => ({
    ...item,
    type: index === 0 ? '导学' : index < 3 ? '讲解' : index < 5 ? '练习' : '项目',
    minutes: item.resource?.estimatedMinutes || 0,
    progress: item.status || '未开始',
  }))
})
const selectedPathActiveKey = computed(() => {
  const items = detailPathItems.value
  if (selectedPathKey.value && items.some((item) => item.key === selectedPathKey.value)) return selectedPathKey.value
  const resourceId = selectedResource.value?.id
  if (resourceId) {
    const matched = items.find((item) => item.resource?.id === resourceId)
    if (matched) return matched.key
  }
  return items.find((item) => String(item.progress).includes('进行'))?.key || items[0]?.key || ''
})
const currentPathItemForResources = computed(
  () => detailPathItems.value.find((item) => item.key === selectedPathActiveKey.value) || detailPathItems.value[0] || null,
)
const activeResourceTopic = computed(
  () => currentPathItemForResources.value?.title || selectedCourseCardStats.value.nextLesson || selectedCourse.value?.title || '当前章节',
)

function toResourcePreviewItem(resource: LearningResource, index: number): ResourcePreviewItem {
  return {
    id: `resource-${resource.id}`,
    title: cleanDisplayText(resource.title),
    subtitle: `${resource.resourceTypeName || resource.resourceType || '课程资料'} · ${resource.estimatedMinutes || 0} 分钟`,
    source: index === 0 ? '老师发布' : '课程资源',
    minutes: resource.estimatedMinutes || 18,
    action: '加入路径',
    status: 'published',
    resource,
  }
}

function searchUrl(site: 'bilibili' | 'books' | 'docs', query: string) {
  const encoded = encodeURIComponent(query)
  if (site === 'bilibili') return `https://search.bilibili.com/all?keyword=${encoded}`
  if (site === 'books') return `https://www.google.com/search?q=${encodeURIComponent(`${query} open textbook OR 官方文档 OR 电子书`)}`
  return `https://www.google.com/search?q=${encodeURIComponent(`${query} 官方文档 示例 代码`)}`
}

function suggestedResource(
  id: string,
  title: string,
  subtitle: string,
  source: string,
  minutes: number,
  options: Partial<Pick<ResourcePreviewItem, 'action' | 'target' | 'url' | 'prompt'>> = {},
): ResourcePreviewItem {
  return {
    id,
    title,
    subtitle,
    source,
    minutes,
    action: options.action || '打开资源',
    status: 'suggested',
    target: options.target || 'external',
    url: options.url,
    prompt: options.prompt,
    resource: null,
  }
}

const resourcePreviewSections = computed(() => {
  const topic = activeResourceTopic.value
  const courseItems = resources.value.slice(0, 2).map(toResourcePreviewItem)
  if (!courseItems.length) {
    courseItems.push(
      suggestedResource('course-outline-pack', `${topic} 学习包`, '讲义、例题、检查点一并生成', 'AI 可生成', 18, {
        action: '去生成',
        target: 'generate',
        prompt: `基于课程「${selectedCourse.value?.title || '当前课程'}」生成「${topic}」的讲义、例题和检查点。`,
      }),
    )
  }

  const webItems = [
    ...resources.value.slice(2, 3).map((resource, index) => toResourcePreviewItem(resource, index + 2)),
    suggestedResource('web-practice-course', `${topic} 实战微课`, 'B 站课程检索 · 按当前模块匹配', 'B站', 20, {
      action: '打开视频',
      url: searchUrl('bilibili', `${selectedCourse.value?.title || ''} ${topic} 教程`),
    }),
    suggestedResource('web-case-walkthrough', `${selectedCourse.value?.title || '本课'} 案例串讲`, 'B 站案例检索 · 先看流程再练习', 'B站', 16, {
      action: '打开视频',
      url: searchUrl('bilibili', `${selectedCourse.value?.title || ''} 案例 实战`),
    }),
  ].slice(0, 2)

  const docItems = [
    ...resources.value.slice(3, 4).map((resource, index) => toResourcePreviewItem(resource, index + 3)),
    suggestedResource('docs-official-guide', `${topic} 文档/电子书检索`, '开放教材、官方文档和示例代码', '开放文档', 14, {
      action: '打开文档',
      url: searchUrl('books', `${selectedCourse.value?.title || ''} ${topic}`),
    }),
    suggestedResource('docs-code-notes', `${topic} 案例代码笔记`, '按知识点整理可复用片段', 'AI 可生成', 12, {
      action: '生成案例',
      target: 'generate',
      prompt: `为「${topic}」生成可运行的案例代码、关键注释和练习任务。`,
    }),
  ].slice(0, 2)

  return [
    { key: 'course', title: '课程资料', subtitle: courseItems.some((item) => item.status === 'published') ? '老师发布 · 已接入' : '暂无发布 · 先生成', items: courseItems },
    { key: 'web', title: '高分网课', subtitle: '公开课 / 精品课 · AI 匹配', items: webItems },
    { key: 'docs', title: '电子书 / 文档', subtitle: '官方文档 / 案例代码', items: docItems },
  ]
})
const profileSignals = computed(() => [
  { label: '知识覆盖', value: '61%' },
  { label: '实践能力', value: '55%' },
  { label: '代码规范', value: '50%' },
])
const latestCourseAssistantUserMessage = computed(() => [...courseAssistantMessages.value].reverse().find((item) => item.role === 'user'))
const latestCourseAssistantAnswer = computed(() => [...courseAssistantMessages.value].reverse().find((item) => item.role === 'assistant'))
const hasCourseAssistantPendingResponse = computed(() =>
  courseAssistantMessages.value.some((message) => message.id.startsWith('pending-course-assistant-')),
)
const courseAssistantDoubtSummary = computed(() => ({
  question: compact(cleanDisplayText(latestCourseAssistantUserMessage.value?.content || courseAssistantLastQuestion.value || '还没有记录疑惑点'), 60),
}))
const courseActionItems = computed(() =>
  isTeacher.value
    ? [
        { label: '资源复核', value: `${resources.value.length} 个`, detail: '确认正文、引用和发布状态' },
        { label: '学生可见', value: `${resources.value.filter((item) => reviewStatusLabel(item.reviewStatus) === '已发布').length} 个`, detail: '发布后同步到学生课程空间' },
        { label: '下一步', value: '发布质检', detail: '检查课程是否可开放给学生' },
      ]
    : [
        { label: '学习进度', value: `${courseProgressPercent.value}%`, detail: selectedResource.value?.title || '选择资源开始学习' },
        { label: '答疑入口', value: 'AI 助教', detail: '围绕当前资源提问和生成测评' },
        { label: '下一步', value: '继续学习', detail: selectedKnowledgePoints.value[1] || selectedResource.value?.title || '等待课程资源' },
      ],
)

async function loadCourses() {
  loading.value = true
  error.value = ''
  if (isStudentCourseDetail.value && activeCourseTab.value === 'overview') activeCourseTab.value = 'path'
  try {
    const [courseResult, taskResult, profileResult] = await Promise.allSettled([coursesApi.list(), tasksApi.list(), profilesApi.list()])
    courses.value = courseResult.status === 'fulfilled' ? courseResult.value : []
    generationTasks.value = taskResult.status === 'fulfilled' ? taskResult.value : []
    profiles.value = profileResult.status === 'fulfilled' ? profileResult.value : []
    const preferred =
      courses.value.find((course) => course.id === routeCourseId.value) ||
      courses.value.find((course) => course.id === app.activeCourseId) ||
      courses.value[0]
    if (preferred && (!selectedCourse.value || selectedCourse.value.id !== preferred.id)) {
      await selectCourse(preferred, false)
    } else if (!preferred) {
      selectedCourse.value = null
      resources.value = []
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '课程加载失败'
  } finally {
    loading.value = false
  }
}

async function selectCourse(course: Course, syncRoute = true) {
  error.value = ''
  try {
    selectedCourse.value = course
    app.setActiveCourse(course.id)
    if (syncRoute && app.role === 'student' && route.path !== `/courses/${course.id}`) {
      void router.push(`/courses/${course.id}`)
    }
    selectedResource.value = null
    if (courseAssistantConversation.value?.courseId !== course.id) {
      courseAssistantConversation.value = null
      courseAssistantMessages.value = []
      courseAssistantError.value = ''
    }
    resources.value = await coursesApi.resources(course.id, { publishedOnly: !isTeacher.value })
    selectedResource.value = resources.value[0] || null
    void loadCourseActivity()
    if (activeCourseTab.value === 'tasks') await loadCourseTasks()
  } catch (err) {
    resources.value = []
    selectedResource.value = null
    error.value = err instanceof Error ? err.message : '课程资源加载失败'
  }
}

async function openCourse(course: Course) {
  activeCourseTab.value = isTeacher.value ? 'overview' : 'path'
  await selectCourse(course)
  trackRecentCourse(course.id)
  await recordCourseEvent('COURSE_OPENED', { title: course.title }, { courseId: course.id, durationSeconds: 30 })
}

async function openCourseTab(tab: typeof activeCourseTab.value) {
  activeCourseTab.value = tab
  courseActionFeedback.value = ''
  await recordCourseEvent('COURSE_TAB_OPENED', { tab }, { durationSeconds: 10 })
  if (tab === 'assistant') await loadCourseAssistantConversation()
  if (tab === 'tasks') await loadCourseTasks()
}

function setCourseFilter(filter: typeof courseFilter.value) {
  courseFilter.value = filter
  const label = courseFilters.find((item) => item.key === filter)?.label || '课程分类'
  courseActionFeedback.value = `已筛选「${label}」，当前显示 ${filteredCourseCards.value.length} 门课程。`
}

function showCoursePath() {
  void openCourseTab('path')
}

const generatingPath = ref(false)
async function generateLearningPath() {
  const studentProfileId = activeStudentProfile.value?.id
  const courseId = selectedCourse.value?.id
  if (!courseId) return
  if (!studentProfileId) {
    courseActionFeedback.value = '请先创建或选择学习画像后再生成学习路径。'
    return
  }
  generatingPath.value = true
  try {
    const result = await agentsApi.invoke('/learning/path-plans', {
      studentProfileId,
      courseId,
      topic: selectedCourse.value?.title || '课程学习路径',
    })
    if (result.fallbackUsed) throw new Error('智能体未就绪（降级），请稍后重试。')
    courseActionFeedback.value = '已生成学习路径。'
    // 重新拉取大纲/资源以反映新路径
    await selectCourse(selectedCourse.value as Course, false)
  } catch (err) {
    courseActionFeedback.value = err instanceof Error ? err.message : '生成学习路径失败，请稍后重试。'
  } finally {
    generatingPath.value = false
  }
}

function showCourseResources() {
  void openCourseTab('resources')
}

async function openPathItem(item: (typeof detailPathItems.value)[number], index: number) {
  selectedPathKey.value = item.key
  if (item.resource) {
    selectedResource.value = item.resource
    courseActionFeedback.value = `已选中「${item.title}」，右侧已同步到关联资源。`
    await recordCourseEvent(
      'COURSE_PATH_ITEM_OPENED',
      { title: item.title, order: index + 1, hasResource: true },
      { courseId: selectedCourse.value?.id, resourceId: item.resource.id, durationSeconds: 20 },
    )
    return
  }
  courseActionFeedback.value = `已选中「${item.title}」，右侧推荐资源和本课助教已按该模块更新。`
  await recordCourseEvent(
    'COURSE_PATH_ITEM_OPENED',
    { title: item.title, order: index + 1, hasResource: false },
    { courseId: selectedCourse.value?.id, resourceId: null, durationSeconds: 10 },
  )
}

function toggleCourseMore(course: Course) {
  activeMoreCourseId.value = activeMoreCourseId.value === course.id ? '' : course.id
}

function closeCourseMore() {
  activeMoreCourseId.value = ''
}

function persistIds(key: string, ids: string[]) {
  storage?.setItem(key, JSON.stringify(ids))
}

function trackRecentCourse(courseId: string) {
  if (!courseId) return
  recentCoursesCleared.value = false
  storage?.removeItem(recentClearedKey)
  recentCourseIds.value = [courseId, ...recentCourseIds.value.filter((id) => id !== courseId)].slice(0, 8)
  persistIds(recentCourseKey, recentCourseIds.value)
}

async function recordCourseEvent(
  eventType: string,
  payload: Record<string, unknown>,
  options: { courseId?: string; resourceId?: string | null; durationSeconds?: number; feedbackScore?: number } = {},
) {
  const studentProfileId = activeStudentProfile.value?.id
  const courseId = options.courseId || selectedCourse.value?.id || app.activeCourseId
  if (!studentProfileId || !courseId || isTeacher.value) return false
  try {
    await learningApi.recordEvent({
      studentProfileId,
      courseId,
      resourceId: options.resourceId ?? selectedResource.value?.id ?? null,
      eventType,
      durationSeconds: Math.max(0, Number(options.durationSeconds || 0)),
      feedbackScore: options.feedbackScore,
      eventPayload: JSON.stringify({
        source: 'student-courses',
        ...payload,
      }),
    })
    return true
  } catch (err) {
    courseActionFeedback.value = err instanceof Error ? err.message : '课程动作已完成，但学习事件暂未写入。'
    return false
  }
}

function openJoinClassDialog() {
  joinDialogOpen.value = true
  classCodeInput.value = ''
  courseActionFeedback.value = ''
}

async function joinClassCourse() {
  const code = classCodeInput.value.trim().toLowerCase()
  const classroomCourses = courses.value.filter((course) => courseSourceKind(course) === 'classroom')
  const matched =
    classroomCourses.find((course) => course.id.toLowerCase() === code) ||
    classroomCourses.find((course) => course.title.toLowerCase().includes(code)) ||
    classroomCourses.find((course) => !joinedCourseIds.value.includes(course.id)) ||
    classroomCourses[0]
  if (!matched) {
    courseActionFeedback.value = '当前没有可加入的班级课程。'
    return
  }
  loading.value = true
  error.value = ''
  try {
    let course = await coursesApi.get(matched.id)
    const studentProfileId = activeStudentProfile.value?.id
    if (!studentProfileId) {
      throw new Error('当前没有学生画像，无法加入班级课程。')
    }
    const enrollment = await coursesApi.join(course.id, { studentProfileId })
    course = enrollment.course || course
    joinedCourseIds.value = [course.id, ...joinedCourseIds.value.filter((id) => id !== course.id)].slice(0, 20)
    persistIds(joinedCourseKey, joinedCourseIds.value)
    joinDialogOpen.value = false
    courseActionFeedback.value = `已加入 ${course.title}，并切换到课程详情。`
    await openCourse(course)
    await recordCourseEvent('CLASS_COURSE_JOINED', { code: classCodeInput.value.trim(), title: course.title }, { courseId: course.id })
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加入班级课程失败'
  } finally {
    loading.value = false
  }
}

async function clearRecentCourses() {
  recentCourseIds.value = []
  recentCoursesCleared.value = true
  persistIds(recentCourseKey, [])
  storage?.setItem(recentClearedKey, '1')
  courseActionFeedback.value = '最近打开记录已清除。'
  await recordCourseEvent('RECENT_COURSES_CLEARED', { action: 'clear-recent-courses' }, { durationSeconds: 5 })
}

async function continueLearning() {
  if (!selectedCourse.value) return
  if (!selectedResource.value && resources.value[0]) selectedResource.value = resources.value[0]
  activeCourseTab.value = selectedResource.value ? 'resources' : 'path'
  trackRecentCourse(selectedCourse.value.id)
  const recorded = await recordCourseEvent(
    'COURSE_CONTINUE_LEARNING',
    { title: selectedCourse.value.title, resourceTitle: selectedResource.value?.title || '' },
    { courseId: selectedCourse.value.id, resourceId: selectedResource.value?.id ?? null, durationSeconds: 60 },
  )
  if (!recorded) {
    courseActionFeedback.value = '继续学习事件没有写回后端，请确认学生画像和课程上下文已加载。'
    return
  }
  courseActionFeedback.value = selectedResource.value
    ? `已定位到「${selectedResource.value.title}」，可以继续阅读。`
    : `已打开「${selectedCourse.value.title}」学习路径，等待可用资源。`
}

async function addResourceToPath(resource: LearningResource) {
  selectedResource.value = resource
  const recorded = await recordCourseEvent(
    'RESOURCE_PATH_INTENT_RECORDED',
    { title: resource.title, resourceType: resource.resourceTypeName || resource.resourceType },
    { courseId: resource.courseId || selectedCourse.value?.id, resourceId: resource.id },
  )
  courseActionFeedback.value = recorded
    ? `已记录「${resource.title}」的学习意向；当前后端尚未提供资源写入学习路径接口。`
    : `无法记录「${resource.title}」的学习意向，请确认学生画像和课程上下文已加载。`
}

async function openResourceRecommendation(item: ResourcePreviewItem) {
  if (item.resource) {
    await addResourceToPath(item.resource)
    return
  }
  if (item.url) {
    window.open(item.url, '_blank', 'noopener,noreferrer')
    courseActionFeedback.value = `已打开「${item.title}」的外部资源检索。`
    await recordCourseEvent(
      'RESOURCE_RECOMMENDATION_OPENED',
      { title: item.title, source: item.source, topic: activeResourceTopic.value, url: item.url },
      { courseId: selectedCourse.value?.id, resourceId: null, durationSeconds: item.minutes },
    )
    return
  }
  courseActionFeedback.value = `正在为「${item.title}」进入 AI 生成资源。`
  await recordCourseEvent(
    'RESOURCE_RECOMMENDATION_SELECTED',
    { title: item.title, source: item.source, topic: activeResourceTopic.value },
    { courseId: selectedCourse.value?.id, resourceId: null, durationSeconds: item.minutes },
  )
  await router.push({
    path: '/learning',
    query: {
      tab: 'generate',
      courseId: selectedCourse.value?.id || '',
      generateTopic: item.title,
      generatePrompt: item.prompt || `基于当前课程和学习画像生成「${item.title}」。`,
    },
  })
}

async function continueCourseFromCard(course: Course) {
  closeCourseMore()
  await openCourse(course)
  await continueLearning()
}

async function addCourseToPath(course: Course) {
  closeCourseMore()
  await selectCourse(course, false)
  const firstResource = resources.value[0]
  if (firstResource) {
    await addResourceToPath(firstResource)
    activeCourseTab.value = 'path'
    courseActionFeedback.value = `已把「${course.title}」的首个资源加入学习路径。`
    return
  }
  courseActionFeedback.value = `「${course.title}」暂时没有已发布资源，已保留为当前课程，可先进入 AI 助手生成资源。`
  await recordCourseEvent('COURSE_PATH_REQUESTED_WITHOUT_RESOURCE', { title: course.title }, { courseId: course.id })
}

async function askCourseFromCard(course: Course) {
  closeCourseMore()
  await selectCourse(course, false)
  await recordCourseEvent(
    'COURSE_ASSISTANT_OPENED',
    { title: course.title, question: getCourseNextTask(course, 0), sourceAction: 'course-card-more' },
    { courseId: course.id },
  )
  await router.push({ path: '/learning', query: { tab: 'chat', courseId: course.id, question: getCourseNextTask(course, 0) } })
}

async function openResourcePreview(resource: LearningResource) {
  selectedResource.value = resource
  activeCourseTab.value = 'resources'
  await recordCourseEvent(
    'RESOURCE_PREVIEWED',
    { title: resource.title, resourceType: resource.resourceTypeName || resource.resourceType },
    { courseId: resource.courseId || selectedCourse.value?.id, resourceId: resource.id, durationSeconds: 30 },
  )
}

async function askCurrentCourse(questionOverride: unknown = '') {
  if (!selectedCourse.value) return
  const explicitQuestion = typeof questionOverride === 'string' ? questionOverride : ''
  const question = (explicitQuestion || courseAssistantDraft.value || selectedCourseCardStats.value.nextLesson).trim()
  const studentProfileId = activeStudentProfile.value?.id
  if (!question || !studentProfileId) {
    courseAssistantError.value = '请先输入问题，并确认当前学生画像已加载。'
    return
  }
  courseAssistantLoading.value = true
  courseAssistantError.value = ''
  courseAssistantLastQuestion.value = question
  let conversationId = ''
  let confirmedMessagesBeforeSend: LearningConversationMessage[] = []
  let pendingUserMessage: LearningConversationMessage | null = null
  try {
    conversationId = await ensureCourseAssistantConversation(question)
    confirmedMessagesBeforeSend = courseAssistantMessages.value.filter((message) => !message.id.startsWith('pending-course-assistant-'))
    pendingUserMessage = makeCourseAssistantLocalMessage(conversationId, 'user', question)
    const pendingAssistantMessage = makeCourseAssistantLocalMessage(
      conversationId,
      'assistant',
      '正在结合本课资源、学习路径和你的画像生成回答...',
    )
    courseAssistantMessages.value = [...confirmedMessagesBeforeSend, pendingUserMessage, pendingAssistantMessage]
    courseAssistantDraft.value = ''
    const response = await learningApi.sendConversationMessage(conversationId, {
      content: question,
      message: question,
      modality: '课程内答疑',
      documentTexts: courseAssistantContextDocuments(),
    })
    courseAssistantConversation.value = response.conversation
    courseAssistantMessages.value = [...confirmedMessagesBeforeSend, response.userMessage, response.assistantMessage]
    courseActionFeedback.value = `已记录「${selectedCourse.value.title}」本轮疑惑，并同步到全局 AI 助手会话。`
    await recordCourseEvent(
      'COURSE_ASSISTANT_ASKED',
      { title: selectedCourse.value.title, question, conversationId: response.conversation.id },
      { courseId: selectedCourse.value.id, durationSeconds: 30 },
    )
  } catch (err) {
    courseAssistantError.value = err instanceof Error ? err.message : '课程 AI 助教暂时无法回答，请稍后重试。'
    if (conversationId && pendingUserMessage) {
      courseAssistantMessages.value = confirmedMessagesBeforeSend
    }
  } finally {
    courseAssistantLoading.value = false
  }
}

async function loadCourseAssistantConversation() {
  const course = selectedCourse.value
  const studentProfileId = activeStudentProfile.value?.id
  if (!course || !studentProfileId) return
  courseAssistantLoading.value = true
  courseAssistantError.value = ''
  try {
    const rows = sortConversationsByActivity(await learningApi.conversations({ studentProfileId, courseId: course.id, archived: false }))
    let current: LearningConversation | null = null
    let currentMessages: LearningConversationMessage[] = []
    for (const row of rows.slice(0, 4)) {
      const messages = filterReadableCourseAssistantMessages(await learningApi.conversationMessages(row.id))
      if (!current || messages.length) {
        current = row
        currentMessages = messages
      }
      if (messages.length) break
    }
    courseAssistantConversation.value = current
    courseAssistantMessages.value = currentMessages
  } catch (err) {
    courseAssistantError.value = err instanceof Error ? err.message : '课程会话加载失败，请稍后刷新。'
  } finally {
    courseAssistantLoading.value = false
  }
}

function courseAssistantContextDocuments() {
  const course = selectedCourse.value
  return [
    course ? `课程：${course.title}。${cleanDisplayText(course.description || '')}` : '',
    selectedKnowledgePoints.value.length ? `本课知识点：${selectedKnowledgePoints.value.slice(0, 8).join('、')}` : '',
    ...resources.value.slice(0, 3).map((resource) => `${resource.title}：${compact(cleanDisplayText(resource.content), 180)}`),
  ].filter(Boolean)
}

function isUnreadableQuestionMarkText(value: unknown) {
  const text = cleanDisplayText(String(value || '')).trim()
  return Boolean(text) && /^[?\s？]+$/.test(text)
}

function filterReadableCourseAssistantMessages(messages: LearningConversationMessage[]) {
  return messages.filter((message) => {
    const content = cleanDisplayText(message.content).trim()
    return Boolean(content) && !isUnreadableQuestionMarkText(content)
  })
}

function sortConversationsByActivity(rows: LearningConversation[]) {
  return [...rows].sort(
    (a, b) =>
      new Date(b.lastMessageAt || b.updatedAt || b.createdAt).getTime() -
      new Date(a.lastMessageAt || a.updatedAt || a.createdAt).getTime(),
  )
}

function makeCourseAssistantLocalMessage(
  conversationId: string,
  role: 'user' | 'assistant',
  content: string,
  prefix = 'pending-course-assistant',
): LearningConversationMessage {
  return {
    id: `${prefix}-${role}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    conversationId,
    role,
    content,
    createdAt: new Date().toISOString(),
    fallbackUsed: prefix.startsWith('fallback'),
  }
}

async function ensureCourseAssistantConversation(question: string) {
  const course = selectedCourse.value
  const studentProfileId = activeStudentProfile.value?.id
  if (!course || !studentProfileId) throw new Error('课程或学生画像未加载。')
  if (courseAssistantConversation.value?.courseId === course.id) return courseAssistantConversation.value.id
  const existingRows = sortConversationsByActivity(await learningApi.conversations({ studentProfileId, courseId: course.id, archived: false }))
  const existing = existingRows[0]
  if (existing) {
    courseAssistantConversation.value = existing
    courseAssistantMessages.value = filterReadableCourseAssistantMessages(await learningApi.conversationMessages(existing.id))
    return existing.id
  }
  const conversation = await learningApi.createConversation({
    studentProfileId,
    courseId: course.id,
    title: `${course.title}：${compact(question, 28)}`,
  })
  courseAssistantConversation.value = conversation
  courseAssistantMessages.value = []
  return conversation.id
}

function courseSourceKind(course: Course) {
  const titleAndDepartment = `${course.title} ${course.department}`
  const description = course.description || ''
  const isSelfBuilt =
    titleAndDepartment.includes('自建') ||
    titleAndDepartment.includes('自定义') ||
    titleAndDepartment.includes('个人课程') ||
    course.title.includes('AI 个性化学习智能体实践') ||
    description.includes('由上传资料生成')
  return isSelfBuilt ? 'self' : 'classroom'
}

function getCourseNextTask(course: Course, index: number) {
  const title = course.title
  if (title.includes('Java') || index === 0) return '第 3 章 数据访问与持久化 练习'
  if (title.includes('AI') || index === 1) return '智能体设计与评估 实验报告'
  if (title.includes('工程') || index === 2) return '课程项目立项与计划书编写'
  return '第 3 章 算法基础 章节测评'
}

function getCourseRecentLabel(course?: Course | null, index = 0) {
  if (!course?.updatedAt) return ['今天 10:25', '昨天 16:40', '06/04 20:05', '06/03 11:20'][index % 4]
  const formatted = formatDate(course.updatedAt)
  if (formatted === '-') return ['今天 10:25', '昨天 16:40', '06/04 20:05', '06/03 11:20'][index % 4]
  return formatted.replace(/\//g, '/').slice(5, 16)
}

function downloadCourse() {
  if (!canDownloadCourse.value || !selectedCourse.value) return
  const course = selectedCourse.value
  const lines = [
    `# ${course.title} 课程清单`,
    '',
    `- 院系：${course.department}`,
    `- 学时：${course.creditHours}`,
    `- 更新时间：${formatDate(course.updatedAt)}`,
    '',
    '## 课程简介',
    cleanDisplayText(course.description),
    '',
    '## 知识点',
    ...(selectedKnowledgePoints.value.length ? selectedKnowledgePoints.value.map((item) => `- ${item}`) : ['- 暂无知识点']),
    '',
    '## 学习资源',
    ...(resources.value.length
      ? resources.value.map((resource) => `- ${resource.title}：${resource.resourceTypeName || resource.resourceType} / ${resource.modality}`)
      : ['- 暂无学习资源']),
  ]
  downloadText(`${safeFilePart(course.title)}-course.md`, lines.join('\n'), 'text/markdown;charset=utf-8')
}

function downloadResource(resource: LearningResource) {
  downloadText(`${safeFilePart(resource.title)}.md`, resource.content || '', 'text/markdown;charset=utf-8')
}

function downloadSelectedResource() {
  if (!selectedResource.value) return
  downloadResource(selectedResource.value)
}

function reviewStatusLabel(status?: string | null) {
  const value = String(status || '').toUpperCase()
  if (value === 'PUBLISHED') return '已发布'
  if (value === 'READY_TO_PUBLISH') return '可发布'
  if (value === 'REVIEW_REQUIRED') return '需复核'
  if (value === 'REVIEWING') return '审核中'
  return value || '待审核'
}

function reviewStatusTone(status?: string | null): 'ok' | 'warn' | 'danger' | 'info' | 'muted' {
  const value = String(status || '').toUpperCase()
  if (value === 'PUBLISHED') return 'ok'
  if (value === 'READY_TO_PUBLISH') return 'info'
  if (value === 'REVIEW_REQUIRED') return 'warn'
  if (value === 'REVIEWING') return 'muted'
  return 'muted'
}

watch(
  () => app.activeCourseId,
  async (courseId) => {
    const course = courses.value.find((item) => item.id === courseId)
    if (course && selectedCourse.value?.id !== course.id) await selectCourse(course, false)
  },
)

watch(
  () => route.params.courseId,
  async (courseId) => {
    if (!isTeacher.value && courseId && activeCourseTab.value === 'overview') activeCourseTab.value = 'path'
    const course = courses.value.find((item) => item.id === String(courseId || ''))
    if (course && selectedCourse.value?.id !== course.id) await selectCourse(course, false)
  },
)

// 支持从外部（如今日学习的老师任务）通过 ?tab=tasks 直接定位到课程任务等分区
watch(
  () => route.query.tab,
  (tab) => {
    const allowed = ['overview', 'resources', 'path', 'tasks', 'assistant', 'records']
    const value = String(tab || '')
    if (isStudentCourseDetail.value && allowed.includes(value)) {
      activeCourseTab.value = value as typeof activeCourseTab.value
      if (value === 'tasks') void loadCourseTasks()
    }
  },
  { immediate: true },
)

onMounted(loadCourses)
</script>

<template>
  <div v-if="isCourseIndex" class="student-course-page student-courses-index">
    <section class="student-course-index-toolbar" aria-label="课程筛选">
      <nav class="student-course-filter-tabs" aria-label="课程分类">
        <button
          v-for="filter in courseFilters"
          :key="filter.key"
          type="button"
          :class="{ active: courseFilter === filter.key }"
          @click="setCourseFilter(filter.key)"
        >
          {{ filter.label }}
        </button>
      </nav>
      <label class="student-course-search">
        <Search :size="20" />
        <input v-model="courseSearchKeyword" type="search" placeholder="搜索课程名称" />
      </label>
      <div class="student-course-toolbar-actions">
        <button class="ghost-button" type="button" @click="openJoinClassDialog"><BookOpenCheck :size="17" />加入班级</button>
        <RouterLink class="button" to="/course-builder"><Plus :size="18" />创建自建课程</RouterLink>
      </div>
    </section>

    <section v-if="joinDialogOpen" class="notice span-12" aria-label="加入班级课程">
      <span>输入班级码或课程关键词，系统会在现有班级课程中匹配并加入。</span>
      <div class="button-row">
        <input v-model="classCodeInput" type="text" placeholder="例如：Java Web / course-id" @keyup.enter="joinClassCourse" />
        <button class="button" type="button" @click="joinClassCourse">确认加入</button>
        <button class="ghost-button" type="button" @click="joinDialogOpen = false">取消</button>
      </div>
    </section>
    <p v-if="courseActionFeedback" class="notice span-12">{{ courseActionFeedback }}</p>

    <div class="student-course-index-layout">
      <section class="student-course-card-area" aria-label="我的课程列表">
        <ErrorNotice :message="error" />
        <LoadingBlock :show="loading" />
        <div v-if="!filteredCourseCards.length && !loading" class="empty-guide student-course-empty">
          <strong>{{ courseFilter === 'archived' ? '还没有已归档课程' : '没有找到匹配课程' }}</strong>
          <span>{{ courseFilter === 'archived' ? '完成学习后归档的课程会显示在这里。' : '换一个分类或关键词继续查找。' }}</span>
        </div>
        <div v-else class="student-course-card-grid">
          <article
            v-for="item in filteredCourseCards"
            :key="item.course.id"
            :class="['student-product-course-card', `tone-${item.visualTone}`]"
          >
            <button
              class="course-card-more"
              type="button"
              :aria-expanded="activeMoreCourseId === item.course.id"
              :aria-label="`${item.course.title} 更多课程操作`"
              @click.stop="toggleCourseMore(item.course)"
            >
              <MoreVertical :size="19" />
              <span>更多</span>
            </button>
            <div v-if="activeMoreCourseId === item.course.id" class="course-card-menu" role="menu">
              <button type="button" role="menuitem" @click="continueCourseFromCard(item.course)">继续学习</button>
              <button type="button" role="menuitem" @click="addCourseToPath(item.course)">加入路径</button>
              <button type="button" role="menuitem" @click="askCourseFromCard(item.course)">基于本课提问</button>
              <button type="button" role="menuitem" @click="closeCourseMore">关闭菜单</button>
            </div>
            <div class="course-card-visual">
              <span>{{ item.source === 'self' ? '自建课程' : '班级课程' }}</span>
              <h3>{{ item.course.title }}</h3>
              <p>{{ item.source === 'self' ? '个人课程' : '李老师' }} · {{ item.course.department || '通识教育' }} · {{ item.course.creditHours }} 学时</p>
            </div>
            <div class="course-card-progress-row">
              <span>进度 <strong>{{ item.progress }}%</strong></span>
              <div class="student-progress-track"><i :style="{ width: `${item.progress}%` }"></i></div>
              <small>已完成 {{ item.completedModules }}/{{ item.totalModules }} 模块</small>
              <ArrowRight :size="15" />
            </div>
            <div class="course-card-next-task">
              <CheckCircle2 :size="16" />
              <span>下一项任务：</span>
              <strong>{{ item.nextTask }}</strong>
            </div>
            <footer class="course-card-footer">
              <span>最近更新： {{ item.recentLabel }}</span>
              <button type="button" @click="openCourse(item.course)">进入课程</button>
            </footer>
          </article>
        </div>
      </section>

      <aside class="student-course-activity-panel" aria-label="课程动态">
        <header>
          <h2>课程动态</h2>
          <button v-if="hasReadableCourseActivities" class="activity-clear-button" type="button" @click="clearReadCourseActivities">
            清除已读
          </button>
        </header>
        <section
          v-for="group in courseActivityGroups"
          :key="group.key"
          :class="['course-activity-group', `tone-${group.tone}`]"
        >
          <h3>
            <span class="activity-icon">
              <Bot v-if="group.key === 'ai'" :size="18" />
              <ClipboardList v-else-if="group.key === 'todo'" :size="18" />
              <BookOpenCheck v-else :size="18" />
            </span>
            {{ group.title }}
            <em v-if="group.badge">{{ group.badge }}</em>
          </h3>
          <RouterLink
            v-for="activity in group.items"
            :key="`${group.key}-${activity.title}`"
            :to="getActivityRoute(activity, group)"
            class="activity-item"
          >
            <strong style="min-width: 0;">{{ activity.title }}</strong>
            <time>{{ activity.time }}</time>
            <small style="min-width: 0;">{{ activity.course }}</small>
          </RouterLink>
        </section>
        <div v-if="!courseActivityGroups.length && !courseActivityLoading" class="empty-guide">
          <strong>暂无课程动态</strong>
          <span>老师发布资源或作业后会显示在这里。</span>
        </div>
      </aside>
    </div>
  </div>

  <div
    v-else-if="isStudentCourseDetail"
    class="student-course-page student-course-detail-page"
    :class="{ 'is-course-assistant-mode': activeCourseTab === 'assistant' }"
  >
    <nav class="student-course-breadcrumb" aria-label="课程位置">
      <RouterLink to="/courses">我的课程</RouterLink>
      <span>/</span>
      <strong>{{ selectedCourse?.title || '课程详情' }}</strong>
    </nav>
    <p v-if="courseActionFeedback" class="notice span-12">{{ courseActionFeedback }}</p>

    <section class="student-course-detail-hero" aria-label="课程详情头图">
      <div class="student-course-cover">
        <img :src="moduleCourseCover" :alt="selectedCourse?.title || '课程头图'" />
      </div>
      <div class="student-course-detail-copy">
        <h2>{{ selectedCourse?.title || '请选择课程' }}</h2>
        <p>{{ selectedCourse?.department || '班级课程' }} · {{ selectedCourse && courseSourceKind(selectedCourse) === 'self' ? '自建课程' : '班级课程' }} · {{ selectedCourse?.creditHours || 0 }} 学时</p>
        <div class="student-course-metrics">
          <article v-for="metric in selectedCourseDetailMetrics" :key="metric.key">
            <span class="metric-icon">
              <Clock v-if="metric.icon === 'progress'" :size="26" />
              <Calendar v-else-if="metric.icon === 'modules'" :size="26" />
              <CheckCircle2 v-else-if="metric.icon === 'todo'" :size="26" />
              <ClipboardList v-else :size="26" />
            </span>
            <div>
              <small>{{ metric.label }}</small>
              <strong>{{ metric.value }}</strong>
              <em>{{ metric.detail }}</em>
            </div>
          </article>
        </div>
      </div>
      <aside class="student-course-detail-actions" aria-label="课程操作">
        <button class="button primary-detail-action" type="button" @click="continueLearning">
          <Play :size="18" />继续学习
        </button>
        <RouterLink class="ghost-button" :to="courseProjectRoute"><Sparkles :size="18" />进入完整 AI 项目空间</RouterLink>
        <button class="ghost-button" type="button" @click="showCourseResources"><FolderOpen :size="18" />查看资料库</button>
      </aside>
    </section>

    <nav class="student-course-detail-tabs" aria-label="课程详情分区">
      <button
        v-for="tab in courseDetailTabs"
        :key="tab.key"
        type="button"
        :class="{ active: activeCourseTab === tab.key }"
        @click="openCourseTab(tab.key)"
      >
        {{ tab.label }}
      </button>
    </nav>

    <section v-if="activeCourseTab === 'path'" class="student-course-overview-grid" :style="pathGridStyle" aria-label="学习路径">
      <article class="detail-path-card">
        <header>
          <h3>学习路径</h3>
          <button type="button" @click="showCoursePath">查看学习指南 <ArrowRight :size="15" /></button>
        </header>
        <div class="detail-path-list">
          <button
            v-for="(item, index) in detailPathItems"
            :key="item.key"
            type="button"
            :class="{ active: item.key === selectedPathActiveKey }"
            :aria-pressed="item.key === selectedPathActiveKey"
            data-testid="course-path-item"
            @click="openPathItem(item, index)"
          >
            <span class="path-index">{{ index + 1 }}</span>
            <span class="path-type">{{ item.type }}</span>
            <strong>{{ item.title }}</strong>
            <small><Clock :size="13" />{{ item.minutes }} 分钟</small>
            <em>{{ item.progress }}</em>
          </button>
          <div v-if="!detailPathItems.length" class="empty-guide">
            <strong>暂无学习路径</strong>
            <span>基于你的画像与本课程，由 AI 生成个性化学习路径。</span>
            <button class="button" type="button" :disabled="generatingPath" @click="generateLearningPath">
              {{ generatingPath ? '生成中…' : '生成学习路径' }}
            </button>
          </div>
        </div>
      </article>

      <div
        class="panel-resizer"
        role="separator"
        aria-orientation="vertical"
        title="拖动调整宽度，双击恢复默认"
        @pointerdown="pathStartResize(0, $event)"
        @dblclick="pathResetLayout()"
      ></div>

      <article class="detail-resource-card">
        <header>
          <h3>AI 推荐学习资源</h3>
          <button type="button" @click="showCourseResources">全部资源 <ArrowRight :size="15" /></button>
        </header>
        <div class="detail-resource-sections">
          <section v-for="section in resourcePreviewSections" :key="section.key">
            <header class="resource-section-head">
              <h4>{{ section.title }}</h4>
            </header>
            <div class="detail-resource-grid">
              <button
                v-for="item in section.items"
                :key="item.id"
                type="button"
                class="resource-reco-card"
                :class="`is-${item.status}`"
                data-testid="resource-reco-card"
                @click="openResourceRecommendation(item)"
              >
                <span class="resource-reco-icon"><FileText :size="20" /></span>
                <span class="resource-reco-copy">
                  <strong>{{ item.title }}</strong>
                  <small>{{ item.subtitle }}</small>
                </span>
                <span class="resource-reco-meta">{{ item.source }} · {{ item.minutes }} 分钟</span>
                <em>{{ item.action }}</em>
              </button>
            </div>
          </section>
        </div>
        <div class="detail-inline-assistant">
          <Bot :size="24" />
          <div>
            <strong>课程 AI 助教</strong>
          </div>
          <button type="button" @click="openCourseTab('assistant')">打开本课助教</button>
        </div>
      </article>

      <div
        class="panel-resizer"
        role="separator"
        aria-orientation="vertical"
        title="拖动调整宽度，双击恢复默认"
        @pointerdown="pathStartResize(1, $event)"
        @dblclick="pathResetLayout()"
      ></div>

      <aside class="detail-right-column">
        <article class="detail-profile-card">
          <header>
            <h3>本课画像摘要</h3>
            <RouterLink to="/profiles">查看详情 <ArrowRight :size="14" /></RouterLink>
          </header>
          <div class="profile-ring">
            <strong>61%</strong>
            <small>中等</small>
          </div>
          <div class="profile-signal-list">
            <div v-for="signal in profileSignals" :key="signal.label">
              <span>{{ signal.label }}</span>
              <i><b :style="{ width: signal.value }"></b></i>
              <em>{{ signal.value }}</em>
            </div>
          </div>
          <footer>
            <span>证据数量 <strong>18 条</strong></span>
            <span>最近变化 <strong>↑ 9%</strong></span>
          </footer>
        </article>
      </aside>
    </section>

    <section v-else-if="activeCourseTab === 'resources'" class="student-resource-tab-panel">
      <article v-for="resource in resources" :key="resource.id" class="student-resource-row">
        <FileText :size="22" />
        <div>
          <strong>{{ resource.title }}</strong>
          <p>{{ compact(resource.content, 120) }}</p>
        </div>
        <StatusPill :status="resource.resourceTypeName || resource.resourceType" tone="info" />
        <button class="ghost-button" type="button" @click="openResourcePreview(resource)">预览</button>
        <button class="ghost-button" type="button" @click="addResourceToPath(resource)">加入路径</button>
      </article>
      <div v-if="!resources.length" class="empty-guide">
        <strong>暂无章节资源</strong>
      </div>
    </section>

    <section v-else-if="activeCourseTab === 'tasks'" class="student-task-tab-panel">
      <div v-if="!activeCourseTask" class="course-task-list">
        <article
          v-for="task in courseTasks"
          :key="task.id"
          class="course-task-card"
          :class="{ done: taskSubmission(task.id) }"
        >
          <span class="course-task-icon">
            <ClipboardList v-if="task.type === 'quiz'" :size="20" />
            <FileText v-else :size="20" />
          </span>
          <div class="course-task-main">
            <div class="course-task-title-row">
              <strong>{{ task.title }}</strong>
              <em class="course-task-type">{{ task.type === 'quiz' ? '测试' : '作业' }}</em>
            </div>
            <p>{{ task.description }}</p>
            <div class="course-task-meta">
              <span>{{ task.publisher }} 发布</span>
              <span><Clock :size="13" /> {{ task.estimatedMinutes }} 分钟</span>
              <span>{{ task.deadlineLabel }}</span>
            </div>
          </div>
          <div class="course-task-action">
            <span v-if="taskSubmission(task.id)" class="course-task-status">
              <CheckCircle2 :size="15" />
              {{ taskSubmission(task.id)?.total ? `已提交 ${taskSubmission(task.id)?.score}/${taskSubmission(task.id)?.total}` : '已提交' }}
            </span>
            <button type="button" @click="openCourseTask(task)">
              {{ taskSubmission(task.id) ? '查看' : (task.type === 'quiz' ? '开始测试' : '去完成') }}
            </button>
          </div>
        </article>
        <div v-if="!courseTasks.length" class="empty-guide"><strong>暂无课程任务</strong></div>
      </div>
<!-- TASK_DETAIL_ANCHOR -->
      <div v-else class="course-task-detail">
        <header class="course-task-detail-head">
          <button type="button" class="ghost-button" @click="closeCourseTask"><ArrowRight :size="15" style="transform: rotate(180deg)" /> 返回任务列表</button>
          <em class="course-task-type">{{ activeCourseTask.type === 'quiz' ? '测试' : '作业' }}</em>
        </header>
        <h3>{{ activeCourseTask.title }}</h3>
        <p class="course-task-detail-desc">{{ activeCourseTask.description }}</p>
        <div class="course-task-meta">
          <span>{{ activeCourseTask.publisher }} 发布</span>
          <span><Clock :size="13" /> 预计 {{ activeCourseTask.estimatedMinutes }} 分钟</span>
          <span>{{ activeCourseTask.deadlineLabel }}</span>
        </div>

        <div v-if="activeCourseTask.type === 'quiz'" class="course-quiz-body">
          <article v-for="(q, qi) in activeCourseTask.questions" :key="q.id" class="course-quiz-question">
            <strong>{{ qi + 1 }}. {{ q.stem }}</strong>
            <button
              v-for="(opt, oi) in q.options"
              :key="oi"
              type="button"
              class="course-quiz-option"
              :class="{ selected: taskQuizAnswers[q.id] === oi, correct: taskSubmission(activeCourseTask.id) && oi === q.answer, wrong: taskSubmission(activeCourseTask.id) && taskQuizAnswers[q.id] === oi && oi !== q.answer }"
              :disabled="Boolean(taskSubmission(activeCourseTask.id))"
              @click="selectQuizOption(q.id, oi)"
            >
              <span class="course-quiz-marker">{{ String.fromCharCode(65 + oi) }}</span>
              {{ opt }}
            </button>
          </article>
        </div>

        <div v-else class="course-homework-body">
          <label>作答内容</label>
          <textarea
            v-model="taskAnswerDraft"
            :readonly="Boolean(taskSubmission(activeCourseTask.id))"
            placeholder="在此撰写作业内容，或粘贴报告正文…"
            rows="10"
          ></textarea>
        </div>

        <footer class="course-task-detail-foot">
          <span v-if="taskSubmission(activeCourseTask.id)" class="course-task-status">
            <CheckCircle2 :size="16" /> 已于 {{ formatDate(taskSubmission(activeCourseTask.id)?.submittedAt) }} 提交
            <template v-if="taskSubmission(activeCourseTask.id)?.total">· 得分 {{ taskSubmission(activeCourseTask.id)?.score }}/{{ taskSubmission(activeCourseTask.id)?.total }}</template>
          </span>
          <button v-else class="button" type="button" :disabled="!canSubmitCourseTask" @click="submitCourseTask">
            <Send :size="16" /> 提交{{ activeCourseTask.type === 'quiz' ? '答卷' : '作业' }}
          </button>
        </footer>
      </div>
    </section>

    <section v-else-if="activeCourseTab === 'assistant'" class="student-course-ai-panel">
      <div class="course-ai-thread-preview">
        <div class="course-ai-avatar"><Bot :size="22" /></div>
        <article>
          <strong>{{ selectedCourse?.title || '当前课程' }} AI 助教</strong>
        </article>
      </div>
      <div class="course-ai-chat-grid">
        <div class="course-ai-thread">
          <article v-if="!courseAssistantMessages.length" class="course-ai-empty">
            <strong>直接问本课内容</strong>
          </article>
          <article
            v-for="message in courseAssistantMessages"
            :key="message.id"
            class="course-ai-turn"
            :class="message.role === 'user' ? 'is-user' : 'is-ai'"
          >
            <span>{{ message.role === 'user' ? '你' : 'AI' }}</span>
            <div>
              <header>
                <strong>{{ message.role === 'user' ? '你的问题' : '课程 AI 助教' }}</strong>
                <small>{{ formatDate(message.createdAt) }}</small>
              </header>
              <MarkdownView v-if="message.role === 'assistant'" :content="message.content" />
              <p v-else>{{ message.content }}</p>
            </div>
          </article>
          <article v-if="courseAssistantLoading && !hasCourseAssistantPendingResponse" class="course-ai-turn is-ai is-loading">
            <span>AI</span>
            <div>
              <header><strong>课程 AI 助教</strong></header>
              <p>正在生成回答...</p>
            </div>
          </article>
        </div>
        <aside class="course-ai-summary-card">
          <strong>本轮疑惑</strong>
          <p>{{ courseAssistantDoubtSummary.question }}</p>
        </aside>
      </div>
      <p v-if="courseAssistantError" class="notice error">{{ courseAssistantError }}</p>
      <form class="course-ai-mini-composer" @submit.prevent="askCurrentCourse()">
        <textarea
          v-model="courseAssistantDraft"
          placeholder="例如：这个知识点和前后章节有什么关系？我应该先掌握哪一步？"
          @keydown.enter.exact.prevent="askCurrentCourse()"
        />
        <div>
          <button type="button" :disabled="courseAssistantLoading" @click="courseAssistantDraft = selectedCourseCardStats.nextLesson">当前模块</button>
          <button class="button" type="submit" :disabled="courseAssistantLoading">
            <ArrowRight :size="17" />{{ courseAssistantLoading ? '思考中...' : '发送' }}
          </button>
        </div>
      </form>
    </section>
  </div>

  <div v-else class="page-grid">
    <section class="dashboard-workbench course-workbench span-12">
      <div class="dashboard-workbench-head">
        <div>
          <h2>{{ courseHeaderTitle }}</h2>
        </div>
        <div class="home-action-row">
          <RouterLink v-if="isTeacher" class="button" to="/course-builder"><UploadCloud :size="17" />新建课程</RouterLink>
          <RouterLink v-else class="button" :to="courseAssistantRoute"><BookOpenCheck :size="17" />开始学习</RouterLink>
          <RouterLink class="ghost-button" :to="courseGenerateRoute"><Sparkles :size="17" />{{ isTeacher ? '生成资源' : '在 AI 助手生成' }}</RouterLink>
          <button class="ghost-button" type="button" @click="loadCourses"><RefreshCw :size="17" />刷新</button>
        </div>
      </div>

      <div class="course-command-band">
        <nav class="course-switch-rail" aria-label="课程切换">
          <button
            v-for="(course, index) in courseSwitchCards"
            :key="course.id"
            type="button"
            :class="{ active: course.active }"
            @click="openCourse(course)"
          >
            <span class="course-switch-index">{{ index + 1 }}</span>
            <span class="course-switch-copy">
              <strong>{{ course.title }}</strong>
              <small>{{ course.department }} · {{ course.creditHours }} 学时</small>
            </span>
            <StatusPill :status="course.active ? '当前' : '切换'" :tone="course.active ? 'ok' : 'muted'" />
          </button>
        </nav>

        <div class="course-product-board" aria-label="课程资源工作区">
          <div class="course-product-main">
            <span>{{ isTeacher ? '教师课程工作区' : '学生课程工作区' }}</span>
            <h3>{{ selectedCourse?.title || '请选择课程' }}</h3>
            <div class="builder-context-strip">
              <span>{{ selectedCourse?.department || '课程归属' }}</span>
              <span>{{ selectedKnowledgePoints.length }} 个知识点</span>
              <span>{{ resources.length }} 个学习资源</span>
            </div>
          </div>
          <div class="course-work-queue">
            <div v-for="item in courseWorkItems" :key="item.label">
              <small>{{ item.label }}</small>
              <strong>{{ item.value }}</strong>
              <span>{{ item.detail }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="courseware-workspace span-12" aria-label="课程学习工作区">
      <nav class="course-detail-tabs" aria-label="课程详情分区">
        <button
          v-for="tab in courseDetailTabs"
          :key="tab.key"
          type="button"
          :class="{ active: activeCourseTab === tab.key }"
          @click="openCourseTab(tab.key)"
        >
          <span>{{ tab.label }}</span>
          <small>{{ tab.count }}</small>
        </button>
      </nav>

      <div v-if="activeCourseTab === 'overview'" class="course-overview-surface">
        <img :src="moduleCourseCover" alt="" aria-hidden="true" />
        <div>
          <span>{{ isTeacher ? '教师课程空间' : '我的课程详情' }}</span>
          <h2>{{ selectedCourse?.title || '请选择课程' }}</h2>
          <div class="course-overview-metrics">
            <article v-for="item in courseWorkItems" :key="item.label">
              <small>{{ item.label }}</small>
              <strong>{{ item.value }}</strong>
              <span>{{ item.detail }}</span>
            </article>
          </div>
        </div>
      </div>

      <div v-else-if="activeCourseTab === 'assistant'" class="course-assistant-surface">
        <div>
          <span>课程内 AI 助教</span>
          <h2>{{ selectedCourse?.title || '当前课程' }} 助教</h2>
        </div>
        <div class="course-assistant-actions">
          <RouterLink class="button" :to="courseAssistantRoute"><BookOpenCheck :size="17" />进入本课对话</RouterLink>
          <RouterLink class="ghost-button" :to="courseGenerateRoute"><Sparkles :size="17" />生成本课资源</RouterLink>
        </div>
      </div>

      <div v-else-if="activeCourseTab === 'records'" class="course-record-surface">
        <div class="course-record-head">
          <div>
            <span>课程内生成记录</span>
            <h2>本课资源生成进度</h2>
          </div>
          <RouterLink class="button" :to="courseGenerateRoute"><Sparkles :size="17" />继续生成</RouterLink>
        </div>
        <div v-if="!courseGenerationRecords.length" class="empty-guide">
          <strong>本课程暂无生成记录</strong>
        </div>
        <div v-else class="course-record-grid">
          <article v-for="task in courseGenerationRecords" :key="task.id">
            <div>
              <StatusPill :status="task.status" :tone="reviewStatusTone(task.status)" />
              <small>{{ task.progressPercent || 0 }}%</small>
            </div>
            <strong>{{ task.topic }}</strong>
            <p>{{ task.currentStep || task.resultSummary || '等待智能体同步生成进度' }}</p>
            <div class="progress-track"><div class="progress-fill" :style="{ width: `${task.progressPercent || 0}%` }" /></div>
            <RouterLink :to="isTeacher ? `/tasks/${task.id}` : { path: '/learning', query: { tab: 'progress', taskId: task.id, courseId: selectedCourse?.id || '' } }">
              {{ isTeacher ? '查看任务详情' : '在 AI 助手查看' }}
            </RouterLink>
          </article>
        </div>
      </div>

      <template v-else>
      <aside class="courseware-outline">
        <div class="courseware-panel-head">
          <div>
            <span>{{ isTeacher ? '课程结构' : '学习单元' }}</span>
            <h3>{{ selectedCourse?.title || '请选择课程' }}</h3>
          </div>
          <strong>{{ courseProgressPercent }}%</strong>
        </div>
        <div class="courseware-progress" aria-hidden="true">
          <span :style="{ width: `${courseProgressPercent}%` }" />
        </div>
        <ErrorNotice :message="error" />
        <LoadingBlock :show="loading" />
        <div v-if="!selectedCourse && !loading" class="empty-guide">
          <strong>请选择课程</strong>
        </div>
        <div v-else-if="!courseOutlineItems.length && !loading" class="empty-guide">
          <strong>课程还没有资源</strong>
          <RouterLink class="button" :to="courseGenerateRoute">{{ isTeacher ? '创建班级资源' : '去 AI 助手生成' }}</RouterLink>
        </div>
        <nav v-else class="courseware-module-list" aria-label="课程单元">
          <button
            v-for="(item, index) in courseOutlineItems"
            :key="item.key"
            type="button"
            :class="{ active: item.resource?.id === selectedResource?.id }"
            :disabled="!item.resource"
            @click="item.resource && (selectedResource = item.resource)"
          >
            <span class="courseware-module-index">{{ index + 1 }}</span>
            <span>
              <strong>{{ item.title }}</strong>
              <small>{{ item.subtitle }}</small>
            </span>
            <StatusPill :status="item.status" :tone="item.resource ? 'info' : 'muted'" />
          </button>
        </nav>
      </aside>

      <article class="courseware-reader">
        <header class="courseware-reader-head">
          <div>
            <span>{{ selectedResourceTypeName }}</span>
            <h2>{{ selectedResource?.title || resourcePanelTitle }}</h2>
          </div>
          <div class="courseware-reader-actions">
            <button class="ghost-button" type="button" @click="loadCourses"><RefreshCw :size="17" />刷新</button>
            <button class="ghost-button" :disabled="!selectedResource" @click="downloadSelectedResource"><Download :size="17" />下载正文</button>
          </div>
        </header>
        <div v-if="selectedResource" class="course-resource-readiness">
          <div>
            <strong>{{ selectedResourceTypeName }}</strong>
            <span>{{ selectedResourceMeta }}</span>
          </div>
          <div>
            <strong>{{ isTeacher ? '发布状态' : '开放状态' }}</strong>
            <StatusPill :status="reviewStatusLabel(selectedResource?.reviewStatus)" :tone="reviewStatusTone(selectedResource?.reviewStatus)" />
          </div>
          <div>
            <strong>学习动作</strong>
            <span>{{ isTeacher ? '复核后发布给学生' : '阅读后进入答疑和测评' }}</span>
          </div>
        </div>
        <div v-if="!selectedResource" class="empty-guide">
          <strong>选择一个学习单元</strong>
        </div>
        <MarkdownView v-if="selectedResourceContent" :content="selectedResourceContent" />
      </article>

      <aside class="courseware-rail">
        <div class="courseware-panel-head compact">
          <div>
            <span>{{ isTeacher ? '发布运营' : '学习动作' }}</span>
            <h3>{{ isTeacher ? '课程开放前检查' : '下一步学习' }}</h3>
          </div>
        </div>
        <div class="courseware-action-stack">
          <div v-for="item in courseActionItems" :key="item.label">
            <small>{{ item.label }}</small>
            <strong>{{ item.value }}</strong>
            <span>{{ item.detail }}</span>
          </div>
        </div>
        <div class="courseware-link-stack">
          <RouterLink class="button" :to="isTeacher ? '/quality' : courseAssistantRoute">
            <BookOpenCheck :size="17" />{{ isTeacher ? '进入发布质检' : '进入 AI 助教' }}
          </RouterLink>
          <RouterLink class="ghost-button" :to="courseGenerateRoute"><Sparkles :size="17" />{{ isTeacher ? '补齐资源' : '在 AI 助手生成' }}</RouterLink>
          <button class="ghost-button" :disabled="!canDownloadCourse" @click="downloadCourse"><Download :size="17" />导出课程清单</button>
        </div>
        <div class="courseware-knowledge-list">
          <strong>知识点</strong>
          <span v-for="point in selectedKnowledgePoints.slice(0, 8)" :key="point">{{ point }}</span>
        </div>
      </aside>
      </template>
    </section>

    <SectionPanel class="span-12 course-archive-panel" :title="resourceListTitle">
      <template #actions>
        <button class="ghost-button" @click="loadCourses"><RefreshCw :size="17" />刷新</button>
        <button class="ghost-button" :disabled="!canDownloadCourse" @click="downloadCourse"><Download :size="17" />导出课程清单</button>
      </template>
      <ErrorNotice :message="error" />
      <LoadingBlock :show="loading" />
      <div class="split-row">
        <div>
          <h3>课程目录</h3>
          <div v-if="!courses.length && !loading" class="empty-guide">
            <strong>暂无课程</strong>
            <span>进入课程建设页上传资料建课，或填写课程表单保存一门课程。</span>
            <RouterLink class="button" to="/course-builder">去建设课程</RouterLink>
          </div>
          <div v-else class="timeline course-list-table">
            <button
              v-for="course in courses"
              :key="course.id"
              class="timeline-body clickable-row course-list-row"
              :class="{ active: selectedCourse?.id === course.id }"
              @click="openCourse(course)"
            >
              <div>
                <strong>{{ course.title }}</strong>
                <p>{{ compact(course.description, 110) }}</p>
              </div>
              <div class="course-list-meta">
                <span>{{ course.department }}</span>
                <span>{{ course.creditHours }} 学时</span>
                <small>{{ formatDate(course.updatedAt) }}</small>
              </div>
              <StatusPill :status="selectedCourse?.id === course.id ? '当前课程' : '可切换'" :tone="selectedCourse?.id === course.id ? 'ok' : 'info'" />
            </button>
          </div>
        </div>
        <div>
          <h3>{{ resourcePanelTitle }}</h3>
          <div v-if="!selectedCourse" class="empty-guide">
            <strong>请选择课程</strong>
            <span>选择课程后查看课程资源。</span>
          </div>
          <div v-else-if="!resources.length" class="empty-guide">
            <strong>暂无资源</strong>
            <span>{{ isTeacher ? '可以为当前课程创建并复核班级资源。' : '当前课程还没有已发布资源，可以先创建资源或等待教师发布。' }}</span>
            <RouterLink class="button" :to="courseGenerateRoute">{{ isTeacher ? '创建班级资源' : '去 AI 助手生成' }}</RouterLink>
          </div>
          <div v-else class="course-resource-library">
            <article v-for="resource in resources" :key="resource.id" class="course-resource-card">
              <div class="course-resource-head">
                <div>
                  <strong>{{ resource.title }}</strong>
                  <p>{{ resource.modality }} / {{ resource.estimatedMinutes }} 分钟</p>
                </div>
                <div class="button-row">
                  <StatusPill :status="resource.resourceTypeName || resource.resourceType" tone="info" />
                  <StatusPill :status="reviewStatusLabel(resource.reviewStatus)" :tone="reviewStatusTone(resource.reviewStatus)" />
                </div>
              </div>
              <p>{{ compact(resource.content, 150) }}</p>
              <small v-if="resource.publishedAt">发布 {{ formatDate(resource.publishedAt) }} / {{ resource.publishedBy || '课程教师' }}</small>
              <div class="button-row">
                <button class="ghost-button" @click="openResourcePreview(resource)">预览</button>
                <button class="ghost-button" @click="downloadResource(resource)"><Download :size="16" />下载正文</button>
              </div>
            </article>
          </div>
        </div>
      </div>
    </SectionPanel>
  </div>
</template>

<style scoped>
:global(html body .app-shell.is-student .student-product-course-card) {
  overflow: visible !important;
}

:global(html body .app-shell.is-student .student-product-course-card .course-card-more) {
  display: inline-flex !important;
  width: auto !important;
  min-width: 72px !important;
  height: 34px !important;
  grid-template-columns: none !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 5px !important;
  padding: 0 10px !important;
  border-radius: 999px !important;
  font-size: 12px !important;
  font-weight: 800 !important;
}

.course-card-menu {
  position: absolute;
  z-index: 8;
  top: 58px;
  right: 16px;
  display: grid;
  min-width: 148px;
  padding: 8px;
  border: 1px solid rgba(15, 23, 42, 0.12);
  border-radius: 10px;
  background: #ffffff;
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.18);
}

.course-card-menu button {
  min-height: 34px;
  border: 0;
  border-radius: 8px;
  background: transparent;
  color: #102a43;
  font-size: 13px;
  font-weight: 750;
  text-align: left;
  cursor: pointer;
}

.course-card-menu button:hover {
  background: rgba(8, 127, 121, 0.1);
  color: #087f79;
}

.resource-chapter-tag {
  display: inline-block;
  margin-left: 8px;
  padding: 2px 10px;
  border-radius: 999px;
  background: rgba(8, 127, 121, 0.1);
  color: #087f79;
  font-size: 12px;
  font-weight: 700;
  vertical-align: middle;
}

/* ===== 课程任务（作业/测试） ===== */
.student-task-tab-panel {
  padding: 8px 4px;
}
.course-task-list {
  display: grid;
  gap: 14px;
}
.course-task-card {
  display: grid;
  grid-template-columns: 44px minmax(0, 1fr) auto;
  gap: 14px;
  align-items: center;
  padding: 16px 18px;
  background: #fff;
  border: 1px solid #dbe8ef;
  border-radius: 14px;
}
.course-task-card.done {
  background: #f6fdfb;
  border-color: #bfe9e2;
}
.course-task-icon {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  border-radius: 11px;
  background: rgba(8, 127, 121, 0.1);
  color: #087f79;
}
.course-task-main {
  min-width: 0;
}
.course-task-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.course-task-title-row strong {
  font-size: 15px;
  color: #102a43;
}
.course-task-type {
  padding: 1px 8px;
  border-radius: 999px;
  background: rgba(138, 92, 246, 0.12);
  color: #6d3fd6;
  font-size: 11px;
  font-style: normal;
  font-weight: 700;
}
.course-task-main p {
  margin: 4px 0 6px;
  color: #5a6f82;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.course-task-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  color: #8094a6;
  font-size: 12px;
}
.course-task-meta span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.course-task-action {
  display: grid;
  gap: 6px;
  justify-items: end;
}
.course-task-action button {
  padding: 8px 16px;
  border: 0;
  border-radius: 9px;
  background: #087f79;
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}
.course-task-status {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: #0a8a72;
  font-size: 12px;
  font-weight: 600;
}

.course-task-detail {
  display: grid;
  gap: 12px;
  max-width: 820px;
  padding: 22px;
  background: #fff;
  border: 1px solid #dbe8ef;
  border-radius: 16px;
}
.course-task-detail-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.course-task-detail h3 {
  margin: 0;
  font-size: 19px;
  color: #102a43;
}
.course-task-detail-desc {
  margin: 0;
  color: #5a6f82;
  font-size: 14px;
}
.course-quiz-body {
  display: grid;
  gap: 18px;
  margin-top: 6px;
}
.course-quiz-question {
  display: grid;
  gap: 8px;
}
.course-quiz-question strong {
  font-size: 14px;
  color: #1e2d3d;
}
.course-quiz-option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: #f7fafc;
  border: 1px solid #dde7ef;
  border-radius: 10px;
  color: #33485c;
  font-size: 14px;
  text-align: left;
  cursor: pointer;
}
.course-quiz-option.selected {
  border-color: #087f79;
  background: rgba(8, 127, 121, 0.08);
}
.course-quiz-option.correct {
  border-color: #1aa179;
  background: rgba(26, 161, 121, 0.12);
}
.course-quiz-option.wrong {
  border-color: #e0604f;
  background: rgba(224, 96, 79, 0.1);
}
.course-quiz-marker {
  display: grid;
  place-items: center;
  width: 24px;
  height: 24px;
  border-radius: 7px;
  background: #fff;
  border: 1px solid #cdd9e3;
  font-size: 12px;
  font-weight: 700;
}
.course-homework-body {
  display: grid;
  gap: 6px;
}
.course-homework-body label {
  font-size: 13px;
  font-weight: 600;
  color: #43586a;
}
.course-homework-body textarea {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #d4e2ea;
  border-radius: 10px;
  font-size: 14px;
  line-height: 1.6;
  resize: vertical;
}
.course-task-detail-foot {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
  margin-top: 6px;
}
</style>
