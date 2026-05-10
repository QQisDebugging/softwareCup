<script setup lang="ts">
import type { EChartsOption } from 'echarts'
import { Download, FileText, RefreshCw } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { coursesApi, demoApi, profilesApi, tasksApi } from '@/api'
import ChartPanel from '@/components/ChartPanel.vue'
import DemoPrepChecklist from '@/components/DemoPrepChecklist.vue'
import ErrorNotice from '@/components/ErrorNotice.vue'
import JsonBlock from '@/components/JsonBlock.vue'
import LoadingBlock from '@/components/LoadingBlock.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import StatusPill from '@/components/StatusPill.vue'
import type { ContestReadinessReport, Course, GenerationTask, ProfileResponse } from '@/types/api'
import { downloadJson, downloadText } from '@/utils/download'

const loading = ref(false)
const error = ref('')
const profiles = ref<ProfileResponse[]>([])
const courses = ref<Course[]>([])
const tasks = ref<GenerationTask[]>([])
const report = ref<ContestReadinessReport | null>(null)

const studentProfileId = ref('')
const courseId = ref('')
const taskId = ref('')

const requirementOption = computed<EChartsOption>(() => ({
  tooltip: {},
  graphic: report.value?.requirements?.length
    ? undefined
    : { type: 'text', left: 'center', top: 'middle', style: { text: '等待评委报告', fill: '#61708a' } },
  grid: { left: 110, right: 18, top: 20, bottom: 30 },
  xAxis: { type: 'value', max: 100 },
  yAxis: { type: 'category', data: report.value?.requirements.map((item) => item.title) || [] },
  series: [
    {
      type: 'bar',
      data: report.value?.requirements.map((item) => item.score) || [],
      itemStyle: { color: '#2f6fef', borderRadius: [0, 4, 4, 0] },
    },
  ],
}))

const metricOption = computed<EChartsOption>(() => {
  const metrics = report.value?.metrics || {}
  const picked = ['enabledAgentCount', 'resourceTypeCount', 'profileDimensionCount', 'generationAuditCount', 'learningEventCount']
  return {
    tooltip: {},
    graphic: report.value ? undefined : { type: 'text', left: 'center', top: 'middle', style: { text: '等待指标数据', fill: '#61708a' } },
    xAxis: { type: 'category', data: picked },
    yAxis: { type: 'value' },
    series: [{ type: 'bar', data: picked.map((key) => Number(metrics[key] || 0)), itemStyle: { color: '#0e7490' } }],
  }
})

async function loadOptions() {
  loading.value = true
  try {
    const [profileList, courseList, taskList] = await Promise.all([profilesApi.list(), coursesApi.list(), tasksApi.list()])
    profiles.value = profileList
    courses.value = courseList
    tasks.value = taskList
    studentProfileId.value ||= profileList[0]?.id || ''
    courseId.value ||= courseList[0]?.id || ''
    taskId.value ||= taskList[0]?.id || ''
    await loadReport()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '评委模式加载失败'
  } finally {
    loading.value = false
  }
}

async function loadReport() {
  error.value = ''
  try {
    report.value = await demoApi.readinessReport({
      studentProfileId: studentProfileId.value || undefined,
      courseId: courseId.value || undefined,
      taskId: taskId.value || undefined,
    })
  } catch (err) {
    error.value = err instanceof Error ? err.message : '评委报告生成失败'
  }
}

function markdownReport() {
  if (!report.value) return ''
  return [
    `# 软件杯 A3 评委模式报告`,
    '',
    `总分：${report.value.overallScore}`,
    '',
    report.value.summary,
    '',
    '## 达成项',
    ...report.value.requirements.map((item) => `- ${item.title}: ${item.status} / ${item.score}\n  - ${item.actual}`),
    '',
    '## 推荐演示顺序',
    ...report.value.recommendedDemoFlow.map((item, index) => `${index + 1}. ${item}`),
    '',
    '## 亮点',
    ...report.value.demoHighlights.map((item) => `- ${item}`),
  ].join('\n')
}

onMounted(loadOptions)
</script>

<template>
  <div class="page-grid">
    <SectionPanel class="span-12" title="评委模式" subtitle="GET /api/demo/readiness-report">
      <template #actions>
        <button class="ghost-button" @click="loadReport"><RefreshCw :size="17" />生成报告</button>
        <button class="ghost-button" :disabled="!report" @click="downloadJson('contest-readiness-report.json', report)">
          <Download :size="17" />JSON
        </button>
        <button class="ghost-button" :disabled="!report" @click="downloadText('contest-readiness-report.md', markdownReport(), 'text/markdown;charset=utf-8')">
          <FileText :size="17" />Markdown
        </button>
      </template>
      <ErrorNotice :message="error" />
      <LoadingBlock :show="loading" />
      <div class="page-grid">
        <div class="field span-4">
          <label>学生</label>
          <select v-model="studentProfileId">
            <option value="">全部</option>
            <option v-for="profile in profiles" :key="profile.id" :value="profile.id">{{ profile.studentName }}</option>
          </select>
        </div>
        <div class="field span-4">
          <label>课程</label>
          <select v-model="courseId">
            <option value="">全部</option>
            <option v-for="course in courses" :key="course.id" :value="course.id">{{ course.title }}</option>
          </select>
        </div>
        <div class="field span-4">
          <label>任务</label>
          <select v-model="taskId">
            <option value="">全部</option>
            <option v-for="task in tasks" :key="task.id" :value="task.id">{{ task.topic }}</option>
          </select>
        </div>
      </div>
    </SectionPanel>

    <SectionPanel class="span-12" title="演示准备清单">
      <DemoPrepChecklist />
    </SectionPanel>

    <article class="metric-tile span-3">
      <span>总分</span>
      <strong>{{ report?.overallScore ?? '-' }}</strong>
      <small>{{ report?.scope || '等待生成' }}</small>
    </article>
    <article class="metric-tile span-3">
      <span>智能体</span>
      <strong>{{ report?.metrics.enabledAgentCount ?? '-' }}</strong>
      <small>启用定义</small>
    </article>
    <article class="metric-tile span-3">
      <span>资源类型</span>
      <strong>{{ report?.metrics.resourceTypeCount ?? '-' }}</strong>
      <small>覆盖类型</small>
    </article>
    <article class="metric-tile span-3">
      <span>审核证据</span>
      <strong>{{ report?.metrics.generationAuditCount ?? '-' }}</strong>
      <small>防幻觉记录</small>
    </article>

    <SectionPanel class="span-7" title="赛题要求完成度">
      <ChartPanel :option="requirementOption" :height="360" />
    </SectionPanel>
    <SectionPanel class="span-5" title="证据数量">
      <ChartPanel :option="metricOption" :height="360" />
    </SectionPanel>

    <SectionPanel class="span-7" title="要求证据卡">
      <div v-if="!report" class="empty-state">等待报告</div>
      <div v-else class="timeline">
        <div v-for="item in report.requirements" :key="item.requirementCode" class="timeline-body">
          <div class="section-head">
            <div>
              <strong>{{ item.title }}</strong>
              <p>{{ item.target }}</p>
            </div>
            <StatusPill :status="item.status" :tone="item.status === 'ACHIEVED' ? 'ok' : 'warn'" />
          </div>
          <p>{{ item.actual }}</p>
          <small>{{ item.evidenceEndpoints.join(' / ') }}</small>
        </div>
      </div>
    </SectionPanel>

    <SectionPanel class="span-5" title="推荐演示流">
      <div v-if="!report" class="empty-state">等待报告</div>
      <div v-else class="timeline">
        <div v-for="(item, index) in report.recommendedDemoFlow" :key="item" class="timeline-item">
          <span class="timeline-index">{{ index + 1 }}</span>
          <div class="timeline-body">{{ item }}</div>
        </div>
      </div>
    </SectionPanel>

    <SectionPanel class="span-12" title="原始报告 JSON">
      <JsonBlock :value="report" />
    </SectionPanel>
  </div>
</template>
