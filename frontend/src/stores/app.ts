import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { authApi, coursesApi, healthApi } from '@/api'
import type { AuthRole, RegisterAccountRequest } from '@/api'
import type { Course, HealthResponse } from '@/types/api'

export type UserRole = AuthRole

export interface PlatformAccount {
  id: string
  username: string
  role: UserRole
  name: string
  title: string
  home: string
  department: string
  status: string
}

const accountStorageKey = 'learning-account'
const legacyAccountIdKey = 'learning-account-id'
const courseStorageKey = 'learning-course-id'

const storage = typeof window === 'undefined' ? null : window.localStorage
const storedCourseId = storage?.getItem(courseStorageKey) || ''

function readStoredAccount(): PlatformAccount | null {
  if (!storage) return null
  try {
    const parsed = JSON.parse(storage.getItem(accountStorageKey) || 'null') as Partial<PlatformAccount> | null
    if (!parsed?.id || !parsed.username || (parsed.role !== 'student' && parsed.role !== 'teacher')) return null
    return {
      id: parsed.id,
      username: parsed.username,
      role: parsed.role,
      name: parsed.name || parsed.username,
      title: parsed.title || (parsed.role === 'teacher' ? '课程教师' : '学生'),
      home: parsed.home || '',
      department: parsed.department || '',
      status: parsed.status || 'active',
    }
  } catch {
    return null
  }
}

function persistAccount(account: PlatformAccount | null) {
  if (!storage) return
  if (!account) {
    storage.removeItem(accountStorageKey)
    storage.removeItem(legacyAccountIdKey)
    return
  }
  storage.setItem(accountStorageKey, JSON.stringify(account))
  storage.setItem(legacyAccountIdKey, account.id)
}

export const useAppStore = defineStore('app', () => {
  const health = ref<HealthResponse | null>(null)
  const healthError = ref('')
  const checking = ref(false)
  const currentAccount = ref<PlatformAccount | null>(readStoredAccount())
  const courses = ref<Course[]>([])
  const coursesLoading = ref(false)
  const activeCourseId = ref(storedCourseId)

  const accounts = computed(() => (currentAccount.value ? [currentAccount.value] : []))
  const accountId = computed(() => currentAccount.value?.id || '')
  const role = computed<UserRole>(() => currentAccount.value?.role || 'student')
  const isLoggedIn = computed(() => Boolean(currentAccount.value))
  const backendOnline = computed(() => String(health.value?.status || '').toUpperCase() === 'UP')
  const activeCourse = computed(() => courses.value.find((course) => course.id === activeCourseId.value) || courses.value[0] || null)
  const currentUser = computed(
    () =>
      currentAccount.value || {
        id: '',
        username: '',
        role: 'student' as UserRole,
        name: '未登录',
        title: '访客',
        home: '请先登录账号',
        department: '',
        status: 'guest',
      },
  )

  async function refreshHealth() {
    checking.value = true
    healthError.value = ''
    try {
      health.value = await healthApi.getHealth()
    } catch (error) {
      health.value = null
      healthError.value = error instanceof Error ? error.message : '后端不可用'
    } finally {
      checking.value = false
    }
  }

  async function loadCourses() {
    coursesLoading.value = true
    try {
      courses.value = await coursesApi.list()
      if (!activeCourseId.value && courses.value[0]?.id) setActiveCourse(courses.value[0].id)
      if (activeCourseId.value && courses.value.length && !courses.value.some((course) => course.id === activeCourseId.value)) {
        setActiveCourse(courses.value[0].id)
      }
    } finally {
      coursesLoading.value = false
    }
  }

  function setActiveCourse(courseId: string) {
    activeCourseId.value = courseId
    if (courseId) storage?.setItem(courseStorageKey, courseId)
  }

  async function login(username: string, password: string, expectedRole?: UserRole) {
    const account = await authApi.login({
      username: username.trim(),
      password,
      role: expectedRole || 'student',
    })
    currentAccount.value = account
    persistAccount(account)
    return ''
  }

  async function register(input: RegisterAccountRequest) {
    const account = await authApi.register({
      ...input,
      username: input.username.trim().toLowerCase(),
      name: input.name.trim(),
      department: input.department?.trim(),
    })
    currentAccount.value = account
    persistAccount(account)
    return ''
  }

  function logout() {
    currentAccount.value = null
    persistAccount(null)
  }

  return {
    accounts,
    accountId,
    currentAccount,
    health,
    healthError,
    checking,
    backendOnline,
    role,
    isLoggedIn,
    currentUser,
    courses,
    coursesLoading,
    activeCourseId,
    activeCourse,
    refreshHealth,
    loadCourses,
    setActiveCourse,
    login,
    register,
    logout,
  }
})
