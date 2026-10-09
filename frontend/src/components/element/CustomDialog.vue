<script setup>
/**
 * CustomDialog — wrapper el-dialog.
 * Mặc định: destroy-on-close, append-to-body, width responsive.
 * fullscreen: phủ toàn viewport, body giãn để nội dung chiếm phần còn lại.
 * Nội dung dài: body cuộn dọc, header/footer luôn hiển thị (max-height theo viewport).
 */
import { computed, useAttrs, useSlots } from 'vue'

defineOptions({ name: 'CustomDialog', inheritAttrs: false })

const visible = defineModel({ type: Boolean, default: false })

const props = defineProps({
  title: { type: String, default: '' },
  /** Chiều rộng dialog. VD: 780 | '780px' | '70%' */
  width: { type: [String, Number], default: 520 },
  /** Căn giữa title. */
  destroyOnClose: { type: Boolean, default: true },
  appendToBody: { type: Boolean, default: true },
  alignCenter: { type: Boolean, default: true },
  fullscreen: { type: Boolean, default: false },
})

const attrs = useAttrs()
const slots = useSlots()

const resolvedWidth = computed(() =>
  typeof props.width === 'number' ? `${props.width}px` : props.width
)

const fallthroughAttrs = computed(() => {
  const { class: _class, style: _style, ...rest } = attrs
  return rest
})

const dialogClass = computed(() => {
  const fromAttrs = attrs.class
  const list = ['custom-dialog']
  if (typeof fromAttrs === 'string' && fromAttrs) list.push(fromAttrs)
  else if (Array.isArray(fromAttrs)) list.push(...fromAttrs.filter(Boolean))
  return list
})
</script>

<template>
  <el-dialog
    v-model="visible"
    :title="title"
    :width="resolvedWidth"
    :fullscreen="fullscreen"
    :align-center="alignCenter"
    :destroy-on-close="destroyOnClose"
    :append-to-body="appendToBody"
    :class="dialogClass"
    :style="{ '--custom-dialog-width': resolvedWidth }"
    v-bind="fallthroughAttrs"
  >
    <template v-for="(_, name) in slots" #[name]="slotData">
      <slot :name="name" v-bind="slotData || {}" />
    </template>
  </el-dialog>
</template>

<style>
.custom-dialog.el-dialog {
  width: min(var(--custom-dialog-width, 520px), calc(100vw - 32px)) !important;
  max-width: var(--custom-dialog-width, 520px);
  max-height: calc(100vh - 32px);
  max-height: calc(100dvh - 32px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.custom-dialog.el-dialog .el-dialog__header {
  flex-shrink: 0;
  margin-right: 0;
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

.custom-dialog.el-dialog.is-fullscreen {
  width: 100% !important;
  max-width: 100% !important;
  height: 100% !important;
  max-height: 100% !important;
  margin: 0 !important;
  border-radius: 0;
  overflow: hidden;
}

.custom-dialog.el-dialog.is-fullscreen .el-dialog__body {
  display: flex;
  flex-direction: column;
}
</style>
