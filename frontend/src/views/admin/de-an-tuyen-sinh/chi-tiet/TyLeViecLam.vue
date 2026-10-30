<script setup>
import BangChiTiet from './BangChiTiet.vue'
import { col, cotChung } from './cot'

defineProps({
  rows: { type: Array, default: () => [] },
})

const { nguon, trinhDo } = cotChung()

const columns = [
  col('nganh', 'Ngành', { minWidth: 220 }),
  trinhDo,
  col('nam_tot_nghiep', 'Năm tốt nghiệp', { width: 140, align: 'center' }),
  col('thoi_diem_khao_sat_thang', 'Khảo sát (tháng)', { width: 150, align: 'center' }),
  col('so_nguoi_tot_nghiep', 'Số tốt nghiệp', { width: 130, align: 'right', type: 'number' }),
  col('so_nguoi_co_viec_lam', 'Có việc làm', { width: 130, align: 'right', type: 'number' }),
  col('ty_le_co_viec_lam', 'Tỷ lệ (%)', { width: 110, align: 'right', type: 'number' }),
  col('phuong_phap_khao_sat', 'Phương pháp', { minWidth: 180 }),
  nguon,
]
</script>

<template>
  <BangChiTiet :rows="rows" :columns="columns" />
</template>
