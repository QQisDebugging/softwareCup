<script setup lang="ts">
import { Download, RefreshCw, Radio } from 'lucide-vue-next'
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
import { compact, formatDate, percent } from '@/utils/format'

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
const sseMessage = ref('')
let eventSource: EventSource | null = null

const createdResource = computed(() =>
  resources.value.find((item) => item.id === task.value?.createdResourceId || item.sourceTaskId === task.value?.id),
)
const resourceMarkdown = computed(() => createdResource.value?.content || task.value?.resultSummary || '')
const taskProgress = computed(() => Math.round(percent(task.value?.progressPercent || 0)))
const canDownloadAudit = computed(() => audits.value.length > 0)

function statusTone(status?: string | null): 'ok' | 'warn' | 'danger' | 'info' | 'muted' {
  const value = String(status || '').toUpperCase()
  if (['SUCCEEDED', 'SUCCESS', 'PASSED', 'UP', 'COMPLETED'].includes(value)) return 'ok'
  if (['FAILED', 'ERROR', 'REJECTED', 'BLOCKED'].includes(value)) return 'danger'
  if (['RUNNING', 'PENDING', 'PROCESSING', 'UNKNOWN'].includes(value)) return 'warn'
  return 'info'
}

async function loadAll() {
  if (!taskId.value) {
    error.value = '任务 ID 为空，请从资源生成页面重新进入任务详情。'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const taskResult = await tasksApi.get(taskId.value)
    task.value = taskResult
    const [stepResult, invocationResult, auditResult] = await Promise.allSettled([
      tasksApi.steps(taskId.value),
      tasksApi.modelInvocations(taskId.value),
      tasksApi.audits(taskId.value),
    ])
    steps.value = stepResult.status === 'fulfilled' ? stepResult.value : []
    invocations.value = invocationResult.status === 'fulfilled' ? invocationResult.value : []
    audits.value = auditResult.status === 'fulfilled' ? auditResult.value : []
    if (taskResult.courseId) {
      try {
        resources.value = await coursesApi.resources(taskResult.courseId)
      } catch {
        resources.value = []
      }
    }
    const failures = [stepResult, invocationResult, auditResult].filter((item) => item.status === 'rejected').length
    if (failures) error.value = `任务主体已加载，但有 ${failures} 个明细接口暂不可用，可稍后刷新。`
  } catch (err) {
    error.value = err instanceof Error ? err.message : '任务加载失败'
  } finally {
    loading.value = false
  }
}

function connectSse() {
  if (!taskId.value) return
  eventSource?.close()
  sseStatus.value = 'connecting'
  sseMessage.value = ''
  try {
    eventSource = new EventSource(`${apiBaseUrl}/tasks/${taskId.value}/events`)
  } catch {
    sseStatus.value = 'closed'
    sseMessage.value = '实时连接创建失败，可手动刷新任务详情。'
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
    sseMessage.value = '实时连接已断开，可手动刷新任务详情。'
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

function downloadAuditJson() {
  if (!canDownloadAudit.value) return
  downloadJson(`${safeFilePart(task.value?.topic || 'task')}-audit.json`, audits.value)
}

function downloadMarkdown() {
  if (!resourceMarkdown.value) return
  downloadText(`${safeFilePart(createdResource.value?.title || task.value?.topic || 'resource')}.md`, resourceMarkdown.value, 'text/markdown;charset=utf-8')
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
        <button class="ghost-button" :disabled="!canDownloadAudit" @click="downloadAuditJson"><Download :size="17" />审核 JSON</button>
        <button class="ghost-button" :disabled="!resourceMarkdown" @click="downloadMarkdown"><Download :size="17" />资源 Markdown</button>
      </template>
      <ErrorNotice :message="error" />
      <LoadingBlock :show="loading" />
      <div v-if="!task && !loading" class="empty-guide">
        <strong>任务暂未加载</strong>
        <span>请从“资源生成”页面创建任务后进入详情，或确认后端任务接口可用。</span>
      </div>
      <div v-if="task" class="split-row">
        <div>
          <h3>{{ task.topic }}</h3>
          <p>{{ task.prompt }}</p>
          <div class="button-row">
            <StatusPill :status="task.status" :tone="statusTone(task.status)" />
            <StatusPill :status="task.currentStep || '等待步骤'" tone="info" />
          </div>
        </div>
        <div>
          <p>进度 {{ taskProgress }}%</p>
          <div class="progress-track"><div class="progress-fill" :style="{ width: `${taskProgress}%` }" /></div>
          <small>创建 {{ formatDate(task.createdAt) }} / 更新 {{ formatDate(task.updatedAt) }}</small>
          <p v-if="task.errorMessage" class="field-error">{{ task.errorMessage }}</p>
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
              <StatusPill :status="step.status" :tone="statusTone(step.status)" />
            </div>
            <p>{{ compact(step.outputSummary || step.inputSummary, 180) }}</p>
            <p v-if="step.errorMessage" class="field-error">{{ step.errorMessage }}</p>
            <div class="progress-track"><div class="progress-fill" :style="{ width: `${Math.round(percent(step.progressPercent))}%` }" /></div>
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
        <button class="ghost-button" :disabled="sseStatus === 'connecting'" @click="connectSse"><Radio :size="16" />重连</button>
      </template>
      <div v-if="sseMessage" class="notice warn-notice"><span>{{ sseMessage }}</span></div>
      <div v-if="!eventLog.length" class="empty-guide">
        <strong>等待 SSE 事件</strong>
        <span>如果实时连接断开，页面不会崩溃，可以点击重连或手动刷新。</span>
      </div>
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
            <StatusPill :status="audit.reviewerRequired ? `${audit.status} / 需复核` : audit.status" :tone="audit.reviewerRequired ? 'warn' : statusTone(audit.status)" />
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
              <td><StatusPill :status="item.fallbackUsed ? 'fallback' : item.status" :tone="item.fallbackUsed ? 'warn' : statusTone(item.status)" /></td>
              <td>{{ item.latencyMs }} ms</td>
            </tr>
          </tbody>
        </table>
      </div>
    </SectionPanel>

    <SectionPanel class="span-12" title="生成资源正文">
      <div v-if="!resourceMarkdown" class="empty-guide">
        <strong>任务完成后显示资源正文</strong>
        <span>如果任务已完成但没有正文，请刷新或检查课程资源接口。</span>
      </div>
      <MarkdownView v-else :content="resourceMarkdown" />
    </SectionPanel>

    <SectionPanel class="span-12" title="调试 JSON">
      <JsonBlock :value="{ task, steps, audits, invocations, createdResource }" />
    </SectionPanel>
  </div>
</template>
