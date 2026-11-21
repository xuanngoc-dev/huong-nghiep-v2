import { fetchTruongHoc } from '@/api/truongHoc'
import { fetchNganh } from '@/api/nganhDaoTao'
import { fetchPhuongThucTuyenSinh } from '@/api/phuongThucTuyenSinh'
import { fetchToHopMonHoc } from '@/api/toHopMonHoc'
import { fetchBaiThiDanhGiaNangLuc } from '@/api/baiThiDanhGiaNangLuc'
import { fetchBangCapChungChi } from '@/api/bangCapChungChi'
import { timLoaiTraCuu } from './loaiTraCuu'

// API danh sách (không cần đăng nhập) theo id loại tra cứu trong loaiTraCuu.js.
const API_THEO_LOAI = {
  truong: fetchTruongHoc,
  nganh: fetchNganh,
  'phuong-thuc': fetchPhuongThucTuyenSinh,
  'to-hop': fetchToHopMonHoc,
  'bai-thi': fetchBaiThiDanhGiaNangLuc,
  'chung-chi': fetchBangCapChungChi,
}

/** Gọi API danh sách của loại tra cứu; trả về {items, total, page, page_size}. */
export function traCuuDanhMuc(loaiId, { q, page = 1, pageSize = 12, loc = {} } = {}) {
  const loai = timLoaiTraCuu(loaiId)
  const params = { ...loai.params, ...loc, page, page_size: pageSize }
  if (q) params.q = q
  return API_THEO_LOAI[loai.id](params)
}
