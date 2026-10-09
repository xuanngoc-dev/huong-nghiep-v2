<script setup>
/**
 * CustomSelect — wrapper el-select.
 * Khi `multiple`: hiện checkbox "Chọn tất cả" ở đầu dropdown.
 * Mobile (≤767px): size="small" trừ khi truyền size tường minh.
 */
import { computed, provide, reactive, ref, useAttrs, useSlots } from 'vue'
import { useResponsiveComponentSize } from '@/composables/useResponsiveSize'

defineOptions({ name: 'CustomSelect', inheritAttrs: false })

const props = defineProps({
  /** Hiện checkbox chọn tất cả (chỉ khi multiple). */
  showSelectAll: { type: Boolean, default: true },
  selectAllLabel: { type: String, default: 'Chọn tất cả' },
})

const model = defineModel({ default: undefined })
const selectRef = ref(null)
const slots = useSlots()
const attrs = useAttrs()
const { resolvedSize } = useResponsiveComponentSize()

const registeredOptions = reactive(new Map())

provide('customSelectOptions', {
  register(key, value) {
    registeredOptions.set(key, value)
  },
  unregister(key) {
    registeredOptions.delete(key)
  },
})

const isMultiple = computed(() => {
  const value = attrs.multiple
  return value === true || value === '' || value === 'true' || value === 1 || value === '1'
})

const showSelectAllCheckbox = computed(() => isMultiple.value && props.showSelectAll)

const forwardedSlotNames = computed(() =>
  Object.keys(slots).filter((name) => !(showSelectAllCheckbox.value && name === 'header')),
)

const allValues = computed(() => [...registeredOptions.values()])

const selectableValues = computed(() => {
  const optionsMap = selectRef.value?.states?.options
  if (optionsMap && typeof optionsMap.values === 'function') {
    const filtered = [...optionsMap.values()]
      .filter((option) => option && option.visible !== false)
      .map((option) => option.value)
    if (filtered.length) return filtered
  }
  return allValues.value
})

const selectedArray = computed(() => (Array.isArray(model.value) ? model.value : []))

const isAllSelected = computed(() => {
  const values = selectableValues.value
  if (!values.length) return false
  return values.every((value) => selectedArray.value.includes(value))
})

const isIndeterminate = computed(() => {
  if (isAllSelected.value) return false
  const values = selectableValues.value
  return values.some((value) => selectedArray.value.includes(value))
})

function toggleSelectAll(checked) {
  const values = selectableValues.value
  const current = Array.isArray(model.value) ? [...model.value] : []

  if (checked) {
    const merged = new Set([...current, ...values])
    model.value = [...merged]
    return
  }

  const removeSet = new Set(values)
  model.value = current.filter((value) => !removeSet.has(value))
}

defineExpose({
  focus: (...args) => selectRef.value?.focus?.(...args),
  blur: (...args) => selectRef.value?.blur?.(...args),
})
</script>

<template>
  <el-select ref="selectRef" v-model="model" clearable v-bind="$attrs" :size="resolvedSize">
    <template v-if="showSelectAllCheckbox" #header>
      <div class="custom-select__select-all" @click.stop @mousedown.stop>
        <el-checkbox
          :model-value="isAllSelected"
          :indeterminate="isIndeterminate"
          :disabled="!selectableValues.length"
          :size="resolvedSize"
          @change="toggleSelectAll"
        >
          {{ selectAllLabel }}
        </el-checkbox>
      </div>
      <slot name="header" />
    </template>

    <template v-for="name in forwardedSlotNames" :key="name" #[name]="slotData">
      <slot :name="name" v-bind="slotData || {}" />
    </template>
  </el-select>
</template>

<style scoped lang="scss">
.custom-select__select-all {
  padding: 0px 8px;

  :deep(.el-checkbox) {
    width: 100%;
    height: auto;
    white-space: normal;
  }

  :deep(.el-checkbox__label) {
    font-weight: 500;
    color: var(--el-text-color-primary);
  }
}
</style>
