import api from '@/api/axios'

export function fetchNhomHolland(params) {
  return api.get('/danh-muc/nhom-tinh-cach-holland', { params }).then((res) => res.data)
}

export function createNhomHolland(payload) {
  return api.post('/danh-muc/nhom-tinh-cach-holland', payload).then((res) => res.data)
}

export function createNhomHollandBulk(payload) {
  return api.post('/danh-muc/nhom-tinh-cach-holland/bulk', payload).then((res) => res.data)
}

export function updateNhomHolland(id, payload) {
  return api.put(`/danh-muc/nhom-tinh-cach-holland/${id}`, payload).then((res) => res.data)
}

export function deleteNhomHolland(id) {
  return api.delete(`/danh-muc/nhom-tinh-cach-holland/${id}`)
}

export function deleteNhomHollandMany(ids) {
  return api.delete('/danh-muc/nhom-tinh-cach-holland', { data: { ids } }).then((res) => res.data)
}
