/** Kỳ trả lương. Mã lưu trong dữ liệu, nhãn hiển thị trên giao diện. */
export const KY_LUONG = [
  { value: 'buoi', label: 'Buổi' },
  { value: 'ngay', label: 'Ngày' },
  { value: 'tuan', label: 'Tuần' },
  { value: 'thang', label: 'Tháng' },
  { value: 'nam', label: 'Năm' },
]

export const KY_LUONG_MAC_DINH = 'thang'

export function nhanKyLuong(value) {
  if (value == null || value === '') return ''
  const raw = String(value).trim().toLowerCase()
  return KY_LUONG.find((item) => item.value === raw || item.label.toLowerCase() === raw)?.label || String(value)
}

export function maKyLuong(value) {
  if (value == null || value === '') return KY_LUONG_MAC_DINH
  const raw = String(value).trim().toLowerCase()
  return KY_LUONG.find((item) => item.value === raw || item.label.toLowerCase() === raw)?.value || ''
}
