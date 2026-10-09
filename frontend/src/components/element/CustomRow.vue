<script setup>
/**
 * CustomRow — wrapper el-row.
 */
import { useSlots } from 'vue'

defineOptions({ name: 'CustomRow', inheritAttrs: false })

const slots = useSlots()
</script>

<template>
  <el-row v-bind="$attrs">
    <template v-for="(_, name) in slots" #[name]="slotData">
      <slot :name="name" v-bind="slotData || {}" />
    </template>
  </el-row>
</template>
