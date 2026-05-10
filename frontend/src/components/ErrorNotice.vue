<script setup lang="ts">
import { AlertTriangle } from 'lucide-vue-next'

defineProps<{ message?: string }>()
</script>

<template>
  <div v-if="message" class="notice error-notice">
    <AlertTriangle :size="18" />
    <span>{{ message }}</span>
  </div>
</template>
