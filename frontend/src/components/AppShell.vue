<script setup lang="ts">
import {
  Bell,
  BookOpenCheck,
  Bot,
  BrainCircuit,
  ChevronDown,
  CircleHelp,
  Eye,
  EyeOff,
  Globe2,
  GraduationCap,
  Home,
  KeyRound,
  LogOut,
  PanelLeftClose,
  PanelLeftOpen,
  PieChart,
  Route,
  Search,
  Send,
  Settings,
  Sparkles,
  UserRound,
  Users,
  X,
} from 'lucide-vue-next'
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { tasksApi } from '@/api'
import { useAppStore } from '@/stores/app'
import type { Course, GenerationTask } from '@/types/api'
import brandIcon from '@/assets/brand-learning-icon.png'

const route = useRoute()
const router = useRouter()
const app = useAppStore()

const studentHome = '/dashboard'
const teacherHome = '/teacher'
const studentNav = [
  { path: '/dashboard', label: '\u4eca\u65e5\u5b66\u4e60', icon: Home },
  { path: '/courses', label: '\u6211\u7684\u8bfe\u7a0b', icon: BookOpenCheck },
  { path: '/profiles', label: '\u5b66\u4e60\u753b\u50cf', icon: PieChart },
  { path: '/learning', label: 'AI \u52a9\u624b', icon: Bot },
  { path: '/settings', label: '\u6a21\u578b\u8bbe\u7f6e', icon: Settings },
]
const teacherNav = [
  { path: '/teacher', label: '教学工作台', icon: Users },
  { path: '/course-builder', label: '课程建设', icon: BookOpenCheck },
  { path: '/profiles', label: '班级画像', icon: BrainCircuit },
  { path: '/generation', label: '发布管理', icon: Send },
  { path: '/settings', label: '模型设置', icon: Settings },
]

const visibleNav = computed(() => (app.role === 'teacher' ? teacherNav : studentNav))
const currentHome = computed(() => (app.role === 'teacher' ? teacherHome : studentHome))
const userInitial = computed(() => app.currentUser.name.trim().slice(0, 1) || (app.role === 'teacher' ? 'T' : 'S'))
const routeTitle = computed(() => {
  if (app.role === 'student') {
    if (route.path === '/dashboard') return '\u4eca\u65e5\u5b66\u4e60'
    if (route.path === '/courses') return '\u6211\u7684\u8bfe\u7a0b'
    if (route.path.startsWith('/courses/')) return '' // 详情页使用内部面包屑
    if (route.path === '/profiles') return '\u5b66\u4e60\u753b\u50cf'
    if (route.path === '/learning') return '' // AI 助手使用自定义页面头部
  }
  if (app.role === 'teacher') {
    if (route.path === '/teacher') return '教学工作台'
    if (route.path === '/profiles') return '\u73ed\u7ea7\u753b\u50cf'
    if (route.path === '/course-builder') return '\u8bfe\u7a0b\u5efa\u8bbe'
    if (route.path === '/generation') return '发布管理'
    if (route.path === '/quality') return '\u53d1\u5e03\u8d28\u68c0'
    if (route.path === '/agents') return '智能体协同'
    if (route.path === '/settings') return '模型设置'
  }
  return String(route.meta.title || '\u667a\u5b66\u5de5\u574a')
})
const routeSubtitle = computed(() => {
  if (app.role === 'teacher') {
    return ''
  }
  return ''
})
const accessNotice = computed(() => {
  const access = String(route.query.access || '')
  if (access === 'student-workspace') return '当前为学生账号，已进入学生工作区；教师工作台、智能体审核和发布质检请切换教师账号。'
  if (access === 'teacher-workspace') return '当前为教师账号，已进入教师工作台；学生学习、答疑和测评请切换学生账号。'
  return ''
})
const teacherOnlyRoutes = ['/teacher', '/agents', '/quality', '/generation', '/tasks']
const studentOnlyRoutes = ['/dashboard', '/learning']
const isInPathPrefix = (path: string, prefixes: string[]) => prefixes.some((prefix) => path === prefix || path.startsWith(`${prefix}/`))
const loginForm = reactive({
  username: '',
  password: '',
})
const authRole = ref<'student' | 'teacher'>('student')
const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  name: '',
  department: '',
  inviteCode: '',
})
const loginError = ref('')
const showPassword = ref(false)
const authMode = ref<'login' | 'register'>('login')
const authSubmitting = ref(false)
const courseMenuOpen = ref(false)
const presetCredentials = [
  { label: '学生账号', role: 'student' as const, username: 'zhang.student', password: 'student@2026' },
  { label: '教师账号', role: 'teacher' as const, username: 'li.teacher', password: 'teacher@2026' },
]
const authFeatureNodes = [
  { label: '课程资源', desc: '智能推荐学习内容', icon: BookOpenCheck },
  { label: '学习分析', desc: '多维分析学习行为', icon: Sparkles },
  { label: '学习任务', desc: '规划路径与目标', icon: Route },
  { label: 'AI 助教', desc: '答疑解惑与辅导', icon: Bot },
  { label: '知识图谱', desc: '构建知识关联网络', icon: BrainCircuit },
]
const authHelperText = computed(() => {
  if (authMode.value === 'login') return '使用平台账号进入对应工作区'
  return authRole.value === 'teacher' ? '教师账号需填写邀请码并提交审核' : '填写班级码后加入老师发放的课程'
})
const authLoginNote = computed(() =>
  authRole.value === 'teacher'
    ? {
        title: '教学工作台',
        desc: '登录后管理课程、发放任务、审核 AI 生成资源并查看班级学情。',
      }
    : {
        title: '学习空间',
        desc: '登录后查看老师发放的课程，也可以上传资料生成自己的自定义课程。',
      },
)
const authPrimaryText = computed(() => {
  if (authMode.value === 'login') return authRole.value === 'teacher' ? '进入教学工作台' : '进入学习空间'
  return authRole.value === 'teacher' ? '提交审核' : '创建并加入班级'
})
const registerIdentityLabel = computed(() => (authRole.value === 'teacher' ? '教师信息' : '身份信息'))
const registerAccountLabel = computed(() => (authRole.value === 'teacher' ? '教师账号' : '学号/账号'))
const registerDepartmentLabel = computed(() => (authRole.value === 'teacher' ? '学校/院系' : '班级码'))
const registerDepartmentPlaceholder = computed(() => (authRole.value === 'teacher' ? '例如 计算机学院' : '请输入老师发放的班级码'))
const sidebarStorageKey = 'learning-sidebar-width'
const sidebarCollapsedStorageKey = 'learning-sidebar-collapsed'
const sidebarDefaultWidth = 320
const sidebarTeacherDefaultWidth = 320
const sidebarMinWidth = 248
const sidebarMaxWidth = 380
const sidebarCollapseThreshold = 112
const sidebarWidth = ref(readSidebarWidth())
const isSidebarCollapsed = ref(readSidebarCollapsed())
const isSidebarResizing = ref(false)
const shellStyle = computed<Record<string, string>>(() => ({
  '--sidebar-width': isSidebarCollapsed.value ? '0px' : String(sidebarWidth.value) + 'px',
}))
const courseSourceKind = (course: Course) => {
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
const classroomCourses = computed(() => app.courses.filter((course) => courseSourceKind(course) === 'classroom'))
const selfCourses = computed(() => app.courses.filter((course) => courseSourceKind(course) === 'self'))
type TopbarPanel = 'search' | 'notifications' | 'help' | 'system'
type TopbarItemTone = 'primary' | 'info' | 'warn' | 'muted'

interface TopbarActionItem {
  id: string
  group: string
  title: string
  description: string
  to: string
  query?: Record<string, string>
  courseId?: string
  tone?: TopbarItemTone
  meta?: string
}

const topbarPanel = ref<TopbarPanel | null>(null)
const topbarSearchQuery = ref('')
const topbarSearchInput = ref<HTMLInputElement | null>(null)
const topbarTasks = ref<GenerationTask[]>([])
const topbarTasksLoading = ref(false)
const topbarTasksError = ref('')

const roleSearchActions = computed<TopbarActionItem[]>(() =>
  app.role === 'teacher'
    ? [
        { id: 'teacher-home', group: '教师工作', title: '教学工作台', description: '管理班级课程、待发布资源和学情证据。', to: '/teacher', tone: 'primary' },
        { id: 'teacher-builder', group: '课程建设', title: '新建或导入课程', description: '上传资料并生成班级课程结构。', to: '/course-builder', tone: 'info' },
        { id: 'teacher-profiles', group: '班级画像', title: '查看班级画像', description: '按课程和学生画像查看掌握度、风险与证据。', to: '/profiles', tone: 'info' },
        { id: 'teacher-generation', group: '发布管理', title: '待发布资源', description: '确认全班可见资源的正文、范围和发布记录。', to: '/generation', tone: 'warn' },
        { id: 'teacher-settings', group: '模型设置', title: '配置模型供应商', description: '切换讯飞星火或 OpenAI 兼容模型，并保存 API 配置。', to: '/settings', tone: 'info' },
      ]
    : [
        { id: 'student-today', group: '学习入口', title: '今日学习', description: '查看今天跨课程最该完成的任务。', to: '/dashboard', tone: 'primary' },
        { id: 'student-courses', group: '课程空间', title: '我的课程', description: '进入班级课程或自建课程的学习空间。', to: '/courses', tone: 'info' },
        { id: 'student-learning', group: 'AI 助手', title: '课程项目空间', description: '围绕课程资料、画像和当前问题连续对话。', to: '/learning', tone: 'primary' },
        { id: 'student-profile', group: '学习画像', title: '综合学习画像', description: '查看跨课程能力、证据和改进建议。', to: '/profiles', tone: 'info' },
      ],
)

const courseSearchActions = computed<TopbarActionItem[]>(() =>
  app.courses.map((course) => ({
    id: `course-${course.id}`,
    group: courseSourceKind(course) === 'self' ? '自建课程' : '班级课程',
    title: course.title,
    description: `${course.department} · ${course.creditHours} 学时`,
    to: app.role === 'teacher' ? '/course-builder' : `/courses/${course.id}`,
    courseId: course.id,
    tone: course.id === app.activeCourseId ? 'primary' : 'muted',
    meta: course.id === app.activeCourseId ? '当前课程' : '切换课程',
  })),
)

const topbarSearchItems = computed<TopbarActionItem[]>(() => [...roleSearchActions.value, ...courseSearchActions.value])
const topbarSearchResults = computed(() => {
  const keyword = topbarSearchQuery.value.trim().toLowerCase()
  const items = topbarSearchItems.value
  if (!keyword) return items.slice(0, 8)
  return items
    .filter((item) => `${item.group} ${item.title} ${item.description} ${item.meta || ''}`.toLowerCase().includes(keyword))
    .slice(0, 10)
})

const topbarNotifications = computed<TopbarActionItem[]>(() => {
  const taskItems: TopbarActionItem[] = topbarTasks.value.slice(0, 4).map((task) => {
    const tone: TopbarItemTone = task.status === 'FAILED' ? 'warn' : task.status === 'SUCCEEDED' ? 'info' : 'primary'
    const studentTaskLabel = task.status === 'FAILED' ? '生成异常' : '课程内生成'
    return {
      id: `task-${task.id}`,
      group: app.role === 'teacher' ? (task.status === 'FAILED' ? '任务异常' : '资源任务') : studentTaskLabel,
      title: task.topic || (app.role === 'teacher' ? '资源生成任务' : '课程学习资源'),
      description:
        task.currentStep ||
        task.resultSummary ||
        (app.role === 'teacher' ? '查看资源生成进度、审核状态和产出记录。' : '在 AI 助手中查看生成进度、资源内容和历史记录。'),
      to: app.role === 'teacher' ? `/tasks/${task.id}` : '/learning',
      query: app.role === 'teacher' ? undefined : { tab: 'progress', taskId: task.id },
      courseId: task.courseId || undefined,
      tone,
      meta: `${task.progressPercent || 0}%`,
    }
  })
  const fallback = app.role === 'teacher'
    ? [
        { id: 'notice-teacher-generation', group: '待处理', title: '检查待发布资源', description: '确认资源正文、发布范围和课程章节。', to: '/generation', tone: 'warn' as const, meta: '发布' },
        { id: 'notice-teacher-profile', group: '班级画像', title: '查看风险学生', description: '根据班级薄弱点和学习证据安排干预。', to: '/profiles', tone: 'info' as const, meta: '学情' },
      ]
    : [
        { id: 'notice-student-learning', group: '今日待办', title: '继续当前课程', description: '进入 AI 助手，围绕当前资料继续学习。', to: '/learning', courseId: app.activeCourseId || undefined, tone: 'primary' as const, meta: '学习' },
        { id: 'notice-student-profile', group: '画像更新', title: '补充学习证据', description: '把答疑、测评和学习行为写入综合画像。', to: '/profiles', tone: 'info' as const, meta: '画像' },
      ]
  return [...taskItems, ...fallback].slice(0, 6)
})

const topbarHelpItems = computed<TopbarActionItem[]>(() =>
  app.role === 'teacher'
    ? [
        { id: 'help-teacher-1', group: '工作台', title: '先看今日待处理', description: '优先处理待发布资源、班级薄弱点和风险学生。', to: '/teacher', tone: 'primary' },
        { id: 'help-teacher-2', group: '课程建设', title: '新建或导入课程', description: '上传资料后组织章节、资源槽位和班级发布范围。', to: '/course-builder', tone: 'info' },
        { id: 'help-teacher-3', group: '发布管理', title: '发布给全班', description: '教师确认正文、适配性和发布范围后再对学生可见。', to: '/generation', tone: 'warn' },
        { id: 'help-teacher-4', group: '模型设置', title: '切换模型供应商', description: '在教师端配置后，资源生成和课程助教会使用同一套模型服务。', to: '/settings', tone: 'info' },
      ]
    : [
        { id: 'help-student-1', group: '课程', title: '课程从哪里来', description: '班级课程来自老师发放，自建课程来自自己上传资料生成。', to: '/courses', tone: 'info' },
        { id: 'help-student-2', group: '学习', title: '如何开始今天的学习', description: '从今日学习进入任务队列，也可以直接进入课程 AI 助手。', to: '/dashboard', tone: 'primary' },
        { id: 'help-student-3', group: 'AI', title: 'AI 助手和课程助教的区别', description: '全局 AI 助手管理课程项目空间；课程内助教只服务当前课程资料。', to: '/learning', tone: 'primary' },
      ],
)
const visibleCourseGroups = computed(() => [
  { key: 'classroom', title: '班级发放课程', description: '由老师发布，进入班级后获得', courses: classroomCourses.value },
  { key: 'self', title: '我的自建课程', description: '上传资料后由 AI 生成', courses: selfCourses.value },
])

function clampSidebarWidth(width: number) {
  return Math.min(sidebarMaxWidth, Math.max(sidebarMinWidth, Math.round(width)))
}

function sidebarDefaultForRole() {
  return app.role === 'teacher' ? sidebarTeacherDefaultWidth : sidebarDefaultWidth
}

function roleStorageKey(base: string) {
  return `${base}-${app.role}`
}

function readSidebarWidth() {
  const defaultWidth = sidebarDefaultForRole()
  if (typeof window === 'undefined') return defaultWidth
  const roleScoped = window.localStorage.getItem(roleStorageKey(sidebarStorageKey))
  const legacy = window.localStorage.getItem(sidebarStorageKey)
  const stored = Number(roleScoped ?? (app.role === 'teacher' ? '' : legacy))
  return Number.isFinite(stored) ? clampSidebarWidth(stored) : defaultWidth
}

function readSidebarCollapsed() {
  if (typeof window === 'undefined') return false
  return window.localStorage.getItem(roleStorageKey(sidebarCollapsedStorageKey)) === 'true'
}

function persistSidebarState() {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(roleStorageKey(sidebarStorageKey), String(sidebarWidth.value))
  window.localStorage.setItem(roleStorageKey(sidebarCollapsedStorageKey), String(isSidebarCollapsed.value))
}

function collapseSidebar() {
  isSidebarCollapsed.value = true
  courseMenuOpen.value = false
  persistSidebarState()
}

function restoreSidebar() {
  isSidebarCollapsed.value = false
  sidebarWidth.value = clampSidebarWidth(sidebarWidth.value || sidebarDefaultForRole())
  persistSidebarState()
}

function handleSidebarPointerMove(event: PointerEvent) {
  if (!isSidebarResizing.value) return
  event.preventDefault()
  if (event.clientX <= sidebarCollapseThreshold) {
    isSidebarCollapsed.value = true
    return
  }
  isSidebarCollapsed.value = false
  sidebarWidth.value = clampSidebarWidth(event.clientX)
}

function stopSidebarResize() {
  if (!isSidebarResizing.value) return
  isSidebarResizing.value = false
  persistSidebarState()
  document.body.classList.remove('is-sidebar-resizing')
  document.removeEventListener('pointermove', handleSidebarPointerMove)
  document.removeEventListener('pointerup', stopSidebarResize)
}

function startSidebarResize(event: PointerEvent) {
  if (typeof window !== 'undefined' && window.innerWidth <= 1120) return
  event.preventDefault()
  if (isSidebarCollapsed.value) restoreSidebar()
  isSidebarResizing.value = true
  document.body.classList.add('is-sidebar-resizing')
  document.addEventListener('pointermove', handleSidebarPointerMove)
  document.addEventListener('pointerup', stopSidebarResize)
  handleSidebarPointerMove(event)
}

function adjustSidebarWidth(delta: number) {
  if (isSidebarCollapsed.value && delta > 0) {
    restoreSidebar()
    return
  }
  const nextWidth = sidebarWidth.value + delta
  if (nextWidth <= sidebarCollapseThreshold) {
    collapseSidebar()
    return
  }
  isSidebarCollapsed.value = false
  sidebarWidth.value = clampSidebarWidth(nextWidth)
  persistSidebarState()
}

function resetSidebarWidth() {
  isSidebarCollapsed.value = false
  sidebarWidth.value = sidebarDefaultForRole()
  persistSidebarState()
}

onMounted(() => {
  void app.refreshHealth()
  if (app.isLoggedIn) void app.loadCourses()
})

onBeforeUnmount(stopSidebarResize)

watch(
  () => [app.isLoggedIn, app.role, route.path],
  () => {
    if (!app.isLoggedIn) return
    if (app.role === 'student' && isInPathPrefix(route.path, teacherOnlyRoutes)) void router.replace(studentHome)
    if (app.role === 'teacher' && isInPathPrefix(route.path, studentOnlyRoutes)) void router.replace(teacherHome)
  },
  { immediate: true },
)

watch(
  () => app.role,
  () => {
    sidebarWidth.value = readSidebarWidth()
    isSidebarCollapsed.value = readSidebarCollapsed()
  },
)

async function submitLogin() {
  loginError.value = ''
  authSubmitting.value = true
  try {
    await app.login(loginForm.username, loginForm.password, authRole.value)
    await app.loadCourses()
    await router.replace(app.role === 'teacher' ? teacherHome : studentHome)
  } catch (error) {
    loginError.value = error instanceof Error ? error.message : '登录失败'
  } finally {
    authSubmitting.value = false
  }
}

async function submitRegister() {
  loginError.value = ''
  if (registerForm.password !== registerForm.confirmPassword) {
    loginError.value = '两次输入的密码不一致'
    return
  }
  authSubmitting.value = true
  try {
    await app.register({
      username: registerForm.username,
      password: registerForm.password,
      role: authRole.value,
      name: registerForm.name,
      department: registerForm.department,
      inviteCode: registerForm.inviteCode,
    })
    await app.loadCourses()
    await router.replace(app.role === 'teacher' ? teacherHome : studentHome)
  } catch (error) {
    loginError.value = error instanceof Error ? error.message : '创建账号失败'
  } finally {
    authSubmitting.value = false
  }
}

function setAuthMode(mode: 'login' | 'register') {
  authMode.value = mode
  loginError.value = ''
}

function setAuthRole(role: 'student' | 'teacher') {
  authRole.value = role
  loginError.value = ''
}

function fillPresetAccount(username: string, password: string, role: 'student' | 'teacher') {
  authMode.value = 'login'
  authRole.value = role
  loginError.value = ''
  loginForm.username = username
  loginForm.password = password
}

function switchAccount() {
  courseMenuOpen.value = false
  app.logout()
  loginForm.username = ''
  loginForm.password = ''
}

function clearAccessNotice() {
  const query = { ...route.query }
  delete query.access
  void router.replace({ path: route.path, query })
}

function selectCourse(courseId: string) {
  app.setActiveCourse(courseId)
  courseMenuOpen.value = false
}

async function loadTopbarTasks(force = false) {
  if (topbarTasksLoading.value || (!force && topbarTasks.value.length)) return
  topbarTasksLoading.value = true
  topbarTasksError.value = ''
  try {
    topbarTasks.value = await tasksApi.list()
  } catch (error) {
    topbarTasksError.value = error instanceof Error ? error.message : '任务动态加载失败'
  } finally {
    topbarTasksLoading.value = false
  }
}

async function openTopbarPanel(panel: TopbarPanel) {
  topbarPanel.value = topbarPanel.value === panel ? null : panel
  if (topbarPanel.value === 'search') {
    await nextTick()
    topbarSearchInput.value?.focus()
  }
  if (topbarPanel.value === 'notifications') void loadTopbarTasks()
}

function closeTopbarPanel() {
  topbarPanel.value = null
}

function revealTopbarSearchPanel() {
  topbarPanel.value = 'search'
}

function runTopbarItem(item: TopbarActionItem) {
  if (item.courseId) app.setActiveCourse(item.courseId)
  closeTopbarPanel()
  void router.push({ path: item.to, query: item.query })
}

function submitTopbarSearch() {
  const first = topbarSearchResults.value[0]
  if (first) runTopbarItem(first)
}

watch(
  () => route.fullPath,
  () => {
    closeTopbarPanel()
  },
)
</script>

<template>
  <div v-if="!app.isLoggedIn" class="login-shell">
    <div class="login-stage">
      <section class="login-visual" aria-label="平台能力">
        <RouterLink class="brand login-brand" to="/dashboard" aria-label="智学工坊">
          <img class="brand-mark" :src="brandIcon" alt="" aria-hidden="true" />
          <div>
            <strong>智学工坊</strong>
            <span>个性化学习平台</span>
          </div>
        </RouterLink>

        <div class="login-copy">
          <h1>智学工坊<span>个性化学习平台</span></h1>
        </div>

        <div class="auth-orbit" aria-hidden="true">
          <div class="auth-orbit-core">
            <BrainCircuit :size="44" :stroke-width="1.45" />
          </div>
          <article v-for="node in authFeatureNodes" :key="node.label" class="auth-orbit-node">
            <span><component :is="node.icon" :size="18" :stroke-width="1.55" /></span>
            <div>
              <strong>{{ node.label }}</strong>
            </div>
          </article>
        </div>
      </section>

      <section :class="['login-card', authMode === 'register' ? 'is-register' : 'is-login']" aria-label="账号入口">
        <div class="auth-tabs" role="tablist" aria-label="账号入口">
          <button type="button" :class="{ active: authMode === 'login' }" @click="setAuthMode('login')">账号登录</button>
          <button type="button" :class="{ active: authMode === 'register' }" @click="setAuthMode('register')">创建账号</button>
        </div>

        <div class="auth-role-switch" role="radiogroup" aria-label="选择身份">
          <button
            type="button"
            :class="{ active: authRole === 'student' }"
            :aria-pressed="authRole === 'student'"
            @click="setAuthRole('student')"
          >
            <UserRound :size="18" :stroke-width="1.55" />
            学生
          </button>
          <button
            type="button"
            :class="{ active: authRole === 'teacher' }"
            :aria-pressed="authRole === 'teacher'"
            @click="setAuthRole('teacher')"
          >
            <Users :size="18" :stroke-width="1.55" />
            教师
          </button>
        </div>

        <form v-if="authMode === 'login'" class="account-login-form auth-form-shell" @submit.prevent="submitLogin">
          <div class="auth-form-section">
            <label>
              <span>账号</span>
              <input v-model="loginForm.username" autocomplete="username" placeholder="请输入账号" />
            </label>
            <label>
              <span>密码</span>
              <div class="password-field">
                <input
                  v-model="loginForm.password"
                  autocomplete="current-password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="请输入密码"
                />
                <button class="icon-button" type="button" :title="showPassword ? '隐藏密码' : '显示密码'" @click="showPassword = !showPassword">
                  <EyeOff v-if="showPassword" :size="18" />
                  <Eye v-else :size="18" />
                </button>
              </div>
            </label>
          </div>
          <small v-if="loginError" class="field-error">{{ loginError }}</small>
          <button class="button login-submit" type="submit" :disabled="authSubmitting"><KeyRound :size="17" />{{ authPrimaryText }}</button>
          <aside class="auth-login-note">
            <span><component :is="authRole === 'teacher' ? Users : GraduationCap" :size="18" :stroke-width="1.55" /></span>
            <div>
              <strong>{{ authLoginNote.title }}</strong>
            </div>
          </aside>
          <div class="auth-link-row">
            <button type="button" @click="setAuthMode('register')">创建账号</button>
            <button type="button">忘记密码？</button>
          </div>
        </form>

        <form v-else class="account-login-form account-register-form auth-form-shell" @submit.prevent="submitRegister">
          <div class="auth-form-section">
            <span class="auth-section-title">{{ registerIdentityLabel }}</span>
            <div class="auth-two-column">
              <label>
                <span>姓名</span>
                <input v-model="registerForm.name" autocomplete="name" placeholder="请输入姓名" />
              </label>
              <label>
                <span>{{ registerAccountLabel }}</span>
                <input v-model="registerForm.username" autocomplete="username" placeholder="4-32 位英文、数字或符号" />
              </label>
              <label>
                <span>{{ registerDepartmentLabel }}</span>
                <input v-model="registerForm.department" :placeholder="registerDepartmentPlaceholder" />
              </label>
              <label v-if="authRole === 'teacher'">
                <span>邀请码</span>
                <input v-model="registerForm.inviteCode" placeholder="请输入管理员发放的邀请码" />
              </label>
            </div>
          </div>

          <div class="auth-form-section">
            <span class="auth-section-title">账号安全</span>
            <div class="auth-two-column">
              <label>
                <span>密码</span>
                <input v-model="registerForm.password" autocomplete="new-password" type="password" placeholder="至少 8 位" />
              </label>
              <label>
                <span>确认密码</span>
                <input v-model="registerForm.confirmPassword" autocomplete="new-password" type="password" placeholder="再次输入密码" />
              </label>
            </div>
          </div>
          <small v-if="loginError" class="field-error">{{ loginError }}</small>
          <button class="button login-submit" type="submit" :disabled="authSubmitting"><KeyRound :size="17" />{{ authPrimaryText }}</button>
        </form>

        <div class="login-support-row">
          <span>登录即表示你同意《用户协议》和《隐私政策》</span>
          <span>{{ authRole === 'teacher' ? '教师权限由平台统一审核' : '课程权限由班级码和教师发放决定' }}</span>
        </div>
      </section>
    </div>
  </div>

  <div
    v-else
    :class="[
      'app-shell',
      app.role === 'teacher' ? 'is-teacher' : 'is-student',
      { 'is-sidebar-resizing': isSidebarResizing, 'is-sidebar-collapsed': isSidebarCollapsed },
    ]"
    :style="shellStyle"
  >
      <aside class="sidebar">
        <RouterLink class="brand" :to="currentHome" aria-label="智学工坊">
          <img class="brand-mark" :src="brandIcon" alt="" aria-hidden="true" />
          <div>
            <strong>智学工坊</strong>
            <span>个性化学习平台</span>
        </div>
      </RouterLink>

      <nav class="nav-list" aria-label="main">
        <RouterLink v-for="item in visibleNav" :key="item.path" :to="item.path" class="nav-item">
          <component :is="item.icon" :size="19" />
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>

      <div class="shell-account-area" aria-label="&#x8d26;&#x53f7;&#x5165;&#x53e3;">
        <div class="sidebar-user-card">
          <span class="identity-avatar" aria-hidden="true">{{ userInitial }}</span>
          <div class="sidebar-user-copy">
            <strong>{{ app.currentUser.name }}</strong>
            <small>{{ app.currentUser.title }} / {{ app.currentUser.username }}</small>
          </div>
          <button class="icon-button sidebar-logout" :title="'\u5207\u6362\u8d26\u53f7\uff1a' + app.currentUser.name" @click="switchAccount">
            <LogOut :size="17" />
          </button>
        </div>
        <button class="sidebar-collapse-action" type="button" @click="collapseSidebar">
          <PanelLeftClose :size="16" :stroke-width="1.8" />
          <span>&#x6536;&#x8d77;&#x4fa7;&#x680f;</span>
        </button>
      </div>

      <button
        class="sidebar-resizer"
        type="button"
        aria-label="拖动调整侧边栏宽度，双击恢复默认"
        :aria-valuemin="sidebarMinWidth"
        :aria-valuemax="sidebarMaxWidth"
        :aria-valuenow="sidebarWidth"
        @pointerdown="startSidebarResize"
        @dblclick="resetSidebarWidth"
        @keydown.left.prevent="adjustSidebarWidth(-16)"
        @keydown.right.prevent="adjustSidebarWidth(16)"
      >
        <span aria-hidden="true"></span>
      </button>
    </aside>

    <button
      v-if="isSidebarCollapsed"
      class="sidebar-restore-button"
      type="button"
      aria-label="&#x5c55;&#x5f00;&#x4fa7;&#x680f;"
      @click="restoreSidebar"
    >
      <img v-if="app.role === 'teacher'" class="sidebar-restore-mark" :src="brandIcon" alt="" aria-hidden="true" />
      <PanelLeftOpen :size="19" :stroke-width="1.9" />
    </button>

    <div class="workspace">
      <header class="topbar">
        <div class="topbar-title">
          <h1>{{ routeTitle }}</h1>
          <p v-if="routeSubtitle">{{ routeSubtitle }}</p>
        </div>
        <div class="topbar-actions account-zone" aria-label="&#x9875;&#x9762;&#x5de5;&#x5177;">
          <form v-if="app.role === 'teacher'" class="topbar-inline-search" @submit.prevent="submitTopbarSearch">
            <Search :size="18" :stroke-width="1.8" aria-hidden="true" />
            <input
              ref="topbarSearchInput"
              v-model="topbarSearchQuery"
              type="search"
              placeholder="搜索课程、资源、学生"
              @focus="revealTopbarSearchPanel"
            />
            <button type="submit" aria-label="搜索"><Search :size="17" :stroke-width="1.8" /></button>
          </form>
          <button
            v-if="app.role !== 'teacher'"
            :class="['icon-button', 'topbar-tool', { 'is-active': topbarPanel === 'search' }]"
            type="button"
            title="&#x641c;&#x7d22;"
            :aria-expanded="topbarPanel === 'search'"
            aria-controls="topbar-search-panel"
            @click="openTopbarPanel('search')"
          >
            <Search :size="18" :stroke-width="1.8" />
          </button>
          <button
            :class="['icon-button', 'topbar-tool', { 'is-active': topbarPanel === 'notifications' }]"
            type="button"
            title="&#x901a;&#x77e5;"
            :aria-expanded="topbarPanel === 'notifications'"
            aria-controls="topbar-notification-panel"
            @click="openTopbarPanel('notifications')"
          >
            <Bell :size="18" :stroke-width="1.8" />
            <span v-if="topbarNotifications.length" class="topbar-tool-badge" aria-hidden="true">{{ Math.min(topbarNotifications.length, 9) }}</span>
          </button>
          <button
            :class="['icon-button', 'topbar-tool', { 'is-active': topbarPanel === 'help' }]"
            type="button"
            title="&#x5e2e;&#x52a9;"
            :aria-expanded="topbarPanel === 'help'"
            aria-controls="topbar-help-panel"
            @click="openTopbarPanel('help')"
          >
            <CircleHelp :size="18" :stroke-width="1.8" />
          </button>
          <button
            v-if="app.role === 'teacher'"
            :class="['icon-button', 'topbar-tool', { 'is-active': topbarPanel === 'system' }]"
            type="button"
            title="平台状态"
            :aria-expanded="topbarPanel === 'system'"
            aria-controls="topbar-system-panel"
            @click="openTopbarPanel('system')"
          >
            <Globe2 :size="18" :stroke-width="1.8" />
          </button>

          <section v-if="topbarPanel === 'search'" id="topbar-search-panel" class="topbar-panel topbar-search-panel" aria-label="全局搜索">
            <header class="topbar-panel-head">
              <div>
                <strong>全局搜索</strong>
              </div>
              <button class="topbar-panel-close" type="button" title="关闭" @click="closeTopbarPanel">
                <X :size="17" :stroke-width="1.8" />
              </button>
            </header>
            <form class="topbar-search-form" @submit.prevent="submitTopbarSearch">
              <Search :size="18" :stroke-width="1.8" />
              <input ref="topbarSearchInput" v-model="topbarSearchQuery" type="search" placeholder="搜索课程、AI 助手、学习画像..." />
              <button type="submit">进入</button>
            </form>
            <div class="topbar-result-list">
              <button v-for="item in topbarSearchResults" :key="item.id" type="button" class="topbar-result-item" @click="runTopbarItem(item)">
                <span :class="['topbar-result-dot', item.tone || 'muted']" aria-hidden="true"></span>
                <div>
                  <small>{{ item.group }}<em v-if="item.meta">{{ item.meta }}</em></small>
                  <strong>{{ item.title }}</strong>
                </div>
              </button>
              <div v-if="!topbarSearchResults.length" class="topbar-empty-state">没有找到匹配结果</div>
            </div>
          </section>

          <section v-if="topbarPanel === 'notifications'" id="topbar-notification-panel" class="topbar-panel topbar-notification-panel" aria-label="通知中心">
            <header class="topbar-panel-head">
              <div>
                <strong>通知中心</strong>
              </div>
              <button class="topbar-panel-close" type="button" title="关闭" @click="closeTopbarPanel">
                <X :size="17" :stroke-width="1.8" />
              </button>
            </header>
            <div v-if="topbarTasksLoading" class="topbar-empty-state">正在读取任务动态...</div>
            <div v-else-if="topbarTasksError" class="topbar-empty-state is-error">{{ topbarTasksError }}</div>
            <div class="topbar-result-list">
              <button v-for="item in topbarNotifications" :key="item.id" type="button" class="topbar-result-item" @click="runTopbarItem(item)">
                <span :class="['topbar-result-dot', item.tone || 'muted']" aria-hidden="true"></span>
                <div>
                  <small>{{ item.group }}<em v-if="item.meta">{{ item.meta }}</em></small>
                  <strong>{{ item.title }}</strong>
                </div>
              </button>
            </div>
          </section>

          <section v-if="topbarPanel === 'help'" id="topbar-help-panel" class="topbar-panel topbar-help-panel" aria-label="帮助中心">
            <header class="topbar-panel-head">
              <div>
                <strong>帮助中心</strong>
              </div>
              <button class="topbar-panel-close" type="button" title="关闭" @click="closeTopbarPanel">
                <X :size="17" :stroke-width="1.8" />
              </button>
            </header>
            <div class="topbar-help-copy">
              <strong>{{ app.role === 'teacher' ? '教师端重点是课程建设、班级画像和发布管理' : '学生端重点是课程、规划和 AI 辅导' }}</strong>
            </div>
            <div class="topbar-result-list">
              <button v-for="item in topbarHelpItems" :key="item.id" type="button" class="topbar-result-item" @click="runTopbarItem(item)">
                <span :class="['topbar-result-dot', item.tone || 'muted']" aria-hidden="true"></span>
                <div>
                  <small>{{ item.group }}</small>
                  <strong>{{ item.title }}</strong>
                </div>
              </button>
            </div>
          </section>

          <section v-if="topbarPanel === 'system'" id="topbar-system-panel" class="topbar-panel topbar-system-panel" aria-label="平台状态">
            <header class="topbar-panel-head">
              <div>
                <strong>平台状态</strong>
              </div>
              <button class="topbar-panel-close" type="button" title="关闭" @click="closeTopbarPanel">
                <X :size="17" :stroke-width="1.8" />
              </button>
            </header>
            <div class="topbar-result-list">
              <button type="button" class="topbar-result-item" @click="runTopbarItem({ id: 'system-course', group: '当前课程', title: app.activeCourse?.title || '未选择课程', description: app.activeCourse ? `${app.activeCourse.department} · ${app.activeCourse.creditHours} 学时` : '在课程建设中选择或创建课程', to: '/course-builder', tone: 'primary' })">
                <span class="topbar-result-dot primary" aria-hidden="true"></span>
                <div>
                  <small>当前课程</small>
                  <strong>{{ app.activeCourse?.title || '未选择课程' }}</strong>
                  <p>{{ app.activeCourse ? `${app.activeCourse.department} · ${app.activeCourse.creditHours} 学时` : '在课程建设中选择或创建课程' }}</p>
                </div>
              </button>
              <button type="button" class="topbar-result-item" @click="app.refreshHealth()">
                <span :class="['topbar-result-dot', app.backendOnline ? 'primary' : 'warn']" aria-hidden="true"></span>
                <div>
                  <small>后端服务</small>
                  <strong>{{ app.backendOnline ? '已连接' : '连接异常' }}</strong>
                  <p>{{ app.backendOnline ? 'API、课程、任务和画像数据可用。' : '请检查 8080 后端服务。' }}</p>
                </div>
              </button>
            </div>
          </section>
        </div>
      </header>

      <div v-if="accessNotice" class="role-access-notice">
        <span>{{ accessNotice }}</span>
        <button type="button" @click="clearAccessNotice">知道了</button>
      </div>

      <main class="page-scroll">
        <RouterView />
      </main>

    </div>
  </div>
</template>
