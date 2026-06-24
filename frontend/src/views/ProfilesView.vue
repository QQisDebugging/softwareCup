<script setup lang="ts">
import {
  Activity,
  AlertTriangle,
  BookOpenCheck,
  CalendarCheck2,
  CheckCircle2,
  ClipboardList,
  Code2,
  FilePlus2,
  HelpCircle,
  Info,
  LineChart,
  MessageSquareText,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  Target,
  ThumbsUp,
  TrendingUp,
  Upload,
  UserRound,
  Users,
} from 'lucide-vue-next'
import type { Component } from 'vue'
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { agentsApi, coursesApi, learningApi, profilesApi } from '@/api'
import ErrorNotice from '@/components/ErrorNotice.vue'
import LoadingBlock from '@/components/LoadingBlock.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import StatusPill from '@/components/StatusPill.vue'
import { useAppStore } from '@/stores/app'
import { useResizablePanels } from '@/composables/useResizablePanels'
import type { Course, EvaluationReport, KnowledgeMastery, LearningEvent, ProfileDimension, ProfileHistory, ProfileResponse, QuizAttempt } from '@/types/api'
import { cleanDisplayText, formatDate } from '@/utils/format'

type Tone = 'ok' | 'warn' | 'danger' | 'info' | 'muted'
type EvidenceTab = '总览' | '知识掌握' | '学习习惯' | '教师证据'

interface ProfileMetric {
  label: string
  value: string
  detail: string
  progress?: number
  tone?: 'up'
  icon?: Component
}

interface RadarDimension {
  key: string
  label: string
  score: number
  delta: string
  icon: Component
  weak?: boolean
}

interface EvidenceItem {
  id: string
  time: string
  type: string
  title: string
  group: EvidenceTab
  course: string
  confidence: number
  status: string
  icon: Component
}

interface TeacherClassOption {
  id: string
  name: string
  shortName: string
  students: number
  masteryBias: number
  stabilityBias: number
  activeBias: number
  riskBias: number
  roster: string[]
}

interface TeacherCourseBlueprint {
  key: string
  label: string
  baseMastery: number
  baseStability: number
  baseActive: number
  weakPoints: string[]
  interventions: string[]
  riskReasons: string[]
  evidenceTopics: string[]
}

interface TeacherWeakKnowledgeRow {
  id: string
  point: string
  mastery: number
  students: number
  intervention: string
}

interface TeacherRiskStudentRow {
  id: string
  name: string
  reason: string
  evidence: string
  action: string
}

const app = useAppStore()
const router = useRouter()

// 画像三栏（能力罗盘 / 证据流 / 干预建议）列宽可拖拽并记忆
const {
  gridStyle: profileGridStyle,
  startResize: profileStartResize,
  resetLayout: profileResetLayout,
} = useResizablePanels({
  storageKey: 'profile-dashboard',
  defaultWeights: [0.82, 1.28, 0.72],
  minWidths: [320, 420, 300],
  spacing: 20,
})
const loading = ref(false)
const evidenceLoading = ref(false)
const error = ref('')
const profiles = ref<ProfileResponse[]>([])
const courses = ref<Course[]>([])
const dimensions = ref<ProfileDimension[]>([])
const profileHistory = ref<ProfileHistory[]>([])
const events = ref<LearningEvent[]>([])
const attempts = ref<QuizAttempt[]>([])
const mastery = ref<KnowledgeMastery[]>([])
const reports = ref<EvaluationReport[]>([])
const selectedProfileId = ref('')
const selectedCourseId = ref('')
const activeEvidenceTab = ref<EvidenceTab>('总览')
const evidenceTabs: EvidenceTab[] = ['总览', '知识掌握', '学习习惯', '教师证据']
const teacherClassId = ref('software-2024-01')
const teacherDateRange = ref('2024-05-10 ~ 2024-05-16')
const teacherProfileDimension = ref('综合画像')
const teacherExpandedEvidence = ref('')
const teacherRiskFocusId = ref('')
const teacherProfileNotice = ref('')
const profileAgentLoading = ref(false)
const teacherClassAnalyticsResult = ref<Record<string, unknown> | null>(null)

const isTeacher = computed(() => app.role === 'teacher')
const teacherClassOptionsRaw: TeacherClassOption[] = [
  {
    id: 'software-2024-01',
    name: '软件工程 2024-01（52人）',
    shortName: '软工 2024-01',
    students: 52,
    masteryBias: 4,
    stabilityBias: 3,
    activeBias: 2,
    riskBias: -1,
    roster: ['张同学', '李同学', '王同学', '陈同学', '赵同学', '刘同学', '孙同学', '周同学', '吴同学', '郑同学', '何同学', '高同学'],
  },
  {
    id: 'software-2024-02',
    name: '软件工程 2024-02（49人）',
    shortName: '软工 2024-02',
    students: 49,
    masteryBias: -3,
    stabilityBias: -1,
    activeBias: 4,
    riskBias: 2,
    roster: ['林同学', '黄同学', '罗同学', '梁同学', '许同学', '宋同学', '唐同学', '邓同学', '韩同学', '曹同学', '彭同学', '余同学'],
  },
  {
    id: 'cs-2024-01',
    name: '计科 2024-01（55人）',
    shortName: '计科 2024-01',
    students: 55,
    masteryBias: 1,
    stabilityBias: 5,
    activeBias: -2,
    riskBias: 1,
    roster: ['马同学', '冯同学', '朱同学', '秦同学', '董同学', '谢同学', '卢同学', '蒋同学', '蔡同学', '袁同学', '杜同学', '叶同学'],
  },
]

// 真实班级（来自后端课程聚合）。加载成功后用真实课程名/人数替换演示班级，使选择器对应真实课程。
const teacherRealClasses = ref<TeacherClassOption[]>([])
const teacherClassOptions = computed<TeacherClassOption[]>(() =>
  teacherRealClasses.value.length ? teacherRealClasses.value : teacherClassOptionsRaw,
)

async function loadTeacherClasses() {
  try {
    const classes = await coursesApi.teacherClasses()
    if (!classes.length) return
    teacherRealClasses.value = classes.map((cls, index) => {
      const blueprintBias = teacherClassOptionsRaw[index % teacherClassOptionsRaw.length]
      return {
        id: cls.courseId,
        name: `${cls.courseTitle}（${cls.studentCount}人）`,
        shortName: cls.courseTitle.length > 12 ? cls.courseTitle.slice(0, 12) : cls.courseTitle,
        students: cls.studentCount,
        masteryBias: blueprintBias.masteryBias,
        stabilityBias: blueprintBias.stabilityBias,
        activeBias: blueprintBias.activeBias,
        riskBias: blueprintBias.riskBias,
        roster: blueprintBias.roster,
      }
    })
    if (!teacherClassOptions.value.some((c) => c.id === teacherClassId.value)) {
      teacherClassId.value = teacherClassOptions.value[0]?.id || teacherClassId.value
    }
  } catch {
    // 后端不可用时保留演示班级
  }
}
const teacherDimensionOptions = ['综合画像', '知识掌握', '学习行为', '测评表现', '资源使用']
const teacherCourseBlueprints: TeacherCourseBlueprint[] = [
  {
    key: 'java-web',
    label: 'Java Web',
    baseMastery: 71,
    baseStability: 76,
    baseActive: 73,
    weakPoints: ['JSP 生命周期与内置对象', 'Servlet 请求与响应流程', '会话管理（Session/Cookie）', '数据库连接池配置', '过滤器与监听器', '事务管理与回滚机制', 'JDBC 批量操作与优化', '文件上传与下载'],
    interventions: ['强化讲解+随堂练习', '知识巩固+案例解析', '实验演练+对比分析', '实践指导+错题分析'],
    riskReasons: ['Servlet 流程题连续失分', 'JSP 实验提交滞后', '会话管理概念混淆', '项目代码运行失败'],
    evidenceTopics: ['过滤器在请求和响应时都会执行的原因', 'Session 和 Cookie 的区别', 'JDBC 连接池的配置作用', 'JSP 内置对象的使用边界'],
  },
  {
    key: 'ai-agent',
    label: 'AI 智能体',
    baseMastery: 68,
    baseStability: 72,
    baseActive: 79,
    weakPoints: ['画像诊断证据链', '资源生成任务拆解', '多智能体协同流程', '提示词约束与引用', '学习路径动态调整', '模型输出质检', '知识图谱结构化', '报告总结与疑惑归纳'],
    interventions: ['流程图复盘+案例补充', '任务拆解练习+同伴讲解', '引用依据检查+短测', '生成记录对比+教师点评'],
    riskReasons: ['画像证据引用不足', '资源生成流程说不清', '提示词约束遗漏', '答疑总结没有沉淀'],
    evidenceTopics: ['画像诊断如何进入资源生成流程', '多智能体之间如何传递上下文', '引用依据和附件上下文怎么组织', 'AI 输出如何做发布前质检'],
  },
  {
    key: 'project-practice',
    label: '工程项目实践',
    baseMastery: 70,
    baseStability: 69,
    baseActive: 76,
    weakPoints: ['需求拆解与范围控制', '接口契约设计', '项目里程碑推进', '测试用例覆盖', '异常处理与日志', '版本协作规范', '验收材料整理', '复盘改进表达'],
    interventions: ['项目案例复盘+清单检查', '接口样例讲解+代码评审', '里程碑督促+小组辅导', '测试任务拆分+错因记录'],
    riskReasons: ['项目任务拆解不完整', '接口设计和实现不一致', '测试证据提交不足', '小组协作记录缺失'],
    evidenceTopics: ['需求说明如何拆成可执行任务', '接口字段和异常返回如何约定', '项目里程碑延期该怎么处理', '验收材料需要哪些证据'],
  },
  {
    key: 'computer-foundation',
    label: '大学计算机基础',
    baseMastery: 74,
    baseStability: 80,
    baseActive: 70,
    weakPoints: ['表格公式组合', '数据清洗步骤', '图表类型选择', '文档排版规范', '演示文稿结构', '文件管理与压缩', '计算思维表达', '信息检索与引用'],
    interventions: ['操作演示+即时练习', '模板对照+错例讲解', '短任务训练+课堂巡检', '成果展示+同伴互评'],
    riskReasons: ['基础操作完成慢', '公式组合错误率高', '图表结论表达弱', '作业文件命名不规范'],
    evidenceTopics: ['公式嵌套为什么总是报错', '怎样选择合适的图表类型', '文档排版怎么满足课程要求', '如何整理课程作业文件'],
  },
  {
    key: 'generic',
    label: '通用课程',
    baseMastery: 69,
    baseStability: 73,
    baseActive: 71,
    weakPoints: ['核心概念关系', '关键步骤迁移', '典型例题应用', '学习资料整理', '错因复盘表达', '阶段测评订正', '任务计划执行', '总结报告结构'],
    interventions: ['概念图解+例题训练', '步骤拆解+短测反馈', '资料清单+学习计划', '复盘模板+教师点评'],
    riskReasons: ['核心概念掌握不稳', '测评订正不完整', '学习计划执行偏低', '答疑后没有复盘'],
    evidenceTopics: ['这个知识点和前后章节的关系', '应该先复习哪一部分', '错题该如何归纳', '下一步任务如何安排'],
  },
]
const selectedProfile = computed(() => profiles.value.find((item) => item.id === selectedProfileId.value) || profiles.value[0])
const selectedCourse = computed(() => courses.value.find((item) => item.id === selectedCourseId.value) || courses.value[0])
const visibleProfiles = computed(() => {
  if (isTeacher.value) return profiles.value
  const own = profiles.value.filter((item) => item.studentName === app.currentUser.name || item.id === selectedProfileId.value)
  return own.length ? own : profiles.value.slice(0, 1)
})
const riskProfiles = computed(() =>
  profiles.value.filter((profile) => {
    const text = `${profile.currentLevel} ${profile.learningGoal} ${profile.preferences} ${profile.constraintsText} ${profile.dialogueSummary}`
    return /薄弱|不足|风险|困难|欠缺|待提升|基础/.test(text)
  }),
)
const masteryAverage = computed(() => {
  const values = mastery.value.map((item) => Number(item.masteryScore)).filter((item) => Number.isFinite(item))
  if (!values.length) return 0
  return Math.round(values.reduce((sum, item) => sum + item, 0) / values.length)
})
const attemptAverage = computed(() => {
  const values = attempts.value.map((item) => (Number(item.score) / Math.max(Number(item.maxScore) || 100, 1)) * 100).filter(Number.isFinite)
  if (!values.length) return 0
  return Math.round(values.reduce((sum, item) => sum + item, 0) / values.length)
})
const confidenceScore = computed(() => Math.min(96, Math.max(52, Math.round((masteryAverage.value || 62) * 0.62 + Math.min(events.value.length, 20) * 1.2))))
const currentLevelText = computed(() => cleanDisplayText(selectedProfile.value?.currentLevel || '画像等级待同步'))
const profileSummary = computed(() => cleanDisplayText(selectedProfile.value?.dialogueSummary || '暂无画像摘要，刷新后会尝试读取学习事件、测评和报告数据。'))
const courseTitle = computed(() => selectedCourse.value?.title || '全部课程')
const teacherSelectedClass = computed(() => teacherClassOptions.value.find((item) => item.id === teacherClassId.value) || teacherClassOptions.value[0])
const teacherClassCourseContext = computed(() => {
  const classInfo = teacherSelectedClass.value
  const course = selectedCourse.value
  const blueprint = resolveTeacherCourseBlueprint(course)
  const seedText = `${classInfo.id}|${course?.id || course?.title || 'all-courses'}|${teacherDateRange.value}`
  const seed = stableHash(seedText)
  const mastery = clampNumber(blueprint.baseMastery + classInfo.masteryBias + seededRange(seed, 1, -5, 5), 48, 91)
  const stability = clampNumber(blueprint.baseStability + classInfo.stabilityBias + seededRange(seed, 2, -4, 4), 46, 94)
  const active = clampNumber(blueprint.baseActive + classInfo.activeBias + seededRange(seed, 3, -5, 5), 45, 96)
  const weakCount = clampNumber(Math.round((100 - mastery) * 0.52 + seededRange(seed, 4, -2, 4)), 6, 28)
  const riskCount = clampNumber(Math.round(classInfo.students * (0.08 + (100 - mastery) / 420)) + classInfo.riskBias + seededRange(seed, 5, -1, 2), 3, Math.min(16, classInfo.students))
  const classDelta = clampNumber(Math.round((mastery - 66) / 2 + seededRange(seed, 6, 1, 5)), 1, 12)
  const analytics = teacherClassAnalyticsResult.value
  const analyticsWeaknesses = stringArray(analytics?.topWeaknesses)
  const analyticsRiskProfiles = recordArray(analytics?.studentRiskProfiles)
  const analyticsMastery = agentNumber(analytics, 'classMasteryAverage', mastery, 0, 100)
  const analyticsEngagement = agentNumber(analytics, 'engagementAverage', active, 0, 100)
  return {
    key: seedText,
    seed,
    classInfo,
    course,
    blueprint,
    mastery: analyticsMastery,
    stability,
    active: analyticsEngagement,
    weakCount: analyticsWeaknesses.length || weakCount,
    riskCount: analyticsRiskProfiles.length || riskCount,
    classDelta,
    weakDelta: clampNumber(Math.round(weakCount / 5) + seededRange(seed, 7, 0, 2), 1, 8),
    riskDelta: clampNumber(Math.round(riskCount / 6) + seededRange(seed, 8, 0, 1), 1, 5),
  }
})
const teacherSummaryMetrics = computed(() => [
  { key: 'mastery', label: '综合掌握度', value: String(teacherClassCourseContext.value.mastery), unit: '%', delta: `${teacherClassCourseContext.value.classDelta}%`, icon: Target, tone: 'teal' },
  { key: 'stability', label: '学习稳定性', value: String(teacherClassCourseContext.value.stability), unit: '%', delta: `${clampNumber(Math.round((teacherClassCourseContext.value.stability - 68) / 3), 1, 9)}%`, icon: TrendingUp, tone: 'teal' },
  { key: 'weak', label: '薄弱知识点数量', value: String(teacherClassCourseContext.value.weakCount), unit: '个', delta: `${teacherClassCourseContext.value.weakDelta}个`, icon: BookOpenCheck, tone: 'orange' },
  { key: 'risk', label: '风险学生数量', value: String(teacherClassCourseContext.value.riskCount), unit: '人', delta: `${teacherClassCourseContext.value.riskDelta}人`, icon: AlertTriangle, tone: 'red' },
  { key: 'active', label: '活跃学生比例', value: String(teacherClassCourseContext.value.active), unit: '%', delta: `${clampNumber(Math.round((teacherClassCourseContext.value.active - 62) / 3), 1, 12)}%`, icon: Users, tone: 'blue' },
])
const teacherRadarAxes = computed(() => {
  const context = teacherClassCourseContext.value
  const seed = context.seed
  const blueprintShift = context.blueprint.key === 'computer-foundation' ? 3 : context.blueprint.key === 'project-practice' ? -1 : 0
  const values = [
    context.mastery + seededRange(seed, 11, -3, 4),
    context.mastery + blueprintShift + seededRange(seed, 12, -7, 5),
    context.stability - 9 + seededRange(seed, 13, -5, 5),
    Math.round((context.mastery + context.stability) / 2) + seededRange(seed, 14, -4, 4),
    context.active + seededRange(seed, 15, -3, 4),
    context.stability - 12 + seededRange(seed, 16, -4, 6),
  ]
  return ['知识基础', '实践能力', '表达能力', '问题解决', '学习投入', '反思复盘'].map((label, index) => {
    const classScore = clampNumber(values[index], 42, 94) / 100
    const schoolScore = clampNumber(values[index] - seededRange(seed, index + 21, 8, 16), 38, 82) / 100
    return { label, classScore, schoolScore }
  })
})
const teacherWeakKnowledgeRows = computed<TeacherWeakKnowledgeRow[]>(() => {
  const context = teacherClassCourseContext.value
  const analytics = teacherClassAnalyticsResult.value
  const topWeaknesses = stringArray(analytics?.topWeaknesses)
  const gaps = recordArray(analytics?.resourceGaps)
  const priority = stringArray(analytics?.interventionPriority)
  if (topWeaknesses.length || gaps.length) {
    const names = topWeaknesses.length ? topWeaknesses : gaps.map((item) => cleanDisplayText(item.knowledgePoint)).filter(Boolean)
    return names.slice(0, 8).map((point, index) => {
      const gap = gaps.find((item) => cleanDisplayText(item.knowledgePoint) === point) || gaps[index]
      return {
        id: `${context.classInfo.id}-agent-wk-${index + 1}`,
        point,
        mastery: clampNumber(context.mastery - 20 + index * 3, 28, 84),
        students: clampNumber(Number(gap?.affectedStudents || context.riskCount || 1), 1, context.classInfo.students),
        intervention: cleanDisplayText(gap?.suggestedAction || priority[index] || '按智能体建议生成补救资源'),
      }
    })
  }
  const baseMastery = clampNumber(context.mastery - 27, 35, 68)
  return context.blueprint.weakPoints.slice(0, 8).map((point, index) => ({
    id: `${context.classInfo.id}-${context.blueprint.key}-wk-${index + 1}`,
    point,
    mastery: clampNumber(baseMastery + index * 3 + seededRange(context.seed, 30 + index, -3, 4), 34, 76),
    students: clampNumber(context.riskCount + (8 - index) * 2 + seededRange(context.seed, 40 + index, -2, 3), 6, context.classInfo.students),
    intervention: context.blueprint.interventions[index % context.blueprint.interventions.length],
  }))
})
const teacherRiskStudentRows = computed<TeacherRiskStudentRow[]>(() => {
  const context = teacherClassCourseContext.value
  const agentRows = recordArray(teacherClassAnalyticsResult.value?.studentRiskProfiles)
  if (agentRows.length) {
    return agentRows.slice(0, Math.min(16, context.classInfo.students)).map((item, index) => {
      const weaknesses = stringArray(item.primaryWeaknesses)
      const score = Number(item.masteryScore || 0)
      return {
        id: cleanDisplayText(item.studentProfileId) || `${context.classInfo.id}-agent-risk-${index + 1}`,
        name: cleanDisplayText(item.studentName) || `学生 ${index + 1}`,
        reason: weaknesses.join('、') || cleanDisplayText(item.riskLevel || '智能体识别为需跟进'),
        evidence: `掌握度 ${Number.isFinite(score) && score > 0 ? score : context.mastery} 分 / 活跃度 ${Number(item.engagementScore || context.active)} 分`,
        action: cleanDisplayText(item.recommendedAction || '按智能体建议干预'),
      }
    })
  }
  const actions = ['提醒+沟通', '个性化辅导', '督促提交', '资源推荐', '学习计划', '课堂点名反馈', '短测复盘']
  return Array.from({ length: context.riskCount }, (_item, index) => {
    const name = context.classInfo.roster[index % context.classInfo.roster.length]
    const score = clampNumber(context.mastery - 31 + seededRange(context.seed, 60 + index, -6, 6), 32, 66)
    return {
      id: `${context.classInfo.id}-${context.blueprint.key}-rs-${index + 1}`,
      name,
      reason: context.blueprint.riskReasons[index % context.blueprint.riskReasons.length],
      evidence: `05-${16 - (index % 5)} ${context.blueprint.label} 阶段证据 ${score} 分`,
      action: actions[index % actions.length],
    }
  })
})
const teacherEvidenceStreams = computed(() => [
  {
    id: 'dialogue',
    title: '对话证据',
    count: 80 + teacherClassCourseContext.value.active + seededRange(teacherClassCourseContext.value.seed, 70, 0, 28),
    icon: MessageSquareText,
    rows: [
      `05-16 14:32 ${teacherClassCourseContext.value.classInfo.roster[0]} 提问：${teacherClassCourseContext.value.blueprint.evidenceTopics[0]}？`,
      `05-16 11:08 ${teacherClassCourseContext.value.classInfo.roster[1]} 提问：${teacherClassCourseContext.value.blueprint.evidenceTopics[1]}？`,
      `05-15 16:47 ${teacherClassCourseContext.value.classInfo.roster[2]} 提问：${teacherClassCourseContext.value.blueprint.evidenceTopics[2]}？`,
    ],
  },
  {
    id: 'quiz',
    title: '测评证据',
    count: 58 + teacherClassCourseContext.value.weakCount + seededRange(teacherClassCourseContext.value.seed, 71, 0, 14),
    icon: ClipboardList,
    rows: [
      `05-15 ${teacherClassCourseContext.value.blueprint.label} 阶段测评平均分：${teacherClassCourseContext.value.mastery - 4} 分｜正确率：${teacherClassCourseContext.value.mastery - 12}%`,
      `05-12 单元测评（${teacherWeakKnowledgeRows.value[0]?.point || '核心知识点'}）平均分：${teacherWeakKnowledgeRows.value[0]?.mastery || 58} 分`,
      `05-09 单元测评（${teacherWeakKnowledgeRows.value[1]?.point || '阶段任务'}）正确率：${teacherWeakKnowledgeRows.value[1]?.mastery || 60}%`,
    ],
  },
  {
    id: 'behavior',
    title: '学习行为证据',
    count: teacherClassCourseContext.value.classInfo.students * 4 + seededRange(teacherClassCourseContext.value.seed, 72, 8, 34),
    icon: LineChart,
    rows: [
      `05-16 ${teacherClassCourseContext.value.classInfo.shortName} 学习时长 ${Math.round(teacherClassCourseContext.value.active * 0.42)}.${seededRange(teacherClassCourseContext.value.seed, 73, 0, 9)} 小时`,
      `05-16 ${teacherClassCourseContext.value.blueprint.label} 资源完成率 ${teacherClassCourseContext.value.active}%`,
      `05-16 讨论参与 ${teacherClassCourseContext.value.active + seededRange(teacherClassCourseContext.value.seed, 74, 6, 28)} 次`,
    ],
  },
  {
    id: 'feedback',
    title: '教师反馈证据',
    count: 24 + teacherClassCourseContext.value.riskCount + seededRange(teacherClassCourseContext.value.seed, 75, 0, 9),
    icon: UserRound,
    rows: [
      `05-15 ${teacherClassCourseContext.value.blueprint.label} 课堂表现较好：${teacherClassCourseContext.value.classInfo.roster[3]}、${teacherClassCourseContext.value.classInfo.roster[4]} 等 ${seededRange(teacherClassCourseContext.value.seed, 76, 4, 9)} 人`,
      `05-14 重点跟进：${teacherRiskStudentRows.value.slice(0, 2).map((row) => row.name).join('、')}`,
      `05-13 作业质量有提升：${teacherClassCourseContext.value.classInfo.roster[5]}、${teacherClassCourseContext.value.classInfo.roster[6]} 等 ${seededRange(teacherClassCourseContext.value.seed, 77, 3, 8)} 人`,
    ],
  },
])
const teacherRadarCenter = 150
const teacherRadarRadius = 104
const teacherRadarRings = [34, 58, 82, 106]
function teacherRadarPoint(index: number, value: number) {
  const axisCount = Math.max(teacherRadarAxes.value.length, 1)
  const angle = (Math.PI * 2 * index) / axisCount - Math.PI / 2
  const distance = value * teacherRadarRadius
  return `${(teacherRadarCenter + Math.cos(angle) * distance).toFixed(1)},${(teacherRadarCenter + Math.sin(angle) * distance).toFixed(1)}`
}
const teacherRadarPolygon = computed(() => teacherRadarAxes.value.map((axis, index) => teacherRadarPoint(index, axis.classScore)).join(' '))
const teacherRadarSchoolPolygon = computed(() => teacherRadarAxes.value.map((axis, index) => teacherRadarPoint(index, axis.schoolScore)).join(' '))
const teacherRadarLabels = computed(() =>
  teacherRadarAxes.value.map((axis, index) => {
    const angle = (Math.PI * 2 * index) / Math.max(teacherRadarAxes.value.length, 1) - Math.PI / 2
    return {
      ...axis,
      x: teacherRadarCenter + Math.cos(angle) * (teacherRadarRadius + 42),
      y: teacherRadarCenter + Math.sin(angle) * (teacherRadarRadius + 32),
    }
  }),
)

const overviewMetrics = computed<ProfileMetric[]>(() => [
  {
    label: isTeacher.value ? '班级平均掌握度' : '综合掌握度',
    value: masteryAverage.value ? `${masteryAverage.value}%` : '待同步',
    detail: mastery.value.length ? `基于 ${mastery.value.length} 个知识点` : '等待课程掌握度数据',
    progress: masteryAverage.value || undefined,
    tone: masteryAverage.value ? 'up' : undefined,
  },
  {
    label: '学习稳定性',
    value: events.value.length >= 6 ? '稳定' : events.value.length ? '跟踪中' : '待观察',
    detail: `${events.value.length} 条学习事件`,
    icon: Activity,
  },
  {
    label: '优势',
    value: topMastery.value?.knowledgePoint || '待识别',
    detail: topMastery.value ? `掌握度 ${Math.round(Number(topMastery.value.masteryScore))}%` : '完成更多测评后自动识别',
    icon: ThumbsUp,
  },
  {
    label: '待提升',
    value: weakMastery.value?.knowledgePoint || weaknessHint.value,
    detail: weakMastery.value ? `掌握度 ${Math.round(Number(weakMastery.value.masteryScore))}%` : '来自画像文本和测评记录',
    icon: TrendingUp,
  },
  {
    label: '画像可信度',
    value: `${confidenceScore.value}%`,
    detail: `画像 ${profiles.value.length} 份 / 证据 ${evidenceItems.value.length} 条`,
    icon: ShieldCheck,
  },
])

const topMastery = computed(() => [...mastery.value].sort((a, b) => Number(b.masteryScore) - Number(a.masteryScore))[0])
const weakMastery = computed(() => [...mastery.value].sort((a, b) => Number(a.masteryScore) - Number(b.masteryScore))[0])
const radarCenterLevel = computed(() => {
  const score = masteryAverage.value || confidenceScore.value
  if (score >= 80) return '高水平'
  if (score >= 60) return '中等水平'
  if (score >= 45) return '待提升'
  return '待采集'
})
const weaknessHint = computed(() => {
  const text = `${selectedProfile.value?.constraintsText || ''} ${selectedProfile.value?.dialogueSummary || ''}`
  if (text.includes('表达')) return '概念表达'
  if (text.includes('实践') || text.includes('代码')) return '实践迁移'
  if (text.includes('时间')) return '时间管理'
  return '待识别'
})
const radarDimensions = computed<RadarDimension[]>(() => [
  { key: 'knowledge', label: '知识基础', score: masteryAverage.value || 62, delta: mastery.value.length ? '+实时' : '待采集', icon: BookOpenCheck },
  { key: 'practice', label: '实践应用', score: Math.max(52, attemptAverage.value || 64), delta: attempts.value.length ? '+测评' : '待测评', icon: Code2 },
  { key: 'solving', label: '问题解决', score: Math.max(50, Math.round((masteryAverage.value || 60) * 0.55 + (attemptAverage.value || 60) * 0.45)), delta: '+综合', icon: Target },
  { key: 'expression', label: '表达复盘', score: weaknessHint.value === '概念表达' ? 48 : 66, delta: weaknessHint.value === '概念表达' ? '待提升' : '+稳定', icon: ClipboardList, weak: weaknessHint.value === '概念表达' },
  { key: 'time', label: '时间管理', score: events.value.length >= 5 ? 72 : 58, delta: `${events.value.length} 事件`, icon: CalendarCheck2 },
  { key: 'collab', label: '课程投入', score: reports.value.length || events.value.length ? 68 : 55, delta: `${reports.value.length} 报告`, icon: UserRound },
])

const radarCenter = 160
const radarRadius = 112
const radarRings = [42, 70, 98, 126]

function radarPoint(index: number, value: number) {
  const angle = (Math.PI * 2 * index) / radarDimensions.value.length - Math.PI / 2
  const distance = (value / 100) * radarRadius
  const x = radarCenter + Math.cos(angle) * distance
  const y = radarCenter + Math.sin(angle) * distance
  return `${x.toFixed(1)},${y.toFixed(1)}`
}

const radarPolygon = computed(() => radarDimensions.value.map((item, index) => radarPoint(index, item.score)).join(' '))
const radarPolylinePoints = computed(() => {
  const points = radarPolygon.value
  return points ? `${points} ${points.split(' ')[0]}` : ''
})
const radarPoints = computed(() =>
  radarDimensions.value.map((item, index) => {
    const [x, y] = radarPoint(index, item.score).split(',').map(Number)
    return { ...item, x, y }
  }),
)
const radarAxisLines = computed(() =>
  radarDimensions.value.map((_item, index) => {
    const angle = (Math.PI * 2 * index) / radarDimensions.value.length - Math.PI / 2
    return {
      x: radarCenter + Math.cos(angle) * radarRadius,
      y: radarCenter + Math.sin(angle) * radarRadius,
    }
  }),
)

const evidenceItems = computed<EvidenceItem[]>(() => {
  const eventRows = events.value.slice(0, 8).map((item, index) => ({
    id: `event-${item.id || index}`,
    time: formatDate(item.createdAt),
    type: eventTypeLabel(item.eventType),
    title: eventTitle(item),
    group: '学习习惯' as const,
    course: courseName(item.courseId),
    confidence: Math.min(96, 70 + index * 3),
    status: '已纳入画像',
    icon: eventIcon(item.eventType),
  }))
  const attemptRows = attempts.value.slice(0, 6).map((item, index) => ({
    id: `attempt-${item.id || index}`,
    time: formatDate(item.createdAt),
    type: '测评',
    title: cleanDisplayText(item.topic || `测评 ${index + 1}`),
    group: '知识掌握' as const,
    course: courseName(item.courseId),
    confidence: Math.round((Number(item.score) / Math.max(Number(item.maxScore) || 100, 1)) * 100),
    status: '已纳入画像',
    icon: ClipboardList,
  }))
  const reportRows = reports.value.slice(0, 4).map((item, index) => ({
    id: `report-${item.id || index}`,
    time: formatDate(item.createdAt),
    type: '报告',
    title: cleanDisplayText(item.title || item.summary || `学习报告 ${index + 1}`),
    group: evidenceTabs[3],
    course: courseTitle.value,
    confidence: 88,
    status: '已纳入画像',
    icon: LineChart,
  }))
  const masteryRows = mastery.value.slice(0, 6).map((item, index) => ({
    id: `mastery-${item.id || index}`,
    time: formatDate(item.updatedAt || ''),
    type: '掌握度',
    title: cleanDisplayText(item.knowledgePoint),
    group: '知识掌握' as const,
    course: courseTitle.value,
    confidence: Math.round(Number(item.masteryScore) || 0),
    status: '已纳入画像',
    icon: BookOpenCheck,
  }))
  const dimensionRows = dimensions.value.slice(0, 8).map((item, index) => ({
    id: `dimension-${item.id || index}`,
    time: formatDate(item.updatedAt || item.createdAt),
    type: '画像维度',
    title: `${cleanDisplayText(item.dimensionName || item.dimensionKey)}：${cleanDisplayText(item.value)}`,
    group: evidenceTabs[3],
    course: courseTitle.value,
    confidence: Math.round(Number(item.confidenceScore) || 0),
    status: evidenceStatusText(item.evidence || item.source, '已纳入画像'),
    icon: Info,
  }))
  const historyRows = profileHistory.value.slice(0, 8).map((item, index) => ({
    id: `history-${item.id || index}`,
    time: formatDate(item.createdAt),
    type: '画像变更',
    title: `${cleanDisplayText(item.dimensionKey)}：${cleanDisplayText(item.newValue)}`,
    group: evidenceTabs[3],
    course: courseTitle.value,
    confidence: 82,
    status: evidenceStatusText(item.evidence || item.source, '历史记录'),
    icon: LineChart,
  }))
  return [...eventRows, ...attemptRows, ...reportRows, ...masteryRows, ...dimensionRows, ...historyRows]
})
const filteredEvidence = computed(() =>
  activeEvidenceTab.value === '总览' ? evidenceItems.value : evidenceItems.value.filter((item) => item.group === activeEvidenceTab.value),
)
const classProfileCards = computed(() =>
  profiles.value.map((profile) => {
    const isRisk = riskProfiles.value.some((item) => item.id === profile.id)
    return {
      profile,
      tone: (isRisk ? 'warn' : 'info') as Tone,
      title: cleanDisplayText(profile.studentName || '未命名学生'),
      summary: cleanDisplayText(profile.dialogueSummary || profile.learningGoal || '暂无画像摘要'),
      level: cleanDisplayText(profile.currentLevel || '水平待同步'),
      goal: cleanDisplayText(profile.learningGoal || '目标待同步'),
    }
  }),
)
const classMetrics = computed(() => [
  { label: '课程数', value: courses.value.length, detail: '教师可切换的课程画像范围' },
  { label: '画像数', value: profiles.value.length, detail: '来自 profilesApi 的学生画像' },
  { label: '风险画像', value: isTeacher.value ? teacherRiskStudentRows.value.length : riskProfiles.value.length, detail: '优先来自班级画像智能体' },
  { label: '证据数', value: evidenceItems.value.length, detail: '学习事件、测评、报告、掌握度' },
])
const interventionCards = computed(() => [
  {
    title: isTeacher.value ? '班级干预建议' : '今日建议',
    icon: Sparkles,
    lines: [
      weakMastery.value
        ? `优先补齐「${weakMastery.value.knowledgePoint}」的讲解、例题和测评。`
        : selectedProfile.value?.learningGoal || '先完成当前课程的关键知识点复盘。',
    ],
    tags: ['推荐'],
    action: isTeacher.value ? '进入资源审核生成补救包' : '加入今日学习',
  },
  {
    title: isTeacher.value ? '重点学生' : '跨课程补弱',
    icon: AlertTriangle,
    lines: isTeacher.value
      ? (riskProfiles.value.length ? riskProfiles.value.slice(0, 3).map((profile) => `${profile.studentName}：${cleanDisplayText(profile.currentLevel || profile.dialogueSummary)}`) : ['暂无明显风险学生'])
      : [weaknessHint.value, selectedProfile.value?.constraintsText || '根据测评和对话继续补充证据'].filter(Boolean),
    action: isTeacher.value ? '查看班级画像列表' : '查看全部补弱任务',
  },
  {
    title: isTeacher.value ? '建议检查的问题' : '建议询问老师的问题',
    icon: HelpCircle,
    lines: [
      selectedCourse.value ? `当前课程「${selectedCourse.value.title}」是否有未发布资源或审核阻断项？` : '是否需要先选择课程范围？',
      weakMastery.value ? `薄弱知识点「${weakMastery.value.knowledgePoint}」是否需要分层讲解？` : '是否需要补充测评证据？',
    ],
    action: isTeacher.value ? '进入发布质检' : '查看全部问题',
  },
  {
    title: '画像变更记录',
    icon: LineChart,
    lines: reports.value.length
      ? reports.value.slice(0, 3).map((item) => `${formatDate(item.createdAt)} ${cleanDisplayText(item.title || item.summary || '学习报告')}`)
      : [`${events.value.length} 条学习事件已纳入当前画像`, `${attempts.value.length} 条测评记录已同步`],
    action: '查看完整记录',
  },
])
const courseMatrix = computed(() =>
  courses.value.slice(0, 6).map((course) => ({
    course: course.title,
    metrics: [
      { label: '知识基础', value: course.id === selectedCourseId.value ? masteryAverage.value || 62 : 60 },
      { label: '实践应用', value: course.id === selectedCourseId.value ? attemptAverage.value || 64 : 58 },
      { label: '表达能力', value: weaknessHint.value === '概念表达' ? 48 : 66 },
      { label: '学习证据', value: course.id === selectedCourseId.value ? Math.min(100, evidenceItems.value.length * 12) : 52 },
    ],
    effort: course.id === selectedCourseId.value ? `${events.value.length} 条证据` : '待同步',
  })),
)

function courseName(courseId?: string) {
  return courses.value.find((course) => course.id === courseId)?.title || courseTitle.value
}

function eventTypeLabel(value?: string) {
  const text = String(value || '').toUpperCase()
  if (text.includes('TUTOR') || text.includes('CHAT')) return '对话'
  if (text.includes('DOWNLOAD') || text.includes('VIEW')) return '学习行为'
  if (text.includes('RESOURCE')) return '资源学习'
  return '学习事件'
}

function eventTitle(item: LearningEvent) {
  const payload = cleanDisplayText(item.eventPayload || '')
  const parsed = parseEventPayload(item.eventPayload)
  const eventType = String(item.eventType || '').toUpperCase()
  const tabLabel = tabName(parsed.tab)
  if (eventType.includes('COURSE_TAB_OPENED')) return tabLabel ? `打开课程「${tabLabel}」分区` : '查看课程空间分区'
  if (eventType.includes('RESOURCE_ADDED_TO_PATH')) return `加入学习路径：${payloadField(parsed, 'resourceTitle') || '课程资源'}`
  if (eventType.includes('COURSE_PATH_OPENED')) return '查看课程学习路径'
  if (eventType.includes('COURSE_CONTINUE')) return '从课程空间继续学习'
  if (eventType.includes('COURSE_RESOURCE_VIEWED') || eventType.includes('RESOURCE_PREVIEWED')) {
    return `预览资源：${payloadField(parsed, 'resourceTitle') || '课程资料'}`
  }
  if (eventType.includes('TODAY_BUDGET_UPDATED')) return `调整今日学习预算为 ${payloadField(parsed, 'budgetMinutes') || item.durationSeconds || 0} 分钟`
  if (eventType.includes('TODAY_PLANNING_WEIGHT_CHANGED')) return `调整今日规划权重：${planningWeightLabel(payloadField(parsed, 'weightKey'))}`
  if (eventType.includes('TODAY_REPLANNED')) return '重新规划今日学习任务'
  if (eventType.includes('TODAY_TASK_STARTED')) return `开始学习任务：${payloadField(parsed, 'taskTitle') || '今日任务'}`
  if (eventType.includes('TODAY_TASK_JOINED')) return `加入今日计划：${payloadField(parsed, 'taskTitle') || '学习任务'}`
  if (eventType.includes('TODAY_TASK_POSTPONED')) return `稍后处理：${payloadField(parsed, 'taskTitle') || '学习任务'}`
  if (eventType.includes('CHAT') || eventType.includes('TUTOR')) return '与课程 AI 助教完成一次对话'
  if (payload && !payload.startsWith('{') && !payload.startsWith('[')) return payload
  return `${eventTypeLabel(item.eventType)} / ${item.durationSeconds || 0} 秒`
}

function eventIcon(value?: string): Component {
  const text = String(value || '').toUpperCase()
  if (text.includes('TUTOR') || text.includes('CHAT')) return MessageSquareText
  if (text.includes('DOWNLOAD') || text.includes('UPLOAD')) return Upload
  if (text.includes('RESOURCE')) return BookOpenCheck
  return Activity
}

function parseEventPayload(value?: string) {
  const text = String(value || '').trim()
  if (!text.startsWith('{') && !text.startsWith('[')) return {} as Record<string, unknown>
  try {
    const parsed = JSON.parse(text)
    return parsed && typeof parsed === 'object' && !Array.isArray(parsed) ? (parsed as Record<string, unknown>) : {}
  } catch {
    return {} as Record<string, unknown>
  }
}

function payloadField(payload: Record<string, unknown>, key: string) {
  const value = payload[key]
  if (value === undefined || value === null) return ''
  return cleanDisplayText(String(value))
}

function tabName(value: unknown) {
  const text = String(value || '')
  if (text === 'path') return '学习路径'
  if (text === 'resources') return '章节资源'
  if (text === 'assistant') return '课程 AI 助教'
  if (text === 'records') return '生成记录'
  return cleanDisplayText(text)
}

function planningWeightLabel(value: string) {
  if (value === 'deadline') return '截止时间'
  if (value === 'mastery') return '薄弱知识'
  if (value === 'course') return '课程权重'
  return value || '综合排序'
}

function stableHash(value: string) {
  let hash = 2166136261
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index)
    hash = Math.imul(hash, 16777619)
  }
  return Math.abs(hash >>> 0)
}

function seededRange(seed: number, salt: number, min: number, max: number) {
  const span = max - min + 1
  const next = Math.abs(Math.imul(seed + salt * 2654435761, 1597334677) >>> 0)
  return min + (next % span)
}

function clampNumber(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, Math.round(value)))
}

function resolveTeacherCourseBlueprint(course?: Course): TeacherCourseBlueprint {
  const text = `${course?.title || ''} ${course?.description || ''} ${course?.syllabusJson || ''}`
  if (/java|servlet|jsp|web/i.test(text)) return teacherCourseBlueprints[0]
  if (/ai|智能体|画像|资源生成|知识图谱|学习路径/i.test(text)) return teacherCourseBlueprints[1]
  if (/项目|工程实践|需求|接口|验收|案例/i.test(text)) return teacherCourseBlueprints[2]
  if (/大学计算机|计算机基础|office|表格|文档|图表|数据/i.test(text)) return teacherCourseBlueprints[3]
  return teacherCourseBlueprints[4]
}

function evidenceStatusText(value?: string, fallback = '已纳入画像') {
  const text = cleanDisplayText(value || '')
  if (!text || text.startsWith('{') || text.startsWith('[')) return fallback
  return text
}

function barStyle(value: number) {
  return { width: `${Math.min(100, Math.max(0, Math.round(value)))}%` }
}

function recordArray(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value) ? value.filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === 'object' && !Array.isArray(item)) : []
}

function stringArray(value: unknown): string[] {
  if (!Array.isArray(value)) return []
  return value.map((item) => cleanDisplayText(item)).filter(Boolean)
}

function agentNumber(record: Record<string, unknown> | null | undefined, key: string, fallback: number, min = 0, max = 100) {
  const value = Number(record?.[key])
  return Number.isFinite(value) ? clampNumber(value, min, max) : fallback
}

function profileAgentDimensions(value: unknown) {
  return recordArray(value)
    .map((item) => {
      const confidence = Number(item.confidenceScore || 0.75)
      return {
        dimensionKey: cleanDisplayText(item.dimensionKey),
        dimensionName: cleanDisplayText(item.dimensionName),
        value: cleanDisplayText(item.value),
        evidence: cleanDisplayText(item.evidence),
        confidenceScore: Math.max(0, Math.min(1, confidence > 1 ? confidence / 100 : confidence)),
        source: cleanDisplayText(item.source || 'PROFILE_INFERENCE_AGENT'),
      }
    })
    .filter((item) => item.dimensionKey && item.value)
}

function profileLearningRecords(profileId: string) {
  return events.value
    .filter((item) => item.studentProfileId === profileId)
    .slice(0, 12)
    .map((item) => `${eventTypeLabel(item.eventType)}：${eventTitle(item)} / ${formatDate(item.createdAt)}`)
}

function buildProfileAgentPayload(profile: ProfileResponse) {
  return {
    studentProfileId: profile.id,
    courseId: selectedCourseId.value || undefined,
    courseTitle: selectedCourse.value?.title || '',
    declaredMajor: profile.major || '',
    currentLevel: profile.currentLevel || '',
    learningGoal: profile.learningGoal || '',
    preferences: profile.preferences || '',
    constraintsText: profile.constraintsText || '',
    dialogueTurns: [profile.dialogueSummary, profile.constraintsText, profile.preferences].filter(Boolean),
    learningRecords: profileLearningRecords(profile.id),
    assessmentSummaries: [
      ...attempts.value.slice(0, 8).map((item) => `${item.topic || '测评'}：${item.score}/${item.maxScore}`),
      ...mastery.value.slice(0, 8).map((item) => `${item.knowledgePoint}：${Math.round(Number(item.masteryScore) || 0)}%`),
      ...reports.value.slice(0, 4).map((item) => item.summary || item.title || ''),
    ].filter(Boolean),
    tutoringSummaries: events.value
      .filter((item) => /TUTOR|CHAT|ASSIST/i.test(item.eventType || ''))
      .slice(0, 8)
      .map((item) => eventTitle(item)),
    documentTexts: evidenceItems.value.slice(0, 12).map((item) => `${item.type}：${item.title} / ${item.status}`),
  }
}

function profileWeaknessSignals(profile: ProfileResponse) {
  const text = `${profile.currentLevel} ${profile.learningGoal} ${profile.preferences} ${profile.constraintsText} ${profile.dialogueSummary}`
  return [
    ...text
      .split(/[，。；;、\s]+/)
      .map((item) => cleanDisplayText(item))
      .filter((item) => /薄弱|不足|风险|困难|欠缺|待提升|基础|表达|实践|时间/.test(item))
      .slice(0, 4),
    ...mastery.value.slice(0, 3).map((item) => item.knowledgePoint),
  ].filter(Boolean)
}

function buildClassAnalyticsPayload() {
  const course = selectedCourse.value
  if (!course?.id) throw new Error('请先选择要分析的课程。')
  const snapshots = profiles.value.map((profile) => ({
    studentProfileId: profile.id,
    studentName: profile.studentName || '匿名学生',
    profileSummary: profile.dialogueSummary || profile.learningGoal || profile.currentLevel || '',
    recentScores:
      profile.id === selectedProfileId.value
        ? attempts.value.slice(0, 6).map((item) => clampNumber(Number(item.score || 0), 0, 100))
        : [],
    completedResources: profile.id === selectedProfileId.value ? events.value.filter((item) => /RESOURCE|COMPLETE/i.test(item.eventType || '')).length : 0,
    tutoringCount: profile.id === selectedProfileId.value ? events.value.filter((item) => /TUTOR|CHAT|ASSIST/i.test(item.eventType || '')).length : 0,
    codePracticeCount: profile.id === selectedProfileId.value ? events.value.filter((item) => /CODE|PRACTICE/i.test(item.eventType || '')).length : 0,
    weaknessSignals: profileWeaknessSignals(profile),
    learningEvents: profile.id === selectedProfileId.value ? profileLearningRecords(profile.id) : [profile.dialogueSummary || profile.currentLevel || '画像摘要待补充'].filter(Boolean),
  }))
  if (!snapshots.length) throw new Error('当前没有可分析的学生画像快照。')
  return {
    courseId: course.id,
    courseTitle: course.title,
    topic: teacherProfileDimension.value || '班级学习表现',
    timeRange: teacherDateRange.value || '最近 7 天',
    snapshots,
    documentTexts: [
      `班级：${teacherSelectedClass.value.name}`,
      `课程：${course.title}`,
      `画像数：${profiles.value.length}`,
      ...evidenceItems.value.slice(0, 12).map((item) => `${item.type}：${item.title}`),
    ],
  }
}

function focusTeacherRiskStudent(row: { id: string; name: string; action: string }) {
  teacherRiskFocusId.value = row.id
  const matched = profiles.value.find((profile) => profile.studentName.includes(row.name.replace('同学', '')))
  if (matched) selectedProfileId.value = matched.id
  teacherProfileNotice.value = `已记录干预动作：${row.name} / ${row.action}`
}

function exportTeacherRiskCsv() {
  const header = ['学生', '风险原因', '最近证据', '建议动作']
  const rows = teacherRiskStudentRows.value.map((row) => [row.name, row.reason, row.evidence, row.action])
  const csv = [header, ...rows].map((row) => row.map((cell) => `"${String(cell).replaceAll('"', '""')}"`).join(',')).join('\n')
  const blob = new Blob([`\uFEFF${csv}`], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `${teacherSelectedClass.value.name.replace(/[（(].*$/, '')}-${teacherClassCourseContext.value.blueprint.label}-风险学生.csv`
  anchor.click()
  URL.revokeObjectURL(url)
  teacherProfileNotice.value = '已导出风险学生 CSV。'
}

function toggleTeacherEvidence(streamId: string) {
  teacherExpandedEvidence.value = teacherExpandedEvidence.value === streamId ? '' : streamId
}

async function refreshTeacherClassProfile() {
  if (profileAgentLoading.value) return
  profileAgentLoading.value = true
  teacherProfileNotice.value = '正在调用班级画像智能体。'
  error.value = ''
  try {
    const response = await agentsApi.invoke('/teaching/class-analytics', buildClassAnalyticsPayload())
    if (Boolean(response.fallbackUsed)) {
      throw new Error('班级画像智能体返回了降级结果，本次不采用。')
    }
    teacherClassAnalyticsResult.value = response
    teacherProfileNotice.value = `${teacherSelectedClass.value.name} / ${courseTitle.value} 已由班级画像智能体刷新${response.artifactId ? `，产物 ${response.artifactId}` : ''}。`
  } catch (err) {
    teacherClassAnalyticsResult.value = null
    const message = err instanceof Error ? err.message : '班级画像智能体分析失败。'
    teacherProfileNotice.value = message
    error.value = message
  } finally {
    profileAgentLoading.value = false
  }
}

function selectProfile(profileId: string) {
  selectedProfileId.value = profileId
}

function selectCourse(courseId: string) {
  selectedCourseId.value = courseId
  app.setActiveCourse(courseId)
}

async function reanalyzeProfile() {
  if (profileAgentLoading.value) return false
  if (!selectedProfile.value) await loadProfiles()
  const profile = selectedProfile.value
  if (!profile) {
    error.value = '当前没有可重新分析的学生画像。'
    return false
  }
  profileAgentLoading.value = true
  error.value = ''
  try {
    const response = await agentsApi.invoke('/profiles/agent-infer', buildProfileAgentPayload(profile))
    if (Boolean(response.fallbackUsed)) {
      throw new Error('画像智能体返回了降级结果，本次不采用。')
    }
    const dimensionsPayload = profileAgentDimensions(response.dimensions)
    if (!dimensionsPayload.length) {
      throw new Error('画像智能体没有返回可写入的维度。')
    }
    await profilesApi.updateDimensions(profile.id, {
      dimensions: dimensionsPayload,
      reason: `PROFILE_INFERENCE_AGENT${response.artifactId ? `:${response.artifactId}` : ''}`,
    })
    if (isTeacher.value) {
      teacherProfileNotice.value = `${profile.studentName} 画像已由智能体重新分析${response.artifactId ? `，产物 ${response.artifactId}` : ''}。`
    }
    await loadProfiles()
    await loadEvidence()
    return true
  } catch (err) {
    const message = err instanceof Error ? err.message : '画像智能体分析失败。'
    error.value = message
    if (isTeacher.value) teacherProfileNotice.value = message
    return false
  } finally {
    profileAgentLoading.value = false
  }
}

async function viewSuggestions() {
  const analyzed = await reanalyzeProfile()
  if (!analyzed) return
  await router.push({
    path: '/learning',
    query: {
      tab: 'chat',
      courseId: selectedCourseId.value || undefined,
      question: weakMastery.value
        ? `请根据我的画像证据，给出 ${weakMastery.value.knowledgePoint} 的补救学习建议。`
        : '请根据我的学习画像给出下一步学习建议。',
    },
  })
}

function viewAllEvidence() {
  activeEvidenceTab.value = evidenceTabs[0]
  void loadEvidence()
}

async function loadProfiles() {
  loading.value = true
  error.value = ''
  try {
    const [profileResult, courseResult] = await Promise.allSettled([profilesApi.list(), coursesApi.list()])
    profiles.value = profileResult.status === 'fulfilled' ? profileResult.value : []
    courses.value = courseResult.status === 'fulfilled' ? courseResult.value : []
    selectedProfileId.value ||= visibleProfiles.value[0]?.id || profiles.value[0]?.id || ''
    selectedCourseId.value ||= courses.value.find((course) => course.id === app.activeCourseId)?.id || courses.value[0]?.id || ''
    if (selectedCourseId.value) app.setActiveCourse(selectedCourseId.value)
    const failures = [profileResult, courseResult].filter((item) => item.status === 'rejected').length
    if (failures) error.value = '画像或课程列表暂未同步，请确认服务在线后刷新。'
    await loadEvidence()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '画像数据加载失败'
  } finally {
    loading.value = false
  }
}

async function loadEvidence() {
  const profileId = selectedProfileId.value
  if (!profileId) {
    dimensions.value = []
    profileHistory.value = []
    events.value = []
    attempts.value = []
    mastery.value = []
    reports.value = []
    return
  }
  evidenceLoading.value = true
  try {
    const [detailResult, dimensionResult, historyResult, eventResult, attemptResult, masteryResult, reportResult] = await Promise.allSettled([
      profilesApi.detail(profileId),
      profilesApi.dimensions(profileId),
      profilesApi.history(profileId),
      learningApi.events(profileId),
      learningApi.attempts(profileId),
      selectedCourseId.value ? learningApi.mastery(profileId, selectedCourseId.value) : Promise.resolve([]),
      selectedCourseId.value ? learningApi.evaluationReports(profileId, selectedCourseId.value) : Promise.resolve([]),
    ])
    if (detailResult.status === 'fulfilled') {
      dimensions.value = detailResult.value.dimensions.length ? detailResult.value.dimensions : []
      profileHistory.value = detailResult.value.recentHistory.length ? detailResult.value.recentHistory : []
    }
    dimensions.value = dimensionResult.status === 'fulfilled' && dimensionResult.value.length ? dimensionResult.value : dimensions.value
    profileHistory.value = historyResult.status === 'fulfilled' && historyResult.value.length ? historyResult.value : profileHistory.value
    events.value = eventResult.status === 'fulfilled' ? eventResult.value : []
    attempts.value = attemptResult.status === 'fulfilled' ? attemptResult.value : []
    mastery.value = masteryResult.status === 'fulfilled' ? masteryResult.value : []
    reports.value = reportResult.status === 'fulfilled' ? reportResult.value : []
  } finally {
    evidenceLoading.value = false
  }
}

watch([selectedProfileId, selectedCourseId], () => {
  void loadEvidence()
})

onMounted(async () => {
  await loadProfiles()
  if (isTeacher.value) await loadTeacherClasses()
})
</script>

<template>
  <div v-if="isTeacher" class="teacher-class-profile-page" aria-label="教师班级画像">
    <ErrorNotice :message="error" />
    <LoadingBlock :show="loading || evidenceLoading || profileAgentLoading" />
    <p v-if="teacherProfileNotice" class="teacher-profile-notice">{{ teacherProfileNotice }}</p>

    <section class="class-profile-filterbar" aria-label="班级画像筛选">
      <label>
        <span>课程</span>
        <select v-model="selectedCourseId" @change="selectCourse(selectedCourseId)">
          <option v-for="course in courses" :key="course.id" :value="course.id">{{ course.title }}</option>
        </select>
      </label>
      <label>
        <span>班级</span>
        <select v-model="teacherClassId">
          <option v-for="item in teacherClassOptions" :key="item.id" :value="item.id">{{ item.name }}</option>
        </select>
      </label>
      <label>
        <span>时间范围</span>
        <input v-model="teacherDateRange" />
      </label>
      <label>
        <span>画像维度</span>
        <select v-model="teacherProfileDimension">
          <option v-for="item in teacherDimensionOptions" :key="item">{{ item }}</option>
        </select>
      </label>
      <button class="class-profile-refresh" type="button" :disabled="loading || evidenceLoading" @click="refreshTeacherClassProfile">
        <RefreshCw :size="17" />刷新画像
      </button>
    </section>

    <p v-if="isTeacher && !teacherClassAnalyticsResult" class="class-profile-estimate-banner">
      当前指标为本地估算，点击「刷新画像」由班级画像智能体生成真实分析。
    </p>

    <section class="class-profile-kpis" aria-label="班级画像指标">
      <article v-for="metric in teacherSummaryMetrics" :key="metric.key" :class="['class-kpi-card', metric.tone]">
        <span class="class-kpi-icon"><component :is="metric.icon" :size="28" /></span>
        <div>
          <small>{{ metric.label }}</small>
          <strong>{{ metric.value }}<em>{{ metric.unit }}</em></strong>
          <p>↑ {{ metric.delta }} <span>较上周</span></p>
        </div>
      </article>
    </section>

    <section class="class-profile-main-grid" aria-label="班级画像分析">
      <article class="class-profile-panel class-radar-card">
        <header>
          <h2>班级能力雷达 <Info :size="15" /></h2>
        </header>
        <div class="teacher-radar-wrap">
          <svg viewBox="0 0 300 300" role="img" aria-label="班级能力雷达">
            <circle v-for="ring in teacherRadarRings" :key="ring" :cx="teacherRadarCenter" :cy="teacherRadarCenter" :r="ring" class="teacher-radar-ring" />
            <line
              v-for="(axis, index) in teacherRadarAxes"
              :key="axis.label"
              :x1="teacherRadarCenter"
              :y1="teacherRadarCenter"
              :x2="teacherRadarPoint(index, 1).split(',')[0]"
              :y2="teacherRadarPoint(index, 1).split(',')[1]"
              class="teacher-radar-axis"
            />
            <polygon :points="teacherRadarSchoolPolygon" class="teacher-radar-school" />
            <polygon :points="teacherRadarPolygon" class="teacher-radar-area" />
          </svg>
          <span v-for="label in teacherRadarLabels" :key="label.label" class="teacher-radar-label" :style="{ left: `${label.x}px`, top: `${label.y}px` }">
            {{ label.label }}<b>{{ label.classScore.toFixed(2) }}</b>
          </span>
        </div>
        <footer><span></span>本班级 <span class="dotted"></span>校级平均</footer>
      </article>

      <article class="class-profile-panel weak-matrix-card">
        <header>
          <h2>薄弱知识点矩阵 <Info :size="15" /></h2>
        </header>
        <div class="weak-row weak-head">
          <span>知识点</span><span>掌握度</span><span>涉及学生数</span><span>建议干预</span>
        </div>
        <div v-for="row in teacherWeakKnowledgeRows" :key="row.id" class="weak-row">
          <strong>{{ row.point }}</strong>
          <span class="weak-progress"><i><b :style="{ width: `${row.mastery}%` }"></b></i>{{ row.mastery }}%</span>
          <span>{{ row.students }}人</span>
          <button type="button" @click="teacherProfileNotice = `已加入干预队列：${row.point}`">{{ row.intervention }}</button>
        </div>
        <footer>
          <span>共 {{ teacherClassCourseContext.weakCount }} 条薄弱知识点</span>
          <button type="button" @click="teacherProfileNotice = `${teacherSelectedClass.name} / ${courseTitle} 已展开薄弱知识点详情`">查看更多</button>
        </footer>
      </article>

      <article class="class-profile-panel risk-table-card">
        <header>
          <h2>风险学生列表 <Info :size="15" /></h2>
          <button type="button" @click="exportTeacherRiskCsv"><Upload :size="15" />导出</button>
        </header>
        <div class="risk-row risk-head">
          <span>学生</span><span>风险原因</span><span>最近证据</span><span>建议动作</span>
        </div>
        <div v-for="row in teacherRiskStudentRows" :key="row.id" class="risk-row" :class="{ focus: teacherRiskFocusId === row.id }">
          <span><b>{{ row.name.slice(0, 1) }}</b>{{ row.name }}</span>
          <span>{{ row.reason }}</span>
          <span>{{ row.evidence }}</span>
          <button type="button" @click="focusTeacherRiskStudent(row)">{{ row.action }}</button>
        </div>
        <footer>
          <span>共 {{ teacherRiskStudentRows.length }} 名风险学生</span>
          <button type="button" @click="teacherProfileNotice = `${teacherSelectedClass.name} / ${courseTitle} 已展开全部风险学生`">查看更多</button>
        </footer>
      </article>
    </section>

    <section class="class-profile-panel evidence-stream-section" aria-label="学生画像证据流">
      <header>
        <h2>学生画像证据流 <Info :size="15" /></h2>
      </header>
      <div class="evidence-stream-grid">
        <article v-for="stream in teacherEvidenceStreams" :key="stream.id" class="evidence-stream-card">
          <header>
            <span><component :is="stream.icon" :size="20" /></span>
            <strong>{{ stream.title }}（{{ stream.count }}）</strong>
            <button type="button" @click="toggleTeacherEvidence(stream.id)">{{ teacherExpandedEvidence === stream.id ? '收起' : '查看更多' }}</button>
          </header>
          <p v-for="row in stream.rows.slice(0, teacherExpandedEvidence === stream.id ? stream.rows.length : 3)" :key="row">{{ row }}</p>
          <small>...</small>
        </article>
      </div>
    </section>
  </div>

  <div v-else class="student-profile-page" aria-label="跨课程综合学习画像">
    <div class="profile-page-actions" aria-label="画像操作">
      <button class="profile-action-button" type="button" @click="viewAllEvidence">
        <FilePlus2 :size="17" :stroke-width="1.9" />
        加载证据
      </button>
      <button class="profile-action-button primary" type="button" :disabled="loading || evidenceLoading" @click="reanalyzeProfile">
        <RefreshCw :size="17" :stroke-width="1.9" />
        重新分析
      </button>
    </div>
    <ErrorNotice :message="error" />
    <LoadingBlock :show="loading || evidenceLoading || profileAgentLoading" />

    <section class="profile-overview-strip" aria-label="画像总览指标">
      <article v-for="metric in overviewMetrics" :key="metric.label" class="profile-overview-card">
        <div v-if="metric.progress !== undefined" class="profile-progress-ring" :style="{ '--ring-value': `${metric.progress}%` }">
          <strong>{{ metric.value }}</strong>
        </div>
        <span v-else class="profile-overview-icon">
          <component :is="metric.icon || Info" :size="28" :stroke-width="1.85" />
        </span>
        <div>
          <small>{{ metric.label }}</small>
          <strong>{{ metric.value }}</strong>
        </div>
      </article>
    </section>

    <section class="profile-dashboard-grid" :style="profileGridStyle" aria-label="画像分析主体">
      <article class="profile-panel profile-radar-panel">
        <header class="profile-panel-head">
          <div>
            <h2>综合能力罗盘</h2>
          </div>
          <Info :size="16" :stroke-width="1.8" />
        </header>

        <div class="profile-radar-stage">
          <svg class="profile-radar-svg" viewBox="0 0 320 320" role="img" aria-label="综合能力罗盘">
            <circle
              v-for="ring in radarRings"
              :key="ring"
              class="radar-ring"
              :cx="radarCenter"
              :cy="radarCenter"
              :r="ring"
            />
            <line
              v-for="(axis, index) in radarAxisLines"
              :key="`axis-${index}`"
              class="radar-axis"
              :x1="radarCenter"
              :y1="radarCenter"
              :x2="axis.x"
              :y2="axis.y"
            />
            <polygon class="radar-area" :points="radarPolygon" />
            <polyline class="radar-line" :points="radarPolylinePoints" />
            <circle v-for="point in radarPoints" :key="point.key" class="radar-dot" :cx="point.x" :cy="point.y" r="5" />
          </svg>
          <div class="radar-center-score" :title="radarCenterLevel">
            <span>综合能力</span>
            <strong>{{ masteryAverage || confidenceScore }}</strong>
          </div>
          <article
            v-for="(dimension, index) in radarDimensions"
            :key="dimension.key"
            class="radar-axis-card"
            :class="[`axis-${index + 1}`, { weak: dimension.weak }]"
          >
            <span><component :is="dimension.icon" :size="18" :stroke-width="1.85" /></span>
            <div>
              <strong>{{ dimension.label }}</strong>
              <small>{{ dimension.score }}/100 · {{ dimension.delta }}</small>
            </div>
            </article>
        </div>
        <footer class="profile-risk-note">
          <AlertTriangle :size="17" :stroke-width="1.9" />
          <span>当前短板：{{ weakMastery?.knowledgePoint || weaknessHint }}</span>
          <button type="button" @click="viewSuggestions">查看提升建议</button>
        </footer>
      </article>

      <div
        class="panel-resizer"
        role="separator"
        aria-orientation="vertical"
        title="拖动调整宽度，双击恢复默认"
        @pointerdown="profileStartResize(0, $event)"
        @dblclick="profileResetLayout()"
      ></div>

      <article class="profile-panel profile-evidence-panel">
        <header class="profile-panel-head">
          <div>
            <h2>画像证据流</h2>
          </div>
        </header>
        <div class="profile-evidence-tabs" role="tablist" aria-label="证据分类">
          <button v-for="tab in evidenceTabs" :key="tab" type="button" :class="{ active: activeEvidenceTab === tab }" @click="activeEvidenceTab = tab">
            {{ tab }}
          </button>
        </div>
        <div v-if="!filteredEvidence.length" class="empty-guide">
          <strong>暂无证据</strong>
        </div>
        <div v-else class="profile-evidence-list">
          <article v-for="item in filteredEvidence" :key="item.id" class="profile-evidence-row">
            <time>{{ item.time }}</time>
            <span class="evidence-icon"><component :is="item.icon" :size="17" :stroke-width="1.85" /></span>
            <div class="evidence-copy">
              <div class="evidence-copy-top">
                <small>{{ item.type }}</small>
                <strong>{{ item.title }}</strong>
              </div>
              <span class="evidence-course">{{ item.course }}</span>
            </div>
            <div class="evidence-meta">
              <div class="evidence-confidence" :aria-label="`画像可信度 ${item.confidence}%`">
                <span>{{ item.confidence }}%</span>
                <i><b :style="barStyle(item.confidence)"></b></i>
              </div>
              <span class="evidence-status">
                {{ item.status }}
                <CheckCircle2 :size="14" :stroke-width="2" />
              </span>
            </div>
          </article>
        </div>
        <footer class="profile-panel-link">
          <button type="button" @click="viewAllEvidence">查看全部证据</button>
        </footer>
      </article>

      <div
        class="panel-resizer"
        role="separator"
        aria-orientation="vertical"
        title="拖动调整宽度，双击恢复默认"
        @pointerdown="profileStartResize(1, $event)"
        @dblclick="profileResetLayout()"
      ></div>

      <aside class="profile-panel profile-intervention-panel" aria-label="个性化干预">
        <header class="profile-panel-head">
          <div>
            <h2>个性化干预</h2>
          </div>
        </header>
        <article v-for="card in interventionCards" :key="card.title" class="intervention-card">
          <header>
            <span><component :is="card.icon" :size="17" :stroke-width="1.85" /></span>
            <strong>{{ card.title }}</strong>
          </header>
          <ol>
            <li v-for="(line, index) in card.lines" :key="line">
              <span>{{ line }}</span>
              <em v-if="card.tags?.[index]">{{ card.tags[index] }}</em>
            </li>
          </ol>
          <button type="button" @click="viewSuggestions">{{ card.action }}</button>
        </article>
      </aside>
    </section>

    <section class="profile-panel profile-matrix-panel" aria-label="课程维度矩阵">
      <header class="profile-panel-head">
        <div>
          <h2>课程维度矩阵</h2>
        </div>
        <button type="button" @click="reanalyzeProfile">刷新维度</button>
      </header>

      <div class="profile-matrix-table">
        <div class="matrix-row matrix-head">
          <span>课程</span>
          <span>知识基础</span>
          <span>实践应用</span>
          <span>表达能力</span>
          <span>学习证据</span>
          <span>学习投入</span>
        </div>
        <div v-for="course in courseMatrix" :key="course.course" class="matrix-row">
          <strong>
            <BookOpenCheck :size="17" :stroke-width="1.8" />
            {{ course.course }}
          </strong>
          <div v-for="metric in course.metrics" :key="metric.label" class="matrix-metric">
            <i><b :style="barStyle(metric.value)"></b></i>
            <span>{{ metric.value }}%</span>
          </div>
          <span class="matrix-effort">{{ course.effort }}</span>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.teacher-class-profile-page {
  display: grid;
  gap: 22px;
  min-width: 0;
  color: #15243b;
}

.teacher-profile-notice {
  min-height: 38px;
  margin: 0;
  padding: 9px 14px;
  color: #087f77;
  background: #eefbf9;
  border: 1px solid #bce5df;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 780;
}

.class-profile-filterbar,
.class-profile-panel,
.class-kpi-card {
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid #d8e5ec;
  border-radius: 12px;
  box-shadow: 0 16px 38px rgba(25, 49, 70, 0.045);
}

.class-profile-filterbar {
  display: grid;
  grid-template-columns: minmax(320px, 1.25fr) minmax(260px, 0.88fr) minmax(280px, 0.9fr) minmax(230px, 0.75fr) 150px;
  gap: 28px;
  align-items: center;
  min-height: 96px;
  padding: 0 22px;
}

.class-profile-filterbar label {
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr);
  align-items: center;
  gap: 12px;
  color: #5e7188;
  font-size: 14px;
  font-weight: 820;
}

.class-profile-filterbar select,
.class-profile-filterbar input {
  width: 100%;
  height: 48px;
  min-width: 0;
  padding: 0 18px;
  color: #152a45;
  background: #ffffff;
  border: 1px solid #cfdee7;
  border-radius: 9px;
  outline: 0;
  font-size: 14px;
  font-weight: 780;
}

.class-profile-refresh {
  display: inline-flex;
  min-height: 48px;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #087f77;
  background: #ffffff;
  border: 1px solid #cfdee7;
  border-radius: 9px;
  cursor: pointer;
  font-weight: 880;
}

.class-profile-kpis {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 20px;
}

.class-kpi-card {
  display: grid;
  grid-template-columns: 74px minmax(0, 1fr);
  align-items: center;
  min-height: 138px;
  padding: 0 28px;
}

.class-kpi-icon {
  display: grid;
  width: 62px;
  height: 62px;
  place-items: center;
  color: #087f77;
  background: #e8f8f6;
  border-radius: 50%;
}

.class-kpi-card.orange .class-kpi-icon {
  color: #e77f28;
  background: #fff1e6;
}

.class-kpi-card.red .class-kpi-icon {
  color: #d94747;
  background: #fff0f0;
}

.class-kpi-card.blue .class-kpi-icon {
  color: #2872d9;
  background: #ebf4ff;
}

.class-kpi-card small {
  color: #253b55;
  font-size: 15px;
  font-weight: 900;
}

.class-kpi-card strong {
  display: block;
  margin-top: 6px;
  color: #111f36;
  font-size: 34px;
  font-weight: 960;
  line-height: 1;
}

.class-kpi-card em {
  margin-left: 4px;
  font-size: 18px;
  font-style: normal;
}

.class-kpi-card p {
  margin: 8px 0 0;
  color: #07847b;
  font-size: 14px;
  font-weight: 850;
}

.class-kpi-card p span {
  margin-left: 10px;
  color: #6d7e92;
  font-weight: 720;
}

.class-profile-main-grid {
  display: grid;
  grid-template-columns: minmax(390px, 0.82fr) minmax(520px, 1.05fr) minmax(560px, 1.05fr);
  gap: 18px;
  min-width: 0;
}

.class-profile-panel {
  min-width: 0;
  overflow: hidden;
}

.class-profile-panel > header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 64px;
  padding: 0 22px;
}

.class-profile-panel h2 {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin: 0;
  color: #14243c;
  font-size: 20px;
  font-weight: 930;
}

.class-profile-panel header button,
.weak-row button,
.risk-row button,
.evidence-stream-card header button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 34px;
  gap: 6px;
  padding: 0 12px;
  color: #07847b;
  background: #ffffff;
  border: 1px solid #c8e0df;
  border-radius: 7px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 840;
  white-space: nowrap;
}

.class-radar-card {
  min-height: 560px;
}

.teacher-radar-wrap {
  position: relative;
  width: 360px;
  height: 360px;
  margin: 18px auto 0;
}

.teacher-radar-wrap svg {
  width: 300px;
  height: 300px;
  margin: 28px 30px;
}

.teacher-radar-ring,
.teacher-radar-axis {
  fill: none;
  stroke: #dce7ed;
  stroke-width: 1;
}

.teacher-radar-school {
  fill: rgba(84, 188, 178, 0.06);
  stroke: #35b5ab;
  stroke-dasharray: 5 6;
  stroke-width: 2;
}

.teacher-radar-area {
  fill: rgba(8, 135, 127, 0.16);
  stroke: #07887f;
  stroke-width: 3;
}

.teacher-radar-label {
  position: absolute;
  display: grid;
  min-width: 76px;
  color: #273951;
  text-align: center;
  transform: translate(-50%, -50%);
  font-size: 13px;
  font-weight: 850;
}

.teacher-radar-label b {
  margin-top: 4px;
  color: #52677f;
  font-weight: 760;
}

.class-radar-card footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #4f647c;
  font-size: 13px;
  font-weight: 760;
}

.class-radar-card footer span {
  width: 28px;
  height: 3px;
  background: #07887f;
  border-radius: 999px;
}

.class-radar-card footer span.dotted {
  background: repeating-linear-gradient(90deg, #35b5ab 0 4px, transparent 4px 8px);
}

.weak-matrix-card,
.risk-table-card {
  display: grid;
  grid-template-rows: 64px 42px repeat(8, 42px) 48px;
  min-height: 560px;
}

.weak-row,
.risk-row {
  display: grid;
  align-items: center;
  gap: 12px;
  min-width: 0;
  padding: 0 22px;
  border-top: 1px solid #edf2f5;
  color: #293d55;
  font-size: 13px;
  font-weight: 760;
}

.weak-row {
  grid-template-columns: minmax(170px, 1fr) 150px 96px 162px;
}

.risk-row {
  grid-template-columns: 88px minmax(120px, 0.82fr) minmax(160px, 1.1fr) 120px;
}

.weak-head,
.risk-head {
  color: #748498;
  background: #f8fbfc;
  font-size: 12px;
  font-weight: 900;
}

.weak-row strong,
.weak-row span,
.risk-row span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.weak-progress {
  display: grid;
  grid-template-columns: minmax(70px, 1fr) 42px;
  align-items: center;
  gap: 8px;
}

.weak-progress i {
  height: 8px;
  overflow: hidden;
  background: #edf2f4;
  border-radius: 999px;
}

.weak-progress b {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, #f05d5a, #f7a03a, #29afa5);
  border-radius: inherit;
}

.risk-row b {
  display: inline-grid;
  width: 22px;
  height: 22px;
  margin-right: 8px;
  place-items: center;
  color: #ffffff;
  background: #08887f;
  border-radius: 50%;
  font-size: 12px;
}

.risk-row.focus {
  background: #effbf9;
}

.weak-matrix-card footer,
.risk-table-card footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 22px;
  color: #617388;
  font-size: 13px;
  font-weight: 760;
}

.weak-matrix-card footer button,
.risk-table-card footer button {
  color: #07847b;
  background: transparent;
  border: 0;
  cursor: pointer;
  font-weight: 850;
}

.evidence-stream-section {
  min-height: 340px;
}

.evidence-stream-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 20px;
  padding: 0 22px 22px;
}

.evidence-stream-card {
  display: grid;
  align-content: start;
  min-height: 240px;
  padding: 22px;
  border: 1px solid #dbe8ee;
  border-radius: 10px;
}

.evidence-stream-card header {
  display: grid;
  grid-template-columns: 30px minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
}

.evidence-stream-card header span {
  display: grid;
  width: 28px;
  height: 28px;
  place-items: center;
  color: #07847b;
  background: #e8f8f6;
  border-radius: 7px;
}

.evidence-stream-card strong {
  color: #1c304a;
  font-weight: 900;
}

.evidence-stream-card p,
.evidence-stream-card small {
  margin: 0 0 16px;
  overflow: hidden;
  color: #30435c;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
  font-weight: 760;
}

@media (max-width: 1500px) {
  .class-profile-filterbar,
  .class-profile-main-grid,
  .class-profile-kpis,
  .evidence-stream-grid {
    grid-template-columns: 1fr;
  }
}

.class-profile-estimate-banner {
  margin: 0 0 14px;
  padding: 10px 16px;
  border-radius: 10px;
  background: rgba(236, 133, 0, 0.1);
  color: #b3681a;
  font-size: 13px;
  font-weight: 600;
}
</style>
