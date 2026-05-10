import axios, { AxiosError } from 'axios'

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
    const detail = error.response?.data as { detail?: string; title?: string; message?: string } | undefined
    const message = !error.response
      ? `后端连接失败：请确认 Spring Boot 已启动，并且 VITE_API_BASE_URL=${apiBaseUrl}`
      : detail?.detail || detail?.message || detail?.title || error.message || '接口调用失败'
    return Promise.reject(new Error(message))
  },
)

export async function get<T>(url: string, params?: Record<string, unknown>): Promise<T> {
  return http.get<T, T>(url, { params })
}

export async function post<T, B = unknown>(url: string, body?: B): Promise<T> {
  return http.post<T, T>(url, body)
}

export async function put<T, B = unknown>(url: string, body?: B): Promise<T> {
  return http.put<T, T>(url, body)
}
