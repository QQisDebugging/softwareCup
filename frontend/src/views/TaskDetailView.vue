<script setup lang="ts">
import { Download, RefreshCw } from 'lucide-vue-next'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { apiBaseUrl, coursesApi, tasksApi } from '@/api'
import ErrorNotice from '@/components/ErrorNotice.vue'
import JsonBlock from '@/components/JsonBlock.vue'
import LoadingBlock from '@/components/LoadingBlock.vue'
import MarkdownView from '@/components/MarkdownView.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import StatusPill from '@/components/StatusPill.vue'
import type { GenerationAudit, GenerationTask, LearningResource, ModelInvocation, TaskStep } from '@/types/api'
import { downloadJson, downloadText, safeFilePart } from '@/utils/download'
import { compact, formatDate } from '@/utils/format'

const route = useRoute()
const taskId = computed(() => String(route.params.taskId || ''))
const loading = ref(false)
const error = ref('')
const task = ref<GenerationTask | null>(null)
const steps = ref<TaskStep[]>([])
const invocations = ref<ModelInvocation[]>([])
const audits = ref<GenerationAudit[]>([])
const resources = ref<LearningResource[]>([])
const eventLog = ref<string[]>([])
const sseStatus = ref<'connecting' | 'connected' | 'closed'>('closed')
let eventSource: EventSource | null = null

const createdResource = computed(() =>
  resources.value.find((item) => item.id === task.value?.createdResourceId || item.sourceTaskId === task.value?.id),
)

async function loadAll() {
  loading.value = true
  error.value = ''
  try {
    const taskResult = await tasksApi.get(taskId.value)
    task.value = taskResult
    const [stepResult, invocationResult, auditResult] = await Promise.all([
      tasksApi.steps(taskId.value),
      tasksApi.modelInvocations(taskId.value),
      tasksApi.audits(taskId.value),
    ])
    steps.value = stepResult
    invocations.value = invocationResult
    audits.value = auditResult
    if (taskResult.courseId) {
      resources.value = await coursesApi.resources(taskResult.courseId)
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '任务加载失败'
  } finally {
    loading.value = false
  }
}

function connectSse() {
  eventSource?.close()
  sseStatus.value = 'connecting'
  try {
    eventSource = new EventSource(`${apiBaseUrl}/tasks/${taskId.value}/events`)
  } catch {
    sseStatus.value = 'closed'
    return
  }
  eventSource.onopen = () => {
    sseStatus.value = 'connected'
  }
  eventSource.onmessage = (event) => {
    eventLog.value.unshift(event.data)
    if (eventLog.value.length > 8) eventLog.value.pop()
    void loadAll()
  }
  eventSource.onerror = () => {
    eventSource?.close()
    eventSource = null
    sseStatus.value = 'closed'
  }
}

function downloadTaskJson() {
  downloadJson(`${safeFilePart(task.value?.topic || 'task')}-task.json`, {
    task: task.value,
    steps: steps.value,
    invocations: invocations.value,
    audits: audits.value,
    resource: createdResource.value,
  })
}

function downloadMarkdown() {
  if (!createdResource.value) return
  downloadText(`${safeFilePart(createdResource.value.title)}.md`, createdResource.value.content || '', 'text/markdown;charset=utf-8')
}

onMounted(() => {
  void loadAll()
  connectSse()
})

onBeforeUnmount(() => eventSource?.close())
</script>

<template>
  <div class="page-grid">
    <SectionPanel class="span-12" title="任务概览">
      <template #actions>
        <button class="ghost-button" @click="loadAll"><RefreshCw :size="17" />刷新</button>
        <button class="ghost-button" :disabled="!task" @click="downloadTaskJson"><Download :size="17" />全量 JSON</button>
        <button class="ghost-button" :disabled="!createdResource" @click="downloadMarkdown"><Download :size="17" />资源 Markdown</button>
      </template>
      <ErrorNotice :message="error" />
      <LoadingBlock :show="loading" />
      <div v-if="task" class="split-row">
        <div>
          <h3>{{ task.topic }}</h3>
          <p>{{ task.prompt }}</p>
          <div class="button-row">
            <StatusPill :status="task.status" :tone="task.status === 'SUCCEEDED' ? 'ok' : task.status === 'FAILED' ? 'danger' : 'warn'" />
            <StatusPill :status="task.currentStep || '等待步骤'" tone="info" />
          </div>
        </div>
        <div>
          <p>进度 {{ task.progressPercent || 0 }}%</p>
          <div class="progress-track"><div class="progress-fill" :style="{ width: `${task.progressPercent || 0}%` }" /></div>
          <small>创建 {{ formatDate(task.createdAt) }} / 更新 {{ formatDate(task.updatedAt) }}</small>
        </div>
      </div>
    </SectionPanel>

    <SectionPanel class="span-7" title="多智能体步骤">
      <div v-if="!steps.length" class="empty-state">暂无步骤</div>
      <div v-else class="timeline">
        <div v-for="step in steps" :key="step.id" class="timeline-item">
          <span class="timeline-index">{{ step.stepOrder }}</span>
          <div class="timeline-body">
            <div class="section-head">
              <div>
                <h3>{{ step.stepName }}</h3>
                <p>{{ step.agentKey }}</p>
              </div>
              <StatusPill :status="step.status" :tone="step.status === 'SUCCEEDED' ? 'ok' : step.status === 'FAILED' ? 'danger' : 'warn'" />
            </div>
            <p>{{ compact(step.outputSummary || step.inputSummary, 180) }}</p>
            <div class="progress-track"><div class="progress-fill" :style="{ width: `${step.progressPercent || 0}%` }" /></div>
          </div>
        </div>
      </div>
    </SectionPanel>

    <SectionPanel class="span-5" title="实时事件">
      <template #actions>
        <StatusPill
          :status="sseStatus === 'connected' ? 'SSE 已连接' : sseStatus === 'connecting' ? 'SSE 连接中' : 'SSE 已断开'"
          :tone="sseStatus === 'connected' ? 'ok' : sseStatus === 'connecting' ? 'warn' : 'muted'"
        />
      </template>
      <div v-if="!eventLog.length" class="empty-state">等待 SSE 事件</div>
      <div v-else class="timeline">
        <div v-for="(event, index) in eventLog" :key="index" class="timeline-body">{{ event }}</div>
      </div>
    </SectionPanel>

    <SectionPanel class="span-6" title="防幻觉与安全审核">
      <div v-if="!audits.length" class="empty-state">暂无审核记录</div>
      <div v-else class="timeline">
        <div v-for="audit in audits" :key="audit.id" class="timeline-body">
          <div class="section-head">
            <strong>{{ audit.auditType }}</strong>
            <StatusPill :status="audit.status" :tone="audit.reviewerRequired ? 'warn' : 'ok'" />
          </div>
          <p>{{ audit.evidenceSummary }}</p>
          <small>{{ formatDate(audit.createdAt) }}</small>
        </div>
      </div>
    </SectionPanel>

    <SectionPanel class="span-6" title="模型调用记录">
      <div v-if="!invocations.length" class="empty-state">暂无模型调用</div>
      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Provider</th>
              <th>模型</th>
              <th>状态</th>
              <th>耗时</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in invocations" :key="item.id">
              <td>{{ item.provider }}</td>
              <td>{{ item.modelName }}</td>
              <td><StatusPill :status="item.fallbackUsed ? 'fallback' : item.status" :tone="item.fallbackUsed ? 'warn' : 'ok'" /></td>
              <td>{{ item.latencyMs }} ms</td>
            </tr>
          </tbody>
        </table>
      </div>
    </SectionPanel>

    <SectionPanel class="span-12" title="生成资源正文">
      <div v-if="!createdResource" class="empty-state">任务完成后显示资源正文</div>
      <MarkdownView v-else :content="createdResource.content" />
    </SectionPanel>

    <SectionPanel class="span-12" title="调试 JSON">
      <JsonBlock :value="{ task, steps, audits, invocations, createdResource }" />
    </SectionPanel>
  </div>
</template>
