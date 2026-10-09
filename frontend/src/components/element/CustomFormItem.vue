<script setup>
/**
 * CustomFormItem — wrapper el-form-item.
 */
import { useSlots } from 'vue'

defineOptions({ name: 'CustomFormItem', inheritAttrs: false })

const slots = useSlots()
</script>

<template>
  <el-form-item v-bind="$attrs">
    <template v-for="(_, name) in slots" #[name]="slotData">
      <slot :name="name" v-bind="slotData || {}" />
    </template>
  </el-form-item>
</template>
