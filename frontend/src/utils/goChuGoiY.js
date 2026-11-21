// Hiệu ứng gõ chữ cho placeholder: gõ từng ký tự → dừng để đọc → xóa từng ký tự → sang gợi ý kế tiếp.
// Hàm thuần (không hẹn giờ) để test được; phần hẹn giờ ở composables/useGoChuGoiY.js.

export const THOI_GIAN_GO_CHU = { go: 70, xoa: 35, dungSauGo: 1600, dungSauXoa: 300 }

export const TRANG_THAI_DAU = { chiSo: 0, soKyTu: 0, dangXoa: false }

function doDai(chu) {
  return Array.from(chu || '').length
}

/** Bước kế tiếp: trả về { trangThai, cho } — trạng thái mới và số ms chờ trước bước sau. */
export function buocGoChu({ chiSo, soKyTu, dangXoa }, danhSach, t = THOI_GIAN_GO_CHU) {
  if (!danhSach.length) return { trangThai: { ...TRANG_THAI_DAU }, cho: t.go }
  const tong = doDai(danhSach[chiSo])
  if (!dangXoa) {
    if (soKyTu < tong) {
      const moi = soKyTu + 1
      return { trangThai: { chiSo, soKyTu: moi, dangXoa: false }, cho: moi === tong ? t.dungSauGo : t.go }
    }
    return { trangThai: { chiSo, soKyTu, dangXoa: true }, cho: t.xoa }
  }
  if (soKyTu > 0) {
    const moi = soKyTu - 1
    return { trangThai: { chiSo, soKyTu: moi, dangXoa: true }, cho: moi === 0 ? t.dungSauXoa : t.xoa }
  }
  const tiepTheo = (chiSo + 1) % danhSach.length
  return { trangThai: { chiSo: tiepTheo, soKyTu: 0, dangXoa: false }, cho: t.go }
}

/** Phần chữ đang hiện của gợi ý hiện tại. */
export function chuDangHien({ chiSo, soKyTu }, danhSach) {
  return Array.from(danhSach[chiSo] || '').slice(0, soKyTu).join('')
}
