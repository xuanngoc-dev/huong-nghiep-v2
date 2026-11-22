// Định dạng thông tin nghề cụ thể đi làm cho trang khách (Thư viện ngành nghề).

export const MUC_DO_AP_LUC = {
  thap: 'Áp lực thấp',
  trung_binh: 'Áp lực trung bình',
  cao: 'Áp lực cao',
}

function laSo(value) {
  return value != null && value !== '' && Number.isFinite(Number(value))
}

function trieu(value) {
  return (Number(value) / 1_000_000).toLocaleString('vi-VN')
}

/** Khoảng lương của nghề (VND, số tiền đầy đủ) dạng "7 - 13 triệu/tháng"; chưa có số hoặc không phải VND/tháng thì ''. */
export function khoangTrieu(nghe, tu, den) {
  const theoThang = (nghe.don_vi_tien_te || 'VND') === 'VND' && (nghe.chu_ky_luong || 'thang') === 'thang'
  if (!theoThang || (!laSo(tu) && !laSo(den))) return ''
  if (laSo(tu) && laSo(den) && Number(tu) !== Number(den)) return `${trieu(tu)} - ${trieu(den)} triệu/tháng`
  return `${trieu(laSo(tu) ? tu : den)} triệu/tháng`
}

/**
 * Dải lương của nghề: từ khởi điểm thấp nhất đến mức cao nhất đang có (mức cao → trung bình → khởi điểm).
 * Nghề chưa có lương thì lấy theo nhóm (lương nhóm tính bằng triệu đồng/tháng).
 */
export function daiLuong(nghe, nhom) {
  const den = [nghe.luong_cao_max, nghe.luong_trung_binh_max, nghe.luong_khoi_diem_max].find(laSo)
  const theoNghe = khoangTrieu(nghe, nghe.luong_khoi_diem_min, den)
  if (theoNghe) return theoNghe
  if (!nhom) return 'Đang cập nhật'
  if (nhom.muc_luong_text) return nhom.muc_luong_text
  const tuNhom = nhom.luong_khoi_diem_min
  const denNhom = [nhom.luong_kinh_nghiem_max, nhom.luong_khoi_diem_max].find(laSo)
  if (!laSo(tuNhom) && !laSo(denNhom)) return 'Đang cập nhật'
  const so = (value) => Number(value).toLocaleString('vi-VN')
  if (laSo(tuNhom) && laSo(denNhom) && Number(tuNhom) !== Number(denNhom)) {
    return `${so(tuNhom)} - ${so(denNhom)} triệu/tháng`
  }
  return `${so(laSo(tuNhom) ? tuNhom : denNhom)} triệu/tháng`
}

/** Tách mục dạng danh sách (ngăn cách bằng dấu ;) thành mảng, bỏ mục rỗng. */
export function tachDanhSach(value) {
  return String(value || '')
    .split(';')
    .map((item) => item.trim())
    .filter(Boolean)
}
