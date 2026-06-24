import { computed, onBeforeUnmount, ref, type CSSProperties } from 'vue'
import { useAppStore } from '@/stores/app'

/**
 * 可拖拽多列分栏。列宽以 fr 权重保存到 localStorage（按角色隔离），
 * 刷新后自动恢复用户调整过的比例。复用 AppShell 侧边栏拖拽的 pointer 事件模式。
 */
export interface ResizablePanelsOptions {
  /** 持久化键名前缀，每个页面/网格用独立的 key */
  storageKey: string
  /** 各列默认 fr 权重，长度即列数 */
  defaultWeights: number[]
  /** 每列最小像素宽度，防止拖到挤没 */
  minWidths?: number[]
  /** 低于该视口宽度时禁用拖拽（移动端回退为自适应） */
  disableBelow?: number
  /** 分隔条轨道宽度（同时承担列间距），默认 24px，使用时需把网格 gap 设为 0 */
  spacing?: number
}

const STORAGE_PREFIX = 'resizable-panels'

export function useResizablePanels(options: ResizablePanelsOptions) {
  const app = useAppStore()
  const columns = options.defaultWeights.length
  const minWidths = options.minWidths ?? new Array(columns).fill(220)
  const disableBelow = options.disableBelow ?? 1120
  const spacing = options.spacing ?? 24

  const weights = ref<number[]>([...options.defaultWeights])
  const resizingIndex = ref<number | null>(null)

  function storageName() {
    return `${STORAGE_PREFIX}-${options.storageKey}-${app.role}`
  }

  function readStored(): number[] | null {
    if (typeof window === 'undefined') return null
    try {
      const raw = window.localStorage.getItem(storageName())
      if (!raw) return null
      const parsed = JSON.parse(raw)
      if (Array.isArray(parsed) && parsed.length === columns && parsed.every((n) => Number.isFinite(n) && n > 0)) {
        return parsed.map(Number)
      }
    } catch {
      return null
    }
    return null
  }

  function persist() {
    if (typeof window === 'undefined') return
    window.localStorage.setItem(storageName(), JSON.stringify(weights.value))
  }

  const stored = readStored()
  if (stored) weights.value = stored

  const gridStyle = computed<CSSProperties>(() => {
    const cols = weights.value
      .map((weight, index) => `minmax(${minWidths[index]}px, ${weight}fr)`)
      .join(` ${spacing}px `)
    return { '--panel-cols': cols, '--panel-gap': '0px' } as CSSProperties
  })

  let startX = 0
  let startLeft = 0
  let startRight = 0
  let containerWidth = 0

  function handlePointerMove(event: PointerEvent) {
    const index = resizingIndex.value
    if (index === null) return
    event.preventDefault()
    const deltaPx = event.clientX - startX
    // 把像素增量换算成 fr：以拖拽前两列的 fr 之和按容器宽度比例分配
    const pairFr = startLeft + startRight
    const pairPx = containerWidth > 0 ? (pairFr / totalWeight()) * containerWidth : 1
    const deltaFr = pairPx > 0 ? (deltaPx / pairPx) * pairFr : 0

    let nextLeft = startLeft + deltaFr
    let nextRight = startRight - deltaFr

    // 用最小宽度换算成最小 fr 做钳制
    const minLeftFr = minFrFor(index)
    const minRightFr = minFrFor(index + 1)
    if (nextLeft < minLeftFr) {
      nextRight -= minLeftFr - nextLeft
      nextLeft = minLeftFr
    }
    if (nextRight < minRightFr) {
      nextLeft -= minRightFr - nextRight
      nextRight = minRightFr
    }
    if (nextLeft < minLeftFr) return

    const next = [...weights.value]
    next[index] = Number(nextLeft.toFixed(4))
    next[index + 1] = Number(nextRight.toFixed(4))
    weights.value = next
  }

  function totalWeight() {
    return weights.value.reduce((sum, n) => sum + n, 0)
  }

  function minFrFor(index: number) {
    if (containerWidth <= 0) return 0.1
    return (minWidths[index] / containerWidth) * totalWeight()
  }

  function stopResize() {
    if (resizingIndex.value === null) return
    resizingIndex.value = null
    persist()
    document.body.classList.remove('is-panels-resizing')
    document.removeEventListener('pointermove', handlePointerMove)
    document.removeEventListener('pointerup', stopResize)
  }

  /** 在第 index 与 index+1 列之间开始拖拽。event.currentTarget 应为分隔条元素。 */
  function startResize(index: number, event: PointerEvent) {
    if (typeof window !== 'undefined' && window.innerWidth <= disableBelow) return
    if (index < 0 || index >= columns - 1) return
    event.preventDefault()
    const resizer = event.currentTarget as HTMLElement | null
    const grid = resizer?.parentElement
    containerWidth = grid?.clientWidth ?? 0
    startX = event.clientX
    startLeft = weights.value[index]
    startRight = weights.value[index + 1]
    resizingIndex.value = index
    document.body.classList.add('is-panels-resizing')
    document.addEventListener('pointermove', handlePointerMove)
    document.addEventListener('pointerup', stopResize)
  }

  /** 双击分隔条恢复默认比例 */
  function resetLayout() {
    weights.value = [...options.defaultWeights]
    persist()
  }

  onBeforeUnmount(() => {
    document.body.classList.remove('is-panels-resizing')
    document.removeEventListener('pointermove', handlePointerMove)
    document.removeEventListener('pointerup', stopResize)
  })

  return { gridStyle, startResize, resetLayout, weights, resizingIndex }
}
