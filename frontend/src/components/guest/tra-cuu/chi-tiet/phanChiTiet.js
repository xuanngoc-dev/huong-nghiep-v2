// Hàm dùng chung cho các modal chi tiết tra cứu (ChiTiet*Modal.vue): dựng dòng thông tin cho CardThongTin.vue.
// Dòng = { label, giaTri, href?, ghiChu? }; CardThongTin tự ẩn dòng rỗng.
// Tách khỏi .vue để test được bằng node --test.

export const LOAI_CHUNG_CHI = { quoc_te: 'Quốc tế', trong_nuoc: 'Trong nước' }

export function coGiaTri(value) {
  return value !== null && value !== undefined && String(value).trim() !== ''
}

/** Bỏ giá trị rỗng khỏi danh sách nhãn. */
export function locNhan(values) {
  return values.filter(coGiaTri)
}

/** Dòng thông tin; mảng (bậc đào tạo, hình thức thi…) nối bằng dấu phẩy, có thể kèm đơn vị. */
export function o(label, giaTri, { donVi = '' } = {}) {
  let value = Array.isArray(giaTri) ? locNhan(giaTri).join(', ') : giaTri
  if (donVi && coGiaTri(value)) value = `${value} ${donVi}`
  return { label, giaTri: value }
}

/** Website nhập thiếu giao thức (vd. "hust.edu.vn") → thêm https:// để không thành link tương đối. */
export function duongDan(value) {
  const url = String(value).trim()
  return /^https?:\/\//i.test(url) ? url : `https://${url}`
}

/** Dòng có link: web mở tab mới, email/điện thoại mở ứng dụng tương ứng. */
export function oLink(label, giaTri, kieu = 'web') {
  const row = o(label, giaTri)
  if (!coGiaTri(row.giaTri)) return row
  const value = String(row.giaTri).trim()
  const href = { web: duongDan(value), email: `mailto:${value}`, tel: `tel:${value.replace(/[^\d+]/g, '')}` }[kieu]
  return { ...row, href }
}

/** Nút lối tắt ở đầu modal (website, nguồn dữ liệu…): bỏ mục không có link. */
export function loiTat(items) {
  return items.filter((item) => coGiaTri(item.url)).map((item) => ({ label: item.label, href: duongDan(item.url) }))
}

/** Danh sách [{ name, value, ghi_chu }] (mô tả công việc, lộ trình… của ngành) → dòng thông tin. */
export function dongTuDanhSach(list) {
  if (!Array.isArray(list)) return []
  return list
    .filter((item) => item && coGiaTri(item.value))
    .map((item) => ({ label: item.name || '', giaTri: item.value, ghiChu: item.ghi_chu || '' }))
}

/** Năm áp dụng: "Từ 2026", "2026 – 2028", chỉ có năm kết thúc → "Đến 2028". */
export function khoangNam(tu, den) {
  if (coGiaTri(tu) && coGiaTri(den)) return String(tu) === String(den) ? String(tu) : `${tu} – ${den}`
  if (coGiaTri(tu)) return `Từ ${tu}`
  if (coGiaTri(den)) return `Đến ${den}`
  return null
}
