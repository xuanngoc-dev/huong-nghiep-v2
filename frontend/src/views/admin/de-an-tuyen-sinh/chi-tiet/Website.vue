<script setup>
import BangChiTiet from './BangChiTiet.vue'
import { col, cotChung } from './cot'

defineProps({
  rows: { type: Array, default: () => [] },
})

const { ghiChu } = cotChung()

const columns = [
  col('loai_website', 'Loại', { width: 140, minWidth: 120 }),
  col('ten_trang', 'Tên trang', { minWidth: 220 }),
  col('url', 'Địa chỉ', { minWidth: 260, type: 'link' }),
  ghiChu,
]
</script>

<template>
  <BangChiTiet :rows="rows" :columns="columns" />
</template>
