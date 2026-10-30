<script setup>
import BangChiTiet from './BangChiTiet.vue'
import { col, cotChung } from './cot'

defineProps({
  rows: { type: Array, default: () => [] },
})

const { ghiChu } = cotChung()

const columns = [
  col('vai_tro', 'Vai trò', { width: 120, minWidth: 110 }),
  col('ten_co_so', 'Tên cơ sở', { minWidth: 220 }),
  col('loai_co_so', 'Loại cơ sở', { width: 140, minWidth: 130 }),
  col('dia_chi', 'Địa chỉ', { minWidth: 260 }),
  col('so_dien_thoai', 'Điện thoại', { width: 140, minWidth: 130 }),
  ghiChu,
]
</script>

<template>
  <BangChiTiet :rows="rows" :columns="columns" />
</template>
