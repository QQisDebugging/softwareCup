<script setup lang="ts">
import { AlertTriangle } from 'lucide-vue-next'
import { computed } from 'vue'

const props = defineProps<{ message?: string }>()

const friendlyMessage = computed(() => {
  const message = String(props.message || '').trim()
  if (!message) return ''
  if (/Network Error|Failed to fetch|ERR_CONNECTION_REFUSED/i.test(message)) {
    return '后端连接失败：请确认 Spring Boot 后端已启动，并检查前端 API 地址。'
  }
  if (/timeout|ECONNABORTED/i.test(message)) {
    return '接口请求超时：请确认后端服务正常运行后重试。'
  }
  return message
})
</script>

<template>
  <div v-if="friendlyMessage" class="notice error-notice">
    <AlertTriangle :size="18" />
    <span>{{ friendlyMessage }}</span>
  </div>
</template>
