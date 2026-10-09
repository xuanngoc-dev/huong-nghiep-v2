<script setup>
/**
 * CustomCard — wrapper el-card.
 */
import { useSlots } from 'vue'

defineOptions({ name: 'CustomCard', inheritAttrs: false })

const slots = useSlots()
</script>

<template>
  <el-card v-bind="$attrs">
    <template v-for="(_, name) in slots" #[name]="slotData">
      <slot :name="name" v-bind="slotData || {}" />
    </template>
  </el-card>
</template>
