<script setup>
/**
 * CustomForm — wrapper el-form.
 * Mặc định label nằm trên (label-position="top").
 * Mobile (≤767px): size="small" (cascade xuống control chưa set size).
 */
import { ref, useSlots } from 'vue'
import { useResponsiveComponentSize } from '@/composables/useResponsiveSize'

defineOptions({ name: 'CustomForm', inheritAttrs: false })

const props = defineProps({
  model: { type: Object, required: true },
  rules: { type: Object, default: undefined },
  labelPosition: { type: String, default: 'top' },
  labelWidth: { type: [String, Number], default: undefined },
})

const formRef = ref(null)
const slots = useSlots()
const { resolvedSize } = useResponsiveComponentSize()

defineExpose({
  validate: (...args) => formRef.value?.validate?.(...args),
  validateField: (...args) => formRef.value?.validateField?.(...args),
  resetFields: (...args) => formRef.value?.resetFields?.(...args),
  clearValidate: (...args) => formRef.value?.clearValidate?.(...args),
  scrollToField: (...args) => formRef.value?.scrollToField?.(...args),
})
</script>

<template>
  <el-form
    ref="formRef"
    :model="props.model"
    :rules="props.rules"
    :label-position="props.labelPosition"
    :label-width="props.labelWidth"
    v-bind="$attrs"
    :size="resolvedSize"
  >
    <template v-for="(_, name) in slots" #[name]="slotData">
      <slot :name="name" v-bind="slotData || {}" />
    </template>
  </el-form>
</template>
