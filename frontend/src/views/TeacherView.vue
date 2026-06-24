<script setup lang="ts">
import type { EChartsOption } from 'echarts'
import {
  Activity,
  AlertTriangle,
  BookOpenCheck,
  CheckCircle2,
  ChevronDown,
  ClipboardCheck,
  Eye,
  FileUp,
  LineChart,
  PlusCircle,
  Send,
} from 'lucide-vue-next'
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { coursesApi, profilesApi, tasksApi } from '@/api'
import ChartPanel from '@/components/ChartPanel.vue'
import ErrorNotice from '@/components/ErrorNotice.vue'
import LoadingBlock from '@/components/LoadingBlock.vue'
import { useAppStore } from '@/stores/app'
import type { Course, GenerationTask, ProfileResponse } from '@/types/api'

interface CourseRow {
  course: Course
  className: string
  students: number
  status: '进行中' | '已结课'
  pendingCount: number
}

const router = useRouter()
const app = useAppStore()

const loading = ref(false)
const error = ref('')
const courses = ref<Course[]>([])
const tasks = ref<GenerationTask[]>([])
const profiles = ref<ProfileResponse[]>([])
const selectedCourseId = ref(app.activeCourseId || '')
const selectedClassId = ref('')
const openActionRow = ref('')
const notice = ref('')

const classOptions = computed(() => {
  const realOptions = courses.value.map((course) => ({
    id: `course-${course.id}`,
    name: course.department ? `${course.department} · ${course.title}` : course.title,
    students: profiles.value.length,
  }))
  return realOptions.length ? realOptions : [{ id: 'no-backend-class', name: '暂无后端班级数据', students: profiles.value.length }]
})

const selectedClass = computed(() => classOptions.value.find((item) => item.id === selectedClassId.value) || classOptions.value[0])
const sourceCourses = computed(() => courses.value)
const activeCourse = computed(() => sourceCourses.value.find((item) => item.id === selectedCourseId.value) || sourceCourses.value[0] || null)
const pendingResourceCount = computed(() => {
  return tasks.value.filter((task) => !isTaskDone(task)).length
})
const passRate = computed(() => {
  if (!tasks.value.length) return 0
  const passed = tasks.value.filter(isTaskDone).length
  return Math.round((passed / Math.max(tasks.value.length, 1)) * 100)
})

const courseRows = computed<CourseRow[]>(() => {
  return sourceCourses.value
    .slice(0, 4)
    .map((course) => {
      const relatedTasks = tasks.value.filter((task) => task.courseId === course.id)
      return {
        course,
        className: course.department || '未设置院系',
        students: profiles.value.length,
        status: '进行中',
        pendingCount: relatedTasks.filter((task) => !isTaskDone(task)).length,
      }
    })
})

const dashboardStats = computed(() => [
  {
    key: 'courses',
    label: '班级课程',
    value: String(sourceCourses.value.length),
    unit: '门',
    icon: BookOpenCheck,
    tone: 'teal',
  },
  {
    key: 'pending',
    label: '待发布资源',
    value: String(pendingResourceCount.value),
    unit: '个',
    icon: Send,
    tone: 'cyan',
  },
  {
    key: 'risk',
    label: '风险学生',
    value: '0',
    unit: '人',
    icon: AlertTriangle,
    tone: 'red',
  },
  {
    key: 'events',
    label: '后端任务记录',
    value: String(tasks.value.length),
    unit: '条',
    icon: Activity,
    tone: 'aqua',
  },
])

const currentCourseLabel = computed(() =>
  activeCourse.value ? `${activeCourse.value.title}${activeCourse.value.creditHours ? ` · ${activeCourse.value.creditHours} 学时` : ''}` : '请选择课程',
)

const todayTodos = computed(() => {
  const pendingTasks = tasks.value.filter((task) => !isTaskDone(task)).slice(0, 3)
  const failedTasks = tasks.value.filter((task) => task.status === 'FAILED').slice(0, 3)
  const incompleteCourses = sourceCourses.value.filter((course) => !course.syllabusJson?.trim()).slice(0, 3)
  return [
    {
      id: 'publish-check',
      title: '发布前检查',
      badge: pendingTasks.length,
      tone: 'teal',
      icon: ClipboardCheck,
      rows: pendingTasks.map((task) => ({ text: taskDisplayTitle(task), count: task.status || '处理中' })),
      route: '/generation',
    },
    {
      id: 'course-quality',
      title: '课程建设缺口',
      badge: incompleteCourses.length,
      tone: 'blue',
      icon: LineChart,
      rows: incompleteCourses.map((course) => ({ text: course.title, count: '缺少后端大纲' })),
      route: '/course-builder',
    },
    {
      id: 'failed-tasks',
      title: '失败任务',
      badge: failedTasks.length,
      tone: 'orange',
      icon: AlertTriangle,
      rows: failedTasks.map((task) => ({ text: taskDisplayTitle(task), count: '查看' })),
      route: '/generation',
    },
  ].filter((group) => group.rows.length > 0)
})

const resourceTimeline = computed(() => {
  return [...tasks.value]
    .sort((left, right) => Date.parse(right.updatedAt || right.createdAt) - Date.parse(left.updatedAt || left.createdAt))
    .slice(0, 5)
    .map((task) => ({
    id: task.id,
    time: formatTaskTime(task.updatedAt || task.createdAt),
    title: taskDisplayTitle(task),
    type: task.status === 'FAILED' ? '需处理' : task.taskType || '资源任务',
    author: app.currentUser.name || '李老师',
  }))
})

const buildProgress = computed(() => {
  const course = activeCourse.value
  const relatedTasks = course ? tasks.value.filter((task) => task.courseId === course.id) : []
  const doneTasks = relatedTasks.filter(isTaskDone)
  const publishedTasks = relatedTasks.filter((task) => task.status === 'PUBLISHED')
  const taskProgress = relatedTasks.length ? Math.round((doneTasks.length / relatedTasks.length) * 100) : 0
  return [
    { label: 'Course info', progress: course ? 100 : 0, state: course ? 'synced' : 'empty' },
    { label: 'Syllabus', progress: course?.syllabusJson?.trim() ? 100 : 0, state: course?.syllabusJson?.trim() ? 'synced' : 'empty' },
    { label: 'Resource tasks', progress: taskProgress, state: relatedTasks.length ? `${taskProgress}%` : 'empty' },
    { label: 'Published records', progress: publishedTasks.length ? 100 : 0, state: publishedTasks.length ? `${publishedTasks.length}` : 'empty' },
  ]
})

const trendRows = computed(() => {
  const buckets = new Map<string, { date: string; active: number; hours: number }>()
  tasks.value.forEach((task) => {
    const date = formatTaskDate(task.updatedAt || task.createdAt)
    if (!date) return
    const bucket = buckets.get(date) || { date, active: 0, hours: 0 }
    bucket.active += 1
    bucket.hours += task.progressPercent >= 100 ? 1 : 0
    buckets.set(date, bucket)
  })
  return [...buckets.values()].sort((left, right) => left.date.localeCompare(right.date)).slice(-7)
})

const trendOption = computed<EChartsOption>(() => ({
  color: ['#07867f', '#2d7de0'],
  tooltip: { trigger: 'axis' },
  legend: {
    top: 0,
    left: 88,
    icon: 'roundRect',
    itemWidth: 18,
    itemHeight: 6,
    textStyle: { color: '#4d6076', fontSize: 12, fontWeight: 700 },
    data: ['活跃学生数（人）', '学习时长（小时）'],
  },
  grid: { left: 40, right: 36, top: 46, bottom: 32 },
  xAxis: {
    type: 'category',
    data: trendRows.value.map((item) => item.date),
    axisLine: { lineStyle: { color: '#d7e4ea' } },
    axisTick: { show: false },
    axisLabel: { color: '#607488', fontSize: 12 },
  },
  yAxis: [
    {
      type: 'value',
      min: 0,
      max: 80,
      splitLine: { lineStyle: { color: '#edf4f6' } },
      axisLabel: { color: '#607488', fontSize: 12 },
    },
    {
      type: 'value',
      min: 0,
      max: 120,
      splitLine: { show: false },
      axisLabel: { color: '#607488', fontSize: 12 },
    },
  ],
  series: [
    {
      name: '活跃学生数（人）',
      type: 'line',
      smooth: true,
      symbolSize: 7,
      data: trendRows.value.map((item) => item.active),
      areaStyle: { color: 'rgba(7, 134, 127, 0.08)' },
    },
    {
      name: '学习时长（小时）',
      type: 'line',
      yAxisIndex: 1,
      smooth: true,
      symbolSize: 7,
      data: trendRows.value.map((item) => item.hours),
      areaStyle: { color: 'rgba(45, 125, 224, 0.07)' },
    },
  ],
}))

function isTaskDone(task: GenerationTask) {
  return task.status === 'SUCCEEDED' || task.status === 'PUBLISHED'
}

function taskDisplayTitle(task: GenerationTask) {
  return task.topic?.trim() || task.taskType?.trim() || 'backend task'
}

function formatTaskTime(value: string) {
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return '--'
  const now = new Date()
  const sameDay = parsed.toDateString() === now.toDateString()
  const yesterday = new Date(now)
  yesterday.setDate(now.getDate() - 1)
  const prefix = sameDay ? 'today' : parsed.toDateString() === yesterday.toDateString() ? 'yesterday' : formatTaskDate(value)
  return `${prefix} ${String(parsed.getHours()).padStart(2, '0')}:${String(parsed.getMinutes()).padStart(2, '0')}`
}

function formatTaskDate(value: string) {
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return ''
  return `${String(parsed.getMonth() + 1).padStart(2, '0')}-${String(parsed.getDate()).padStart(2, '0')}`
}

function setNotice(message: string) {
  notice.value = message
  window.setTimeout(() => {
    if (notice.value === message) notice.value = ''
  }, 2400)
}

function selectCourse(courseId: string) {
  selectedCourseId.value = courseId
  app.setActiveCourse(courseId)
}

function navigateTo(path: string, query: Record<string, string> = {}) {
  void router.push({ path, query })
}

function createCourse() {
  navigateTo('/course-builder', { mode: 'create' })
}

function uploadMaterial() {
  navigateTo('/course-builder', { mode: 'upload', courseId: selectedCourseId.value })
}

function viewPending() {
  navigateTo('/generation', { scope: 'pending', courseId: selectedCourseId.value })
}

function manageCourse(course: Course) {
  selectCourse(course.id)
  navigateTo('/course-builder', { courseId: course.id })
}

function viewLearningProfile(course: Course) {
  selectCourse(course.id)
  navigateTo('/profiles', { courseId: course.id, classId: selectedClassId.value })
}

function toggleRowMenu(courseId: string) {
  openActionRow.value = openActionRow.value === courseId ? '' : courseId
}

function runRowAction(course: Course, action: 'publish' | 'quality' | 'student') {
  openActionRow.value = ''
  selectCourse(course.id)
  if (action === 'publish') navigateTo('/generation', { courseId: course.id })
  if (action === 'quality') navigateTo('/quality', { courseId: course.id })
  if (action === 'student') navigateTo('/profiles', { courseId: course.id, focus: 'risk' })
}

function openTodo(routePath: string, id: string) {
  navigateTo(routePath, { from: 'teacher-workbench', focus: id, courseId: selectedCourseId.value })
}

function ensureSelections() {
  if ((!selectedCourseId.value || !sourceCourses.value.some((course) => course.id === selectedCourseId.value)) && sourceCourses.value[0]) {
    selectedCourseId.value = app.activeCourseId || sourceCourses.value[0].id
    if (!sourceCourses.value.some((course) => course.id === selectedCourseId.value)) {
      selectedCourseId.value = sourceCourses.value[0].id
    }
  }
  if (!classOptions.value.some((item) => item.id === selectedClassId.value)) {
    selectedClassId.value = classOptions.value[0]?.id || ''
  }
  if (selectedCourseId.value) app.setActiveCourse(selectedCourseId.value)
}

async function loadWorkbench() {
  loading.value = true
  error.value = ''
  try {
    const [courseResult, taskResult, profileResult] = await Promise.allSettled([coursesApi.list(), tasksApi.list(), profilesApi.list()])
    if (courseResult.status === 'fulfilled') courses.value = courseResult.value
    if (taskResult.status === 'fulfilled') tasks.value = taskResult.value
    if (profileResult.status === 'fulfilled') profiles.value = profileResult.value
    ensureSelections()
    const failed = [courseResult, taskResult, profileResult].filter((item) => item.status === 'rejected').length
    if (failed) error.value = '部分后端数据暂未同步，页面未使用本地样例补齐。'
  } catch (err) {
    error.value = err instanceof Error ? err.message : '教师工作台加载失败'
  } finally {
    loading.value = false
  }
}

watch(selectedCourseId, (courseId) => {
  if (courseId) app.setActiveCourse(courseId)
})

watch(classOptions, ensureSelections)

onMounted(loadWorkbench)
</script>

<template>
  <section class="teacher-workbench-page" aria-label="教学工作台">
    <LoadingBlock v-if="loading" message="正在同步教师工作台..." />
    <ErrorNotice v-if="error" :message="error" />
    <div v-if="notice" class="teacher-toast">{{ notice }}</div>

    <section class="teacher-control-bar" aria-label="课程与班级筛选">
      <label class="teacher-select-wrap">
        <span>当前课程</span>
        <select v-model="selectedCourseId" @change="setNotice('已切换当前课程')">
          <option v-for="course in sourceCourses" :key="course.id" :value="course.id">{{ course.title }}</option>
        </select>
        <ChevronDown :size="16" aria-hidden="true" />
      </label>

      <label class="teacher-select-wrap is-class">
        <span>班级</span>
        <select v-model="selectedClassId" @change="setNotice('已切换班级视图')">
          <option v-for="classItem in classOptions" :key="classItem.id" :value="classItem.id">{{ classItem.name }}</option>
        </select>
        <ChevronDown :size="16" aria-hidden="true" />
      </label>

      <div class="teacher-main-actions">
        <button class="teacher-button primary" type="button" @click="createCourse">
          <PlusCircle :size="18" />
          新建课程
        </button>
        <button class="teacher-button" type="button" @click="uploadMaterial">
          <FileUp :size="18" />
          上传资料
        </button>
        <button class="teacher-button" type="button" @click="viewPending">
          <Eye :size="18" />
          查看待发布
        </button>
      </div>
    </section>

    <section class="teacher-stat-grid" aria-label="教学关键指标">
      <article v-for="item in dashboardStats" :key="item.key" class="teacher-stat-card">
        <span :class="['teacher-stat-icon', item.tone]">
          <component :is="item.icon" :size="25" :stroke-width="1.8" />
        </span>
        <div>
          <p>{{ item.label }}</p>
          <strong>{{ item.value }}</strong>
          <em>{{ item.unit }}</em>
        </div>
      </article>
      <article class="teacher-stat-card pass-rate">
        <span class="rate-ring" :style="{ '--rate': `${passRate * 3.6}deg` }" aria-hidden="true"></span>
        <div>
          <p>资源通过率</p>
          <strong>{{ passRate }}</strong>
          <em>%</em>
        </div>
      </article>
    </section>

    <section class="teacher-main-grid">
      <article class="teacher-panel course-ops">
        <header class="teacher-panel-head">
          <div>
            <h2>{{ selectedClass.name }}</h2>
          </div>
          <button class="teacher-link-button" type="button" @click="navigateTo('/courses')">查看课程库</button>
        </header>
        <div class="course-ops-table" role="table" aria-label="课程运营表">
          <div class="course-ops-row course-ops-head" role="row">
            <span>课程名称</span>
            <span>班级</span>
            <span>学生数</span>
            <span>课程状态</span>
            <span>待处理事项</span>
            <span>操作</span>
          </div>
          <div v-for="row in courseRows" :key="row.course.id" class="course-ops-row" role="row">
            <strong>{{ row.course.title }}</strong>
            <span>{{ row.className }}</span>
            <span>{{ row.students }}</span>
            <span><i :class="['course-state', row.status === '进行中' ? 'running' : 'ended']">{{ row.status }}</i></span>
            <span class="pending-cell">
              <template v-if="row.pendingCount">待发布资源 <b>{{ row.pendingCount }}</b></template>
              <template v-else>--</template>
            </span>
            <span class="row-actions">
              <button type="button" @click="manageCourse(row.course)">管理</button>
              <button type="button" @click="viewLearningProfile(row.course)">学情</button>
              <span class="more-wrap">
                <button type="button" @click="toggleRowMenu(row.course.id)">
                  更多
                  <ChevronDown :size="13" />
                </button>
                <div v-if="openActionRow === row.course.id" class="row-action-popover">
                  <button type="button" @click="runRowAction(row.course, 'publish')">发布管理</button>
                  <button type="button" @click="runRowAction(row.course, 'student')">风险学生</button>
                  <button type="button" @click="runRowAction(row.course, 'quality')">发布质检</button>
                </div>
              </span>
            </span>
          </div>
        </div>
        <footer class="table-footer">
          <span>共 {{ courseRows.length }} 条</span>
          <div class="pager">
            <button type="button" aria-label="上一页" disabled>‹</button>
            <b>1</b>
            <button type="button" aria-label="下一页" disabled>›</button>
            <select aria-label="每页条数">
              <option>10 条/页</option>
              <option>20 条/页</option>
            </select>
          </div>
        </footer>
      </article>

      <article class="teacher-panel today-todos">
        <header class="teacher-panel-head">
          <div>
            <h2>发布、薄弱点与风险学生</h2>
          </div>
        </header>
        <div class="todo-group-list">
          <section v-for="group in todayTodos" :key="group.id" class="todo-group">
            <div :class="['todo-icon', group.tone]"><component :is="group.icon" :size="18" /></div>
            <div class="todo-copy">
              <header>
                <strong>{{ group.title }}</strong>
                <span>{{ group.badge }}</span>
              </header>
              <button v-for="row in group.rows" :key="row.text" type="button" @click="openTodo(group.route, group.id)">
                <small>{{ row.text }}</small>
                <em>{{ row.count }}</em>
              </button>
            </div>
          </section>
        </div>
      </article>
    </section>

    <section class="teacher-bottom-grid">
      <article class="teacher-panel trend-panel">
        <header class="teacher-panel-head compact">
          <div>
            <h2>活跃度与学习时长</h2>
          </div>
          <select aria-label="趋势时间范围">
            <option>近 7 天</option>
            <option>近 30 天</option>
          </select>
        </header>
        <ChartPanel :option="trendOption" :height="260" />
      </article>

      <article class="teacher-panel timeline-panel">
        <header class="teacher-panel-head compact">
          <div>
            <h2>{{ currentCourseLabel }}</h2>
          </div>
          <button class="teacher-link-button" type="button" @click="viewPending">查看更多</button>
        </header>
        <ol class="resource-timeline">
          <li v-for="item in resourceTimeline" :key="item.id">
            <time>{{ item.time }}</time>
            <span></span>
            <div>
              <strong>{{ item.title }}</strong>
              <small>{{ item.author }} 发布</small>
            </div>
            <em>{{ item.type }}</em>
          </li>
        </ol>
      </article>

      <article class="teacher-panel build-panel">
        <header class="teacher-panel-head compact">
          <div>
            <h2>从建课到发布的闭环</h2>
          </div>
          <button class="teacher-link-button" type="button" @click="navigateTo('/course-builder', { courseId: selectedCourseId })">查看全部</button>
        </header>
        <div class="build-progress-list">
          <div v-for="(item, index) in buildProgress" :key="item.label" class="build-row">
            <span>{{ index + 1 }}.</span>
            <strong>{{ item.label }}</strong>
            <i><b :style="{ width: `${item.progress}%` }"></b></i>
            <em :class="{ done: item.progress === 100 }">
              <CheckCircle2 v-if="item.progress === 100" :size="15" />
              {{ item.state }}
            </em>
          </div>
        </div>
      </article>
    </section>
  </section>
</template>

<style scoped>
.teacher-workbench-page {
  position: relative;
  display: grid;
  gap: 18px;
  min-width: 0;
  color: #10223b;
}

.teacher-toast {
  position: fixed;
  top: 92px;
  right: 36px;
  z-index: 120;
  padding: 10px 14px;
  color: #ffffff;
  background: #07867f;
  border-radius: 999px;
  box-shadow: 0 18px 36px rgba(7, 134, 127, 0.22);
  font-size: 13px;
  font-weight: 800;
}

.teacher-control-bar,
.teacher-panel,
.teacher-stat-card {
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(199, 216, 226, 0.94);
  border-radius: 12px;
  box-shadow: 0 16px 34px rgba(31, 55, 74, 0.045);
}

.teacher-control-bar {
  display: grid;
  grid-template-columns: minmax(360px, 1fr) minmax(260px, 0.72fr) auto;
  gap: 16px;
  align-items: center;
  min-height: 78px;
  padding: 16px 24px;
}

.teacher-select-wrap {
  position: relative;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  min-height: 44px;
  gap: 12px;
  padding: 0 14px;
  background: #fbfefe;
  border: 1px solid #cfe0e8;
  border-radius: 8px;
}

.teacher-select-wrap span {
  color: #596a7c;
  font-size: 13px;
  font-weight: 800;
}

.teacher-select-wrap select,
.teacher-panel-head select {
  width: 100%;
  min-width: 0;
  color: #13243b;
  background: transparent;
  border: 0;
  outline: 0;
  font: inherit;
  font-size: 14px;
  font-weight: 800;
  appearance: none;
}

.teacher-main-actions {
  display: grid;
  grid-template-columns: repeat(3, max-content);
  gap: 16px;
  justify-content: end;
}

.teacher-button,
.teacher-link-button,
.row-actions button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 42px;
  padding: 0 22px;
  color: #087f79;
  background: #ffffff;
  border: 1px solid rgba(8, 127, 121, 0.5);
  border-radius: 7px;
  font-size: 14px;
  font-weight: 900;
  cursor: pointer;
  transition:
    transform 140ms ease,
    border-color 140ms ease,
    background-color 140ms ease;
}

.teacher-button:hover,
.teacher-link-button:hover,
.row-actions button:hover {
  border-color: #07867f;
  transform: translateY(-1px);
}

.teacher-button.primary {
  color: #ffffff;
  background: linear-gradient(135deg, #059286 0%, #08766f 100%);
  border-color: transparent;
  box-shadow: 0 14px 28px rgba(5, 146, 134, 0.2);
}

.teacher-stat-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 0;
}

.teacher-stat-card {
  display: grid;
  grid-template-columns: 68px minmax(0, 1fr);
  align-items: center;
  min-height: 108px;
  padding: 22px 24px;
  border-radius: 0;
  box-shadow: none;
}

.teacher-stat-card:first-child {
  border-radius: 12px 0 0 12px;
}

.teacher-stat-card:last-child {
  border-radius: 0 12px 12px 0;
}

.teacher-stat-card + .teacher-stat-card {
  border-left: 0;
}

.teacher-stat-icon,
.todo-icon {
  display: grid;
  place-items: center;
  width: 58px;
  height: 58px;
  border-radius: 16px;
}

.teacher-stat-icon.teal,
.todo-icon.teal {
  color: #07867f;
  background: #e3f6f2;
}

.teacher-stat-icon.cyan {
  color: #067c88;
  background: #e8f7f8;
}

.teacher-stat-icon.red {
  color: #e45151;
  background: #fff0ef;
}

.teacher-stat-icon.aqua {
  color: #0f928b;
  background: #e1f5f3;
}

.todo-icon.blue {
  color: #2d7de0;
  background: #eef6ff;
}

.todo-icon.orange {
  color: #f97316;
  background: #fff4e8;
}

.teacher-stat-card p,
.teacher-panel-head p {
  margin: 0;
  color: #526579;
  font-size: 14px;
  font-weight: 800;
}

.teacher-stat-card strong {
  display: inline-block;
  margin-top: 6px;
  color: #061833;
  font-size: 31px;
  font-weight: 950;
  line-height: 1;
}

.teacher-stat-card em {
  margin-left: 6px;
  color: #061833;
  font-size: 16px;
  font-style: normal;
  font-weight: 850;
}

.pass-rate {
  grid-template-columns: 68px minmax(0, 1fr);
}

.rate-ring {
  width: 58px;
  height: 58px;
  border-radius: 50%;
  background: conic-gradient(#07867f var(--rate), #dbe9ee 0);
  box-shadow: inset 0 0 0 11px #ffffff;
}

.teacher-main-grid,
.teacher-bottom-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.55fr) minmax(420px, 0.9fr);
  gap: 18px;
}

.teacher-bottom-grid {
  grid-template-columns: minmax(470px, 1fr) minmax(430px, 0.82fr) minmax(520px, 1.02fr);
}

.teacher-panel {
  min-width: 0;
  padding: 18px;
}

.teacher-panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 15px;
}

.teacher-panel-head h2 {
  margin: 4px 0 0;
  color: #52677d;
  font-size: 13px;
  font-weight: 780;
  line-height: 1.25;
}

.teacher-panel-head.compact {
  align-items: center;
  margin-bottom: 10px;
}

.teacher-panel-head.compact h2 {
  font-size: 14px;
  font-weight: 800;
  color: #5e7185;
}

.teacher-link-button {
  min-height: 34px;
  padding: 0 14px;
  border-color: transparent;
  background: transparent;
  box-shadow: none;
}

.course-ops-table {
  overflow: visible;
  border: 1px solid #d3e2e9;
  border-radius: 10px;
}

.course-ops-row {
  display: grid;
  grid-template-columns: minmax(250px, 1.42fr) minmax(164px, 0.75fr) 86px 120px minmax(150px, 0.82fr) 204px;
  align-items: center;
  min-height: 58px;
  gap: 12px;
  padding: 0 14px;
  color: #21334b;
  border-top: 1px solid #dbe7ed;
  font-size: 13px;
  font-weight: 780;
}

.course-ops-head {
  min-height: 42px;
  color: #63768b;
  background: linear-gradient(180deg, #f9fcfd 0%, #f3f8fa 100%);
  border-top: 0;
  font-size: 12px;
  font-weight: 860;
}

.course-ops-row strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
  font-weight: 920;
}

.course-state {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 0 13px;
  border-radius: 8px;
  font-style: normal;
  font-size: 12px;
  font-weight: 900;
}

.course-state.running {
  color: #087f79;
  background: #dff4ee;
}

.course-state.ended {
  color: #637386;
  background: #eef2f4;
}

.pending-cell b {
  color: #f0642f;
}

.row-actions {
  position: relative;
  display: grid;
  grid-template-columns: repeat(3, max-content);
  gap: 8px;
  justify-content: end;
}

.row-actions button {
  min-height: 30px;
  padding: 0 12px;
  color: #087f79;
  background: #fbfefe;
  font-size: 12px;
}

.more-wrap {
  position: relative;
}

.more-wrap > button {
  gap: 4px;
}

.row-action-popover {
  position: absolute;
  right: 0;
  top: calc(100% + 8px);
  z-index: 20;
  display: grid;
  width: 132px;
  padding: 8px;
  background: #ffffff;
  border: 1px solid #cddfe7;
  border-radius: 10px;
  box-shadow: 0 18px 38px rgba(26, 48, 70, 0.16);
}

.row-action-popover button {
  justify-content: flex-start;
  min-height: 32px;
  border: 0;
}

.table-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 56px;
  color: #53677e;
  font-size: 13px;
  font-weight: 760;
}

.pager {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pager button,
.pager b,
.pager select {
  display: grid;
  min-width: 36px;
  height: 36px;
  place-items: center;
  color: #40536b;
  background: #ffffff;
  border: 1px solid #ccdae4;
  border-radius: 8px;
  font: inherit;
}

.pager b {
  color: #ffffff;
  background: #07867f;
  border-color: transparent;
}

.pager select {
  width: 112px;
  padding: 0 10px;
}

.todo-group-list {
  display: grid;
  gap: 0;
}

.todo-group {
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr);
  gap: 14px;
  padding: 14px 2px 16px;
  border-top: 1px solid #e0eaef;
}

.todo-group:first-child {
  border-top: 0;
}

.todo-icon {
  width: 34px;
  height: 34px;
  border-radius: 10px;
}

.todo-copy header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}

.todo-copy strong {
  color: #10223b;
  font-size: 15px;
  font-weight: 930;
}

.todo-copy header span {
  display: grid;
  min-width: 22px;
  height: 22px;
  place-items: center;
  color: #ffffff;
  background: #ff6b68;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 900;
}

.todo-copy button {
  display: grid;
  width: 100%;
  grid-template-columns: minmax(0, 1fr) max-content;
  gap: 16px;
  min-height: 28px;
  padding: 0;
  text-align: left;
  background: transparent;
  border: 0;
  cursor: pointer;
}

.todo-copy small {
  overflow: hidden;
  color: #41556e;
  font-size: 13px;
  font-weight: 760;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.todo-copy em {
  color: #087f79;
  font-style: normal;
  font-size: 13px;
  font-weight: 860;
}

.trend-panel,
.timeline-panel,
.build-panel {
  min-height: 334px;
}

.teacher-panel-head select {
  width: 98px;
  min-height: 34px;
  padding: 0 13px;
  border: 1px solid #cfdee6;
  border-radius: 8px;
}

.resource-timeline {
  display: grid;
  gap: 0;
  margin: 10px 0 0;
  padding: 0;
  list-style: none;
}

.resource-timeline li {
  display: grid;
  grid-template-columns: 82px 16px minmax(0, 1fr) max-content;
  gap: 12px;
  align-items: start;
  min-height: 47px;
}

.resource-timeline time {
  color: #607488;
  font-size: 12px;
  font-weight: 800;
}

.resource-timeline li > span {
  position: relative;
  width: 9px;
  height: 9px;
  margin-top: 4px;
  background: #07867f;
  border-radius: 50%;
  box-shadow: 0 0 0 5px #e4f6f4;
}

.resource-timeline li:not(:last-child) > span::after {
  position: absolute;
  top: 12px;
  left: 4px;
  width: 1px;
  height: 42px;
  background: #cde2e7;
  content: '';
}

.resource-timeline strong,
.resource-timeline small {
  display: block;
  min-width: 0;
}

.resource-timeline strong {
  overflow: hidden;
  color: #10223b;
  font-size: 13px;
  font-weight: 890;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.resource-timeline small {
  margin-top: 3px;
  color: #708198;
  font-size: 12px;
  font-weight: 700;
}

.resource-timeline em {
  padding: 3px 8px;
  color: #087f79;
  background: #e3f6f2;
  border-radius: 7px;
  font-style: normal;
  font-size: 11px;
  font-weight: 900;
}

.build-progress-list {
  display: grid;
  gap: 14px;
  margin-top: 12px;
}

.build-row {
  display: grid;
  grid-template-columns: 22px 134px minmax(0, 1fr) 76px;
  align-items: center;
  gap: 13px;
  min-height: 27px;
  color: #52677d;
  font-size: 13px;
  font-weight: 800;
}

.build-row strong {
  color: #21344b;
  font-weight: 900;
}

.build-row i {
  display: block;
  height: 7px;
  overflow: hidden;
  background: #e7eef2;
  border-radius: 999px;
}

.build-row i b {
  display: block;
  height: 100%;
  background: #07867f;
  border-radius: inherit;
}

.build-row em {
  display: inline-flex;
  align-items: center;
  justify-content: flex-end;
  gap: 6px;
  color: #40546a;
  font-style: normal;
  font-weight: 860;
}

.build-row em.done {
  color: #07867f;
}

@media (max-width: 1500px) {
  .teacher-control-bar {
    grid-template-columns: minmax(0, 1fr) minmax(210px, 0.7fr);
  }

  .teacher-main-actions {
    grid-column: 1 / -1;
  }

  .teacher-main-actions {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .teacher-bottom-grid {
    grid-template-columns: minmax(0, 1fr);
  }
}

@media (max-width: 1180px) {
  .teacher-stat-grid,
  .teacher-main-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .teacher-stat-card,
  .teacher-stat-card:first-child,
  .teacher-stat-card:last-child {
    border-radius: 12px;
  }

  .teacher-stat-card + .teacher-stat-card {
    border-left: 1px solid rgba(199, 216, 226, 0.94);
  }

  .course-ops-table {
    overflow-x: auto;
  }

  .course-ops-row {
    min-width: 980px;
  }
}
</style>
