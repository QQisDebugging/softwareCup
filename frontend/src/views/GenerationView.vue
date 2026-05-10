<script setup lang="ts">
import { Send, Sparkles } from 'lucide-vue-next'
import { onMounted, reactive, ref } from 'vue'
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

const form = reactive({
  studentProfileId: '',
  courseId: '',
  topic: 'Spring Boot Controller 与 REST API',
  resourceType: 'COURSE_EXPLANATION_DOCUMENT',
  modality: '文本+图解脚本',
  prompt: '面向 Java 基础较弱的大二学生，用项目案例讲解 Controller、DTO 和 Service 分层，并附带练习题和防错提示。',
})

async function loadOptions() {
  loading.value = true
  error.value = ''
  try {
    const [profileList, courseList, typeList] = await Promise.all([
      profilesApi.list(),
      coursesApi.list(),
      coursesApi.resourceTypes(),
    ])
    profiles.value = profileList
    courses.value = courseList
    resourceTypes.value = typeList
    form.studentProfileId ||= profileList[0]?.id || ''
    form.courseId ||= courseList[0]?.id || ''
    form.resourceType ||= typeList[0]?.code || ''
  } catch (err) {
    error.value = err instanceof Error ? err.message : '生成选项加载失败'
  } finally {
    loading.value = false
  }
}

async function submit() {
  submitting.value = true
  error.value = ''
  try {
    const task = await tasksApi.createResourceGeneration({ ...form })
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
          <label>学生画像</label>
          <select v-model="form.studentProfileId" required>
            <option value="" disabled>请选择学生</option>
            <option v-for="profile in profiles" :key="profile.id" :value="profile.id">
              {{ profile.studentName }} - {{ profile.learningGoal }}
            </option>
          </select>
        </div>
        <div class="field">
          <label>课程</label>
          <select v-model="form.courseId" required>
            <option value="" disabled>请选择课程</option>
            <option v-for="course in courses" :key="course.id" :value="course.id">
              {{ course.title }}
            </option>
          </select>
        </div>
        <div class="field">
          <label>资源类型</label>
          <select v-model="form.resourceType" required>
            <option v-for="type in resourceTypes" :key="type.code" :value="type.code">
              {{ type.displayName }}
            </option>
          </select>
        </div>
        <div class="field">
          <label>主题</label>
          <input v-model="form.topic" required />
        </div>
        <div class="field">
          <label>模态</label>
          <input v-model="form.modality" />
        </div>
        <div class="field">
          <label>生成要求</label>
          <textarea v-model="form.prompt" />
        </div>
        <button class="button" :disabled="submitting || !form.studentProfileId || !form.courseId || !form.resourceType || !form.topic">
          <Send :size="17" />创建并进入任务详情
        </button>
      </form>
      <div v-if="!profiles.length || !courses.length" class="notice warn-notice">
        请先在“学生画像”和“课程资源”页面创建至少一个学生画像和一门课程。
      </div>
    </SectionPanel>

    <SectionPanel class="span-7" title="比赛演示链路">
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
