<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Bot, CheckCircle2, RefreshCw, Save, Server } from 'lucide-vue-next'
import { settingsApi, type ProviderConfigRequest, type ProviderStatus } from '@/api'
import ErrorNotice from '@/components/ErrorNotice.vue'
import LoadingBlock from '@/components/LoadingBlock.vue'

type ProviderKey = 'xfyun_spark' | 'openai_compatible'

interface PresetOption {
  label: string
  baseUrl: string
  model: string
  hint: string
}

// OpenAI 兼容供应商常用预设，选中后自动填入端点和默认模型
const openaiPresets: Record<string, PresetOption> = {
  deepseek: { label: 'DeepSeek', baseUrl: 'https://api.deepseek.com/v1', model: 'deepseek-chat', hint: '深度求索' },
  qwen: { label: '通义千问', baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1', model: 'qwen-plus', hint: '阿里云百炼' },
  zhipu: { label: '智谱 GLM', baseUrl: 'https://open.bigmodel.cn/api/paas/v4', model: 'glm-4-plus', hint: '智谱 AI' },
  kimi: { label: 'Kimi', baseUrl: 'https://api.moonshot.cn/v1', model: 'moonshot-v1-8k', hint: '月之暗面' },
  openai: { label: 'OpenAI', baseUrl: 'https://api.openai.com/v1', model: 'gpt-4o-mini', hint: '官方 API' },
}

const loading = ref(false)
const saving = ref(false)
const error = ref('')
const feedback = ref('')
const status = ref<ProviderStatus>({})

const provider = ref<ProviderKey>('xfyun_spark')
const openaiPreset = ref('deepseek')
const openaiBaseUrl = ref(openaiPresets.deepseek.baseUrl)
const openaiModel = ref(openaiPresets.deepseek.model)
const openaiApiKey = ref('')
const xfyunModel = ref('generalv3.5')
const xfyunApiPassword = ref('')

// 已配置的 Key 用掩码回显，避免明文泄露；留空表示不修改
const openaiKeyConfigured = ref(false)
const xfyunKeyConfigured = ref(false)

const activeProviderLabel = computed(() => {
  const active = String(status.value.activeProvider || status.value.configuredProvider || '')
  if (active === 'xfyun_spark') return '讯飞星火'
  if (active === 'openai_compatible') return 'OpenAI 兼容'
  if (active === 'offline') return '本地离线'
  return active || '未知'
})

const serviceOnline = computed(() => status.value.serviceOnline !== false)

function applyPreset(key: string) {
  const preset = openaiPresets[key]
  if (!preset) return
  openaiPreset.value = key
  openaiBaseUrl.value = preset.baseUrl
  openaiModel.value = preset.model
}

function hydrateFromStatus(next: ProviderStatus) {
  status.value = next
  const configured = String(next.configuredProvider || '')
  if (configured === 'openai_compatible' || configured === 'xfyun_spark') {
    provider.value = configured
  }
  if (next.openaiBaseUrl) openaiBaseUrl.value = String(next.openaiBaseUrl)
  if (next.openaiModel) openaiModel.value = String(next.openaiModel)
  if (next.xfyunModel) xfyunModel.value = String(next.xfyunModel)
  openaiKeyConfigured.value = Boolean(next.openaiConfigured)
  xfyunKeyConfigured.value = Boolean(next.xfyunConfigured)
}

async function loadStatus() {
  loading.value = true
  error.value = ''
  try {
    hydrateFromStatus(await settingsApi.providerStatus())
  } catch (err) {
    error.value = err instanceof Error ? err.message : '无法获取模型服务状态。'
  } finally {
    loading.value = false
  }
}

async function save() {
  saving.value = true
  error.value = ''
  feedback.value = ''
  try {
    const body: ProviderConfigRequest = { provider: provider.value }
    if (provider.value === 'openai_compatible') {
      body.openaiBaseUrl = openaiBaseUrl.value.trim()
      body.openaiModel = openaiModel.value.trim()
      if (openaiApiKey.value.trim()) body.openaiApiKey = openaiApiKey.value.trim()
    } else {
      body.xfyunModel = xfyunModel.value.trim()
      if (xfyunApiPassword.value.trim()) body.xfyunApiPassword = xfyunApiPassword.value.trim()
    }
    hydrateFromStatus(await settingsApi.updateProviderConfig(body))
    feedback.value = `已切换到「${activeProviderLabel.value}」，新会话立即生效。`
    openaiApiKey.value = ''
    xfyunApiPassword.value = ''
  } catch (err) {
    error.value = err instanceof Error ? err.message : '保存失败，请确认模型服务在线。'
  } finally {
    saving.value = false
  }
}

onMounted(loadStatus)
</script>

<template>
  <div class="settings-view">
    <header class="settings-head">
      <div>
        <h2>模型与 API 设置</h2>
      </div>
      <button class="ghost-button" type="button" :disabled="loading" @click="loadStatus">
        <RefreshCw :size="16" /> 刷新状态
      </button>
    </header>

    <div class="settings-status-bar" :class="{ offline: !serviceOnline }">
      <Server :size="16" />
      <span v-if="serviceOnline">模型服务在线 · 当前供应商：<strong>{{ activeProviderLabel }}</strong></span>
      <span v-else>模型服务不可达，请确认 resource-agent 服务已启动。</span>
      <small v-if="status.lastError" class="settings-last-error">最近错误：{{ status.lastError }}</small>
    </div>

    <ErrorNotice :message="error" />
    <p v-if="feedback" class="settings-feedback"><CheckCircle2 :size="16" /> {{ feedback }}</p>
    <LoadingBlock :show="loading" text="正在读取模型配置" />

    <div class="settings-provider-cards">
      <button
        type="button"
        class="settings-provider-card"
        :class="{ active: provider === 'xfyun_spark' }"
        @click="provider = 'xfyun_spark'"
      >
        <Bot :size="20" />
        <strong>讯飞星火</strong>
        <small>xfyun_spark · 默认</small>
        <em v-if="xfyunKeyConfigured" class="settings-badge">已配置</em>
      </button>
      <button
        type="button"
        class="settings-provider-card"
        :class="{ active: provider === 'openai_compatible' }"
        @click="provider = 'openai_compatible'"
      >
        <Bot :size="20" />
        <strong>OpenAI 兼容</strong>
        <small>DeepSeek / 通义 / 智谱 / Kimi</small>
        <em v-if="openaiKeyConfigured" class="settings-badge">已配置</em>
      </button>
    </div>

    <section v-if="provider === 'openai_compatible'" class="settings-form-card">
      <h3>OpenAI 兼容配置</h3>
      <div class="settings-preset-row">
        <button
          v-for="(preset, key) in openaiPresets"
          :key="key"
          type="button"
          class="settings-preset-chip"
          :class="{ active: openaiPreset === key }"
          @click="applyPreset(key)"
        >
          {{ preset.label }}
        </button>
      </div>
      <label class="settings-field">
        <span>API 端点 (Base URL)</span>
        <input v-model="openaiBaseUrl" type="text" placeholder="https://api.deepseek.com/v1" />
      </label>
      <label class="settings-field">
        <span>模型名称</span>
        <input v-model="openaiModel" type="text" placeholder="deepseek-chat" />
      </label>
      <label class="settings-field">
        <span>API Key {{ openaiKeyConfigured ? '（已配置，留空则不修改）' : '' }}</span>
        <input v-model="openaiApiKey" type="password" autocomplete="off" :placeholder="openaiKeyConfigured ? '••••••••（保持不变）' : 'sk-...'" />
      </label>
    </section>

    <section v-else class="settings-form-card">
      <h3>讯飞星火配置</h3>
      <label class="settings-field">
        <span>模型名称</span>
        <input v-model="xfyunModel" type="text" placeholder="generalv3.5" />
      </label>
      <label class="settings-field">
        <span>API Password {{ xfyunKeyConfigured ? '（已配置，留空则不修改）' : '' }}</span>
        <input v-model="xfyunApiPassword" type="password" autocomplete="off" :placeholder="xfyunKeyConfigured ? '••••••••（保持不变）' : 'APIPassword'" />
      </label>
    </section>

    <footer class="settings-actions">
      <button class="button" type="button" :disabled="saving || loading" @click="save">
        <Save :size="16" /> {{ saving ? '正在应用…' : '保存并切换' }}
      </button>
    </footer>
  </div>
</template>

<style scoped>
.settings-view {
  display: grid;
  gap: 18px;
  max-width: 760px;
  margin: 0 auto;
  padding: 8px 4px 40px;
}

.settings-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.settings-head h2 {
  margin: 0 0 4px;
  font-size: 22px;
  font-weight: 800;
  color: #102a43;
}

.settings-head p {
  margin: 0;
  color: #62788c;
  font-size: 14px;
}

.settings-status-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 12px;
  background: rgba(8, 127, 121, 0.08);
  color: #0a6b66;
  font-size: 14px;
}

.settings-status-bar.offline {
  background: rgba(220, 80, 60, 0.1);
  color: #b3402e;
}

.settings-last-error {
  width: 100%;
  color: #b3402e;
  font-size: 12px;
}

.settings-feedback {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  color: #0a6b66;
  font-size: 14px;
  font-weight: 600;
}

.settings-provider-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.settings-provider-card {
  position: relative;
  display: grid;
  gap: 4px;
  padding: 18px 16px;
  text-align: left;
  background: #ffffff;
  border: 1.5px solid #dbe8ef;
  border-radius: 14px;
  cursor: pointer;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.settings-provider-card:hover {
  border-color: #b6d8d4;
}

.settings-provider-card.active {
  border-color: #087f79;
  box-shadow: 0 0 0 3px rgba(8, 127, 121, 0.12);
}

.settings-provider-card strong {
  font-size: 15px;
  color: #102a43;
}

.settings-provider-card small {
  font-size: 12px;
  color: #7a90a4;
}

.settings-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(8, 127, 121, 0.12);
  color: #087f79;
  font-size: 11px;
  font-style: normal;
  font-weight: 700;
}

.settings-form-card {
  display: grid;
  gap: 14px;
  padding: 22px;
  background: #ffffff;
  border: 1px solid #dbe8ef;
  border-radius: 16px;
}

.settings-form-card h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: #102a43;
}

.settings-preset-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.settings-preset-chip {
  padding: 6px 14px;
  border: 1px solid #d4e2ea;
  border-radius: 999px;
  background: #f6fafb;
  color: #4a6072;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.settings-preset-chip.active {
  border-color: #087f79;
  background: rgba(8, 127, 121, 0.1);
  color: #087f79;
}

.settings-field {
  display: grid;
  gap: 6px;
}

.settings-field span {
  font-size: 13px;
  font-weight: 600;
  color: #43586a;
}

.settings-field input {
  height: 42px;
  padding: 0 14px;
  border: 1px solid #d4e2ea;
  border-radius: 10px;
  font-size: 14px;
  color: #102a43;
}

.settings-field input:focus {
  outline: none;
  border-color: #087f79;
  box-shadow: 0 0 0 3px rgba(8, 127, 121, 0.12);
}

.settings-hint {
  margin: 0;
  color: #8094a6;
  font-size: 12px;
}

.settings-actions {
  display: flex;
  justify-content: flex-end;
}
</style>
