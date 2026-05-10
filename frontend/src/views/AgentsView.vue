<script setup lang="ts">
import { Download, Play, RefreshCw } from 'lucide-vue-next'
import { computed, onMounted, ref, watch } from 'vue'
import { agentsApi, coursesApi, profilesApi } from '@/api'
import ErrorNotice from '@/components/ErrorNotice.vue'
import JsonBlock from '@/components/JsonBlock.vue'
import LoadingBlock from '@/components/LoadingBlock.vue'
import MarkdownView from '@/components/MarkdownView.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import StatusPill from '@/components/StatusPill.vue'
import type { AgentArtifact, AgentDefinition, AgentTool, Course, ProfileResponse } from '@/types/api'
import { downloadJson, safeFilePart } from '@/utils/download'
import { compact, formatDate, parseMaybeJson } from '@/utils/format'

const loading = ref(false)
const invoking = ref(false)
const error = ref('')
const definitions = ref<AgentDefinition[]>([])
const artifacts = ref<AgentArtifact[]>([])
const profiles = ref<ProfileResponse[]>([])
const courses = ref<Course[]>([])
const selectedToolKey = ref('path')
const payloadText = ref('')
const response = ref<Record<string, unknown> | null>(null)

const payloadParseError = computed(() => {
  try {
    JSON.parse(payloadText.value || '{}')
    return ''
  } catch {
    return '请求 JSON 格式错误，请修正后再调用。'
  }
})

const context = computed(() => ({
  studentProfileId: profiles.value[0]?.id || 'demo-profile',
  courseId: courses.value[0]?.id || 'demo-course',
  studentProfileSummary: profiles.value[0]?.dialogueSummary || 'Java 基础较弱，喜欢图解和项目案例。',
  courseTitle: courses.value[0]?.title || 'Java Web 应用开发与软件工程实践',
}))

const tools = computed<AgentTool[]>(() => [
  {
    key: 'path',
    title: '学习路径规划',
    endpoint: '/learning/path-plans',
    category: '学生端',
    samplePayload: { ...context.value, topic: 'Spring Boot Controller 与 REST API', timeframeDays: 7, dailyMinutes: 45 },
  },
  {
    key: 'graph',
    title: '知识图谱',
    endpoint: '/learning/knowledge-graphs',
    category: '学生端',
    samplePayload: { courseId: context.value.courseId, courseTitle: context.value.courseTitle, topic: 'REST API 分层', weaknessSignals: ['MVC 分层职责'] },
  },
  {
    key: 'audit',
    title: '防幻觉审计',
    endpoint: '/learning/content-audits',
    category: '安全',
    samplePayload: { courseTitle: context.value.courseTitle, topic: 'Controller 分层', content: 'Controller 可以直接保存数据库以提升效率。', citations: [] },
  },
  {
    key: 'prereq',
    title: '先修诊断',
    endpoint: '/learning/prerequisites/diagnose',
    category: '诊断',
    samplePayload: { ...context.value, targetTopic: 'Spring Boot Controller 与 REST API', completedTopics: ['Java 面向对象基础'], assessmentWeaknesses: ['HTTP 请求响应'] },
  },
  {
    key: 'curate',
    title: '资源策展',
    endpoint: '/learning/resource-bundles/curate',
    category: '资源',
    samplePayload: { ...context.value, topic: 'Spring Boot Controller 与 REST API', weaknesses: ['MVC 分层职责'], timeBudgetMinutes: 120 },
  },
  {
    key: 'portfolio',
    title: '学习档案报告',
    endpoint: '/learning/portfolio-reports',
    category: '报告',
    samplePayload: { ...context.value, studentName: '张同学', topic: 'Spring Boot Controller 与 REST API', completedResources: ['完成图解资源'], assessmentSummaries: ['入口测评 58/100，复测 72/100'] },
  },
  {
    key: 'trace',
    title: '智能体追踪',
    endpoint: '/learning/agent-traces',
    category: '可解释',
    samplePayload: { taskName: '个性化资源生成', userIntent: '生成 REST API 分层资源', involvedAgents: ['profile_agent', 'resource_generator_agent', 'content_audit_agent'], requestPayload: { topic: 'REST API' } },
  },
  {
    key: 'profile-infer',
    title: '画像推断',
    endpoint: '/profiles/agent-infer',
    category: '画像',
    samplePayload: { courseTitle: context.value.courseTitle, declaredMajor: '软件工程', currentLevel: 'Java 基础较弱', learningGoal: '掌握 REST API 分层', dialogueTurns: ['我总是混淆 Controller 和 Service。'] },
  },
  {
    key: 'events',
    title: '学习事件分析',
    endpoint: '/learning/events/analyze',
    category: '闭环',
    samplePayload: { ...context.value, targetTopic: 'Spring Boot Controller 与 REST API', learningEvents: ['完成 2 个资源卡', '错题复盘：Controller 直接访问 Repository'], assessmentSummaries: ['58/100', '72/100'] },
  },
  {
    key: 'item-analysis',
    title: '测评题目分析',
    endpoint: '/learning/assessments/item-analysis',
    category: '教师端',
    samplePayload: { courseId: context.value.courseId, courseTitle: context.value.courseTitle, topic: 'REST API', attempts: [{ questionId: 'q1', knowledgePoint: 'MVC 分层职责', questionType: '简答题', score: 5, maxScore: 15, correct: false, feedback: '职责混淆' }] },
  },
  {
    key: 'project-review',
    title: '项目级代码审查',
    endpoint: '/learning/code-projects/review',
    category: '代码',
    samplePayload: { ...context.value, projectTitle: 'REST API 分层练习', files: [{ path: 'UserController.java', language: 'Java', content: '@RestController class UserController { UserRepository repo; User save(@RequestBody User u){ return repo.save(u); } }' }] },
  },
  {
    key: 'storyboard',
    title: '多模态分镜',
    endpoint: '/learning/storyboards',
    category: '多模态',
    samplePayload: { ...context.value, topic: 'Controller 与 Service 分层', targetDurationMinutes: 5 },
  },
])

const selectedTool = computed(() => tools.value.find((item) => item.key === selectedToolKey.value) || tools.value[0])

const markdownCandidate = computed(() => {
  const value = response.value
  if (!value) return ''
  return String(value.content || value.summary || value.timelineMarkdown || value.answer || value.feedback || '')
})

watch(selectedTool, (tool) => {
  payloadText.value = JSON.stringify(tool.samplePayload, null, 2)
  response.value = null
}, { immediate: true })

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [definitionList, profileList, courseList] = await Promise.all([
      agentsApi.definitions(),
      profilesApi.list(),
      coursesApi.list(),
    ])
    definitions.value = definitionList
    profiles.value = profileList
    courses.value = courseList
    artifacts.value = profileList[0]?.id ? await agentsApi.artifacts({ studentProfileId: profileList[0].id }) : []
  } catch (err) {
    error.value = err instanceof Error ? err.message : '智能体信息加载失败'
  } finally {
    loading.value = false
  }
}

async function invokeTool() {
  if (payloadParseError.value) {
    error.value = payloadParseError.value
    return
  }
  invoking.value = true
  error.value = ''
  try {
    const payload = JSON.parse(payloadText.value) as Record<string, unknown>
    response.value = await agentsApi.invoke(selectedTool.value.endpoint, payload)
    if (profiles.value[0]?.id) artifacts.value = await agentsApi.artifacts({ studentProfileId: profiles.value[0].id })
  } catch (err) {
    error.value = err instanceof Error ? err.message : '智能体调用失败'
  } finally {
    invoking.value = false
  }
}

function resetPayload() {
  payloadText.value = JSON.stringify(selectedTool.value.samplePayload, null, 2)
}

onMounted(load)
</script>

<template>
  <div class="page-grid">
    <SectionPanel class="span-4" title="智能体工具箱" subtitle="全部通过 Java 后端代理">
      <template #actions>
        <button class="ghost-button" @click="load"><RefreshCw :size="17" />刷新</button>
      </template>
      <ErrorNotice :message="error" />
      <LoadingBlock :show="loading" />
      <div class="timeline">
        <button
          v-for="tool in tools"
          :key="tool.key"
          class="timeline-body clickable-row"
          :style="{ borderColor: tool.key === selectedToolKey ? '#2f6fef' : undefined }"
          @click="selectedToolKey = tool.key"
        >
          <div class="section-head">
            <strong>{{ tool.title }}</strong>
            <StatusPill :status="tool.category" tone="info" />
          </div>
          <small>{{ tool.endpoint }}</small>
        </button>
      </div>
    </SectionPanel>

    <SectionPanel class="span-8" :title="selectedTool.title" :subtitle="selectedTool.endpoint">
      <template #actions>
        <button class="ghost-button" @click="resetPayload">示例</button>
        <button class="button" :disabled="invoking || !!payloadParseError" @click="invokeTool"><Play :size="17" />调用</button>
      </template>
      <div class="field">
        <label>请求 JSON</label>
        <textarea v-model="payloadText" class="code-area" />
      </div>
      <ErrorNotice :message="payloadParseError" />
      <LoadingBlock :show="invoking" text="智能体正在处理" />
    </SectionPanel>

    <SectionPanel class="span-7" title="响应展示">
      <template #actions>
        <button class="ghost-button" :disabled="!response" @click="downloadJson(`${safeFilePart(selectedTool.title)}.json`, response)">
          <Download :size="17" />JSON
        </button>
      </template>
      <div v-if="!response" class="empty-state">提交请求后展示结构化结果</div>
      <template v-else>
        <MarkdownView v-if="markdownCandidate" :content="markdownCandidate" />
        <JsonBlock :value="response" />
      </template>
    </SectionPanel>

    <SectionPanel class="span-5" title="已启用智能体与产物">
      <p><strong>{{ definitions.length }}</strong> 个后端智能体定义，<strong>{{ artifacts.length }}</strong> 条近期产物。</p>
      <div class="timeline">
        <div v-for="item in artifacts.slice(0, 6)" :key="item.id" class="timeline-body">
          <div class="section-head">
            <strong>{{ item.artifactType }}</strong>
            <StatusPill :status="item.status" :tone="item.status === 'SUCCEEDED' ? 'ok' : 'warn'" />
          </div>
          <p>{{ compact(String(parseMaybeJson<Record<string, unknown>>(item.payloadJson, {}).summary || item.requestSummary || '-'), 120) }}</p>
          <small>{{ item.agentEndpoint }} / {{ formatDate(item.createdAt) }}</small>
        </div>
      </div>
    </SectionPanel>
  </div>
</template>
