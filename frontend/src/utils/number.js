/** Định dạng số nguyên kiểu Việt Nam: 1000000 → 1.000.000 */
export function formatInteger(value) {
  if (value == null || value === '') return ''
  const num = Math.round(Number(value))
  if (Number.isNaN(num)) return ''
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.')
}

/** Parse chuỗi nhập tiền về số nguyên */
export function parseIntegerInput(text) {
  if (text == null || text === '') return null
  const digits = String(text).replace(/\D/g, '')
  if (!digits) return null
  const num = Number(digits)
  return Number.isNaN(num) ? null : num
}

/**
 * Formatter cho el-input-number: chuỗi số thô ("-1234.5") → hiển thị kiểu Việt Nam ("-1.234,5").
 * Giữ nguyên phần thập phân đang gõ dở (ví dụ "8." → "8,").
 */
export function formatSoNhap(raw) {
  if (raw == null || raw === '') return ''
  const text = String(raw)
  const am = text.startsWith('-') ? '-' : ''
  const [nguyen, thapPhan] = text.slice(am.length).split('.')
  const nhom = nguyen.replace(/\B(?=(\d{3})+(?!\d))/g, '.')
  return am + nhom + (thapPhan !== undefined ? `,${thapPhan}` : '')
}

/**
 * Parser cho el-input-number: chuỗi đang hiển thị ("1.234,5") → chuỗi số thô ("1234.5").
 * Dấu "." là phân tách hàng nghìn, "," là thập phân; dấu "." vừa gõ ở cuối (chưa có ",") được hiểu là thập phân.
 */
export function parseSoNhap(text) {
  if (text == null) return ''
  let value = String(text).trim()
  if (value.endsWith('.') && !value.includes(',')) value = `${value.slice(0, -1)},`
  const am = value.startsWith('-') ? '-' : ''
  const [nguyen, ...phanSau] = value.split(',')
  const so = nguyen.replace(/\D/g, '')
  if (!phanSau.length) return am + so
  return `${am}${so}.${phanSau.join('').replace(/\D/g, '')}`
}
