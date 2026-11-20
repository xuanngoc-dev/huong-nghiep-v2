export const TUY_CHON_TRANG_THAI = [
  { giaTri: 'thu_thap', nhan: 'Đang thu thập', loai: 'info' },
  { giaTri: 'cho_duyet', nhan: 'Chờ duyệt', loai: 'warning' },
  { giaTri: 'yeu_cau_bo_sung', nhan: 'Yêu cầu bổ sung', loai: 'danger' },
  { giaTri: 'da_duyet_va_nhap', nhan: 'Đã duyệt và nhập', loai: 'success' },
]

export const TRANG_THU_THAP = 'de-an-tuyen-sinh-thu-thap-du-lieu'
export const TRANG_XET_DUYET = 'de-an-tuyen-sinh-xet-duyet-du-lieu'

const TINH_TRANG_NGUON = {
  chua_tim_nguon: { nhan: 'Chưa tìm nguồn', loai: 'info' },
  chua_co_nguon_phu_hop: { nhan: 'Chưa có nguồn phù hợp', loai: 'warning' },
  cho_chon_nguon: { nhan: 'Đã tìm nguồn · Chờ chọn', loai: 'warning' },
  san_sang_tao_nhap: { nhan: 'Sẵn sàng tạo bản nháp', loai: 'success' },
}

export function trangThaiPhien(giaTri, dangTaoBanNhap = false) {
  if (dangTaoBanNhap) return { nhan: 'Đang tạo bản nháp', loai: 'warning' }
  return TUY_CHON_TRANG_THAI.find((item) => item.giaTri === giaTri) || { nhan: giaTri || '—', loai: 'info' }
}

export function loiTaoBanNhapDaLuu(phien) {
  return ['thu_thap', 'yeu_cau_bo_sung'].includes(phien?.trang_thai) ? phien.loi_tao_ban_nhap : null
}

export function nguonBiBoQuaKhiTaoBanNhap(phien) {
  const phienBan = phien?.ban_nhap?.phien_ban
  if (!phienBan) return {}
  const lanTao = phien.lich_su?.find((muc) => muc.hanh_dong === 'tao_ban_nhap' && muc.phien_ban <= phienBan)
  return lanTao?.chi_tiet?.loi_nguon || {}
}

export function trangThaiThuThap(phien, dangTaoBanNhap = phien.dang_tao_ban_nhap, hienTinhTrangNguon = true) {
  if (!dangTaoBanNhap && loiTaoBanNhapDaLuu(phien)) return { nhan: 'Tạo bản nháp thất bại', loai: 'danger' }
  return hienTinhTrangNguon && !dangTaoBanNhap && phien.trang_thai === 'thu_thap' && Object.hasOwn(TINH_TRANG_NGUON, phien.tinh_trang_nguon)
    ? TINH_TRANG_NGUON[phien.tinh_trang_nguon]
    : trangThaiPhien(phien.trang_thai, dangTaoBanNhap)
}

export function ngayGio(giaTri) {
  if (!giaTri) return '—'
  const ngay = new Date(giaTri)
  return Number.isNaN(ngay.getTime()) ? giaTri : ngay.toLocaleString('vi-VN')
}

export function ngayVanBan(giaTri) {
  if (!giaTri) return '—'
  const namThangNgay = /^(\d{4})-(\d{2})-(\d{2})$/.exec(giaTri)
  return namThangNgay ? `${namThangNgay[3]}/${namThangNgay[2]}/${namThangNgay[1]}` : giaTri
}

export function urlTaiLieu(giaTri, viTri) {
  try {
    const url = new URL(giaTri)
    if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password) return null
    const trang = /\b(?:trang|page)\s*(?:pdf\s*)?#?\s*([1-9]\d*)(?!\d)/i.exec(viTri || '')
    if (trang && /\.pdf$/i.test(url.pathname)) url.hash = `page=${trang[1]}`
    return url.href
  } catch {
    return null
  }
}

export function lienKetDanChung(danChung, nguon) {
  const trangNguon = urlTaiLieu(nguon?.url)
  const tepKemTheo = urlTaiLieu(danChung.url_tai_lieu)
  const taiLieuRieng = tepKemTheo && tepKemTheo.split('#')[0] !== trangNguon?.split('#')[0]
  const viTri = danChung.vi_tri || ''
  const nhanTep = /^bảng ảnh\s/i.test(viTri) ? 'Mở ảnh dẫn chứng' : 'Mở tài liệu dẫn chứng'
  return {
    url: urlTaiLieu(tepKemTheo || trangNguon, viTri),
    nhan: taiLieuRieng ? nhanTep : nguon?.url,
    trangNguon: taiLieuRieng ? trangNguon : null,
  }
}

export function chiTietLoiPhien(detail) {
  if (typeof detail === 'string') return { noiDung: detail, loi: [] }
  return {
    noiDung: detail?.message || (Array.isArray(detail) ? 'Dữ liệu gửi lên không hợp lệ.' : 'Không thể hoàn tất thao tác. Vui lòng thử lại.'),
    loi: Array.isArray(detail?.loi) ? detail.loi : [],
    deAnId: detail?.de_an_id,
    nguonIds: Array.isArray(detail?.nguon_ids) ? detail.nguon_ids : [],
    dangTaoBanNhap: detail?.dang_tao_ban_nhap === true,
  }
}

export function loiPhien(error) {
  let duLieu = error.response?.data
  if (typeof duLieu === 'string') {
    try {
      duLieu = JSON.parse(duLieu)
    } catch {
      duLieu = null
    }
  }
  return {
    ...chiTietLoiPhien(duLieu?.detail),
    trangThai: error.response?.status,
  }
}
