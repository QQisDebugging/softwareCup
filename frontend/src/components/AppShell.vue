<script setup lang="ts">
import {
  Activity,
  Bot,
  BrainCircuit,
  ClipboardCheck,
  FileText,
  GraduationCap,
  Home,
  Layers3,
  Network,
  RefreshCw,
  Route,
  ShieldCheck,
  Sparkles,
  Users,
} from 'lucide-vue-next'
import { onMounted } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import StatusPill from '@/components/StatusPill.vue'
import { apiBaseUrl } from '@/api'

const route = useRoute()
const app = useAppStore()

const nav = [
  { path: '/dashboard', label: '演示总览', icon: Home },
  { path: '/profiles', label: '学生画像', icon: BrainCircuit },
  { path: '/courses', label: '课程资源', icon: GraduationCap },
  { path: '/generation', label: '资源生成', icon: Sparkles },
  { path: '/learning', label: '学习闭环', icon: Route },
  { path: '/agents', label: '智能体工具箱', icon: Bot },
  { path: '/teacher', label: '教师分析', icon: Users },
  { path: '/demo', label: '评委模式', icon: ClipboardCheck },
]

onMounted(() => {
  void app.refreshHealth()
})
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar">
      <RouterLink class="brand" to="/dashboard" aria-label="SoftwareCup">
        <Network :size="24" />
        <div>
          <strong>SoftwareCup</strong>
          <span>Learning Agents</span>
        </div>
      </RouterLink>

      <nav class="nav-list" aria-label="main">
        <RouterLink v-for="item in nav" :key="item.path" :to="item.path" class="nav-item">
          <component :is="item.icon" :size="19" />
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>

      <div class="sidebar-foot">
        <div class="mini-stack">
          <Layers3 :size="18" />
          <span>Spring Boot API</span>
        </div>
        <small>{{ apiBaseUrl }}</small>
      </div>
    </aside>

    <div class="workspace">
      <header class="topbar">
        <div>
          <p>当前视图</p>
          <h1>{{ String(route.meta.title || '演示总览') }}</h1>
        </div>
        <div class="topbar-actions">
          <StatusPill
            :status="app.backendOnline ? '后端在线' : app.healthError ? '后端离线' : '检测中'"
            :tone="app.backendOnline ? 'ok' : app.healthError ? 'danger' : 'warn'"
          />
          <button class="icon-button" title="刷新后端状态" @click="app.refreshHealth">
            <RefreshCw :size="18" />
          </button>
        </div>
      </header>

      <main class="page-scroll">
        <RouterView />
      </main>

      <footer class="app-footer">
        <span><Activity :size="16" /> 多智能体任务链</span>
        <span><ShieldCheck :size="16" /> 防幻觉审核</span>
        <span><FileText :size="16" /> 可下载证据</span>
      </footer>
    </div>
  </div>
</template>
