/** Đơn vị tiền dùng chung cho mức lương. Mã lưu trong dữ liệu, nhãn hiển thị trên giao diện. */
export const DON_VI_TIEN = [
  { value: 'VND', label: 'VNĐ' },
  { value: 'USD', label: 'USD' },
  { value: 'EUR', label: 'EUR' },
]

export const DON_VI_TIEN_MAC_DINH = 'VND'

export function nhanDonViTien(value) {
  if (value == null || value === '') return ''
  return DON_VI_TIEN.find((item) => item.value === value)?.label || String(value)
}
