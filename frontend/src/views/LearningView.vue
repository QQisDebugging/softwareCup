<script setup lang="ts">
import type { EChartsOption } from 'echarts'
import { Download, RefreshCw, Send } from 'lucide-vue-next'
import { computed, onMounted, reactive, ref } from 'vue'
import { coursesApi, learningApi, profilesApi } from '@/api'
import ChartPanel from '@/components/ChartPanel.vue'
import ErrorNotice from '@/components/ErrorNotice.vue'
import JsonBlock from '@/components/JsonBlock.vue'
import LoadingBlock from '@/components/LoadingBlock.vue'
import MarkdownView from '@/components/MarkdownView.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import StatusPill from '@/components/StatusPill.vue'
import type { Course, EvaluationReport, KnowledgeMastery, LearningEvent, ProfileResponse, QuizAttempt } from '@/types/api'
import { downloadJson, downloadText, jsonToMarkdown, safeFilePart } from '@/utils/download'
import { compact, formatDate, isRecord, parseMaybeJson, percent } from '@/utils/format'

interface AssessmentQuestion {
  id: string
  type: string
  stem: string
  options: string[]
  answer: string
  rubric: string
  explanation: string
  difficulty: string
  knowledgePoints: string[]
  score: number
}

const questionTypeOptions = ['选择题', '判断题', '简答题', '代码纠错题']

const loading = ref(false)
const historyLoading = ref(false)
const actionLoading = ref('')
const error = ref('')
const profiles = ref<ProfileResponse[]>([])
const courses = ref<Course[]>([])
const tutoringResult = ref<Record<string, unknown> | null>(null)
const assessmentResult = ref<Record<string, unknown> | null>(null)
const gradeResult = ref<Record<string, unknown> | null>(null)
const events = ref<LearningEvent[]>([])
const tutoringHistory = ref<Record<string, unknown>[]>([])
const attempts = ref<QuizAttempt[]>([])
const mastery = ref<KnowledgeMastery[]>([])
const reports = ref<EvaluationReport[]>([])

const form = reactive({
  studentProfileId: '',
  courseId: '',
  question: 'Controller 为什么不应该直接写复杂业务逻辑？',
  modality: '文本+图解',
  topic: 'Spring Boot Controller 与 REST API',
  difficulty: '自适应',
  count: 4,
  questionTypes: ['选择题', '判断题', '简答题', '代码纠错题'],
  documentText: 'Controller 负责请求响应，Service 负责业务规则，Repository 负责数据访问。',
})

const answers = ref<Record<string, string>>({})

const selectedProfile = computed(() => profiles.value.find((item) => item.id === form.studentProfileId))
const selectedCourse = computed(() => courses.value.find((item) => item.id === form.courseId))
const hasContext = computed(() => Boolean(form.studentProfileId && form.courseId))
const contextHint = computed(() => {
  if (!profiles.value.length || !courses.value.length) return '请先创建学生画像和课程，学习闭环接口需要这两个 ID。'
  if (!form.studentProfileId) return '请选择学生画像。'
  if (!form.courseId) return '请选择课程。'
  return ''
})

const canRunTutoring = computed(() => !actionLoading.value && hasContext.value && Boolean(form.question.trim()))
const canGenerateAssessment = computed(
  () => !actionLoading.value && hasContext.value && Boolean(form.topic.trim()) && form.count > 0 && form.questionTypes.length > 0,
)
const canGrade = computed(
  () => !actionLoading.value && hasContext.value && questions.value.length > 0 && questions.value.every((item) => answers.value[item.id]?.trim()),
)
const hasLearningData = computed(
  () =>
    Boolean(tutoringResult.value || assessmentResult.value || gradeResult.value) ||
    events.value.length > 0 ||
    tutoringHistory.value.length > 0 ||
    attempts.value.length > 0 ||
    mastery.value.length > 0 ||
    reports.value.length > 0,
)

function asStringArray(value: unknown): string[] {
  const parsed = typeof value === 'string' ? parseMaybeJson<unknown>(value, value) : value
  if (Array.isArray(parsed)) {
    return parsed
      .map((item) => {
        if (typeof item === 'string') return item
        if (isRecord(item)) return String(item.title || item.text || item.url || item.label || JSON.stringify(item))
        return String(item)
      })
      .filter(Boolean)
  }
  if (typeof parsed === 'string' && parsed.trim()) return parsed.split(/\n|；|;/).map((item) => item.trim()).filter(Boolean)
  return []
}

function asRecordArray(value: unknown): Record<string, unknown>[] {
  const parsed = typeof value === 'string' ? parseMaybeJson<unknown>(value, []) : value
  return Array.isArray(parsed) ? parsed.filter(isRecord) : []
}

function normalizeQuestion(value: unknown, index: number): AssessmentQuestion {
  const record = isRecord(value) ? value : {}
  return {
    id: String(record.id || record.questionId || `q-${index + 1}`),
    type: String(record.type || record.questionType || '题目'),
    stem: String(record.stem || record.question || record.title || `题目 ${index + 1}`),
    options: asStringArray(record.options),
    answer: String(record.answer || record.referenceAnswer || ''),
    rubric: String(record.rubric || record.scoringRubric || ''),
    explanation: String(record.explanation || record.analysis || ''),
    difficulty: String(record.difficulty || form.difficulty),
    knowledgePoints: asStringArray(record.knowledgePoints || record.knowledgePoint),
    score: Number(record.score || record.maxScore || 10),
  }
}

const questions = computed<AssessmentQuestion[]>(() => {
  const raw =
    assessmentResult.value?.questions ||
    assessmentResult.value?.items ||
    assessmentResult.value?.assessmentQuestions ||
    assessmentResult.value?.questionList
  return Array.isArray(raw) ? raw.map(normalizeQuestion) : []
})

const answerMarkdown = computed(() =>
  String(tutoringResult.value?.answer || tutoringResult.value?.content || tutoringResult.value?.summary || tutoringResult.value?.message || ''),
)
const citations = computed(() => asStringArray(tutoringResult.value?.citations || tutoringResult.value?.references))
const followUpQuestions = computed(() => asStringArray(tutoringResult.value?.followUpQuestions || tutoringResult.value?.followUps))
const learningActions = computed(() => asStringArray(tutoringResult.value?.learningActions || tutoringResult.value?.actions))
const profileSignals = computed(() => asStringArray(tutoringResult.value?.profileSignals || tutoringResult.value?.signals))

const gradeScore = computed(() => Number(gradeResult.value?.score || gradeResult.value?.totalScore || 0))
const gradeMaxScore = computed(() => Number(gradeResult.value?.maxScore || gradeResult.value?.totalMaxScore || 100))
const gradePercent = computed(() => Math.round((gradeScore.value / Math.max(1, gradeMaxScore.value)) * 100))
const gradeFeedback = computed(() => String(gradeResult.value?.feedback || gradeResult.value?.summary || '暂无总评'))
const weaknessSignals = computed(() => asStringArray(gradeResult.value?.weaknessSignals || gradeResult.value?.weaknesses))
const nextResourceTypes = computed(() => asStringArray(gradeResult.value?.nextResourceTypes || gradeResult.value?.recommendedResources))
const profileUpdateSuggestions = computed(() =>
  asStringArray(gradeResult.value?.profileUpdateSuggestions || gradeResult.value?.profileSignals || gradeResult.value?.profileUpdates),
)
const itemFeedback = computed(() =>
  asRecordArray(gradeResult.value?.itemFeedback || gradeResult.value?.questionFeedback || gradeResult.value?.questionResults),
)

const scoreOption = computed<EChartsOption>(() => ({
  tooltip: {},
  graphic: attempts.value.length
    ? undefined
    : { type: 'text', left: 'center', top: 'middle', style: { text: '暂无测评趋势', fill: '#61708a' } },
  grid: { left: 38, right: 18, top: 24, bottom: 34 },
  xAxis: { type: 'category', data: attempts.value.map((item, index) => item.topic || `第${index + 1}次`) },
  yAxis: { type: 'value', max: 100 },
  series: [
    {
      type: 'line',
      smooth: true,
      data: attempts.value.map((item) => Math.round((Number(item.score || 0) / Math.max(1, Number(item.maxScore || 1))) * 100)),
      itemStyle: { color: '#2f6fef' },
      areaStyle: { opacity: 0.14 },
    },
  ],
}))

const masteryOption = computed<EChartsOption>(() => ({
  tooltip: {},
  graphic: mastery.value.length
    ? undefined
    : { type: 'text', left: 'center', top: 'middle', style: { text: '暂无掌握度数据', fill: '#61708a' } },
  grid: { left: 120, right: 18, top: 20, bottom: 30 },
  xAxis: { type: 'value', max: 100 },
  yAxis: { type: 'category', data: mastery.value.map((item) => item.knowledgePoint || '-') },
  series: [
    {
      type: 'bar',
      data: mastery.value.map((item) => Math.round(percent(item.masteryScore))),
      itemStyle: { color: '#0f8a55', borderRadius: [0, 4, 4, 0] },
    },
  ],
}))

async function loadOptions() {
  loading.value = true
  error.value = ''
  try {
    const [profileResult, courseResult] = await Promise.allSettled([profilesApi.list(), coursesApi.list()])
    profiles.value = profileResult.status === 'fulfilled' ? profileResult.value : []
    courses.value = courseResult.status === 'fulfilled' ? courseResult.value : []
    form.studentProfileId ||= profiles.value[0]?.id || ''
    form.courseId ||= courses.value[0]?.id || ''
    if (profileResult.status === 'rejected' || courseResult.status === 'rejected') {
      error.value = '学生画像或课程列表暂不可用，请确认后端服务后刷新。'
    }
    await loadHistory()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '学习闭环选项加载失败'
  } finally {
    loading.value = false
  }
}

async function loadHistory() {
  if (!hasContext.value) {
    events.value = []
    tutoringHistory.value = []
    attempts.value = []
    mastery.value = []
    reports.value = []
    return
  }
  historyLoading.value = true
  error.value = ''
  const [eventResult, tutoringResultList, attemptResult, masteryResult, reportResult] = await Promise.allSettled([
    learningApi.events(form.studentProfileId),
    learningApi.tutoringHistory(form.studentProfileId),
    learningApi.attempts(form.studentProfileId),
    learningApi.mastery(form.studentProfileId, form.courseId),
    learningApi.evaluationReports(form.studentProfileId, form.courseId),
  ])
  events.value = eventResult.status === 'fulfilled' ? eventResult.value : []
  tutoringHistory.value = tutoringResultList.status === 'fulfilled' ? tutoringResultList.value : []
  attempts.value = attemptResult.status === 'fulfilled' ? attemptResult.value : []
  mastery.value = masteryResult.status === 'fulfilled' ? masteryResult.value : []
  reports.value = reportResult.status === 'fulfilled' ? reportResult.value : []
  const failures = [eventResult, tutoringResultList, attemptResult, masteryResult, reportResult].filter((item) => item.status === 'rejected').length
  if (failures) error.value = `学习记录有 ${failures} 个接口暂不可用，页面已保留空状态。`
  historyLoading.value = false
}

async function runTutoring() {
  if (!canRunTutoring.value) {
    error.value = contextHint.value || '请输入答疑问题。'
    return
  }
  actionLoading.value = 'tutoring'
  error.value = ''
  try {
    tutoringResult.value = await learningApi.tutoring({
      studentProfileId: form.studentProfileId,
      courseId: form.courseId,
      question: form.question.trim(),
      modality: form.modality.trim(),
      documentTexts: form.documentText ? [form.documentText] : [],
    })
    await loadHistory()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '智能答疑失败'
  } finally {
    actionLoading.value = ''
  }
}

async function generateAssessment() {
  if (!canGenerateAssessment.value) {
    error.value = contextHint.value || '请补全测评主题、题量和题型。'
    return
  }
  actionLoading.value = 'assessment'
  error.value = ''
  try {
    assessmentResult.value = await learningApi.generateAssessment({
      studentProfileId: form.studentProfileId,
      courseId: form.courseId,
      topic: form.topic.trim(),
      difficulty: form.difficulty.trim(),
      count: Number(form.count),
      questionTypes: form.questionTypes,
      documentTexts: form.documentText ? [form.documentText] : [],
    })
    answers.value = Object.fromEntries(questions.value.map((item) => [item.id, '']))
  } catch (err) {
    error.value = err instanceof Error ? err.message : '测评生成失败'
  } finally {
    actionLoading.value = ''
  }
}

async function gradeAssessment() {
  if (!canGrade.value) {
    error.value = contextHint.value || '请为每道题填写答案后再提交批改。'
    return
  }
  actionLoading.value = 'grade'
  error.value = ''
  try {
    gradeResult.value = await learningApi.gradeAssessment({
      studentProfileId: form.studentProfileId,
      courseId: form.courseId,
      topic: form.topic.trim(),
      questions: questions.value,
      answers: questions.value.map((item) => ({ questionId: item.id, answer: answers.value[item.id] || '' })),
    })
    await loadHistory()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '测评批改失败'
  } finally {
    actionLoading.value = ''
  }
}

function downloadLearningJson() {
  downloadJson(`${safeFilePart(form.topic)}-learning-loop.json`, {
    tutoringResult: tutoringResult.value,
    assessmentResult: assessmentResult.value,
    gradeResult: gradeResult.value,
    events: events.value,
    tutoringHistory: tutoringHistory.value,
    attempts: attempts.value,
    mastery: mastery.value,
    reports: reports.value,
  })
}

function downloadTutoringMarkdown() {
  const lines = [
    `# ${form.topic} 智能答疑记录`,
    '',
    `- 学生画像：${selectedProfile.value?.studentName || form.studentProfileId || '-'}`,
    `- 课程：${selectedCourse.value?.title || form.courseId || '-'}`,
    `- 问题：${form.question}`,
    '',
    '## 回答',
    answerMarkdown.value || '暂无回答',
    '',
    '## 引用',
    ...(citations.value.length ? citations.value.map((item) => `- ${item}`) : ['暂无引用']),
    '',
    '## 后续问题',
    ...(followUpQuestions.value.length ? followUpQuestions.value.map((item) => `- ${item}`) : ['暂无后续问题']),
    '',
    '## 学习行动',
    ...(learningActions.value.length ? learningActions.value.map((item) => `- ${item}`) : ['暂无学习行动']),
    '',
    '## 画像信号',
    ...(profileSignals.value.length ? profileSignals.value.map((item) => `- ${item}`) : ['暂无画像信号']),
  ]
  downloadText(`${safeFilePart(form.topic)}-tutoring.md`, lines.join('\n'), 'text/markdown;charset=utf-8')
}

function downloadAssessmentJson() {
  downloadJson(`${safeFilePart(form.topic)}-assessment.json`, {
    assessmentResult: assessmentResult.value,
    questions: questions.value,
    answers: answers.value,
    gradeResult: gradeResult.value,
  })
}

function downloadLearningMarkdown() {
  const lines = [
    `# ${form.topic} 学习闭环报告`,
    '',
    `- 学生：${selectedProfile.value?.studentName || '-'}`,
    `- 课程：${selectedCourse.value?.title || '-'}`,
    `- 最近测评：${attempts.value.length} 次`,
    `- 掌握度记录：${mastery.value.length} 条`,
    `- 学习事件：${events.value.length} 条`,
    '',
    '## 智能答疑',
    answerMarkdown.value || '暂无答疑结果',
    '',
    '## 批改结果',
    gradeResult.value ? `得分：${gradeScore.value} / ${gradeMaxScore.value}\n\n${gradeFeedback.value}` : '暂无批改结果',
    '',
    '## 薄弱点',
    ...(weaknessSignals.value.length ? weaknessSignals.value.map((item) => `- ${item}`) : ['暂无薄弱点']),
    '',
    '## 下一步资源建议',
    ...(nextResourceTypes.value.length ? nextResourceTypes.value.map((item) => `- ${item}`) : ['暂无资源建议']),
    '',
    jsonToMarkdown('完整 JSON', {
      tutoringResult: tutoringResult.value,
      assessmentResult: assessmentResult.value,
      gradeResult: gradeResult.value,
      events: events.value,
      attempts: attempts.value,
      mastery: mastery.value,
      reports: reports.value,
    }),
  ]
  downloadText(`${safeFilePart(form.topic)}-learning-report.md`, lines.join('\n'), 'text/markdown;charset=utf-8')
}

onMounted(loadOptions)
</script>

<template>
  <div class="page-grid">
    <SectionPanel class="span-12" title="学习闭环参数" subtitle="学生画像 + 课程上下文驱动答疑、测评、批改和学习记录">
      <template #actions>
        <button class="ghost-button" @click="loadOptions"><RefreshCw :size="17" />刷新</button>
        <button class="ghost-button" :disabled="!hasLearningData" @click="downloadLearningJson">
          <Download :size="17" />学习报告 JSON
        </button>
        <button class="ghost-button" :disabled="!hasLearningData" @click="downloadLearningMarkdown">
          <Download :size="17" />学习报告 Markdown
        </button>
      </template>
      <ErrorNotice :message="error" />
      <LoadingBlock :show="loading" />
      <div class="split-row">
        <div class="field">
          <label>学生画像 <span class="required-mark">*</span></label>
          <select v-model="form.studentProfileId" @change="loadHistory">
            <option value="" disabled>请选择学生画像</option>
            <option v-for="profile in profiles" :key="profile.id" :value="profile.id">{{ profile.studentName }} - {{ profile.learningGoal }}</option>
          </select>
        </div>
        <div class="field">
          <label>课程 <span class="required-mark">*</span></label>
          <select v-model="form.courseId" @change="loadHistory">
            <option value="" disabled>请选择课程</option>
            <option v-for="course in courses" :key="course.id" :value="course.id">{{ course.title }}</option>
          </select>
        </div>
      </div>
      <div v-if="contextHint" class="notice warn-notice">
        <span>{{ contextHint }}</span>
      </div>
      <LoadingBlock :show="historyLoading" text="正在同步学习记录" />
    </SectionPanel>

    <SectionPanel class="span-6" title="智能答疑" subtitle="POST /api/learning/tutoring">
      <template #actions>
        <button class="ghost-button" :disabled="!tutoringResult" @click="downloadTutoringMarkdown"><Download :size="17" />Markdown</button>
      </template>
      <div class="form-grid">
        <div class="field">
          <label>问题 <span class="required-mark">*</span></label>
          <textarea v-model="form.question" />
          <small v-if="!form.question.trim()" class="field-error">请输入答疑问题。</small>
        </div>
        <div class="field">
          <label>模态</label>
          <input v-model="form.modality" />
        </div>
        <div class="field">
          <label>补充资料</label>
          <textarea v-model="form.documentText" />
        </div>
        <button class="button" :disabled="!canRunTutoring" @click="runTutoring">
          <Send :size="17" />发起答疑
        </button>
      </div>
      <LoadingBlock :show="actionLoading === 'tutoring'" text="智能体正在组织答案" />
      <div v-if="!tutoringResult" class="empty-guide">
        <strong>等待答疑结果</strong>
        <span>选择学生和课程后提交问题，结果会展示回答、引用、后续问题、学习行动和画像信号。</span>
      </div>
      <template v-else>
        <MarkdownView :content="answerMarkdown" />
        <div class="learning-chip-grid">
          <div>
            <strong>引用</strong>
            <span v-for="item in citations" :key="item">{{ item }}</span>
            <small v-if="!citations.length">暂无引用</small>
          </div>
          <div>
            <strong>后续问题</strong>
            <span v-for="item in followUpQuestions" :key="item">{{ item }}</span>
            <small v-if="!followUpQuestions.length">暂无后续问题</small>
          </div>
          <div>
            <strong>学习行动</strong>
            <span v-for="item in learningActions" :key="item">{{ item }}</span>
            <small v-if="!learningActions.length">暂无学习行动</small>
          </div>
          <div>
            <strong>画像信号</strong>
            <span v-for="item in profileSignals" :key="item">{{ item }}</span>
            <small v-if="!profileSignals.length">暂无画像信号</small>
          </div>
        </div>
      </template>
    </SectionPanel>

    <SectionPanel class="span-6" title="测评生成与自动批改" subtitle="POST /api/learning/assessments/*">
      <template #actions>
        <button class="ghost-button" :disabled="!assessmentResult && !gradeResult" @click="downloadAssessmentJson">
          <Download :size="17" />测评 JSON
        </button>
      </template>
      <div class="form-grid">
        <div class="split-row">
          <div class="field">
            <label>主题 <span class="required-mark">*</span></label>
            <input v-model="form.topic" />
          </div>
          <div class="field">
            <label>题量</label>
            <input v-model.number="form.count" type="number" min="1" max="12" />
          </div>
        </div>
        <div class="field">
          <label>难度</label>
          <select v-model="form.difficulty">
            <option value="入门">入门</option>
            <option value="自适应">自适应</option>
            <option value="进阶">进阶</option>
            <option value="挑战">挑战</option>
          </select>
        </div>
        <div class="field">
          <label>题型 <span class="required-mark">*</span></label>
          <div class="toggle-grid">
            <label v-for="type in questionTypeOptions" :key="type" class="check-tile">
              <input v-model="form.questionTypes" type="checkbox" :value="type" />
              <span>{{ type }}</span>
            </label>
          </div>
          <small v-if="!form.questionTypes.length" class="field-error">请至少选择一种题型。</small>
        </div>
        <button class="button" :disabled="!canGenerateAssessment" @click="generateAssessment">
          <Send :size="17" />生成测评
        </button>
      </div>

      <LoadingBlock :show="actionLoading === 'assessment' || actionLoading === 'grade'" />
      <div v-if="!questions.length" class="empty-guide">
        <strong>等待测评题目</strong>
        <span>生成后会在这里填写学生答案并提交自动批改。</span>
      </div>
      <div v-else class="timeline">
        <div v-for="question in questions" :key="question.id" class="timeline-body">
          <div class="section-head">
            <div>
              <strong>{{ question.stem }}</strong>
              <p>{{ question.knowledgePoints.join(' / ') || question.difficulty }}</p>
            </div>
            <StatusPill :status="question.type" tone="info" />
          </div>
          <p v-if="question.options.length">{{ question.options.join(' / ') }}</p>
          <small v-if="question.rubric">评分标准：{{ question.rubric }}</small>
          <div class="field">
            <label>学生答案 <span class="required-mark">*</span></label>
            <textarea v-model="answers[question.id]" />
          </div>
        </div>
        <button class="button" :disabled="!canGrade" @click="gradeAssessment">提交批改</button>
        <small v-if="questions.length && !canGrade" class="field-error">请补齐所有学生答案后再批改。</small>
      </div>
    </SectionPanel>

    <SectionPanel class="span-6" title="批改结果">
      <div v-if="!gradeResult" class="empty-guide">
        <strong>等待批改结果</strong>
        <span>自动批改后展示总分、逐题反馈、薄弱点、资源建议和画像更新建议。</span>
      </div>
      <template v-else>
        <div class="grade-hero">
          <strong>{{ gradeScore }} / {{ gradeMaxScore }}</strong>
          <StatusPill :status="`${gradePercent}%`" :tone="gradePercent >= 80 ? 'ok' : gradePercent >= 60 ? 'warn' : 'danger'" />
          <p>{{ gradeFeedback }}</p>
        </div>
        <div class="learning-chip-grid">
          <div>
            <strong>薄弱点</strong>
            <span v-for="item in weaknessSignals" :key="item">{{ item }}</span>
            <small v-if="!weaknessSignals.length">暂无薄弱点</small>
          </div>
          <div>
            <strong>下一步资源</strong>
            <span v-for="item in nextResourceTypes" :key="item">{{ item }}</span>
            <small v-if="!nextResourceTypes.length">暂无资源建议</small>
          </div>
          <div>
            <strong>画像更新建议</strong>
            <span v-for="item in profileUpdateSuggestions" :key="item">{{ item }}</span>
            <small v-if="!profileUpdateSuggestions.length">暂无画像更新建议</small>
          </div>
        </div>
        <div v-if="itemFeedback.length" class="timeline">
          <div v-for="(item, index) in itemFeedback" :key="index" class="timeline-body">
            <strong>{{ item.questionId || item.stem || `题目 ${index + 1}` }}</strong>
            <p>{{ item.feedback || item.comment || item.analysis || '-' }}</p>
          </div>
        </div>
        <JsonBlock :value="gradeResult" max-height="320px" />
      </template>
    </SectionPanel>

    <SectionPanel class="span-6" title="学习效果可视化">
      <ChartPanel :option="scoreOption" :height="240" />
      <ChartPanel :option="masteryOption" :height="260" />
    </SectionPanel>

    <SectionPanel class="span-12" title="学习记录">
      <LoadingBlock :show="historyLoading" />
      <div class="record-grid">
        <div>
          <h3>学习事件</h3>
          <div v-if="!events.length" class="empty-guide"><strong>暂无学习事件</strong><span>GET /api/learning/events 暂无数据。</span></div>
          <div v-else class="timeline">
            <div v-for="item in events.slice(0, 6)" :key="item.id" class="timeline-body">
              <div class="section-head">
                <strong>{{ item.eventType }}</strong>
                <StatusPill :status="formatDate(item.createdAt)" tone="muted" />
              </div>
              <p>{{ compact(item.eventPayload || item.resourceId || '-', 120) }}</p>
            </div>
          </div>
        </div>
        <div>
          <h3>答疑记录</h3>
          <div v-if="!tutoringHistory.length" class="empty-guide"><strong>暂无答疑记录</strong><span>GET /api/learning/tutoring 暂无数据。</span></div>
          <div v-else class="timeline">
            <div v-for="(item, index) in tutoringHistory.slice(0, 6)" :key="index" class="timeline-body">
              <strong>{{ item.question || item.topic || `答疑 ${index + 1}` }}</strong>
              <p>{{ compact(item.answer || item.summary || item.content || '-', 140) }}</p>
            </div>
          </div>
        </div>
        <div>
          <h3>测评记录</h3>
          <div v-if="!attempts.length" class="empty-guide"><strong>暂无测评记录</strong><span>GET /api/learning/attempts 暂无数据。</span></div>
          <div v-else class="timeline">
            <div v-for="item in attempts.slice(0, 6)" :key="item.id" class="timeline-body">
              <div class="section-head">
                <strong>{{ item.topic }}</strong>
                <StatusPill :status="`${item.score}/${item.maxScore}`" tone="info" />
              </div>
              <p>{{ compact(item.weaknessSignals, 120) }}</p>
              <small>{{ formatDate(item.createdAt) }}</small>
            </div>
          </div>
        </div>
        <div>
          <h3>知识掌握度</h3>
          <div v-if="!mastery.length" class="empty-guide"><strong>暂无掌握度</strong><span>GET /api/learning/mastery 暂无数据。</span></div>
          <div v-else class="timeline">
            <div v-for="item in mastery.slice(0, 6)" :key="item.id || item.knowledgePoint" class="timeline-body">
              <div class="section-head">
                <strong>{{ item.knowledgePoint }}</strong>
                <StatusPill :status="`${Math.round(percent(item.masteryScore))}%`" tone="ok" />
              </div>
              <p>{{ compact(item.evidence, 120) }}</p>
            </div>
          </div>
        </div>
        <div>
          <h3>评估报告</h3>
          <div v-if="!reports.length" class="empty-guide"><strong>暂无评估报告</strong><span>GET /api/learning/evaluation-reports 暂无数据。</span></div>
          <div v-else class="timeline">
            <div v-for="item in reports.slice(0, 6)" :key="item.id" class="timeline-body">
              <strong>{{ item.title || item.id }}</strong>
              <p>{{ compact(item.summary || item.reportJson, 150) }}</p>
              <small>{{ formatDate(item.createdAt) }}</small>
            </div>
          </div>
        </div>
      </div>
    </SectionPanel>
  </div>
</template>
