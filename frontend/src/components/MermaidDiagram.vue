<script setup lang="ts">
import mermaid from 'mermaid'
import { ref, watch, onMounted } from 'vue'

const props = defineProps<{ code?: string | null }>()

const container = ref<HTMLElement | null>(null)
const errored = ref(false)
let initialized = false
let renderSeq = 0

function ensureInit() {
  if (initialized) return
  mermaid.initialize({
    startOnLoad: false,
    theme: 'neutral',
    securityLevel: 'strict',
    fontFamily: 'inherit',
  })
  initialized = true
}

// 后端返回的 mermaid 字符串常被 ```mermaid ... ``` 围栏包裹，渲染前剥离
function normalize(raw: string): string {
  return raw
    .replace(/^\s*```(?:mermaid)?\s*/i, '')
    .replace(/```\s*$/i, '')
    .trim()
}

async function render() {
  const el = container.value
  const source = normalize(props.code || '')
  if (!el) return
  if (!source) {
    el.innerHTML = ''
    errored.value = false
    return
  }
  ensureInit()
  const seq = ++renderSeq
  try {
    const { svg } = await mermaid.render(`mmd-${seq}-${Date.now()}`, source)
    if (seq !== renderSeq) return // 已有更新的渲染，丢弃旧结果
    el.innerHTML = svg
    errored.value = false
  } catch {
    if (seq !== renderSeq) return
    errored.value = true
    el.innerHTML = ''
  }
}

onMounted(render)
watch(() => props.code, render)
</script>

<template>
  <div class="mermaid-diagram">
    <div v-show="!errored" ref="container" class="mermaid-canvas" />
    <pre v-if="errored" class="mermaid-fallback">{{ code }}</pre>
  </div>
</template>

<style scoped>
.mermaid-diagram {
  width: 100%;
  overflow-x: auto;
}
.mermaid-canvas {
  display: flex;
  justify-content: center;
}
.mermaid-canvas :deep(svg) {
  max-width: 100%;
  height: auto;
}
.mermaid-fallback {
  margin: 0;
  padding: 12px;
  background: #f6fafb;
  border: 1px solid #dde7ef;
  border-radius: 10px;
  font-size: 12px;
  color: #5a6f82;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
