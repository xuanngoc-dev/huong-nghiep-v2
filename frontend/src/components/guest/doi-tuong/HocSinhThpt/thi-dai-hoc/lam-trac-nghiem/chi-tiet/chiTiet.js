const NHAN_MUC = {
  mo_ta: 'Mô tả',
  ky_nang_phu_hop: 'Kỹ năng phù hợp',
  mon_hoc_tieu_bieu: 'Môn học tiêu biểu',
  co_hoi_nghe_nghiep: 'Cơ hội nghề nghiệp',
  muc_luong: 'Mức lương tham khảo',
  muc_luong_tham_khao: 'Mức lương tham khảo',
  cong_cu: 'Công cụ thường dùng',
  do_phu_hop: 'Độ phù hợp',
  diem_can_nhac: 'Điểm cân nhắc',
  truong_dao_tao: 'Các trường đào tạo',
  thoi_gian_dao_tao: 'Thời gian đào tạo',
}

export function docChiTiet(item) {
  const text = String(item?.chi_tiet || '').trim()
  if (!text.startsWith('{')) return { vanBan: text, json: null }
  try {
    const data = JSON.parse(text)
    if (data && typeof data === 'object' && !Array.isArray(data)) return { vanBan: '', json: data }
  } catch {
    /* Giữ nguyên đoạn văn khi chi tiết không phải JSON. */
  }
  return { vanBan: text, json: null }
}

export function noiGiaTri(value) {
  if (Array.isArray(value)) {
    return value.map((item) => noiGiaTri(item)).filter(Boolean).join('\n')
  }
  if (value && typeof value === 'object') {
    return Object.entries(value)
      .map(([key, item]) => {
        const text = noiGiaTri(item)
        return text ? `${NHAN_MUC[key] || key}: ${text}` : ''
      })
      .filter(Boolean)
      .join('\n')
  }
  if (value == null) return ''
  return String(value).trim()
}

export function layChiTiet(json, keys) {
  if (!json) return null
  for (const key of keys) {
    if (noiGiaTri(json[key])) return json[key]
  }
  return null
}

export function tachDong(value) {
  if (Array.isArray(value)) return value.flatMap((item) => tachDong(item))
  const text = noiGiaTri(value)
  if (!text) return []
  const lines = text.split(/\n+/).map((item) => item.trim()).filter(Boolean)
  return lines.length ? lines : [text]
}

export function thanhBuoc(value) {
  const raw = Array.isArray(value)
    ? value
    : value && typeof value === 'object'
      ? Object.values(value)
      : tachDong(value)
  return raw
    .map((item, index) => {
      if (item && typeof item === 'object' && !Array.isArray(item)) {
        const tieuDe = String(item.tieu_de || item.ten || item.ten_buoc || item.chuc_danh || `Bước ${index + 1}`).trim()
        const noiDung = String(item.mo_ta || item.noi_dung || item.mo_ta_ngan || '').trim()
        const ghiChu = String(item.ghi_chu || '').trim()
        if (!tieuDe && !noiDung && !ghiChu) return null
        return { tieuDe: tieuDe || `Bước ${index + 1}`, noiDung, ghiChu }
      }
      const text = String(item ?? '').trim()
      return text ? { tieuDe: text, noiDung: '' } : null
    })
    .filter(Boolean)
}

export function thanhTruong(value) {
  const raw = Array.isArray(value)
    ? value
    : value && typeof value === 'object'
      ? Object.values(value)
      : tachDong(value)
  return raw
    .map((item) => {
      if (item && typeof item === 'object' && !Array.isArray(item)) {
        const ten = String(item.ten_truong || item.ten || item.tieu_de || '').trim()
        const phu = [item.dia_chi, item.website, item.mo_ta].map((phan) => String(phan || '').trim()).filter(Boolean)
        if (!ten && !phu.length) {
          const text = noiGiaTri(item)
          return text ? { ten: text, phu: '' } : null
        }
        return { ten: ten || phu.shift() || '', phu: phu.join(' · ') }
      }
      const text = String(item ?? '').trim()
      return text ? { ten: text, phu: '' } : null
    })
    .filter((item) => item?.ten)
}
