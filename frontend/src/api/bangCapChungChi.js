import api from '@/api/axios'

export function fetchBangCapChungChi(params) {
  return api.get('/danh-muc/bang-cap-chung-chi', { params }).then((res) => res.data)
}

export function createBangCapChungChi(payload) {
  return api.post('/danh-muc/bang-cap-chung-chi', payload).then((res) => res.data)
}

export function createBangCapChungChiBulk(payload, config) {
  return api.post('/danh-muc/bang-cap-chung-chi/bulk', payload, config).then((res) => res.data)
}

export function updateBangCapChungChi(id, payload) {
  return api.put(`/danh-muc/bang-cap-chung-chi/${id}`, payload).then((res) => res.data)
}

export function deleteBangCapChungChi(id) {
  return api.delete(`/danh-muc/bang-cap-chung-chi/${id}`)
}

export function deleteBangCapChungChiMany(ids) {
  return api.delete('/danh-muc/bang-cap-chung-chi', { data: { ids } }).then((res) => res.data)
}
