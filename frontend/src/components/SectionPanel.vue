<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
}>()
</script>

<template>
  <section class="section-panel">
    <header class="section-head">
      <div>
        <h2>{{ title }}</h2>
      </div>
      <slot name="actions" />
    </header>
    <slot />
  </section>
</template>
