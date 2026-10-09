<script setup>
/**
 * CustomTableColumn — wrapper el-table-column.
 * Tự gán `fixed` theo cấu hình cột (nếu bảng truyền `column-settings`).
 * Class `custom-table-col` gắn vào ô; trên mobile thu width/min-width.
 */
import { computed, inject, unref, useAttrs, useSlots } from 'vue'
import {
  FIXED_COL,
  TABLE_COLUMN_SETTINGS_KEY,
  TABLE_IS_MOBILE_KEY,
  TABLE_MOBILE_WIDTH_SCALE,
} from '@/composables/useTableColumns'

defineOptions({ name: 'CustomTableColumn', inheritAttrs: false })

const props = defineProps({
  /** Khóa cột trong useTableColumns, khi không suy ra được từ type/prop/label. */
  configKey: {
    type: String,
    default: '',
  },
})

const slots = useSlots()
const attrs = useAttrs()
const settingsRef = inject(TABLE_COLUMN_SETTINGS_KEY, null)
const isMobileRef = inject(TABLE_IS_MOBILE_KEY, null)

function resolveConfigKey() {
  if (props.configKey) return props.configKey
  if (attrs.type === 'selection') return FIXED_COL.selection
  if (attrs.label === 'STT' || attrs.label === 'Số thứ tự') return FIXED_COL.stt
  if (attrs.label === 'Thao tác') return FIXED_COL.actions
  return attrs.prop || attrs.label || null
}

const resolvedFixed = computed(() => {
  const settings = unref(settingsRef)
  const key = resolveConfigKey()
  if (settings?.columnFixed && key && settings.isPinColumn?.(key)) {
    return settings.columnFixed(key) || false
  }
  return attrs.fixed
})

/** Gộp class ô body — giữ class-name từ attrs nếu có. */
const mergedClassName = computed(() => {
  const existing = attrs['class-name'] ?? attrs.className ?? ''
  return [existing, 'custom-table-col'].filter(Boolean).join(' ')
})

/** Gộp class ô header. */
const mergedLabelClassName = computed(() => {
  const existing = attrs['label-class-name'] ?? attrs.labelClassName ?? ''
  return [existing, 'custom-table-col-header'].filter(Boolean).join(' ')
})

function scaleColumnSize(value) {
  if (value == null || value === '') return undefined
  const raw = String(value).trim()
  const num = Number(raw.replace(/px$/i, ''))
  if (!Number.isFinite(num)) return value
  const scaled = Math.round(num * TABLE_MOBILE_WIDTH_SCALE)
  // selection/STT vẫn đủ chỗ; cột khác tối thiểu 40px
  const floor = attrs.type === 'selection' ? 32 : 40
  return Math.max(scaled, floor)
}

const resolvedWidth = computed(() => {
  const raw = attrs.width
  if (raw == null || raw === '') return undefined
  return unref(isMobileRef) ? scaleColumnSize(raw) : raw
})

const resolvedMinWidth = computed(() => {
  const raw = attrs['min-width'] ?? attrs.minWidth
  if (raw == null || raw === '') return undefined
  return unref(isMobileRef) ? scaleColumnSize(raw) : raw
})

/** Bỏ width/min-width/class khỏi attrs — bind riêng bên dưới. */
const restAttrs = computed(() => {
  const {
    width: _w,
    minWidth: _mw,
    'min-width': _mwKebab,
    className: _cn,
    'class-name': _cnKebab,
    labelClassName: _lcn,
    'label-class-name': _lcnKebab,
    fixed: _fixed,
    ...rest
  } = attrs
  return rest
})
</script>

<template>
  <el-table-column
    v-bind="restAttrs"
    :fixed="resolvedFixed"
    :width="resolvedWidth"
    :min-width="resolvedMinWidth"
    :class-name="mergedClassName"
    :label-class-name="mergedLabelClassName"
  >
    <template v-for="(_, name) in slots" #[name]="scope">
      <slot :name="name" v-bind="scope || {}" />
    </template>
  </el-table-column>
</template>
