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

export function compact(value?: unknown, limit = 120) {
  if (value === null || value === undefined || value === '') return '-'
  const text = typeof value === 'string' ? value : String(value)
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
