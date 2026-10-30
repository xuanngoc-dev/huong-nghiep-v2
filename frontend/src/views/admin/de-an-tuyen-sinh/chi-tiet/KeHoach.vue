<script setup>
import BangChiTiet from './BangChiTiet.vue'
import { col, cotChung } from './cot'

defineProps({
  rows: { type: Array, default: () => [] },
})

const { chuongTrinh, ghiChu } = cotChung()

const columns = [
  chuongTrinh,
  col('don_vi_chi_tieu', 'Đơn vị chỉ tiêu', { minWidth: 160 }),
  col('pham_vi_tuyen_sinh', 'Phạm vi', { minWidth: 180 }),
  col('dot_tuyen_sinh', 'Đợt', { width: 140, minWidth: 120 }),
  col('thoi_gian_nhan_ho_so', 'Thời gian nhận hồ sơ', { minWidth: 200 }),
  col('dieu_kien_chung', 'Điều kiện chung', { minWidth: 240 }),
  ghiChu,
]
</script>

<template>
  <BangChiTiet :rows="rows" :columns="columns" />
</template>
