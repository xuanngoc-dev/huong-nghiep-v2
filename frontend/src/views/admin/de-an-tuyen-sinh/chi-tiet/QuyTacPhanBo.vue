<script setup>
import BangChiTiet from './BangChiTiet.vue'
import { col, cotChung } from './cot'

defineProps({
  rows: { type: Array, default: () => [] },
})

const { chuongTrinh, phuongThuc, ghiChu, trangThai, nguon } = cotChung()

const columns = [
  col('kieu_phan_bo', 'Kiểu phân bổ', { minWidth: 160 }),
  col('thu_tu_uu_tien', 'Thứ tự', { width: 90, align: 'center' }),
  col('quy_tac_xu_ly_dong_diem', 'Xử lý đồng điểm', { minWidth: 220 }),
  col('quy_tac_chuyen_chi_tieu', 'Chuyển chỉ tiêu', { minWidth: 220 }),
  col('noi_dung_quy_tac', 'Nội dung', { minWidth: 260 }),
  chuongTrinh,
  phuongThuc,
  nguon,
  trangThai,
  ghiChu,
]
</script>

<template>
  <BangChiTiet :rows="rows" :columns="columns" />
</template>
