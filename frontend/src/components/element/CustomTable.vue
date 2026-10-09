<script setup>
/**
 * CustomTable — wrapper el-table.
 * Default slot phải là con trực tiếp của el-table để cột được đăng ký đúng.
 * Mobile (≤767px): chữ/padding gọn hơn; cung cấp isMobile để cột thu width.
 */
import { nextTick, onBeforeUnmount, onMounted, provide, ref, toRef } from 'vue'
import { TABLE_COLUMN_SETTINGS_KEY, TABLE_IS_MOBILE_KEY } from '@/composables/useTableColumns'

defineOptions({ name: 'CustomTable', inheritAttrs: false })

const props = defineProps({
  /** Giá trị trả về từ useTableColumns(...) — dùng để ghim cột trái/phải. */
  columnSettings: {
    type: Object,
    default: null,
  },
  /** Hiện lớp loading trên bảng. inheritAttrs=false nên v-loading bên ngoài không xuyên vào. */
  loading: {
    type: Boolean,
    default: false,
  },
})

provide(TABLE_COLUMN_SETTINGS_KEY, toRef(props, 'columnSettings'))

const tableRef = ref(null)
const isMobile = ref(false)
provide(TABLE_IS_MOBILE_KEY, isMobile)

const MOBILE_MQ = '(max-width: 767px)'
let mediaQuery = null

function syncMobile() {
  const next = !!mediaQuery?.matches
  if (next === isMobile.value) return
  isMobile.value = next
  nextTick(() => tableRef.value?.doLayout?.())
}

onMounted(() => {
  mediaQuery = window.matchMedia(MOBILE_MQ)
  isMobile.value = mediaQuery.matches
  mediaQuery.addEventListener('change', syncMobile)
})

onBeforeUnmount(() => {
  mediaQuery?.removeEventListener('change', syncMobile)
  mediaQuery = null
})

defineExpose({
  clearSelection: (...args) => tableRef.value?.clearSelection?.(...args),
  getSelectionRows: (...args) => tableRef.value?.getSelectionRows?.(...args),
  toggleRowSelection: (...args) => tableRef.value?.toggleRowSelection?.(...args),
  setCurrentRow: (...args) => tableRef.value?.setCurrentRow?.(...args),
  clearSort: (...args) => tableRef.value?.clearSort?.(...args),
  clearFilter: (...args) => tableRef.value?.clearFilter?.(...args),
  doLayout: (...args) => tableRef.value?.doLayout?.(...args),
  sort: (...args) => tableRef.value?.sort?.(...args),
})
</script>

<template>
  <el-table
    ref="tableRef"
    v-loading="loading"
    class="custom-table"
    :class="{ 'is-mobile-compact': isMobile }"
    border
    :key="columnSettings?.fixedSignature || undefined"
    v-bind="$attrs"
  >
    <slot />
    <template v-if="$slots.append" #append>
      <slot name="append" />
    </template>
    <template v-if="$slots.empty" #empty>
      <slot name="empty" />
    </template>
  </el-table>
</template>

<style scoped>
.custom-table {
  --el-table-header-bg-color: var(--el-color-primary);
  --el-table-header-text-color: #fff;
}

.custom-table :deep(th.el-table__cell .el-checkbox__inner) {
  border-color: rgb(255 255 255 / 85%);
  background-color: transparent;
}

.custom-table :deep(th.el-table__cell .el-checkbox__input.is-checked .el-checkbox__inner),
.custom-table :deep(th.el-table__cell .el-checkbox__input.is-indeterminate .el-checkbox__inner) {
  background-color: #fff;
  border-color: #fff;
}

.custom-table :deep(th.el-table__cell .el-checkbox__input.is-checked .el-checkbox__inner::after) {
  border-color: var(--el-color-primary);
}

.custom-table :deep(th.el-table__cell .el-checkbox__input.is-indeterminate .el-checkbox__inner::before) {
  background-color: var(--el-color-primary);
}

/* Mobile: thu chữ, padding, margin, gap để nhìn được nhiều nội dung hơn */
.custom-table.is-mobile-compact {
  font-size: 11px;
}

.custom-table.is-mobile-compact :deep(th.el-table__cell),
.custom-table.is-mobile-compact :deep(td.el-table__cell) {
  padding: 2px 0;
}

.custom-table.is-mobile-compact :deep(th.el-table__cell > .cell),
.custom-table.is-mobile-compact :deep(td.el-table__cell > .cell) {
  font-size: 11px;
  line-height: 1.2;
  padding: 0 2px;
}

.custom-table.is-mobile-compact :deep(.el-table__header th.el-table__cell > .cell) {
  font-size: 10px;
  line-height: 1.15;
  padding: 0 2px;
}

.custom-table.is-mobile-compact :deep(.el-checkbox) {
  height: 12px;
  margin: 0;
}

.custom-table.is-mobile-compact :deep(.el-checkbox__inner) {
  width: 12px;
  height: 12px;
}

.custom-table.is-mobile-compact :deep(.el-checkbox__inner::after) {
  left: 3px;
  height: 6px;
  width: 2px;
}

.custom-table.is-mobile-compact :deep(.el-tag) {
  height: 18px;
  margin: 0;
  padding: 0 4px;
  font-size: 10px;
  line-height: 16px;
}

.custom-table.is-mobile-compact :deep(.el-button) {
  --el-button-size: 22px;
  margin: 0;
  font-size: 11px;
}

.custom-table.is-mobile-compact :deep(.el-button.is-link),
.custom-table.is-mobile-compact :deep(.el-button.is-text) {
  margin: 0;
  padding: 1px 2px;
  font-size: 11px;
}

.custom-table.is-mobile-compact :deep(.el-button + .el-button) {
  margin-left: 2px;
}

.custom-table.is-mobile-compact :deep(.el-button .el-icon),
.custom-table.is-mobile-compact :deep(.el-icon) {
  font-size: 13px;
  margin: 0;
}

.custom-table.is-mobile-compact :deep(.action-btns) {
  gap: 0;
  margin: 0;
}

.custom-table.is-mobile-compact :deep(.status-cell) {
  gap: 4px;
  margin: 0;
}

.custom-table.is-mobile-compact :deep(.status-label) {
  font-size: 11px;
  margin: 0;
}

.custom-table.is-mobile-compact :deep(.custom-table-col),
.custom-table.is-mobile-compact :deep(.custom-table-col-header) {
  font-size: 11px;
}

.custom-table.is-mobile-compact :deep(.el-table__empty-text) {
  font-size: 11px;
  line-height: 1.2;
}
</style>
