// Giá trị enum của danh mục du học THPT. Khớp backend/app/models/dm_thpt_duhoc.py.

export const LOAI_HINH_DU_HOC = [
  { value: 'du_hoc_nghe', label: 'Du học nghề', mau: 'warning' },
  { value: 'du_hoc_hoc_thuat', label: 'Du học học thuật', mau: 'primary' },
  { value: 'chuyen_tiep', label: 'Chuyển tiếp', mau: 'success' },
]

export const LOAI_CHI_PHI = [
  { value: 'truoc_khi_bay', label: 'Trước khi bay', mau: 'primary' },
  { value: 'tai_nuoc_so_tai', label: 'Tại nước sở tại', mau: 'warning' },
  { value: 'chung_minh_tai_chinh', label: 'Chứng minh tài chính', mau: 'danger' },
  { value: 'khoan_bu_dap', label: 'Khoản bù đắp', mau: 'success' },
]

export const LOAI_KENH = [
  { value: 'chinh_thong', label: 'Chính thống', mau: 'success' },
  { value: 'trung_tam_tu_van', label: 'Trung tâm tư vấn', mau: 'primary' },
  { value: 'cong_dong', label: 'Cộng đồng', mau: 'warning' },
  { value: 'ho_tro_he_thong', label: 'Hỗ trợ hệ thống', mau: 'info' },
]

// Gợi ý đơn vị tiền (ô chọn vẫn cho nhập mã khác).
export const DON_VI_TIEN_DU_HOC = ['VND', 'USD', 'EUR', 'JPY', 'KRW', 'AUD', 'GBP', 'SGD', 'CAD', 'TWD', 'CNY']

export function nhanEnum(ds, value) {
  return ds.find((item) => item.value === value)?.label || value || '—'
}

export function mauEnum(ds, value) {
  return ds.find((item) => item.value === value)?.mau || 'info'
}
