<script setup>
import BangChiTiet from './BangChiTiet.vue'
import { col, cotChung } from './cot'

defineProps({
  rows: { type: Array, default: () => [] },
})

const { chuongTrinh, ghiChu, trangThai } = cotChung()

const columns = [
  col('ma_doi_tuong', 'Mã', { width: 120, align: 'center' }),
  col('ten_doi_tuong', 'Tên đối tượng', { minWidth: 240 }),
  col('mo_ta', 'Mô tả', { minWidth: 240 }),
  col('nam_tot_nghiep_tu', 'Tốt nghiệp từ', { width: 130, align: 'center' }),
  col('nam_tot_nghiep_den', 'Tốt nghiệp đến', { width: 140, align: 'center' }),
  col('pham_vi_ap_dung', 'Phạm vi', { minWidth: 160 }),
  chuongTrinh,
  trangThai,
  ghiChu,
]
</script>

<template>
  <BangChiTiet :rows="rows" :columns="columns" />
</template>
