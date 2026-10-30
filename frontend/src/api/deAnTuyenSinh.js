import api from '@/api/axios'

export function fetchDeAnTuyenSinh(params) {
  return api.get('/de-an-tuyen-sinh', { params }).then((res) => res.data)
}

export function createDeAnTuyenSinh(payload) {
  return api.post('/de-an-tuyen-sinh', payload).then((res) => res.data)
}

export function createDeAnTuyenSinhBulk(payload, config) {
  return api.post('/de-an-tuyen-sinh/bulk', payload, config).then((res) => res.data)
}

export function updateDeAnTuyenSinh(id, payload) {
  return api.put(`/de-an-tuyen-sinh/${id}`, payload).then((res) => res.data)
}

export function deleteDeAnTuyenSinh(id) {
  return api.delete(`/de-an-tuyen-sinh/${id}`)
}

export function deleteDeAnTuyenSinhMany(ids) {
  return api.delete('/de-an-tuyen-sinh', { data: { ids } }).then((res) => res.data)
}
