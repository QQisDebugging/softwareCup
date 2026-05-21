import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { healthApi } from '@/api'
import type { HealthResponse } from '@/types/api'

export const useAppStore = defineStore('app', () => {
  const health = ref<HealthResponse | null>(null)
  const healthError = ref('')
  const checking = ref(false)

  const backendOnline = computed(() => String(health.value?.status || '').toUpperCase() === 'UP')

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

  return { health, healthError, checking, backendOnline, refreshHealth }
})
