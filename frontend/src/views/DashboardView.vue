<script setup lang="ts">
import type { EChartsOption } from 'echarts'
import {
  Activity,
  BookOpen,
  Bot,
  ClipboardCheck,
  GraduationCap,
  RefreshCw,
  Route,
  Sparkles,
  UserRound,
} from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { agentsApi, apiBaseUrl, coursesApi, healthApi, profilesApi, tasksApi } from '@/api'
import ChartPanel from '@/components/ChartPanel.vue'
import DemoPrepChecklist from '@/components/DemoPrepChecklist.vue'
import ErrorNotice from '@/components/ErrorNotice.vue'
import LoadingBlock from '@/components/LoadingBlock.vue'
import MetricTile from '@/components/MetricTile.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import StatusPill from '@/components/StatusPill.vue'
import type { AgentDefinition, Course, GenerationTask, HealthResponse, ProfileResponse } from '@/types/api'
import { formatDate } from '@/utils/format'

const loading = ref(false)
const error = ref('')
const health = ref<HealthResponse | null>(null)
const agents = ref<AgentDefinition[]>([])
const tasks = ref<GenerationTask[]>([])
const profiles = ref<ProfileResponse[]>([])
const courses = ref<Course[]>([])
const endpointErrors = ref<Record<string, string>>({})

const demoEntrances = computed(() => [
  { to: '/profiles', title: '学生画像', desc: '创建画像并查看维度证据', icon: UserRound },
  { to: '/courses', title: '课程资源', desc: '维护课程并查看资源库', icon: GraduationCap },
  { to: '/generation', title: '资源生成', desc: '发起多智能体生成任务', icon: Sparkles },
  { to: tasks.value[0]?.id ? `/tasks/${tasks.value[0].id}` : '/generation', title: '任务详情', desc: '查看进度、步骤和审计', icon: Activity },
  { to: '/learning', title: '学习闭环', desc: '答疑、测评、批改与记录', icon: Route },
  { to: '/agents', title: '智能体工具箱', desc: '直接调试后端代理接口', icon: Bot },
  { to: '/teacher', title: '教师分析', desc: '班级掌握度和干预建议', icon: BookOpen },
  { to: '/demo', title: '评委模式', desc: '答辩证据和完成度报告', icon: ClipboardCheck },
])

const endpointStatus = computed(() => [
  { label: 'GET /health', ok: Boolean(health.value), error: endpointErrors.value.health },
  { label: 'GET /agents', ok: agents.value.length > 0, error: endpointErrors.value.agents },
  { label: 'GET /tasks', ok: !endpointErrors.value.tasks, error: endpointErrors.value.tasks },
  { label: 'GET /profiles', ok: !endpointErrors.value.profiles, error: endpointErrors.value.profiles },
  { label: 'GET /courses', ok: !endpointErrors.value.courses, error: endpointErrors.value.courses },
])

const statusNotes = computed(() => {
  const notes = []
  if (!String(apiBaseUrl).includes('localhost:8080/api')) {
    notes.push(`当前 API 地址为 ${apiBaseUrl}，如非预期请检查 frontend/.env.development。`)
  }
  if (!health.value) {
    notes.push('Java 后端未连通：在 backend 目录运行 .\\mvnw.cmd spring-boot:run。')
  }
  if (endpointErrors.value.agents || endpointErrors.value.tasks || endpointErrors.value.profiles || endpointErrors.value.courses) {
    notes.push('部分业务接口暂不可用：首页会保留空状态，继续启动后端依赖或刷新即可。')
  }
  return notes.length ? notes : ['三端基础联调正常，可以从下方演示入口按顺序开始比赛展示。']
})

const taskStatusOption = computed<EChartsOption>(() => {
  const counts = tasks.value.reduce<Record<string, number>>((acc, item) => {
    acc[item.status || 'UNKNOWN'] = (acc[item.status || 'UNKNOWN'] || 0) + 1
    return acc
  }, {})
  const data = Object.entries(counts).map(([name, value]) => ({ name, value }))
  return {
    tooltip: { trigger: 'item' },
    color: ['#2f6fef', '#0e7490', '#0f8a55', '#a15c00', '#c24138', '#64748b'],
    graphic: data.length
      ? undefined
      : { type: 'text', left: 'center', top: 'middle', style: { text: '暂无任务数据', fill: '#61708a' } },
    series: [
      {
        type: 'pie',
        radius: ['48%', '72%'],
        label: { formatter: '{b}: {c}' },
        data,
      },
    ],
  }
})

const agentOption = computed<EChartsOption>(() => ({
  tooltip: {},
  graphic: agents.value.length
    ? undefined
    : { type: 'text', left: 'center', top: 'middle', style: { text: '暂无智能体数据', fill: '#61708a' } },
  grid: { left: 36, right: 16, top: 20, bottom: 36 },
  xAxis: {
    type: 'category',
    data: agents.value.slice(0, 9).map((item) => item.displayName || item.agentKey),
    axisLabel: { rotate: 30, interval: 0 },
  },
  yAxis: { type: 'value' },
  series: [
    {
      type: 'bar',
      data: agents.value.slice(0, 9).map((_, index) => index + 1),
      itemStyle: { color: '#2f6fef', borderRadius: [4, 4, 0, 0] },
    },
  ],
}))

async function load() {
  loading.value = true
  error.value = ''
  endpointErrors.value = {}
  try {
    const [healthResult, agentsResult, tasksResult, profilesResult, coursesResult] = await Promise.allSettled([
      healthApi.getHealth(),
      agentsApi.definitions(),
      tasksApi.list(),
      profilesApi.list(),
      coursesApi.list(),
    ])
    if (healthResult.status === 'fulfilled') health.value = healthResult.value
    else {
      health.value = null
      endpointErrors.value.health = healthResult.reason instanceof Error ? healthResult.reason.message : '后端健康检查失败'
    }
    if (agentsResult.status === 'fulfilled') agents.value = agentsResult.value
    else {
      agents.value = []
      endpointErrors.value.agents = agentsResult.reason instanceof Error ? agentsResult.reason.message : '智能体列表不可用'
    }
    if (tasksResult.status === 'fulfilled') tasks.value = tasksResult.value
    else {
      tasks.value = []
      endpointErrors.value.tasks = tasksResult.reason instanceof Error ? tasksResult.reason.message : '任务列表不可用'
    }
    if (profilesResult.status === 'fulfilled') profiles.value = profilesResult.value
    else {
      profiles.value = []
      endpointErrors.value.profiles = profilesResult.reason instanceof Error ? profilesResult.reason.message : '学生画像列表不可用'
    }
    if (coursesResult.status === 'fulfilled') courses.value = coursesResult.value
    else {
      courses.value = []
      endpointErrors.value.courses = coursesResult.reason instanceof Error ? coursesResult.reason.message : '课程列表不可用'
    }
    const failures = Object.keys(endpointErrors.value).length
    if (failures) error.value = `有 ${failures} 个接口暂不可用，请按演示准备清单确认服务状态。`
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="page-grid">
    <MetricTile class="span-3" label="学生画像" :value="profiles.length" detail="对话式构建" />
    <MetricTile class="span-3" label="课程" :value="courses.length" detail="知识库输入" />
    <MetricTile class="span-3" label="智能体" :value="agents.length" detail="后端启用定义" />
    <MetricTile class="span-3" label="生成任务" :value="tasks.length" detail="最近任务" />

    <SectionPanel class="span-12" title="系统状态" subtitle="Spring Boot 后端与演示数据">
      <template #actions>
        <button class="ghost-button" @click="load"><RefreshCw :size="17" />刷新</button>
      </template>
      <ErrorNotice :message="error" />
      <LoadingBlock :show="loading" />
      <div class="split-row">
        <div class="timeline-body">
          <h3>后端</h3>
          <StatusPill :status="health?.status || (loading ? '检测中' : '离线')" :tone="health?.status === 'UP' ? 'ok' : loading ? 'warn' : 'danger'" />
          <p>{{ health?.service || 'software-cup-learning-backend' }}</p>
          <small>{{ health?.timestamp ? formatDate(String(health.timestamp)) : apiBaseUrl }}</small>
        </div>
        <div class="timeline-body">
          <h3>联调状态说明</h3>
          <ul class="compact-list">
            <li v-for="note in statusNotes" :key="note">{{ note }}</li>
          </ul>
        </div>
      </div>
      <div class="endpoint-grid">
        <div v-for="item in endpointStatus" :key="item.label" class="endpoint-card">
          <strong>{{ item.label }}</strong>
          <StatusPill
            :status="item.error ? '失败' : item.ok ? '正常' : loading ? '检测中' : '暂无数据'"
            :tone="item.error ? 'danger' : item.ok ? 'ok' : loading ? 'warn' : 'muted'"
          />
          <small>{{ item.error || '接口可用时将自动展示数据。' }}</small>
        </div>
      </div>
    </SectionPanel>

    <SectionPanel class="span-12" title="演示准备清单" subtitle="复制命令并确认三段服务状态">
      <DemoPrepChecklist />
    </SectionPanel>

    <SectionPanel class="span-6" title="任务状态分布">
      <ChartPanel :option="taskStatusOption" :height="300" />
    </SectionPanel>
    <SectionPanel class="span-6" title="智能体顺序">
      <ChartPanel :option="agentOption" :height="300" />
    </SectionPanel>

    <SectionPanel class="span-12" title="最近任务">
      <div v-if="!tasks.length" class="empty-state">暂无任务</div>
      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>主题</th>
              <th>状态</th>
              <th>进度</th>
              <th>当前步骤</th>
              <th>更新时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="task in tasks" :key="task.id" class="clickable-row" @click="$router.push(`/tasks/${task.id}`)">
              <td>{{ task.topic }}</td>
              <td><StatusPill :status="task.status" :tone="task.status === 'SUCCEEDED' ? 'ok' : task.status === 'FAILED' ? 'danger' : 'warn'" /></td>
              <td>
                <div class="progress-track"><div class="progress-fill" :style="{ width: `${task.progressPercent || 0}%` }" /></div>
              </td>
              <td>{{ task.currentStep || '-' }}</td>
              <td>{{ formatDate(task.updatedAt) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </SectionPanel>

    <SectionPanel class="span-12" title="演示入口" subtitle="比赛现场建议按从左到右、从上到下的顺序演示">
      <div class="demo-entry-grid">
        <RouterLink v-for="item in demoEntrances" :key="item.title" class="demo-entry" :to="item.to">
          <component :is="item.icon" :size="20" />
          <div>
            <strong>{{ item.title }}</strong>
            <small>{{ item.desc }}</small>
          </div>
        </RouterLink>
      </div>
    </SectionPanel>
  </div>
</template>
