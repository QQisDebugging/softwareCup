<script setup lang="ts">
import MarkdownIt from 'markdown-it'
import { computed } from 'vue'
import { hasMeaningfulValue } from '@/utils/format'

const props = defineProps<{ content?: string | null }>()

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
})

const hasContent = computed(() => hasMeaningfulValue(props.content))
const rendered = computed(() => md.render(props.content || ''))
</script>

<template>
  <div v-if="!hasContent" class="empty-state">暂无 Markdown 内容</div>
  <article v-else class="markdown-body" v-html="rendered" />
</template>
