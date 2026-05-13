<script setup lang="ts">
import { CheckCircle2, Download, Play, RefreshCw, Wand2 } from 'lucide-vue-next'
import { computed, onMounted, ref, watch } from 'vue'
import { agentsApi, coursesApi, profilesApi } from '@/api'
import ErrorNotice from '@/components/ErrorNotice.vue'
import JsonBlock from '@/components/JsonBlock.vue'
import LoadingBlock from '@/components/LoadingBlock.vue'
import MarkdownView from '@/components/MarkdownView.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import StatusPill from '@/components/StatusPill.vue'
import { useAppStore } from '@/stores/app'
import type { AgentArtifact, AgentDefinition, AgentTool, Course, ProfileResponse } from '@/types/api'
import { downloadJson, safeFilePart } from '@/utils/download'
import { compact, formatDate, isRecord, parseMaybeJson, safeStringify } from '@/utils/format'

const app = useAppStore()
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

const backendOffline = computed(() => Boolean(app.healthError && !app.backendOnline))

const payloadParseError = computed(() => {
  try {
    JSON.parse(payloadText.value || '{}')
    return ''
  } catch (err) {
    return err instanceof Error ? `请求 JSON 格式错误：${err.message}` : '请求 JSON 格式错误，请修正后再调用。'
  }
})

const context = computed(() => {
  const profile = profiles.value[0]
  const course = courses.value[0]
  return {
    studentProfileId: profile?.id || 'demo-profile-id',
    courseId: course?.id || 'demo-course-id',
    studentName: profile?.studentName || '张同学',
    courseTitle: course?.title || 'Java Web 应用开发与软件工程实践',
    studentProfileSummary: profile?.dialogueSummary || 'Java 基础较弱，喜欢图解、项目案例和短时任务。',
    learningGoal: profile?.learningGoal || '掌握 Spring Boot Controller、Service、Repository 分层开发',
    currentLevel: profile?.currentLevel || '大二，Java 基础较弱，刚接触 Spring Boot',
    topic: 'Spring Boot Controller 与 REST API',
  }
})

const tools = computed<AgentTool[]>(() => [
  {
    key: 'path',
    title: '学习路径规划',
    endpoint: '/learning/path-plans',
    proxyTarget: '/agents/path/plan',
    category: '学生端',
    description: '生成阶段目标、资源顺序和每日学习安排。',
    samplePayload: {
      studentProfileId: context.value.studentProfileId,
      courseId: context.value.courseId,
      studentProfileSummary: context.value.studentProfileSummary,
      courseTitle: context.value.courseTitle,
      topic: context.value.topic,
      timeframeDays: 7,
      dailyMinutes: 45,
      targetOutcome: '能够设计并实现一个分层 REST API',
    },
  },
  {
    key: 'graph',
    title: '知识图谱',
    endpoint: '/learning/knowledge-graphs',
    proxyTarget: '/agents/knowledge/graph',
    category: '学生端',
    description: '根据课程主题生成知识节点、依赖关系和学习顺序。',
    samplePayload: {
      courseId: context.value.courseId,
      courseTitle: context.value.courseTitle,
      topic: 'REST API 分层',
      weaknessSignals: ['MVC 分层职责', 'HTTP 请求响应', 'DTO 与 Entity 区分'],
      targetLevel: context.value.currentLevel,
    },
  },
  {
    key: 'audit',
    title: '防幻觉审计',
    endpoint: '/learning/content-audits',
    proxyTarget: '/agents/safety/audit',
    category: '安全',
    description: '审计内容准确性、引用覆盖、风险表述和人工复核点。',
    samplePayload: {
      courseTitle: context.value.courseTitle,
      topic: 'Controller 分层',
      content: 'Controller 可以直接保存数据库以提升效率。',
      citations: [],
      auditFocus: ['unsupportedClaims', 'riskyClaims', 'missingCitations', 'studentSafety'],
    },
  },
  {
    key: 'course-diagnosis',
    title: '课程诊断',
    endpoint: '/teaching/course-diagnostics',
    proxyTarget: '/agents/course/diagnose',
    category: '教师端',
    description: '诊断课程薄弱知识点、资源缺口和教学干预建议。',
    samplePayload: {
      courseId: context.value.courseId,
      courseTitle: context.value.courseTitle,
      topic: context.value.topic,
      classSize: 32,
      recentWeaknesses: ['分层职责混淆', '接口参数校验薄弱', '错误处理缺失'],
      resourceCoverage: ['讲义', '小测', '项目案例'],
    },
  },
  {
    key: 'code-generate',
    title: '代码练习生成',
    endpoint: '/learning/code-practice/generate',
    proxyTarget: '/agents/code/practice/generate',
    category: '代码',
    description: '生成可评分的代码练习、测试点和提示。',
    samplePayload: {
      studentProfileId: context.value.studentProfileId,
      courseId: context.value.courseId,
      topic: 'REST API 参数校验',
      language: 'Java',
      difficulty: '入门到进阶',
      constraints: ['Spring Boot', 'Controller-Service 分层', '包含单元测试要求'],
    },
  },
  {
    key: 'code-grade',
    title: '代码练习批改',
    endpoint: '/learning/code-practice/grade',
    proxyTarget: '/agents/code/practice/grade',
    category: '代码',
    description: '批改代码答案，输出得分、缺陷、修正建议和下一步动作。',
    samplePayload: {
      studentProfileId: context.value.studentProfileId,
      courseId: context.value.courseId,
      topic: 'REST API 参数校验',
      language: 'Java',
      prompt: '实现 UserController 的 createUser 接口并校验 name/email。',
      submission: '@PostMapping("/users") User create(@RequestBody User u){ return service.save(u); }',
      rubric: ['参数校验', '分层调用', '错误响应', '可测试性'],
    },
  },
  {
    key: 'storyboard',
    title: '多模态分镜',
    endpoint: '/learning/storyboards',
    proxyTarget: '/agents/multimodal/storyboard',
    category: '多模态',
    description: '生成短视频、图解或课堂展示的分镜脚本。',
    samplePayload: {
      studentProfileId: context.value.studentProfileId,
      courseId: context.value.courseId,
      topic: 'Controller 与 Service 分层',
      modality: '短视频+图解脚本',
      targetDurationMinutes: 5,
      visualStyle: '先类比，再代码，再练习',
    },
  },
  {
    key: 'prereq',
    title: '先修诊断',
    endpoint: '/learning/prerequisites/diagnose',
    proxyTarget: '/agents/prerequisite/diagnose',
    category: '诊断',
    description: '判断学习目标前的先修能力缺口和热身任务。',
    samplePayload: {
      studentProfileId: context.value.studentProfileId,
      courseId: context.value.courseId,
      targetTopic: context.value.topic,
      completedTopics: ['Java 面向对象基础', 'HTTP 请求响应基础'],
      assessmentWeaknesses: ['Controller 与 Service 职责混淆'],
      targetDeadlineDays: 7,
    },
  },
  {
    key: 'curate',
    title: '资源策展',
    endpoint: '/learning/resource-bundles/curate',
    proxyTarget: '/agents/resources/curate',
    category: '资源',
    description: '按学习目标和时间预算策展资源包。',
    samplePayload: {
      studentProfileId: context.value.studentProfileId,
      courseId: context.value.courseId,
      topic: context.value.topic,
      weaknesses: ['MVC 分层职责', 'DTO 与 Entity 区分'],
      preferredModalities: ['图解', '代码示例', '小测'],
      timeBudgetMinutes: 120,
    },
  },
  {
    key: 'portfolio',
    title: '学习档案报告',
    endpoint: '/learning/portfolio-reports',
    proxyTarget: '/agents/report/portfolio',
    category: '报告',
    description: '汇总学习证据、测评变化和画像更新建议。',
    samplePayload: {
      studentProfileId: context.value.studentProfileId,
      courseId: context.value.courseId,
      studentName: context.value.studentName,
      topic: context.value.topic,
      completedResources: ['完成 Controller 分层图解', '完成 REST API 小测'],
      assessmentSummaries: ['入口测评 58/100', '复测 72/100'],
      tutorNotes: ['仍需强化错误响应设计'],
    },
  },
  {
    key: 'trace',
    title: '智能体追踪',
    endpoint: '/learning/agent-traces',
    proxyTarget: '/agents/trace/explain',
    category: '可解释',
    description: '解释多智能体协作过程、输入输出和证据链。',
    samplePayload: {
      taskName: '个性化资源生成',
      userIntent: '生成 REST API 分层资源',
      involvedAgents: ['profile_agent', 'planner_agent', 'resource_generator_agent', 'content_audit_agent'],
      requestPayload: { topic: context.value.topic, studentProfileId: context.value.studentProfileId },
    },
  },
  {
    key: 'profile-infer',
    title: '画像推断',
    endpoint: '/profiles/agent-infer',
    proxyTarget: '/agents/profile/infer',
    category: '画像',
    description: '根据对话和学习证据推断画像维度。',
    samplePayload: {
      studentProfileId: context.value.studentProfileId,
      courseTitle: context.value.courseTitle,
      declaredMajor: '软件工程',
      currentLevel: context.value.currentLevel,
      learningGoal: context.value.learningGoal,
      dialogueTurns: ['我总是混淆 Controller 和 Service。', '我更喜欢先看图解再做小项目。'],
    },
  },
  {
    key: 'events',
    title: '学习事件分析',
    endpoint: '/learning/events/analyze',
    proxyTarget: '/agents/learning/events/analyze',
    category: '闭环',
    description: '分析学习事件、测评变化和干预触发点。',
    samplePayload: {
      studentProfileId: context.value.studentProfileId,
      courseId: context.value.courseId,
      targetTopic: context.value.topic,
      learningEvents: ['完成 2 个资源卡', '错题复盘：Controller 直接访问 Repository', '观看分层图解 6 分钟'],
      assessmentSummaries: ['58/100', '72/100'],
    },
  },
  {
    key: 'item-analysis',
    title: '测评题目分析',
    endpoint: '/learning/assessments/item-analysis',
    proxyTarget: '/agents/assessment/item-analysis',
    category: '教师端',
    description: '分析测评题目质量、错误分布和知识点覆盖。',
    samplePayload: {
      courseId: context.value.courseId,
      courseTitle: context.value.courseTitle,
      topic: 'REST API',
      attempts: [
        {
          questionId: 'q1',
          knowledgePoint: 'MVC 分层职责',
          questionType: '简答题',
          score: 5,
          maxScore: 15,
          correct: false,
          feedback: '职责混淆',
        },
      ],
    },
  },
  {
    key: 'project-review',
    title: '项目级代码审查',
    endpoint: '/learning/code-projects/review',
    proxyTarget: '/agents/code/project-review',
    category: '代码',
    description: '审查多文件项目结构、分层质量和可维护性。',
    samplePayload: {
      studentProfileId: context.value.studentProfileId,
      courseId: context.value.courseId,
      projectTitle: 'REST API 分层练习',
      files: [
        {
          path: 'UserController.java',
          language: 'Java',
          content: '@RestController class UserController { UserRepository repo; User save(@RequestBody User u){ return repo.save(u); } }',
        },
      ],
      reviewFocus: ['layering', 'validation', 'errorHandling', 'testability'],
    },
  },
  {
    key: 'class-analytics',
    title: '班级分析',
    endpoint: '/teaching/class-analytics',
    proxyTarget: '/agents/class/analytics',
    category: '教师端',
    description: '生成班级掌握度、风险学生和分层干预建议。',
    samplePayload: {
      courseId: context.value.courseId,
      courseTitle: context.value.courseTitle,
      topic: context.value.topic,
      classSize: 32,
      masterySnapshots: [
        { knowledgePoint: 'MVC 分层职责', masteryScore: 62 },
        { knowledgePoint: 'DTO 与 Entity 区分', masteryScore: 54 },
      ],
      riskStudents: [{ studentName: context.value.studentName, riskReason: '测评低分且学习时长不足' }],
    },
  },
  {
    key: 'demo-scenario',
    title: '评委演示脚本',
    endpoint: '/demo/scenario-plans',
    proxyTarget: '/agents/demo/scenario-plan',
    category: '评委模式',
    description: '生成答辩现场的演示顺序、证据点和备用路径。',
    samplePayload: {
      scenarioName: '软件杯智能教育系统答辩',
      studentProfileId: context.value.studentProfileId,
      courseId: context.value.courseId,
      highlightModules: ['学生画像', '资源生成', '多智能体过程', '学习闭环', '防幻觉审计'],
      timeLimitMinutes: 8,
      audience: '评委',
    },
  },
])

const selectedTool = computed(() => tools.value.find((item) => item.key === selectedToolKey.value) || tools.value[0])
const canInvoke = computed(() => !invoking.value && !payloadParseError.value && !backendOffline.value)

const responseSummary = computed(() => {
  const value = response.value
  if (!value) return ''
  const direct = value.summary || value.title || value.feedback || value.safetySummary
  if (typeof direct === 'string') return direct
  const content = markdownCandidate.value
  return content ? compact(content, 240) : '后端已返回结构化 JSON，详见原始响应。'
})

function stringList(value: unknown): string[] {
  const parsed = typeof value === 'string' ? parseMaybeJson<unknown>(value, value) : value
  if (Array.isArray(parsed)) {
    return parsed
      .map((item) => {
        if (typeof item === 'string') return item
        if (isRecord(item)) return String(item.title || item.text || item.url || item.source || item.label || safeStringify(item))
        return String(item)
      })
      .filter(Boolean)
  }
  if (typeof parsed === 'string' && parsed.trim()) return parsed.split(/\n|；|;/).map((item) => item.trim()).filter(Boolean)
  return []
}

const citations = computed(() => stringList(response.value?.citations || response.value?.references || response.value?.evidenceEndpoints))

const markdownCandidate = computed(() => {
  const value = response.value
  if (!value) return ''
  const parts = [
    value.markdown,
    value.contentMarkdown,
    value.timelineMarkdown,
    value.reportMarkdown,
    value.storyboardMarkdown,
    value.content,
    value.answer,
    value.feedback,
    value.summary,
  ]
  const text = parts.find((item) => typeof item === 'string' && item.trim())
  if (typeof text === 'string') return text
  if (typeof value.mermaidDiagram === 'string' && value.mermaidDiagram.trim()) {
    return `\`\`\`mermaid\n${value.mermaidDiagram}\n\`\`\``
  }
  return ''
})

watch(selectedTool, (tool) => {
  payloadText.value = safeStringify(tool.samplePayload)
  response.value = null
  error.value = ''
}, { immediate: true })

async function load() {
  loading.value = true
  error.value = ''
  await app.refreshHealth()
  const [definitionResult, profileResult, courseResult] = await Promise.allSettled([
    agentsApi.definitions(),
    profilesApi.list(),
    coursesApi.list(),
  ])
  definitions.value = definitionResult.status === 'fulfilled' ? definitionResult.value : []
  profiles.value = profileResult.status === 'fulfilled' ? profileResult.value : []
  courses.value = courseResult.status === 'fulfilled' ? courseResult.value : []
  if (profiles.value[0]?.id || courses.value[0]?.id) {
    try {
      artifacts.value = await agentsApi.artifacts({ studentProfileId: profiles.value[0]?.id, courseId: courses.value[0]?.id })
    } catch {
      artifacts.value = []
    }
  } else {
    artifacts.value = []
  }
  const failures = [definitionResult, profileResult, courseResult].filter((item) => item.status === 'rejected').length
  if (failures) error.value = `有 ${failures} 个基础接口暂不可用，工具列表仍可查看。`
  loading.value = false
}

function resetPayload() {
  payloadText.value = safeStringify(selectedTool.value.samplePayload)
  error.value = ''
}

function formatPayload() {
  if (payloadParseError.value) {
    error.value = payloadParseError.value
    return
  }
  payloadText.value = safeStringify(JSON.parse(payloadText.value || '{}'))
  error.value = ''
}

async function invokeTool() {
  if (backendOffline.value) {
    error.value = '后端离线：请启动 Spring Boot 后端后再调用智能体代理接口。'
    return
  }
  if (payloadParseError.value) {
    error.value = payloadParseError.value
    return
  }
  invoking.value = true
  error.value = ''
  try {
    const payload = JSON.parse(payloadText.value || '{}') as Record<string, unknown>
    response.value = await agentsApi.invoke(selectedTool.value.endpoint, payload)
    if (profiles.value[0]?.id || courses.value[0]?.id) {
      artifacts.value = await agentsApi.artifacts({ studentProfileId: profiles.value[0]?.id, courseId: courses.value[0]?.id })
    }
  } catch (err) {
    response.value = null
    error.value = err instanceof Error ? err.message : '智能体调用失败'
  } finally {
    invoking.value = false
  }
}

function artifactSummary(item: AgentArtifact) {
  const payload = parseMaybeJson<Record<string, unknown>>(item.payloadJson, {})
  const summary = payload.summary || payload.content || payload.answer || item.requestSummary || item.safetySummary
  return compact(summary, 140)
}

onMounted(load)
</script>

<template>
  <div class="page-grid">
    <SectionPanel class="span-12" title="后端代理接口调试台" subtitle="所有工具均调用 Java 后端 /api 代理接口，前端不直接访问 Python Agent">
      <template #actions>
        <button class="ghost-button" @click="load"><RefreshCw :size="17" />刷新状态</button>
      </template>
      <ErrorNotice :message="error" />
      <LoadingBlock :show="loading" />
      <div class="demo-context">
        <div>
          <strong>后端状态</strong>
          <span>{{ app.backendOnline ? 'Spring Boot 在线' : app.checking ? '检测中' : 'Spring Boot 离线' }}</span>
          <small>{{ app.healthError || '接口调用会通过 VITE_API_BASE_URL 指向的 Java 后端代理。' }}</small>
        </div>
        <div>
          <strong>当前上下文</strong>
          <span>{{ context.studentName }} / {{ context.courseTitle }}</span>
          <small>没有真实数据时使用 demo id 填充示例请求体，方便现场展示字段结构。</small>
        </div>
      </div>
      <div v-if="backendOffline" class="notice warn-notice">
        <span>后端离线时工具列表仍保留；调用按钮会被禁用。请启动 Spring Boot 后端后刷新状态。</span>
      </div>
    </SectionPanel>

    <SectionPanel class="span-4" title="智能体工具箱" subtitle="真实后端代理接口">
      <div class="agent-tool-grid">
        <button
          v-for="tool in tools"
          :key="tool.key"
          class="agent-tool-card"
          :style="{ borderColor: tool.key === selectedToolKey ? '#2f6fef' : undefined }"
          @click="selectedToolKey = tool.key"
        >
          <div class="section-head">
            <strong>{{ tool.title }}</strong>
            <StatusPill :status="tool.category" tone="info" />
          </div>
          <p>{{ tool.description }}</p>
          <small>{{ tool.endpoint }}</small>
        </button>
      </div>
    </SectionPanel>

    <SectionPanel class="span-8" :title="selectedTool.title" :subtitle="`${selectedTool.endpoint} -> ${selectedTool.proxyTarget}`">
      <template #actions>
        <button class="ghost-button" @click="resetPayload"><RefreshCw :size="16" />恢复示例</button>
        <button class="ghost-button" :disabled="!!payloadParseError" @click="formatPayload"><Wand2 :size="16" />格式化</button>
        <button class="button" :disabled="!canInvoke" @click="invokeTool"><Play :size="17" />调用代理</button>
      </template>
      <div class="field">
        <label>请求 JSON</label>
        <textarea v-model="payloadText" class="code-area" spellcheck="false" />
        <small class="field-help">请求将提交给 Java 后端 {{ selectedTool.endpoint }}，由后端代理到 {{ selectedTool.proxyTarget }}。</small>
        <small v-if="payloadParseError" class="field-error">{{ payloadParseError }}</small>
        <small v-else-if="backendOffline" class="field-error">后端离线，暂不能提交。请启动 Spring Boot 后端。</small>
      </div>
      <LoadingBlock :show="invoking" text="智能体代理正在处理" />
    </SectionPanel>

    <SectionPanel class="span-7" title="响应展示">
      <template #actions>
        <button class="ghost-button" :disabled="!response" @click="downloadJson(`${safeFilePart(selectedTool.title)}.json`, response)">
          <Download :size="17" />响应 JSON
        </button>
      </template>
      <div v-if="!response" class="empty-guide">
        <strong>提交请求后展示结构化结果</strong>
        <span>响应会拆成摘要、引用、Markdown 内容和原始 JSON，便于比赛现场解释。</span>
      </div>
      <template v-else>
        <div class="response-summary">
          <div>
            <strong>Summary</strong>
            <p>{{ responseSummary }}</p>
          </div>
          <StatusPill status="代理返回成功" tone="ok" />
        </div>
        <div class="learning-chip-grid">
          <div>
            <strong>Citations</strong>
            <span v-for="item in citations" :key="item">{{ item }}</span>
            <small v-if="!citations.length">响应中暂无 citations 字段</small>
          </div>
          <div>
            <strong>Trace</strong>
            <span>{{ response.traceId || response.requestId || '暂无 traceId' }}</span>
            <small>{{ selectedTool.proxyTarget }}</small>
          </div>
        </div>
        <MarkdownView v-if="markdownCandidate" :content="markdownCandidate" />
        <JsonBlock :value="response" />
      </template>
    </SectionPanel>

    <SectionPanel class="span-5" title="后端智能体定义与产物">
      <p><strong>{{ definitions.length }}</strong> 个后端智能体定义，<strong>{{ artifacts.length }}</strong> 条近期产物。</p>
      <div v-if="!definitions.length && !artifacts.length" class="empty-guide">
        <strong>暂无后端定义或产物</strong>
        <span>后端离线或尚未调用代理接口时这里为空，不影响工具列表展示。</span>
      </div>
      <div v-else class="timeline">
        <div v-for="definition in definitions.slice(0, 4)" :key="definition.id" class="timeline-body">
          <div class="section-head">
            <strong>{{ definition.displayName }}</strong>
            <StatusPill :status="definition.agentKey" tone="info" />
          </div>
          <p>{{ compact(definition.responsibility || definition.outputContract, 120) }}</p>
        </div>
        <div v-for="item in artifacts.slice(0, 6)" :key="item.id" class="timeline-body">
          <div class="section-head">
            <strong>{{ item.artifactType }}</strong>
            <StatusPill :status="item.status" :tone="item.status === 'SUCCEEDED' ? 'ok' : item.status === 'FAILED' ? 'danger' : 'warn'" />
          </div>
          <p>{{ artifactSummary(item) }}</p>
          <small>{{ item.agentEndpoint }} / {{ formatDate(item.createdAt) }}</small>
        </div>
      </div>
    </SectionPanel>
  </div>
</template>
