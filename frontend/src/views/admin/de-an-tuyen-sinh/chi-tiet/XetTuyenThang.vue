<script setup>
import BangChiTiet from './BangChiTiet.vue'
import { col, cotChung } from './cot'

defineProps({
  rows: { type: Array, default: () => [] },
})

const { ghiChu, trangThai } = cotChung()

const columns = [
  col('ma_chinh_sach', 'Mã', { width: 120, align: 'center' }),
  col('ten_chinh_sach', 'Tên chính sách', { minWidth: 220 }),
  col('nhom_doi_tuong', 'Nhóm đối tượng', { minWidth: 180 }),
  col('can_cu_phap_ly', 'Căn cứ', { minWidth: 180 }),
  col('mo_ta_doi_tuong', 'Mô tả đối tượng', { minWidth: 240 }),
  col('mon_thi_linh_vuc', 'Môn / lĩnh vực', { minWidth: 160 }),
  col('cap_thi', 'Cấp thi', { width: 120, minWidth: 110 }),
  col('muc_giai', 'Mức giải', { width: 140, minWidth: 120 }),
  col('thoi_han_thanh_tich_nam', 'Thời hạn (năm)', { width: 140, align: 'center' }),
  col('pham_vi_chuong_trinh', 'Phạm vi chương trình', { minWidth: 200 }),
  col('dieu_kien_phu', 'Điều kiện phụ', { minWidth: 200 }),
  col('chi_tieu_tuyen_thang', 'Chỉ tiêu', { width: 110, align: 'right', type: 'number' }),
  col('ho_so_minh_chung', 'Hồ sơ minh chứng', { minWidth: 200 }),
  col('thu_tu_tieu_chi_xet', 'Thứ tự tiêu chí', { minWidth: 180 }),
  col('tieu_chi_phu_khi_dong_diem', 'Tiêu chí đồng điểm', { minWidth: 200 }),
  col('nguyen_tac_khi_vuot_chi_tieu', 'Khi vượt chỉ tiêu', { minWidth: 200 }),
  col('thoi_gian_nhan_ho_so', 'Thời gian nhận hồ sơ', { minWidth: 180 }),
  trangThai,
  ghiChu,
]
</script>

<template>
  <BangChiTiet :rows="rows" :columns="columns" />
</template>
