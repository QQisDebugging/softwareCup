<script setup lang="ts">
import { AlertTriangle } from 'lucide-vue-next'
import { computed } from 'vue'

const props = defineProps<{ message?: string }>()

const friendlyMessage = computed(() => {
  const message = String(props.message || '').trim()
  if (!message) return ''
  if (/Network Error|Failed to fetch|ERR_CONNECTION_REFUSED/i.test(message)) {
    return '学习服务连接失败：请确认服务已启动后重试。'
  }
  if (/timeout|ECONNABORTED/i.test(message)) {
    return '请求等待时间较长，请稍后重试。'
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
