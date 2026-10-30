<script setup>
import BangChiTiet from './BangChiTiet.vue'
import { col, cotChung } from './cot'

defineProps({
  rows: { type: Array, default: () => [] },
})

const { ghiChu } = cotChung()

const columns = [
  col('nhom_nhan_su', 'Nhóm', { minWidth: 160 }),
  col('ten_nhan_su', 'Tên', { minWidth: 200 }),
  col('chuc_danh', 'Chức danh', { minWidth: 160 }),
  col('hoc_vi', 'Học vị', { width: 140, minWidth: 120 }),
  col('hoc_ham', 'Học hàm', { width: 140, minWidth: 120 }),
  col('linh_vuc_chuyen_mon', 'Lĩnh vực', { minWidth: 180 }),
  col('so_luong', 'Số lượng', { width: 110, align: 'right', type: 'number' }),
  col('nam_thong_ke', 'Năm thống kê', { width: 130, align: 'center' }),
  ghiChu,
]
</script>

<template>
  <BangChiTiet :rows="rows" :columns="columns" />
</template>
