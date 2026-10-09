<script setup>
/**
 * CustomRadioButton — wrapper el-radio-button.
 */
import { useSlots } from 'vue'

defineOptions({ name: 'CustomRadioButton', inheritAttrs: false })

const slots = useSlots()
</script>

<template>
  <el-radio-button v-bind="$attrs">
    <template v-for="(_, name) in slots" #[name]="slotData">
      <slot :name="name" v-bind="slotData || {}" />
    </template>
  </el-radio-button>
</template>
