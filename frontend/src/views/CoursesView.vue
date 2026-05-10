<script setup lang="ts">
import { Download, RefreshCw, Save } from 'lucide-vue-next'
import { onMounted, reactive, ref } from 'vue'
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
  saving.value = true
  error.value = ''
  try {
    const created = await coursesApi.create({ ...form })
    await loadCourses()
    await selectCourse(created)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '课程创建失败'
  } finally {
    saving.value = false
  }
}

function downloadCourse() {
  if (!selectedCourse.value) return
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
    <SectionPanel class="span-4" title="创建课程" subtitle="POST /api/courses">
      <ErrorNotice :message="error" />
      <form class="form-grid" @submit.prevent="createCourse">
        <div class="field">
          <label>课程名称</label>
          <input v-model="form.title" required />
        </div>
        <div class="field">
          <label>院系</label>
          <input v-model="form.department" />
        </div>
        <div class="field">
          <label>学时</label>
          <input v-model.number="form.creditHours" type="number" min="1" />
        </div>
        <div class="field">
          <label>描述</label>
          <textarea v-model="form.description" />
        </div>
        <div class="field">
          <label>教学大纲 JSON</label>
          <textarea v-model="form.syllabusJson" class="code-area" />
        </div>
        <button class="button" :disabled="saving"><Save :size="17" />保存课程</button>
      </form>
      <LoadingBlock :show="saving" text="正在保存课程" />
    </SectionPanel>

    <SectionPanel class="span-8" title="课程与资源">
      <template #actions>
        <button class="ghost-button" @click="loadCourses"><RefreshCw :size="17" />刷新</button>
        <button class="ghost-button" :disabled="!selectedCourse" @click="downloadCourse"><Download :size="17" />导出</button>
      </template>
      <LoadingBlock :show="loading" />
      <div class="split-row">
        <div>
          <h3>课程列表</h3>
          <div v-if="!courses.length" class="empty-state">暂无课程</div>
          <div v-else class="timeline">
            <button v-for="course in courses" :key="course.id" class="timeline-body clickable-row" @click="selectCourse(course)">
              <strong>{{ course.title }}</strong>
              <p>{{ compact(course.description, 90) }}</p>
              <small>{{ course.department }} / {{ formatDate(course.updatedAt) }}</small>
            </button>
          </div>
        </div>
        <div>
          <h3>生成资源</h3>
          <div v-if="!resources.length" class="empty-state">暂无资源</div>
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
      <div v-if="!selectedResource" class="empty-state">选择一个资源预览正文</div>
      <MarkdownView v-else :content="selectedResource.content" />
    </SectionPanel>
  </div>
</template>
