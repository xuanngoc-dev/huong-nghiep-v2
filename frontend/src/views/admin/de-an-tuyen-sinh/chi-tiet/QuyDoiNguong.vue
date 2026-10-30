<script setup>
import BangChiTiet from './BangChiTiet.vue'
import { col, cotChung } from './cot'

defineProps({
  rows: { type: Array, default: () => [] },
})

const { chuongTrinh, ghiChu, trangThai, nguon, nam } = cotChung()

const columns = [
  chuongTrinh,
  nam,
  col('phuong_thuc_nguon', 'Phương thức nguồn', { minWidth: 220 }),
  col('to_hop_nguon', 'Tổ hợp nguồn', { minWidth: 180 }),
  col('phuong_thuc_dich', 'Phương thức đích', { minWidth: 220 }),
  col('to_hop_dich', 'Tổ hợp đích', { minWidth: 180 }),
  col('diem_moc_nguon', 'Điểm mốc nguồn', { width: 150, align: 'right', type: 'number' }),
  col('diem_moc_dich', 'Điểm mốc đích', { width: 140, align: 'right', type: 'number' }),
  col('do_lech_diem', 'Độ lệch điểm', { width: 140, align: 'right', type: 'number' }),
  col('thang_diem_nguon', 'Thang điểm nguồn', { width: 160, align: 'right', type: 'number' }),
  col('thang_diem_dich', 'Thang điểm đích', { width: 150, align: 'right', type: 'number' }),
  col('cong_thuc_noi_suy', 'Công thức nội suy', { minWidth: 220 }),
  col('dieu_kien_ap_dung', 'Điều kiện áp dụng', { minWidth: 240 }),
  nguon,
  trangThai,
  ghiChu,
]
</script>

<template>
  <BangChiTiet :rows="rows" :columns="columns" />
</template>
