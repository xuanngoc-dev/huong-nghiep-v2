export const TRINH_DO_LABELS = {
  dai_hoc: 'Đại học',
  thac_si: 'Thạc sĩ',
  tien_si: 'Tiến sĩ',
  cao_dang: 'Cao đẳng',
  trung_cap: 'Trung cấp',
}

export const HINH_THUC_LABELS = {
  chinh_quy: 'Chính quy',
  lien_thong: 'Liên thông',
  vua_hoc_vua_lam: 'Vừa học vừa làm',
  tu_xa: 'Đào tạo từ xa',
  van_bang_2: 'Văn bằng 2',
}

export const STATUS_LABELS = {
  nhap: 'Nháp',
  cong_bo: 'Đã công bố',
  het_hieu_luc: 'Hết hiệu lực',
}

export function formatDate(value) {
  if (!value) return '—'
  const [year, month, day] = String(value).slice(0, 10).split('-')
  if (!year || !month || !day) return value
  return `${day}/${month}/${year}`
}

function formatToken(value) {
  if (value == null || value === '') return ''
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

export function formatCell(value, column) {
  if (column?.type === 'bool') {
    if (value == null || value === '') return '—'
    return value ? 'Có' : 'Không'
  }
  if (value == null || value === '') return '—'
  if (column?.type === 'status') return STATUS_LABELS[value] || String(value)
  if (column?.type === 'code') return column.labels?.[value] || String(value)
  if (column?.type === 'date') return formatDate(value)
  if (column?.type === 'number') {
    const number = Number(value)
    if (Number.isFinite(number)) return number.toLocaleString('vi-VN')
  }
  if (Array.isArray(value)) {
    const text = value.map(formatToken).filter(Boolean).join(', ')
    return text || '—'
  }
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

export function formatQuota(value) {
  if (value == null || value === '') return '—'
  return Number(value).toLocaleString('vi-VN')
}
