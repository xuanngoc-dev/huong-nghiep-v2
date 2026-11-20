const NHOM_THEO_TU_KHOA = [
  ['hoc_phi', 'Học phí'],
  ['chi_tieu', 'Chỉ tiêu'],
  ['to_hop', 'Tổ hợp'],
  ['cong_thuc', 'Công thức'],
  ['diem', 'Điểm'],
  ['quy_doi', 'Điểm'],
  ['dieu_kien', 'Điều kiện'],
  ['doi_tuong', 'Điều kiện'],
  ['tieu_chi', 'Điều kiện'],
  ['phuong_thuc', 'Phương thức'],
  ['phuong_an', 'Phương thức'],
  ['co_so', 'Cơ sở'],
  ['tru_so', 'Cơ sở'],
  ['chuong_trinh', 'Chương trình'],
]

const THU_TU_NHOM = ['Thông tin chung', 'Cơ sở', 'Chương trình', 'Chỉ tiêu', 'Phương thức', 'Tổ hợp', 'Điều kiện', 'Công thức', 'Điểm', 'Học phí']
const NHAN_NHANH = { thong_tin_import: 'Thông tin nhập', dats_tuyen_sinh: 'Đề án', quy_tac_xet_tuyen: 'Quy tắc' }
const NHAN_KHOA = {
  'chi tieu': 'Chỉ tiêu', 'chi tieu tuyen sinh': 'Chỉ tiêu tuyển sinh', 'chi tieu phuong thuc': 'Chỉ tiêu phương thức',
  'ma xet tuyen': 'Mã xét tuyển', 'ten chuong trinh': 'Tên chương trình', 'ma nganh': 'Mã ngành',
  'diem chuan': 'Điểm chuẩn', 'diem san': 'Điểm sàn', 'thang diem': 'Thang điểm', 'ghi chu': 'Ghi chú',
  'ma cong thuc': 'Mã công thức', 'cong thuc tinh diem': 'Công thức tính điểm',
  'hoc phi': 'Học phí', 'hoc phi tu': 'Học phí từ', 'hoc phi den': 'Học phí đến',
  'co so': 'Cơ sở', 'ma co so': 'Mã cơ sở', 'to hop': 'Tổ hợp', 'nam tuyen sinh': 'Năm tuyển sinh',
  'chuong trinh dao tao': 'Chương trình đào tạo', 'phuong thuc': 'Phương thức',
}

export function tachDuongDan(duongDan) {
  return duongDan.slice(1).split('/').map((phan) => phan.replaceAll('~1', '/').replaceAll('~0', '~'))
}

export function giaTriTheoDuongDan(duLieu, duongDan) {
  return tachDuongDan(duongDan).reduce((giaTri, khoa) => {
    if (giaTri && typeof giaTri === 'object' && Object.hasOwn(giaTri, khoa)) return giaTri[khoa]
    return undefined
  }, duLieu)
}

function nhanKhoa(khoa) {
  if (Object.hasOwn(NHAN_NHANH, khoa)) return NHAN_NHANH[khoa]
  const tu = khoa.replace(/^dats_/, '').replaceAll('_', ' ')
  return Object.hasOwn(NHAN_KHOA, tu) ? NHAN_KHOA[tu] : `${tu.charAt(0).toUpperCase()}${tu.slice(1)}`
}

function thongTinMuc(muc, duLieu) {
  const cacPhan = tachDuongDan(muc.duong_dan)
  const cacKhoa = cacPhan.filter((phan) => !/^\d+$/.test(phan))
  const cacNhan = []
  let giaTri = duLieu
  for (const phan of cacPhan) {
    giaTri = giaTri && typeof giaTri === 'object' && Object.hasOwn(giaTri, phan) ? giaTri[phan] : undefined
    if (!/^\d+$/.test(phan)) {
      cacNhan.push(nhanKhoa(phan))
      continue
    }
    const ma = giaTri?.ma_xet_tuyen || giaTri?.ma_phuong_thuc_cua_truong || giaTri?.ma_cong_thuc || giaTri?.ma_co_so
    cacNhan.push(ma || `Mục ${Number(phan) + 1}`)
  }
  // Ưu tiên trường cụ thể, chẳng hạn chỉ tiêu của một chương trình thuộc nhóm Chỉ tiêu.
  const capCuoi = cacKhoa.at(-1) || ''
  const nhom = NHOM_THEO_TU_KHOA.find(([tu]) => capCuoi.includes(tu))?.[1]
    || NHOM_THEO_TU_KHOA.find(([tu]) => cacKhoa.slice(1).some((khoa) => khoa.includes(tu)))?.[1]
    || 'Thông tin chung'
  return { ...muc, giaTri, nhom, nhan: cacNhan.at(-1), viTri: cacNhan.slice(0, -1).join(' › ') }
}

export function lapDanhSachMuc(banNhap, banTruoc) {
  if (!banNhap) return []
  const mucCu = new Map((banTruoc?.muc || []).map((muc) => [muc.duong_dan, muc]))
  const danhSach = (banNhap.muc || []).map((muc) => {
    const item = thongTinMuc(muc, banNhap.du_lieu)
    const truoc = mucCu.get(muc.duong_dan)
    const giaTriTruoc = truoc && giaTriTheoDuongDan(banTruoc.du_lieu, muc.duong_dan)
    mucCu.delete(muc.duong_dan)
    return { ...item, giaTriTruoc, daThayDoi: Boolean(banTruoc) && (!truoc || !bangNhau(giaTriTruoc, item.giaTri) || truoc.ghi_chu !== muc.ghi_chu) }
  })
  for (const muc of mucCu.values()) {
    const item = thongTinMuc(muc, banTruoc.du_lieu)
    danhSach.push({ ...item, giaTriTruoc: item.giaTri, giaTri: undefined, daThayDoi: true, daBo: true })
  }
  return danhSach
}

export function nhomMuc(danhSach) {
  const dem = new Map()
  for (const muc of danhSach) dem.set(muc.nhom, (dem.get(muc.nhom) || 0) + 1)
  return THU_TU_NHOM.filter((nhom) => dem.has(nhom)).map((nhom) => ({ nhom, soLuong: dem.get(nhom) }))
}

export function bangNhau(a, b) {
  if (a === b) return true
  if (!a || !b || typeof a !== 'object' || typeof b !== 'object' || Array.isArray(a) !== Array.isArray(b)) return false
  const khoa = Object.keys(a)
  return khoa.length === Object.keys(b).length && khoa.every((key) => Object.hasOwn(b, key) && bangNhau(a[key], b[key]))
}

export function hienGiaTri(giaTri) {
  if (giaTri === undefined) return '—'
  return typeof giaTri === 'string' ? giaTri : JSON.stringify(giaTri, null, 2)
}

export function phanTichGiaTri(noiDung) {
  return JSON.parse(noiDung, (_, value) => {
    if (typeof value === 'number' && !Number.isFinite(value)) throw new RangeError('Giá trị số vượt phạm vi biểu diễn.')
    return value
  })
}
