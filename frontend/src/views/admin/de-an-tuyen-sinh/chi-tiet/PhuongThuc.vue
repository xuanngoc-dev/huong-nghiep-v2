<script setup>
import BangChiTiet from './BangChiTiet.vue'
import { col, cotChung } from './cot'

defineProps({
  rows: { type: Array, default: () => [] },
})

const { chuongTrinh, ghiChu } = cotChung()

const columns = [
  chuongTrinh,
  col('ma_phuong_thuc_cua_bo', 'Mã của Bộ', { width: 120, minWidth: 110, align: 'center' }),
  col('ma_phuong_thuc_cua_truong', 'Mã của trường', { width: 140, minWidth: 130, align: 'center' }),
  col('ten_phuong_thuc_cua_truong', 'Tên phương thức', { minWidth: 220 }),
  col('chi_tieu_phuong_thuc', 'Chỉ tiêu', { width: 110, align: 'right', type: 'number' }),
  col('diem_san', 'Điểm sàn', { width: 110, align: 'right', type: 'number' }),
  col('diem_chuan', 'Điểm chuẩn', { width: 120, align: 'right', type: 'number' }),
  col('thang_diem', 'Thang điểm', { width: 120, align: 'right', type: 'number' }),
  col('cong_thuc_tinh_diem', 'Công thức', { minWidth: 220 }),
  col('to_hop_mon_hoc', 'Tổ hợp', { minWidth: 160 }),
  col('thu_tu_uu_tien', 'Thứ tự', { width: 90, align: 'center' }),
  col('dieu_kien_can', 'Điều kiện cần', { minWidth: 220 }),
  col('dieu_kien_du', 'Điều kiện đủ', { minWidth: 220 }),
  col('ghi_chu_chi_tieu', 'Ghi chú chỉ tiêu', { minWidth: 200 }),
  ghiChu,
]
</script>

<template>
  <BangChiTiet :rows="rows" :columns="columns" />
</template>
