<script setup lang="ts">
import { Download, RefreshCw, Save } from 'lucide-vue-next'
import { computed, onMounted, reactive, ref } from 'vue'
import { coursesApi } from '@/api'
import ErrorNotice from '@/components/ErrorNotice.vue'
import LoadingBlock from '@/components/LoadingBlock.vue'
import MarkdownView from '@/components/MarkdownView.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import StatusPill from '@/components/StatusPill.vue'
import type { Course, LearningResource } from '@/types/api'
import { downloadJson, downloadText, safeFilePart } from '@/utils/download'
import { compact, formatDate } from '@/utils/format'

const loading = ref(false)
const saving = ref(false)
const error = ref('')
const courses = ref<Course[]>([])
const selectedCourse = ref<Course | null>(null)
const resources = ref<LearningResource[]>([])
const selectedResource = ref<LearningResource | null>(null)

const form = reactive({
  title: 'Java Web 应用开发与软件工程实践',
  department: '计算机科学与技术',
  description: '覆盖 Spring Boot、数据库、REST API、文件上传、异步任务、测试与部署。',
  creditHours: 48,
  syllabusJson: JSON.stringify(
    {
      weeks: [
        { week: 1, topic: '课程导论与工程环境' },
        { week: 2, topic: 'Java Web 与 HTTP 基础' },
        { week: 3, topic: 'Spring Boot 项目结构' },
        { week: 4, topic: 'REST API 设计' },
      ],
    },
    null,
    2,
  ),
})

const syllabusParseError = computed(() => {
  if (!form.syllabusJson.trim()) return ''
  try {
    JSON.parse(form.syllabusJson)
    return ''
  } catch {
    return '教学大纲必须是合法 JSON，或清空后再保存。'
  }
})

const formErrors = computed<Record<string, string>>(() => {
  const errors: Record<string, string> = {}
  if (!form.title.trim()) errors.title = '请输入课程名称'
  if (!form.department.trim()) errors.department = '请输入院系'
  if (!form.description.trim()) errors.description = '请输入课程描述'
  if (!Number.isFinite(Number(form.creditHours)) || Number(form.creditHours) <= 0) errors.creditHours = '学时必须大于 0'
  if (syllabusParseError.value) errors.syllabusJson = syllabusParseError.value
  return errors
})

const canCreateCourse = computed(() => !saving.value && Object.keys(formErrors.value).length === 0)
const canDownloadCourse = computed(() => Boolean(selectedCourse.value?.title))

async function loadCourses() {
  loading.value = true
  error.value = ''
  try {
    courses.value = await coursesApi.list()
    if (!selectedCourse.value && courses.value.length) {
      await selectCourse(courses.value[0])
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '课程加载失败'
  } finally {
    loading.value = false
  }
}

async function selectCourse(course: Course) {
  error.value = ''
  try {
    selectedCourse.value = course
    selectedResource.value = null
    resources.value = await coursesApi.resources(course.id)
  } catch (err) {
    resources.value = []
    error.value = err instanceof Error ? err.message : '课程资源加载失败'
  }
}

async function createCourse() {
  if (!canCreateCourse.value) {
    error.value = Object.values(formErrors.value)[0] || '请先补全课程表单。'
    return
  }
  saving.value = true
  error.value = ''
  try {
    const created = await coursesApi.create({ ...form })
    await loadCourses()
    if (created.id) await selectCourse(created)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '课程创建失败'
  } finally {
    saving.value = false
  }
}

function downloadCourse() {
  if (!canDownloadCourse.value || !selectedCourse.value) return
  downloadJson(`${safeFilePart(selectedCourse.value.title)}-course.json`, {
    course: selectedCourse.value,
    resources: resources.value,
  })
}

function downloadResource(resource: LearningResource) {
  downloadText(`${safeFilePart(resource.title)}.md`, resource.content || '', 'text/markdown;charset=utf-8')
}

onMounted(loadCourses)
</script>

<template>
  <div class="page-grid">
    <SectionPanel class="span-12" title="课程到资源链路" subtitle="先创建或选择课程，再在资源生成页面绑定学生画像生成个性化学习资源">
      <div class="profile-flow">
        <div class="profile-flow-item">
          <span>1</span>
          <strong>创建课程</strong>
          <small>课程信息与教学大纲进入后端知识上下文</small>
        </div>
        <div class="profile-flow-item">
          <span>2</span>
          <strong>查看资源库</strong>
          <small>课程下已生成资源集中展示</small>
        </div>
        <div class="profile-flow-item">
          <span>3</span>
          <strong>选择画像生成</strong>
          <small>跳转资源生成，绑定学生画像和课程</small>
        </div>
        <div class="profile-flow-item">
          <span>4</span>
          <strong>下载材料</strong>
          <small>课程 JSON 与资源 Markdown 可导出</small>
        </div>
      </div>
    </SectionPanel>

    <SectionPanel class="span-4" title="创建课程" subtitle="POST /api/courses">
      <ErrorNotice :message="error" />
      <form class="form-grid" @submit.prevent="createCourse">
        <div class="field">
          <label>课程名称 <span class="required-mark">*</span></label>
          <input v-model="form.title" required />
          <small v-if="formErrors.title" class="field-error">{{ formErrors.title }}</small>
        </div>
        <div class="field">
          <label>院系 <span class="required-mark">*</span></label>
          <input v-model="form.department" />
          <small v-if="formErrors.department" class="field-error">{{ formErrors.department }}</small>
        </div>
        <div class="field">
          <label>学时 <span class="required-mark">*</span></label>
          <input v-model.number="form.creditHours" type="number" min="1" />
          <small v-if="formErrors.creditHours" class="field-error">{{ formErrors.creditHours }}</small>
        </div>
        <div class="field">
          <label>描述 <span class="required-mark">*</span></label>
          <textarea v-model="form.description" />
          <small v-if="formErrors.description" class="field-error">{{ formErrors.description }}</small>
        </div>
        <div class="field">
          <label>教学大纲 JSON</label>
          <textarea v-model="form.syllabusJson" class="code-area" />
          <small class="field-help">支持后端课程知识结构，留空或填写合法 JSON。</small>
          <small v-if="formErrors.syllabusJson" class="field-error">{{ formErrors.syllabusJson }}</small>
        </div>
        <button class="button" :disabled="!canCreateCourse"><Save :size="17" />保存课程</button>
      </form>
      <LoadingBlock :show="saving" text="正在保存课程" />
    </SectionPanel>

    <SectionPanel class="span-8" title="课程与资源">
      <template #actions>
        <button class="ghost-button" @click="loadCourses"><RefreshCw :size="17" />刷新</button>
        <button class="ghost-button" :disabled="!canDownloadCourse" @click="downloadCourse"><Download :size="17" />导出</button>
      </template>
      <LoadingBlock :show="loading" />
      <div class="split-row">
        <div>
          <h3>课程列表</h3>
          <div v-if="!courses.length && !loading" class="empty-guide">
            <strong>暂无课程</strong>
            <span>先创建一门课程；如果后端离线，请启动 Spring Boot 后刷新。</span>
          </div>
          <div v-else class="timeline">
            <button
              v-for="course in courses"
              :key="course.id"
              class="timeline-body clickable-row"
              :style="{ borderColor: selectedCourse?.id === course.id ? '#2f6fef' : undefined }"
              @click="selectCourse(course)"
            >
              <strong>{{ course.title }}</strong>
              <p>{{ compact(course.description, 90) }}</p>
              <small>{{ course.department }} / {{ formatDate(course.updatedAt) }}</small>
            </button>
          </div>
        </div>
        <div>
          <h3>生成资源</h3>
          <div v-if="!selectedCourse" class="empty-guide">
            <strong>请选择课程</strong>
            <span>选择课程后展示其已生成资源。</span>
          </div>
          <div v-else-if="!resources.length" class="empty-guide">
            <strong>暂无资源</strong>
            <span>可以前往“资源生成”页面，为当前课程创建个性化资源。</span>
            <RouterLink class="button" to="/generation">去生成资源</RouterLink>
          </div>
          <div v-else class="timeline">
            <div v-for="resource in resources" :key="resource.id" class="timeline-body">
              <div class="section-head">
                <div>
                  <strong>{{ resource.title }}</strong>
                  <p>{{ resource.modality }} / {{ resource.estimatedMinutes }} 分钟</p>
                </div>
                <StatusPill :status="resource.resourceTypeName || resource.resourceType" tone="info" />
              </div>
              <p>{{ compact(resource.content, 150) }}</p>
              <div class="button-row">
                <button class="ghost-button" @click="selectedResource = resource">预览</button>
                <button class="ghost-button" @click="downloadResource(resource)"><Download :size="16" />Markdown</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </SectionPanel>

    <SectionPanel class="span-12" title="资源预览">
      <div v-if="!selectedResource" class="empty-guide">
        <strong>选择一个资源预览正文</strong>
        <span>资源内容支持 Markdown 展示，并可单独下载。</span>
      </div>
      <MarkdownView v-else :content="selectedResource.content" />
    </SectionPanel>
  </div>
</template>
