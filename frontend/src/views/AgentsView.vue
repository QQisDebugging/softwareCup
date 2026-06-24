<script setup lang="ts">
import { Download, Play, RefreshCw } from 'lucide-vue-next'
import { computed, onMounted, ref, watch } from 'vue'
import { agentsApi, coursesApi, profilesApi } from '@/api'
import ErrorNotice from '@/components/ErrorNotice.vue'
import LoadingBlock from '@/components/LoadingBlock.vue'
import MarkdownView from '@/components/MarkdownView.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import StatusPill from '@/components/StatusPill.vue'
import { useAppStore } from '@/stores/app'
import type { AgentArtifact, AgentTool, Course, ProfileResponse } from '@/types/api'
import { downloadJson, safeFilePart } from '@/utils/download'
import { cleanDisplayText, compact, formatDate, isRecord, parseMaybeJson, safeStringify } from '@/utils/format'

const app = useAppStore()
const loading = ref(false)
const invoking = ref(false)
const error = ref('')
const artifacts = ref<AgentArtifact[]>([])
const profiles = ref<ProfileResponse[]>([])
const courses = ref<Course[]>([])
const selectedToolKey = ref('path')
const selectedCourseId = ref('')
const selectedProfileId = ref('')
const payloadText = ref('')
const response = ref<Record<string, unknown> | null>(null)

const serviceUnavailable = computed(() => Boolean(app.healthError && !app.backendOnline))
const selectedCourse = computed(() => courses.value.find((item) => item.id === selectedCourseId.value) || courses.value[0])
const selectedProfile = computed(() => profiles.value.find((item) => item.id === selectedProfileId.value) || profiles.value[0])
const selectedCourseDescription = computed(() => cleanDisplayText(selectedCourse.value?.description || '选择课程后，可围绕该课程生成路径、资源、测评和教师分析。'))
const courseSwitchCards = computed(() =>
  courses.value.map((course) => ({
    ...course,
    active: course.id === selectedCourse.value?.id,
    descriptionText: cleanDisplayText(course.description),
  })),
)
const profileSwitchCards = computed(() =>
  profiles.value.map((profile) => ({
    ...profile,
    active: profile.id === selectedProfileId.value,
    summaryText: cleanDisplayText(profile.dialogueSummary),
  })),
)
const agentRunQueue = computed(() => [
  {
    label: '任务',
    title: selectedTool.value.title,
    detail: selectedTool.value.description,
    tone: 'info' as const,
  },
  {
    label: '上下文',
    title: `${context.value.studentName} / ${context.value.courseTitle}`,
    detail: selectedProfile.value?.dialogueSummary || '学生画像会影响路径、资源难度和复核重点。',
    tone: selectedProfile.value && selectedCourse.value ? 'ok' as const : 'warn' as const,
  },
  {
    label: '当前状态',
    title: invoking.value ? '正在处理' : response.value ? '结果待复核' : '等待提交',
    detail: response.value ? responseSummary.value || '已形成可复核结果。' : '提交后会生成摘要、引用、正文和审核信息。',
    tone: invoking.value ? 'warn' as const : response.value ? 'ok' as const : 'muted' as const,
  },
])

const payloadParseError = computed(() => {
  try {
    JSON.parse(payloadText.value || '{}')
    return ''
  } catch (err) {
    return err instanceof Error ? `任务细节暂时无法保存：${err.message}` : '任务细节暂时无法保存，请检查后再运行。'
  }
})

const payloadObject = computed<Record<string, unknown>>(() => {
  try {
    const parsed = JSON.parse(payloadText.value || '{}')
    return isRecord(parsed) ? parsed : {}
  } catch {
    return {}
  }
})

function payloadTextValue(value: unknown): string {
  if (Array.isArray(value)) return value.map((item) => payloadTextValue(item)).filter(Boolean).join('、')
  if (isRecord(value)) {
    const label = value.title || value.topic || value.knowledgePoint || value.path || value.studentName || value.riskReason
    return cleanDisplayText(String(label || safeStringify(value)))
  }
  if (value === null || value === undefined) return ''
  return cleanDisplayText(String(value))
}

function firstPayloadValue(keys: string[]) {
  const payload = payloadObject.value
  for (const key of keys) {
    const value = payload[key]
    const text = payloadTextValue(value)
    if (text) return text
  }
  return ''
}

const payloadBriefCards = computed(() => [
  {
    label: '学习对象',
    value: firstPayloadValue(['studentName', 'studentProfileSummary', 'studentProfileId']) || context.value.studentName,
    detail: selectedProfile.value?.major || '画像驱动个性化策略',
  },
  {
    label: '课程上下文',
    value: firstPayloadValue(['courseTitle', 'courseId']) || context.value.courseTitle,
    detail: selectedCourse.value?.department || '课程知识库与资源空间',
  },
  {
    label: '任务主题',
    value: firstPayloadValue(['topic', 'targetTopic', 'projectTitle', 'scenarioTitle', 'taskName']) || selectedTool.value.title,
    detail: selectedTool.value.category,
  },
  {
    label: '交付目标',
    value: firstPayloadValue(['targetOutcome', 'prompt', 'reviewFocus', 'auditFocus', 'preferredModalities', 'modality']) || selectedTool.value.description,
    detail: '提交后可复核、可编辑、可发布',
  },
])

const payloadKeyLabels: Record<string, string> = {
  topic: '主题',
  targetTopic: '目标主题',
  projectTitle: '项目主题',
  scenarioTitle: '场景',
  taskName: '任务',
  timeframeDays: '学习周期',
  dailyMinutes: '每日时长',
  targetOutcome: '达成目标',
  prompt: '练习要求',
  reviewFocus: '复核重点',
  auditFocus: '审核重点',
  preferredModalities: '资源形态',
  modality: '呈现形态',
  weaknessSignals: '薄弱信号',
  recentWeaknesses: '近期薄弱点',
  resourceCoverage: '资源覆盖',
  classSize: '班级人数',
  language: '编程语言',
  difficulty: '难度',
  constraints: '约束',
  citations: '引用',
  content: '内容',
  submission: '提交内容',
  rubric: '评分标准',
}

function payloadKeyLabel(key: string) {
  return payloadKeyLabels[key] || key.replace(/([a-z])([A-Z])/g, '$1 $2').replace(/_/g, ' ')
}

const payloadParameterChips = computed(() =>
  Object.entries(payloadObject.value)
    .filter(([key]) => !['studentProfileId', 'courseId', 'studentName', 'studentProfileSummary', 'courseTitle'].includes(key))
    .slice(0, 10)
    .map(([key, value]) => ({
      key: payloadKeyLabel(key),
      value: compact(payloadTextValue(value), 72),
    }))
    .filter((item) => item.value),
)
const editablePayloadFields = computed(() =>
  Object.entries(payloadObject.value)
    .filter(([key]) => !['studentProfileId', 'courseId', 'studentName', 'studentProfileSummary', 'courseTitle'].includes(key))
    .slice(0, 8)
    .map(([key, value]) => {
      const text = payloadTextValue(value)
      return {
        key,
        label: payloadKeyLabel(key),
        value: text,
        multiline:
          ['prompt', 'content', 'submission', 'constraints', 'reviewFocus', 'auditFocus', 'targetOutcome'].includes(key) ||
          text.length > 72,
      }
    }),
)

function profileText(profile?: ProfileResponse) {
  if (!profile) return ''
  return [profile.major, profile.currentLevel, profile.learningGoal, profile.preferences, profile.constraintsText, profile.dialogueSummary].join('\n')
}

function inferProfileFocus(profile?: ProfileResponse) {
  const text = profileText(profile)
  if (text.includes('数据') || text.includes('公式') || text.includes('图表')) return '公式组合与图表解读'
  if (text.includes('通识') || text.includes('信息安全') || text.includes('数字素养')) return '计算机基础与信息安全场景判断'
  if (text.includes('项目制') || text.includes('任务拆解') || text.includes('成果复盘') || text.includes('资料引用')) return '项目任务拆解与成果复盘'
  return '当前章节核心知识点'
}

function inferDailyMinutes(profile?: ProfileResponse) {
  const text = profileText(profile)
  if (text.includes('20 分钟')) return 20
  if (text.includes('30 分钟')) return 30
  if (text.includes('60 分钟')) return 60
  return 45
}

function inferWeaknessSignals(profile?: ProfileResponse) {
  const text = profileText(profile)
  if (text.includes('公式') || text.includes('图表')) return ['公式组合', '图表选择', '结论表达']
  if (text.includes('信息安全') || text.includes('通识')) return ['概念边界', '场景判断', '安全注意事项']
  if (text.includes('项目制') || text.includes('任务拆解') || text.includes('成果复盘') || text.includes('资料引用')) {
    return ['任务拆解', '资料引用', '成果复盘']
  }
  return ['概念关系不清', '步骤迁移困难', '综合应用表达薄弱']
}

function inferPreferredModalities(profile?: ProfileResponse) {
  const text = profileText(profile)
  if (text.includes('录屏') || text.includes('步骤')) return ['步骤清单', '操作脚本', '短练习']
  if (text.includes('卡片') || text.includes('生活化')) return ['概念卡片', '生活化案例', '低门槛小测']
  if (text.includes('看板') || text.includes('教师反馈')) return ['任务看板', '案例拆解', '阶段检查']
  return ['图解', '例题讲解', '小测']
}

function inferTargetOutcome(profile?: ProfileResponse) {
  const text = profileText(profile)
  if (text.includes('数据') || text.includes('公式')) return '能够完成数据清洗、公式计算、图表表达和结论说明。'
  if (text.includes('通识') || text.includes('信息安全')) return '能够解释基础概念、判断典型场景，并完成低门槛小测。'
  if (text.includes('项目制') || text.includes('任务拆解') || text.includes('成果复盘') || text.includes('资料引用')) return '能够拆解项目任务、引用资料依据，并提交成果复盘。'
  return '能够理解当前知识点、完成配套练习，并在综合任务中正确应用。'
}

const adaptiveContext = computed(() => {
  const profile = selectedProfile.value
  return {
    topic: inferProfileFocus(profile),
    dailyMinutes: inferDailyMinutes(profile),
    weaknessSignals: inferWeaknessSignals(profile),
    preferredModalities: inferPreferredModalities(profile),
    targetOutcome: inferTargetOutcome(profile),
  }
})

const context = computed(() => {
  const profile = selectedProfile.value
  const course = selectedCourse.value
  return {
    studentProfileId: profile?.id || 'initial-profile-id',
    courseId: course?.id || 'initial-course-id',
    studentName: profile?.studentName || '当前学生',
    courseTitle: course?.title || '当前课程',
    studentProfileSummary: profile?.dialogueSummary || '画像待同步：系统会结合对话、测评和学习事件识别基础、偏好、目标与短板。',
    learningGoal: profile?.learningGoal || '完成当前课程的阶段学习目标，并形成可追踪的资源学习与测评闭环。',
    currentLevel: profile?.currentLevel || '基础水平待由对话、测评和学习事件确认。',
    topic: adaptiveContext.value.topic,
    dailyMinutes: adaptiveContext.value.dailyMinutes,
    weaknessSignals: adaptiveContext.value.weaknessSignals,
    preferredModalities: adaptiveContext.value.preferredModalities,
    targetOutcome: adaptiveContext.value.targetOutcome,
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
      dailyMinutes: context.value.dailyMinutes,
      targetOutcome: context.value.targetOutcome,
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
      topic: context.value.topic,
      weaknessSignals: context.value.weaknessSignals,
      targetLevel: context.value.currentLevel,
    },
  },
  {
    key: 'audit',
    title: '内容安全检查',
    endpoint: '/learning/content-audits',
    proxyTarget: '/agents/safety/audit',
    category: '安全',
    description: '检查内容准确性、引用覆盖、风险表述和人工复核点。',
    samplePayload: {
      courseTitle: context.value.courseTitle,
      topic: context.value.topic,
      content: '只要记住结论就能完成所有相关题目，不需要理解推导过程。',
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
      recentWeaknesses: context.value.weaknessSignals,
      resourceCoverage: ['讲义', '小测', '案例任务'],
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
      topic: context.value.topic,
      language: '课程指定语言',
      difficulty: '入门到进阶',
      constraints: ['贴合当前课程材料', '包含可评分测试点', '给出分层提示与参考答案'],
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
      topic: context.value.topic,
      language: '课程指定语言',
      prompt: '完成当前知识点对应的练习任务，并说明关键步骤。',
      submission: '{{学生提交内容}}',
      rubric: ['概念准确', '步骤完整', '迁移应用', '表达清晰'],
    },
  },
  {
    key: 'storyboard',
    title: '多模态分镜',
    endpoint: '/learning/storyboards',
    proxyTarget: '/agents/multimodal/storyboard',
    category: '多模态',
    description: '生成短视频、图解或课堂讲解的分镜脚本。',
    samplePayload: {
      studentProfileId: context.value.studentProfileId,
      courseId: context.value.courseId,
      topic: context.value.topic,
      modality: '短视频+图解脚本',
      targetDurationMinutes: 5,
      visualStyle: '先概念关系，再例题拆解，再练习反馈',
    },
  },
  {
    key: 'prereq',
    title: '先修诊断',
    endpoint: '/learning/prerequisites/diagnose',
    proxyTarget: '/agents/prerequisite/diagnose',
    category: '诊断',
    description: '判断学习目标前的基础掌握缺口和热身任务。',
    samplePayload: {
      studentProfileId: context.value.studentProfileId,
      courseId: context.value.courseId,
      targetTopic: context.value.topic,
      completedTopics: ['课程导入', '前置概念自测'],
      assessmentWeaknesses: ['概念关系不清', '步骤迁移不稳定'],
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
      weaknesses: context.value.weaknessSignals,
      preferredModalities: context.value.preferredModalities,
      timeBudgetMinutes: context.value.dailyMinutes * 4,
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
      completedResources: ['完成知识点图解', '完成章节小测'],
      assessmentSummaries: ['入口测评 58/100', '复测 72/100'],
      tutorNotes: ['仍需强化概念迁移与综合表达'],
    },
  },
  {
    key: 'trace',
    title: '处理追踪',
    endpoint: '/learning/agent-traces',
    proxyTarget: '/agents/trace/explain',
    category: '可解释',
    description: '解释自动处理过程、输入输出和证据链。',
    samplePayload: {
      taskName: '个性化资源生成',
      userIntent: '生成当前知识点的个性化学习资源',
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
      declaredMajor: selectedProfile.value?.major || '课程方向待填写',
      currentLevel: context.value.currentLevel,
      learningGoal: context.value.learningGoal,
      dialogueTurns: ['我对这个知识点的前后关系不太清楚。', '我更喜欢先看结构图，再做练习或案例任务。'],
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
      learningEvents: ['完成 2 个资源卡', `错题复盘：${context.value.weaknessSignals[0] || '核心概念'}仍需巩固`, '观看知识点图解 6 分钟'],
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
      topic: context.value.topic,
      attempts: [
        {
          questionId: 'q1',
          knowledgePoint: context.value.topic,
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
      projectTitle: '当前知识点综合任务',
      files: [
        {
          path: '{{学生提交文件}}',
          language: '课程指定语言',
          content: '{{学生提交内容}}',
        },
      ],
      reviewFocus: ['conceptAccuracy', 'stepCompleteness', 'evidenceUse', 'testability'],
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
        { knowledgePoint: '核心概念辨析', masteryScore: 62 },
        { knowledgePoint: '综合应用表达', masteryScore: 54 },
      ],
      riskStudents: [{ studentName: context.value.studentName, riskReason: '测评低分且学习时长不足' }],
    },
  },
  {
    key: 'teaching-scenario',
    title: '教学方案编排',
    endpoint: '/teaching/scenario-plans',
    proxyTarget: '/agents/teaching/scenario-plan',
    category: '教学运营',
    description: '根据课程目标、学生画像和课堂时间生成课堂安排、证据点和备用路径。',
    samplePayload: {
      scenarioTitle: '当前课程个性化学习周计划',
      courseTitle: context.value.courseTitle,
      studentProfileSummary: context.value.studentProfileSummary,
      timeLimitMinutes: 8,
      audience: '课程教师',
      coreEndpoints: ['/api/profiles/dialogue', '/api/tasks/resource-generation', '/api/learning/path-plans'],
      availableArtifacts: ['8 维学习画像', '7 类课程资源', '内容安全审核记录'],
      riskConcerns: ['生成结果证据不足', '学生数据缺失', '发布前未完成教师复核'],
    },
  },
])

const toolByKey = computed(() => Object.fromEntries(tools.value.map((tool) => [tool.key, tool])))
const orchestrationStages = computed(() =>
  [
    {
      title: '画像与证据采集',
      desc: '从对话、学习事件和测评记录中更新不少于 6 维学习画像。',
      toolKeys: ['profile-infer', 'events', 'prereq'],
    },
    {
      title: '路径与资源规划',
      desc: '把课程目标、薄弱点和时间预算转成个性化学习顺序。',
      toolKeys: ['path', 'curate', 'graph'],
    },
    {
      title: '多模态资源生产',
      desc: '生成讲解文档、思维导图、练习、视频脚本、代码实操和课件材料。',
      toolKeys: ['storyboard', 'code-generate', 'project-review'],
    },
    {
      title: '测评批改闭环',
      desc: '自动生成测评、批改答案、分析题目质量并回写掌握度。',
      toolKeys: ['code-grade', 'item-analysis'],
    },
    {
      title: '教师教学运营',
      desc: '服务课程诊断、班级学情、干预分组和课堂方案编排。',
      toolKeys: ['course-diagnosis', 'class-analytics', 'teaching-scenario'],
    },
    {
      title: '审核与可解释报告',
      desc: '进行事实核验与内容安全检查，输出学习档案和处理追踪证据。',
      toolKeys: ['audit', 'portfolio', 'trace'],
    },
  ].map((stage) => ({
    ...stage,
    tools: stage.toolKeys.map((key) => toolByKey.value[key]).filter((tool): tool is AgentTool => Boolean(tool)),
  })),
)
const selectedTool = computed(() => tools.value.find((item) => item.key === selectedToolKey.value) || tools.value[0])
const selectedStage = computed(() =>
  orchestrationStages.value.find((stage) => stage.tools.some((tool) => tool.key === selectedToolKey.value)),
)
const canInvoke = computed(() => !invoking.value && !payloadParseError.value && !serviceUnavailable.value)

const responseSummary = computed(() => {
  const value = response.value
  if (!value) return ''
  const direct = value.summary || value.title || value.feedback || value.safetySummary
  if (typeof direct === 'string') return direct
  const content = markdownCandidate.value
  return content ? compact(content, 240) : '已形成结构化结果，可查看处理证据。'
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

const responseHighlights = computed(() => {
  const value = response.value
  if (!value) return []
  const groups = [
    {
      label: '交付内容',
      values: stringList(
        value.recommendedResources ||
          value.resources ||
          value.items ||
          value.plan ||
          value.learningActions ||
          value.actions ||
          value.tasks,
      ),
    },
    {
      label: '风险与审核',
      values: stringList(
        value.safetyFindings ||
          value.risks ||
          value.blockingIssues ||
          value.reviewFindings ||
          value.weaknessSignals ||
          value.gaps,
      ),
    },
    {
      label: '下一步',
      values: stringList(value.nextActions || value.followUpQuestions || value.followUps || value.recommendations),
    },
  ]
  return groups
    .map((group) => ({ ...group, values: group.values.slice(0, 4) }))
    .filter((group) => group.values.length)
})

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
  const [profileResult, courseResult] = await Promise.allSettled([
    profilesApi.list(),
    coursesApi.list(),
  ])
  profiles.value = profileResult.status === 'fulfilled' ? profileResult.value : []
  courses.value = courseResult.status === 'fulfilled' ? courseResult.value : []
  const preferredCourse = courses.value.find((course) => course.id === app.activeCourseId) || courses.value[0]
  selectedCourseId.value ||= preferredCourse?.id || ''
  selectedProfileId.value ||= profiles.value[0]?.id || ''
  if (selectedCourseId.value) {
    app.setActiveCourse(selectedCourseId.value)
  }
  await loadArtifacts()
  const failures = [profileResult, courseResult].filter((item) => item.status === 'rejected').length
  if (failures) error.value = `有 ${failures} 项基础数据暂未同步，备课事项仍可查看。`
  loading.value = false
}

async function loadArtifacts() {
  if (!selectedProfileId.value && !selectedCourseId.value) {
    artifacts.value = []
    return
  }
  try {
    artifacts.value = await agentsApi.artifacts({ studentProfileId: selectedProfileId.value || undefined, courseId: selectedCourseId.value || undefined })
  } catch {
    artifacts.value = []
  }
}

function resetPayload() {
  payloadText.value = safeStringify(selectedTool.value.samplePayload)
  error.value = ''
}

function updatePayloadField(key: string, rawValue: string) {
  const current = { ...payloadObject.value }
  const previous = current[key]
  if (Array.isArray(previous)) {
    current[key] = rawValue
      .split(/[、,，\n]/)
      .map((item) => item.trim())
      .filter(Boolean)
  } else if (typeof previous === 'number') {
    const parsed = Number(rawValue)
    current[key] = Number.isFinite(parsed) ? parsed : previous
  } else {
    current[key] = rawValue
  }
  payloadText.value = safeStringify(current)
  error.value = ''
}

async function invokeTool() {
  if (serviceUnavailable.value) {
    error.value = '学习服务暂不可用：请启动学习服务后再运行任务。'
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
    await loadArtifacts()
  } catch (err) {
    response.value = null
    error.value = err instanceof Error ? err.message : '任务处理失败'
  } finally {
    invoking.value = false
  }
}

function artifactSummary(item: AgentArtifact) {
  const payload = parseMaybeJson<Record<string, unknown>>(item.payloadJson, {})
  const summary = payload.summary || payload.content || payload.answer || item.requestSummary || item.safetySummary
  return compact(summary, 140)
}

const artifactTypeLabels: Record<string, string> = {
  PROFILE: '学习画像',
  KNOWLEDGE_GRAPH: '知识图谱',
  PATH_PLAN: '学习路径',
  RESOURCE: '学习资源',
  AUDIT: '内容审核',
  TUTORING: '答疑记录',
  EVALUATION: '学习评估',
}

const artifactStatusLabels: Record<string, string> = {
  SUCCEEDED: '已完成',
  FAILED: '需处理',
  PENDING: '处理中',
  RUNNING: '处理中',
}

const endpointLabels: Record<string, string> = {
  '/agents/path/plan': '路径规划处理',
  '/agents/knowledge/graph': '知识图谱处理',
  '/agents/safety/audit': '内容审核处理',
  '/agents/course/diagnose': '课程诊断处理',
  '/agents/code/practice/generate': '代码练习生成处理',
  '/agents/code/practice/grade': '代码练习批改处理',
  '/agents/tutor/answer': '智能答疑处理',
  '/agents/learning/evaluate': '学习评估处理',
  '/agents/teaching/orchestrate': '教学编排处理',
}

function displayArtifactType(value?: string) {
  if (!value) return '处理记录'
  return artifactTypeLabels[value] || cleanDisplayText(value).replace(/_/g, ' ')
}

function displayArtifactStatus(value?: string) {
  if (!value) return '处理中'
  return artifactStatusLabels[value] || cleanDisplayText(value)
}

function displayEndpoint(value?: string) {
  if (!value) return '处理记录'
  return endpointLabels[value] || '处理记录'
}

function switchCourse(courseId: string) {
  if (!courseId || courseId === selectedCourseId.value) return
  selectedCourseId.value = courseId
}

watch(selectedCourseId, (courseId, previousCourseId) => {
  if (courseId) app.setActiveCourse(courseId)
  if (previousCourseId && courseId !== previousCourseId) {
    response.value = null
    resetPayload()
    void loadArtifacts()
  }
})

watch(selectedProfileId, (profileId, previousProfileId) => {
  if (previousProfileId && profileId !== previousProfileId) {
    response.value = null
    resetPayload()
    void loadArtifacts()
  }
})

watch(
  () => app.activeCourseId,
  (courseId) => {
    if (courseId && courses.value.some((course) => course.id === courseId)) selectedCourseId.value = courseId
  },
)

onMounted(load)
</script>

<template>
  <div class="page-grid">
    <section class="dashboard-workbench agents-workbench span-12">
      <div class="dashboard-workbench-head">
        <div>
          <h2>智能体协同</h2>
        </div>
        <div class="home-action-row">
          <button class="button" :disabled="!canInvoke" @click="invokeTool"><Play :size="17" />运行任务</button>
          <button class="ghost-button" @click="load"><RefreshCw :size="17" />刷新</button>
          <button class="ghost-button" :disabled="!response" @click="downloadJson(`${safeFilePart(selectedTool.title)}.json`, response)">
            <Download :size="17" />导出结果
          </button>
        </div>
      </div>

      <ErrorNotice :message="error" />
      <LoadingBlock :show="loading" />
      <div class="agent-sample-lane" aria-label="学习画像样例切换">
        <button
          v-for="profile in profileSwitchCards"
          :key="profile.id"
          type="button"
          :class="{ active: profile.active }"
          @click="selectedProfileId = profile.id"
        >
          <span>{{ profile.major }}</span>
          <strong>{{ profile.studentName }}</strong>
        </button>
      </div>
      <div class="course-card-switcher" aria-label="备课任务课程切换">
        <button
          v-for="course in courseSwitchCards"
          :key="course.id"
          type="button"
          :class="{ active: course.active }"
          @click="switchCourse(course.id)"
        >
          <span>{{ course.department }}</span>
          <strong>{{ course.title }}</strong>
          <small>{{ course.creditHours }} 学时 · {{ course.active ? '当前课程' : '切换课程' }}</small>
        </button>
      </div>

      <div class="agent-command-surface">
        <label>
          <strong>学习画像</strong>
          <select v-model="selectedProfileId">
            <option value="">选择画像</option>
            <option v-for="profile in profiles" :key="profile.id" :value="profile.id">{{ profile.studentName }} · {{ profile.major }}</option>
          </select>
        </label>
        <div>
          <strong>当前任务对象</strong>
          <span>{{ context.studentName }} / {{ context.courseTitle }}</span>
        </div>
        <div>
          <strong>发布规则</strong>
          <span>生成、审核、发布分离</span>
        </div>
        <div>
          <strong>输出去向</strong>
          <span>进入课程空间或学习记录</span>
        </div>
      </div>
      <div class="agent-run-queue">
        <div v-for="item in agentRunQueue" :key="item.label">
          <StatusPill :status="item.label" :tone="item.tone" />
          <strong>{{ item.title }}</strong>
          <small>{{ item.detail }}</small>
        </div>
      </div>
      <div v-if="serviceUnavailable" class="notice warn-notice">
        <span>学习服务暂不可用，任务暂不能提交。请启动学习服务后刷新状态。</span>
      </div>
    </section>

    <SectionPanel class="span-12 agent-orchestration-panel" title="智能体生产线">
      <div class="orchestration-board">
        <article
          v-for="(stage, index) in orchestrationStages"
          :key="stage.title"
          class="orchestration-card"
          :class="{ active: selectedStage?.title === stage.title }"
        >
          <span class="agent-flow-index">{{ index + 1 }}</span>
          <strong>{{ stage.title }}</strong>
          <div class="orchestration-tool-list">
            <button
              v-for="tool in stage.tools"
              :key="tool.key"
              type="button"
              :class="{ active: tool.key === selectedToolKey }"
              @click="selectedToolKey = tool.key"
            >
              {{ tool.title }}
            </button>
          </div>
        </article>
      </div>
    </SectionPanel>

    <SectionPanel class="span-4 agent-directory-panel" title="备课事项">
      <div class="agent-directory-summary">
        <span>当前任务</span>
        <strong>{{ selectedStage?.title || '课程任务' }}</strong>
        <small>{{ selectedTool.title }} · {{ selectedTool.category }}</small>
      </div>
      <div class="agent-tool-grid">
        <button
          v-for="tool in tools"
          :key="tool.key"
          class="agent-tool-card"
          :class="{ active: tool.key === selectedToolKey }"
          @click="selectedToolKey = tool.key"
        >
          <div class="agent-tool-title">
            <strong>{{ tool.title }}</strong>
            <StatusPill :status="tool.category" tone="info" />
          </div>
        </button>
      </div>
    </SectionPanel>

    <SectionPanel class="span-8 agent-composer-panel" :title="selectedTool.title">
      <template #actions>
        <button class="ghost-button" @click="resetPayload"><RefreshCw :size="16" />恢复模板</button>
        <button class="button" :disabled="!canInvoke" @click="invokeTool"><Play :size="17" />运行任务</button>
      </template>
      <div class="agent-composer">
        <div class="agent-composer-grid">
          <article v-for="item in payloadBriefCards" :key="item.label">
            <span>{{ item.label }}</span>
            <strong>{{ compact(item.value, 84) }}</strong>
            <small>{{ item.detail }}</small>
          </article>
        </div>
        <div class="agent-parameter-strip" aria-label="任务参数摘要">
          <span v-for="item in payloadParameterChips" :key="item.key">
            <strong>{{ item.key }}</strong>
            {{ item.value }}
          </span>
        </div>
        <div class="agent-submit-note">
          <strong>提交后生成可复核结果</strong>
        </div>
        <div class="agent-task-editor">
          <div class="agent-task-editor-head">
            <strong>任务要求</strong>
          </div>
          <div class="agent-task-field-grid">
            <label v-for="field in editablePayloadFields" :key="field.key" :class="{ wide: field.multiline }">
              <span>{{ field.label }}</span>
              <textarea
                v-if="field.multiline"
                :value="field.value"
                rows="3"
                @input="updatePayloadField(field.key, ($event.target as HTMLTextAreaElement).value)"
              />
              <input
                v-else
                :value="field.value"
                @input="updatePayloadField(field.key, ($event.target as HTMLInputElement).value)"
              />
            </label>
          </div>
        </div>
        <small v-if="payloadParseError" class="field-error">{{ payloadParseError }}</small>
        <small v-else-if="serviceUnavailable" class="field-error">学习服务暂不可用，暂不能提交。请启动服务后刷新状态。</small>
      </div>
      <LoadingBlock :show="invoking" text="正在生成结果" />
    </SectionPanel>

    <SectionPanel class="span-7 agent-review-panel" title="结果复核">
      <template #actions>
        <button class="ghost-button" :disabled="!response" @click="downloadJson(`${safeFilePart(selectedTool.title)}.json`, response)">
          <Download :size="17" />导出结果
        </button>
      </template>
      <div v-if="!response" class="empty-guide">
        <strong>运行后查看复核结果</strong>
      </div>
      <template v-else>
        <div class="response-summary">
          <div>
            <strong>摘要</strong>
            <p>{{ responseSummary }}</p>
          </div>
          <StatusPill status="处理成功" tone="ok" />
        </div>
        <div class="learning-chip-grid">
          <div>
            <strong>引用证据</strong>
            <span v-for="item in citations" :key="item">{{ item }}</span>
            <small v-if="!citations.length">暂无引用证据</small>
          </div>
          <div>
            <strong>证据编号</strong>
            <span>{{ response.traceId || response.requestId || '等待证据编号' }}</span>
            <small>{{ displayEndpoint(selectedTool.proxyTarget) }}</small>
          </div>
        </div>
        <MarkdownView v-if="markdownCandidate" :content="markdownCandidate" />
        <div v-if="responseHighlights.length" class="agent-result-grid">
          <article v-for="group in responseHighlights" :key="group.label">
            <strong>{{ group.label }}</strong>
            <span v-for="item in group.values" :key="item">{{ item }}</span>
          </article>
        </div>
      </template>
    </SectionPanel>

    <SectionPanel class="span-5 agent-artifact-panel" title="最近产物">
      <p><strong>{{ artifacts.length }}</strong> 条近期产物，运行任务后会记录摘要、引用和复核信息。</p>
      <div v-if="!artifacts.length" class="empty-guide">
        <strong>暂无任务记录</strong>
      </div>
      <div v-else class="timeline">
        <div v-for="item in artifacts.slice(0, 6)" :key="item.id" class="timeline-body">
          <div class="section-head">
            <strong>{{ displayArtifactType(item.artifactType) }}</strong>
            <StatusPill :status="displayArtifactStatus(item.status)" :tone="item.status === 'SUCCEEDED' ? 'ok' : item.status === 'FAILED' ? 'danger' : 'warn'" />
          </div>
          <p>{{ artifactSummary(item) }}</p>
          <small>{{ displayEndpoint(item.agentEndpoint) }} / {{ formatDate(item.createdAt) }}</small>
        </div>
      </div>
    </SectionPanel>
  </div>
</template>
