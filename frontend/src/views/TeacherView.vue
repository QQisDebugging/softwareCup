<script setup lang="ts">
import type { EChartsOption } from 'echarts'
import { Download, Play } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { agentsApi, coursesApi, profilesApi } from '@/api'
import ChartPanel from '@/components/ChartPanel.vue'
import ErrorNotice from '@/components/ErrorNotice.vue'
import JsonBlock from '@/components/JsonBlock.vue'
import LoadingBlock from '@/components/LoadingBlock.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import StatusPill from '@/components/StatusPill.vue'
import type { Course, ProfileResponse } from '@/types/api'
import { downloadJson, safeFilePart } from '@/utils/download'

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

const diagnosisOption = computed<EChartsOption>(() => ({
  tooltip: {},
  graphic: diagnosis.value ? undefined : { type: 'text', left: 'center', top: 'middle', style: { text: '等待课程诊断', fill: '#61708a' } },
  series: [
    {
      type: 'gauge',
      min: 0,
      max: 100,
      progress: { show: true, width: 14 },
      detail: { formatter: '{value}%' },
      data: [{ value: Number(diagnosis.value?.coverageScore || 0), name: '课程覆盖率' }],
    },
  ],
}))

const analyticsOption = computed<EChartsOption>(() => ({
  tooltip: {},
  graphic: analytics.value ? undefined : { type: 'text', left: 'center', top: 'middle', style: { text: '等待班级分析', fill: '#61708a' } },
  radar: {
    indicator: [
      { name: '班级掌握度', max: 100 },
      { name: '参与度', max: 100 },
      { name: '干预紧迫度', max: 100 },
      { name: '资源完整度', max: 100 },
    ],
  },
  series: [
    {
      type: 'radar',
      data: [
        {
          value: [
            Number(analytics.value?.classMasteryAverage || 0),
            Number(analytics.value?.engagementAverage || 0),
            Array.isArray(analytics.value?.studentRiskProfiles) ? Math.min(100, Number(analytics.value?.studentRiskProfiles.length) * 18) : 0,
            Array.isArray(analytics.value?.resourceGaps) ? Math.max(20, 100 - Number(analytics.value?.resourceGaps.length) * 12) : 0,
          ],
        },
      ],
    },
  ],
}))

async function loadOptions() {
  loading.value = true
  error.value = ''
  try {
    const [courseList, profileList] = await Promise.all([coursesApi.list(), profilesApi.list()])
    courses.value = courseList
    profiles.value = profileList
    selectedCourseId.value ||= courseList[0]?.id || ''
    selectedProfileId.value ||= profileList[0]?.id || ''
  } catch (err) {
    error.value = err instanceof Error ? err.message : '教师端选项加载失败'
  } finally {
    loading.value = false
  }
}

async function runDiagnosis() {
  running.value = 'diagnosis'
  error.value = ''
  try {
    diagnosis.value = await agentsApi.invoke('/teaching/course-diagnostics', {
      courseId: selectedCourseId.value,
      courseTitle: selectedCourse.value?.title || '',
      courseDescription: selectedCourse.value?.description || '',
      syllabusText: selectedCourse.value?.syllabusJson || '',
      targetStudentProfile: selectedProfile.value?.dialogueSummary || selectedProfile.value?.currentLevel || '',
    })
  } catch (err) {
    error.value = err instanceof Error ? err.message : '课程诊断失败'
  } finally {
    running.value = ''
  }
}

async function runAnalytics() {
  running.value = 'analytics'
  error.value = ''
  try {
    analytics.value = await agentsApi.invoke('/teaching/class-analytics', {
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
      ],
    })
  } catch (err) {
    error.value = err instanceof Error ? err.message : '班级分析失败'
  } finally {
    running.value = ''
  }
}

onMounted(loadOptions)
</script>

<template>
  <div class="page-grid">
    <SectionPanel class="span-12" title="教师端参数">
      <ErrorNotice :message="error" />
      <LoadingBlock :show="loading" />
      <div class="split-row">
        <div class="field">
          <label>课程</label>
          <select v-model="selectedCourseId">
            <option v-for="course in courses" :key="course.id" :value="course.id">{{ course.title }}</option>
          </select>
        </div>
        <div class="field">
          <label>代表学生</label>
          <select v-model="selectedProfileId">
            <option v-for="profile in profiles" :key="profile.id" :value="profile.id">{{ profile.studentName }}</option>
          </select>
        </div>
      </div>
      <div class="field">
        <label>分析主题</label>
        <input v-model="topic" />
      </div>
      <div v-if="!courses.length" class="notice warn-notice">请先创建课程，教师端诊断依赖 courseId。</div>
    </SectionPanel>

    <SectionPanel class="span-6" title="课程诊断" subtitle="POST /api/teaching/course-diagnostics">
      <template #actions>
        <button class="ghost-button" :disabled="!diagnosis" @click="downloadJson(`${safeFilePart(topic)}-course-diagnosis.json`, diagnosis)">
          <Download :size="17" />JSON
        </button>
        <button class="button" :disabled="running === 'diagnosis' || !selectedCourseId" @click="runDiagnosis"><Play :size="17" />诊断</button>
      </template>
      <LoadingBlock :show="running === 'diagnosis'" />
      <ChartPanel :option="diagnosisOption" :height="260" />
      <div v-if="diagnosis" class="timeline">
        <div class="timeline-body">
          <strong>缺失知识点</strong>
          <p>{{ Array.isArray(diagnosis.missingKnowledgePoints) ? diagnosis.missingKnowledgePoints.join('、') : '-' }}</p>
        </div>
        <div class="timeline-body">
          <strong>建设任务</strong>
          <p>{{ Array.isArray(diagnosis.recommendedTasks) ? diagnosis.recommendedTasks.join('；') : '-' }}</p>
        </div>
      </div>
    </SectionPanel>

    <SectionPanel class="span-6" title="班级学情分析" subtitle="POST /api/teaching/class-analytics">
      <template #actions>
        <button class="ghost-button" :disabled="!analytics" @click="downloadJson(`${safeFilePart(topic)}-class-analytics.json`, analytics)">
          <Download :size="17" />JSON
        </button>
        <button class="button" :disabled="running === 'analytics' || !selectedCourseId" @click="runAnalytics"><Play :size="17" />分析</button>
      </template>
      <LoadingBlock :show="running === 'analytics'" />
      <ChartPanel :option="analyticsOption" :height="260" />
      <div v-if="analytics" class="timeline">
        <div class="timeline-body">
          <div class="section-head">
            <strong>班级趋势</strong>
            <StatusPill :status="String(analytics.classTrend || '-')" tone="info" />
          </div>
          <p>{{ Array.isArray(analytics.interventionPriority) ? analytics.interventionPriority.join('；') : '-' }}</p>
        </div>
      </div>
    </SectionPanel>

    <SectionPanel class="span-12" title="教师端原始响应">
      <JsonBlock :value="{ diagnosis, analytics }" />
    </SectionPanel>
  </div>
</template>
