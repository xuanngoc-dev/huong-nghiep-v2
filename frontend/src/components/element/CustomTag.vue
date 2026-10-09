<script setup>
/**
 * CustomTag — wrapper el-tag.
 * Mobile (≤767px): size="small" trừ khi truyền size tường minh.
 */
import { useSlots } from 'vue'
import { useResponsiveComponentSize } from '@/composables/useResponsiveSize'

defineOptions({ name: 'CustomTag', inheritAttrs: false })

const slots = useSlots()
const { resolvedSize } = useResponsiveComponentSize()
</script>

<template>
  <el-tag v-bind="$attrs" :size="resolvedSize">
    <template v-for="(_, name) in slots" #[name]="slotData">
      <slot :name="name" v-bind="slotData || {}" />
    </template>
  </el-tag>
</template>
