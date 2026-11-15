import api from '@/api/axios'

export function fetchCauHinhGoiCuoc(params) {
  return api.get('/he-thong/cau-hinh-goi-cuoc', { params }).then((res) => res.data)
}

export function updateTrangThaiCauHinhGoiCuoc(id, trangThai) {
  return api
    .patch(`/he-thong/cau-hinh-goi-cuoc/${id}/trang-thai`, { trang_thai: trangThai }, { skipLoading: true })
    .then((res) => res.data)
}

export function createCauHinhGoiCuoc(payload) {
  return api.post('/he-thong/cau-hinh-goi-cuoc', payload).then((res) => res.data)
}

export function updateCauHinhGoiCuoc(id, payload) {
  return api.put(`/he-thong/cau-hinh-goi-cuoc/${id}`, payload).then((res) => res.data)
}

export function deleteCauHinhGoiCuoc(id) {
  return api.delete(`/he-thong/cau-hinh-goi-cuoc/${id}`)
}

export function deleteCauHinhGoiCuocMany(ids) {
  return api.delete('/he-thong/cau-hinh-goi-cuoc', { data: { ids } }).then((res) => res.data)
}

// Gói đang bán cho thành viên ở trang nạp tiền.
export function fetchGoiCuocDangBan(params) {
  return api.get('/he-thong/cau-hinh-goi-cuoc/dang-ban', { params, skipLoading: true }).then((res) => res.data)
}
