import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/dashboard' },
    {
      path: '/dashboard',
      name: 'dashboard',
      meta: { title: '演示总览' },
      component: () => import('@/views/DashboardView.vue'),
    },
    {
      path: '/profiles',
      name: 'profiles',
      meta: { title: '学生画像' },
      component: () => import('@/views/ProfilesView.vue'),
    },
    {
      path: '/courses',
      name: 'courses',
      meta: { title: '课程资源' },
      component: () => import('@/views/CoursesView.vue'),
    },
    {
      path: '/generation',
      name: 'generation',
      meta: { title: '资源生成' },
      component: () => import('@/views/GenerationView.vue'),
    },
    {
      path: '/tasks/:taskId',
      name: 'task-detail',
      meta: { title: '任务详情' },
      component: () => import('@/views/TaskDetailView.vue'),
    },
    {
      path: '/learning',
      name: 'learning',
      meta: { title: '学习闭环' },
      component: () => import('@/views/LearningView.vue'),
    },
    {
      path: '/agents',
      name: 'agents',
      meta: { title: '智能体工具箱' },
      component: () => import('@/views/AgentsView.vue'),
    },
    {
      path: '/teacher',
      name: 'teacher',
      meta: { title: '教师分析' },
      component: () => import('@/views/TeacherView.vue'),
    },
    {
      path: '/demo',
      name: 'demo',
      meta: { title: '评委模式' },
      component: () => import('@/views/DemoView.vue'),
    },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

export default router
