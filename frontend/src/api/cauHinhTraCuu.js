import api from '@/api/axios'

export function fetchCauHinhTraCuu(params) {
  return api.get('/he-thong/cau-hinh-tra-cuu', { params }).then((res) => res.data)
}

export function updateTrangThaiCauHinhTraCuu(id, trangThai) {
  return api
    .patch(`/he-thong/cau-hinh-tra-cuu/${id}/trang-thai`, { trang_thai: trangThai }, { skipLoading: true })
    .then((res) => res.data)
}

export function createCauHinhTraCuu(payload) {
  return api.post('/he-thong/cau-hinh-tra-cuu', payload).then((res) => res.data)
}

export function updateCauHinhTraCuu(id, payload) {
  return api.put(`/he-thong/cau-hinh-tra-cuu/${id}`, payload).then((res) => res.data)
}

export function deleteCauHinhTraCuu(id) {
  return api.delete(`/he-thong/cau-hinh-tra-cuu/${id}`)
}

export function deleteCauHinhTraCuuMany(ids) {
  return api.delete('/he-thong/cau-hinh-tra-cuu', { data: { ids } }).then((res) => res.data)
}
