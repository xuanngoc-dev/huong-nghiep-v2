import { nhanDonViTien } from '@/constants/donViTien'
import { nhanKyLuong } from '@/constants/kyLuong'

function soTien(value) {
  if (value == null || value === '') return null
  const num = Number(value)
  return Number.isFinite(num) ? Math.round(num * 10) / 10 : null
}

export function hienSoTien(value) {
  const num = soTien(value)
  if (num == null) return ''
  const text = Number.isInteger(num) ? String(num) : num.toFixed(1)
  return text.replace('.', ',')
}

export function danhSachMucLuong(value) {
  if (value == null || value === '') return []
  if (typeof value === 'string') {
    const text = value.trim()
    return text ? [{ name: '', min: null, max: null, unit: '', value: text }] : []
  }
  if (!Array.isArray(value)) return []
  return value
    .map((item) => {
      if (item == null) return null
      if (typeof item !== 'object') {
        const text = String(item).trim()
        return text ? { name: '', min: null, max: null, unit: '', value: text } : null
      }
      const name = String(item.name ?? item.ten ?? '').trim()
      const legacy = String(item.value ?? item.gia_tri ?? item.mo_ta ?? '').trim()
      const min = soTien(item.min ?? item.tu)
      const max = soTien(item.max ?? item.den)
      const unit = String(item.unit ?? item.don_vi ?? '').trim()
      const period = String(item.period ?? item.ky ?? item.ky_luong ?? '').trim()
      if (!name && !legacy && min == null && max == null) return null
      return { name, min, max, unit, period, value: legacy }
    })
    .filter(Boolean)
}

export function hienMucLuong(item) {
  if (!item) return ''
  if (item.min != null || item.max != null) {
    const khoang =
      item.min != null && item.max != null && item.min !== item.max
        ? `${hienSoTien(item.min)}–${hienSoTien(item.max)}`
        : hienSoTien(item.min ?? item.max)
    const donVi = nhanDonViTien(item.unit)
    const tien = donVi ? `${khoang} ${donVi}` : khoang
    const ky = nhanKyLuong(item.period).toLocaleLowerCase('vi')
    return ky ? `${tien}/${ky}` : tien
  }
  return String(item.value || '').trim()
}

export function noiMucLuong(value, sep = '\n') {
  return danhSachMucLuong(value)
    .map((item) => {
      const luong = hienMucLuong(item)
      return item.name && luong ? `${item.name}: ${luong}` : item.name || luong
    })
    .filter(Boolean)
    .join(sep)
}

export function danhSachCap(value) {
  if (value == null || value === '') return []
  if (typeof value === 'string') {
    const text = value.trim()
    return text ? [{ name: '', value: text }] : []
  }
  if (!Array.isArray(value)) return []
  return value
    .map((item) => {
      if (item == null) return null
      if (typeof item !== 'object') {
        const text = String(item).trim()
        return text ? { name: '', value: text } : null
      }
      const name = String(item.name ?? item.ten ?? '').trim()
      const val = String(item.value ?? item.gia_tri ?? item.mo_ta ?? '').trim()
      const ghiChu = String(item.ghi_chu ?? '').trim()
      if (!name && !val && !ghiChu) return null
      return { name, value: val, ghi_chu: ghiChu }
    })
    .filter(Boolean)
}

export function noiCap(value, sep = '\n') {
  return danhSachCap(value)
    .map((item) => {
      const chinh = item.name && item.value ? `${item.name}: ${item.value}` : item.name || item.value
      if (item.ghi_chu && chinh) return `${chinh} (${item.ghi_chu})`
      return chinh || item.ghi_chu
    })
    .filter(Boolean)
    .join(sep)
}
