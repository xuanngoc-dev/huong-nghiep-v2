import api from '@/api/axios'

export function fetchLoaiCauHoi(params) {
  return api.get('/danh-muc/loai-cau-hoi', { params }).then((res) => res.data)
}

export function createLoaiCauHoi(payload) {
  return api.post('/danh-muc/loai-cau-hoi', payload).then((res) => res.data)
}

export function createLoaiCauHoiBulk(payload) {
  return api.post('/danh-muc/loai-cau-hoi/bulk', payload).then((res) => res.data)
}

export function updateLoaiCauHoi(id, payload) {
  return api.put(`/danh-muc/loai-cau-hoi/${id}`, payload).then((res) => res.data)
}

export function deleteLoaiCauHoi(id) {
  return api.delete(`/danh-muc/loai-cau-hoi/${id}`)
}

export function deleteLoaiCauHoiMany(ids) {
  return api.delete('/danh-muc/loai-cau-hoi', { data: { ids } }).then((res) => res.data)
}
