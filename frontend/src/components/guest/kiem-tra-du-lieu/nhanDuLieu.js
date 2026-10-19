const NHAN = {
  ma_truong: 'Mã trường',
  ten_truong: 'Tên trường',
  loai_hinh: 'Loại hình',
  nam_tuyen_sinh: 'Năm tuyển sinh',
  dieu_kien_chung: 'Điều kiện chung',
  ma_nganh: 'Mã ngành',
  ma_xet_tuyen: 'Mã xét tuyển',
  ten_nganh: 'Tên ngành',
  ten_chuong_trinh: 'Tên chương trình',
  chi_tieu_nganh: 'Chỉ tiêu ngành',
  dieu_kien_nganh: 'Điều kiện ngành',
  phuong_thuc_tuyen_sinh: 'Phương thức tuyển sinh',
  ma_phuong_thuc: 'Mã phương thức',
  ten_phuong_thuc: 'Tên phương thức',
  loai_phuong_thuc: 'Loại phương thức',
  nhom_phuong_thuc_truong: 'Nhóm phương thức',
  dien_xet_tuyen: 'Diện xét tuyển',
  chi_tieu_phuong_thuc: 'Chỉ tiêu phương thức',
  diem_chuan: 'Điểm chuẩn',
  diem_san: 'Điểm sàn',
  thang_diem: 'Thang điểm',
  ghi_chu: 'Ghi chú',
  dieu_kien_phu: 'Điều kiện phụ',
  to_hop_mon: 'Tổ hợp môn',
  cong_thuc_tinh_diem: 'Công thức tính điểm',
  quy_doi_diem: 'Điểm quy đổi',
  diem_cong_uu_tien: 'Điểm ưu tiên, khuyến khích',
  tieu_chi_dong_diem: 'Tiêu chí đồng điểm',
  ma_to_hap: 'Mã tổ hợp',
  ten_to_hap: 'Tên tổ hợp',
  chi_tieu_to_hap: 'Chỉ tiêu tổ hợp',
  danh_sach_mon: 'Danh sách môn',
  he_so_mon: 'Hệ số môn',
  loai: 'Loại',
  gia_tri: 'Giá trị',
  toan_tu: 'Toán tử',
  nguon_diem: 'Nguồn điểm',
  ap_dung_khi: 'Áp dụng khi',
  logic: 'Logic',
  lop: 'Lớp',
  hoc_ky: 'Học kỳ',
  mon: 'Môn',
  cong_thuc: 'Công thức',
  quy_tac: 'Quy tắc',
  nguyen_tac: 'Nguyên tắc',
  diem_thuong: 'Điểm thưởng',
  diem_xet_thuong: 'Điểm xét thưởng',
  diem_khuyen_khich: 'Điểm khuyến khích',
  uu_tien_khu_vuc: 'Ưu tiên khu vực',
  uu_tien_doi_tuong: 'Ưu tiên đối tượng',
  bang_diem_thuong: 'Bảng điểm thưởng',
  bang_quy_doi: 'Bảng quy đổi',
  chung_chi: 'Chứng chỉ',
  chung_chi_ngoai_ngu: 'Chứng chỉ ngoại ngữ',
}

const MON = {
  TOAN: 'Toán',
  VAN: 'Ngữ văn',
  NGU_VAN: 'Ngữ văn',
  VAT_LY: 'Vật lý',
  HOA_HOC: 'Hóa học',
  SINH_HOC: 'Sinh học',
  LICH_SU: 'Lịch sử',
  DIA_LY: 'Địa lý',
  GDCD: 'GDCD',
  TIENG_ANH: 'Tiếng Anh',
  TIN_HOC: 'Tin học',
  CONG_NGHE: 'Công nghệ',
  KTPL: 'KTPL',
}

export const KHOA_PHUONG_THUC_META = [
  'ma_phuong_thuc',
  'ten_phuong_thuc',
  'loai_phuong_thuc',
  'nhom_phuong_thuc_truong',
  'dien_xet_tuyen',
  'chi_tieu_phuong_thuc',
  'diem_chuan',
  'diem_san',
  'thang_diem',
]

export const KHOA_PHUONG_THUC_KHOI = [
  ['cong_thuc_tinh_diem', 'Công thức tính điểm'],
  ['to_hop_mon', 'Tổ hợp môn'],
  ['dieu_kien_phu', 'Điều kiện phụ'],
  ['quy_doi_diem', 'Điểm quy đổi'],
  ['diem_cong_uu_tien', 'Điểm ưu tiên, khuyến khích'],
  ['tieu_chi_dong_diem', 'Tiêu chí đồng điểm'],
]

export const KHOA_NGANH_META = ['ma_nganh', 'ma_xet_tuyen', 'ten_nganh', 'ten_chuong_trinh', 'chi_tieu_nganh']

const MUC_SO_SANH = [
  'cong_thuc_tinh_diem',
  'quy_doi_diem',
  'diem_cong_uu_tien',
  'dieu_kien_phu',
  'to_hop_mon',
  'tieu_chi_dong_diem',
  'ghi_chu',
  'thang_diem',
  'diem_san',
  'diem_chuan',
  'chi_tieu_phuong_thuc',
]

export function nhan(key) {
  if (NHAN[key]) return NHAN[key]
  return String(key ?? '').replaceAll('_', ' ')
}

export function coGiaTri(value) {
  if (value == null) return false
  if (typeof value === 'string') return value.trim() !== ''
  if (Array.isArray(value)) return value.length > 0
  if (typeof value === 'object') return Object.keys(value).length > 0
  return true
}

export function chuanHoa(value) {
  return String(value ?? '')
    .normalize('NFD')
    .replace(/\p{M}/gu, '')
    .replace(/đ/g, 'd')
    .replace(/Đ/g, 'D')
    .toLowerCase()
}

export function khop(query, ...parts) {
  const needle = chuanHoa(query).trim()
  if (!needle) return true
  return chuanHoa(parts.filter((part) => part != null).join(' ')).includes(needle)
}

export function tenNganh(nganh) {
  return nganh?.ten_chuong_trinh || nganh?.ten_nganh || 'Ngành chưa đặt tên'
}

export function maNganh(nganh) {
  const maXet = nganh?.ma_xet_tuyen
  const ma = nganh?.ma_nganh
  if (maXet && ma && String(maXet) !== String(ma)) return `${maXet} · ${ma}`
  return maXet || ma || ''
}

export function nhanTruong(item) {
  const ma = item.ma_truong ? ` (${item.ma_truong})` : ''
  const nam = item.nam_tuyen_sinh ? ` · ${item.nam_tuyen_sinh}` : ''
  return `${item.ten_truong}${ma}${nam} · ${item.so_nganh} ngành · ${item.ten_tep}`
}

export function nhomPhuongThuc(nganhs) {
  const map = new Map()
  nganhs.forEach((nganh, nganhIndex) => {
    const methods = Array.isArray(nganh?.phuong_thuc_tuyen_sinh) ? nganh.phuong_thuc_tuyen_sinh : []
    methods.forEach((phuongThuc, phuongThucIndex) => {
      if (!phuongThuc || typeof phuongThuc !== 'object' || Array.isArray(phuongThuc)) return
      const key = [phuongThuc.ma_phuong_thuc, phuongThuc.ten_phuong_thuc, phuongThuc.loai_phuong_thuc]
        .map((part) => part ?? '')
        .join('\u0000')
      if (!map.has(key)) {
        map.set(key, {
          key,
          ma: phuongThuc.ma_phuong_thuc ?? '',
          ten: phuongThuc.ten_phuong_thuc || 'Phương thức chưa đặt tên',
          loai: phuongThuc.loai_phuong_thuc || '',
          apDung: [],
        })
      }
      map.get(key).apDung.push({
        khoa: `${nganhIndex}:${phuongThucIndex}`,
        nganh,
        phuongThuc,
      })
    })
  })
  return [...map.values()].sort(
    (a, b) => String(a.ma).localeCompare(String(b.ma), 'vi') || String(a.ten).localeCompare(String(b.ten), 'vi'),
  )
}

export function khoiTrungNhau(nganhs, field) {
  const map = new Map()
  for (const nganh of nganhs) {
    const methods = Array.isArray(nganh?.phuong_thuc_tuyen_sinh) ? nganh.phuong_thuc_tuyen_sinh : []
    for (const phuongThuc of methods) {
      if (!phuongThuc || typeof phuongThuc !== 'object') continue
      const value = phuongThuc[field]
      if (!coGiaTri(value)) continue
      const key = JSON.stringify(value)
      if (!map.has(key)) map.set(key, { value, apDung: [] })
      map.get(key).apDung.push({
        nganh: tenNganh(nganh),
        ma: maNganh(nganh),
        phuongThuc: phuongThuc.ten_phuong_thuc || phuongThuc.ma_phuong_thuc || 'Phương thức',
        maPhuongThuc: phuongThuc.ma_phuong_thuc || '',
      })
    }
  }
  return [...map.values()]
}

export function mucKhacNhau(apDung) {
  if (apDung.length < 2) return []
  return MUC_SO_SANH.filter((key) => {
    const first = JSON.stringify(apDung[0].phuongThuc?.[key] ?? null)
    return apDung.some((item) => JSON.stringify(item.phuongThuc?.[key] ?? null) !== first)
  }).map((key) => nhan(key))
}

export function tenMon(value) {
  if (Array.isArray(value)) return value.map((item) => tenMon(item)).filter(Boolean).join(', ')
  if (value && typeof value === 'object') return value.ten || value.ma || JSON.stringify(value)
  if (value == null || value === '') return ''
  const code = String(value)
  return MON[code] || code.replaceAll('_', ' ')
}

export function heSoMon(value) {
  if (!coGiaTri(value)) return ''
  if (Array.isArray(value)) return value.map((item) => heSoMon(item)).filter(Boolean).join(', ')
  if (value && typeof value === 'object') {
    return Object.entries(value)
      .map(([mon, heSo]) => `${tenMon(mon)} × ${heSo}`)
      .join(', ')
  }
  return String(value)
}

export function khoaConLai(record, known) {
  if (!record || typeof record !== 'object') return {}
  const skip = new Set(known)
  return Object.fromEntries(Object.entries(record).filter(([key]) => !skip.has(key)))
}
