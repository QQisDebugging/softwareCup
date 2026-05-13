<script setup lang="ts">
import { computed } from 'vue'
import { hasMeaningfulValue, parseMaybeJson, safeStringify } from '@/utils/format'

const props = defineProps<{
  value: unknown
  maxHeight?: string
}>()

const parsed = computed(() => {
  if (!hasMeaningfulValue(props.value)) {
    return { text: '{}', note: '暂无 JSON 数据' }
  }
  if (typeof props.value === 'string') {
    const parsedValue = parseMaybeJson(props.value, null)
    if (parsedValue === null) {
      return { text: props.value, note: '内容不是标准 JSON，已按文本展示' }
    }
    return { text: safeStringify(parsedValue), note: '' }
  }
  return { text: safeStringify(props.value), note: '' }
})
</script>

<template>
  <div class="json-shell">
    <small v-if="parsed.note" class="json-note">{{ parsed.note }}</small>
    <pre class="json-block" :style="{ maxHeight: maxHeight || '360px' }"><code>{{ parsed.text }}</code></pre>
  </div>
</template>
