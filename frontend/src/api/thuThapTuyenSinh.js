import api from '@/api/axios'

const goc = '/de-an-tuyen-sinh/thu-thap'
const phien = (id) => `${goc}/phien/${id}`
const taiNen = { skipLoading: true }
const xuLyAi = { ...taiNen, timeout: 360000 }

export const nhanDienTruong = (ma_truong) =>
  api.get(`${goc}/truong`, { ...taiNen, params: { ma_truong } }).then((res) => res.data)

export const taoPhienTuyenSinh = (duLieu, tuDong = false) =>
  api.post(`${goc}/phien`, duLieu, { ...taiNen, params: { tu_dong: tuDong } }).then((res) => res.data)

export const layDanhSachPhien = (params) =>
  api.get(`${goc}/phien`, { ...taiNen, params }).then((res) => res.data)

export const layPhienTuyenSinh = (id, phien_ban) =>
  api.get(phien(id), { ...taiNen, params: { phien_ban } }).then((res) => res.data)

export const xoaPhienTuyenSinh = (id) =>
  api.delete(phien(id), taiNen).then((res) => res.data)

export const timNguonTuyenSinh = (id) =>
  api.post(`${phien(id)}/tim-nguon`, {}, xuLyAi).then((res) => res.data)

export const themNguonTuyenSinh = (id, url) =>
  api.post(`${phien(id)}/nguon`, { url }, xuLyAi).then((res) => res.data)

export const chonNguonTuyenSinh = (id, nguonId, lua_chon, ly_do) =>
  api.patch(`${phien(id)}/nguon/${nguonId}`, { lua_chon, ly_do }, taiNen).then((res) => res.data)

export const chonTatCaNguonTuyenSinh = (id) =>
  api.patch(`${phien(id)}/nguon`, { lua_chon: 'su_dung' }, taiNen).then((res) => res.data)

export const taoBanNhapTuyenSinh = (id, tuDong = false) =>
  api.post(`${phien(id)}/tao-ban-nhap`, {}, { ...taiNen, params: { tu_dong: tuDong } }).then((res) => res.data)

export const dungTaoBanNhapTuyenSinh = (id, luot_tao_ban_nhap) =>
  api.post(`${phien(id)}/dung-tao-ban-nhap`, { luot_tao_ban_nhap }, taiNen).then((res) => res.data)

export const suaBanNhapTuyenSinh = (id, phien_ban, thay_doi, xac_nhan_doi_chieu) =>
  api.patch(`${phien(id)}/ban-nhap`, { phien_ban, thay_doi, xac_nhan_doi_chieu }, taiNen).then((res) => res.data)

export const yeuCauBoSungTuyenSinh = (id, phien_ban, duong_dan, ly_do) =>
  api.post(`${phien(id)}/yeu-cau-bo-sung`, { phien_ban, duong_dan, ly_do }, taiNen).then((res) => res.data)

export const duyetBanNhapTuyenSinh = (id, phien_ban) =>
  api.post(`${phien(id)}/duyet`, { phien_ban }, { ...taiNen, timeout: 60000 }).then((res) => res.data)

export const duyetNhieuPhienTuyenSinh = (phien) =>
  api.post(`${goc}/phien/duyet-hang-loat`, { phien }, { ...taiNen, timeout: 590000 }).then((res) => res.data)

export const layJsonTuyenSinhDaDuyet = (id) =>
  api.get(`${phien(id)}/json`, { ...taiNen, responseType: 'text' }).then((res) => res.data)
