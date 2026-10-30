<script setup>
import BangChiTiet from './BangChiTiet.vue'
import { col, cotChung } from './cot'

defineProps({
  rows: { type: Array, default: () => [] },
})

const { chuongTrinh, ghiChu, trinhDo, hinhThuc } = cotChung()

const columns = [
  chuongTrinh,
  trinhDo,
  hinhThuc,
  col('nam_thong_ke', 'Năm thống kê', { width: 130, align: 'center' }),
  col('so_luong_nguoi_hoc', 'Người học', { width: 120, align: 'right', type: 'number' }),
  ghiChu,
]
</script>

<template>
  <BangChiTiet :rows="rows" :columns="columns" />
</template>
