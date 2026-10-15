export const TRUONG_HOC_EXPORT_COLUMNS = [
  { header: 'STT', key: 'stt', width: 8 },
  { header: 'Mã trường', key: 'ma_truong', width: 14 },
  { header: 'Tên viết tắt', key: 'ten_viet_tat', width: 16 },
  { header: 'Tên trường', key: 'ten_truong', width: 42 },
  { header: 'Tên tiếng Anh', key: 'ten_tieng_anh', width: 42 },
  { header: 'Khu vực', key: 'khu_vuc', width: 18 },
  { header: 'Địa chỉ', key: 'dia_chi', width: 40 },
  { header: 'Loại hình đào tạo', key: 'loai_hinh_dao_tao', width: 20 },
  { header: 'Nhóm ngành', key: 'nhom_nganh', width: 24 },
  { header: 'Website', key: 'website', width: 28 },
  { header: 'Email', key: 'email', width: 28 },
  { header: 'Số điện thoại', key: 'so_dien_thoai', width: 18 },
  { header: 'Học phí trung bình', key: 'hoc_phi_trung_binh', width: 22 },
  { header: 'Năm thành lập', key: 'nam_thanh_lap', width: 16 },
  { header: 'Trạng thái', key: 'trang_thai', width: 14 },
  { header: 'Giới thiệu', key: 'gioi_thieu', width: 40 },
]

function text(value) {
  if (value == null) return ''
  return value
}

export function truongHocListParams(filters, paging = {}) {
  const params = {}
  if (paging.page != null) params.page = paging.page
  if (paging.pageSize != null) params.page_size = paging.pageSize
  const q = String(filters?.q ?? '').trim()
  const khuVuc = String(filters?.khu_vuc ?? '').trim()
  if (q) params.q = q
  if (khuVuc) params.khu_vuc = khuVuc
  if (filters?.loai_hinh_dao_tao) params.loai_hinh_dao_tao = filters.loai_hinh_dao_tao
  const status = filters?.trang_thai
  if (status !== '' && status != null) params.trang_thai = status
  return params
}

export function truongHocExportRows(items) {
  return items.map((row, index) => ({
    stt: index + 1,
    ma_truong: text(row.ma_truong),
    ten_viet_tat: text(row.ten_viet_tat),
    ten_truong: text(row.ten_truong),
    ten_tieng_anh: text(row.ten_tieng_anh),
    khu_vuc: text(row.khu_vuc),
    dia_chi: text(row.dia_chi),
    loai_hinh_dao_tao: text(row.loai_hinh_dao_tao),
    nhom_nganh: text(row.nhom_nganh),
    website: text(row.website),
    email: text(row.email),
    so_dien_thoai: text(row.so_dien_thoai),
    hoc_phi_trung_binh: text(row.hoc_phi_trung_binh),
    nam_thanh_lap: row.nam_thanh_lap ?? null,
    trang_thai: row.trang_thai === 1 ? 'Hoạt động' : 'Khóa',
    gioi_thieu: text(row.gioi_thieu),
  }))
}

export function truongHocExportFilename(date = new Date()) {
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `truong-dai-hoc-${date.getFullYear()}-${month}-${day}.xlsx`
}
