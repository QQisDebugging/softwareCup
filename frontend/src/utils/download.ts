import { hasMeaningfulValue, safeStringify } from '@/utils/format'

function notifyEmptyDownload() {
  window.alert('暂无可下载内容，请先完成一次查询或生成。')
}

export function downloadText(filename: string, text: string, type = 'text/plain;charset=utf-8') {
  if (!hasMeaningfulValue(text)) {
    notifyEmptyDownload()
    return false
  }
  const blob = new Blob([text], { type })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
  return true
}

export function downloadJson(filename: string, value: unknown) {
  if (!hasMeaningfulValue(value)) {
    notifyEmptyDownload()
    return false
  }
  return downloadText(filename, safeStringify(value), 'application/json;charset=utf-8')
}

export function safeFilePart(value: string) {
  return value.replace(/[\\/:*?"<>|\s]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 48) || 'softwarecup'
}

export function jsonToMarkdown(title: string, value: unknown) {
  return `# ${title}\n\n\`\`\`json\n${safeStringify(value)}\n\`\`\`\n`
}

export async function copyText(value: string) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(value)
    return
  }
  const textarea = document.createElement('textarea')
  textarea.value = value
  textarea.style.position = 'fixed'
  textarea.style.opacity = '0'
  document.body.appendChild(textarea)
  textarea.select()
  document.execCommand('copy')
  document.body.removeChild(textarea)
}
