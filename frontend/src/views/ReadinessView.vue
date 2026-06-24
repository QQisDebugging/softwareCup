<script setup lang="ts">
import {
  BookMarked,
  CircleDashed,
  CircleCheck,
  Download,
  FileText,
  RefreshCw,
  Route,
  Sparkles,
} from 'lucide-vue-next'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { coursesApi, profilesApi, qualityApi, tasksApi } from '@/api'
import ErrorNotice from '@/components/ErrorNotice.vue'
import LoadingBlock from '@/components/LoadingBlock.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import StatusPill from '@/components/StatusPill.vue'
import type { Course, ContestReadinessReport, ContestRequirementEvidence, GenerationTask, ProfileResponse } from '@/types/api'
import { downloadJson, downloadText, safeFilePart } from '@/utils/download'
import { cleanDisplayText, formatDate, percent } from '@/utils/format'

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
const route = useRoute()
const router = useRouter()

const selectedProfile = computed(() => profiles.value.find((item) => item.id === studentProfileId.value))
const selectedCourse = computed(() => courses.value.find((item) => item.id === courseId.value))
const selectedTask = computed(() => tasks.value.find((item) => item.id === taskId.value))
const scopedTasks = computed(() => tasks.value.filter((task) => !courseId.value || task.courseId === courseId.value))
const selectedTaskSummary = computed(() => {
  if (!selectedTask.value) return '未限定任务，质检会按当前画像和课程范围汇总。'
  return `${selectedTask.value.topic} / ${selectedTask.value.status} / ${selectedTask.value.progressPercent || 0}%`
})

const readinessLevel = computed(() => {
  const score = report.value?.overallScore || 0
  if (score >= 90) return '发布质量达标'
  if (score >= 75) return '可发布需复核'
  if (score >= 60) return '需补齐关键证据'
  return '暂不建议发布'
})

function statusTone(status?: string): 'ok' | 'warn' | 'danger' | 'info' | 'muted' {
  const value = String(status || '').toUpperCase()
  if (['EXCELLENT', 'SUCCEEDED', 'PASS', 'PASSED', 'READY'].includes(value)) return 'ok'
  if (['FAILED', 'MISSING', 'BLOCKED', 'RISK', 'DEMO_DATA_NEEDED'].includes(value)) return 'danger'
  if (['PARTIAL', 'PENDING', 'UNKNOWN'].includes(value)) return 'warn'
  return 'info'
}

const readinessTone = computed(() => {
  const score = report.value?.overallScore || 0
  if (score >= 85) return 'ok'
  if (score >= 65) return 'warn'
  return 'danger'
})

const metricCards = computed(() => {
  const metrics = report.value?.metrics
  return [
    { key: 'enabledAgentCount', label: '多智能体', value: metrics?.enabledAgentCount || 0, target: 8 },
    { key: 'resourceTypeCount', label: '资源类型', value: metrics?.resourceTypeCount || 0, target: 5 },
    { key: 'taskCount', label: '任务完成', value: metrics?.successfulTaskCount || 0, target: 1 },
    { key: 'learningPathCount', label: '学习路径', value: metrics?.learningPathCount || 0, target: 1 },
    { key: 'learningEventCount', label: '学习事件', value: metrics?.learningEventCount || 0, target: 1 },
    { key: 'generationAuditCount', label: '内容审核', value: metrics?.generationAuditCount || 0, target: 1 },
  ]
})

const evidenceCoverage = computed(() => {
  if (!report.value?.requirements?.length) return [] as ContestRequirementEvidence[]
  return report.value.requirements
})

const endpointList = computed(() => {
  if (!report.value?.requirements?.length) return [] as string[]
  return [...new Set(report.value.requirements.flatMap((item) => item.evidenceEndpoints || []))].filter(Boolean)
})
const qualitySummary = computed(() => cleanDisplayText(report.value?.summary || ''))
const qualityFlow = computed(() => (report.value?.recommendedDemoFlow || []).map((item) => cleanDisplayText(item)).filter(Boolean))
const qualityHighlights = computed(() => (report.value?.demoHighlights || []).map((item) => cleanDisplayText(item)).filter(Boolean))

function exportMarkdown() {
  if (!report.value) return
  const rows = report.value.requirements
    .map(
      (item) =>
        `- ${cleanDisplayText(item.title)}：${item.status}（${item.score}）实际证据: ${cleanDisplayText(item.actual || '-')}；目标: ${cleanDisplayText(
          item.target || '-',
        )}；接口: ${item.evidenceEndpoints.join('；') || '-'}`,
    )
    .join('\n')
  const text = [
    '# 智学工坊发布质检报告',
    `- 生成时间：${formatDate(report.value.generatedAt)}`,
    `- 范围：${cleanDisplayText(report.value.scope || '-')}`,
    `- 总分：${report.value.overallScore}`,
    `- 状态：${readinessLevel.value}`,
    '',
    '## 快照',
    (qualitySummary.value || '无摘要').replace(/\\s+/g, ' '),
    '',
    '## 关键指标',
    ...metricCards.value.map((item) => `- ${item.label}：${item.value}/${item.target}`),
    '',
    '## 关键要求',
    rows || '- 尚未生成',
    '',
    '## 建议处理顺序',
    ...(qualityFlow.value.length
      ? qualityFlow.value.map((item, index) => `${index + 1}. ${item}`)
      : ['- 尚未生成']),
  ].join('\n')
  void downloadText(`${safeFilePart('zhixue-quality-report')}.md`, text, 'text/markdown;charset=utf-8')
}

function exportHtml() {
  if (!report.value) return
  const requirementRows = report.value.requirements
    .map(
      (item) => `<tr><td>${escapeHtml(cleanDisplayText(item.title))}</td><td>${escapeHtml(item.status)}</td><td>${escapeHtml(String(item.score))}</td><td>${escapeHtml(
        cleanDisplayText(item.actual),
      )}</td><td>${escapeHtml(item.evidenceEndpoints.join(' / '))}</td></tr>`,
    )
    .join('')
  const flow = qualityFlow.value.map((item, index) => `<li>${index + 1}. ${escapeHtml(item)}</li>`).join('')
  const raw = `<!doctype html><html lang="zh"><head><meta charset="utf-8"/><title>智学工坊发布质检报告</title><style>body{font-family:Arial, sans-serif;padding:24px;color:#172033}table{border-collapse:collapse;width:100%}th,td{border:1px solid #dbe3ef;padding:8px}th{background:#eef5ff}</style></head><body><h1>智学工坊发布质检报告</h1><p>${escapeHtml(
      qualitySummary.value || '',
  )}</p><div><strong>质量分：</strong>${report.value.overallScore}</div><div><strong>范围：</strong>${escapeHtml(cleanDisplayText(report.value.scope || ''))}</div><h2>建议处理顺序</h2><ol>${flow}</ol><h2>要求完成情况</h2><table><thead><tr><th>要求</th><th>状态</th><th>得分</th><th>实际</th><th>证据端点</th></tr></thead><tbody>${requirementRows}</tbody></table></body></html>`
  void downloadText(`${safeFilePart('zhixue-quality-report')}.html`, raw, 'text/html;charset=utf-8')
}

function escapeHtml(value: unknown) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

async function loadOptions() {
  loading.value = true
  error.value = ''
  try {
    const [profileResult, courseResult, taskResult] = await Promise.allSettled([profilesApi.list(), coursesApi.list(), tasksApi.list()])
    profiles.value = profileResult.status === 'fulfilled' ? profileResult.value : []
    courses.value = courseResult.status === 'fulfilled' ? courseResult.value : []
    tasks.value = taskResult.status === 'fulfilled' ? taskResult.value : []
    applyRouteScope()
    studentProfileId.value ||= profiles.value[0]?.id || ''
    courseId.value ||= courses.value[0]?.id || ''
    taskId.value ||= scopedTasks.value[0]?.id || tasks.value[0]?.id || ''
    if (profileResult.status === 'rejected' || courseResult.status === 'rejected' || taskResult.status === 'rejected') {
      error.value = '读取基础数据失败，请确认后端服务在线后重试'
    }
    await loadReport()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '读取基础数据失败'
  } finally {
    loading.value = false
  }
}

async function loadReport() {
  reportLoading.value = true
  error.value = ''
  try {
    report.value = await qualityApi.getReadinessReport({
      studentProfileId: studentProfileId.value || undefined,
      courseId: courseId.value || undefined,
      taskId: taskId.value || undefined,
    })
  } catch (err) {
    report.value = null
    error.value = `未生成体检报告：${err instanceof Error ? err.message : '接口不可达'}`
  } finally {
    reportLoading.value = false
  }
}

function applyRouteScope() {
  const queryCourseId = typeof route.query.courseId === 'string' ? route.query.courseId : ''
  const queryTaskId = typeof route.query.taskId === 'string' ? route.query.taskId : ''
  if (queryCourseId) courseId.value = queryCourseId
  if (queryTaskId) taskId.value = queryTaskId
}

async function reloadTasksAndReport() {
  await loadOptions()
}

async function openSelectedTaskReview() {
  if (!taskId.value) {
    error.value = '请先选择一个资源任务，再进入任务审核详情。'
    return
  }
  await router.push(`/tasks/${taskId.value}`)
}

async function openResourceReview() {
  await router.push({
    path: '/generation',
    query: {
      ...(courseId.value ? { courseId: courseId.value } : {}),
      ...(taskId.value ? { taskId: taskId.value } : {}),
    },
  })
}

watch(
  () => [route.query.courseId, route.query.taskId],
  () => {
    applyRouteScope()
    void loadReport()
  },
)

watch(courseId, () => {
  if (taskId.value && !scopedTasks.value.some((task) => task.id === taskId.value)) {
    taskId.value = scopedTasks.value[0]?.id || ''
  }
})

onMounted(loadOptions)
</script>

<template>
  <div class="page-grid">
    <SectionPanel class="span-12" title="发布质检">
      <template #actions>
        <button class="ghost-button" :disabled="loading" @click="reloadTasksAndReport"><RefreshCw :size="17" />加载任务</button>
        <button class="ghost-button" @click="loadReport"><Sparkles :size="17" />重新生成质检</button>
        <button class="ghost-button" :disabled="!taskId" @click="openSelectedTaskReview"><Route :size="17" />进入任务审核</button>
        <button class="button" @click="openResourceReview"><CircleCheck :size="17" />回到资源审核</button>
        <button class="ghost-button" :disabled="!report" @click="() => void exportMarkdown()"><FileText :size="17" />导出 Markdown</button>
        <button class="ghost-button" :disabled="!report" @click="() => void exportHtml()"><FileText :size="17" />导出 HTML</button>
        <button class="ghost-button" :disabled="!report" @click="() => void downloadJson(`${safeFilePart('zhixue-quality-report')}.json`, report)"><Download :size="17" />导出 JSON</button>
      </template>
      <ErrorNotice :message="error" />
      <LoadingBlock :show="loading || reportLoading" />
      <div class="page-grid">
        <div class="field span-4">
          <label>学生画像</label>
          <select v-model="studentProfileId">
            <option value="">全部</option>
            <option v-for="item in profiles" :key="item.id" :value="item.id">{{ item.studentName }}</option>
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
            <option v-for="task in scopedTasks" :key="task.id" :value="task.id">{{ task.topic }}</option>
          </select>
          <small>{{ selectedTaskSummary }}</small>
        </div>
      </div>
    </SectionPanel>

    <section class="contest-hero span-12">
      <div>
        <span class="contest-eyebrow">发布质检</span>
        <h2>{{ readinessLevel }}</h2>
        <p v-if="qualitySummary">{{ qualitySummary }}</p>
      </div>
      <div class="score-ring">
        <strong>{{ report?.overallScore ?? '-' }}</strong>
        <small>质量分</small>
        <StatusPill :status="readinessLevel" :tone="readinessTone" />
      </div>
    </section>

    <article v-for="item in metricCards" :key="item.key" class="metric-tile span-2">
      <span>{{ item.label }}</span>
      <strong>{{ report ? item.value : '-' }}</strong>
      <small>目标 {{ item.target }}</small>
    </article>

    <SectionPanel class="span-8" title="需求完成度">
      <div v-if="!evidenceCoverage.length" class="empty-guide">
        <strong>尚未生成体检</strong>
      </div>
      <div v-else class="requirement-grid">
        <article v-for="req in evidenceCoverage" :key="req.requirementCode" class="requirement-card">
          <div class="section-head">
            <div>
              <strong>{{ cleanDisplayText(req.title) }}</strong>
              <p>{{ cleanDisplayText(req.category) }} / {{ req.requirementCode }}</p>
            </div>
            <StatusPill :status="req.status" :tone="statusTone(req.status)" />
          </div>
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: `${percent(req.score)}%` }" />
          </div>
          <p>{{ cleanDisplayText(req.actual || req.target) }}</p>
          <div class="evidence-chip-grid">
            <span v-for="endpoint in req.evidenceEndpoints" :key="endpoint">{{ endpoint }}</span>
            <small v-if="!req.evidenceEndpoints.length">无证据端点</small>
          </div>
          <small>{{ req.evidenceNotes.map((item) => cleanDisplayText(item)).join('；') || '暂无证据说明' }}</small>
        </article>
      </div>
    </SectionPanel>

    <SectionPanel class="span-4" title="建议处理顺序">
      <div v-if="!qualityFlow.length" class="empty-guide">
        <strong>尚未生成处理顺序</strong>
      </div>
      <div v-else class="timeline">
        <div v-for="(item, index) in qualityFlow" :key="item" class="timeline-item">
          <span class="timeline-index">{{ index + 1 }}</span>
          <div class="timeline-body">
            <Sparkles :size="15" />
            <span>{{ item }}</span>
          </div>
        </div>
      </div>
      <Route class="timeline-icon" :size="16" />
    </SectionPanel>

    <SectionPanel class="span-6" title="可用能力与建议">
      <ul class="evidence-list">
        <li v-for="item in qualityHighlights" :key="item">{{ item }}</li>
        <li v-if="!qualityHighlights.length">当前尚未生成建议</li>
      </ul>
      <div class="contest-chip-row" aria-label="证据端点总览">
        <span v-for="entry in endpointList" :key="entry">{{ entry }}</span>
        <span v-if="!endpointList.length">暂无端点</span>
      </div>
    </SectionPanel>

    <SectionPanel class="span-6" title="元数据">
      <div class="profile-current-panel">
        <div class="current-card">
          <BookMarked :size="18" />
          <div>
            <strong>{{ selectedProfile?.studentName || '全部' }}</strong>
            <small>学生画像</small>
          </div>
        </div>
        <div class="current-card">
          <CircleDashed :size="18" />
          <div>
            <strong>{{ selectedCourse?.title || '全部课程' }}</strong>
            <small>课程范围</small>
          </div>
        </div>
        <div class="current-card">
          <CircleCheck :size="18" />
          <div>
            <strong>{{ selectedTask?.topic || '全部任务' }}</strong>
            <small>任务范围</small>
          </div>
        </div>
        <div class="current-card">
          <strong>更新时间</strong>
          <small>{{ report ? formatDate(report.generatedAt) : '-' }}</small>
        </div>
      </div>
    </SectionPanel>
  </div>
</template>
