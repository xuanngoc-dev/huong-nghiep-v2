import api from '@/api/axios'

export function fetchCauHinhEnduser(params) {
  return api.get('/he-thong/cau-hinh-enduser', { params }).then((res) => res.data)
}

export function updateTrangThaiCauHinhEnduser(id, trangThai) {
  return api
    .patch(`/he-thong/cau-hinh-enduser/${id}/trang-thai`, { trang_thai: trangThai }, { skipLoading: true })
    .then((res) => res.data)
}

export function createCauHinhEnduser(payload) {
  return api.post('/he-thong/cau-hinh-enduser', payload).then((res) => res.data)
}

export function updateCauHinhEnduser(id, payload) {
  return api.put(`/he-thong/cau-hinh-enduser/${id}`, payload).then((res) => res.data)
}

export function deleteCauHinhEnduser(id) {
  return api.delete(`/he-thong/cau-hinh-enduser/${id}`)
}

export function deleteCauHinhEnduserMany(ids) {
  return api.delete('/he-thong/cau-hinh-enduser', { data: { ids } }).then((res) => res.data)
}

export function fetchCauHinhEnduserDangApDung() {
  return api.get('/he-thong/cau-hinh-enduser/dang-ap-dung', { skipLoading: true }).then((res) => res.data)
}
