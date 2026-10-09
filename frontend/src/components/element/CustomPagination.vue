<script setup>
/**
 * CustomPagination — wrapper el-pagination.
 */
import { useSlots } from 'vue'

defineOptions({ name: 'CustomPagination', inheritAttrs: false })

const slots = useSlots()
</script>

<template>
  <el-pagination v-bind="$attrs">
    <template v-for="(_, name) in slots" #[name]="slotData">
      <slot :name="name" v-bind="slotData || {}" />
    </template>
  </el-pagination>
</template>
