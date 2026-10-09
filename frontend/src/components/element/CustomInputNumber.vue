<script setup>
/**
 * CustomInputNumber — wrapper el-input-number.
 * Mobile (≤767px): size="small" trừ khi truyền size tường minh.
 */
import { useSlots } from 'vue'
import { useResponsiveComponentSize } from '@/composables/useResponsiveSize'

defineOptions({ name: 'CustomInputNumber', inheritAttrs: false })

const model = defineModel({ default: undefined })
const slots = useSlots()
const { resolvedSize } = useResponsiveComponentSize()
</script>

<template>
  <el-input-number v-model="model" v-bind="$attrs" :size="resolvedSize">
    <template v-for="(_, name) in slots" #[name]="slotData">
      <slot :name="name" v-bind="slotData || {}" />
    </template>
  </el-input-number>
</template>
