<script setup lang="ts">
defineProps<{ show?: boolean; text?: string }>()
</script>

<template>
  <div v-if="show" class="loading-block-skeleton" aria-busy="true" aria-live="polite">
    <div class="skeleton-line" style="width: 40%"></div>
    <div class="skeleton-line" style="width: 80%"></div>
    <div class="skeleton-line" style="width: 60%"></div>
  </div>
</template>

<style scoped>
.loading-block-skeleton {
  display: grid;
  gap: 12px;
  padding: 16px 0;
  width: 100%;
}

.skeleton-line {
  height: 12px;
  background: linear-gradient(90deg, var(--surface-hover) 25%, var(--line) 50%, var(--surface-hover) 75%);
  background-size: 400% 100%;
  border-radius: var(--radius-sm);
  animation: shimmer 1.5s infinite var(--ease-prod);
}

@keyframes shimmer {
  0% {
    background-position: 100% 0;
  }
  100% {
    background-position: -100% 0;
  }
}
</style>
