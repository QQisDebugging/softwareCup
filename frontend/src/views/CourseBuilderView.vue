<script setup lang="ts">
import {
  BookOpenCheck,
  CheckCircle2,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Eye,
  FileArchive,
  FileText,
  FileUp,
  GripVertical,
  MoreVertical,
  Pencil,
  Plus,
  RefreshCw,
  Route,
  Save,
  Send,
  Sparkles,
  Trash2,
  UploadCloud,
  WandSparkles,
  X,
} from 'lucide-vue-next'
import { computed, onMounted, reactive, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { agentsApi, coursesApi, uploadsApi } from '@/api'
import ErrorNotice from '@/components/ErrorNotice.vue'
import LoadingBlock from '@/components/LoadingBlock.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import StatusPill from '@/components/StatusPill.vue'
import { useAppStore } from '@/stores/app'
import type { Course, CreateCourseRequest, UploadAsset } from '@/types/api'
import { cleanDisplayText, compact, formatDate, isRecord, parseMaybeJson } from '@/utils/format'

interface ImportedCourseFile {
  id: string
  name: string
  size: number
  extension: string
  kind: string
  status: string
  parseMessage: string
  preview: string
  knowledgePoints: string[]
  draft: Record<string, unknown>
  asset?: UploadAsset
}

interface CourseBuildTemplate {
  title: string
  titleTemplate: string
  departmentTemplate: string
  descriptionTemplate: string
  creditHours: number
  knowledgePoints: string[]
  weeks: Array<{ week: number; topic: string }>
  usageHint: string
}

type CourseSourceKey = 'classroom' | 'self'
type TeacherCheckStatus = '通过' | '部分未通过' | '待检查'
type Tone = 'ok' | 'warn' | 'danger' | 'info' | 'muted'

interface TeacherMaterialFile {
  id: string
  name: string
  type: string
  status: string
  sizeMb: string
  progress?: number
}

interface TeacherChapterNode {
  id: string
  title: string
  expanded: boolean
  children: Array<{ id: string; title: string }>
}

interface TeacherKnowledgeRow {
  id: string
  chapterId: string
  name: string
  objective: string
  hours: string
}

type TeacherStructureDrawerMode = 'chapter' | 'knowledge'

interface TeacherStructureDraft {
  open: boolean
  mode: TeacherStructureDrawerMode
  editingId: string
  title: string
  name: string
  objective: string
  hours: string
  sectionTitle: string
}

interface TeacherVisibleClass {
  id: string
  name: string
  studentCount: number
  enabled: boolean
}

const app = useAppStore()
const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const uploading = ref(false)
const error = ref('')
const courses = ref<Course[]>([])
const selectedCourse = ref<Course | null>(null)
const uploadInput = ref<HTMLInputElement | null>(null)
const importedFiles = ref<ImportedCourseFile[]>([])
const newKnowledgePoint = ref('')
const activeCourseTemplateTitle = ref('资料导入课程')
const activeCourseSource = ref<CourseSourceKey>('self')
const teacherUploadInput = ref<HTMLInputElement | null>(null)
const teacherBuilderStep = ref(3)
const teacherMaterialTypeFilter = ref('全部类型')
const teacherMaterialStatusFilter = ref('全部状态')
const teacherSelectedChapterId = ref('chapter-1')
const teacherOpenMaterialMenu = ref('')
const teacherKnowledgePage = ref(1)
const teacherLastSaved = ref('今天 14:32')
const teacherDraftVersion = ref('v0.7')
const teacherNotice = ref('')
const teacherSaving = ref(false)
const teacherStructureLoading = ref(false)
const teacherStructureResult = ref<Record<string, unknown> | null>(null)
const teacherStructureArtifactId = ref('')
const teacherDiagnosticArtifactId = ref('')
const teacherStructureDraft = reactive<TeacherStructureDraft>({
  open: false,
  mode: 'chapter',
  editingId: '',
  title: '新增章节',
  name: '',
  objective: '',
  hours: '0.5',
  sectionTitle: '',
})

const form = reactive({
  title: '自定义课程',
  department: '课程空间',
  description: '上传 PPT、教材、讲义或题库后，系统会抽取知识点并生成可保存、可切换、可用于资源生成的课程结构。',
  creditHours: 32,
  syllabusJson: JSON.stringify(
    {
      source: 'course_builder',
      courseSource: 'self_upload',
      courseMode: 'personal_course',
      knowledgePoints: ['课程目标', '核心知识点', '练习与反馈'],
      weeks: [
        { week: 1, topic: '课程导入与资料梳理' },
        { week: 2, topic: '核心知识点学习' },
        { week: 3, topic: '练习反馈与学习评估' },
      ],
    },
    null,
    2,
  ),
})

const isTeacher = computed(() => app.role === 'teacher')
const teacherMaterialFiles = ref<TeacherMaterialFile[]>([])
const teacherChapterTree = ref<TeacherChapterNode[]>([
  { id: 'chapter-1', title: '第 1 章 课程导论', expanded: true, children: [] },
  {
    id: 'chapter-2',
    title: '第 2 章 Java Web 基础',
    expanded: true,
    children: [
      { id: 'section-2-1', title: '2.1 HTML 语法' },
      { id: 'section-2-2', title: '2.2 CSS 样式' },
      { id: 'section-2-3', title: '2.3 JavaScript 基础' },
    ],
  },
  {
    id: 'chapter-3',
    title: '第 3 章 Servlet 技术',
    expanded: true,
    children: [
      { id: 'section-3-1', title: '3.1 Servlet 概述' },
      { id: 'section-3-2', title: '3.2 请求与响应' },
      { id: 'section-3-3', title: '3.3 会话管理' },
    ],
  },
  {
    id: 'chapter-4',
    title: '第 4 章 JSP 技术',
    expanded: true,
    children: [
      { id: 'section-4-1', title: '4.1 JSP 基础语法' },
      { id: 'section-4-2', title: '4.2 内置对象' },
      { id: 'section-4-3', title: '4.3 表单处理' },
    ],
  },
  {
    id: 'chapter-5',
    title: '第 5 章 数据访问技术',
    expanded: true,
    children: [
      { id: 'section-5-1', title: '5.1 JDBC 基础' },
      { id: 'section-5-2', title: '5.2 连接池' },
      { id: 'section-5-3', title: '5.3 DAO 模式' },
    ],
  },
])
const teacherKnowledgeRows = ref<TeacherKnowledgeRow[]>([
  { id: 'kp-1', chapterId: 'chapter-1', name: '课程背景与目标', objective: '理解课程定位与学习目标', hours: '0.5' },
  { id: 'kp-2', chapterId: 'chapter-1', name: 'Web 应用技术发展历程', objective: '了解 Web 技术演进与趋势', hours: '0.5' },
  { id: 'kp-3', chapterId: 'chapter-1', name: '课程内容与学习路径', objective: '明确课程结构与学习路径', hours: '0.5' },
  { id: 'kp-4', chapterId: 'chapter-1', name: '开发环境与工具介绍', objective: '掌握开发工具与环境配置', hours: '0.5' },
  { id: 'kp-5', chapterId: 'chapter-1', name: '项目案例概览', objective: '了解项目案例与应用场景', hours: '0.5' },
  { id: 'kp-6', chapterId: 'chapter-1', name: '考核方式与评分标准', objective: '理解考核方式与评分细则', hours: '0.5' },
])
const teacherVisibleClasses = ref<TeacherVisibleClass[]>([
  { id: 'class-1', name: '软件工程 2024-01', studentCount: 52, enabled: true },
])
const teacherLearningObjectives = ref([
  '掌握 Java Web 开发的核心技术与原理',
  '能够使用 Servlet、JSP 完成 Web 应用开发',
  '掌握数据库访问与业务逻辑实现方法',
  '具备完成中小型 Web 项目开发的能力',
])
const teacherPublishChecks = ref<Array<{ label: string; status: TeacherCheckStatus; issueCount?: number }>>([
  { label: '章节结构完整性', status: '通过' },
  { label: '知识点覆盖度', status: '通过' },
  { label: '资源槽位完整性', status: '部分未通过', issueCount: 6 },
  { label: '学习目标一致性', status: '通过' },
  { label: '敏感内容检测', status: '通过' },
])
const teacherMaterialTypeOptions = ['全部类型', 'PDF', 'PPT', 'DOCX', 'ZIP']
const teacherMaterialStatusOptions = ['全部状态', '已解析', '解析中', '待处理']
const teacherFilteredMaterials = computed(() =>
  teacherMaterialFiles.value.filter((file) => {
    const typeMatch = teacherMaterialTypeFilter.value === '全部类型' || file.type === teacherMaterialTypeFilter.value
    const statusMatch = teacherMaterialStatusFilter.value === '全部状态' || file.status === teacherMaterialStatusFilter.value
    return typeMatch && statusMatch
  }),
)
const teacherActiveChapter = computed(() => teacherChapterTree.value.find((chapter) => chapter.id === teacherSelectedChapterId.value) || teacherChapterTree.value[0])
const teacherVisibleKnowledgeRows = computed(() => teacherKnowledgeRows.value.filter((row) => row.chapterId === teacherActiveChapter.value?.id))
const teacherPagedKnowledgeRows = computed(() => teacherVisibleKnowledgeRows.value.slice((teacherKnowledgePage.value - 1) * 6, teacherKnowledgePage.value * 6))
const teacherResourceSlotStatus = computed(() => ({
  total: 32,
  filled: teacherMaterialFiles.value.filter((file) => file.status === '已解析').length * 9,
  partial: teacherMaterialFiles.value.filter((file) => file.status === '解析中').length * 8,
  missing: Math.max(6, teacherMaterialFiles.value.filter((file) => file.status === '待处理').length * 2),
}))
const teacherPreviewCourse = computed(() => ({
  title: String(teacherStructureResult.value?.suggestedTitle || selectedCourse.value?.title || form.title),
  department: String(teacherStructureResult.value?.suggestedDepartment || selectedCourse.value?.department || form.department),
  chapters: teacherChapterTree.value.length,
  knowledgeCount: teacherKnowledgeRows.value.length,
  slotCount: teacherResourceSlotStatus.value.total,
}))
const courseBuildTemplates: CourseBuildTemplate[] = [
  {
    title: '资料导入课程',
    titleTemplate: '{{资料名称}} 自建课程',
    departmentTemplate: '{{课程归属}}',
    descriptionTemplate: '基于{{资料类型}}资料构建课程空间，沉淀{{学习目标}}、知识点和学习单元，后续资源生成会沿用这套上下文。',
    creditHours: 32,
    knowledgePoints: ['资料导读', '核心概念', '典型问题'],
    weeks: [
      { week: 1, topic: '资料导读与目标确认' },
      { week: 2, topic: '核心知识点拆解' },
      { week: 3, topic: '练习与反馈整理' },
    ],
    usageHint: '适合从 PPT、教材、讲义、题库快速整理一门课。',
  },
  {
    title: '教师班级课程',
    titleTemplate: '{{课程名称}} 班级课程',
    departmentTemplate: '{{课程归属}}',
    descriptionTemplate: '围绕{{学习目标}}组织班级课程结构，包含单元节奏、重点难点、资源生产入口和学习数据回收。',
    creditHours: 48,
    knowledgePoints: ['课程目标', '重点难点', '评价标准'],
    weeks: [
      { week: 1, topic: '课程导入与诊断' },
      { week: 2, topic: '知识讲授与任务推进' },
      { week: 3, topic: '作业反馈与补救学习' },
      { week: 4, topic: '总结评估与学习报告' },
    ],
    usageHint: '适合教师把一门课发布给班级并持续维护。',
  },
  {
    title: '项目实训课程',
    titleTemplate: '{{项目主题}} 实训课程',
    departmentTemplate: '{{课程归属}}',
    descriptionTemplate: '按{{项目主题}}拆分任务、资料、训练目标和成果要求，形成可执行的项目式学习路径。',
    creditHours: 40,
    knowledgePoints: ['项目背景', '任务流程', '成果要求'],
    weeks: [
      { week: 1, topic: '项目背景与资料准备' },
      { week: 2, topic: '任务拆解与方案设计' },
      { week: 3, topic: '实践推进与问题诊断' },
      { week: 4, topic: '成果提交与复盘' },
    ],
    usageHint: '适合实训、课程设计、竞赛训练和专题学习。',
  },
]
const selectedCourseDescription = computed(() =>
  cleanDisplayText(selectedCourse.value?.description || '可以不绑定已有课程，直接把上传资料生成一门新课程。'),
)
const builderTitle = computed(() => (isTeacher.value ? '课程建设' : '自定义课程'))
const courseSpaceLabel = computed(() => (isTeacher.value ? '课程空间' : '我的课程'))
const courseSourceModes = computed(() => [
  {
    key: 'classroom' as const,
    label: isTeacher.value ? '班级发放' : '班级课程',
    title: isTeacher.value ? '发放班级课程' : '加入班级课程',
    desc: isTeacher.value
      ? '选择已有课程或整理课程后发放给班级，学生端只看到已发布内容。'
      : '选择老师已经发放的课程，直接进入学习、答疑和资源使用。',
    status: selectedCourse.value ? selectedCourse.value.title : '待选择课程',
  },
  {
    key: 'self' as const,
    label: isTeacher.value ? '资料导入' : '自建课程',
    title: isTeacher.value ? '导入资料建课' : '上传资料自建课程',
    desc: isTeacher.value
      ? '上传 PPT、教材、讲义或题库，生成教师可维护的课程空间。'
      : '上传 PPT、教材、书本或讲义，生成只属于自己的课程结构。',
    status: importedFiles.value.length ? `${importedFiles.value.length} 个文件` : '待上传资料',
  },
])
const activeCourseSourceMode = computed(
  () => courseSourceModes.value.find((mode) => mode.key === activeCourseSource.value) || courseSourceModes.value[1],
)
const visibleCourseBuildTemplates = computed(() =>
  isTeacher.value ? courseBuildTemplates : courseBuildTemplates.filter((template) => template.title !== '教师班级课程'),
)
const syllabusParseError = computed(() => {
  if (!form.syllabusJson.trim()) return ''
  try {
    JSON.parse(form.syllabusJson)
    return ''
  } catch {
    return '课程结构暂时无法保存，请检查学习单元后再试。'
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
const uploadSummary = computed(() => {
  const totalMb = importedFiles.value.reduce((sum, item) => sum + item.size, 0) / 1024 / 1024
  const kinds = Array.from(new Set(importedFiles.value.map((item) => item.kind))).join('、') || '待上传'
  return `${importedFiles.value.length} 个文件 / ${totalMb.toFixed(1)} MB / ${kinds}`
})
const allKnowledgePoints = computed(() => Array.from(new Set(importedFiles.value.flatMap((item) => item.knowledgePoints))).slice(0, 12))
const parsedSyllabus = computed(() => parseMaybeJson<Record<string, unknown>>(form.syllabusJson, {}))
const syllabusWeeks = computed(() => {
  const weeks = parsedSyllabus.value.weeks
  return Array.isArray(weeks) ? weeks.filter(isRecord).slice(0, 8) : []
})
const previewKnowledgePoints = computed(() => {
  const fromDraft = parsedSyllabus.value.knowledgePoints
  const points = Array.isArray(fromDraft) ? fromDraft.map((item) => String(item)).filter(Boolean) : []
  return Array.from(new Set([...allKnowledgePoints.value, ...points])).slice(0, 12)
})
const courseStructureItems = computed(() => [
  {
    label: '课程名称',
    value: form.title && form.title !== '自定义课程' ? form.title : '待填写课程名称',
  },
  {
    label: '资料类型',
    value: importedFiles.value.length ? Array.from(new Set(importedFiles.value.map((item) => item.kind))).join('、') : 'PPT / 教材 / 讲义 / 题库',
  },
  {
    label: '学习单元',
    value: syllabusWeeks.value.length ? `${syllabusWeeks.value.length} 个学习单元` : '由资料解析或手动添加',
  },
  {
    label: '知识点',
    value: previewKnowledgePoints.value.length ? `${previewKnowledgePoints.value.length} 个知识点` : '由资料解析或手动添加',
  },
])
const buildQualityChecks = computed(() => [
  {
    title: '资料来源',
    value: importedFiles.value.length ? `${importedFiles.value.length} 个文件` : '待上传',
    passed: importedFiles.value.length > 0,
  },
  {
    title: '知识点覆盖',
    value: previewKnowledgePoints.value.length ? `${previewKnowledgePoints.value.length} 个知识点` : '待抽取',
    passed: previewKnowledgePoints.value.length >= 3,
  },
  {
    title: '周次结构',
    value: syllabusWeeks.value.length ? `${syllabusWeeks.value.length} 个学习单元` : '待生成',
    passed: syllabusWeeks.value.length >= 2,
  },
  {
    title: '后续资源上下文',
    value: form.title.trim() && form.description.trim() ? '已准备' : '待完善',
    passed: Boolean(form.title.trim() && form.description.trim()),
  },
])
const buildReadiness = computed(() => buildQualityChecks.value.filter((item) => item.passed).length)
const generationTarget = computed(() => {
  const courseQuery = selectedCourse.value?.id ? `?courseId=${encodeURIComponent(selectedCourse.value.id)}` : ''
  return isTeacher.value ? `/generation${courseQuery}` : `/learning?tab=generate${selectedCourse.value?.id ? `&courseId=${encodeURIComponent(selectedCourse.value.id)}` : ''}`
})
const nextActions = computed(() => [
  {
    title: '保存课程空间',
    desc: canCreateCourse.value ? `保存后会进入${courseSpaceLabel.value}，并作为学习、助教和资源生成的上下文。` : '先补齐课程名称、描述、学时和学习单元。',
    to: '',
    primary: true,
  },
  {
    title: isTeacher.value ? '进入资源审核' : '去 AI 助手生成',
    desc: isTeacher.value ? '基于已保存课程生成并审核班级讲解、题库、导图和课件。' : '基于已保存课程和学习画像生成讲解、题库、导图、实操案例和课件。',
    to: generationTarget.value,
    primary: false,
  },
  {
    title: '查看课程空间',
    desc: `确认课程是否已经进入${courseSpaceLabel.value}，并查看已发布资源。`,
    to: '/courses',
    primary: false,
  },
])
const builderFlowSteps = computed(() => [
  {
    title: activeCourseSource.value === 'classroom' ? '选择班级课程' : '上传资料',
    detail:
      activeCourseSource.value === 'classroom'
        ? selectedCourse.value?.title || '选择老师发放或准备发放的课程'
        : importedFiles.value.length
          ? `${importedFiles.value.length} 个文件已进入资料包`
          : '接收 PPT、教材、讲义和题库',
    icon: activeCourseSource.value === 'classroom' ? BookOpenCheck : UploadCloud,
  },
  {
    title: '抽取知识点',
    detail: previewKnowledgePoints.value.length ? `${previewKnowledgePoints.value.length} 个知识点进入大纲` : '解析正文、章节和题目线索',
    icon: BookOpenCheck,
  },
  {
    title: '保存课程',
    detail: canCreateCourse.value ? '课程草稿可保存为课程空间' : '补齐名称、描述、学时和单元',
    icon: Save,
  },
  {
    title: isTeacher.value ? '审核资源' : 'AI 生成资源',
    detail: isTeacher.value ? '进入教师资源审核页生产并发布课程资源' : '在 AI 助手里生产讲解、题库、导图和实操案例',
    icon: Sparkles,
  },
])
const courseStats = computed(() => [
  { label: '课程来源', value: activeCourseSourceMode.value.label, detail: activeCourseSourceMode.value.status },
  { label: '已有课程', value: courses.value.length, detail: selectedCourse.value?.title || '可选择一个课程作为资料归属' },
  { label: '上传资料', value: importedFiles.value.length, detail: uploadSummary.value },
  { label: '抽取知识点', value: previewKnowledgePoints.value.length, detail: '进入课程大纲和后续资源生成上下文' },
])
const courseSwitchCards = computed(() =>
  courses.value.map((course) => ({
    ...course,
    active: course.id === selectedCourse.value?.id,
    descriptionText: cleanDisplayText(course.description),
  })),
)

function currentSyllabusObject() {
  const parsed = parseMaybeJson<Record<string, unknown>>(form.syllabusJson, {})
  return isRecord(parsed) ? parsed : {}
}

function writeSyllabus(next: Record<string, unknown>) {
  form.syllabusJson = JSON.stringify(next, null, 2)
}

function renderCourseTemplate(value: string) {
  const firstFileName = importedFiles.value[0]?.name.replace(/\.[^.]+$/, '') || selectedCourse.value?.title || '课程资料'
  const materialTypes = importedFiles.value.length
    ? Array.from(new Set(importedFiles.value.map((item) => item.kind))).join('、')
    : 'PPT、教材、讲义或题库'
  const ownership = isTeacher.value ? '教师课程空间' : '学生个人课程'
  return value
    .replaceAll('{{资料名称}}', firstFileName)
    .replaceAll('{{课程名称}}', form.title && form.title !== '自定义课程' ? form.title : firstFileName)
    .replaceAll('{{项目主题}}', firstFileName)
    .replaceAll('{{资料类型}}', materialTypes)
    .replaceAll('{{课程归属}}', ownership)
    .replaceAll('{{学习目标}}', '学习目标')
}

function applyCourseTemplate(template: CourseBuildTemplate) {
  activeCourseSource.value = template.title === '教师班级课程' ? 'classroom' : 'self'
  activeCourseTemplateTitle.value = template.title
  form.title = renderCourseTemplate(template.titleTemplate)
  form.department = renderCourseTemplate(template.departmentTemplate)
  form.description = renderCourseTemplate(template.descriptionTemplate)
  form.creditHours = template.creditHours
  writeSyllabus({
    source: 'course_builder_plan',
    courseSource: activeCourseSource.value === 'classroom' ? 'classroom_assigned' : 'self_upload',
    courseMode: isTeacher.value ? 'class_course' : 'personal_course',
    plan: template.title,
    files: importedFiles.value.map((item) => ({
      assetId: item.asset?.id,
      name: item.name,
      kind: item.kind,
      size: item.size,
      status: item.status,
      parseMessage: item.parseMessage,
      knowledgePoints: item.knowledgePoints,
    })),
    knowledgePoints: template.knowledgePoints.map((point) => renderCourseTemplate(point)),
    weeks: template.weeks.map((week) => ({ ...week, topic: renderCourseTemplate(week.topic) })),
  })
  error.value = ''
}

function updateSyllabusWeek(index: number, topic: string) {
  const current = currentSyllabusObject()
  const weeks = Array.isArray(current.weeks) ? current.weeks.filter(isRecord) : []
  weeks[index] = {
    ...(weeks[index] || {}),
    week: Number(weeks[index]?.week || index + 1),
    topic,
  }
  writeSyllabus({ ...current, weeks })
}

function addSyllabusWeek() {
  const current = currentSyllabusObject()
  const weeks = Array.isArray(current.weeks) ? current.weeks.filter(isRecord) : []
  weeks.push({ week: weeks.length + 1, topic: `学习单元 ${weeks.length + 1}` })
  writeSyllabus({ ...current, weeks })
}

function removeSyllabusWeek(index: number) {
  const current = currentSyllabusObject()
  const weeks = (Array.isArray(current.weeks) ? current.weeks.filter(isRecord) : [])
    .filter((_, itemIndex) => itemIndex !== index)
    .map((item, itemIndex) => ({ ...item, week: itemIndex + 1 }))
  writeSyllabus({ ...current, weeks })
}

function addKnowledgePoint() {
  const point = newKnowledgePoint.value.trim()
  if (!point) return
  const current = currentSyllabusObject()
  const points = Array.isArray(current.knowledgePoints) ? current.knowledgePoints.map((item) => String(item)).filter(Boolean) : []
  writeSyllabus({ ...current, knowledgePoints: Array.from(new Set([...points, point])) })
  newKnowledgePoint.value = ''
}

function removeKnowledgePoint(point: string) {
  const current = currentSyllabusObject()
  const points = Array.isArray(current.knowledgePoints) ? current.knowledgePoints.map((item) => String(item)).filter(Boolean) : []
  writeSyllabus({ ...current, knowledgePoints: points.filter((item) => item !== point) })
}

async function loadCourses() {
  loading.value = true
  error.value = ''
  try {
    courses.value = await coursesApi.list()
    selectedCourse.value = courses.value.find((course) => course.id === app.activeCourseId) || courses.value[0] || null
  } catch (err) {
    error.value = err instanceof Error ? err.message : '课程加载失败'
  } finally {
    loading.value = false
  }
}

async function loadTeacherMaterials() {
  if (!isTeacher.value) return
  try {
    const assets = await uploadsApi.listCourseMaterials(selectedCourse.value?.id)
    teacherMaterialFiles.value = assets.filter((asset) => asset.uploaderRole === 'teacher').map((asset) => teacherMaterialFromUpload(asset))
  } catch (err) {
    error.value = err instanceof Error ? err.message : '教师资料池加载失败'
  }
}

function selectCourse(course: Course) {
  activeCourseSource.value = 'classroom'
  selectedCourse.value = course
  app.setActiveCourse(course.id)
  void loadTeacherMaterials()
}

function fileKind(name: string) {
  const ext = name.split('.').pop()?.toLowerCase() || ''
  if (['ppt', 'pptx'].includes(ext)) return '课件'
  if (['pdf', 'epub'].includes(ext)) return '教材'
  if (['doc', 'docx', 'md', 'txt'].includes(ext)) return '讲义'
  if (['xls', 'xlsx', 'csv'].includes(ext)) return '题库'
  return '资料'
}

function normalizeImportedAsset(asset: UploadAsset): ImportedCourseFile {
  const knowledgePoints = parseMaybeJson<string[]>(asset.knowledgePointsJson, [])
  const draft = parseMaybeJson<Record<string, unknown>>(asset.courseDraftJson, {})
  return {
    id: asset.id,
    name: asset.originalFilename,
    size: asset.sizeBytes,
    extension: asset.originalFilename.split('.').pop()?.toUpperCase() || 'FILE',
    kind: fileKind(asset.originalFilename),
    status: asset.parseStatus === 'ANALYZED' ? '已解析' : asset.parseStatus === 'METADATA_ONLY' ? '已保存' : asset.parseStatus,
    parseMessage: asset.parseMessage,
    preview: asset.extractedTextPreview,
    knowledgePoints: Array.isArray(knowledgePoints) ? knowledgePoints : [],
    draft: isRecord(draft) ? draft : {},
    asset,
  }
}

function localDraftForFile(file: File): Record<string, unknown> {
  const name = file.name.replace(/\.[^.]+$/, '')
  const kind = fileKind(file.name)
  return {
    source: isTeacher.value ? 'teacher_material_import' : 'student_self_course_upload',
    sourceFile: file.name,
    materialType: kind,
    suggestedTitle: `${name} 自建课程`,
    suggestedDepartment: isTeacher.value ? '课程教师导入' : '学生个人课程',
    suggestedCreditHours: 16,
    suggestedDescription: `基于 ${file.name} 构建课程资料包，可继续用于画像诊断、资源生成、路径规划、智能答疑和学习评估。`,
    knowledgePoints: [name],
    weeks: [{ week: 1, topic: name }],
  }
}

async function addFiles(fileList: FileList | File[]) {
  const files = Array.from(fileList)
  if (!files.length) return
  activeCourseSource.value = 'self'
  uploading.value = true
  const placeholders = files.map((file) => ({
    id: `${file.name}-${file.size}-${file.lastModified}-${Math.random().toString(36).slice(2)}`,
    name: file.name,
    size: file.size,
    extension: file.name.split('.').pop()?.toUpperCase() || 'FILE',
    kind: fileKind(file.name),
    status: '上传中',
    parseMessage: '正在保存资料并抽取知识点。',
    preview: '',
    knowledgePoints: [],
    draft: localDraftForFile(file),
  }))
  importedFiles.value = [...importedFiles.value, ...placeholders]
  try {
    await Promise.all(
      files.map(async (file, index) => {
        const placeholderId = placeholders[index].id
        try {
          const asset = await uploadsApi.uploadCourseMaterial(file, {
            courseId: selectedCourse.value?.id || app.activeCourseId,
            role: app.role,
          })
          const parsed = normalizeImportedAsset(asset)
          importedFiles.value = importedFiles.value.map((item) => (item.id === placeholderId ? parsed : item))
        } catch (err) {
          const message = err instanceof Error ? err.message : '资料暂未同步，已生成课程草稿。'
          importedFiles.value = importedFiles.value.map((item) =>
            item.id === placeholderId
              ? {
                  ...item,
                  status: '草稿待同步',
                  parseMessage: message,
                  knowledgePoints: [file.name.replace(/\.[^.]+$/, '')],
                  draft: localDraftForFile(file),
                }
              : item,
          )
          error.value = message
        }
      }),
    )
  } finally {
    uploading.value = false
    if (uploadInput.value) uploadInput.value.value = ''
  }
}

function removeImportedFile(fileId: string) {
  importedFiles.value = importedFiles.value.filter((item) => item.id !== fileId)
}

function applyUploadDraft() {
  if (!importedFiles.value.length) {
    error.value = '请先上传 PPT、教材或讲义，再生成课程草稿。'
    return
  }
  activeCourseSource.value = 'self'
  const draft = importedFiles.value.find((item) => Object.keys(item.draft).length)?.draft || {}
  const baseName = importedFiles.value[0].name.replace(/\.[^.]+$/, '')
  const kinds = Array.from(new Set(importedFiles.value.map((item) => item.kind)))
  form.title = String(draft.suggestedTitle || `${baseName} 自建课程`)
  form.department = String(draft.suggestedDepartment || (isTeacher.value ? '课程教师导入' : '学生个人课程'))
  form.description = String(
    draft.suggestedDescription ||
      `基于 ${importedFiles.value.map((item) => item.name).join('、')} 构建课程知识库，覆盖${kinds.join('、')}等资料，可用于画像诊断、资源生成、学习路径规划和智能答疑。`,
  )
  form.creditHours = Number(draft.suggestedCreditHours || Math.max(Number(form.creditHours) || 16, importedFiles.value.length * 8))
  form.syllabusJson = JSON.stringify(
    {
      source: isTeacher.value ? 'teacher_import' : 'student_upload',
      courseSource: 'self_upload',
      courseMode: isTeacher.value ? 'class_course' : 'personal_course',
      files: importedFiles.value.map((item) => ({
        assetId: item.asset?.id,
        name: item.name,
        kind: item.kind,
        size: item.size,
        status: item.status,
        parseMessage: item.parseMessage,
        knowledgePoints: item.knowledgePoints,
      })),
      knowledgePoints: allKnowledgePoints.value,
      textPreview: importedFiles.value.map((item) => item.preview).filter(Boolean).join('\n\n').slice(0, 1600),
      courseContext: ['资料上传', '正文解析', '知识点抽取', '画像匹配', '资源生成', '安全审核', '学习推送'],
      weeks: Array.isArray(draft.weeks) && draft.weeks.length
        ? draft.weeks
        : importedFiles.value.slice(0, 8).map((item, index) => ({
            week: index + 1,
            topic: `${item.kind}精读：${item.name.replace(/\.[^.]+$/, '')}`,
          })),
    },
    null,
    2,
  )
  activeCourseTemplateTitle.value = '资料导入课程'
  error.value = ''
}

function teacherMaterialStatusTone(status: string): Tone {
  if (status === '已解析') return 'ok'
  if (status === '解析中') return 'info'
  if (status === '待处理') return 'warn'
  return 'muted'
}

function teacherMaterialFromUpload(asset: UploadAsset): TeacherMaterialFile {
  const status = asset.parseStatus === 'ANALYZED' ? '已解析' : asset.parseStatus === 'STORED' ? '待处理' : '解析中'
  return {
    id: asset.id,
    name: asset.originalFilename,
    type: asset.materialType || asset.originalFilename.split('.').pop()?.toUpperCase() || 'FILE',
    status,
    sizeMb: `${(Number(asset.sizeBytes || 0) / 1024 / 1024).toFixed(1)} MB`,
  }
}

function teacherCheckStatus(value: unknown): TeacherCheckStatus {
  const text = String(value || '').toLowerCase()
  if (text.includes('pass') || text.includes('通过')) return '通过'
  if (text.includes('warn') || text.includes('partial') || text.includes('部分')) return '部分未通过'
  return '待检查'
}

function asRecordArray(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value) ? value.filter((item): item is Record<string, unknown> => isRecord(item)) : []
}

function applyTeacherStructureResponse(response: Record<string, unknown>) {
  teacherStructureResult.value = response
  const chapters = asRecordArray(response.chapters)
  if (chapters.length) {
    teacherChapterTree.value = chapters.map((chapter, index) => ({
      id: String(chapter.id || `chapter-${index + 1}`),
      title: String(chapter.title || `第 ${index + 1} 章`),
      expanded: true,
      children: (Array.isArray(chapter.sections) ? chapter.sections : []).map((section, sectionIndex) => ({
        id: `section-${index + 1}-${sectionIndex + 1}`,
        title: String(section),
      })),
    }))
    teacherSelectedChapterId.value = teacherChapterTree.value[0]?.id || ''
  }
  const knowledgePoints = asRecordArray(response.knowledgePoints)
  if (knowledgePoints.length) {
    teacherKnowledgeRows.value = knowledgePoints.map((point, index) => ({
      id: String(point.id || `kp-${index + 1}`),
      chapterId: String(point.chapterId || teacherChapterTree.value[0]?.id || 'chapter-1'),
      name: String(point.name || `知识点 ${index + 1}`),
      objective: String(point.objective || '由 AI 结构建议生成，等待教师复核。'),
      hours: String(point.hours || '1'),
    }))
  }
  const objectives = Array.isArray(response.learningObjectives) ? response.learningObjectives.map(String).filter(Boolean) : []
  if (objectives.length) teacherLearningObjectives.value = objectives
  const checks = asRecordArray(response.publishChecks)
  if (checks.length) {
    teacherPublishChecks.value = checks.map((check) => ({
      label: String(check.label || '发布检查'),
      status: teacherCheckStatus(check.status),
      issueCount: Number(check.issueCount || 0) || undefined,
    }))
  }
}

function teacherTriggerUpload() {
  teacherUploadInput.value?.click()
}

async function handleTeacherUpload(fileList: FileList | File[]) {
  const files = Array.from(fileList)
  if (!files.length) return
  uploading.value = true
  error.value = ''
  try {
    const uploaded = await Promise.all(
      files.map((file) => uploadsApi.uploadCourseMaterial(file, { courseId: selectedCourse.value?.id, role: 'teacher' })),
    )
    teacherMaterialFiles.value = [
      ...uploaded.map((asset) => teacherMaterialFromUpload(asset)),
      ...teacherMaterialFiles.value,
    ]
    teacherBuilderStep.value = Math.max(teacherBuilderStep.value, 2)
    teacherNotice.value = `已上传 ${uploaded.length} 个资料文件，解析结果来自后端课程素材接口。`
  } catch (err) {
    error.value = err instanceof Error ? err.message : '教师资料上传失败'
  } finally {
    uploading.value = false
    if (teacherUploadInput.value) teacherUploadInput.value.value = ''
  }
}

async function handleTeacherMaterialAction(file: TeacherMaterialFile, action: 'parsed' | 'reparse' | 'remove') {
  teacherOpenMaterialMenu.value = ''
  error.value = ''
  try {
    if (action === 'remove') {
      await uploadsApi.deleteCourseMaterial(file.id)
      teacherMaterialFiles.value = teacherMaterialFiles.value.filter((item) => item.id !== file.id)
      teacherNotice.value = `已从后端资料池移除 ${file.name}`
    } else if (action === 'reparse') {
      const reparsed = await uploadsApi.reparseCourseMaterial(file.id)
      teacherMaterialFiles.value = teacherMaterialFiles.value.map((item) => (item.id === file.id ? teacherMaterialFromUpload(reparsed) : item))
      teacherNotice.value = `${file.name} 已重新解析，解析结果来自后端课程素材接口。`
    } else {
      teacherNotice.value = `解析状态来自后端上传结果，不能手动标记 ${file.name} 为已解析。`
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '教师资料操作失败'
  }
}

async function clearTeacherParsedMaterials() {
  const parsedFiles = teacherMaterialFiles.value.filter((file) => file.status === '已解析')
  if (!parsedFiles.length) {
    teacherNotice.value = '当前没有已解析资料可清空。'
    return
  }
  error.value = ''
  try {
    await Promise.all(parsedFiles.map((file) => uploadsApi.deleteCourseMaterial(file.id)))
    teacherMaterialFiles.value = teacherMaterialFiles.value.filter((file) => file.status !== '已解析')
    teacherNotice.value = `已从后端资料池清空 ${parsedFiles.length} 个已解析资料。`
  } catch (err) {
    error.value = err instanceof Error ? err.message : '清空已解析资料失败'
  }
}

function toggleTeacherChapter(chapterId: string) {
  teacherChapterTree.value = teacherChapterTree.value.map((chapter) => (chapter.id === chapterId ? { ...chapter, expanded: !chapter.expanded } : chapter))
}

function selectTeacherChapter(chapterId: string) {
  teacherSelectedChapterId.value = chapterId
  teacherKnowledgePage.value = 1
}

function resetTeacherStructureDraft(next: Partial<TeacherStructureDraft>) {
  Object.assign(teacherStructureDraft, {
    open: true,
    mode: 'chapter',
    editingId: '',
    title: '新增章节',
    name: '',
    objective: '',
    hours: '0.5',
    sectionTitle: '',
    ...next,
  })
}

function addTeacherChapter() {
  const index = teacherChapterTree.value.length + 1
  resetTeacherStructureDraft({
    mode: 'chapter',
    title: '新增章节',
    name: `第 ${index} 章 新建章节`,
    objective: '补充本章教学目标、章节定位与评价要求',
    sectionTitle: '',
  })
}

function removeTeacherChapter() {
  if (!teacherActiveChapter.value || teacherChapterTree.value.length <= 1) return
  const chapterId = teacherActiveChapter.value.id
  teacherChapterTree.value = teacherChapterTree.value.filter((chapter) => chapter.id !== chapterId)
  teacherKnowledgeRows.value = teacherKnowledgeRows.value.filter((row) => row.chapterId !== chapterId)
  teacherSelectedChapterId.value = teacherChapterTree.value[0]?.id || ''
  teacherNotice.value = '已删除当前章节及其知识点。'
}

function addTeacherKnowledge() {
  if (!teacherActiveChapter.value) return
  const index = teacherVisibleKnowledgeRows.value.length + 1
  resetTeacherStructureDraft({
    mode: 'knowledge',
    title: '新增知识点',
    name: `新建知识点 ${index}`,
    objective: '补充教学目标与评价要求',
    hours: '0.5',
  })
}

function editTeacherKnowledge(row: TeacherKnowledgeRow) {
  resetTeacherStructureDraft({
    mode: 'knowledge',
    editingId: row.id,
    title: '编辑知识点',
    name: row.name,
    objective: row.objective,
    hours: row.hours,
  })
}

function deleteTeacherKnowledge(rowId: string) {
  teacherKnowledgeRows.value = teacherKnowledgeRows.value.filter((row) => row.id !== rowId)
  const maxPage = Math.max(1, Math.ceil(teacherVisibleKnowledgeRows.value.length / 6))
  teacherKnowledgePage.value = Math.min(teacherKnowledgePage.value, maxPage)
  teacherNotice.value = '已删除知识点。'
}

function moveTeacherKnowledge(rowId: string, direction: -1 | 1) {
  const rows = [...teacherKnowledgeRows.value]
  const index = rows.findIndex((row) => row.id === rowId)
  if (index < 0) return
  const chapterId = rows[index].chapterId
  const chapterRows = rows.filter((row) => row.chapterId === chapterId)
  const chapterIndex = chapterRows.findIndex((row) => row.id === rowId)
  const targetChapterIndex = chapterIndex + direction
  if (targetChapterIndex < 0 || targetChapterIndex >= chapterRows.length) return
  const targetId = chapterRows[targetChapterIndex].id
  const targetIndex = rows.findIndex((row) => row.id === targetId)
  ;[rows[index], rows[targetIndex]] = [rows[targetIndex], rows[index]]
  teacherKnowledgeRows.value = rows
}

function closeTeacherStructureDraft() {
  teacherStructureDraft.open = false
}

function saveTeacherStructureDraft() {
  const name = teacherStructureDraft.name.trim()
  if (!name) {
    teacherNotice.value = teacherStructureDraft.mode === 'chapter' ? '请先填写章节名称。' : '请先填写知识点名称。'
    return
  }
  if (teacherStructureDraft.mode === 'chapter') {
    const chapter: TeacherChapterNode = {
      id: `chapter-${Date.now()}`,
      title: name,
      expanded: true,
      children: teacherStructureDraft.sectionTitle.trim()
        ? [{ id: `section-${Date.now()}`, title: teacherStructureDraft.sectionTitle.trim() }]
        : [],
    }
    teacherChapterTree.value = [...teacherChapterTree.value, chapter]
    teacherSelectedChapterId.value = chapter.id
    teacherKnowledgePage.value = 1
    teacherNotice.value = '已保存新章节，并定位到该章节。'
  } else if (teacherStructureDraft.editingId) {
    const hours = String(teacherStructureDraft.hours || '').trim() || '0.5'
    teacherKnowledgeRows.value = teacherKnowledgeRows.value.map((row) =>
      row.id === teacherStructureDraft.editingId
        ? {
            ...row,
            name,
            objective: teacherStructureDraft.objective.trim() || '补充教学目标与评价要求',
            hours,
          }
        : row,
    )
    teacherNotice.value = `已更新知识点：${name}`
  } else if (teacherActiveChapter.value) {
    const nextCount = teacherVisibleKnowledgeRows.value.length + 1
    const hours = String(teacherStructureDraft.hours || '').trim() || '0.5'
    teacherKnowledgeRows.value = [
      ...teacherKnowledgeRows.value,
      {
        id: `kp-${Date.now()}`,
        chapterId: teacherActiveChapter.value.id,
        name,
        objective: teacherStructureDraft.objective.trim() || '补充教学目标与评价要求',
        hours,
      },
    ]
    teacherKnowledgePage.value = Math.ceil(nextCount / 6)
    teacherNotice.value = `已保存知识点：${name}`
  }
  closeTeacherStructureDraft()
}

async function runTeacherAIStructure() {
  teacherStructureLoading.value = true
  teacherNotice.value = ''
  error.value = ''
  try {
    const response = await agentsApi.invoke('/teaching/course-structures', {
      courseId: selectedCourse.value?.id || undefined,
      courseTitle: teacherPreviewCourse.value.title,
      sourceFile: teacherMaterialFiles.value.map((file) => file.name).join('、'),
      materialType: 'TEACHER_MATERIAL_POOL',
      uploaderRole: 'teacher',
      extractedText: teacherMaterialFiles.value.map((file) => `${file.name}：${file.status}`).join('\n'),
      knownKnowledgePoints: teacherKnowledgeRows.value.map((row) => row.name),
      learningObjectives: teacherLearningObjectives.value,
      existingChapters: teacherChapterTree.value.map((chapter) => chapter.title),
      desiredWeeks: Math.max(1, teacherChapterTree.value.length),
      documentTexts: [
        selectedCourse.value?.description || '',
        selectedCourse.value?.syllabusJson || '',
        teacherMaterialFiles.value.map((file) => `${file.name} ${file.type} ${file.status}`).join('\n'),
      ].filter(Boolean),
    })
    applyTeacherStructureResponse(response)
    teacherBuilderStep.value = 3
    teacherStructureArtifactId.value = String(response.artifactId || '')
    teacherNotice.value = `AI 结构建议已生成${teacherStructureArtifactId.value ? `，artifact=${teacherStructureArtifactId.value}` : ''}。`
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'AI 建议结构生成失败'
  } finally {
    teacherStructureLoading.value = false
  }
}

function importTeacherOutline() {
  teacherBuilderStep.value = Math.max(teacherBuilderStep.value, 3)
  if (!teacherChapterTree.value.some((chapter) => chapter.title.includes('项目综合实战'))) {
    teacherChapterTree.value = [
      ...teacherChapterTree.value,
      { id: `chapter-${Date.now()}`, title: '第 6 章 项目综合实战', expanded: true, children: [{ id: `section-${Date.now()}`, title: '6.1 项目设计与提交' }] },
    ]
  }
  teacherNotice.value = '已导入外部大纲并追加项目综合实战章节。'
}

function buildTeacherCoursePayload(): CreateCourseRequest {
  const result = teacherStructureResult.value || {}
  const creditHours = Number(result.suggestedCreditHours || selectedCourse.value?.creditHours || form.creditHours || 48)
  return {
    title: String(result.suggestedTitle || teacherPreviewCourse.value.title || form.title),
    department: String(result.suggestedDepartment || teacherPreviewCourse.value.department || form.department),
    description: String(result.suggestedDescription || selectedCourse.value?.description || form.description),
    creditHours: Number.isFinite(creditHours) ? creditHours : 48,
    syllabusJson: JSON.stringify(
      {
        source: 'teacher_course_builder',
        structureArtifactId: teacherStructureArtifactId.value,
        diagnosticArtifactId: teacherDiagnosticArtifactId.value,
        aiProvider: result.provider || '',
        aiModel: result.model || '',
        executionMode: result.executionMode || '',
        builderStep: teacherBuilderStep.value,
        chapters: teacherChapterTree.value,
        knowledgePoints: teacherKnowledgeRows.value,
        materials: teacherMaterialFiles.value,
        visibleClasses: teacherVisibleClasses.value.filter((item) => item.enabled),
        learningObjectives: teacherLearningObjectives.value,
        resourceSlotStatus: teacherResourceSlotStatus.value,
        publishChecks: teacherPublishChecks.value,
      },
      null,
      2,
    ),
  }
}

function saveTeacherDraft() {
  const payload = buildTeacherCoursePayload()
  localStorage.setItem('teacher-course-builder-draft', JSON.stringify(payload))
  teacherLastSaved.value = '刚刚'
  const nextVersion = Number(teacherDraftVersion.value.replace('v0.', '')) + 1
  teacherDraftVersion.value = `v0.${Number.isFinite(nextVersion) ? nextVersion : 8}`
  teacherNotice.value = '课程草稿已保存到本地草稿箱。'
}

function previewTeacherStudent() {
  teacherNotice.value = '请先提交发布；发布后可在课程空间查看学生端效果。'
}

async function submitTeacherPublish() {
  teacherSaving.value = true
  teacherNotice.value = ''
  error.value = ''
  try {
    if (!teacherStructureArtifactId.value) {
      await runTeacherAIStructure()
    }
    if (!teacherStructureArtifactId.value) {
      throw new Error('AI 课程结构未生成，不能提交发布检查。')
    }
    if (selectedCourse.value?.id) {
      const diagnostic = await agentsApi.invoke('/teaching/course-diagnostics', {
        courseId: selectedCourse.value.id,
        courseTitle: teacherPreviewCourse.value.title,
        topic: teacherPreviewCourse.value.title,
        syllabusText: JSON.stringify({
          chapters: teacherChapterTree.value,
          knowledgePoints: teacherKnowledgeRows.value,
          objectives: teacherLearningObjectives.value,
        }),
        documentTexts: teacherMaterialFiles.value.map((file) => `${file.name} ${file.status}`),
      })
      teacherDiagnosticArtifactId.value = String(diagnostic.artifactId || '')
    }
    const created = await coursesApi.create(buildTeacherCoursePayload())
    app.setActiveCourse(created.id)
    await app.loadCourses()
    await loadCourses()
    selectedCourse.value = created
    teacherLastSaved.value = '刚刚'
    teacherNotice.value = `课程已通过 AI 结构建议和课程诊断后写入后端课程空间${teacherDiagnosticArtifactId.value ? `，诊断 artifact=${teacherDiagnosticArtifactId.value}` : ''}。`
  } catch (err) {
    error.value = err instanceof Error ? err.message : '课程提交失败'
  } finally {
    teacherSaving.value = false
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
    app.setActiveCourse(created.id)
    await app.loadCourses()
    await loadCourses()
    selectedCourse.value = created
  } catch (err) {
    error.value = err instanceof Error ? err.message : '课程保存失败'
  } finally {
    saving.value = false
  }
}

async function initializeCourseBuilder() {
  await loadCourses()
  await loadTeacherMaterials()
}

onMounted(initializeCourseBuilder)
</script>

<template>
  <div v-if="isTeacher" class="teacher-builder-page" aria-label="教师课程建设">
    <ErrorNotice :message="error" />
    <p v-if="teacherNotice" class="teacher-builder-notice">{{ teacherNotice }}</p>

    <section class="teacher-builder-grid" aria-label="课程建设工作区">
      <aside class="teacher-builder-panel material-pool" aria-label="资料池">
        <header class="teacher-panel-head">
          <div>
            <h2>资料池</h2>
          </div>
        </header>
        <button
          class="teacher-upload-zone"
          type="button"
          @click="teacherTriggerUpload"
          @dragover.prevent
          @drop.prevent="handleTeacherUpload($event.dataTransfer?.files || [])"
        >
          <UploadCloud :size="34" />
          <strong>点击或拖拽文件到此处上传</strong>
          <span>支持 PDF、PPT、DOCX、ZIP，单个文件 <=200MB</span>
          <input
            ref="teacherUploadInput"
            hidden
            multiple
            type="file"
            accept=".pdf,.ppt,.pptx,.doc,.docx,.zip"
            @change="handleTeacherUpload(($event.target as HTMLInputElement).files || [])"
          />
        </button>
        <div class="teacher-filter-row">
          <label>
            <span>类型</span>
            <select v-model="teacherMaterialTypeFilter">
              <option v-for="option in teacherMaterialTypeOptions" :key="option">{{ option }}</option>
            </select>
          </label>
          <label>
            <span>状态</span>
            <select v-model="teacherMaterialStatusFilter">
              <option v-for="option in teacherMaterialStatusOptions" :key="option">{{ option }}</option>
            </select>
          </label>
        </div>
        <div class="teacher-material-table" role="table" aria-label="资料列表">
          <div class="teacher-material-row table-head" role="row">
            <span>文件名</span>
            <span>类型</span>
            <span>状态</span>
            <span>大小</span>
            <span>操作</span>
          </div>
          <div v-for="file in teacherFilteredMaterials" :key="file.id" class="teacher-material-row" role="row">
            <span class="material-name"><FileText :size="15" />{{ file.name }}</span>
            <span>{{ file.type }}</span>
            <span>
              <StatusPill :status="file.status" :tone="teacherMaterialStatusTone(file.status)" />
              <i v-if="file.progress" class="mini-progress"><b :style="{ width: `${file.progress}%` }"></b></i>
            </span>
            <span>{{ file.sizeMb }}</span>
            <span class="material-actions">
              <button class="teacher-icon-button" type="button" @click.stop="teacherOpenMaterialMenu = teacherOpenMaterialMenu === file.id ? '' : file.id">
                <MoreVertical :size="16" />
              </button>
              <menu v-if="teacherOpenMaterialMenu === file.id" class="teacher-row-menu">
                <button type="button" @click="handleTeacherMaterialAction(file, 'parsed')">标记已解析</button>
                <button type="button" @click="handleTeacherMaterialAction(file, 'reparse')">重新解析</button>
                <button type="button" @click="handleTeacherMaterialAction(file, 'remove')">移除文件</button>
              </menu>
            </span>
          </div>
        </div>
        <footer class="teacher-panel-foot">
          <span>共 {{ teacherMaterialFiles.length }} 个文件</span>
          <button type="button" @click="clearTeacherParsedMaterials">清空已完成</button>
        </footer>
      </aside>

      <main class="teacher-builder-panel structure-editor" aria-label="课程结构编辑">
        <header class="teacher-panel-head structure-head">
          <div>
            <h2>课程结构编辑</h2>
          </div>
          <div class="teacher-button-row">
            <button class="teacher-ghost-action" type="button" @click="runTeacherAIStructure"><WandSparkles :size="16" />AI 建议结构</button>
            <button class="teacher-ghost-action" type="button" @click="importTeacherOutline"><FileUp :size="16" />导入大纲</button>
          </div>
        </header>
        <div class="teacher-structure-body">
          <aside class="teacher-chapter-tree">
            <div class="chapter-tree-head">
              <strong>章节树</strong>
              <span>
                <button class="teacher-icon-button" type="button" aria-label="新增章节" @click="addTeacherChapter"><Plus :size="15" /></button>
                <button class="teacher-icon-button" type="button" aria-label="删除当前章节" @click="removeTeacherChapter"><X :size="15" /></button>
              </span>
            </div>
            <button
              v-for="chapter in teacherChapterTree"
              :key="chapter.id"
              type="button"
              class="chapter-node"
              :class="{ active: chapter.id === teacherSelectedChapterId }"
              @click="selectTeacherChapter(chapter.id)"
            >
              <span @click.stop="toggleTeacherChapter(chapter.id)">
                <ChevronDown v-if="chapter.expanded" :size="15" />
                <ChevronRight v-else :size="15" />
              </span>
              <strong>{{ chapter.title }}</strong>
              <template v-if="chapter.expanded">
                <small v-for="child in chapter.children" :key="child.id">
                  <GripVertical :size="12" />{{ child.title }}
                </small>
              </template>
            </button>
            <button class="new-chapter-button" type="button" @click="addTeacherChapter"><Plus :size="15" />新建章节</button>
          </aside>
          <section class="teacher-knowledge-table" aria-label="知识点列表">
            <div class="knowledge-head">
              <strong>知识点列表 <span>（{{ teacherActiveChapter?.title }}）</span></strong>
              <button class="teacher-ghost-action" type="button" aria-label="新增知识点" @click="addTeacherKnowledge"><Plus :size="16" />新增知识点</button>
            </div>
            <div class="knowledge-row knowledge-row-head">
              <span>知识点名称</span>
              <span>教学目标</span>
              <span>建议学时</span>
              <span>操作</span>
            </div>
            <div v-for="row in teacherPagedKnowledgeRows" :key="row.id" class="knowledge-row">
              <span><GripVertical :size="14" />{{ row.name }}</span>
              <span>{{ row.objective }}</span>
              <span>{{ row.hours }}</span>
              <span class="knowledge-actions">
                <button class="teacher-icon-button" type="button" title="上移" @click="moveTeacherKnowledge(row.id, -1)"><ChevronLeft :size="15" /></button>
                <button class="teacher-icon-button" type="button" title="编辑" @click="editTeacherKnowledge(row)"><Pencil :size="15" /></button>
                <button class="teacher-icon-button danger" type="button" title="删除" @click="deleteTeacherKnowledge(row.id)"><Trash2 :size="15" /></button>
                <button class="teacher-icon-button" type="button" title="下移" @click="moveTeacherKnowledge(row.id, 1)"><ChevronRight :size="15" /></button>
              </span>
            </div>
            <footer class="teacher-table-foot">
              <span>共 {{ teacherVisibleKnowledgeRows.length }} 条</span>
              <div>
                <button class="teacher-icon-button" type="button" :disabled="teacherKnowledgePage <= 1" @click="teacherKnowledgePage--"><ChevronLeft :size="15" /></button>
                <strong>{{ teacherKnowledgePage }}</strong>
                <button class="teacher-icon-button" type="button" :disabled="teacherKnowledgePage * 6 >= teacherVisibleKnowledgeRows.length" @click="teacherKnowledgePage++"><ChevronRight :size="15" /></button>
                <select aria-label="每页条数">
                  <option>10 条/页</option>
                  <option>20 条/页</option>
                </select>
              </div>
            </footer>
          </section>
        </div>
      </main>
    </section>

      <footer class="teacher-builder-footer">
        <span>最近保存：{{ teacherLastSaved }}</span>
        <span>草稿版本：{{ teacherDraftVersion }}</span>
        <div>
        <button class="teacher-ghost-action" type="button" @click="saveTeacherDraft"><Save :size="17" />保存草稿</button>
        <button class="teacher-ghost-action" type="button" @click="previewTeacherStudent"><Eye :size="17" />预览学生端</button>
        <button class="teacher-primary-action" type="button" :disabled="teacherSaving" @click="submitTeacherPublish"><Send :size="17" />提交发布</button>
        </div>
      </footer>

      <Transition name="teacher-drawer-fade">
        <button
          v-if="teacherStructureDraft.open"
          class="teacher-drawer-scrim"
          type="button"
          aria-label="关闭结构编辑"
          @click="closeTeacherStructureDraft"
        ></button>
      </Transition>
      <Transition name="teacher-drawer-slide">
        <aside
          v-if="teacherStructureDraft.open"
          class="teacher-structure-drawer"
          role="dialog"
          aria-modal="true"
          :aria-label="teacherStructureDraft.title"
        >
          <form @submit.prevent="saveTeacherStructureDraft">
            <header>
              <div>
                <span>{{ teacherStructureDraft.mode === 'chapter' ? '课程章节' : teacherActiveChapter?.title }}</span>
                <h2>{{ teacherStructureDraft.title }}</h2>
                <p>先在这里完成名称、目标和学时设置，保存后才写入课程结构。</p>
              </div>
              <button class="teacher-icon-button" type="button" aria-label="关闭" @click="closeTeacherStructureDraft">
                <X :size="16" />
              </button>
            </header>

            <label class="drawer-field">
              <span>{{ teacherStructureDraft.mode === 'chapter' ? '章节名称' : '知识点名称' }}</span>
              <input
                v-model="teacherStructureDraft.name"
                :placeholder="teacherStructureDraft.mode === 'chapter' ? '例如 第 6 章 项目综合实战' : '例如 Cookie 与 Session 管理'"
                autofocus
              />
            </label>

            <label class="drawer-field">
              <span>{{ teacherStructureDraft.mode === 'chapter' ? '章节目标' : '教学目标' }}</span>
              <textarea v-model="teacherStructureDraft.objective" rows="5" placeholder="写清楚本章节或知识点的教学目标、评价方式和资源要求"></textarea>
            </label>

            <label v-if="teacherStructureDraft.mode === 'chapter'" class="drawer-field">
              <span>首个小节（可选）</span>
              <input v-model="teacherStructureDraft.sectionTitle" placeholder="例如 6.1 项目设计与提交" />
            </label>

            <label v-else class="drawer-field compact">
              <span>建议学时</span>
              <input v-model="teacherStructureDraft.hours" type="number" min="0.5" step="0.5" />
            </label>

            <div class="drawer-preview">
              <strong>保存后位置</strong>
              <span v-if="teacherStructureDraft.mode === 'chapter'">章节树底部，并自动选中新章节。</span>
              <span v-else>{{ teacherActiveChapter?.title }} 的知识点列表，按分页定位到新增项。</span>
            </div>

            <footer>
              <button class="teacher-ghost-action" type="button" @click="closeTeacherStructureDraft">取消</button>
              <button class="teacher-primary-action" type="submit">
                <Save :size="17" />保存并定位
              </button>
            </footer>
          </form>
        </aside>
      </Transition>
    </div>

  <div v-else class="page-grid">
    <section class="dashboard-workbench course-workbench span-12">
      <div class="dashboard-workbench-head">
        <div>
          <h2>{{ builderTitle }}</h2>
        </div>
        <div class="home-action-row">
          <button class="button" type="button" @click="uploadInput?.click()"><UploadCloud :size="17" />上传资料</button>
          <RouterLink class="ghost-button" to="/courses"><BookOpenCheck :size="17" />查看{{ courseSpaceLabel }}</RouterLink>
          <button class="ghost-button" type="button" @click="loadCourses"><RefreshCw :size="17" />刷新</button>
        </div>
      </div>
      <div class="builder-command-band">
        <div class="course-source-switch" aria-label="课程来源">
          <button
            v-for="mode in courseSourceModes"
            :key="mode.key"
            type="button"
            :class="{ active: activeCourseSource === mode.key }"
            @click="activeCourseSource = mode.key"
          >
            <span>{{ mode.label }}</span>
            <strong>{{ mode.title }}</strong>
            <StatusPill :status="activeCourseSource === mode.key ? '当前来源' : mode.status" :tone="activeCourseSource === mode.key ? 'ok' : 'muted'" />
          </button>
        </div>

        <nav class="builder-course-rail" aria-label="资料归属课程">
          <button
            v-for="(course, index) in courseSwitchCards"
            :key="course.id"
            type="button"
            :class="{ active: course.active }"
            @click="selectCourse(course)"
          >
            <span class="builder-switch-index">{{ index + 1 }}</span>
            <span class="builder-switch-copy">
              <strong>{{ course.title }}</strong>
              <small>{{ course.department }} · {{ course.creditHours }} 学时</small>
            </span>
            <StatusPill :status="course.active ? '归属' : '绑定'" :tone="course.active ? 'ok' : 'muted'" />
          </button>
        </nav>

        <div class="builder-overview-lane">
          <div class="builder-overview-copy">
            <span>{{ activeCourseSourceMode.title }}</span>
            <strong>{{ form.title || '等待课程草稿' }}</strong>
            <div class="builder-context-strip" aria-label="建课上下文摘要">
              <span>{{ uploadSummary }}</span>
              <span>{{ activeCourseSource === 'classroom' ? selectedCourse?.title || '待选择班级课程' : selectedCourse?.title || '不绑定已有课程' }}</span>
              <span>{{ buildReadiness }}/{{ buildQualityChecks.length }} 项就绪</span>
            </div>
          </div>

          <dl class="builder-metric-list">
            <div v-for="item in courseStats" :key="item.label">
              <dt>{{ item.label }}</dt>
              <dd>{{ item.value }}</dd>
            </div>
          </dl>
        </div>

        <div class="builder-template-console" aria-label="课程方案与结构字段">
          <aside class="builder-template-slots">
            <div>
              <span>课程结构</span>
              <strong>把资料整理成可编辑的课程骨架</strong>
            </div>
            <dl>
              <div v-for="item in courseStructureItems" :key="item.label">
                <dt>{{ item.label }}</dt>
                <dd>{{ item.value }}</dd>
              </div>
            </dl>
          </aside>
          <section class="builder-template-library">
            <button
              v-for="template in visibleCourseBuildTemplates"
              :key="template.title"
              type="button"
              :class="{ active: activeCourseTemplateTitle === template.title }"
              @click="applyCourseTemplate(template)"
            >
              <span>{{ template.title }}</span>
              <strong>{{ renderCourseTemplate(template.titleTemplate) }}</strong>
            </button>
          </section>
        </div>

        <div class="builder-action-queue" aria-label="建课检查">
          <div v-for="item in buildQualityChecks" :key="item.title" :class="{ passed: item.passed }">
            <CheckCircle2 :size="16" />
            <strong>{{ item.title }}</strong>
          </div>
        </div>

        <div class="builder-readiness-strip" aria-label="课程准备状态">
          <span v-for="item in builderFlowSteps" :key="item.title">
            <component :is="item.icon" :size="17" />
            <strong>{{ item.title }}</strong>
          </span>
        </div>

        <div class="builder-next-actions" aria-label="课程建设下一步">
          <article v-for="item in nextActions" :key="item.title" :class="{ primary: item.primary }">
            <div>
              <strong>{{ item.title }}</strong>
            </div>
            <button v-if="!item.to" class="button" type="button" :disabled="!canCreateCourse || saving" @click="createCourse">
              <Save :size="16" />保存
            </button>
            <RouterLink v-else class="ghost-button" :to="item.to">
              <Sparkles v-if="item.title.includes('资源') || item.title.includes('AI')" :size="16" />
              <BookOpenCheck v-else :size="16" />进入
            </RouterLink>
          </article>
        </div>
      </div>
    </section>

    <SectionPanel
      class="span-12"
      :title="isTeacher ? '班级资料与课程草稿' : '资料上传与自定义课程'"
    >
      <ErrorNotice :message="error" />
      <div class="upload-studio">
        <button
          class="upload-dropzone"
          type="button"
          @click="uploadInput?.click()"
          @dragover.prevent
          @drop.prevent="addFiles($event.dataTransfer?.files || [])"
          :disabled="uploading"
        >
          <UploadCloud :size="34" />
          <strong>拖拽 PPT、PDF、教材章节、讲义、题库到这里</strong>
          <input
            ref="uploadInput"
            type="file"
            multiple
            hidden
            accept=".ppt,.pptx,.pdf,.doc,.docx,.txt,.md,.epub,.xls,.xlsx,.csv"
            @change="addFiles(($event.target as HTMLInputElement).files || [])"
          />
        </button>
        <div class="upload-inspector">
          <div class="section-head">
            <div>
              <p>{{ activeCourseSource === 'classroom' ? '班级课程资料' : '自建资料包' }}</p>
              <h3>{{ uploadSummary }}</h3>
            </div>
            <StatusPill :status="isTeacher ? '教师课程建设' : '学生自建课程'" tone="info" />
          </div>
          <div v-if="!importedFiles.length" class="empty-guide">
            <strong>还没有上传资料</strong>
          </div>
          <div v-else class="upload-file-list">
            <div v-for="file in importedFiles" :key="file.id" class="upload-file-row">
              <FileArchive :size="18" />
              <div>
                <strong>{{ file.name }}</strong>
                <small>{{ file.kind }} / {{ file.extension }} / {{ (file.size / 1024 / 1024).toFixed(2) }} MB</small>
                <small v-if="file.knowledgePoints.length">知识点：{{ file.knowledgePoints.slice(0, 4).join('、') }}</small>
                <small v-if="file.parseMessage">{{ file.parseMessage }}</small>
              </div>
              <StatusPill :status="file.status" tone="warn" />
              <button class="icon-button" type="button" title="移除资料" @click="removeImportedFile(file.id)">
                <Trash2 :size="16" />
              </button>
            </div>
          </div>
          <LoadingBlock :show="uploading" text="正在上传并解析课程资料" />
          <div class="button-row">
            <button class="button" type="button" :disabled="!importedFiles.length || uploading" @click="applyUploadDraft">
              <BookOpenCheck :size="17" />生成课程草稿
            </button>
            <span class="inline-hint"><CheckCircle2 :size="15" />草稿会填入下方表单，确认后保存为课程。</span>
          </div>
        </div>
      </div>
    </SectionPanel>

    <SectionPanel
      class="span-12 course-draft-panel"
      :title="isTeacher ? '班级课程草稿' : '自定义课程草稿'"
    >
      <div class="course-draft-workspace">
        <form class="form-grid course-draft-form" @submit.prevent="createCourse">
          <div class="field">
            <label>课程名称 <span class="required-mark">*</span></label>
            <input v-model="form.title" required />
            <small v-if="formErrors.title" class="field-error">{{ formErrors.title }}</small>
          </div>
          <div class="field">
            <label>院系/归属 <span class="required-mark">*</span></label>
            <input v-model="form.department" />
            <small v-if="formErrors.department" class="field-error">{{ formErrors.department }}</small>
          </div>
          <div class="field">
            <label>学时 <span class="required-mark">*</span></label>
            <input v-model.number="form.creditHours" type="number" min="1" />
            <small v-if="formErrors.creditHours" class="field-error">{{ formErrors.creditHours }}</small>
          </div>
          <div class="field">
            <label>课程描述 <span class="required-mark">*</span></label>
            <textarea v-model="form.description" />
            <small v-if="formErrors.description" class="field-error">{{ formErrors.description }}</small>
          </div>
          <div class="course-outline-summary">
            <div>
              <strong>学习单元</strong>
              <span>{{ syllabusWeeks.length || '待生成' }}</span>
            </div>
            <div>
              <strong>知识覆盖</strong>
              <span>{{ previewKnowledgePoints.length || '待抽取' }}</span>
            </div>
            <div>
              <strong>资料来源</strong>
              <span>{{ importedFiles.length || '待上传' }}</span>
            </div>
          </div>
          <div class="course-outline-editor">
            <div class="outline-editor-head">
              <div>
                <strong>学习单元</strong>
              </div>
              <button class="ghost-button" type="button" @click="addSyllabusWeek"><Route :size="16" />添加单元</button>
            </div>
            <div v-if="!syllabusWeeks.length" class="empty-guide compact-empty">
              <strong>等待课程结构</strong>
            </div>
            <div v-else class="outline-unit-editor">
              <article v-for="(week, index) in syllabusWeeks" :key="String(week.week || week.topic || index)">
                <span>单元 {{ week.week || index + 1 }}</span>
                <input
                  :value="String(week.topic || week.title || '')"
                  aria-label="学习单元主题"
                  @input="updateSyllabusWeek(index, ($event.target as HTMLInputElement).value)"
                />
                <button class="icon-button" type="button" title="移除学习单元" @click="removeSyllabusWeek(index)">
                  <Trash2 :size="15" />
                </button>
              </article>
            </div>
            <div class="outline-knowledge-editor">
              <strong>知识点覆盖</strong>
              <div class="outline-chip-editor">
                <button v-for="point in previewKnowledgePoints" :key="point" type="button" @click="removeKnowledgePoint(point)">
                  {{ point }} <span>×</span>
                </button>
              </div>
              <div class="outline-add-row">
                <input v-model="newKnowledgePoint" placeholder="补充知识点，例如 核心概念、方法步骤或典型问题" @keydown.enter.prevent="addKnowledgePoint" />
                <button class="ghost-button" type="button" @click="addKnowledgePoint">添加</button>
              </div>
              <small v-if="formErrors.syllabusJson" class="field-error">{{ formErrors.syllabusJson }}</small>
            </div>
          </div>
          <button class="button" :disabled="!canCreateCourse"><Save :size="17" />保存为课程</button>
        </form>
        <aside class="course-draft-preview" aria-label="课程草稿预览">
          <div class="context-grid">
            <div>
              <strong>课程名称</strong>
              <span>{{ form.title || '待生成' }}</span>
              <small>{{ form.department || '待填写院系/归属' }} / {{ form.creditHours || 0 }} 学时</small>
            </div>
            <div>
              <strong>保存检查</strong>
              <span>{{ buildReadiness }}/{{ buildQualityChecks.length }} 项就绪</span>
            </div>
          </div>
          <div class="builder-check-grid">
            <div v-for="item in buildQualityChecks" :key="item.title" :class="{ passed: item.passed }">
              <CheckCircle2 :size="17" />
              <strong>{{ item.title }}</strong>
              <span>{{ item.value }}</span>
            </div>
          </div>
          <div class="builder-knowledge-board">
            <div>
              <h3>知识点覆盖</h3>
              <div v-if="!previewKnowledgePoints.length" class="empty-guide">
                <strong>等待资料解析</strong>
              </div>
              <div v-else class="builder-chip-list">
                <span v-for="point in previewKnowledgePoints" :key="point">{{ point }}</span>
              </div>
            </div>
            <div>
              <h3>学习单元</h3>
              <div v-if="!syllabusWeeks.length" class="empty-guide">
                <strong>暂无学习单元</strong>
              </div>
              <div v-else class="timeline">
                <div v-for="week in syllabusWeeks" :key="String(week.week || week.topic)" class="timeline-body">
                  <strong>第 {{ week.week || '-' }} 单元</strong>
                  <p>{{ String(week.topic || week.title || '未命名学习单元') }}</p>
                </div>
              </div>
            </div>
          </div>
        </aside>
      </div>
      <LoadingBlock :show="saving" text="正在保存课程" />
    </SectionPanel>

    <SectionPanel class="span-12 course-space-panel" title="课程空间">
      <LoadingBlock :show="loading" />
      <div class="context-grid">
        <div>
          <strong>{{ activeCourseSource === 'classroom' ? '老师发放课程' : '资料归属课程' }}</strong>
          <span>{{ selectedCourse?.title || '未选择' }}</span>
        </div>
        <div>
          <strong>生成后下一步</strong>
          <span>{{ isTeacher ? '进入资源审核' : '去 AI 助手生成' }}</span>
        </div>
      </div>
      <div v-if="!courses.length && !loading" class="empty-guide">
        <strong>暂无课程</strong>
      </div>
      <div v-else class="course-space-list">
        <button
          v-for="course in courses"
          :key="course.id"
          class="course-space-row clickable-row"
          :class="{ active: selectedCourse?.id === course.id }"
          @click="selectCourse(course)"
        >
          <div>
            <strong>{{ course.title }}</strong>
            <p>{{ compact(course.description, 96) }}</p>
          </div>
          <small>{{ course.department }} / {{ formatDate(course.updatedAt) }}</small>
          <StatusPill :status="selectedCourse?.id === course.id ? '当前' : '选择'" :tone="selectedCourse?.id === course.id ? 'ok' : 'muted'" />
        </button>
      </div>
      <div class="button-row">
        <button class="button" type="button" :disabled="!canCreateCourse || saving" @click="createCourse"><Save :size="17" />保存当前课程</button>
        <RouterLink class="ghost-button" :to="generationTarget"><Sparkles :size="17" />{{ isTeacher ? '去审核资源' : '去 AI 助手生成' }}</RouterLink>
        <RouterLink class="ghost-button" to="/courses">查看我的课程</RouterLink>
      </div>
    </SectionPanel>
  </div>
</template>

<style scoped>
.teacher-builder-page {
  display: grid;
  gap: 20px;
  min-width: 0;
  color: #14233a;
}

.teacher-builder-notice {
  display: flex;
  align-items: center;
  min-height: 38px;
  margin: 0;
  padding: 0 16px;
  color: #06786f;
  background: #eefbf9;
  border: 1px solid #b8e5df;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 780;
}

.teacher-builder-panel,
.teacher-builder-footer {
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid #d8e5ec;
  border-radius: 12px;
  box-shadow: 0 16px 38px rgba(25, 49, 70, 0.045);
}

.teacher-builder-grid {
  display: grid;
  grid-template-columns: minmax(320px, 0.62fr) minmax(560px, 1.38fr);
  gap: 22px;
  align-items: stretch;
  min-width: 0;
}

.teacher-builder-panel {
  min-width: 0;
  min-height: clamp(860px, calc(100dvh - 260px), 1040px);
  overflow: hidden;
}

.teacher-panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 76px;
  padding: 0 22px;
  border-bottom: 1px solid #e1ebf0;
}

.teacher-panel-head h2 {
  margin: 0;
  color: #16243c;
  font-size: 20px;
  font-weight: 930;
  letter-spacing: 0;
}

.teacher-panel-head p {
  margin: 5px 0 0;
  color: #6b7d90;
  font-size: 13px;
  font-weight: 720;
}

.teacher-upload-zone {
  display: grid;
  place-items: center;
  justify-self: stretch;
  width: calc(100% - 44px);
  box-sizing: border-box;
  min-height: 178px;
  margin: 22px;
  padding: 26px;
  color: #0c8177;
  background: #fbfefe;
  border: 1px dashed #a9ccd9;
  border-radius: 8px;
  cursor: pointer;
}

.teacher-upload-zone strong {
  margin-top: 12px;
  color: #1e2f48;
  font-size: 15px;
  font-weight: 880;
}

.teacher-upload-zone span {
  margin-top: 7px;
  color: #708196;
  font-size: 13px;
  font-weight: 720;
}

.teacher-filter-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  padding: 0 22px 16px;
}

.teacher-filter-row label {
  display: grid;
  gap: 6px;
  color: #6d7e91;
  font-size: 12px;
  font-weight: 800;
}

.teacher-filter-row select,
.teacher-table-foot select {
  height: 38px;
  padding: 0 12px;
  color: #17283f;
  background: #ffffff;
  border: 1px solid #d2e0e8;
  border-radius: 8px;
  outline: 0;
  font-weight: 760;
}

.teacher-material-table {
  display: grid;
  padding: 0 22px;
}

.teacher-material-row {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1.55fr) 58px 92px 76px 40px;
  align-items: center;
  min-height: 62px;
  gap: 10px;
  border-bottom: 1px solid #ebf1f4;
  color: #273851;
  font-size: 13px;
  font-weight: 760;
}

.teacher-material-row.table-head {
  min-height: 42px;
  color: #718194;
  background: #f7fafb;
  border-top: 1px solid #ecf1f4;
  font-size: 12px;
  font-weight: 850;
}

.material-name {
  display: inline-flex;
  align-items: center;
  min-width: 0;
  gap: 7px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mini-progress {
  display: block;
  width: 68px;
  height: 5px;
  margin-top: 5px;
  overflow: hidden;
  background: #e8eef2;
  border-radius: 999px;
}

.mini-progress b {
  display: block;
  height: 100%;
  background: #0a968d;
}

.teacher-icon-button {
  display: inline-grid;
  width: 30px;
  height: 30px;
  place-items: center;
  color: #486078;
  background: #ffffff;
  border: 1px solid #d2e1e8;
  border-radius: 7px;
  cursor: pointer;
}

.teacher-icon-button:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

.teacher-icon-button.danger {
  color: #ef5d55;
}

.material-actions {
  position: relative;
}

.teacher-row-menu {
  position: absolute;
  top: 34px;
  right: 0;
  z-index: 20;
  display: grid;
  width: 120px;
  margin: 0;
  padding: 6px;
  background: #ffffff;
  border: 1px solid #d8e4eb;
  border-radius: 8px;
  box-shadow: 0 14px 30px rgba(31, 54, 74, 0.13);
}

.teacher-row-menu button {
  height: 30px;
  padding: 0 9px;
  color: #22354d;
  background: transparent;
  border: 0;
  border-radius: 6px;
  cursor: pointer;
  text-align: left;
  font-size: 12px;
  font-weight: 780;
}

.teacher-row-menu button:hover {
  background: #edf8f7;
}

.teacher-panel-foot,
.teacher-table-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 58px;
  padding: 0 22px;
  color: #607286;
  font-size: 13px;
  font-weight: 780;
}

.teacher-panel-foot button,
.teacher-table-foot button {
  color: #07847b;
  background: transparent;
  border: 0;
  cursor: pointer;
  font-weight: 840;
}

.structure-editor {
  display: grid;
  grid-template-rows: 76px minmax(0, 1fr);
}

.structure-head {
  padding-right: 18px;
}

.teacher-button-row {
  display: flex;
  gap: 12px;
}

.teacher-ghost-action,
.teacher-primary-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 42px;
  gap: 8px;
  padding: 0 18px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 880;
}

.teacher-ghost-action {
  color: #087f77;
  background: #ffffff;
  border: 1px solid #cbdde6;
}

.teacher-primary-action {
  color: #ffffff;
  background: linear-gradient(135deg, #0a9a91, #08766e);
  border: 1px solid #08766e;
  box-shadow: 0 12px 24px rgba(8, 127, 121, 0.15);
}

.teacher-primary-action:disabled {
  cursor: wait;
  opacity: 0.68;
}

.teacher-structure-body {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  min-height: 0;
  overflow: hidden;
}

.teacher-chapter-tree {
  display: grid;
  grid-template-rows: 48px minmax(0, auto);
  gap: 4px;
  min-width: 0;
  padding: 16px;
  border-right: 1px solid #e1ebf0;
  overflow: auto;
  overscroll-behavior: contain;
}

.chapter-tree-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #1a2c44;
  font-weight: 900;
}

.chapter-node {
  display: grid;
  grid-template-columns: 22px minmax(0, 1fr);
  align-items: center;
  gap: 4px 8px;
  min-height: 42px;
  padding: 8px 10px;
  color: #22354d;
  background: transparent;
  border: 0;
  border-radius: 8px;
  cursor: pointer;
  text-align: left;
}

.chapter-node.active {
  background: linear-gradient(90deg, #e7f8f6, #f5fcfb);
  box-shadow: inset 3px 0 0 #08867e;
}

.chapter-node strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
  font-weight: 880;
}

.chapter-node small {
  grid-column: 2;
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  gap: 5px;
  color: #607489;
  font-size: 13px;
  font-weight: 740;
}

.new-chapter-button {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  gap: 7px;
  margin-top: 10px;
  color: #07847b;
  background: transparent;
  border: 0;
  cursor: pointer;
  font-weight: 860;
}

.teacher-knowledge-table {
  display: grid;
  grid-template-rows: 56px 42px repeat(6, 62px) 58px;
  min-width: 0;
  padding: 16px 18px;
  overflow-x: auto;
  overflow-y: hidden;
}

.knowledge-head,
.knowledge-row,
.teacher-table-foot {
  min-width: 0;
}

.knowledge-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.knowledge-head strong {
  color: #1b2d45;
  font-weight: 900;
}

.knowledge-head span {
  color: #5c7188;
  font-size: 13px;
}

.knowledge-row {
  display: grid;
  grid-template-columns: minmax(150px, 1fr) minmax(180px, 1.18fr) 76px 156px;
  align-items: center;
  min-width: 650px;
  gap: 12px;
  border-bottom: 1px solid #e8f0f4;
  color: #263a53;
  font-size: 13px;
  font-weight: 760;
}

.knowledge-row > span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.knowledge-row > span:first-child {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-weight: 850;
}

.knowledge-row-head {
  min-height: 42px;
  padding: 0 12px;
  color: #6f7f92;
  background: #f7fafb;
  border: 1px solid #e7eef2;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 880;
}

.knowledge-actions {
  display: inline-flex;
  justify-content: flex-end;
  min-width: 156px;
  gap: 6px;
  overflow: visible !important;
  white-space: nowrap !important;
}

.teacher-table-foot {
  padding: 0;
}

.teacher-table-foot div {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.teacher-table-foot strong {
  display: grid;
  width: 30px;
  height: 30px;
  place-items: center;
  color: #ffffff;
  background: #08887f;
  border-radius: 7px;
}

.teacher-builder-footer {
  display: grid;
  grid-template-columns: auto auto minmax(0, 1fr);
  align-items: center;
  min-height: 86px;
  gap: 46px;
  padding: 0 30px;
  color: #607389;
  font-size: 14px;
  font-weight: 800;
}

.teacher-builder-footer div {
  display: flex;
  justify-content: flex-end;
  gap: 24px;
}

.teacher-drawer-scrim {
  position: fixed;
  inset: 0;
  z-index: 80;
  background: rgba(10, 23, 38, 0.24);
  border: 0;
  cursor: pointer;
}

.teacher-structure-drawer {
  position: fixed;
  top: 0;
  right: 0;
  z-index: 90;
  display: grid;
  width: min(468px, calc(100vw - 34px));
  height: 100dvh;
  padding: 18px;
  background: linear-gradient(180deg, #fbfefe, #f4fbfa);
  border-left: 1px solid #cfe0e8;
  box-shadow: -24px 0 52px rgba(24, 48, 70, 0.18);
}

.teacher-structure-drawer form {
  display: grid;
  grid-template-rows: auto auto auto auto minmax(0, 1fr) auto;
  gap: 18px;
  min-height: 0;
}

.teacher-structure-drawer header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  padding: 8px 4px 12px;
  border-bottom: 1px solid #dce9ee;
}

.teacher-structure-drawer header span {
  color: #087f77;
  font-size: 13px;
  font-weight: 850;
}

.teacher-structure-drawer header h2 {
  margin: 7px 0 0;
  color: #13233b;
  font-size: 24px;
  font-weight: 940;
  letter-spacing: 0;
}

.teacher-structure-drawer header p {
  margin: 8px 0 0;
  color: #60758c;
  font-size: 13px;
  line-height: 1.6;
  font-weight: 720;
}

.drawer-field {
  display: grid;
  gap: 8px;
  color: #233750;
  font-size: 13px;
  font-weight: 850;
}

.drawer-field input,
.drawer-field textarea {
  width: 100%;
  box-sizing: border-box;
  color: #14243d;
  background: #ffffff;
  border: 1px solid #cfe0e8;
  border-radius: 8px;
  outline: 0;
  font: inherit;
  font-weight: 760;
}

.drawer-field input {
  height: 44px;
  padding: 0 13px;
}

.drawer-field textarea {
  resize: vertical;
  min-height: 118px;
  padding: 12px 13px;
  line-height: 1.7;
}

.drawer-field.compact {
  max-width: 180px;
}

.drawer-field input:focus,
.drawer-field textarea:focus {
  border-color: #0a928a;
  box-shadow: 0 0 0 3px rgba(10, 146, 138, 0.12);
}

.drawer-preview {
  align-self: start;
  display: grid;
  gap: 7px;
  padding: 14px;
  color: #526980;
  background: #edf8f7;
  border: 1px solid #c9e5e1;
  border-radius: 10px;
  font-size: 13px;
  line-height: 1.6;
  font-weight: 740;
}

.drawer-preview strong {
  color: #087a72;
  font-weight: 900;
}

.teacher-structure-drawer footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #dce9ee;
}

.teacher-drawer-fade-enter-active,
.teacher-drawer-fade-leave-active,
.teacher-drawer-slide-enter-active,
.teacher-drawer-slide-leave-active {
  transition: opacity 0.18s ease, transform 0.22s ease;
}

.teacher-drawer-fade-enter-from,
.teacher-drawer-fade-leave-to {
  opacity: 0;
}

.teacher-drawer-slide-enter-from,
.teacher-drawer-slide-leave-to {
  opacity: 0;
  transform: translateX(28px);
}

@media (max-width: 1500px) {
  .teacher-builder-grid {
    grid-template-columns: 1fr;
  }

  .teacher-builder-panel {
    min-height: auto;
  }
}

@media (max-width: 760px) {
  .teacher-builder-grid {
    gap: 16px;
  }

  .teacher-upload-zone {
    width: calc(100% - 32px);
    margin: 16px;
    padding: 22px 18px;
  }

  .teacher-builder-panel {
    overflow: visible;
  }

  .structure-head {
    align-items: flex-start;
    min-height: auto;
    gap: 14px;
    padding: 18px;
  }

  .teacher-button-row {
    display: grid;
    width: 100%;
    grid-template-columns: 1fr 1fr;
  }

  .teacher-structure-body {
    grid-template-columns: 1fr;
  }

  .teacher-chapter-tree {
    border-right: 0;
    border-bottom: 1px solid #e1ebf0;
    overflow: visible;
  }

  .teacher-knowledge-table {
    overflow-x: auto;
  }

  .knowledge-row {
    min-width: 620px;
  }
}
</style>
