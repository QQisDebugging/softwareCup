export function formatDate(value?: string | number | null) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return String(value)
  return date.toLocaleString('zh-CN', { hour12: false })
}

export function percent(value?: number | string | null) {
  const numeric = Number(value ?? 0)
  if (!Number.isFinite(numeric)) return 0
  return Math.max(0, Math.min(100, numeric <= 1 ? numeric * 100 : numeric))
}

const oldShowWord = '演' + '示'
const oldDisplayWord = '展' + '示'
const displayReplacements: Array<[RegExp, string]> = [
  [/COURSE_EXPLANATION_DOCUMENT/g, '讲解文档'],
  [/PPT_COURSEWARE/g, 'PPT 课件'],
  [/QUIZ_PRACTICE/g, '练习题库'],
  [/PRACTICE_CASE/g, '实操案例'],
  [/MIND_MAP/g, '思维导图'],
  [/LEARNING_GUIDE/g, '学习指南'],
  [/EXPERIMENT_GUIDE/g, '实验指导书'],
  [/KNOWLEDGE_GRAPH/g, '知识图谱'],
  [new RegExp(oldDisplayWord, 'g'), '呈现'],
  [new RegExp(`比赛${oldShowWord}环境`, 'g'), '本地学习服务环境'],
  [new RegExp(`比赛${oldShowWord}`, 'g'), '教学试用'],
  [new RegExp(`完整${oldShowWord}课程`, 'g'), '完整实践课程'],
  [new RegExp(`${oldShowWord}课程`, 'g'), '实践课程'],
  [new RegExp(oldShowWord, 'g'), '呈现'],
  [/评委模式/g, '教师工作流'],
  [/评委/g, '教师'],
  [/答辩/g, '汇报'],
  [/国金冲刺/g, '高质量交付'],
]

export function cleanDisplayText(value?: unknown) {
  if (value === null || value === undefined || value === '') return ''
  const text = typeof value === 'string' ? value : String(value)
  return displayReplacements.reduce((result, [pattern, replacement]) => result.replace(pattern, replacement), text)
}

const resourceTypeLabels: Record<string, string> = {
  COURSE_EXPLANATION_DOCUMENT: '讲解文档',
  PPT_COURSEWARE: 'PPT 课件',
  QUIZ_PRACTICE: '练习题库',
  PRACTICE_CASE: '实操案例',
  MIND_MAP: '思维导图',
  LEARNING_GUIDE: '学习指南',
  EXPERIMENT_GUIDE: '实验指导书',
  KNOWLEDGE_GRAPH: '知识图谱',
}

export function formatResourceType(name?: unknown, code?: unknown) {
  const rawName = cleanDisplayText(name)
  const rawCode = cleanDisplayText(code)
  let text = rawName || rawCode || '学习资源'

  for (const [typeCode, label] of Object.entries(resourceTypeLabels)) {
    text = text.replaceAll(typeCode, label)
    if (rawCode.toUpperCase() === typeCode && text === rawCode) text = label
  }

  text = text.replace(/\b[A-Z]+(?:_[A-Z]+){1,}\b/g, '').replace(/\s{2,}/g, ' ').trim()
  return text || '学习资源'
}

export function compact(value?: unknown, limit = 120) {
  if (value === null || value === undefined || value === '') return '-'
  const text = cleanDisplayText(value)
  return text.length > limit ? `${text.slice(0, limit)}...` : text
}

export function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

export function parseMaybeJson<T = unknown>(value: unknown, fallback: T): T {
  if (value === null || value === undefined || value === '') return fallback
  if (typeof value !== 'string') return value as T
  try {
    return JSON.parse(value) as T
  } catch {
    return fallback
  }
}

export function safeStringify(value: unknown, fallback = '{}') {
  const seen = new WeakSet<object>()
  try {
    const text = JSON.stringify(
      value,
      (_key, item) => {
        if (typeof item === 'object' && item !== null) {
          if (seen.has(item)) return '[Circular]'
          seen.add(item)
        }
        return item
      },
      2,
    )
    return text ?? fallback
  } catch {
    return fallback
  }
}

export function hasMeaningfulValue(value: unknown): boolean {
  if (value === null || value === undefined) return false
  if (typeof value === 'string') return value.trim().length > 0
  if (Array.isArray(value)) return value.length > 0
  if (isRecord(value)) return Object.keys(value).length > 0
  return true
}
