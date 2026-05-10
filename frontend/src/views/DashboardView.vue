<script setup lang="ts">
import type { EChartsOption } from 'echarts'
import { Activity, RefreshCw } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { agentsApi, coursesApi, healthApi, profilesApi, tasksApi } from '@/api'
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
  try {
    const [healthResult, agentsResult, tasksResult, profilesResult, coursesResult] = await Promise.allSettled([
      healthApi.getHealth(),
      agentsApi.definitions(),
      tasksApi.list(),
      profilesApi.list(),
      coursesApi.list(),
    ])
    if (healthResult.status === 'fulfilled') health.value = healthResult.value
    if (agentsResult.status === 'fulfilled') agents.value = agentsResult.value
    if (tasksResult.status === 'fulfilled') tasks.value = tasksResult.value
    if (profilesResult.status === 'fulfilled') profiles.value = profilesResult.value
    if (coursesResult.status === 'fulfilled') courses.value = coursesResult.value
    const rejected = [healthResult, agentsResult, tasksResult, profilesResult, coursesResult].find(
      (item) => item.status === 'rejected',
    )
    if (rejected?.status === 'rejected') error.value = rejected.reason instanceof Error ? rejected.reason.message : '部分接口不可用'
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
          <StatusPill :status="health?.status || 'UNKNOWN'" :tone="health?.status === 'UP' ? 'ok' : 'warn'" />
          <p>{{ health?.service || 'software-cup-learning-backend' }}</p>
          <small>{{ formatDate(String(health?.timestamp || '')) }}</small>
        </div>
        <div class="timeline-body">
          <h3>演示主链路</h3>
          <p>画像 -> 资源生成 -> 多智能体过程 -> 防幻觉审计 -> 学习闭环 -> 评委报告</p>
          <StatusPill status="Vue3 主程已接入" tone="info" />
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

    <SectionPanel class="span-12" title="演示入口">
      <div class="button-row">
        <RouterLink class="button" to="/profiles"><Activity :size="17" />创建画像</RouterLink>
        <RouterLink class="button" to="/generation"><Activity :size="17" />生成资源</RouterLink>
        <RouterLink class="button" to="/learning"><Activity :size="17" />学习闭环</RouterLink>
        <RouterLink class="button" to="/demo"><Activity :size="17" />评委模式</RouterLink>
      </div>
    </SectionPanel>
  </div>
</template>
