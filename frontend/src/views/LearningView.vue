<script setup lang="ts">
import type { EChartsOption } from 'echarts'
import { Download, Send } from 'lucide-vue-next'
import { computed, onMounted, reactive, ref } from 'vue'
import { coursesApi, learningApi, profilesApi } from '@/api'
import ChartPanel from '@/components/ChartPanel.vue'
import ErrorNotice from '@/components/ErrorNotice.vue'
import JsonBlock from '@/components/JsonBlock.vue'
import LoadingBlock from '@/components/LoadingBlock.vue'
import MarkdownView from '@/components/MarkdownView.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import StatusPill from '@/components/StatusPill.vue'
import type { Course, KnowledgeMastery, ProfileResponse, QuizAttempt } from '@/types/api'
import { downloadJson, downloadText, safeFilePart } from '@/utils/download'

interface AssessmentQuestion {
  id: string
  type: string
  stem: string
  options?: string[]
  answer: string
  rubric: string
  explanation: string
  difficulty: string
  knowledgePoints?: string[]
  score: number
}

const loading = ref(false)
const actionLoading = ref('')
const error = ref('')
const profiles = ref<ProfileResponse[]>([])
const courses = ref<Course[]>([])
const tutoringResult = ref<Record<string, unknown> | null>(null)
const assessmentResult = ref<Record<string, unknown> | null>(null)
const gradeResult = ref<Record<string, unknown> | null>(null)
const attempts = ref<QuizAttempt[]>([])
const mastery = ref<KnowledgeMastery[]>([])

const form = reactive({
  studentProfileId: '',
  courseId: '',
  question: 'Controller 为什么不应该直接写复杂业务逻辑？',
  modality: '文本+图解',
  topic: 'Spring Boot Controller 与 REST API',
  difficulty: '自适应',
  count: 4,
  documentText: 'Controller 负责请求响应，Service 负责业务规则，Repository 负责数据访问。',
})

const answers = ref<Record<string, string>>({})

const questions = computed<AssessmentQuestion[]>(() => {
  const raw = assessmentResult.value?.questions
  return Array.isArray(raw) ? (raw as AssessmentQuestion[]) : []
})

const scoreOption = computed<EChartsOption>(() => ({
  tooltip: {},
  graphic: attempts.value.length
    ? undefined
    : { type: 'text', left: 'center', top: 'middle', style: { text: '暂无测评趋势', fill: '#61708a' } },
  grid: { left: 36, right: 16, top: 24, bottom: 30 },
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
      data: mastery.value.map((item) => Number(item.masteryScore || 0)),
      itemStyle: { color: '#0f8a55', borderRadius: [0, 4, 4, 0] },
    },
  ],
}))

async function loadOptions() {
  loading.value = true
  error.value = ''
  try {
    const [profileList, courseList] = await Promise.all([profilesApi.list(), coursesApi.list()])
    profiles.value = profileList
    courses.value = courseList
    form.studentProfileId ||= profileList[0]?.id || ''
    form.courseId ||= courseList[0]?.id || ''
    await loadHistory()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '学习闭环选项加载失败'
  } finally {
    loading.value = false
  }
}

async function loadHistory() {
  if (!form.studentProfileId) return
  error.value = ''
  try {
    attempts.value = await learningApi.attempts(form.studentProfileId)
    if (form.courseId) {
      mastery.value = await learningApi.mastery(form.studentProfileId, form.courseId)
    }
  } catch (err) {
    attempts.value = []
    mastery.value = []
    error.value = err instanceof Error ? err.message : '学习历史加载失败'
  }
}

async function runTutoring() {
  actionLoading.value = 'tutoring'
  error.value = ''
  try {
    tutoringResult.value = await learningApi.tutoring({
      studentProfileId: form.studentProfileId,
      courseId: form.courseId,
      question: form.question,
      modality: form.modality,
      documentTexts: form.documentText ? [form.documentText] : [],
    })
  } catch (err) {
    error.value = err instanceof Error ? err.message : '智能答疑失败'
  } finally {
    actionLoading.value = ''
  }
}

async function generateAssessment() {
  actionLoading.value = 'assessment'
  error.value = ''
  try {
    assessmentResult.value = await learningApi.generateAssessment({
      studentProfileId: form.studentProfileId,
      courseId: form.courseId,
      topic: form.topic,
      difficulty: form.difficulty,
      count: form.count,
      questionTypes: ['选择题', '判断题', '简答题', '代码纠错题'],
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
  actionLoading.value = 'grade'
  error.value = ''
  try {
    gradeResult.value = await learningApi.gradeAssessment({
      studentProfileId: form.studentProfileId,
      courseId: form.courseId,
      topic: form.topic,
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
    attempts: attempts.value,
    mastery: mastery.value,
  })
}

function downloadTutoringMarkdown() {
  downloadText(`${safeFilePart(form.topic)}-tutoring.md`, String(tutoringResult.value?.answer || ''), 'text/markdown;charset=utf-8')
}

onMounted(loadOptions)
</script>

<template>
  <div class="page-grid">
    <SectionPanel class="span-12" title="学习闭环参数">
      <template #actions>
        <button class="ghost-button" :disabled="!tutoringResult && !assessmentResult && !gradeResult && !attempts.length && !mastery.length" @click="downloadLearningJson">
          <Download :size="17" />学习报告 JSON
        </button>
      </template>
      <ErrorNotice :message="error" />
      <LoadingBlock :show="loading" />
      <div class="split-row">
        <div class="field">
          <label>学生画像</label>
          <select v-model="form.studentProfileId" @change="loadHistory">
            <option v-for="profile in profiles" :key="profile.id" :value="profile.id">{{ profile.studentName }}</option>
          </select>
        </div>
        <div class="field">
          <label>课程</label>
          <select v-model="form.courseId" @change="loadHistory">
            <option v-for="course in courses" :key="course.id" :value="course.id">{{ course.title }}</option>
          </select>
        </div>
      </div>
      <div v-if="!profiles.length || !courses.length" class="notice warn-notice">
        请先创建学生画像和课程，学习闭环接口需要这两个 ID。
      </div>
    </SectionPanel>

    <SectionPanel class="span-6" title="智能答疑" subtitle="POST /api/learning/tutoring">
      <template #actions>
        <button class="ghost-button" :disabled="!tutoringResult" @click="downloadTutoringMarkdown"><Download :size="17" />Markdown</button>
      </template>
      <div class="form-grid">
        <div class="field">
          <label>问题</label>
          <textarea v-model="form.question" />
        </div>
        <div class="field">
          <label>模态</label>
          <input v-model="form.modality" />
        </div>
        <button class="button" :disabled="actionLoading === 'tutoring' || !form.studentProfileId || !form.courseId || !form.question" @click="runTutoring">
          <Send :size="17" />发起答疑
        </button>
      </div>
      <LoadingBlock :show="actionLoading === 'tutoring'" text="智能体正在组织答案" />
      <MarkdownView v-if="tutoringResult" :content="String(tutoringResult.answer || '')" />
    </SectionPanel>

    <SectionPanel class="span-6" title="测评生成与批改" subtitle="POST /api/learning/assessments/*">
      <div class="form-grid">
        <div class="split-row">
          <div class="field">
            <label>主题</label>
            <input v-model="form.topic" />
          </div>
          <div class="field">
            <label>题量</label>
            <input v-model.number="form.count" type="number" min="1" max="12" />
          </div>
        </div>
        <div class="field">
          <label>补充资料</label>
          <textarea v-model="form.documentText" />
        </div>
        <button class="button" :disabled="actionLoading === 'assessment' || !form.studentProfileId || !form.courseId || !form.topic" @click="generateAssessment">
          <Send :size="17" />生成测评
        </button>
      </div>

      <div v-if="questions.length" class="timeline">
        <div v-for="question in questions" :key="question.id" class="timeline-body">
          <div class="section-head">
            <strong>{{ question.stem }}</strong>
            <StatusPill :status="question.type" tone="info" />
          </div>
          <p v-if="question.options?.length">{{ question.options.join(' / ') }}</p>
          <div class="field">
            <label>学生答案</label>
            <textarea v-model="answers[question.id]" />
          </div>
        </div>
        <button class="button" :disabled="actionLoading === 'grade' || !questions.length" @click="gradeAssessment">提交批改</button>
      </div>
      <LoadingBlock :show="actionLoading === 'assessment' || actionLoading === 'grade'" />
    </SectionPanel>

    <SectionPanel class="span-6" title="批改结果">
      <div v-if="!gradeResult" class="empty-state">等待批改结果</div>
      <template v-else>
        <h3>{{ gradeResult.score }} / {{ gradeResult.maxScore }}</h3>
        <StatusPill :status="String(gradeResult.masteryLevel || '掌握度')" tone="ok" />
        <p>{{ gradeResult.feedback }}</p>
        <JsonBlock :value="gradeResult" max-height="320px" />
      </template>
    </SectionPanel>

    <SectionPanel class="span-6" title="学习效果可视化">
      <ChartPanel :option="scoreOption" :height="240" />
      <ChartPanel :option="masteryOption" :height="260" />
    </SectionPanel>
  </div>
</template>
