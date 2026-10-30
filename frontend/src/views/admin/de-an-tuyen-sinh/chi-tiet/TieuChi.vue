<script setup>
import BangChiTiet from './BangChiTiet.vue'
import { col, cotChung } from './cot'

defineProps({
  rows: { type: Array, default: () => [] },
})

const { chuongTrinh, phuongThuc, ghiChu, trangThai, nguon } = cotChung()

const columns = [
  col('ma_tieu_chi', 'Mã', { width: 120, align: 'center' }),
  col('ten_tieu_chi', 'Tên tiêu chí', { minWidth: 220 }),
  col('loai_tieu_chi', 'Loại', { width: 130, minWidth: 120 }),
  col('thu_tu_ap_dung', 'Thứ tự', { width: 90, align: 'center' }),
  col('toan_tu_so_sanh', 'Toán tử', { width: 110, align: 'center' }),
  col('gia_tri_tieu_chi', 'Giá trị', { minWidth: 160 }),
  col('noi_dung_tieu_chi', 'Nội dung', { minWidth: 260 }),
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
