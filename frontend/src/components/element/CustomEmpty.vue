<script setup>
/**
 * CustomEmpty — wrapper el-empty.
 */
import { useSlots } from 'vue'

defineOptions({ name: 'CustomEmpty', inheritAttrs: false })

const slots = useSlots()
</script>

<template>
  <el-empty v-bind="$attrs">
    <template v-for="(_, name) in slots" #[name]="slotData">
      <slot :name="name" v-bind="slotData || {}" />
    </template>
  </el-empty>
</template>
