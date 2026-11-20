// Định dạng dữ liệu danh mục xuất khẩu lao động THPT để hiển thị ở trang khách.

// Thu nhập nhóm nghề lưu theo triệu VNĐ/tháng; ưu tiên phần mô tả chữ.
export function thuNhap(nhom) {
  if (nhom.muc_thu_nhap_text) return nhom.muc_thu_nhap_text
  const min = nhom.thu_nhap_thang_min != null ? Number(nhom.thu_nhap_thang_min) : null
  const max = nhom.thu_nhap_thang_max != null ? Number(nhom.thu_nhap_thang_max) : null
  if (min == null && max == null) return ''
  if (min != null && max != null && min !== max) return `${min} - ${max} triệu VNĐ/tháng`
  return `${max ?? min} triệu VNĐ/tháng`
}

export function thoiGianChuanBi(nhom) {
  if (nhom.thoi_gian_chuan_bi_text) return nhom.thoi_gian_chuan_bi_text
  const min = nhom.thoi_gian_chuan_bi_thang_min || 0
  const max = nhom.thoi_gian_chuan_bi_thang_max || 0
  if (!min && !max) return ''
  if (min && max && min !== max) return `${min} - ${max} tháng`
  return `${max || min} tháng`
}

const dinhDangSo = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2 })

export function khoangTien(item) {
  const min = item.chi_phi_min != null ? Number(item.chi_phi_min) : null
  const max = item.chi_phi_max != null ? Number(item.chi_phi_max) : null
  const donVi = item.don_vi_tien || 'VND'
  if (min == null && max == null) return 'Tùy trường hợp'
  if (min != null && max != null && min !== max) return `${dinhDangSo.format(min)} - ${dinhDangSo.format(max)} ${donVi}`
  return `${dinhDangSo.format(max ?? min)} ${donVi}`
}
