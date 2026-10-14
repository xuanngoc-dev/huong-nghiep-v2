import api from '@/api/axios'

export function fetchTruongHoc(params) {
  return api.get('/danh-muc/truong-hoc', { params }).then((res) => res.data)
}

export function createTruongHoc(payload) {
  return api.post('/danh-muc/truong-hoc', payload).then((res) => res.data)
}

export function createTruongHocBulk(payload, config) {
  return api.post('/danh-muc/truong-hoc/bulk', payload, config).then((res) => res.data)
}

export function updateTruongHoc(id, payload) {
  return api.put(`/danh-muc/truong-hoc/${id}`, payload).then((res) => res.data)
}

export function deleteTruongHoc(id) {
  return api.delete(`/danh-muc/truong-hoc/${id}`)
}

export function deleteTruongHocMany(ids) {
  return api.delete('/danh-muc/truong-hoc', { data: { ids } }).then((res) => res.data)
}
