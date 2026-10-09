<script setup>
/**
 * CustomInput — wrapper el-input.
 * Chỉnh style / hành vi mặc định tại đây để áp dụng toàn app.
 * Mobile (≤767px): size="small" trừ khi truyền size tường minh.
 *
 * Với type="number": hiển thị định dạng 1.000.000, model vẫn là số nguyên.
 */
import { computed, ref, useAttrs, useSlots, watch } from 'vue'
import { useResponsiveComponentSize } from '@/composables/useResponsiveSize'
import { formatInteger, parseIntegerInput } from '@/utils/number'

defineOptions({ name: 'CustomInput', inheritAttrs: false })

const model = defineModel({ default: undefined })

const attrs = useAttrs()
const inputRef = ref(null)
const slots = useSlots()
const displayValue = ref('')
const { resolvedSize } = useResponsiveComponentSize()

const isNumberInput = computed(() => attrs.type === 'number')

const inputAttrs = computed(() => {
  if (!isNumberInput.value) return attrs

  const { type, onBlur, ...rest } = attrs

  return {
    placeholder: '0',
    ...rest,
    type: 'text',
    inputmode: rest.inputmode ?? 'numeric',
  }
})

watch(
  () => model.value,
  (val) => {
    if (!isNumberInput.value) return

    const formatted = formatInteger(val)
    if (formatted !== displayValue.value) {
      displayValue.value = formatted
    }
  },
  { immediate: true },
)

function onUpdate(val) {
  if (!isNumberInput.value) {
    model.value = val
    return
  }

  const parsed = parseIntegerInput(val)
  model.value = parsed
  displayValue.value = parsed == null ? '' : formatInteger(parsed)
}

function onBlur(event) {
  if (isNumberInput.value) {
    displayValue.value = formatInteger(model.value)
  }

  if (typeof attrs.onBlur === 'function') {
    attrs.onBlur(event)
  }
}

defineExpose({
  focus: (...args) => inputRef.value?.focus?.(...args),
  blur: (...args) => inputRef.value?.blur?.(...args),
  select: (...args) => inputRef.value?.select?.(...args),
  clear: (...args) => inputRef.value?.clear?.(...args),
})
</script>

<template>
  <el-input
    ref="inputRef"
    :model-value="isNumberInput ? displayValue : model"
    v-bind="inputAttrs"
    :size="resolvedSize"
    @update:model-value="onUpdate"
    @blur="onBlur"
  >
    <template v-for="(_, name) in slots" #[name]="slotData">
      <slot :name="name" v-bind="slotData || {}" />
    </template>
  </el-input>
</template>
