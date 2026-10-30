<script setup>
import BangChiTiet from './BangChiTiet.vue'
import { col, cotChung } from './cot'

defineProps({
  rows: { type: Array, default: () => [] },
})

const { ghiChu } = cotChung()

const columns = [
  col('ten_co_so', 'Cơ sở', { minWidth: 180 }),
  col('loai_co_so_vat_chat', 'Loại', { minWidth: 160 }),
  col('ten_hang_muc', 'Hạng mục', { minWidth: 220 }),
  col('so_luong', 'Số lượng', { width: 120, align: 'right', type: 'number' }),
  col('don_vi_tinh', 'Đơn vị', { width: 110, minWidth: 100 }),
  col('muc_dich_su_dung', 'Mục đích', { minWidth: 200 }),
  col('nam_thong_ke', 'Năm thống kê', { width: 130, align: 'center' }),
  ghiChu,
]
</script>

<template>
  <BangChiTiet :rows="rows" :columns="columns" />
</template>
