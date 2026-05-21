<script setup lang="ts">
defineProps<{ show?: boolean; text?: string }>()
</script>

<template>
  <div v-if="show" class="loading-block">
    <span class="spinner" />
    <span>{{ text || '正在加载' }}</span>
  </div>
</template>
