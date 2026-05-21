<script setup lang="ts">
import type { EChartsOption } from 'echarts'
import { Download, RefreshCw, Send } from 'lucide-vue-next'
import { computed, onMounted, reactive, ref } from 'vue'
import { profilesApi } from '@/api'
import ChartPanel from '@/components/ChartPanel.vue'
import ErrorNotice from '@/components/ErrorNotice.vue'
import LoadingBlock from '@/components/LoadingBlock.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import StatusPill from '@/components/StatusPill.vue'
import type { BuildProfileRequest, ProfileDetail, ProfileHistory, ProfileResponse } from '@/types/api'
import { downloadJson, downloadText, jsonToMarkdown, safeFilePart } from '@/utils/download'
import { formatDate, percent } from '@/utils/format'

const loading = ref(false)
const listLoading = ref(false)
const selectedLoading = ref(false)
const error = ref('')
const profiles = ref<ProfileResponse[]>([])
const selected = ref<ProfileDetail | null>(null)
const history = ref<ProfileHistory[]>([])

const form = reactive({
  studentName: '张同学',
  major: '软件工程',
  currentLevel: '大二，Java 基础较弱，刚接触 Spring Boot',
  learningGoal: '两周内掌握 Spring Boot Controller、Service、Repository 分层开发',
  preferences: '喜欢图解、案例驱动和短视频脚本',
  constraintsText: '每天可学习 45 分钟，优先补基础和易错点',
  dialogueTurns:
    '系统：你希望提升哪门课？\n学生：Java Web 和 Spring Boot。\n系统：你最容易卡在哪里？\n学生：Controller、Service、Repository 分层总混。\n系统：你喜欢什么学习方式？\n学生：先图解，再做一个能跑的小项目。',
})

const dialogueLines = computed(() =>
  form.dialogueTurns
    .split('\n')
    .map((item) => item.trim())
    .filter(Boolean),
)

const formErrors = computed<Record<string, string>>(() => {
  const errors: Record<string, string> = {}
  if (!form.studentName.trim()) errors.studentName = '请输入学生姓名'
  if (!form.major.trim()) errors.major = '请输入专业'
  if (!form.currentLevel.trim()) errors.currentLevel = '请输入当前水平'
  if (!form.learningGoal.trim()) errors.learningGoal = '请输入学习目标'
  if (!dialogueLines.value.length) errors.dialogueTurns = '请至少输入一轮对话'
  return errors
})

const canSubmit = computed(() => !loading.value && Object.keys(formErrors.value).length === 0)
const canDownload = computed(() => Boolean(selected.value?.profile.studentName))
const selectedSummary = computed(() => selected.value?.profile.dialogueSummary || '暂无画像摘要')
const selectedDimensionCount = computed(() => selected.value?.dimensions.length || 0)

const radarOption = computed<EChartsOption>(() => {
  const dimensions = selected.value?.dimensions || []
  const data = dimensions.map((item) => Math.round(percent(item.confidenceScore)))
  return {
    tooltip: {},
    color: ['#2f6fef'],
    graphic: dimensions.length
      ? undefined
      : { type: 'text', left: 'center', top: 'middle', style: { text: '暂无画像维度', fill: '#61708a' } },
    radar: {
      indicator: dimensions.map((item) => ({ name: item.dimensionName || item.dimensionKey, max: 100 })),
      radius: '62%',
    },
    series: [
      {
        type: 'radar',
        areaStyle: { opacity: 0.18 },
        data: [
          {
            name: '置信度',
            value: data,
          },
        ],
      },
    ],
  }
})

function requestBody(): BuildProfileRequest {
  return {
    studentName: form.studentName.trim(),
    major: form.major.trim(),
    currentLevel: form.currentLevel.trim(),
    learningGoal: form.learningGoal.trim(),
    preferences: form.preferences.trim(),
    constraintsText: form.constraintsText.trim(),
    dialogueTurns: dialogueLines.value,
  }
}

async function loadProfiles() {
  listLoading.value = true
  error.value = ''
  try {
    profiles.value = await profilesApi.list()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '画像列表加载失败'
  } finally {
    listLoading.value = false
  }
}

async function selectProfile(profileId: string) {
  if (!profileId) return
  selectedLoading.value = true
  error.value = ''
  try {
    const [detailResult, historyResult] = await Promise.allSettled([
      profilesApi.detail(profileId),
      profilesApi.history(profileId),
    ])
    if (detailResult.status === 'fulfilled') {
      selected.value = detailResult.value
    } else {
      selected.value = null
      throw detailResult.reason
    }
    if (historyResult.status === 'fulfilled') {
      history.value = historyResult.value
    } else {
      history.value = selected.value.recentHistory || []
      error.value = '画像详情已加载，但历史记录接口暂不可用。'
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '画像详情加载失败'
  } finally {
    selectedLoading.value = false
  }
}

async function submit() {
  if (!canSubmit.value) {
    error.value = Object.values(formErrors.value)[0] || '请先补全画像创建表单。'
    return
  }
  loading.value = true
  error.value = ''
  try {
    selected.value = await profilesApi.createFromDialogue(requestBody())
    history.value = selected.value.recentHistory || []
    await loadProfiles()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '画像创建失败'
  } finally {
    loading.value = false
  }
}

function downloadProfileJson() {
  if (!canDownload.value || !selected.value) return
  downloadJson(`${safeFilePart(selected.value.profile.studentName)}-profile.json`, selected.value)
}

function downloadProfileMarkdown() {
  if (!canDownload.value || !selected.value) return
  const profile = selected.value.profile
  const lines = [
    `# ${profile.studentName} 学习画像`,
    '',
    `- 专业：${profile.major}`,
    `- 当前基础：${profile.currentLevel}`,
    `- 学习目标：${profile.learningGoal}`,
    `- 资源偏好：${profile.preferences}`,
    `- 时间约束：${profile.constraintsText}`,
    '',
    `## 画像摘要`,
    selectedSummary.value,
    '',
    '## 画像维度',
    ...(selected.value.dimensions.length
      ? selected.value.dimensions.map(
          (item) =>
            `- **${item.dimensionName}**：${item.value}\n  - 证据：${item.evidence}\n  - 来源：${item.source}\n  - 置信度：${Math.round(percent(item.confidenceScore))}%`,
        )
      : ['暂无画像维度']),
    '',
    '## 演化历史',
    ...(history.value.length
      ? history.value.map((item) => `- ${formatDate(item.createdAt)} ${item.dimensionKey}：${item.newValue}\n  - 证据：${item.evidence}`)
      : ['暂无演化历史']),
    '',
    jsonToMarkdown('完整 JSON', selected.value),
  ]
  downloadText(`${safeFilePart(profile.studentName)}-profile.md`, lines.join('\n'), 'text/markdown;charset=utf-8')
}

onMounted(loadProfiles)
</script>

<template>
  <div class="page-grid">
    <SectionPanel class="span-12" title="画像演示链路" subtitle="创建画像后，系统会展示维度证据、置信度雷达图、历史演化与可下载报告">
      <div class="profile-flow">
        <div class="profile-flow-item">
          <span>1</span>
          <strong>输入多轮对话</strong>
          <small>每行一轮，自动过滤空行</small>
        </div>
        <div class="profile-flow-item">
          <span>2</span>
          <strong>后端生成画像</strong>
          <small>POST /api/profiles/dialogue</small>
        </div>
        <div class="profile-flow-item">
          <span>3</span>
          <strong>展示维度证据</strong>
          <small>雷达图 + 证据卡片</small>
        </div>
        <div class="profile-flow-item">
          <span>4</span>
          <strong>导出答辩材料</strong>
          <small>JSON / Markdown 报告</small>
        </div>
      </div>
    </SectionPanel>

    <SectionPanel class="span-5" title="对话式画像构建" subtitle="POST /api/profiles/dialogue">
      <ErrorNotice :message="error" />
      <form class="form-grid" @submit.prevent="submit">
        <div class="split-row">
          <div class="field">
            <label>学生姓名 <span class="required-mark">*</span></label>
            <input v-model="form.studentName" required />
            <small v-if="formErrors.studentName" class="field-error">{{ formErrors.studentName }}</small>
          </div>
          <div class="field">
            <label>专业 <span class="required-mark">*</span></label>
            <input v-model="form.major" required />
            <small v-if="formErrors.major" class="field-error">{{ formErrors.major }}</small>
          </div>
        </div>
        <div class="field">
          <label>当前水平 <span class="required-mark">*</span></label>
          <input v-model="form.currentLevel" required />
          <small v-if="formErrors.currentLevel" class="field-error">{{ formErrors.currentLevel }}</small>
        </div>
        <div class="field">
          <label>学习目标 <span class="required-mark">*</span></label>
          <input v-model="form.learningGoal" required />
          <small v-if="formErrors.learningGoal" class="field-error">{{ formErrors.learningGoal }}</small>
        </div>
        <div class="field">
          <label>偏好</label>
          <input v-model="form.preferences" />
        </div>
        <div class="field">
          <label>时间约束</label>
          <input v-model="form.constraintsText" />
        </div>
        <div class="field">
          <label>多轮对话 <span class="required-mark">*</span></label>
          <textarea v-model="form.dialogueTurns" />
          <small class="field-help">当前有效对话 {{ dialogueLines.length }} 行；空行会在提交时自动过滤。</small>
          <small v-if="formErrors.dialogueTurns" class="field-error">{{ formErrors.dialogueTurns }}</small>
        </div>
        <button class="button" :disabled="!canSubmit"><Send :size="17" />生成画像</button>
      </form>
      <LoadingBlock :show="loading" text="正在抽取画像维度" />
    </SectionPanel>

    <SectionPanel class="span-7" title="画像结果" :subtitle="selectedSummary">
      <template #actions>
        <button class="ghost-button" :disabled="!canDownload" @click="downloadProfileJson"><Download :size="17" />JSON</button>
        <button class="ghost-button" :disabled="!canDownload" @click="downloadProfileMarkdown"><Download :size="17" />Markdown</button>
      </template>

      <LoadingBlock :show="selectedLoading" text="正在加载画像详情" />
      <div v-if="!selected && !selectedLoading" class="empty-guide">
        <strong>请选择或创建画像</strong>
        <span>比赛演示时可以直接使用左侧预置表单生成画像，也可以从下方列表选择已有学生。</span>
      </div>
      <template v-else>
        <div v-if="selected" class="split-row">
          <div class="profile-hero">
            <h3>{{ selected.profile.studentName }}</h3>
            <p>{{ selected.profile.major }} / {{ selected.profile.currentLevel }}</p>
            <p>{{ selected.profile.learningGoal }}</p>
            <div class="button-row">
              <StatusPill :status="`${selectedDimensionCount} 个画像维度`" tone="info" />
              <StatusPill :status="history.length ? `${history.length} 条历史` : '暂无历史'" :tone="history.length ? 'ok' : 'muted'" />
            </div>
          </div>
          <ChartPanel v-if="selected.dimensions.length" :option="radarOption" :height="260" />
          <div v-else class="empty-state">暂无可视化维度</div>
        </div>
        <div v-if="selected?.dimensions.length" class="timeline">
          <div v-for="dimension in selected.dimensions" :key="dimension.id" class="timeline-item">
            <span class="timeline-index">{{ Math.round(percent(dimension.confidenceScore)) }}</span>
            <div class="timeline-body">
              <div class="section-head">
                <div>
                  <h3>{{ dimension.dimensionName }}</h3>
                  <p>{{ dimension.dimensionKey }} / {{ dimension.source }}</p>
                </div>
                <StatusPill :status="`${Math.round(percent(dimension.confidenceScore))}%`" tone="ok" />
              </div>
              <p>{{ dimension.value }}</p>
              <small>{{ dimension.evidence }}</small>
            </div>
          </div>
        </div>
        <div v-else-if="selected" class="empty-state">后端暂未返回画像维度，页面已保留结果区等待刷新。</div>
      </template>
    </SectionPanel>

    <SectionPanel class="span-6" title="画像列表">
      <template #actions>
        <button class="ghost-button" @click="loadProfiles"><RefreshCw :size="17" />刷新</button>
      </template>
      <LoadingBlock :show="listLoading" />
      <div v-if="!profiles.length && !listLoading" class="empty-guide">
        <strong>暂无画像</strong>
        <span>先使用上方表单生成第一个学生画像；如果后端离线，请启动 Spring Boot 后再刷新。</span>
      </div>
      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>学生</th>
              <th>专业</th>
              <th>目标</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="profile in profiles" :key="profile.id" class="clickable-row" @click="selectProfile(profile.id)">
              <td>{{ profile.studentName }}</td>
              <td>{{ profile.major }}</td>
              <td>{{ profile.learningGoal }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </SectionPanel>

    <SectionPanel class="span-6" title="画像演化历史">
      <div v-if="!history.length" class="empty-guide">
        <strong>暂无历史</strong>
        <span>创建或更新画像维度后，这里会展示画像信号的变化证据。</span>
      </div>
      <div v-else class="timeline">
        <div v-for="item in history" :key="item.id" class="timeline-body">
          <div class="section-head">
            <div>
              <strong>{{ item.dimensionKey }}</strong>
              <p>{{ item.eventType }}</p>
            </div>
            <StatusPill :status="formatDate(item.createdAt)" tone="muted" />
          </div>
          <p>{{ item.newValue }}</p>
          <small>{{ item.evidence || item.source }}</small>
        </div>
      </div>
    </SectionPanel>
  </div>
</template>
