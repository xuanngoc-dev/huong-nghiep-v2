<script setup>
import BangChiTiet from './BangChiTiet.vue'
import { col, cotChung } from './cot'

defineProps({
  rows: { type: Array, default: () => [] },
})

const { chuongTrinh, phuongThuc, ghiChu, trangThai, nguon, nam } = cotChung()

const columns = [
  col('loai_diem_cong', 'Loại', { minWidth: 160 }),
  col('ma_doi_tuong_cong', 'Mã đối tượng', { width: 140, align: 'center' }),
  col('doi_tuong_duoc_cong', 'Đối tượng được cộng', { minWidth: 220 }),
  col('dieu_kien_ap_dung', 'Điều kiện', { minWidth: 220 }),
  col('diem_cong', 'Điểm cộng', { width: 120, align: 'right', type: 'number' }),
  col('thang_diem', 'Thang điểm', { width: 120, align: 'right', type: 'number' }),
  col('muc_diem_cong_toi_da', 'Mức tối đa', { width: 120, align: 'right', type: 'number' }),
  col('co_cong_don', 'Cộng dồn', { width: 110, align: 'center', type: 'bool' }),
  col('quy_tac_ket_hop', 'Quy tắc kết hợp', { minWidth: 200 }),
  nam,
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
