// Giá trị enum của danh mục hướng đi sau THCS. Khớp backend/app/models/dm_thcs_huong_di.py.
export { mauEnum, nhanEnum } from '@/constants/thptDuHoc'

export const MUC_DO_AP_LUC_HOC_TAP = [
  { value: 'thap', label: 'Thấp', mau: 'success' },
  { value: 'trung_binh', label: 'Trung bình', mau: 'warning' },
  { value: 'cao', label: 'Cao', mau: 'danger' },
]

export const MUC_DO_TU_GIAC = [
  { value: 'trung_binh', label: 'Trung bình', mau: 'success' },
  { value: 'cao', label: 'Cao', mau: 'warning' },
  { value: 'rat_cao', label: 'Rất cao', mau: 'danger' },
]

export const LOAI_UU_NHUOC_DIEM = [
  { value: 'uu_diem', label: 'Ưu điểm', mau: 'success' },
  { value: 'nhuoc_diem', label: 'Nhược điểm', mau: 'danger' },
]

export const DOI_TUONG_NHAN_LUU_Y = [
  { value: 'ca_hai', label: 'Cả học sinh và phụ huynh', mau: 'info' },
  { value: 'hoc_sinh', label: 'Học sinh', mau: 'primary' },
  { value: 'phu_huynh', label: 'Phụ huynh', mau: 'warning' },
]

export const MUC_DIEM_PHU_HOP = [
  { value: 1, label: '1 - Rất ít phù hợp' },
  { value: 2, label: '2 - Ít phù hợp' },
  { value: 3, label: '3 - Phù hợp vừa' },
  { value: 4, label: '4 - Phù hợp' },
  { value: 5, label: '5 - Rất phù hợp' },
]

export function mauDiem(diem) {
  if (diem >= 5) return 'success'
  if (diem >= 4) return 'primary'
  if (diem >= 3) return 'warning'
  return 'info'
}
