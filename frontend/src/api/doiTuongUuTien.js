import api from '@/api/axios'

export function fetchDoiTuongUuTien(params) {
  return api.get('/danh-muc/doi-tuong-uu-tien', { params }).then((res) => res.data)
}

export function createDoiTuongUuTien(payload) {
  return api.post('/danh-muc/doi-tuong-uu-tien', payload).then((res) => res.data)
}

export function createDoiTuongUuTienBulk(payload) {
  return api.post('/danh-muc/doi-tuong-uu-tien/bulk', payload).then((res) => res.data)
}

export function updateDoiTuongUuTien(id, payload) {
  return api.put(`/danh-muc/doi-tuong-uu-tien/${id}`, payload).then((res) => res.data)
}

export function deleteDoiTuongUuTien(id) {
  return api.delete(`/danh-muc/doi-tuong-uu-tien/${id}`)
}

export function deleteDoiTuongUuTienMany(ids) {
  return api.delete('/danh-muc/doi-tuong-uu-tien', { data: { ids } }).then((res) => res.data)
}
