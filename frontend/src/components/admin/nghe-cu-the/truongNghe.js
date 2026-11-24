// Nhãn và định dạng các trường của nghề cụ thể đi làm, dùng chung cho form, bảng và modal chi tiết (khu quản trị).

export const MUC_DO_AP_LUC = [
  { value: 'thap', label: 'Thấp', mau: 'success' },
  { value: 'trung_binh', label: 'Trung bình', mau: 'warning' },
  { value: 'cao', label: 'Cao', mau: 'danger' },
]

export const CHU_KY_LUONG = [
  { value: 'gio', label: 'Theo giờ', donVi: 'giờ' },
  { value: 'ngay', label: 'Theo ngày', donVi: 'ngày' },
  { value: 'thang', label: 'Theo tháng', donVi: 'tháng' },
  { value: 'nam', label: 'Theo năm', donVi: 'năm' },
]

// Ô văn bản nhiều dòng của thông tin chi tiết, chia theo nhóm hiển thị trong form.
// Các mục dạng danh sách (vị trí, kỹ năng, chứng chỉ) ngăn cách bằng dấu ;
export const VAN_BAN_CHUNG = [
  { key: 'mo_ta_cong_viec', label: 'Mô tả công việc', toiDa: 10000, placeholder: 'Nhập mô tả công việc' },
  { key: 'trach_nhiem_chinh', label: 'Trách nhiệm chính', toiDa: 10000, placeholder: 'Nhập các trách nhiệm chính' },
  {
    key: 'vi_tri_tuyen_dung_mau',
    label: 'Vị trí tuyển dụng mẫu',
    toiDa: 5000,
    placeholder: 'Nhập tên vị trí, ngăn cách bằng dấu ;',
  },
]
export const VAN_BAN_DAO_TAO = [
  { key: 'chuyen_nganh_phu_hop', label: 'Chuyên ngành phù hợp', toiDa: 5000, placeholder: 'Nhập chuyên ngành, ngăn cách bằng dấu ;' },
  { key: 'chung_chi_giay_phep', label: 'Chứng chỉ / giấy phép', toiDa: 5000, placeholder: 'Nhập chứng chỉ, giấy phép' },
  { key: 'ky_nang_chuyen_mon', label: 'Kỹ năng chuyên môn', toiDa: 5000, placeholder: 'Nhập kỹ năng, ngăn cách bằng dấu ;' },
  { key: 'ky_nang_mem', label: 'Kỹ năng mềm', toiDa: 5000, placeholder: 'Nhập kỹ năng, ngăn cách bằng dấu ;' },
]
export const VAN_BAN_MOI_TRUONG = [
  { key: 'moi_truong_lam_viec', label: 'Môi trường làm việc', toiDa: 5000, placeholder: 'Nhập môi trường làm việc' },
  { key: 'trien_vong_nghe_nghiep', label: 'Triển vọng nghề nghiệp', toiDa: 5000, placeholder: 'Nhập triển vọng nghề nghiệp' },
]
// Lộ trình phát triển (lo_trinh_phat_trien) nhập riêng theo giai đoạn: xem BangLoTrinhNghe.vue và các hàm *LoTrinh bên dưới.
// Lương: số tiền đầy đủ theo đơn vị tiền tệ (API trả Decimal dạng chuỗi).
export const TRUONG_LUONG = [
  { key: 'luong_khoi_diem_min', label: 'Lương khởi điểm từ' },
  { key: 'luong_khoi_diem_max', label: 'Lương khởi điểm đến' },
  { key: 'luong_trung_binh_min', label: 'Lương trung bình từ' },
  { key: 'luong_trung_binh_max', label: 'Lương trung bình đến' },
  { key: 'luong_cao_min', label: 'Lương mức cao từ' },
  { key: 'luong_cao_max', label: 'Lương mức cao đến' },
]
// Ba mức lương dạng khoảng (từ - đến) để hiển thị.
export const KHOANG_LUONG = [
  { key: 'luong_khoi_diem', label: 'Lương khởi điểm' },
  { key: 'luong_trung_binh', label: 'Lương trung bình' },
  { key: 'luong_cao', label: 'Lương mức cao' },
]

export function soHoacNull(value) {
  if (value == null || value === '') return null
  const so = Number(value)
  return Number.isFinite(so) ? so : null
}

export function nhanMucDoApLuc(value) {
  return MUC_DO_AP_LUC.find((item) => item.value === value)
}

/** Khoảng lương của một mức, ví dụ "8.000.000 - 10.000.000 VND/tháng"; chưa có số thì trả ''. */
export function khoangLuong(nghe, tienTo) {
  const tu = soHoacNull(nghe[`${tienTo}_min`])
  const den = soHoacNull(nghe[`${tienTo}_max`])
  if (tu == null && den == null) return ''
  const dinhDang = (so) => so.toLocaleString('vi-VN')
  const khoang = tu != null && den != null && tu !== den ? `${dinhDang(tu)} - ${dinhDang(den)}` : dinhDang(tu ?? den)
  const chuKy = CHU_KY_LUONG.find((item) => item.value === nghe.chu_ky_luong)?.donVi || 'tháng'
  return `${khoang} ${nghe.don_vi_tien_te || 'VND'}/${chuKy}`
}

/** Một giai đoạn lộ trình trống (dòng mới trong bảng nhập). */
export function buocLoTrinhRong() {
  return { giai_doan: '', mo_ta_cong_viec: '', luong_trung_binh_min: null, luong_trung_binh_max: null, ghi_chu: '' }
}

/** Lộ trình từ API (mảng giai đoạn; dữ liệu cũ có thể là chuỗi "A → B") → mảng cho form sửa. */
export function dsLoTrinh(value) {
  if (Array.isArray(value)) {
    return value.map((buoc) => ({
      ...buocLoTrinhRong(),
      ...buoc,
      mo_ta_cong_viec: buoc.mo_ta_cong_viec || '',
      ghi_chu: buoc.ghi_chu || '',
      luong_trung_binh_min: soHoacNull(buoc.luong_trung_binh_min),
      luong_trung_binh_max: soHoacNull(buoc.luong_trung_binh_max),
    }))
  }
  return String(value || '')
    .split(/→|->|=>/)
    .map((ten) => ten.trim().replace(/\.$/, '').trim())
    .filter(Boolean)
    .map((ten) => ({ ...buocLoTrinhRong(), giai_doan: ten }))
}

/**
 * Lộ trình từ form / JSON import → payload: bỏ dòng trống hoàn toàn, chữ rỗng → null; không còn dòng nào → null.
 * Chuỗi kiểu cũ "A → B → C" giữ nguyên để API tự tách.
 */
export function chuanHoaLoTrinh(value) {
  if (typeof value === 'string') return value.trim() || null
  if (!Array.isArray(value)) return null
  const chu = (v) => (v == null ? null : String(v).trim() || null)
  const ds = value
    .filter((buoc) => buoc && typeof buoc === 'object')
    .map((buoc) => ({
      giai_doan: chu(buoc.giai_doan) || '',
      mo_ta_cong_viec: chu(buoc.mo_ta_cong_viec),
      luong_trung_binh_min: soHoacNull(buoc.luong_trung_binh_min),
      luong_trung_binh_max: soHoacNull(buoc.luong_trung_binh_max),
      ghi_chu: chu(buoc.ghi_chu),
    }))
    .filter(
      (buoc) =>
        buoc.giai_doan ||
        buoc.mo_ta_cong_viec ||
        buoc.ghi_chu ||
        buoc.luong_trung_binh_min != null ||
        buoc.luong_trung_binh_max != null,
    )
  return ds.length ? ds : null
}

/** Lỗi đầu tiên của lộ trình trên form (thiếu tên giai đoạn, lương từ > đến); hợp lệ thì ''. */
export function loiLoTrinh(value) {
  const ds = chuanHoaLoTrinh(Array.isArray(value) ? value : []) || []
  for (const [i, buoc] of ds.entries()) {
    if (!buoc.giai_doan) return `Giai đoạn ${i + 1}: vui lòng nhập tên giai đoạn`
    const { luong_trung_binh_min: tu, luong_trung_binh_max: den } = buoc
    if (tu != null && den != null && tu > den) return `Giai đoạn ${i + 1}: lương trung bình từ phải ≤ đến`
  }
  return ''
}

/** Tên các giai đoạn nối bằng "→" (cột bảng danh sách); chưa có thì ''. */
export function tenLoTrinh(value) {
  return dsLoTrinh(value)
    .map((buoc) => buoc.giai_doan)
    .join(' → ')
}
