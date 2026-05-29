<script setup lang="ts">
import type { EChartsOption } from 'echarts'
import { Download, FileText, Printer, RefreshCw } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { coursesApi, demoApi, profilesApi, tasksApi } from '@/api'
import ChartPanel from '@/components/ChartPanel.vue'
import DemoPrepChecklist from '@/components/DemoPrepChecklist.vue'
import ErrorNotice from '@/components/ErrorNotice.vue'
import JsonBlock from '@/components/JsonBlock.vue'
import LoadingBlock from '@/components/LoadingBlock.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import StatusPill from '@/components/StatusPill.vue'
import type { ContestReadinessReport, ContestRequirementEvidence, Course, GenerationTask, ProfileResponse } from '@/types/api'
import { downloadJson, downloadText, safeFilePart } from '@/utils/download'
import { compact, formatDate, percent } from '@/utils/format'

const loading = ref(false)
const reportLoading = ref(false)
const error = ref('')
const profiles = ref<ProfileResponse[]>([])
const courses = ref<Course[]>([])
const tasks = ref<GenerationTask[]>([])
const report = ref<ContestReadinessReport | null>(null)

const studentProfileId = ref('')
const courseId = ref('')
const taskId = ref('')

const selectedProfile = computed(() => profiles.value.find((item) => item.id === studentProfileId.value))
const selectedCourse = computed(() => courses.value.find((item) => item.id === courseId.value))
const selectedTask = computed(() => tasks.value.find((item) => item.id === taskId.value))

function metricNumber(key: string) {
  const value = report.value?.metrics?.[key]
  const numeric = Number(value ?? 0)
  return Number.isFinite(numeric) ? numeric : 0
}

function statusTone(status?: string): 'ok' | 'warn' | 'danger' | 'info' | 'muted' {
  const value = String(status || '').toUpperCase()
  if (['ACHIEVED', 'SUCCEEDED', 'PASS', 'PASSED', 'READY'].includes(value)) return 'ok'
  if (['FAILED', 'MISSING', 'BLOCKED', 'RISK'].includes(value)) return 'danger'
  if (['PARTIAL', 'PENDING', 'UNKNOWN'].includes(value)) return 'warn'
  return 'info'
}

const readinessLevel = computed(() => {
  const score = report.value?.overallScore ?? 0
  if (score >= 90) return '答辩就绪'
  if (score >= 75) return '基本就绪'
  if (score >= 60) return '需要补证据'
  return '待完善'
})

const readinessTone = computed(() => {
  const score = report.value?.overallScore ?? 0
  if (score >= 85) return 'ok'
  if (score >= 60) return 'warn'
  return 'danger'
})

const coreMetrics = computed(() => [
  { key: 'enabledAgentCount', label: '多智能体数量', value: metricNumber('enabledAgentCount'), target: 8 },
  { key: 'resourceTypeCount', label: '资源类型覆盖', value: metricNumber('resourceTypeCount'), target: 5 },
  { key: 'learningEventCount', label: '学习闭环证据', value: metricNumber('learningEventCount'), target: 1 },
  { key: 'generationAuditCount', label: '防幻觉审核', value: metricNumber('generationAuditCount'), target: 1 },
])

const requirementOption = computed<EChartsOption>(() => ({
  tooltip: {},
  graphic: report.value?.requirements?.length
    ? undefined
    : { type: 'text', left: 'center', top: 'middle', style: { text: '等待评委报告', fill: '#61708a' } },
  grid: { left: 120, right: 20, top: 20, bottom: 30 },
  xAxis: { type: 'value', max: 100 },
  yAxis: {
    type: 'category',
    data: report.value?.requirements.map((item) => compact(item.title, 12)) || [],
  },
  series: [
    {
      type: 'bar',
      data: report.value?.requirements.map((item) => Math.round(percent(item.score))) || [],
      itemStyle: { color: '#2f6fef', borderRadius: [0, 4, 4, 0] },
    },
  ],
}))

const metricOption = computed<EChartsOption>(() => ({
  tooltip: {},
  graphic: report.value
    ? undefined
    : { type: 'text', left: 'center', top: 'middle', style: { text: '等待指标数据', fill: '#61708a' } },
  grid: { left: 36, right: 18, top: 24, bottom: 50 },
  xAxis: {
    type: 'category',
    data: coreMetrics.value.map((item) => item.label),
    axisLabel: { interval: 0, rotate: 18 },
  },
  yAxis: { type: 'value', minInterval: 1 },
  series: [
    {
      type: 'bar',
      data: coreMetrics.value.map((item) => item.value),
      itemStyle: { color: '#0e7490', borderRadius: [4, 4, 0, 0] },
    },
  ],
}))

const coverageOption = computed<EChartsOption>(() => ({
  tooltip: {},
  radar: {
    indicator: coreMetrics.value.map((item) => ({ name: item.label, max: Math.max(item.target, item.value, 1) })),
    radius: '62%',
  },
  series: [
    {
      type: 'radar',
      areaStyle: { opacity: 0.16 },
      data: [{ name: '证据覆盖', value: coreMetrics.value.map((item) => item.value) }],
    },
  ],
}))

async function loadOptions() {
  loading.value = true
  error.value = ''
  const [profileResult, courseResult, taskResult] = await Promise.allSettled([
    profilesApi.list(),
    coursesApi.list(),
    tasksApi.list(),
  ])
  profiles.value = profileResult.status === 'fulfilled' ? profileResult.value : []
  courses.value = courseResult.status === 'fulfilled' ? courseResult.value : []
  tasks.value = taskResult.status === 'fulfilled' ? taskResult.value : []
  studentProfileId.value ||= profiles.value[0]?.id || ''
  courseId.value ||= courses.value[0]?.id || ''
  taskId.value ||= tasks.value[0]?.id || ''
  const failures = [profileResult, courseResult, taskResult].filter((item) => item.status === 'rejected').length
  if (failures) error.value = '评委模式基础选项暂不可用，请确认后端服务后刷新。'
  loading.value = false
  await loadReport()
}

async function loadReport() {
  reportLoading.value = true
  error.value = ''
  try {
    report.value = await demoApi.readinessReport({
      studentProfileId: studentProfileId.value || undefined,
      courseId: courseId.value || undefined,
      taskId: taskId.value || undefined,
    })
  } catch (err) {
    report.value = null
    error.value = `后端未生成评委报告：${err instanceof Error ? err.message : '请启动 Spring Boot 后端并刷新'}`
  } finally {
    reportLoading.value = false
  }
}

function requirementMarkdown(item: ContestRequirementEvidence) {
  return [
    `### ${item.title}`,
    '',
    `- 状态：${item.status}`,
    `- 得分：${item.score}`,
    `- 目标：${item.target || '-'}`,
    `- 实际：${item.actual || '-'}`,
    `- 证据接口：${item.evidenceEndpoints.length ? item.evidenceEndpoints.join('、') : '-'}`,
    `- 证据说明：${item.evidenceNotes.length ? item.evidenceNotes.join('；') : '-'}`,
  ].join('\n')
}

function markdownReport() {
  if (!report.value) return ''
  return [
    '# 软件杯 A3 评委模式报告',
    '',
    `- 总分：${report.value.overallScore}`,
    `- 就绪状态：${readinessLevel.value}`,
    `- 范围：${report.value.scope}`,
    `- 生成时间：${formatDate(report.value.generatedAt)}`,
    `- 学生：${selectedProfile.value?.studentName || '全部'}`,
    `- 课程：${selectedCourse.value?.title || '全部'}`,
    `- 任务：${selectedTask.value?.topic || '全部'}`,
    '',
    '## 总结',
    report.value.summary || '暂无总结',
    '',
    '## 核心指标',
    ...coreMetrics.value.map((item) => `- ${item.label}：${item.value} / 目标 ${item.target}`),
    '',
    '## 赛题要求完成度',
    ...report.value.requirements.map(requirementMarkdown),
    '',
    '## 推荐演示顺序',
    ...(report.value.recommendedDemoFlow.length
      ? report.value.recommendedDemoFlow.map((item, index) => `${index + 1}. ${item}`)
      : ['暂无推荐演示顺序']),
    '',
    '## 演示亮点',
    ...(report.value.demoHighlights.length ? report.value.demoHighlights.map((item) => `- ${item}`) : ['暂无演示亮点']),
  ].join('\n')
}

function escapeHtml(value: unknown) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function printableHtml() {
  if (!report.value) return ''
  const requirementRows = report.value.requirements
    .map(
      (item) => `
        <tr>
          <td>${escapeHtml(item.title)}</td>
          <td>${escapeHtml(item.status)}</td>
          <td>${escapeHtml(item.score)}</td>
          <td>${escapeHtml(item.actual)}</td>
          <td>${escapeHtml(item.evidenceEndpoints.join(' / '))}</td>
        </tr>`,
    )
    .join('')
  const flow = report.value.recommendedDemoFlow.map((item, index) => `<li>${index + 1}. ${escapeHtml(item)}</li>`).join('')
  const highlights = report.value.demoHighlights.map((item) => `<li>${escapeHtml(item)}</li>`).join('')
  return `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>软件杯评委模式报告</title>
  <style>
    body { font-family: "Microsoft YaHei", Arial, sans-serif; margin: 32px; color: #172033; }
    h1 { margin-bottom: 8px; }
    .meta, .cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 18px 0; }
    .card { border: 1px solid #dbe3ef; border-radius: 8px; padding: 12px; background: #f8fbff; }
    .score { font-size: 42px; font-weight: 800; color: #1d4ed8; }
    table { width: 100%; border-collapse: collapse; margin-top: 14px; }
    th, td { border: 1px solid #dbe3ef; padding: 8px; text-align: left; vertical-align: top; }
    th { background: #f5f8fc; }
    @media print { body { margin: 18mm; } .card { break-inside: avoid; } }
  </style>
</head>
<body>
  <h1>软件杯 A3 评委模式报告</h1>
  <p>${escapeHtml(report.value.summary || '暂无总结')}</p>
  <div class="meta">
    <div class="card"><strong>总分</strong><div class="score">${escapeHtml(report.value.overallScore)}</div></div>
    <div class="card"><strong>学生</strong><p>${escapeHtml(selectedProfile.value?.studentName || '全部')}</p></div>
    <div class="card"><strong>课程</strong><p>${escapeHtml(selectedCourse.value?.title || '全部')}</p></div>
    <div class="card"><strong>任务</strong><p>${escapeHtml(selectedTask.value?.topic || '全部')}</p></div>
  </div>
  <div class="cards">
    ${coreMetrics.value.map((item) => `<div class="card"><strong>${escapeHtml(item.label)}</strong><p>${escapeHtml(item.value)} / ${escapeHtml(item.target)}</p></div>`).join('')}
  </div>
  <h2>赛题要求完成度</h2>
  <table>
    <thead><tr><th>要求</th><th>状态</th><th>得分</th><th>实际证据</th><th>接口证据</th></tr></thead>
    <tbody>${requirementRows}</tbody>
  </table>
  <h2>推荐演示顺序</h2>
  <ol>${flow}</ol>
  <h2>演示亮点</h2>
  <ul>${highlights}</ul>
</body>
</html>`
}

function downloadReportJson() {
  downloadJson('contest-readiness-report.json', report.value)
}

function downloadReportMarkdown() {
  downloadText('contest-readiness-report.md', markdownReport(), 'text/markdown;charset=utf-8')
}

function downloadReportHtml() {
  downloadText('contest-readiness-report.html', printableHtml(), 'text/html;charset=utf-8')
}

onMounted(loadOptions)
</script>

<template>
  <div class="page-grid demo-page">
    <SectionPanel class="span-12" title="评委模式" subtitle="GET /api/demo/readiness-report">
      <template #actions>
        <button class="ghost-button" @click="loadReport"><RefreshCw :size="17" />生成报告</button>
        <button class="ghost-button" :disabled="!report" @click="downloadReportJson">
          <Download :size="17" />JSON
        </button>
        <button class="ghost-button" :disabled="!report" @click="downloadReportMarkdown">
          <FileText :size="17" />Markdown
        </button>
        <button class="ghost-button" :disabled="!report" @click="downloadReportHtml">
          <Printer :size="17" />可打印 HTML
        </button>
      </template>
      <ErrorNotice :message="error" />
      <LoadingBlock :show="loading || reportLoading" />
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
      <div v-if="!report && !reportLoading" class="notice warn-notice">
        <span>后端未生成评委报告：请启动 Spring Boot 后端，确认已有画像、课程、任务和学习证据后点击“生成报告”。</span>
      </div>
    </SectionPanel>

    <section class="demo-hero span-12">
      <div>
        <span>答辩首页</span>
        <h2>{{ readinessLevel }}</h2>
        <p>{{ report?.summary || '等待后端生成评委报告。页面会汇总赛题要求完成度、多智能体证据、资源覆盖和学习闭环证据。' }}</p>
      </div>
      <div class="score-ring">
        <strong>{{ report?.overallScore ?? '-' }}</strong>
        <small>overallScore</small>
        <StatusPill :status="readinessLevel" :tone="readinessTone" />
      </div>
    </section>

    <SectionPanel class="span-12" title="演示准备清单">
      <DemoPrepChecklist />
    </SectionPanel>

    <article v-for="item in coreMetrics" :key="item.key" class="metric-tile span-3">
      <span>{{ item.label }}</span>
      <strong>{{ report ? item.value : '-' }}</strong>
      <small>目标 {{ item.target }}</small>
    </article>

    <SectionPanel class="span-6" title="赛题要求完成度">
      <ChartPanel :option="requirementOption" :height="360" />
    </SectionPanel>
    <SectionPanel class="span-3" title="证据数量">
      <ChartPanel :option="metricOption" :height="360" />
    </SectionPanel>
    <SectionPanel class="span-3" title="覆盖雷达">
      <ChartPanel :option="coverageOption" :height="360" />
    </SectionPanel>

    <SectionPanel class="span-8" title="要求证据卡">
      <div v-if="!report?.requirements.length" class="empty-guide">
        <strong>等待要求证据</strong>
        <span>生成评委报告后，这里会展示 requirement cards、完成状态、实际证据和接口证据。</span>
      </div>
      <div v-else class="requirement-grid">
        <article v-for="item in report.requirements" :key="item.requirementCode" class="requirement-card">
          <div class="section-head">
            <div>
              <strong>{{ item.title }}</strong>
              <p>{{ item.category }} / {{ item.requirementCode }}</p>
            </div>
            <StatusPill :status="item.status" :tone="statusTone(item.status)" />
          </div>
          <div class="progress-track"><div class="progress-fill" :style="{ width: `${Math.round(percent(item.score))}%` }" /></div>
          <p>{{ item.actual || item.target }}</p>
          <div class="endpoint-list">
            <span v-for="endpoint in item.evidenceEndpoints" :key="endpoint">{{ endpoint }}</span>
            <small v-if="!item.evidenceEndpoints.length">暂无 evidence endpoint</small>
          </div>
          <small>{{ item.evidenceNotes.join('；') }}</small>
        </article>
      </div>
    </SectionPanel>

    <SectionPanel class="span-4" title="推荐演示流">
      <div v-if="!report?.recommendedDemoFlow.length" class="empty-guide">
        <strong>等待推荐演示顺序</strong>
        <span>报告生成后会给出评委模式下的推荐讲解路径。</span>
      </div>
      <div v-else class="timeline">
        <div v-for="(item, index) in report.recommendedDemoFlow" :key="item" class="timeline-item">
          <span class="timeline-index">{{ index + 1 }}</span>
          <div class="timeline-body">{{ item }}</div>
        </div>
      </div>
    </SectionPanel>

    <SectionPanel class="span-5" title="演示亮点">
      <div v-if="!report?.demoHighlights.length" class="empty-guide">
        <strong>等待演示亮点</strong>
        <span>生成报告后会总结画像、资源、多智能体、审计和学习闭环亮点。</span>
      </div>
      <div v-else class="timeline">
        <div v-for="item in report.demoHighlights" :key="item" class="timeline-body">{{ item }}</div>
      </div>
    </SectionPanel>

    <SectionPanel class="span-7" title="证据端点总览">
      <div v-if="!report?.requirements.length" class="empty-guide">
        <strong>暂无证据端点</strong>
        <span>报告生成后按赛题要求汇总后端接口证据。</span>
      </div>
      <div v-else class="endpoint-list endpoint-list-wide">
        <template v-for="item in report.requirements" :key="item.requirementCode">
          <span v-for="endpoint in item.evidenceEndpoints" :key="`${item.requirementCode}-${endpoint}`">{{ endpoint }}</span>
        </template>
      </div>
    </SectionPanel>

    <SectionPanel class="span-12" title="原始报告 JSON">
      <JsonBlock :value="report" />
    </SectionPanel>
  </div>
</template>
