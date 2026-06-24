import { asObject, post } from '../http'

export type AuthRole = 'student' | 'teacher'

export interface AuthAccountResponse {
  id: string
  username: string
  role: AuthRole
  name: string
  title: string
  home: string
  department: string
  status: string
}

export interface LoginRequest {
  username: string
  password: string
  role: AuthRole
}

export interface RegisterAccountRequest {
  username: string
  password: string
  role: AuthRole
  name: string
  department?: string
  inviteCode?: string
}

function normalizeAccount(value: unknown): AuthAccountResponse {
  const record = asObject<AuthAccountResponse>(value, {
    id: '',
    username: '',
    role: 'student',
    name: '',
    title: '',
    home: '',
    department: '',
    status: 'active',
  })
  return {
    ...record,
    role: record.role === 'teacher' ? 'teacher' : 'student',
  }
}

export const authApi = {
  login: async (body: LoginRequest) => normalizeAccount(await post<unknown, LoginRequest>('/auth/login', body)),
  register: async (body: RegisterAccountRequest) =>
    normalizeAccount(await post<unknown, RegisterAccountRequest>('/auth/register', body)),
}
