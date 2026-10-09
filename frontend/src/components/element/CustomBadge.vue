<script setup>
/**
 * CustomBadge — wrapper el-badge.
 */
import { useSlots } from 'vue'

defineOptions({ name: 'CustomBadge', inheritAttrs: false })

const slots = useSlots()
</script>

<template>
  <el-badge v-bind="$attrs">
    <template v-for="(_, name) in slots" #[name]="slotData">
      <slot :name="name" v-bind="slotData || {}" />
    </template>
  </el-badge>
</template>
