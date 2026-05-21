<script setup lang="ts">
defineProps<{
  status?: string | number | boolean | null
  tone?: 'ok' | 'warn' | 'danger' | 'info' | 'muted'
}>()
</script>

<template>
  <span class="status-pill" :class="tone || 'info'">{{ status ?? '-' }}</span>
</template>
