<script setup>
import BangChiTiet from './BangChiTiet.vue'
import { col, cotChung } from './cot'

defineProps({
  rows: { type: Array, default: () => [] },
})

const { phuongThuc, ghiChu } = cotChung()

const columns = [
  phuongThuc,
  col('to_hop', 'Tổ hợp', { minWidth: 200 }),
  col('thu_tu_hien_thi', 'Thứ tự', { width: 90, align: 'center' }),
  ghiChu,
]
</script>

<template>
  <BangChiTiet :rows="rows" :columns="columns" />
</template>
