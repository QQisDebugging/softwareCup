import axios, { AxiosError } from 'axios'
import { isRecord } from '@/utils/format'

export const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api'

export const http = axios.create({
  baseURL: apiBaseUrl,
  timeout: 45000,
  headers: {
    'Content-Type': 'application/json;charset=utf-8',
  },
})

http.interceptors.response.use(
  (response) => response.data,
  (error: AxiosError) => {
    const message = normalizeApiError(error)
    return Promise.reject(new Error(message))
  },
)

function readServerMessage(data: unknown) {
  if (typeof data === 'string') return data
  if (!isRecord(data)) return ''
  const detail = data.detail || data.message || data.title || data.error
  return typeof detail === 'string' ? detail : ''
}

export function normalizeApiError(error: AxiosError) {
  if (error.code === 'ECONNABORTED') {
    return `接口请求超时：请确认平台服务正在运行，并检查 ${apiBaseUrl}`
  }
  if (!error.response) {
    return `后端连接失败：请确认平台服务已启动，并且 VITE_API_BASE_URL=${apiBaseUrl}`
  }

  const status = error.response.status
  const serverMessage = readServerMessage(error.response.data)
  if (serverMessage) return serverMessage
  if (status === 404) return '接口不存在或路径不匹配，请检查前端 API 封装与后端服务。'
  if (status === 401 || status === 403) return '接口无访问权限，请确认后端鉴权或运行环境配置。'
  if (status >= 500) return '后端处理异常：请查看平台服务日志。'
  return `接口调用失败，HTTP 状态码 ${status}。`
}

export function unwrapApiPayload(value: unknown): unknown {
  if (!isRecord(value)) return value
  const data = value.data
  const result = value.result
  if (Array.isArray(data) || isRecord(data)) return data
  if (Array.isArray(result) || isRecord(result)) return result
  return value
}

export function asArray<T>(value: unknown): T[] {
  const payload = unwrapApiPayload(value)
  if (Array.isArray(payload)) return payload as T[]
  if (!isRecord(payload)) return []
  for (const key of ['items', 'list', 'records', 'content', 'results']) {
    const nested = payload[key]
    if (Array.isArray(nested)) return nested as T[]
  }
  return []
}

export function asObject<T extends object>(value: unknown, fallback: T): T {
  const payload = unwrapApiPayload(value)
  if (isRecord(payload)) return { ...fallback, ...payload } as T
  return fallback
}

export function asApiRecord(value: unknown): Record<string, unknown> {
  const payload = unwrapApiPayload(value)
  if (isRecord(payload)) return payload
  if (payload === null || payload === undefined) return {}
  if (typeof payload === 'string') return { content: payload }
  return { value: payload }
}

export async function get<T>(url: string, params?: Record<string, unknown>): Promise<T> {
  return http.get<T, T>(url, { params })
}

export async function post<T, B = unknown>(url: string, body?: B): Promise<T> {
  return http.post<T, T>(url, body)
}

export async function postForm<T>(url: string, body: FormData): Promise<T> {
  return http.post<T, T>(url, body, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 90000,
  })
}

export async function put<T, B = unknown>(url: string, body?: B): Promise<T> {
  return http.put<T, T>(url, body)
}

export async function patch<T, B = unknown>(url: string, body?: B): Promise<T> {
  return http.patch<T, T>(url, body)
}

export async function del<T>(url: string, params?: Record<string, unknown>): Promise<T> {
  return http.delete<T, T>(url, { params })
}

export async function getArray<T>(url: string, params?: Record<string, unknown>): Promise<T[]> {
  return asArray<T>(await get<unknown>(url, params))
}
