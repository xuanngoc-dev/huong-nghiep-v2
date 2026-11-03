<script setup>
/**
 * CustomDialog — wrapper el-dialog.
 * Mặc định: rộng khoảng 90% viewport, cao 90vh, căn giữa, destroy-on-close.
 * Kéo mép trên/dưới/trái/phải để đổi kích thước.
 * Giữ header để kéo đổi vị trí.
 * Nút thu gọn (trước nút phóng/thu) ẩn body và footer, chỉ còn header.
 * Nút phóng/thu đổi kích thước khung; bấm lại để về width/height mặc định.
 * fullscreen: phủ toàn viewport, không kéo và không thu gọn.
 */
import { computed, nextTick, onBeforeUnmount, onMounted, ref, useAttrs, useSlots, watch } from 'vue'

defineOptions({ name: 'CustomDialog', inheritAttrs: false })

const EDGES = ['n', 'e', 's', 'w']
const VIEWPORT_GAP = 32
const MIN_WIDTH = 360
const MIN_HEIGHT = 240
const COMPACT_WIDTH_RATIO = 0.55
const COMPACT_HEIGHT_RATIO = 0.48

const visible = defineModel({ type: Boolean, default: false })

const props = defineProps({
  title: { type: String, default: '' },
  /** Chiều rộng mặc định. VD: 780 | '780px' | '90%' */
  width: { type: [String, Number], default: '90%' },
  /** Chiều cao mặc định. VD: '90vh' | 640 */
  height: { type: [String, Number], default: '90vh' },
  destroyOnClose: { type: Boolean, default: true },
  appendToBody: { type: Boolean, default: true },
  alignCenter: { type: Boolean, default: true },
  fullscreen: { type: Boolean, default: false },
})

const attrs = useAttrs()
const slots = useSlots()

const dialogComponent = ref(null)
const box = ref({ width: 0, height: 0 })
const placed = ref(null)
const collapsed = ref(false)
const minimized = ref(false)
const userSized = ref(false)
const resizing = ref(false)
const dragging = ref(false)

let resizeSession = null
let dragSession = null

const showClose = computed(() => {
  const value = attrs.showClose ?? attrs['show-close']
  return value !== false && value !== 'false'
})

const resolvedWidth = computed(() =>
  typeof props.width === 'number' ? `${props.width}px` : props.width
)

const fallthroughAttrs = computed(() => {
  const { class: _class, style: _style, onOpened: _onOpened, ...rest } = attrs
  return rest
})

const activeEdges = computed(() => (minimized.value ? ['e', 'w'] : EDGES))

const dialogClass = computed(() => {
  const fromAttrs = attrs.class
  const list = ['custom-dialog']
  if (resizing.value) list.push('is-resizing')
  if (dragging.value) list.push('is-dragging')
  if (minimized.value) list.push('is-minimized')
  if (!showClose.value) list.push('is-close-hidden')
  if (typeof fromAttrs === 'string' && fromAttrs) list.push(fromAttrs)
  else if (Array.isArray(fromAttrs)) list.push(...fromAttrs.filter(Boolean))
  return list
})

const dialogStyle = computed(() => {
  const extra = attrs.style
  const style = extra && typeof extra === 'object' && !Array.isArray(extra) ? { ...extra } : {}
  if (!props.fullscreen && box.value.width && box.value.height) {
    style['--custom-dialog-width'] = `${box.value.width}px`
    style['--custom-dialog-height'] = `${box.value.height}px`
  } else if (!props.fullscreen) {
    style['--custom-dialog-width'] = resolvedWidth.value
    style['--custom-dialog-height'] = typeof props.height === 'number' ? `${props.height}px` : props.height
  }
  if (!props.fullscreen && placed.value) {
    style.position = 'absolute'
    style.margin = '0'
    style.left = `${placed.value.left}px`
    style.top = `${placed.value.top}px`
  }
  return style
})

const dialogWidth = computed(() => {
  if (props.fullscreen) return '100%'
  if (box.value.width) return box.value.width
  return resolvedWidth.value
})

function viewport() {
  if (typeof window === 'undefined') return { width: 1280, height: 800 }
  return { width: window.innerWidth, height: window.innerHeight }
}

function parseLength(value, axis) {
  const view = viewport()
  const base = axis === 'x' ? view.width : view.height
  if (value == null || value === '') return base * 0.9
  if (typeof value === 'number') return value
  const raw = String(value).trim()
  if (raw.endsWith('%')) return (Number.parseFloat(raw) / 100) * base
  if (raw.endsWith('vw')) return (Number.parseFloat(raw) / 100) * view.width
  if (raw.endsWith('vh')) return (Number.parseFloat(raw) / 100) * view.height
  const pixels = Number.parseFloat(raw)
  return Number.isFinite(pixels) ? pixels : base * 0.9
}

function clampBox(width, height) {
  const view = viewport()
  const maxWidth = Math.max(160, view.width - VIEWPORT_GAP)
  const maxHeight = Math.max(160, view.height - VIEWPORT_GAP)
  const minWidth = Math.min(MIN_WIDTH, maxWidth)
  const minHeight = Math.min(MIN_HEIGHT, maxHeight)
  return {
    width: Math.round(Math.min(maxWidth, Math.max(minWidth, width))),
    height: Math.round(Math.min(maxHeight, Math.max(minHeight, height))),
  }
}

function defaultBox() {
  return clampBox(parseLength(props.width, 'x'), parseLength(props.height, 'y'))
}

function compactBox() {
  const base = defaultBox()
  return clampBox(base.width * COMPACT_WIDTH_RATIO, base.height * COMPACT_HEIGHT_RATIO)
}

function clampPosition(left, top, width, height) {
  const view = viewport()
  const visibleWidth = Math.min(width, view.width)
  const minLeft = Math.min(0, 48 - visibleWidth)
  const maxLeft = Math.max(minLeft, view.width - 48)
  const maxTop = Math.max(0, view.height - Math.min(height, 48) - 8)
  return {
    left: Math.round(Math.min(maxLeft, Math.max(minLeft, left))),
    top: Math.round(Math.min(maxTop, Math.max(0, top))),
  }
}

function keepPlacedInView() {
  if (!placed.value) return
  const el = dialogEl()
  const height = minimized.value ? el?.offsetHeight || 48 : box.value.height
  placed.value = clampPosition(placed.value.left, placed.value.top, box.value.width, height)
}

function resetOnOpen() {
  box.value = defaultBox()
  collapsed.value = false
  minimized.value = false
  userSized.value = false
  placed.value = null
}

function toggleCompact() {
  if (collapsed.value) {
    box.value = defaultBox()
    collapsed.value = false
    minimized.value = false
    userSized.value = false
    placed.value = null
    return
  }
  const compact = compactBox()
  box.value = {
    width: Math.min(box.value.width, compact.width),
    height: Math.min(box.value.height, compact.height),
  }
  collapsed.value = true
  keepPlacedInView()
}

function toggleMinimize() {
  minimized.value = !minimized.value
}

function resizeCursor(edge) {
  return edge === 'n' || edge === 's' ? 'ns-resize' : 'ew-resize'
}

function setResizeCursor(edge) {
  if (typeof document === 'undefined') return
  document.body.style.cursor = edge ? resizeCursor(edge) : ''
  document.body.style.userSelect = edge ? 'none' : ''
}

function clearResizeSession() {
  resizeSession = null
  resizing.value = false
  setResizeCursor('')
}

function onResizeStart(edge, event) {
  if (props.fullscreen || event.button !== 0) return
  if (minimized.value && (edge === 'n' || edge === 's')) return
  event.preventDefault()
  event.stopPropagation()
  resizeSession = {
    edge,
    pointerId: event.pointerId,
    startX: event.clientX,
    startY: event.clientY,
    width: box.value.width,
    height: box.value.height,
    left: placed.value?.left ?? null,
    top: placed.value?.top ?? null,
    anchored: Boolean(placed.value),
  }
  resizing.value = true
  setResizeCursor(edge)
  event.currentTarget.setPointerCapture(event.pointerId)
}

function onResizeMove(event) {
  if (!resizeSession || event.pointerId !== resizeSession.pointerId) return
  const dx = event.clientX - resizeSession.startX
  const dy = event.clientY - resizeSession.startY
  // Centered dialog: each edge moves half of the size change. A placed dialog moves 1:1.
  const horizontal = resizeSession.anchored ? 1 : 2
  const vertical = resizeSession.anchored ? 1 : props.alignCenter ? 2 : 1
  let { width, height } = resizeSession
  if (resizeSession.edge === 'e') width += dx * horizontal
  if (resizeSession.edge === 'w') width -= dx * horizontal
  if (resizeSession.edge === 's') height += dy * vertical
  if (resizeSession.edge === 'n') height -= dy * vertical
  const next = clampBox(width, height)
  if (minimized.value) next.height = resizeSession.height
  box.value = next
  if (resizeSession.anchored) {
    let left = resizeSession.left
    let top = resizeSession.top
    if (resizeSession.edge === 'w') left += resizeSession.width - next.width
    if (resizeSession.edge === 'n') top += resizeSession.height - next.height
    placed.value = clampPosition(left, top, next.width, minimized.value ? 48 : next.height)
  }
  collapsed.value = false
  userSized.value = true
}

function onResizeEnd(event) {
  if (!resizeSession || event.pointerId !== resizeSession.pointerId) return
  if (event.currentTarget?.hasPointerCapture?.(event.pointerId)) {
    event.currentTarget.releasePointerCapture(event.pointerId)
  }
  clearResizeSession()
}

function dialogEl() {
  const content = dialogComponent.value?.dialogContentRef
  if (content instanceof Element) return content
  const el = content?.$el
  return el instanceof Element ? el : null
}

function clearDragSession() {
  dragSession = null
  dragging.value = false
  if (typeof document !== 'undefined') {
    document.body.style.cursor = resizing.value ? document.body.style.cursor : ''
    if (!resizing.value) document.body.style.userSelect = ''
  }
}

function onDragStart(event) {
  if (props.fullscreen || event.button !== 0 || resizing.value) return
  const target = event.target
  if (!(target instanceof Element)) return
  if (target.closest('button, a, input, textarea, select, .custom-dialog__edge, [role="button"]')) return
  const el = dialogEl()
  if (!el) return
  const rect = el.getBoundingClientRect()
  dragSession = {
    pointerId: event.pointerId,
    startX: event.clientX,
    startY: event.clientY,
    left: rect.left,
    top: rect.top,
  }
  dragging.value = true
  placed.value = { left: Math.round(rect.left), top: Math.round(rect.top) }
  document.body.style.cursor = 'grabbing'
  document.body.style.userSelect = 'none'
  event.preventDefault()
  event.currentTarget.setPointerCapture(event.pointerId)
}

function onDragMove(event) {
  if (!dragSession || event.pointerId !== dragSession.pointerId) return
  const el = dialogEl()
  const height = minimized.value ? el?.offsetHeight || 48 : box.value.height
  placed.value = clampPosition(
    dragSession.left + event.clientX - dragSession.startX,
    dragSession.top + event.clientY - dragSession.startY,
    box.value.width,
    height,
  )
}

function onDragEnd(event) {
  if (!dragSession || event.pointerId !== dragSession.pointerId) return
  if (event.currentTarget?.hasPointerCapture?.(event.pointerId)) {
    event.currentTarget.releasePointerCapture(event.pointerId)
  }
  clearDragSession()
}

function bindHeaderDrag() {
  const header = dialogEl()?.querySelector('.el-dialog__header')
  if (!header || header.__customDialogDrag) return
  header.__customDialogDrag = true
  header.addEventListener('pointerdown', onDragStart)
  header.addEventListener('pointermove', onDragMove)
  header.addEventListener('pointerup', onDragEnd)
  header.addEventListener('pointercancel', onDragEnd)
}

function handleOpened(...args) {
  bindHeaderDrag()
  const hook = attrs.onOpened
  if (typeof hook === 'function') hook(...args)
  else if (Array.isArray(hook)) hook.forEach((fn) => fn?.(...args))
}

function onViewportResize() {
  if (!visible.value || props.fullscreen || resizing.value || dragging.value) return
  if (!minimized.value && !collapsed.value && !userSized.value && !placed.value) {
    box.value = defaultBox()
    return
  }
  if (!minimized.value) box.value = clampBox(box.value.width, box.value.height)
  keepPlacedInView()
}

watch(visible, (open) => {
  if (open) {
    resetOnOpen()
    nextTick(() => bindHeaderDrag())
    return
  }
  clearResizeSession()
  clearDragSession()
})

watch(
  () => [props.width, props.height, props.fullscreen],
  () => {
    if (!visible.value || collapsed.value || userSized.value || resizing.value) return
    box.value = defaultBox()
  },
)

onMounted(() => {
  box.value = box.value.width ? box.value : defaultBox()
  window.addEventListener('resize', onViewportResize)
})

onBeforeUnmount(() => {
  clearResizeSession()
  clearDragSession()
  window.removeEventListener('resize', onViewportResize)
})

resetOnOpen()
</script>

<template>
  <el-dialog
    ref="dialogComponent"
    v-model="visible"
    :title="title"
    :width="dialogWidth"
    :fullscreen="fullscreen"
    :align-center="alignCenter"
    :destroy-on-close="destroyOnClose"
    :append-to-body="appendToBody"
    :class="dialogClass"
    :style="dialogStyle"
    v-bind="fallthroughAttrs"
    @opened="handleOpened"
  >
    <template #header="headerSlot">
      <slot v-if="slots.header" name="header" v-bind="headerSlot || {}" />
      <span v-else class="el-dialog__title" role="heading" aria-level="2">{{ title }}</span>
      <button
        v-if="!fullscreen"
        type="button"
        class="custom-dialog__icon-btn custom-dialog__minimize-btn"
        :aria-label="minimized ? 'Hiện nội dung' : 'Thu gọn'"
        :title="minimized ? 'Hiện nội dung' : 'Thu gọn'"
        @pointerdown.stop
        @click="toggleMinimize"
      >
        <svg viewBox="0 0 16 16" aria-hidden="true">
          <path
            v-if="minimized"
            d="M2.5 3.5h11v9h-11z"
            fill="none"
            stroke="currentColor"
            stroke-width="1.4"
            stroke-linejoin="round"
          />
          <path
            v-else
            d="M2.5 8h11"
            fill="none"
            stroke="currentColor"
            stroke-width="1.4"
            stroke-linecap="round"
          />
        </svg>
      </button>
      <button
        v-if="!fullscreen"
        type="button"
        class="custom-dialog__icon-btn custom-dialog__size-btn"
        :aria-label="collapsed ? 'Phóng to' : 'Thu nhỏ'"
        :title="collapsed ? 'Phóng to' : 'Thu nhỏ'"
        @pointerdown.stop
        @click="toggleCompact"
      >
        <svg viewBox="0 0 16 16" aria-hidden="true">
          <path
            v-if="collapsed"
            d="M2 6V2h4M10 2h4v4M14 10v4h-4M6 14H2v-4"
            fill="none"
            stroke="currentColor"
            stroke-width="1.4"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
          <path
            v-else
            d="M6 2v4H2M10 2v4h4M14 10h-4v4M2 10h4v4"
            fill="none"
            stroke="currentColor"
            stroke-width="1.4"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </button>
      <template v-if="!fullscreen">
        <div
          v-for="edge in activeEdges"
          :key="edge"
          :class="['custom-dialog__edge', `custom-dialog__edge--${edge}`]"
          aria-hidden="true"
          @pointerdown="onResizeStart(edge, $event)"
          @pointermove="onResizeMove"
          @pointerup="onResizeEnd"
          @pointercancel="onResizeEnd"
        />
      </template>
    </template>

    <template v-for="name in Object.keys(slots).filter((slotName) => slotName !== 'header')" :key="name" #[name]="slotData">
      <slot :name="name" v-bind="slotData || {}" />
    </template>
  </el-dialog>
</template>

<style>
.custom-dialog.el-dialog {
  width: min(var(--custom-dialog-width, 90%), calc(100vw - 32px)) !important;
  max-width: calc(100vw - 32px);
  height: var(--custom-dialog-height, 90vh);
  max-height: calc(100vh - 32px);
  max-height: calc(100dvh - 32px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: width 0.18s ease, height 0.18s ease;
}

.custom-dialog.el-dialog.is-resizing,
.custom-dialog.el-dialog.is-dragging {
  transition: none;
}

.custom-dialog.el-dialog:not(.is-fullscreen) .el-dialog__header {
  cursor: grab;
  user-select: none;
}

.custom-dialog.el-dialog.is-dragging .el-dialog__header {
  cursor: grabbing;
}

.custom-dialog.el-dialog .el-dialog__header {
  flex-shrink: 0;
  margin-right: 0;
}

.custom-dialog.el-dialog .el-dialog__header.show-close {
  padding-right: 136px;
}

.custom-dialog.el-dialog.is-close-hidden .el-dialog__header {
  padding-right: 88px;
}

.custom-dialog.el-dialog.is-minimized {
  height: auto !important;
  min-height: 0;
  padding-bottom: 12px;
}

.custom-dialog.el-dialog.is-minimized .el-dialog__header {
  padding-bottom: 0;
}

.custom-dialog.el-dialog.is-minimized .el-dialog__body,
.custom-dialog.el-dialog.is-minimized .el-dialog__footer {
  display: none !important;
}

.custom-dialog.el-dialog .el-dialog__body {
  flex: 1 1 auto;
  min-height: 0;
  overflow-x: hidden;
  overflow-y: auto;
}

.custom-dialog.el-dialog .el-dialog__footer {
  flex-shrink: 0;
}

.custom-dialog__icon-btn {
  position: absolute;
  top: 0;
  z-index: 4;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  padding: 0;
  border: none;
  background: transparent;
  color: var(--el-color-info);
  cursor: pointer;
}

.custom-dialog__size-btn {
  right: 48px;
}

.custom-dialog__minimize-btn {
  right: 96px;
}

.custom-dialog.is-close-hidden .custom-dialog__size-btn {
  right: 0;
}

.custom-dialog.is-close-hidden .custom-dialog__minimize-btn {
  right: 48px;
}

.custom-dialog__icon-btn:hover,
.custom-dialog__icon-btn:focus-visible {
  color: var(--el-color-primary);
}

.custom-dialog__icon-btn svg {
  display: block;
  width: 16px;
  height: 16px;
}

.custom-dialog__edge {
  position: absolute;
  z-index: 3;
  touch-action: none;
}

.custom-dialog__edge::after {
  content: '';
  position: absolute;
  background: var(--el-color-primary);
  opacity: 0;
  transition: opacity 0.15s ease;
}

.custom-dialog__edge:hover::after {
  opacity: 0.9;
}

.custom-dialog__edge--n,
.custom-dialog__edge--s {
  left: 12px;
  right: 12px;
  height: 8px;
  cursor: ns-resize;
}

.custom-dialog__edge--n {
  top: 0;
  right: 152px;
}

.custom-dialog.is-close-hidden .custom-dialog__edge--n {
  right: 104px;
}

.custom-dialog.is-minimized .custom-dialog__edge--e,
.custom-dialog.is-minimized .custom-dialog__edge--w {
  top: 8px;
  bottom: 8px;
}

.custom-dialog__edge--s {
  bottom: 0;
}

.custom-dialog__edge--n::after,
.custom-dialog__edge--s::after {
  left: 0;
  right: 0;
  top: 50%;
  height: 2px;
  transform: translateY(-50%);
}

.custom-dialog__edge--e,
.custom-dialog__edge--w {
  top: 48px;
  bottom: 12px;
  width: 8px;
  cursor: ew-resize;
}

.custom-dialog__edge--e {
  right: 0;
}

.custom-dialog__edge--w {
  left: 0;
}

.custom-dialog__edge--e::after,
.custom-dialog__edge--w::after {
  top: 0;
  bottom: 0;
  left: 50%;
  width: 2px;
  transform: translateX(-50%);
}

.custom-dialog.el-dialog.is-fullscreen {
  width: 100% !important;
  max-width: 100% !important;
  height: 100% !important;
  max-height: 100% !important;
  margin: 0 !important;
  border-radius: 0;
  overflow: hidden;
  transition: none;
}

.custom-dialog.el-dialog.is-fullscreen .el-dialog__body {
  display: flex;
  flex-direction: column;
}
</style>
