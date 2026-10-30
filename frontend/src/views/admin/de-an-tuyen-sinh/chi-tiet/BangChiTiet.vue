<script setup>
import { formatCell } from './format'

defineProps({
  rows: { type: Array, default: () => [] },
  columns: { type: Array, default: () => [] },
  emptyText: { type: String, default: 'Chưa có dữ liệu.' },
})
</script>

<template>
  <CustomTable :data="rows" row-key="row_key" stripe border max-height="480">
    <CustomTableColumn label="STT" width="72" align="center">
      <template #default="{ $index }">{{ $index + 1 }}</template>
    </CustomTableColumn>
    <CustomTableColumn
      v-for="column in columns"
      :key="column.prop"
      :prop="column.prop"
      :label="column.label"
      :width="column.width"
      :min-width="column.minWidth"
      :align="column.align"
      :show-overflow-tooltip="column.tooltip === true && column.type !== 'link'"
    >
      <template #default="{ row }">
        <a
          v-if="column.type === 'link' && row[column.prop]"
          class="cell-link"
          :href="row[column.prop]"
          target="_blank"
          rel="noopener noreferrer"
        >{{ row[column.prop] }}</a>
        <span v-else>{{ formatCell(row[column.prop], column) }}</span>
      </template>
    </CustomTableColumn>
    <template #empty>
      <CustomEmpty :description="emptyText" />
    </template>
  </CustomTable>
</template>

<style scoped>
.cell-link {
  color: var(--el-color-primary);
  overflow-wrap: anywhere;
}
</style>
