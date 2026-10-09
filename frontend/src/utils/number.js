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
