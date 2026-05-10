<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  value: unknown
  maxHeight?: string
}>()

const formatted = computed(() => JSON.stringify(props.value ?? {}, null, 2))
</script>

<template>
  <pre class="json-block" :style="{ maxHeight: maxHeight || '360px' }"><code>{{ formatted }}</code></pre>
</template>
