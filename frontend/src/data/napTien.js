// Hằng số dùng chung cho nạp tiền (khớp backend app/services/nap_tien.py).

export const LOAI_AP_DUNG = [
  { value: 'edu_coin', label: 'Edu coin', donVi: 'Edu coin', tag: 'danger' },
  { value: 'tra_cuu', label: 'Tra cứu', donVi: 'lượt tra cứu', tag: 'primary' },
  { value: 'hoi_dap', label: 'Hỏi đáp', donVi: 'lượt hỏi đáp', tag: 'warning' },
  { value: 'khao_sat', label: 'Khảo sát', donVi: 'lượt khảo sát', tag: 'success' },
  { value: 'token', label: 'Token', donVi: 'token', tag: 'info' },
]

// trang_thai ht_lich_su_nap_tien
export const TRANG_THAI_NAP_TIEN = [
  { value: 0, label: 'Chờ thanh toán', tag: 'warning' },
  { value: 1, label: 'Thành công', tag: 'success' },
  { value: 2, label: 'Đã hủy', tag: 'info' },
  { value: 3, label: 'Thất bại', tag: 'danger' },
]

// trang_thai_doi_soat ht_lich_su_giao_dich_ngan_hang
export const TRANG_THAI_DOI_SOAT = [
  { value: 0, label: 'Chưa khớp', tag: 'warning' },
  { value: 1, label: 'Đã khớp', tag: 'success' },
  { value: 2, label: 'Tiền ra', tag: 'info' },
  { value: 3, label: 'Thiếu tiền', tag: 'danger' },
]

export function timTheoGiaTri(list, value) {
  return list.find((item) => item.value === value) || { value, label: value ?? '—', tag: 'info' }
}

export function hienSo(value) {
  return Number(value || 0).toLocaleString('vi-VN')
}

export function hienTien(value) {
  return `${hienSo(value)} đ`
}

export function hienThoiGian(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return String(value)
  return date.toLocaleString('vi-VN', { hour12: false })
}
