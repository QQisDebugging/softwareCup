<script setup lang="ts">
import { Send, Sparkles } from 'lucide-vue-next'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { coursesApi, profilesApi, tasksApi } from '@/api'
import ErrorNotice from '@/components/ErrorNotice.vue'
import LoadingBlock from '@/components/LoadingBlock.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import StatusPill from '@/components/StatusPill.vue'
import type { Course, ProfileResponse, ResourceType } from '@/types/api'

const router = useRouter()
const loading = ref(false)
const submitting = ref(false)
const error = ref('')
const profiles = ref<ProfileResponse[]>([])
const courses = ref<Course[]>([])
const resourceTypes = ref<ResourceType[]>([])
const usingFallbackResourceTypes = ref(false)

const fallbackResourceTypes: ResourceType[] = [
  { code: 'COURSE_EXPLANATION_DOCUMENT', displayName: '课程讲解文档（前端兜底）' },
  { code: 'PRACTICE_QUIZ', displayName: '练习测评题（前端兜底）' },
  { code: 'MIND_MAP', displayName: '知识图谱/思维导图（前端兜底）' },
  { code: 'LESSON_SCRIPT', displayName: '多模态讲解脚本（前端兜底）' },
]

const form = reactive({
  studentProfileId: '',
  courseId: '',
  topic: 'Spring Boot Controller 与 REST API',
  resourceType: 'COURSE_EXPLANATION_DOCUMENT',
  modality: '文本+图解脚本',
  prompt: '面向 Java 基础较弱的大二学生，用项目案例讲解 Controller、DTO 和 Service 分层，并附带练习题和防错提示。',
})

const selectedProfile = computed(() => profiles.value.find((item) => item.id === form.studentProfileId))
const selectedCourse = computed(() => courses.value.find((item) => item.id === form.courseId))

const formErrors = computed<Record<string, string>>(() => {
  const errors: Record<string, string> = {}
  if (!form.studentProfileId) errors.studentProfileId = '请先选择学生画像'
  if (!form.courseId) errors.courseId = '请先选择课程'
  if (!form.resourceType) errors.resourceType = '请选择资源类型'
  if (!form.topic.trim()) errors.topic = '请输入资源主题'
  if (!form.modality.trim()) errors.modality = '请输入资源模态'
  if (!form.prompt.trim()) errors.prompt = '请输入生成要求'
  return errors
})

const canSubmit = computed(() => !submitting.value && Object.keys(formErrors.value).length === 0)

async function loadOptions() {
  loading.value = true
  error.value = ''
  usingFallbackResourceTypes.value = false
  try {
    const [profileResult, courseResult, typeResult] = await Promise.allSettled([
      profilesApi.list(),
      coursesApi.list(),
      coursesApi.resourceTypes(),
    ])
    if (profileResult.status === 'fulfilled') profiles.value = profileResult.value
    else profiles.value = []
    if (courseResult.status === 'fulfilled') courses.value = courseResult.value
    else courses.value = []
    if (typeResult.status === 'fulfilled' && typeResult.value.length) {
      resourceTypes.value = typeResult.value
    } else {
      resourceTypes.value = fallbackResourceTypes
      usingFallbackResourceTypes.value = true
    }
    form.studentProfileId ||= profiles.value[0]?.id || ''
    form.courseId ||= courses.value[0]?.id || ''
    form.resourceType ||= resourceTypes.value[0]?.code || ''
    const failures = [profileResult, courseResult].filter((item) => item.status === 'rejected').length
    if (failures) error.value = '学生画像或课程列表暂不可用，请确认后端服务后刷新。'
  } catch (err) {
    error.value = err instanceof Error ? err.message : '生成选项加载失败'
  } finally {
    loading.value = false
  }
}

async function submit() {
  if (!canSubmit.value) {
    error.value = Object.values(formErrors.value)[0] || '请先补全生成任务表单。'
    return
  }
  submitting.value = true
  error.value = ''
  try {
    const task = await tasksApi.createResourceGeneration({
      studentProfileId: form.studentProfileId,
      courseId: form.courseId,
      topic: form.topic.trim(),
      resourceType: form.resourceType,
      modality: form.modality.trim(),
      prompt: form.prompt.trim(),
    })
    if (!task.id) throw new Error('任务已提交，但后端未返回 taskId，请刷新任务列表或查看后端日志。')
    await router.push(`/tasks/${task.id}`)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '任务创建失败'
  } finally {
    submitting.value = false
  }
}

onMounted(loadOptions)
</script>

<template>
  <div class="page-grid">
    <SectionPanel class="span-5" title="创建资源生成任务" subtitle="POST /api/tasks/resource-generation">
      <ErrorNotice :message="error" />
      <LoadingBlock :show="loading" />
      <form class="form-grid" @submit.prevent="submit">
        <div class="field">
          <label>学生画像 <span class="required-mark">*</span></label>
          <select v-model="form.studentProfileId" required>
            <option value="" disabled>请选择学生</option>
            <option v-for="profile in profiles" :key="profile.id" :value="profile.id">
              {{ profile.studentName }} - {{ profile.learningGoal }}
            </option>
          </select>
          <small v-if="formErrors.studentProfileId" class="field-error">{{ formErrors.studentProfileId }}</small>
        </div>
        <div class="field">
          <label>课程 <span class="required-mark">*</span></label>
          <select v-model="form.courseId" required>
            <option value="" disabled>请选择课程</option>
            <option v-for="course in courses" :key="course.id" :value="course.id">
              {{ course.title }}
            </option>
          </select>
          <small v-if="formErrors.courseId" class="field-error">{{ formErrors.courseId }}</small>
        </div>
        <div class="field">
          <label>资源类型 <span class="required-mark">*</span></label>
          <select v-model="form.resourceType" required>
            <option v-for="type in resourceTypes" :key="type.code" :value="type.code">
              {{ type.displayName }}
            </option>
          </select>
          <small v-if="usingFallbackResourceTypes" class="field-help">资源类型接口暂不可用，当前使用前端兜底选项。</small>
          <small v-if="formErrors.resourceType" class="field-error">{{ formErrors.resourceType }}</small>
        </div>
        <div class="field">
          <label>主题 <span class="required-mark">*</span></label>
          <input v-model="form.topic" required />
          <small v-if="formErrors.topic" class="field-error">{{ formErrors.topic }}</small>
        </div>
        <div class="field">
          <label>模态 <span class="required-mark">*</span></label>
          <input v-model="form.modality" />
          <small v-if="formErrors.modality" class="field-error">{{ formErrors.modality }}</small>
        </div>
        <div class="field">
          <label>生成要求 <span class="required-mark">*</span></label>
          <textarea v-model="form.prompt" />
          <small v-if="formErrors.prompt" class="field-error">{{ formErrors.prompt }}</small>
        </div>
        <button class="button" :disabled="!canSubmit">
          <Send :size="17" />创建并进入任务详情
        </button>
      </form>
      <LoadingBlock :show="submitting" text="正在创建生成任务" />
      <div v-if="!profiles.length || !courses.length" class="notice warn-notice">
        <span>请先在“学生画像”和“课程资源”页面创建至少一个学生画像和一门课程。</span>
      </div>
    </SectionPanel>

    <SectionPanel class="span-7" title="比赛演示链路">
      <div class="demo-context">
        <div>
          <strong>当前学生</strong>
          <span>{{ selectedProfile?.studentName || '未选择' }}</span>
          <small>{{ selectedProfile?.learningGoal || '选择画像后生成会结合学习目标和薄弱点。' }}</small>
        </div>
        <div>
          <strong>当前课程</strong>
          <span>{{ selectedCourse?.title || '未选择' }}</span>
          <small>{{ selectedCourse?.description || '选择课程后生成会结合课程知识结构。' }}</small>
        </div>
      </div>
      <div class="timeline">
        <div class="timeline-item">
          <span class="timeline-index">1</span>
          <div class="timeline-body">
            <h3>画像分析</h3>
            <p>读取学生基础、偏好、目标和薄弱点，为后续资源定制提供依据。</p>
            <StatusPill status="Profile Analyzer" tone="info" />
          </div>
        </div>
        <div class="timeline-item">
          <span class="timeline-index">2</span>
          <div class="timeline-body">
            <h3>多智能体生成</h3>
            <p>路径规划、文档生成、题库、思维导图、实操案例和 PPT 课件协作产出。</p>
            <StatusPill status="9-step workflow" tone="ok" />
          </div>
        </div>
        <div class="timeline-item">
          <span class="timeline-index">3</span>
          <div class="timeline-body">
            <h3>防幻觉审计</h3>
            <p>生成后强制执行引用覆盖、学术准确性、内容安全和人工复核门禁。</p>
            <StatusPill status="Content Audit" tone="warn" />
          </div>
        </div>
      </div>
    </SectionPanel>

    <SectionPanel class="span-12" title="资源类型覆盖">
      <div v-if="usingFallbackResourceTypes" class="notice warn-notice">
        <span>GET /api/resource-types 暂未返回可用数据，以下资源类型为前端兜底选项，仅用于保证演示流程不断。</span>
      </div>
      <div class="page-grid">
        <article v-for="type in resourceTypes" :key="type.code" class="metric-tile span-3">
          <span>{{ type.code }}</span>
          <strong style="font-size: 18px">{{ type.displayName }}</strong>
        </article>
      </div>
      <div v-if="!resourceTypes.length" class="empty-state"><Sparkles :size="18" />等待后端资源类型接口</div>
    </SectionPanel>
  </div>
</template>
