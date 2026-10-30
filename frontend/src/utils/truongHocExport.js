export const TRUONG_HOC_EXPORT_COLUMNS = [
  { header: 'STT', key: 'stt', width: 8 },
  { header: 'Mã trường', key: 'ma_truong', width: 14 },
  { header: 'Tên trường', key: 'ten_truong', width: 42 },
  { header: 'Tên tiếng Anh', key: 'ten_tieng_anh', width: 42 },
  { header: 'Tên viết tắt', key: 'ten_viet_tat', width: 16 },
  { header: 'Tên gọi khác', key: 'ten_goi_khac', width: 28 },
  { header: 'Slug', key: 'slug', width: 24 },
  { header: 'Loại cơ sở', key: 'loai_co_so', width: 18 },
  { header: 'Loại hình', key: 'loai_hinh', width: 22 },
  { header: 'Cơ quan chủ quản', key: 'co_quan_chu_quan', width: 28 },
  { header: 'Trường trực thuộc', key: 'truong_cha_id', width: 18 },
  { header: 'Ngày thành lập', key: 'ngay_thanh_lap', width: 16 },
  { header: 'Năm thành lập', key: 'nam_thanh_lap', width: 16 },
  { header: 'Giới thiệu ngắn', key: 'gioi_thieu_ngan', width: 36 },
  { header: 'Giới thiệu chi tiết', key: 'gioi_thieu_chi_tiet', width: 40 },
  { header: 'Thế mạnh', key: 'the_manh', width: 32 },
  { header: 'Bậc đào tạo', key: 'bac_dao_tao', width: 24 },
  { header: 'Lĩnh vực đào tạo chính', key: 'linh_vuc_dao_tao_chinh', width: 28 },
  { header: 'Lĩnh vực đào tạo khác', key: 'linh_vuc_dao_tao_khac', width: 28 },
  { header: 'Mã tỉnh/thành', key: 'ma_tinh_thanh', width: 16 },
  { header: 'Tỉnh/thành', key: 'ten_tinh_thanh', width: 18 },
  { header: 'Mã phường/xã', key: 'ma_phuong_xa', width: 16 },
  { header: 'Phường/xã', key: 'ten_phuong_xa', width: 18 },
  { header: 'Địa chỉ trụ sở', key: 'dia_chi_tru_so', width: 40 },
  { header: 'Vùng miền', key: 'vung_mien', width: 14 },
  { header: 'Vĩ độ', key: 'vi_do', width: 14 },
  { header: 'Kinh độ', key: 'kinh_do', width: 14 },
  { header: 'Số điện thoại', key: 'so_dien_thoai', width: 18 },
  { header: 'Email', key: 'email', width: 28 },
  { header: 'Website', key: 'website', width: 28 },
  { header: 'Website tuyển sinh', key: 'website_tuyen_sinh', width: 28 },
  { header: 'Hotline tuyển sinh', key: 'hotline_tuyen_sinh', width: 18 },
  { header: 'Email tuyển sinh', key: 'email_tuyen_sinh', width: 28 },
  { header: 'Logo', key: 'logo_url', width: 28 },
  { header: 'Ảnh đại diện', key: 'anh_dai_dien_url', width: 28 },
  { header: 'Diện tích (m²)', key: 'dien_tich_m2', width: 16 },
  { header: 'Học phí trung bình', key: 'hoc_phi_trung_binh', width: 22 },
  { header: 'Trạng thái', key: 'trang_thai_hoat_dong', width: 18 },
  { header: 'Nguồn dữ liệu', key: 'nguon_du_lieu_url', width: 28 },
  { header: 'Ngày xác minh', key: 'ngay_xac_minh', width: 20 },
  { header: 'Ghi chú', key: 'ghi_chu', width: 32 },
  { header: 'Tạo lúc', key: 'tao_luc', width: 20 },
  { header: 'Cập nhật lúc', key: 'cap_nhat_luc', width: 20 },
]

function text(value) {
  if (value == null) return ''
  if (Array.isArray(value)) return value.join(', ')
  return value
}

export function truongHocListParams(filters, paging = {}) {
  const params = {}
  if (paging.page != null) params.page = paging.page
  if (paging.pageSize != null) params.page_size = paging.pageSize
  const q = String(filters?.q ?? '').trim()
  const vungMien = String(filters?.vung_mien ?? '').trim()
  if (q) params.q = q
  if (vungMien) params.vung_mien = vungMien
  if (filters?.loai_hinh) params.loai_hinh = filters.loai_hinh
  if (filters?.loai_co_so) params.loai_co_so = filters.loai_co_so
  const status = String(filters?.trang_thai_hoat_dong ?? '').trim()
  if (status) params.trang_thai_hoat_dong = status
  return params
}

export function truongHocExportRows(items) {
  return items.map((row, index) => {
    const exported = { stt: index + 1 }
    for (const column of TRUONG_HOC_EXPORT_COLUMNS) {
      if (column.key === 'stt') continue
      exported[column.key] = text(row[column.key])
    }
    return exported
  })
}

export function truongHocExportFilename(date = new Date()) {
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `truong-dai-hoc-${date.getFullYear()}-${month}-${day}.xlsx`
}
