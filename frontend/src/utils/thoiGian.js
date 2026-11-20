// Múi giờ hiển thị, khớp TIMEZONE của backend (mặc định giờ Việt Nam, UTC+7). Đổi bằng VITE_TIMEZONE.
export const MUI_GIO = import.meta.env?.VITE_TIMEZONE || 'Asia/Ho_Chi_Minh'

// Chuỗi ngày giờ không kèm múi giờ (API trả cột DateTime theo múi giờ hệ thống, không có offset).
const KHONG_MUI_GIO = /^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2})(?::(\d{2})(?:\.(\d{1,6}))?)?)?$/

const MAC_DINH = { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }

// Số phút múi giờ lệch so với UTC tại một thời điểm.
function lechPhut(thoiDiem) {
  const phan = Object.fromEntries(
    new Intl.DateTimeFormat('en-US', {
      timeZone: MUI_GIO,
      hourCycle: 'h23',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
      .formatToParts(thoiDiem)
      .map((p) => [p.type, Number(p.value)]),
  )
  const theoMuiGio = Date.UTC(phan.year, phan.month - 1, phan.day, phan.hour, phan.minute, phan.second)
  return Math.round((theoMuiGio - Math.floor(thoiDiem.getTime() / 1000) * 1000) / 60000)
}

/** Đọc giá trị thời gian từ API thành Date; chuỗi không kèm múi giờ hiểu theo MUI_GIO (không theo máy người xem). */
export function docThoiGian(value) {
  if (value == null || value === '') return null
  if (value instanceof Date || typeof value === 'number') {
    const date = new Date(value)
    return Number.isNaN(date.getTime()) ? null : date
  }
  const khop = KHONG_MUI_GIO.exec(String(value).trim())
  if (khop) {
    const [, nam, thang, ngay, gio = '0', phut = '0', giay = '0', le = '0'] = khop
    const gocUtc = Date.UTC(+nam, +thang - 1, +ngay, +gio, +phut, +giay, Number(le.padEnd(3, '0').slice(0, 3)))
    return new Date(gocUtc - lechPhut(new Date(gocUtc)) * 60000)
  }
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? null : date
}

/** Ngày giờ theo MUI_GIO, mặc định dạng "20/11/2026, 17:30"; giá trị rỗng / sai trả `macDinh`. */
export function dinhDangThoiGian(value, options = MAC_DINH, macDinh = '') {
  const date = docThoiGian(value)
  return date ? date.toLocaleString('vi-VN', { ...options, timeZone: MUI_GIO }) : macDinh
}

/** Ngày theo MUI_GIO dạng "20/11/2026". */
export function dinhDangNgay(value, macDinh = '') {
  const date = docThoiGian(value)
  return date ? date.toLocaleDateString('vi-VN', { timeZone: MUI_GIO }) : macDinh
}

/** Thứ trong tuần theo MUI_GIO (0 = Chủ nhật), như Date.getDay(). */
export function thuTrongTuan(value) {
  const date = docThoiGian(value)
  if (!date) return null
  const ten = new Intl.DateTimeFormat('en-US', { timeZone: MUI_GIO, weekday: 'short' }).format(date)
  return ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(ten)
}
