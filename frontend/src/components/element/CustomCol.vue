<script setup>
/**
 * CustomCol — wrapper el-col.
 */
import { useSlots } from 'vue'

defineOptions({ name: 'CustomCol', inheritAttrs: false })

const slots = useSlots()
</script>

<template>
  <el-col v-bind="$attrs">
    <template v-for="(_, name) in slots" #[name]="slotData">
      <slot :name="name" v-bind="slotData || {}" />
    </template>
  </el-col>
</template>
