export function formatDate(value?: string | null) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('zh-CN', { hour12: false })
}

export function percent(value?: number | string | null) {
  const numeric = Number(value ?? 0)
  if (!Number.isFinite(numeric)) return 0
  return Math.max(0, Math.min(100, numeric <= 1 ? numeric * 100 : numeric))
}

export function compact(value?: string | null, limit = 120) {
  if (!value) return '-'
  return value.length > limit ? `${value.slice(0, limit)}...` : value
}

export function parseMaybeJson<T = unknown>(value: string | undefined | null, fallback: T): T {
  if (!value) return fallback
  try {
    return JSON.parse(value) as T
  } catch {
    return fallback
  }
}
