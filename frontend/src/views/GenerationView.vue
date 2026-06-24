<script setup lang="ts">
import {
  AlertTriangle,
  BookOpenCheck,
  CheckCircle2,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  CircleCheck,
  Clock3,
  Download,
  Eye,
  FileText,
  FlaskConical,
  Info,
  ListChecks,
  Loader2,
  Map as MapIcon,
  Paperclip,
  RefreshCw,
  RotateCcw,
  Send,
  XCircle,
} from 'lucide-vue-next'
import { computed, markRaw, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { coursesApi, tasksApi } from '@/api'
import { useAppStore } from '@/stores/app'
import type { Course, GenerationTask } from '@/types/api'

type PublishStatus = 'pending' | 'revision' | 'ready' | 'published'
type ResourceKind = 'all' | 'courseware' | 'practice' | 'mindmap' | 'lab' | 'reading'
type PreviewTab = 'courseware' | 'practice' | 'mindmap' | 'evidence' | 'logs'
type ActionKind = 'export' | 'regenerate' | 'reject' | 'revise' | 'publish' | ''

interface StatusOption {
  key: PublishStatus
  label: string
  tone: 'info' | 'warn' | 'ok' | 'muted'
}

interface KindOption {
  key: ResourceKind
  label: string
}

interface ReleaseCheck {
  id: string
  title: string
  description: string
  status: 'pass' | 'warn' | 'partial'
  detail?: string
  bullets?: string[]
}

interface PublishTask {
  id: string
  backendTaskId?: string
  title: string
  courseId: string
  courseName: string
  chapter: string
  kind: Exclude<ResourceKind, 'all'>
  kindLabel: string
  assetCount: number
  progress: number
  status: PublishStatus
  savedAt: string
  version: string
  summary: string
  checks: ReleaseCheck[]
  logs: string[]
}

interface ToastState {
  tone: 'ok' | 'warn' | 'info'
  message: string
}

const app = useAppStore()
const route = useRoute()

const loading = ref(false)
const actionLoading = ref<ActionKind>('')
const toast = ref<ToastState | null>(null)
const courses = ref<Course[]>([])
const tasks = ref<PublishTask[]>([])
const selectedCourseId = ref('')
const selectedStatus = ref<PublishStatus>('pending')
const selectedKind = ref<ResourceKind>('all')
const selectedTaskId = ref('')
const activeTab = ref<PreviewTab>('courseware')
const currentPage = ref(1)
const pageSize = ref(8)
const lastSavedAt = ref('今天 15:08')

const fallbackCourses: Course[] = [
  {
    id: 'java-web',
    title: 'Java Web 应用开发与软件工程实践',
    department: '计算机科学与技术',
    description: '面向软件工程 2024-01 的班级课程。',
    creditHours: 48,
    syllabusJson: '',
    createdAt: '',
    updatedAt: '',
  },
  {
    id: 'data-structure',
    title: '数据结构与算法',
    department: '软件工程',
    description: '面向软件工程 2024-01 的班级课程。',
    creditHours: 56,
    syllabusJson: '',
    createdAt: '',
    updatedAt: '',
  },
  {
    id: 'os-principle',
    title: '操作系统原理',
    department: '计算机科学与技术',
    description: '面向软件工程 2024-01 的班级课程。',
    creditHours: 40,
    syllabusJson: '',
    createdAt: '',
    updatedAt: '',
  },
]

const statusOptions: StatusOption[] = [
  { key: 'pending', label: '待检查', tone: 'info' },
  { key: 'revision', label: '需修改', tone: 'warn' },
  { key: 'ready', label: '可发布', tone: 'ok' },
  { key: 'published', label: '已发布', tone: 'muted' },
]

const kindOptions: KindOption[] = [
  { key: 'all', label: '全部' },
  { key: 'courseware', label: '课件' },
  { key: 'practice', label: '练习' },
  { key: 'mindmap', label: '导图' },
  { key: 'lab', label: '实验指导' },
  { key: 'reading', label: '拓展阅读' },
]

const previewTabs: Array<{ key: PreviewTab; label: string }> = [
  { key: 'courseware', label: '课件正文' },
  { key: 'practice', label: '练习题' },
  { key: 'mindmap', label: '思维导图' },
  { key: 'evidence', label: '引用证据' },
  { key: 'logs', label: '生成日志' },
]

const kindMeta: Record<Exclude<ResourceKind, 'all'>, { icon: unknown; className: string }> = {
  courseware: { icon: markRaw(FileText), className: 'blue' },
  practice: { icon: markRaw(ListChecks), className: 'green' },
  mindmap: { icon: markRaw(MapIcon), className: 'violet' },
  lab: { icon: markRaw(FlaskConical), className: 'orange' },
  reading: { icon: markRaw(BookOpenCheck), className: 'cyan' },
}

const selectedCourse = computed(() => courses.value.find((course) => course.id === selectedCourseId.value) ?? courses.value[0])
const statusCounts = computed(() =>
  statusOptions.reduce(
    (record, item) => {
      record[item.key] = tasks.value.filter((task) => task.courseId === selectedCourseId.value && task.status === item.key).length
      return record
    },
    {} as Record<PublishStatus, number>,
  ),
)
const filteredTasks = computed(() =>
  tasks.value.filter((task) => {
    const matchCourse = task.courseId === selectedCourseId.value
    const matchStatus = task.status === selectedStatus.value
    const matchKind = selectedKind.value === 'all' || task.kind === selectedKind.value
    return matchCourse && matchStatus && matchKind
  }),
)
const totalPages = computed(() => Math.max(1, Math.ceil(filteredTasks.value.length / pageSize.value)))
const pagedTasks = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredTasks.value.slice(start, start + pageSize.value)
})
const selectedTask = computed(() => tasks.value.find((task) => task.id === selectedTaskId.value) ?? filteredTasks.value[0] ?? tasks.value[0])
const checkSummary = computed(() => {
  const checks = selectedTask.value?.checks ?? []
  return {
    pass: checks.filter((item) => item.status === 'pass').length,
    warn: checks.filter((item) => item.status === 'warn').length,
    partial: checks.filter((item) => item.status === 'partial').length,
  }
})
const releaseConclusion = computed(() => {
  if (!selectedTask.value) return '暂无选中的待发布资源。'
  if (checkSummary.value.warn > 0) return '建议修正警告项后发布，或确认无误后直接发布。'
  if (checkSummary.value.partial > 0) return '还有部分项目需要补齐，可要求修改后再次检查。'
  return '资源通过检查，可以发布给当前班级。'
})
const resourcePreviewTitle = computed(() => {
  const task = selectedTask.value
  if (!task) return '资源预览'
  const title = task.title.startsWith(task.chapter) ? task.title : `${task.chapter} ${task.title}`
  return `资源预览：${title}`
})
const currentKindIcon = computed(() => (selectedTask.value ? kindMeta[selectedTask.value.kind].icon : FileText))
const activeCoursePublishable = computed(() => tasks.value.filter((task) => task.courseId === selectedCourseId.value && task.status === 'ready').length)

watch([selectedCourseId, selectedStatus, selectedKind], () => {
  currentPage.value = 1
  selectedTaskId.value = filteredTasks.value[0]?.id ?? ''
})

watch(filteredTasks, (items) => {
  if (!items.some((item) => item.id === selectedTaskId.value)) selectedTaskId.value = items[0]?.id ?? ''
})

watch(toast, (value) => {
  if (!value) return
  window.setTimeout(() => {
    toast.value = null
  }, 2600)
})

onMounted(async () => {
  await loadPageData()
})

async function loadPageData() {
  loading.value = true
  try {
    const [loadedCourses, loadedTasks] = await Promise.all([
      coursesApi.list().then((items) => items as Course[]).catch(() => [] as Course[]),
      tasksApi.list().then((items) => items as GenerationTask[]).catch(() => [] as GenerationTask[]),
    ])
    courses.value = mergeCourses(loadedCourses)
    const queryCourseId = typeof route.query.courseId === 'string' ? route.query.courseId : ''
    selectedCourseId.value =
      (queryCourseId && courses.value.some((course) => course.id === queryCourseId) && queryCourseId) ||
      (app.activeCourseId && courses.value.some((course) => course.id === app.activeCourseId) && app.activeCourseId) ||
      courses.value[0]?.id ||
      ''

    tasks.value = mergeTasks(loadedTasks, courses.value)
    selectedTaskId.value = filteredTasks.value[0]?.id ?? tasks.value.find((task) => task.courseId === selectedCourseId.value)?.id ?? ''
  } finally {
    loading.value = false
  }
}

function mergeCourses(remoteCourses: Course[]) {
  const byTitle = new globalThis.Map<string, Course>()
  ;[...remoteCourses, ...fallbackCourses].forEach((course) => {
    if (!course.title) return
    if (!byTitle.has(course.title)) byTitle.set(course.title, course)
  })
  return Array.from(byTitle.values())
}

function mergeTasks(remoteTasks: GenerationTask[], courseList: Course[]) {
  const generated = remoteTasks
    .filter((task) => !hasCorruptText([task.topic, task.prompt, task.resultSummary, task.currentStep].join(' ')))
    .slice(0, 5)
    .map((task, index) => fromGenerationTask(task, courseList, index))
  const fallback = buildFallbackTasks(courseList)
  const keys = new Set(fallback.map((task) => `${task.courseId}-${task.title}`))
  const merged = [...fallback, ...generated.filter((task) => !keys.has(`${task.courseId}-${task.title}`))]
  return merged.length ? merged : fallback
}

function hasCorruptText(value: string) {
  const text = String(value || '')
  return /\?{2,}/.test(text) || /�/.test(text)
}

function fromGenerationTask(task: GenerationTask, courseList: Course[], index: number): PublishTask {
  const course = courseList.find((item) => item.id === task.courseId) ?? courseList[index % Math.max(courseList.length, 1)] ?? fallbackCourses[0]
  const status: PublishStatus = task.status === 'FAILED' ? 'revision' : task.status === 'SUCCEEDED' ? 'pending' : 'pending'
  const kind = (['courseware', 'practice', 'mindmap', 'lab', 'reading'] as const)[index % 5]
  return createTask({
    id: `backend-${task.id || index}`,
    backendTaskId: task.id,
    title: cleanTaskTitle(task.topic || `AI 生成资源 ${index + 1}`),
    courseId: course.id,
    courseName: course.title,
    chapter: index % 2 === 0 ? '第4章 会话跟踪技术' : '第3章 Servlet 技术',
    kind,
    assetCount: Math.max(4, Math.round((task.progressPercent || 80) / 10)),
    progress: Math.max(60, Math.min(100, task.progressPercent || 100)),
    status,
    savedAt: task.updatedAt ? '今天 15:08' : '今天 14:32',
    version: 'v0.7',
    summary: task.resultSummary || '基于课程资料与知识点结构生成资源，等待教师完成发布前检查。',
  })
}

function buildFallbackTasks(courseList: Course[]): PublishTask[] {
  const java = courseList.find((course) => course.title.includes('Java Web')) ?? courseList[0] ?? fallbackCourses[0]
  const data = courseList.find((course) => course.title.includes('数据结构')) ?? java
  return [
    createTask({
      id: 'pub-001',
      title: '第4章 会话跟踪技术 课件与练习',
      courseId: java.id,
      courseName: java.title,
      chapter: '第4章 会话跟踪技术',
      kind: 'courseware',
      assetCount: 12,
      progress: 100,
      status: 'pending',
      savedAt: '今天 15:08',
      version: 'v0.7',
      summary: '围绕 Cookie、Session 与会话生命周期生成课件正文、练习题和引用证据。',
    }),
    createTask({
      id: 'pub-002',
      title: '实验二：Servlet 实现',
      courseId: java.id,
      courseName: java.title,
      chapter: '第3章 Servlet 技术',
      kind: 'lab',
      assetCount: 8,
      progress: 80,
      status: 'pending',
      savedAt: '今天 14:51',
      version: 'v0.7',
      summary: '包含实验目标、步骤、代码骨架与结果提交规范，需要确认发布范围。',
    }),
    createTask({
      id: 'pub-003',
      title: '第5章 JSP 技术 课件',
      courseId: java.id,
      courseName: java.title,
      chapter: '第5章 JSP 技术',
      kind: 'courseware',
      assetCount: 9,
      progress: 100,
      status: 'revision',
      savedAt: '昨天 16:20',
      version: 'v0.6',
      summary: '课件内容完整，但表达层与脚本片段需要补充说明。',
    }),
    createTask({
      id: 'pub-004',
      title: '项目模板下载与说明',
      courseId: java.id,
      courseName: java.title,
      chapter: '项目实践',
      kind: 'reading',
      assetCount: 6,
      progress: 100,
      status: 'ready',
      savedAt: '今天 13:18',
      version: 'v1.0',
      summary: '项目模板、目录说明、提交规范已匹配课程目标。',
    }),
    createTask({
      id: 'pub-005',
      title: '第3章 Servlet 基础拓展阅读',
      courseId: java.id,
      courseName: java.title,
      chapter: '第3章 Servlet 技术',
      kind: 'reading',
      assetCount: 5,
      progress: 100,
      status: 'published',
      savedAt: '05-15',
      version: 'v1.0',
      summary: '已发布到课程空间，用于学生课前预习。',
    }),
    createTask({
      id: 'pub-006',
      title: '数据库连接配置指导文档',
      courseId: data.id,
      courseName: data.title,
      chapter: '数据库连接',
      kind: 'lab',
      assetCount: 4,
      progress: 100,
      status: 'published',
      savedAt: '05-13',
      version: 'v1.0',
      summary: '已发布，包含 JDBC 连接池配置与常见错误。',
    }),
    createTask({
      id: 'pub-007',
      title: 'JDBC 批量操作优化练习题',
      courseId: java.id,
      courseName: java.title,
      chapter: '第7章 RESTful API 设计',
      kind: 'practice',
      assetCount: 7,
      progress: 60,
      status: 'revision',
      savedAt: '昨天 21:05',
      version: 'v0.5',
      summary: '题目难度跨度较大，需要补齐分层提示与答案解析。',
    }),
    createTask({
      id: 'pub-008',
      title: '第2章 Java Web 基础课件',
      courseId: java.id,
      courseName: java.title,
      chapter: '第2章 Java Web 基础',
      kind: 'courseware',
      assetCount: 10,
      progress: 100,
      status: 'pending',
      savedAt: '今天 09:30',
      version: 'v0.7',
      summary: '包含 Web 应用结构、请求响应流程和部署练习。',
    }),
  ]
}

function createTask(task: Omit<PublishTask, 'kindLabel' | 'checks' | 'logs'>): PublishTask {
  const kindLabelMap: Record<Exclude<ResourceKind, 'all'>, string> = {
    courseware: '课件',
    practice: '练习',
    mindmap: '导图',
    lab: '实验指导',
    reading: '拓展阅读',
  }
  return {
    ...task,
    kindLabel: kindLabelMap[task.kind],
    checks: buildChecks(task.status),
    logs: [
      `${task.savedAt}  多智能体完成正文、资源范围与引用证据汇总。`,
      `${task.savedAt}  课程匹配度检查完成，生成发布前检查面板。`,
      '系统保留生成提示、引用证据与发布操作记录。',
    ],
  }
}

function buildChecks(status: PublishStatus): ReleaseCheck[] {
  const hasWarning = status === 'pending' || status === 'revision'
  return [
    {
      id: 'match',
      title: '课程匹配度',
      description: '资源内容与本课程教学目标、章节结构匹配',
      status: 'pass',
      detail: '课程名称、章节范围和学习目标均已对齐。',
    },
    {
      id: 'citation',
      title: '引用证据',
      description: '关键内容有可靠来源支撑，引用规范',
      status: 'pass',
      detail: '教材、课件与课堂资料均已写入证据链。',
    },
    {
      id: 'facts',
      title: '事实准确性',
      description: '技术概念、代码示例、数据编号无明显错误',
      status: hasWarning ? 'warn' : 'pass',
      detail: hasWarning ? '发现 1 条需要关注项' : '未发现高风险事实问题。',
      bullets: hasWarning
        ? ['PPT 第 12 页：JSessionID 默认过期时间的描述不准确，建议补充服务器配置差异。']
        : ['术语、概念和示例代码一致。'],
    },
    {
      id: 'safety',
      title: '内容安全',
      description: '无敏感信息、违规内容或不当表达',
      status: 'pass',
      detail: '未包含个人隐私、密钥和外部不安全链接。',
    },
    {
      id: 'readability',
      title: '学生可读性',
      description: '语言表达清晰，难度适中，适合学生理解',
      status: status === 'revision' ? 'warn' : 'partial',
      detail: status === 'revision' ? '发现 2 条表达和层级问题' : '建议教师确认表达是否适合当前班级。',
      bullets:
        status === 'revision'
          ? ['部分段落过长，建议拆分并增加小标题。', '代码示例缺少注释说明，建议补充。']
          : ['建议补充“为什么要学习会话跟踪”的应用场景。'],
    },
  ]
}

function cleanTaskTitle(title: string) {
  return title.replace(/\s*[-|｜].*$/, '').trim() || '生成资源'
}

function statusLabel(status: PublishStatus) {
  return statusOptions.find((item) => item.key === status)?.label ?? status
}

function statusClass(status: PublishStatus) {
  return `status-${status}`
}

function checkIcon(status: ReleaseCheck['status']) {
  if (status === 'pass') return CheckCircle2
  if (status === 'warn') return AlertTriangle
  return Info
}

function checkClass(status: ReleaseCheck['status']) {
  return `check-${status}`
}

function selectTask(task: PublishTask) {
  selectedTaskId.value = task.id
  activeTab.value = task.kind === 'practice' ? 'practice' : 'courseware'
}

function nextPage() {
  currentPage.value = Math.min(totalPages.value, currentPage.value + 1)
}

function previousPage() {
  currentPage.value = Math.max(1, currentPage.value - 1)
}

function updateTaskStatus(taskId: string, status: PublishStatus, progress = 100) {
  const task = tasks.value.find((item) => item.id === taskId)
  if (!task) return
  task.status = status
  task.progress = progress
  task.checks = buildChecks(status)
  task.savedAt = '刚刚'
  task.logs.unshift(`刚刚  ${app.currentUser.name || '李老师'} 将资源状态更新为「${statusLabel(status)}」。`)
  lastSavedAt.value = '刚刚'
}

function refreshPanel() {
  lastSavedAt.value = '刚刚'
  selectedTask.value?.logs.unshift('刚刚  已刷新发布检查面板和预览内容。')
  showToast('info', '已刷新当前资源的检查结果')
}

async function publishSelected() {
  const task = selectedTask.value
  if (!task) return
  if (!task.backendTaskId) {
    showToast('warn', '当前资源没有后端任务编号，不能发布到班级课程空间。')
    return
  }
  actionLoading.value = 'publish'
  try {
    await tasksApi.reviewDecision(task.backendTaskId, {
      decision: 'APPROVED',
      reviewer: app.currentUser.name || '李老师',
      note: '教师确认资源准确、可读且适合全班发布。',
    })
    await tasksApi.publish(task.backendTaskId, {
      publisherName: app.currentUser.name || '李老师',
      publishNote: '教师确认发布给当前班级。',
    })
    updateTaskStatus(task.id, 'published', 100)
    showToast('ok', '已通过并发布到班级课程空间')
  } catch (err) {
    showToast('warn', err instanceof Error ? `发布失败：${err.message}` : '发布失败，请稍后重试。')
  } finally {
    actionLoading.value = ''
  }
}

async function requestRevision() {
  const task = selectedTask.value
  if (!task) return
  if (!task.backendTaskId) {
    showToast('warn', '当前资源没有后端任务编号，不能提交修订决策。')
    return
  }
  actionLoading.value = 'revise'
  try {
    await tasksApi.reviewDecision(task.backendTaskId, {
      decision: 'CHANGES_REQUIRED',
      reviewer: app.currentUser.name || '李老师',
      note: '请补充发布检查面板标记的事实准确性和学生可读性问题。',
    })
    updateTaskStatus(task.id, 'revision', Math.min(task.progress, 80))
    showToast('warn', '已要求修改，资源回到修订队列')
  } catch (err) {
    showToast('warn', err instanceof Error ? `修订决策失败：${err.message}` : '修订决策失败，请稍后重试。')
  } finally {
    actionLoading.value = ''
  }
}

async function rejectSelected() {
  const task = selectedTask.value
  if (!task) return
  if (!task.backendTaskId) {
    showToast('warn', '当前资源没有后端任务编号，不能提交驳回决策。')
    return
  }
  actionLoading.value = 'reject'
  try {
    await tasksApi.reviewDecision(task.backendTaskId, {
      decision: 'REJECTED',
      reviewer: app.currentUser.name || '李老师',
      note: '当前资源不满足发布条件，请重新生成或重新关联证据。',
    })
    updateTaskStatus(task.id, 'revision', 0)
    task.logs.unshift('刚刚  教师驳回该资源，要求重新生成或补充证据。')
    showToast('warn', '已驳回当前资源')
  } catch (err) {
    showToast('warn', err instanceof Error ? `驳回失败：${err.message}` : '驳回失败，请稍后重试。')
  } finally {
    actionLoading.value = ''
  }
}

function regenerateSelected() {
  const task = selectedTask.value
  if (!task) return
  if (!task.backendTaskId) {
    showToast('warn', '当前资源没有后端任务编号，不能重新生成。')
    return
  }
  showToast('info', '当前后端尚未提供重新生成接口，请从资源生成入口创建新任务。')
}

function exportEvidence() {
  const task = selectedTask.value
  if (!task) return
  actionLoading.value = 'export'
  const payload = {
    exportedAt: new Date().toISOString(),
    publisher: app.currentUser.name || '李老师',
    course: task.courseName,
    task: task.title,
    status: statusLabel(task.status),
    checks: task.checks,
    logs: task.logs,
  }
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${task.title.replace(/[\\/:*?"<>|]/g, '_')}-证据包.json`
  link.click()
  URL.revokeObjectURL(url)
  actionLoading.value = ''
  showToast('ok', '证据包已导出')
}

function showToast(tone: ToastState['tone'], message: string) {
  toast.value = { tone, message }
}
</script>

<template>
  <div class="publish-management-page">
    <div v-if="toast" class="publish-toast" :class="`toast-${toast.tone}`">
      <CircleCheck v-if="toast.tone === 'ok'" :size="16" />
      <AlertTriangle v-else-if="toast.tone === 'warn'" :size="16" />
      <Info v-else :size="16" />
      <span>{{ toast.message }}</span>
    </div>

    <section class="publish-filter-panel">
      <div class="filter-group course-filter">
        <span class="filter-label">课程</span>
        <label class="select-shell">
          <select v-model="selectedCourseId" aria-label="选择课程">
            <option v-for="course in courses" :key="course.id" :value="course.id">
              {{ course.title }}
            </option>
          </select>
          <ChevronDown :size="16" />
        </label>
      </div>

      <div class="filter-group status-filter">
        <span class="filter-label">状态</span>
        <div class="segmented-list">
          <button
            v-for="status in statusOptions"
            :key="status.key"
            type="button"
            class="filter-chip"
            :class="[{ active: selectedStatus === status.key }, `chip-${status.tone}`]"
            @click="selectedStatus = status.key"
          >
            <span>{{ status.label }}</span>
            <strong>{{ statusCounts[status.key] || 0 }}</strong>
          </button>
        </div>
      </div>

      <div class="filter-group type-filter">
        <span class="filter-label">资源类型</span>
        <div class="type-chip-list">
          <button
            v-for="kind in kindOptions"
            :key="kind.key"
            type="button"
            class="type-chip"
            :class="{ active: selectedKind === kind.key }"
            @click="selectedKind = kind.key"
          >
            {{ kind.label }}
          </button>
        </div>
      </div>
    </section>

    <section class="publish-main-grid" :aria-busy="loading">
      <article class="publish-card queue-card">
        <div class="card-title-row">
          <div class="card-title-main">
            <h2>待发布任务列表</h2>
          </div>
          <div class="card-title-actions">
            <span class="metric-chip">{{ filteredTasks.length }} 条</span>
            <Loader2 v-if="loading" class="spin" :size="18" />
          </div>
        </div>

        <div class="queue-table" role="table">
          <div class="queue-row queue-head" role="row">
            <span>任务名称</span>
            <span>课程</span>
            <span>数量</span>
            <span>进度</span>
            <span>状态</span>
          </div>
          <button
            v-for="task in pagedTasks"
            :key="task.id"
            type="button"
            class="queue-row queue-item"
            :class="{ selected: task.id === selectedTask?.id }"
            role="row"
            @click="selectTask(task)"
          >
            <span class="task-name-cell">
              <span class="task-icon" :class="kindMeta[task.kind].className">
                <component :is="kindMeta[task.kind].icon" :size="15" />
              </span>
              <span class="task-title-line">
                <strong>{{ task.title }}</strong>
                <span class="kind-badge">{{ task.kindLabel }}</span>
              </span>
            </span>
            <span class="course-cell">{{ task.courseName }}</span>
            <span>{{ task.assetCount }}</span>
            <span class="progress-cell">
              <strong>{{ task.progress }}%</strong>
              <i><b :style="{ width: `${task.progress}%` }" /></i>
            </span>
            <span class="status-pill" :class="statusClass(task.status)">{{ statusLabel(task.status) }}</span>
          </button>
        </div>

        <div class="table-footer">
          <span>共 {{ filteredTasks.length }} 条</span>
          <div class="pager">
            <button type="button" :disabled="currentPage === 1" @click="previousPage">
              <ChevronLeft :size="16" />
            </button>
            <strong>{{ currentPage }}</strong>
            <button type="button" :disabled="currentPage === totalPages" @click="nextPage">
              <ChevronRight :size="16" />
            </button>
            <label class="page-size">
              <select v-model.number="pageSize" aria-label="每页条数">
                <option :value="5">5 条/页</option>
                <option :value="8">8 条/页</option>
                <option :value="10">10 条/页</option>
              </select>
              <ChevronDown :size="14" />
            </label>
          </div>
        </div>
      </article>

      <article class="publish-card preview-card">
        <div class="card-title-row">
          <div class="card-title-main">
            <h2>{{ resourcePreviewTitle }}</h2>
          </div>
          <div class="card-title-actions">
            <span class="resource-badge">
              <component :is="currentKindIcon" :size="15" />
              {{ selectedTask?.kindLabel || '资源' }}
            </span>
            <span v-if="selectedTask" class="metric-chip">{{ selectedTask.assetCount }} 个资源</span>
          </div>
        </div>

        <div class="preview-tabs" role="tablist" aria-label="资源预览标签">
          <button
            v-for="tab in previewTabs"
            :key="tab.key"
            type="button"
            :class="{ active: activeTab === tab.key }"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>

        <div class="preview-body">
          <div v-if="activeTab === 'courseware'" class="document-preview">
            <h3>{{ selectedTask?.chapter }}</h3>
            <h4>4.1 会话跟踪概述</h4>
            <p>
              在 Web 应用中，HTTP 协议是无状态的，每个请求之间相互独立。为了在多个请求之间维护用户状态，需要使用会话跟踪技术。
            </p>
            <h4>4.2 Cookie 技术</h4>
            <ol>
              <li>Cookie 的基本概念：服务器发送到客户端并保存在本地的一小段数据。</li>
              <li>Cookie 的工作流程：请求、写入、后续携带与响应。</li>
            </ol>
            <div class="flow-diagram" aria-label="Cookie 工作流程">
              <span>浏览器<br />客户端</span>
              <div class="flow-lines">
                <i>1. 首次请求</i>
                <i>2. 设置 Cookie</i>
                <i>3. 后续请求携带 Cookie</i>
                <i>4. 响应</i>
              </div>
              <span>服务器<br />Web 容器</span>
            </div>
            <h4>3. 示例代码</h4>
            <pre><code>Cookie cookie = new Cookie("username", "zhangsan");
cookie.setMaxAge(30 * 60);
response.addCookie(cookie);</code></pre>
          </div>

          <div v-else-if="activeTab === 'practice'" class="practice-preview">
            <div class="practice-item">
              <strong>1. Cookie 与 Session 的区别是什么？</strong>
              <p>要求学生从存储位置、生命周期、安全性和适用场景四个角度作答。</p>
            </div>
            <div class="practice-item">
              <strong>2. 设计登录状态保持流程</strong>
              <p>给出用户登录后访问个人中心的请求链路，并标注 Cookie 的写入与读取位置。</p>
            </div>
            <div class="practice-item">
              <strong>3. 调试题：JSessionID 丢失</strong>
              <p>根据日志定位 Session 无法保持的原因，并给出修复方案。</p>
            </div>
          </div>

          <div v-else-if="activeTab === 'mindmap'" class="mindmap-preview">
            <div class="mind-node root">会话跟踪技术</div>
            <div class="mind-branches">
              <span>Cookie</span>
              <span>Session</span>
              <span>URL 重写</span>
              <span>安全风险</span>
              <span>实验应用</span>
            </div>
            <p>导图已关联本章课件、练习题和实验指导书，发布后学生可在课程详情页直接引用。</p>
          </div>

          <div v-else-if="activeTab === 'evidence'" class="evidence-preview">
            <div class="evidence-item">
              <Paperclip :size="16" />
              <span>《Java Web 技术体系.pdf》第 4 章，Cookie 与 Session 概念定义。</span>
            </div>
            <div class="evidence-item">
              <Paperclip :size="16" />
              <span>课程讲义《Servlet 与 JSP 基础.pptx》第 32-45 页。</span>
            </div>
            <div class="evidence-item">
              <Paperclip :size="16" />
              <span>项目实验指导书：会话登录与购物车示例。</span>
            </div>
          </div>

          <div v-else class="logs-preview">
            <div v-for="log in selectedTask?.logs" :key="log" class="log-line">
              <Clock3 :size="15" />
              <span>{{ log }}</span>
            </div>
          </div>
        </div>

        <div class="viewer-toolbar">
          <button type="button"><ChevronLeft :size="16" /></button>
          <strong>1</strong>
          <span>/ 18</span>
          <button type="button"><ChevronRight :size="16" /></button>
          <div class="zoom-control">
            <button type="button">-</button>
            <span>100%</span>
            <button type="button">+</button>
          </div>
          <button type="button" class="square-button"><Eye :size="16" /></button>
        </div>
      </article>

      <article class="publish-card check-card">
        <div class="card-title-row compact">
          <div class="card-title-main">
            <h2>发布检查面板</h2>
          </div>
          <button type="button" class="text-action" @click="refreshPanel">
            <RefreshCw :size="15" />
            刷新
          </button>
        </div>

        <div class="check-list">
          <section v-for="check in selectedTask?.checks" :key="check.id" class="check-item" :class="checkClass(check.status)">
            <div class="check-main">
              <span class="check-icon">
                <component :is="checkIcon(check.status)" :size="17" />
              </span>
              <div>
                <h3 :title="check.description">{{ check.title }}</h3>
              </div>
              <strong>{{ check.status === 'pass' ? '通过' : check.status === 'warn' ? '警告' : '待确认' }}</strong>
            </div>
            <div v-if="check.bullets?.length" class="check-detail">
              <span>{{ check.detail }}</span>
              <ul>
                <li v-for="bullet in check.bullets" :key="bullet">{{ bullet }}</li>
              </ul>
            </div>
          </section>
        </div>

        <div class="check-conclusion">
          <span>检查结论：</span>
          <strong><CheckCircle2 :size="15" /> {{ checkSummary.pass }} 项通过</strong>
          <strong class="warn"><AlertTriangle :size="15" /> {{ checkSummary.warn }} 项警告</strong>
          <strong class="partial"><Info :size="15" /> {{ checkSummary.partial }} 项待确认</strong>
          <p>{{ releaseConclusion }}</p>
        </div>
      </article>
    </section>

    <section class="publish-info-strip">
      <Info :size="18" />
      <span>发布审核</span>
      <strong>当前课程可发布：{{ activeCoursePublishable }} 个</strong>
    </section>

    <section class="publish-action-bar">
      <div class="draft-meta">
        <span>最近保存：{{ lastSavedAt }}</span>
        <i />
        <span>草稿版本：{{ selectedTask?.version || 'v0.7' }}</span>
      </div>
      <div class="action-buttons">
        <button type="button" class="outline-action" :disabled="actionLoading === 'export'" @click="exportEvidence">
          <Loader2 v-if="actionLoading === 'export'" class="spin" :size="16" />
          <Download v-else :size="16" />
          导出证据包
        </button>
        <button type="button" class="outline-action" @click="regenerateSelected">
          <RotateCcw :size="16" />
          重新生成问题资源
        </button>
        <button type="button" class="danger-action" @click="rejectSelected">
          <XCircle :size="16" />
          驳回
        </button>
        <button type="button" class="warn-action" @click="requestRevision">
          <AlertTriangle :size="16" />
          要求修改
        </button>
        <button type="button" class="primary-action" :disabled="actionLoading === 'publish'" @click="publishSelected">
          <Loader2 v-if="actionLoading === 'publish'" class="spin" :size="16" />
          <Send v-else :size="16" />
          通过并发布
        </button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.publish-management-page {
  position: relative;
  display: grid;
  gap: 16px;
  width: 100%;
  min-width: 0;
  color: #10203f;
}

.publish-toast {
  position: fixed;
  z-index: 80;
  top: 82px;
  right: 36px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 38px;
  padding: 0 14px;
  border: 1px solid #c9dee8;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 12px 32px rgba(15, 42, 70, 0.12);
  font-size: 13px;
  font-weight: 700;
}

.toast-ok {
  color: #04786e;
}

.toast-warn {
  color: #c46c18;
}

.toast-info {
  color: #2469a6;
}

.publish-filter-panel,
.publish-card,
.publish-info-strip,
.publish-action-bar {
  border: 1px solid #d7e2ea;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 8px 26px rgba(19, 50, 80, 0.045);
}

.publish-filter-panel {
  display: grid;
  grid-template-columns: minmax(280px, 1fr) auto minmax(520px, 1.45fr);
  align-items: center;
  gap: 24px;
  min-height: 82px;
  padding: 14px 18px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.filter-label {
  flex: 0 0 auto;
  color: #566780;
  font-size: 13px;
  font-weight: 700;
}

.select-shell {
  position: relative;
  display: flex;
  align-items: center;
  min-width: 0;
  height: 44px;
  border: 1px solid #cddce6;
  border-radius: 8px;
  background: #ffffff;
}

.select-shell select,
.page-size select {
  width: 100%;
  height: 100%;
  min-width: 0;
  appearance: none;
  border: 0;
  outline: none;
  background: transparent;
  color: #10203f;
  font-size: 14px;
  font-weight: 700;
}

.select-shell select {
  padding: 0 38px 0 14px;
}

.select-shell svg {
  position: absolute;
  right: 12px;
  color: #43546e;
  pointer-events: none;
}

.course-filter .select-shell {
  width: min(410px, 100%);
}

.segmented-list,
.type-chip-list {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.filter-chip,
.type-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  height: 42px;
  padding: 0 18px;
  white-space: nowrap;
  border: 1px solid #d7e2ea;
  border-radius: 8px;
  background: #ffffff;
  color: #283954;
  font-size: 14px;
  font-weight: 700;
}

.filter-chip strong {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
  padding: 0 7px;
  border-radius: 999px;
  background: #eef6f4;
  color: #08766e;
}

.filter-chip.active,
.type-chip.active {
  border-color: #9fd8d3;
  background: linear-gradient(180deg, #e7f7f5, #dff3f1);
  color: #007d75;
}

.chip-warn strong {
  background: #fff2dc;
  color: #ba6a16;
}

.chip-ok strong {
  background: #e8f7ef;
  color: #258556;
}

.chip-muted strong {
  background: #edf2f7;
  color: #53627a;
}

.publish-main-grid {
  display: grid;
  grid-template-columns: minmax(430px, 0.96fr) minmax(520px, 1.08fr) minmax(390px, 0.9fr);
  gap: 16px;
  align-items: stretch;
  min-width: 0;
}

.publish-card {
  min-width: 0;
  overflow: hidden;
}

.card-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 58px;
  padding: 15px 20px;
  border-bottom: 1px solid #e4ebf0;
}

.card-title-row.compact {
  min-height: 58px;
}

.card-title-main {
  min-width: 0;
}

.card-title-row h2 {
  min-width: 0;
  overflow: hidden;
  margin: 0;
  color: #10203f;
  font-size: 18px;
  line-height: 1.25;
  font-weight: 850;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-title-actions {
  display: inline-flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  flex: 0 0 auto;
  min-width: 0;
}

.metric-chip,
.kind-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 26px;
  padding: 0 9px;
  border: 1px solid #cfece8;
  border-radius: 999px;
  color: #007a72;
  background: #edfafa;
  font-size: 12px;
  font-weight: 850;
  white-space: nowrap;
}

.spin {
  animation: spin 0.9s linear infinite;
}

.queue-table {
  display: grid;
  min-height: 500px;
}

.queue-row {
  display: grid;
  grid-template-columns: minmax(180px, 1.36fr) minmax(120px, 0.86fr) 54px minmax(86px, 0.7fr) 70px;
  column-gap: 12px;
  align-items: center;
  width: 100%;
  min-width: 0;
  padding: 0 18px;
}

.queue-head {
  height: 42px;
  color: #63728a;
  background: #f8fafc;
  border-bottom: 1px solid #e3ebf1;
  font-size: 12px;
  font-weight: 800;
}

.queue-item {
  min-height: 64px;
  text-align: left;
  border-bottom: 1px solid #e6edf2;
  background: #ffffff;
  color: #10203f;
}

.queue-item:hover {
  background: #f6fbfb;
}

.queue-item.selected {
  background: linear-gradient(90deg, rgba(225, 247, 244, 0.96), rgba(255, 255, 255, 0.96));
  box-shadow: inset 3px 0 0 #008b83;
}

.task-name-cell {
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr);
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.task-title-line,
.task-name-cell strong,
.course-cell {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-title-line {
  display: flex;
  align-items: center;
  gap: 8px;
}

.task-name-cell strong {
  flex: 1 1 auto;
  color: #142342;
  font-size: 13px;
  font-weight: 800;
}

.kind-badge {
  flex: 0 0 auto;
  height: 22px;
  padding: 0 8px;
  font-size: 11px;
}

.task-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 7px;
  color: #ffffff;
}

.task-icon.blue {
  background: #3c8be8;
}

.task-icon.green {
  background: #20a672;
}

.task-icon.violet {
  background: #8764f5;
}

.task-icon.orange {
  background: #ff986b;
}

.task-icon.cyan {
  background: #22b8b4;
}

.course-cell {
  display: block;
  color: #16365a;
  font-size: 12px;
  font-weight: 700;
  line-height: 1.45;
}

.progress-cell {
  display: grid;
  gap: 6px;
  min-width: 0;
}

.progress-cell strong {
  color: #193655;
  font-size: 12px;
}

.progress-cell i {
  display: block;
  width: 100%;
  height: 6px;
  overflow: hidden;
  border-radius: 999px;
  background: #e7eef3;
}

.progress-cell b {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #008c82, #27b4a8);
}

.status-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 58px;
  height: 26px;
  padding: 0 9px;
  border: 1px solid transparent;
  border-radius: 7px;
  font-size: 12px;
  font-weight: 800;
  white-space: nowrap;
}

.status-pending {
  color: #206da7;
  background: #e9f4ff;
  border-color: #cce5fb;
}

.status-revision {
  color: #bd6516;
  background: #fff3e6;
  border-color: #ffd9b4;
}

.status-ready {
  color: #087d62;
  background: #e8f7ef;
  border-color: #c8ebdc;
}

.status-published {
  color: #5c6877;
  background: #f2f5f8;
  border-color: #dce5eb;
}

.table-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  height: 64px;
  padding: 0 18px;
  color: #63728a;
  font-size: 13px;
}

.pager {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pager button,
.viewer-toolbar button,
.square-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid #d5e2ec;
  border-radius: 7px;
  background: #ffffff;
  color: #40516d;
}

.pager button:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

.pager strong {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 7px;
  background: #008b83;
  color: #ffffff;
}

.page-size {
  position: relative;
  display: flex;
  align-items: center;
  width: 92px;
  height: 34px;
  border: 1px solid #d5e2ec;
  border-radius: 7px;
  background: #ffffff;
}

.page-size select {
  padding: 0 26px 0 10px;
  font-size: 12px;
}

.page-size svg {
  position: absolute;
  right: 8px;
  pointer-events: none;
}

.resource-badge,
.text-action {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  white-space: nowrap;
  color: #007c74;
  font-size: 13px;
  font-weight: 800;
}

.resource-badge {
  height: 30px;
  padding: 0 10px;
  border-radius: 999px;
  background: #e7f6f4;
}

.text-action {
  color: #008b83;
}

.preview-tabs {
  display: flex;
  align-items: center;
  gap: 28px;
  height: 48px;
  padding: 0 20px;
  border-bottom: 1px solid #e4ebf0;
}

.preview-tabs button {
  position: relative;
  height: 48px;
  color: #52637b;
  font-size: 13px;
  font-weight: 800;
}

.preview-tabs button.active {
  color: #007c74;
}

.preview-tabs button.active::after {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  height: 2px;
  border-radius: 999px;
  background: #008b83;
  content: '';
}

.preview-body {
  min-height: 478px;
  padding: 18px 20px 12px;
  background: linear-gradient(180deg, #ffffff, #fbfdfd);
}

.document-preview {
  display: grid;
  gap: 12px;
  min-height: 440px;
  padding: 22px;
  border: 1px solid #e1e9ef;
  border-radius: 9px;
  background: #ffffff;
}

.document-preview h3,
.document-preview h4,
.document-preview p,
.document-preview ol {
  margin: 0;
}

.document-preview h3 {
  font-size: 20px;
  font-weight: 900;
}

.document-preview h4 {
  margin-top: 4px;
  font-size: 16px;
  font-weight: 850;
}

.document-preview p,
.document-preview li {
  color: #33435e;
  font-size: 13px;
  line-height: 1.8;
}

.document-preview ol {
  padding-left: 18px;
}

.flow-diagram {
  display: grid;
  grid-template-columns: 96px 1fr 96px;
  align-items: center;
  gap: 14px;
  margin: 4px 0;
}

.flow-diagram > span {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 76px;
  text-align: center;
  border: 1px solid #b9d0e8;
  border-radius: 7px;
  background: #f7fbff;
  color: #24415f;
  font-weight: 800;
}

.flow-lines {
  display: grid;
  gap: 7px;
}

.flow-lines i {
  display: block;
  padding: 4px 8px;
  text-align: center;
  border-radius: 999px;
  background: linear-gradient(90deg, #eff7fb, #f8fbfe);
  color: #4a5d75;
  font-size: 11px;
  font-style: normal;
}

.document-preview pre {
  margin: 0;
  padding: 14px;
  overflow: auto;
  border: 1px solid #e4ebf0;
  border-radius: 8px;
  background: #f8fafc;
  color: #17314c;
  font-size: 12px;
  line-height: 1.7;
}

.practice-preview,
.evidence-preview,
.logs-preview,
.mindmap-preview {
  display: grid;
  gap: 14px;
  min-height: 440px;
  align-content: start;
}

.practice-item,
.evidence-item,
.log-line {
  display: grid;
  gap: 8px;
  padding: 16px;
  border: 1px solid #e1e9ef;
  border-radius: 9px;
  background: #ffffff;
}

.practice-item strong {
  color: #10203f;
}

.practice-item p,
.evidence-item,
.log-line {
  color: #52637b;
  font-size: 13px;
  line-height: 1.7;
}

.evidence-item,
.log-line {
  grid-template-columns: 20px minmax(0, 1fr);
  align-items: start;
}

.evidence-item svg,
.log-line svg {
  color: #008b83;
}

.mindmap-preview {
  justify-items: center;
  padding: 40px 20px;
}

.mind-node {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 180px;
  height: 58px;
  border-radius: 999px;
  background: linear-gradient(135deg, #008b83, #21b7aa);
  color: #ffffff;
  font-size: 18px;
  font-weight: 900;
}

.mind-branches {
  display: grid;
  grid-template-columns: repeat(5, minmax(80px, 1fr));
  gap: 12px;
  width: 100%;
  margin-top: 28px;
}

.mind-branches span {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  border: 1px solid #cfe2e8;
  border-radius: 8px;
  background: #f5fbfa;
  color: #0a756e;
  font-weight: 800;
}

.mindmap-preview p {
  max-width: 520px;
  margin: 20px 0 0;
  color: #5c6e86;
  line-height: 1.75;
}

.viewer-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 58px;
  padding: 0 20px;
  border-top: 1px solid #e4ebf0;
  color: #52637b;
}

.viewer-toolbar strong {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid #d5e2ec;
  border-radius: 7px;
  color: #008b83;
}

.zoom-control {
  display: flex;
  align-items: center;
  gap: 0;
  margin-left: auto;
  overflow: hidden;
  border: 1px solid #d5e2ec;
  border-radius: 7px;
}

.zoom-control button {
  border: 0;
  border-radius: 0;
}

.zoom-control span {
  min-width: 58px;
  text-align: center;
  color: #293b54;
  font-size: 13px;
  font-weight: 800;
}

.check-list {
  display: grid;
  min-height: 526px;
}

.check-item {
  padding: 16px 18px;
  border-bottom: 1px solid #e4ebf0;
}

.check-main {
  display: grid;
  grid-template-columns: 32px minmax(0, 1fr) auto;
  gap: 10px;
  align-items: start;
}

.check-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 8px;
}

.check-pass .check-icon {
  background: #e8f7ef;
  color: #0c8b67;
}

.check-warn .check-icon {
  background: #fff0dc;
  color: #d07218;
}

.check-partial .check-icon {
  background: #eaf4ff;
  color: #2f78b7;
}

.check-main h3 {
  margin: 0;
}

.check-main h3 {
  color: #142342;
  font-size: 14px;
  font-weight: 850;
}

.check-main strong {
  color: #0c8b67;
  font-size: 13px;
  font-weight: 850;
}

.check-warn .check-main strong {
  color: #d07218;
}

.check-partial .check-main strong {
  color: #2f78b7;
}

.check-detail {
  margin: 12px 0 0 42px;
  padding: 12px 14px;
  border: 1px solid #e3ebf1;
  border-radius: 8px;
  background: #fbfdfd;
  color: #52637b;
  font-size: 12.5px;
  line-height: 1.65;
}

.check-detail ul {
  margin: 6px 0 0;
  padding-left: 17px;
}

.check-conclusion {
  margin: 16px 18px 18px;
  padding: 14px;
  border: 1px solid #e3ebf1;
  border-radius: 9px;
  background: #fbfdfd;
  color: #506178;
  font-size: 13px;
}

.check-conclusion span {
  color: #142342;
  font-weight: 850;
}

.check-conclusion strong {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin-left: 8px;
  color: #0c8b67;
}

.check-conclusion strong.warn {
  color: #d07218;
}

.check-conclusion strong.partial {
  color: #2f78b7;
}

.check-conclusion p {
  margin: 9px 0 0;
  line-height: 1.6;
}

.publish-info-strip {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 54px;
  padding: 0 18px;
  color: #2469a6;
  background: linear-gradient(90deg, #edf7ff, #f8fcff);
  font-size: 13px;
  font-weight: 700;
}

.publish-info-strip svg {
  flex: 0 0 auto;
  color: #2d83c5;
}

.publish-info-strip strong {
  margin-left: auto;
  color: #008b83;
  white-space: nowrap;
}

.publish-action-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  min-height: 72px;
  padding: 14px 18px;
}

.draft-meta {
  display: inline-flex;
  align-items: center;
  gap: 14px;
  color: #60718a;
  font-size: 13px;
  font-weight: 700;
}

.draft-meta i {
  width: 1px;
  height: 16px;
  background: #d7e2ea;
}

.action-buttons {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  flex-wrap: wrap;
}

.outline-action,
.danger-action,
.warn-action,
.primary-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-width: 126px;
  height: 42px;
  padding: 0 18px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 850;
}

.outline-action {
  color: #008178;
  border: 1px solid #a9d8d4;
  background: #ffffff;
}

.danger-action {
  color: #e24d47;
  border: 1px solid #ffb9b7;
  background: #fffafa;
}

.warn-action {
  color: #c96b17;
  border: 1px solid #ffd2a2;
  background: #fff9f2;
}

.primary-action {
  min-width: 150px;
  color: #ffffff;
  background: linear-gradient(135deg, #008b83, #069f94);
  box-shadow: 0 10px 22px rgba(0, 139, 131, 0.18);
}

.primary-action:disabled,
.outline-action:disabled {
  cursor: not-allowed;
  opacity: 0.65;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1500px) {
  .publish-filter-panel {
    grid-template-columns: 1fr;
    align-items: start;
  }

  .publish-main-grid {
    grid-template-columns: 1fr;
  }

  .queue-table,
  .check-list {
    min-height: auto;
  }

  .queue-row {
    grid-template-columns: minmax(180px, 1.35fr) minmax(120px, 0.9fr) 54px minmax(92px, 0.72fr) 76px;
  }
}

@media (max-width: 900px) {
  .publish-management-page {
    gap: 12px;
  }

  .segmented-list,
  .type-chip-list,
  .publish-action-bar,
  .publish-info-strip {
    flex-wrap: wrap;
  }

  .queue-row {
    grid-template-columns: minmax(0, 1fr) 60px 72px;
  }

  .queue-row > span:nth-child(2),
  .queue-row > span:nth-child(3),
  .queue-head > span:nth-child(2),
  .queue-head > span:nth-child(3) {
    display: none;
  }

  .preview-tabs {
    gap: 14px;
    overflow-x: auto;
  }

  .mind-branches,
  .flow-diagram {
    grid-template-columns: 1fr;
  }

  .publish-action-bar {
    align-items: flex-start;
  }

  .draft-meta,
  .action-buttons {
    width: 100%;
  }
}
</style>
