<script setup>
import BangChiTiet from './BangChiTiet.vue'
import { col, cotChung } from './cot'

defineProps({
  rows: { type: Array, default: () => [] },
})

const { ghiChu } = cotChung()

const columns = [
  col('ten_don_vi', 'Đơn vị', { minWidth: 220 }),
  col('ten_nguoi_lien_he', 'Người liên hệ', { minWidth: 180 }),
  col('chuc_vu', 'Chức vụ', { minWidth: 160 }),
  col('so_dien_thoai', 'Điện thoại', { width: 140, minWidth: 130 }),
  col('email', 'Email', { minWidth: 200 }),
  col('thoi_gian_lien_he', 'Thời gian liên hệ', { minWidth: 180 }),
  ghiChu,
]
</script>

<template>
  <BangChiTiet :rows="rows" :columns="columns" />
</template>
