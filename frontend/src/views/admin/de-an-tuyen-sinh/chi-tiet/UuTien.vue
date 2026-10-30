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
  col('muc_giai', 'Mức giải', { width: 140, minWidth: 120 }),
  col('thoi_han_thanh_tich_nam', 'Thời hạn (năm)', { width: 140, align: 'center' }),
  col('pham_vi_chuong_trinh', 'Phạm vi chương trình', { minWidth: 200 }),
  col('hinh_thuc_uu_tien', 'Hình thức ưu tiên', { minWidth: 170 }),
  col('loai_diem_cong', 'Loại điểm cộng', { minWidth: 160 }),
  col('muc_diem_cong', 'Mức điểm cộng', { width: 140, align: 'right', type: 'number' }),
  col('dieu_kien_nguong_dau_vao', 'Ngưỡng đầu vào', { minWidth: 180 }),
  col('chi_tieu_uu_tien', 'Chỉ tiêu', { width: 110, align: 'right', type: 'number' }),
  col('thu_tu_tieu_chi_xet', 'Thứ tự tiêu chí', { minWidth: 180 }),
  col('tieu_chi_phu_khi_dong_diem', 'Tiêu chí đồng điểm', { minWidth: 200 }),
  col('ho_so_minh_chung', 'Hồ sơ minh chứng', { minWidth: 200 }),
  col('thoi_gian_nhan_ho_so', 'Thời gian nhận hồ sơ', { minWidth: 180 }),
  trangThai,
  ghiChu,
]
</script>

<template>
  <BangChiTiet :rows="rows" :columns="columns" />
</template>
