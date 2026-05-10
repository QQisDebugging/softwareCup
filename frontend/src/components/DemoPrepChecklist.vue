<script setup lang="ts">
import { CheckCircle2, Clipboard, RefreshCw, Server, Terminal, XCircle } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { apiBaseUrl, healthApi } from '@/api'
import StatusPill from '@/components/StatusPill.vue'
import { copyText } from '@/utils/download'

type ProbeStatus = 'checking' | 'up' | 'down'

const javaStatus = ref<ProbeStatus>('checking')
const pythonStatus = ref<ProbeStatus>('checking')
const copied = ref('')
const checking = ref(false)

const pythonHealthUrl = 'http://localhost:9001/health'
const javaHealthUrl = `${apiBaseUrl}/health`

const commands = [
  {
    key: 'python',
    title: '启动 Python Agent',
    command:
      'cd D:\\competiton\\software\\softwareCup\\agents\\resource-agent\n.\\.venv\\Scripts\\Activate.ps1\nuvicorn main:app --host 0.0.0.0 --port 9001 --reload',
  },
  {
    key: 'backend',
    title: '启动 Spring Boot 后端',
    command: 'cd D:\\competiton\\software\\softwareCup\\backend\n.\\mvnw.cmd spring-boot:run',
  },
  {
    key: 'frontend',
    title: '启动 Vue3 前端',
    command: 'cd D:\\competiton\\software\\softwareCup\\frontend\nnpm.cmd run dev -- --port 5173',
  },
]

const javaText = computed(() => (javaStatus.value === 'up' ? '后端在线' : javaStatus.value === 'checking' ? '检测中' : '需要启动后端'))
const pythonText = computed(() =>
  pythonStatus.value === 'up' ? 'Agent 在线' : pythonStatus.value === 'checking' ? '检测中' : '需要启动 Python Agent',
)

async function checkServices() {
  checking.value = true
  javaStatus.value = 'checking'
  pythonStatus.value = 'checking'
  const [javaResult, pythonResult] = await Promise.allSettled([
    healthApi.getHealth(),
    fetch(pythonHealthUrl, { method: 'GET' }).then((response) => {
      if (!response.ok) throw new Error(String(response.status))
      return response.json()
    }),
  ])
  javaStatus.value = javaResult.status === 'fulfilled' && String(javaResult.value.status || '').toUpperCase() === 'UP' ? 'up' : 'down'
  pythonStatus.value = pythonResult.status === 'fulfilled' ? 'up' : 'down'
  checking.value = false
}

async function copyCommand(key: string, command: string) {
  await copyText(command)
  copied.value = key
  window.setTimeout(() => {
    if (copied.value === key) copied.value = ''
  }, 1600)
}

onMounted(checkServices)
</script>

<template>
  <div class="prep-list">
    <div class="prep-status-grid">
      <div class="prep-status">
        <Server :size="18" />
        <div>
          <strong>Java 后端</strong>
          <small>{{ javaHealthUrl }}</small>
        </div>
        <StatusPill :status="javaText" :tone="javaStatus === 'up' ? 'ok' : javaStatus === 'checking' ? 'warn' : 'danger'" />
      </div>
      <div class="prep-status">
        <Server :size="18" />
        <div>
          <strong>Python Agent</strong>
          <small>{{ pythonHealthUrl }}</small>
        </div>
        <StatusPill :status="pythonText" :tone="pythonStatus === 'up' ? 'ok' : pythonStatus === 'checking' ? 'warn' : 'danger'" />
      </div>
      <div class="prep-status">
        <Terminal :size="18" />
        <div>
          <strong>前端 API 地址</strong>
          <small>{{ apiBaseUrl }}</small>
        </div>
        <button class="ghost-button" :disabled="checking" @click="checkServices"><RefreshCw :size="16" />重新检测</button>
      </div>
    </div>

    <div class="command-grid">
      <article v-for="item in commands" :key="item.key" class="command-card">
        <div class="section-head">
          <strong>{{ item.title }}</strong>
          <button class="ghost-button" @click="copyCommand(item.key, item.command)">
            <Clipboard v-if="copied !== item.key" :size="16" />
            <CheckCircle2 v-else :size="16" />
            {{ copied === item.key ? '已复制' : '复制命令' }}
          </button>
        </div>
        <pre><code>{{ item.command }}</code></pre>
      </article>
    </div>

    <div v-if="javaStatus === 'down' || pythonStatus === 'down'" class="notice warn-notice">
      <XCircle :size="18" />
      <span>如果接口返回空或失败，先按上面的顺序启动 Python Agent、Spring Boot 后端，再刷新前端页面。</span>
    </div>
  </div>
</template>
