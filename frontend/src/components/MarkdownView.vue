<script setup lang="ts">
import MarkdownIt from 'markdown-it'
import { computed } from 'vue'
import { cleanDisplayText, hasMeaningfulValue } from '@/utils/format'

const props = defineProps<{ content?: string | null }>()

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
})

// 后端常把换行编码成字面量 <br>，并把标题、代码块挤在同一行，
// 导致 markdown-it 无法识别块级结构、<br> 被转义成纯文本。
// 渲染前先把这些标记还原成真实换行，让 Markdown 正常解析。
function normalizeForMarkdown(text: string) {
  if (!text) return ''
  return text
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/\r\n/g, '\n')
    // 行内出现的 ``` 代码围栏前后补换行，确保被识别为代码块
    .replace(/([^\n])(```)/g, '$1\n$2')
    .replace(/(```[^\n]*)\n?/g, '$1\n')
    // 行内出现的 Markdown 标题（#、##…）前补换行
    .replace(/([^\n])(#{1,6}\s)/g, '$1\n\n$2')
    // 合并多余空行
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}

const content = computed(() => normalizeForMarkdown(cleanDisplayText(props.content)))
const hasContent = computed(() => hasMeaningfulValue(content.value))
const rendered = computed(() => md.render(content.value))
</script>

<template>
  <div v-if="!hasContent" class="empty-state">暂无 Markdown 内容</div>
  <article v-else class="markdown-body" v-html="rendered" />
</template>
