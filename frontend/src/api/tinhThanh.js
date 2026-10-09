import api from '@/api/axios'

export function fetchTinhThanh(params) {
  return api.get('/danh-muc/tinh-thanh', { params }).then((res) => res.data)
}

export function createTinhThanh(payload) {
  return api.post('/danh-muc/tinh-thanh', payload).then((res) => res.data)
}

export function createTinhThanhBulk(payload) {
  return api.post('/danh-muc/tinh-thanh/bulk', payload).then((res) => res.data)
}

export function updateTinhThanh(id, payload) {
  return api.put(`/danh-muc/tinh-thanh/${id}`, payload).then((res) => res.data)
}

export function deleteTinhThanh(id) {
  return api.delete(`/danh-muc/tinh-thanh/${id}`)
}

export function deleteTinhThanhMany(ids) {
  return api.delete('/danh-muc/tinh-thanh', { data: { ids } }).then((res) => res.data)
}
