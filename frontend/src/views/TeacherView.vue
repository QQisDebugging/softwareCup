<script setup lang="ts">
import type { EChartsOption } from 'echarts'
import { Download, Play, RefreshCw } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { agentsApi, coursesApi, profilesApi } from '@/api'
import ChartPanel from '@/components/ChartPanel.vue'
import ErrorNotice from '@/components/ErrorNotice.vue'
import JsonBlock from '@/components/JsonBlock.vue'
import LoadingBlock from '@/components/LoadingBlock.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import StatusPill from '@/components/StatusPill.vue'
import type { Course, ProfileResponse } from '@/types/api'
import { downloadJson, downloadText, jsonToMarkdown, safeFilePart } from '@/utils/download'
import { compact, formatDate, isRecord, parseMaybeJson, percent } from '@/utils/format'

const loading = ref(false)
const running = ref('')
const error = ref('')
const courses = ref<Course[]>([])
const profiles = ref<ProfileResponse[]>([])
const diagnosis = ref<Record<string, unknown> | null>(null)
const analytics = ref<Record<string, unknown> | null>(null)

const selectedCourseId = ref('')
const selectedProfileId = ref('')
const topic = ref('Spring Boot Controller 与 REST API')

const selectedCourse = computed(() => courses.value.find((item) => item.id === selectedCourseId.value))
const selectedProfile = computed(() => profiles.value.find((item) => item.id === selectedProfileId.value))
const canRun = computed(() => Boolean(selectedCourseId.value && !running.value))
const hasReport = computed(() => Boolean(diagnosis.value || analytics.value))
const contextHint = computed(() => {
  if (!courses.value.length) return '请先在课程资源页面创建课程，教师端诊断依赖 courseId。'
  if (!selectedCourseId.value) return '请选择课程后再运行教师分析。'
  return ''
})

function asNumber(value: unknown, fallback = 0) {
  const numeric = Number(value ?? fallback)
  return Number.isFinite(numeric) ? numeric : fallback
}

function stringList(value: unknown): string[] {
  const parsed = typeof value === 'string' ? parseMaybeJson<unknown>(value, value) : value
  if (Array.isArray(parsed)) {
    return parsed
      .map((item) => {
        if (typeof item === 'string') return item
        if (isRecord(item)) return String(item.title || item.name || item.knowledgePoint || item.reason || JSON.stringify(item))
        return String(item)
      })
      .filter(Boolean)
  }
  if (typeof parsed === 'string' && parsed.trim()) {
    return parsed.split(/\n|；|;/).map((item) => item.trim()).filter(Boolean)
  }
  return []
}

function recordList(value: unknown): Record<string, unknown>[] {
  const parsed = typeof value === 'string' ? parseMaybeJson<unknown>(value, []) : value
  return Array.isArray(parsed) ? parsed.filter(isRecord) : []
}

const classMastery = computed(() =>
  Math.round(
    percent(
      asNumber(
        analytics.value?.classMasteryAverage ||
          analytics.value?.masteryAverage ||
          analytics.value?.averageMastery ||
          diagnosis.value?.coverageScore ||
          0,
      ),
    ),
  ),
)
const engagement = computed(() => Math.round(percent(asNumber(analytics.value?.engagementAverage || analytics.value?.participationRate || 0))))
const courseCoverage = computed(() => Math.round(percent(asNumber(diagnosis.value?.coverageScore || diagnosis.value?.courseCoverage || 0))))
const riskStudents = computed(() => recordList(analytics.value?.studentRiskProfiles || analytics.value?.riskStudents || analytics.value?.atRiskStudents))
const interventionGroups = computed(() =>
  recordList(analytics.value?.interventionGroups || analytics.value?.interventionPriority || analytics.value?.groups),
)
const resourceGaps = computed(() =>
  stringList(
    analytics.value?.resourceGaps ||
      diagnosis.value?.resourceGaps ||
      diagnosis.value?.missingResources ||
      diagnosis.value?.missingKnowledgePoints,
  ),
)
const missingKnowledgePoints = computed(() => stringList(diagnosis.value?.missingKnowledgePoints || diagnosis.value?.weakKnowledgePoints))
const recommendedTasks = computed(() => stringList(diagnosis.value?.recommendedTasks || diagnosis.value?.teachingActions || diagnosis.value?.nextActions))
const classTrend = computed(() => String(analytics.value?.classTrend || analytics.value?.trend || '等待分析'))

const masteryChartOption = computed<EChartsOption>(() => {
  const points = recordList(analytics.value?.masterySnapshots || analytics.value?.knowledgeMastery)
  const names = points.length ? points.map((item, index) => String(item.knowledgePoint || item.name || `知识点 ${index + 1}`)) : ['课程覆盖率', '班级掌握度', '参与度']
  const values = points.length
    ? points.map((item) => Math.round(percent(asNumber(item.masteryScore || item.score || item.value))))
    : [courseCoverage.value, classMastery.value, engagement.value]
  return {
    tooltip: {},
    graphic: hasReport.value
      ? undefined
      : { type: 'text', left: 'center', top: 'middle', style: { text: '等待教师分析数据', fill: '#61708a' } },
    grid: { left: 110, right: 18, top: 24, bottom: 28 },
    xAxis: { type: 'value', max: 100 },
    yAxis: { type: 'category', data: names },
    series: [{ type: 'bar', data: values, itemStyle: { color: '#2f6fef', borderRadius: [0, 4, 4, 0] } }],
  }
})

const riskChartOption = computed<EChartsOption>(() => {
  const groups = riskStudents.value.reduce<Record<string, number>>((acc, item) => {
    const level = String(item.riskLevel || item.level || item.riskReason || '待干预')
    acc[level] = (acc[level] || 0) + 1
    return acc
  }, {})
  const data = Object.entries(groups).map(([name, value]) => ({ name, value }))
  return {
    tooltip: { trigger: 'item' },
    color: ['#c24138', '#a15c00', '#0e7490', '#64748b'],
    graphic: data.length
      ? undefined
      : { type: 'text', left: 'center', top: 'middle', style: { text: '暂无风险学生', fill: '#61708a' } },
    series: [{ type: 'pie', radius: ['45%', '72%'], data, label: { formatter: '{b}: {c}' } }],
  }
})

const resourceGapOption = computed<EChartsOption>(() => ({
  tooltip: {},
  graphic: resourceGaps.value.length
    ? undefined
    : { type: 'text', left: 'center', top: 'middle', style: { text: '暂无资源缺口', fill: '#61708a' } },
  grid: { left: 90, right: 18, top: 24, bottom: 28 },
  xAxis: { type: 'value', minInterval: 1 },
  yAxis: { type: 'category', data: resourceGaps.value.map((item) => compact(item, 10)) },
  series: [
    {
      type: 'bar',
      data: resourceGaps.value.map((_item, index) => Math.max(1, resourceGaps.value.length - index)),
      itemStyle: { color: '#0f8a55', borderRadius: [0, 4, 4, 0] },
    },
  ],
}))

async function loadOptions() {
  loading.value = true
  error.value = ''
  const [courseResult, profileResult] = await Promise.allSettled([coursesApi.list(), profilesApi.list()])
  courses.value = courseResult.status === 'fulfilled' ? courseResult.value : []
  profiles.value = profileResult.status === 'fulfilled' ? profileResult.value : []
  selectedCourseId.value ||= courses.value[0]?.id || ''
  selectedProfileId.value ||= profiles.value[0]?.id || ''
  const failures = [courseResult, profileResult].filter((item) => item.status === 'rejected').length
  if (failures) error.value = '教师分析基础选项暂不可用，请确认后端服务后刷新。'
  loading.value = false
}

function diagnosisPayload() {
  return {
    courseId: selectedCourseId.value,
    courseTitle: selectedCourse.value?.title || '',
    courseDescription: selectedCourse.value?.description || '',
    syllabusText: selectedCourse.value?.syllabusJson || '',
    topic: topic.value,
    targetStudentProfile: selectedProfile.value?.dialogueSummary || selectedProfile.value?.currentLevel || '',
    expectedOutputs: ['missingKnowledgePoints', 'resourceGaps', 'recommendedTasks', 'coverageScore'],
  }
}

function analyticsPayload() {
  return {
    courseId: selectedCourseId.value,
    courseTitle: selectedCourse.value?.title || '',
    topic: topic.value,
    snapshots: [
      {
        studentProfileId: selectedProfileId.value || 'demo-1',
        studentName: selectedProfile.value?.studentName || '张同学',
        profileSummary: selectedProfile.value?.dialogueSummary || 'Java 基础较弱',
        recentScores: [48, 55, 72],
        completedResources: 2,
        tutoringCount: 1,
        codePracticeCount: 0,
        weaknessSignals: ['HTTP 请求响应', 'MVC 分层职责'],
        learningEvents: ['错题复盘'],
      },
      {
        studentProfileId: 'peer-1',
        studentName: '李同学',
        profileSummary: '实操不足',
        recentScores: [68, 72],
        completedResources: 2,
        tutoringCount: 1,
        codePracticeCount: 0,
        weaknessSignals: ['MVC 分层职责', 'REST API 边界'],
        learningEvents: ['完成资源卡'],
      },
      {
        studentProfileId: 'peer-2',
        studentName: '王同学',
        profileSummary: '理论较好但项目经验少',
        recentScores: [75, 81],
        completedResources: 4,
        tutoringCount: 2,
        codePracticeCount: 1,
        weaknessSignals: ['异常处理'],
        learningEvents: ['完成代码练习'],
      },
    ],
    expectedOutputs: ['classMasteryAverage', 'engagementAverage', 'studentRiskProfiles', 'interventionGroups', 'resourceGaps'],
  }
}

async function runDiagnosis() {
  if (!canRun.value) {
    error.value = contextHint.value || '请选择课程后再运行课程诊断。'
    return
  }
  running.value = 'diagnosis'
  error.value = ''
  try {
    diagnosis.value = await agentsApi.invoke('/teaching/course-diagnostics', diagnosisPayload())
  } catch (err) {
    error.value = `教师分析接口暂不可用：${err instanceof Error ? err.message : '课程诊断失败'}`
  } finally {
    running.value = ''
  }
}

async function runAnalytics() {
  if (!canRun.value) {
    error.value = contextHint.value || '请选择课程后再运行班级分析。'
    return
  }
  running.value = 'analytics'
  error.value = ''
  try {
    analytics.value = await agentsApi.invoke('/teaching/class-analytics', analyticsPayload())
  } catch (err) {
    error.value = `教师分析接口暂不可用：${err instanceof Error ? err.message : '班级分析失败'}`
  } finally {
    running.value = ''
  }
}

async function runAll() {
  if (!canRun.value) {
    error.value = contextHint.value || '请选择课程后再运行教师分析。'
    return
  }
  await runDiagnosis()
  await runAnalytics()
}

function downloadTeacherJson() {
  downloadJson(`${safeFilePart(topic.value)}-teacher-analysis.json`, {
    course: selectedCourse.value,
    representativeStudent: selectedProfile.value,
    diagnosis: diagnosis.value,
    analytics: analytics.value,
  })
}

function downloadTeacherMarkdown() {
  const lines = [
    `# ${topic.value} 教师分析报告`,
    '',
    `- 课程：${selectedCourse.value?.title || '-'}`,
    `- 代表学生：${selectedProfile.value?.studentName || '-'}`,
    `- 班级掌握度：${classMastery.value}%`,
    `- 参与度：${engagement.value}%`,
    `- 课程覆盖率：${courseCoverage.value}%`,
    `- 班级趋势：${classTrend.value}`,
    '',
    '## 资源缺口',
    ...(resourceGaps.value.length ? resourceGaps.value.map((item) => `- ${item}`) : ['暂无资源缺口']),
    '',
    '## 风险学生',
    ...(riskStudents.value.length
      ? riskStudents.value.map((item) => `- ${item.studentName || item.name || '学生'}：${item.riskReason || item.reason || item.riskLevel || '待干预'}`)
      : ['暂无风险学生']),
    '',
    '## 干预分组',
    ...(interventionGroups.value.length
      ? interventionGroups.value.map((item) => `- ${item.groupName || item.name || item.level || '干预组'}：${item.action || item.strategy || item.reason || '-'}`)
      : ['暂无干预分组']),
    '',
    '## 建设任务',
    ...(recommendedTasks.value.length ? recommendedTasks.value.map((item) => `- ${item}`) : ['暂无建设任务']),
    '',
    jsonToMarkdown('完整 JSON', { diagnosis: diagnosis.value, analytics: analytics.value }),
  ]
  downloadText(`${safeFilePart(topic.value)}-teacher-analysis.md`, lines.join('\n'), 'text/markdown;charset=utf-8')
}

onMounted(loadOptions)
</script>

<template>
  <div class="page-grid">
    <SectionPanel class="span-12" title="教师端看板参数" subtitle="课程诊断 + 班级学情分析，全部经 Java 后端代理接口调用">
      <template #actions>
        <button class="ghost-button" @click="loadOptions"><RefreshCw :size="17" />刷新选项</button>
        <button class="ghost-button" :disabled="!hasReport" @click="downloadTeacherJson"><Download :size="17" />JSON</button>
        <button class="ghost-button" :disabled="!hasReport" @click="downloadTeacherMarkdown"><Download :size="17" />Markdown</button>
        <button class="button" :disabled="!canRun" @click="runAll"><Play :size="17" />运行全部分析</button>
      </template>
      <ErrorNotice :message="error" />
      <LoadingBlock :show="loading" />
      <div class="split-row">
        <div class="field">
          <label>课程 <span class="required-mark">*</span></label>
          <select v-model="selectedCourseId">
            <option value="" disabled>请选择课程</option>
            <option v-for="course in courses" :key="course.id" :value="course.id">{{ course.title }}</option>
          </select>
        </div>
        <div class="field">
          <label>代表学生</label>
          <select v-model="selectedProfileId">
            <option value="">使用演示学生快照</option>
            <option v-for="profile in profiles" :key="profile.id" :value="profile.id">{{ profile.studentName }}</option>
          </select>
        </div>
      </div>
      <div class="field">
        <label>分析主题</label>
        <input v-model="topic" />
      </div>
      <div v-if="contextHint" class="notice warn-notice"><span>{{ contextHint }}</span></div>
    </SectionPanel>

    <article class="metric-tile span-3">
      <span>班级掌握度</span>
      <strong>{{ classMastery }}%</strong>
      <small>来自 /api/teaching/class-analytics</small>
    </article>
    <article class="metric-tile span-3">
      <span>参与度</span>
      <strong>{{ engagement }}%</strong>
      <small>学习事件和资源完成度</small>
    </article>
    <article class="metric-tile span-3">
      <span>风险学生</span>
      <strong>{{ riskStudents.length }}</strong>
      <small>需要干预或重点观察</small>
    </article>
    <article class="metric-tile span-3">
      <span>资源缺口</span>
      <strong>{{ resourceGaps.length }}</strong>
      <small>来自诊断与班级分析</small>
    </article>

    <SectionPanel class="span-4" title="课程诊断" subtitle="POST /api/teaching/course-diagnostics">
      <template #actions>
        <button class="button" :disabled="running === 'diagnosis' || !selectedCourseId" @click="runDiagnosis"><Play :size="17" />诊断</button>
      </template>
      <LoadingBlock :show="running === 'diagnosis'" text="正在诊断课程" />
      <div v-if="!diagnosis" class="empty-guide">
        <strong>等待课程诊断</strong>
        <span>运行后展示缺失知识点、资源缺口和建设任务。</span>
      </div>
      <div v-else class="timeline">
        <div class="timeline-body">
          <strong>缺失知识点</strong>
          <p>{{ missingKnowledgePoints.length ? missingKnowledgePoints.join('、') : '暂无缺失知识点' }}</p>
        </div>
        <div class="timeline-body">
          <strong>建设任务</strong>
          <p>{{ recommendedTasks.length ? recommendedTasks.join('；') : '暂无建设任务' }}</p>
        </div>
      </div>
    </SectionPanel>

    <SectionPanel class="span-4" title="班级学情分析" subtitle="POST /api/teaching/class-analytics">
      <template #actions>
        <button class="button" :disabled="running === 'analytics' || !selectedCourseId" @click="runAnalytics"><Play :size="17" />分析</button>
      </template>
      <LoadingBlock :show="running === 'analytics'" text="正在分析班级" />
      <div v-if="!analytics" class="empty-guide">
        <strong>等待班级分析</strong>
        <span>运行后展示班级趋势、风险学生和干预分组。</span>
      </div>
      <div v-else class="timeline">
        <div class="timeline-body">
          <div class="section-head">
            <strong>班级趋势</strong>
            <StatusPill :status="classTrend" tone="info" />
          </div>
          <p>{{ stringList(analytics.interventionPriority || analytics.nextActions).join('；') || '暂无优先干预建议' }}</p>
        </div>
      </div>
    </SectionPanel>

    <SectionPanel class="span-4" title="演示说明">
      <div class="empty-guide">
        <strong>教师端看板</strong>
        <span>本页展示课程诊断、班级掌握度、参与度、风险学生、干预分组和资源缺口，适合作为教师端能力答辩页。</span>
      </div>
    </SectionPanel>

    <SectionPanel class="span-4" title="掌握度图">
      <ChartPanel :option="masteryChartOption" :height="300" />
    </SectionPanel>
    <SectionPanel class="span-4" title="风险分布">
      <ChartPanel :option="riskChartOption" :height="300" />
    </SectionPanel>
    <SectionPanel class="span-4" title="资源缺口">
      <ChartPanel :option="resourceGapOption" :height="300" />
    </SectionPanel>

    <SectionPanel class="span-4" title="风险学生">
      <div v-if="!riskStudents.length" class="empty-guide"><strong>暂无风险学生</strong><span>班级分析接口返回后会展示风险学生和原因。</span></div>
      <div v-else class="timeline">
        <div v-for="(item, index) in riskStudents" :key="index" class="timeline-body">
          <div class="section-head">
            <strong>{{ item.studentName || item.name || `学生 ${index + 1}` }}</strong>
            <StatusPill :status="String(item.riskLevel || item.level || '待干预')" tone="warn" />
          </div>
          <p>{{ item.riskReason || item.reason || item.suggestion || '-' }}</p>
        </div>
      </div>
    </SectionPanel>

    <SectionPanel class="span-4" title="干预分组">
      <div v-if="!interventionGroups.length" class="empty-guide"><strong>暂无干预分组</strong><span>班级分析接口返回后会展示分组策略。</span></div>
      <div v-else class="timeline">
        <div v-for="(item, index) in interventionGroups" :key="index" class="timeline-body">
          <strong>{{ item.groupName || item.name || item.level || `干预组 ${index + 1}` }}</strong>
          <p>{{ item.action || item.strategy || item.reason || item.description || '-' }}</p>
        </div>
      </div>
    </SectionPanel>

    <SectionPanel class="span-4" title="资源缺口">
      <div v-if="!resourceGaps.length" class="empty-guide"><strong>暂无资源缺口</strong><span>课程诊断或班级分析返回后会展示需要补齐的资源。</span></div>
      <div v-else class="timeline">
        <div v-for="(item, index) in resourceGaps" :key="item" class="timeline-body">
          <div class="section-head">
            <strong>缺口 {{ index + 1 }}</strong>
            <StatusPill status="待补齐" tone="warn" />
          </div>
          <p>{{ item }}</p>
        </div>
      </div>
    </SectionPanel>

    <SectionPanel class="span-12" title="教师端原始响应">
      <JsonBlock :value="{ diagnosis, analytics, generatedAt: formatDate(Date.now()) }" />
    </SectionPanel>
  </div>
</template>
