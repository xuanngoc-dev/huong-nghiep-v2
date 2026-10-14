<script setup>
/**
 * CustomPagination — wrapper el-pagination.
 * Danh sách page size cố định trong component, không nhận từ prop.
 */
import { useSlots } from 'vue'

defineOptions({ name: 'CustomPagination', inheritAttrs: false })

const PAGE_SIZES = [10, 20, 50, 100, 200, 500, 1000]

const slots = useSlots()
</script>

<template>
  <el-pagination v-bind="$attrs" :page-sizes="PAGE_SIZES">
    <template v-for="(_, name) in slots" #[name]="slotData">
      <slot :name="name" v-bind="slotData || {}" />
    </template>
  </el-pagination>
</template>
