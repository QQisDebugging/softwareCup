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

const radarOption = computed<EChartsOption>(() => {
  const dimensions = selected.value?.dimensions || []
  return {
    tooltip: {},
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
            value: dimensions.map((item) => Math.round(percent(item.confidenceScore))),
          },
        ],
      },
    ],
  }
})

function requestBody(): BuildProfileRequest {
  return {
    studentName: form.studentName,
    major: form.major,
    currentLevel: form.currentLevel,
    learningGoal: form.learningGoal,
    preferences: form.preferences,
    constraintsText: form.constraintsText,
    dialogueTurns: form.dialogueTurns
      .split('\n')
      .map((item) => item.trim())
      .filter(Boolean),
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
  error.value = ''
  try {
    selected.value = await profilesApi.detail(profileId)
    history.value = await profilesApi.history(profileId)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '画像详情加载失败'
  }
}

async function submit() {
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
  if (!selected.value) return
  downloadJson(`${safeFilePart(selected.value.profile.studentName)}-profile.json`, selected.value)
}

function downloadProfileMarkdown() {
  if (!selected.value) return
  const profile = selected.value.profile
  const lines = [
    `# ${profile.studentName} 学习画像`,
    '',
    `- 专业：${profile.major}`,
    `- 当前基础：${profile.currentLevel}`,
    `- 学习目标：${profile.learningGoal}`,
    `- 资源偏好：${profile.preferences}`,
    '',
    '## 画像维度',
    ...selected.value.dimensions.map(
      (item) => `- **${item.dimensionName}**：${item.value}\n  - 证据：${item.evidence}\n  - 置信度：${Math.round(percent(item.confidenceScore))}%`,
    ),
    '',
    jsonToMarkdown('完整 JSON', selected.value),
  ]
  downloadText(`${safeFilePart(profile.studentName)}-profile.md`, lines.join('\n'), 'text/markdown;charset=utf-8')
}

onMounted(loadProfiles)
</script>

<template>
  <div class="page-grid">
    <SectionPanel class="span-5" title="对话式画像构建" subtitle="POST /api/profiles/dialogue">
      <ErrorNotice :message="error" />
      <form class="form-grid" @submit.prevent="submit">
        <div class="split-row">
          <div class="field">
            <label>学生姓名</label>
            <input v-model="form.studentName" required />
          </div>
          <div class="field">
            <label>专业</label>
            <input v-model="form.major" required />
          </div>
        </div>
        <div class="field">
          <label>当前水平</label>
          <input v-model="form.currentLevel" required />
        </div>
        <div class="field">
          <label>学习目标</label>
          <input v-model="form.learningGoal" required />
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
          <label>多轮对话</label>
          <textarea v-model="form.dialogueTurns" />
        </div>
        <button class="button" :disabled="loading"><Send :size="17" />生成画像</button>
      </form>
      <LoadingBlock :show="loading" text="正在抽取画像维度" />
    </SectionPanel>

    <SectionPanel class="span-7" title="画像结果" :subtitle="selected?.profile.dialogueSummary">
      <template #actions>
        <button class="ghost-button" :disabled="!selected" @click="downloadProfileJson"><Download :size="17" />JSON</button>
        <button class="ghost-button" :disabled="!selected" @click="downloadProfileMarkdown"><Download :size="17" />Markdown</button>
      </template>

      <div v-if="!selected" class="empty-state">请选择或创建画像</div>
      <template v-else>
        <div class="split-row">
          <div>
            <h3>{{ selected.profile.studentName }}</h3>
            <p>{{ selected.profile.major }} / {{ selected.profile.currentLevel }}</p>
            <StatusPill :status="`${selected.dimensions.length} 个画像维度`" tone="info" />
          </div>
          <ChartPanel v-if="selected.dimensions.length" :option="radarOption" :height="260" />
          <div v-else class="empty-state">暂无可视化维度</div>
        </div>
        <div class="timeline">
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
      </template>
    </SectionPanel>

    <SectionPanel class="span-6" title="画像列表">
      <template #actions>
        <button class="ghost-button" @click="loadProfiles"><RefreshCw :size="17" />刷新</button>
      </template>
      <LoadingBlock :show="listLoading" />
      <div v-if="!profiles.length" class="empty-state">暂无画像</div>
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
      <div v-if="!history.length" class="empty-state">暂无历史</div>
      <div v-else class="timeline">
        <div v-for="item in history" :key="item.id" class="timeline-body">
          <strong>{{ item.dimensionKey }}</strong>
          <p>{{ item.newValue }}</p>
          <small>{{ item.evidence || item.source }} / {{ formatDate(item.createdAt) }}</small>
        </div>
      </div>
    </SectionPanel>
  </div>
</template>
