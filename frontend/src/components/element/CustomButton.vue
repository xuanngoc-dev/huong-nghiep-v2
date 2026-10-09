<script setup>
/**
 * CustomButton — wrapper el-button.
 * Mobile (≤767px): size="small" trừ khi truyền size tường minh.
 * Kế thừa size từ BulkActionBar nếu có (ưu tiên sau attrs.size).
 */
import { inject, useSlots } from 'vue'
import { BULK_ACTION_BTN_SIZE_KEY } from '@/components/element/buttonContext'
import { useResponsiveComponentSize } from '@/composables/useResponsiveSize'

defineOptions({ name: 'CustomButton', inheritAttrs: false })

const slots = useSlots()
const inheritedSize = inject(BULK_ACTION_BTN_SIZE_KEY, null)
const { resolvedSize } = useResponsiveComponentSize({ inherited: inheritedSize })
</script>

<template>
  <el-button v-bind="$attrs" :size="resolvedSize">
    <template v-for="(_, name) in slots" #[name]="slotData">
      <slot :name="name" v-bind="slotData || {}" />
    </template>
  </el-button>
</template>
