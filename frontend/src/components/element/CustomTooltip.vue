<script setup>
/**
 * CustomTooltip — wrapper el-tooltip.
 */
import { useSlots } from 'vue'

defineOptions({ name: 'CustomTooltip', inheritAttrs: false })

const slots = useSlots()
</script>

<template>
  <el-tooltip v-bind="$attrs">
    <template v-for="(_, name) in slots" #[name]="slotData">
      <slot :name="name" v-bind="slotData || {}" />
    </template>
  </el-tooltip>
</template>
