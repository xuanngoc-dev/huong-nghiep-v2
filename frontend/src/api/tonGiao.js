import api from '@/api/axios'

export function fetchTonGiao(params) {
  return api.get('/danh-muc/ton-giao', { params }).then((res) => res.data)
}

export function createTonGiao(payload) {
  return api.post('/danh-muc/ton-giao', payload).then((res) => res.data)
}

export function createTonGiaoBulk(payload) {
  return api.post('/danh-muc/ton-giao/bulk', payload).then((res) => res.data)
}

export function updateTonGiao(id, payload) {
  return api.put(`/danh-muc/ton-giao/${id}`, payload).then((res) => res.data)
}

export function deleteTonGiao(id) {
  return api.delete(`/danh-muc/ton-giao/${id}`)
}

export function deleteTonGiaoMany(ids) {
  return api.delete('/danh-muc/ton-giao', { data: { ids } }).then((res) => res.data)
}
