<script setup>
import BangChiTiet from './BangChiTiet.vue'
import { col, cotChung } from './cot'

defineProps({
  rows: { type: Array, default: () => [] },
})

const { chuongTrinh, phuongThuc, ghiChu } = cotChung()

const columns = [
  col('ten_giay_to', 'Giấy tờ', { minWidth: 220 }),
  col('doi_tuong_phai_nop', 'Đối tượng phải nộp', { minWidth: 220 }),
  col('bat_buoc', 'Bắt buộc', { width: 110, align: 'center', type: 'bool' }),
  col('hinh_thuc_nop', 'Hình thức nộp', { minWidth: 150 }),
  col('thoi_han_nop', 'Thời hạn', { minWidth: 180 }),
  chuongTrinh,
  phuongThuc,
  ghiChu,
]
</script>

<template>
  <BangChiTiet :rows="rows" :columns="columns" />
</template>
