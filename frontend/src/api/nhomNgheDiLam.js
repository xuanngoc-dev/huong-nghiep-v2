import api from '@/api/axios'

// Nhóm nghề đi làm
const NHOM = '/danh-muc/nhom-nghe-di-lam'

export function fetchNhomNgheDiLam(params, config = {}) {
  return api.get(NHOM, { ...config, params }).then((res) => res.data)
}

export function createNhomNgheDiLam(payload) {
  return api.post(NHOM, payload).then((res) => res.data)
}

export function createNhomNgheDiLamBulk(payload, config) {
  return api.post(`${NHOM}/bulk`, payload, config).then((res) => res.data)
}

export function updateNhomNgheDiLam(id, payload) {
  return api.put(`${NHOM}/${id}`, payload).then((res) => res.data)
}

export function updateTrangThaiNhomNgheDiLam(id, trangThai) {
  return api.patch(`${NHOM}/${id}/trang-thai`, { trang_thai: trangThai }).then((res) => res.data)
}

export function updateTrangThaiNhomNgheDiLamMany(ids, trangThai) {
  return api.patch(`${NHOM}/trang-thai`, { ids, trang_thai: trangThai }).then((res) => res.data)
}

export function deleteNhomNgheDiLam(id) {
  return api.delete(`${NHOM}/${id}`)
}

export function deleteNhomNgheDiLamMany(ids) {
  return api.delete(NHOM, { data: { ids } }).then((res) => res.data)
}

// Nghề cụ thể
const NGHE = '/danh-muc/nghe-cu-the-di-lam'

export function fetchNgheCuTheDiLam(params) {
  return api.get(NGHE, { params }).then((res) => res.data)
}

export function createNgheCuTheDiLam(payload) {
  return api.post(NGHE, payload).then((res) => res.data)
}

export function createNgheCuTheDiLamBulk(payload, config) {
  return api.post(`${NGHE}/bulk`, payload, config).then((res) => res.data)
}

export function updateNgheCuTheDiLam(id, payload) {
  return api.put(`${NGHE}/${id}`, payload).then((res) => res.data)
}

export function deleteNgheCuTheDiLam(id) {
  return api.delete(`${NGHE}/${id}`)
}

export function deleteNgheCuTheDiLamMany(ids) {
  return api.delete(NGHE, { data: { ids } }).then((res) => res.data)
}

// Tiêu chí gợi ý
const TIEU_CHI = '/danh-muc/tieu-chi-goi-y'

export function fetchTieuChiGoiY(params) {
  return api.get(TIEU_CHI, { params }).then((res) => res.data)
}

export function fetchNhomTieuChi() {
  return api.get(`${TIEU_CHI}/nhom`).then((res) => res.data)
}

export function createTieuChiGoiY(payload) {
  return api.post(TIEU_CHI, payload).then((res) => res.data)
}

export function createTieuChiGoiYBulk(payload, config) {
  return api.post(`${TIEU_CHI}/bulk`, payload, config).then((res) => res.data)
}

export function updateTieuChiGoiY(id, payload) {
  return api.put(`${TIEU_CHI}/${id}`, payload).then((res) => res.data)
}

export function deleteTieuChiGoiY(id) {
  return api.delete(`${TIEU_CHI}/${id}`)
}

export function deleteTieuChiGoiYMany(ids) {
  return api.delete(TIEU_CHI, { data: { ids } }).then((res) => res.data)
}

// Nhóm nghề - tiêu chí (khóa ghép nhom_nghe_di_lam_id + tieu_chi_goi_y_id)
const LIEN_KET = '/danh-muc/nhom-nghe-tieu-chi'

export function fetchNhomNgheTieuChi(params) {
  return api.get(LIEN_KET, { params }).then((res) => res.data)
}

export function createNhomNgheTieuChi(payload) {
  return api.post(LIEN_KET, payload).then((res) => res.data)
}

export function createNhomNgheTieuChiBulk(payload, config) {
  return api.post(`${LIEN_KET}/bulk`, payload, config).then((res) => res.data)
}

export function updateNhomNgheTieuChi(nhomId, tieuChiId, payload) {
  return api.put(`${LIEN_KET}/${nhomId}/${tieuChiId}`, payload).then((res) => res.data)
}

export function deleteNhomNgheTieuChi(nhomId, tieuChiId) {
  return api.delete(`${LIEN_KET}/${nhomId}/${tieuChiId}`)
}

// items: [{ nhom_nghe_di_lam_id, tieu_chi_goi_y_id }]
export function deleteNhomNgheTieuChiMany(items) {
  return api.delete(LIEN_KET, { data: { items } }).then((res) => res.data)
}
