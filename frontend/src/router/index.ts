import { createRouter, createWebHistory } from 'vue-router'
import { useAppStore } from '@/stores/app'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'entry',
      meta: {
        title: '登录',
      },
      component: () => import('@/views/DashboardView.vue'),
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      meta: {
        title: '学生主页',
        roles: ['student'],
      },
      component: () => import('@/views/DashboardView.vue'),
    },
    {
      path: '/profiles',
      name: 'profiles',
      meta: {
        title: '学习画像',
      },
      component: () => import('@/views/ProfilesView.vue'),
    },
    {
      path: '/courses',
      name: 'courses',
      meta: {
        title: '课程空间',
      },
      component: () => import('@/views/CoursesView.vue'),
    },
    {
      path: '/courses/:courseId',
      name: 'course-detail',
      meta: {
        title: '课程详情',
      },
      component: () => import('@/views/CoursesView.vue'),
    },
    {
      path: '/course-builder',
      name: 'course-builder',
      meta: {
        title: '课程建设',
      },
      component: () => import('@/views/CourseBuilderView.vue'),
    },
    {
      path: '/generation',
      name: 'generation',
      meta: {
        title: '发布管理',
        roles: ['teacher'],
      },
      component: () => import('@/views/GenerationView.vue'),
    },
    { path: '/readiness', redirect: '/quality' },
    {
      path: '/quality',
      name: 'quality',
      meta: {
        title: '发布质检',
        roles: ['teacher'],
      },
      component: () => import('@/views/ReadinessView.vue'),
    },
    {
      path: '/tasks/:taskId',
      name: 'task-detail',
      meta: {
        title: '资源任务',
        roles: ['student', 'teacher'],
      },
      component: () => import('@/views/TaskDetailView.vue'),
    },
    {
      path: '/learning',
      name: 'learning',
      meta: {
        title: 'AI 辅导',
        roles: ['student'],
      },
      component: () => import('@/views/LearningView.vue'),
    },
    {
      path: '/agents',
      name: 'agents',
      meta: {
        title: '智能体协同',
        roles: ['teacher'],
      },
      component: () => import('@/views/AgentsView.vue'),
    },
    {
      path: '/settings',
      name: 'settings',
      meta: {
        title: '模型设置',
        roles: ['student', 'teacher'],
      },
      component: () => import('@/views/SettingsView.vue'),
    },
    {
      path: '/teacher',
      name: 'teacher',
      meta: {
        title: '教师工作台',
        roles: ['teacher'],
      },
      component: () => import('@/views/TeacherView.vue'),
    },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach((to, _from, next) => {
  const app = useAppStore()
  const title = typeof to.meta.title === 'string' ? to.meta.title : '智学工坊'
  document.title = `智学工坊 ${title}`

  const isLoggedIn = app.isLoggedIn
  const roles = (to.meta.roles as string[] | undefined) ?? ['student', 'teacher']
  const hasTeacherOnly = roles.length === 1 && roles[0] === 'teacher'
  const hasStudentOnly = roles.length === 1 && roles[0] === 'student'

  if (!isLoggedIn) return to.path === '/' ? next() : next('/')

  if (to.path === '/') {
    return next(app.role === 'teacher' ? '/teacher' : '/dashboard')
  }

  if ((hasTeacherOnly && app.role !== 'teacher') || (hasStudentOnly && app.role !== 'student')) {
    return next({
      path: app.role === 'teacher' ? '/teacher' : '/dashboard',
      query: { access: app.role === 'teacher' ? 'teacher-workspace' : 'student-workspace' },
    })
  }

  return next()
})

export default router
