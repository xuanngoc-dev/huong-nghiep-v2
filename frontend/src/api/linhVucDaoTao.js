import api from '@/api/axios'

export function fetchLinhVuc(params) {
  return api.get('/danh-muc/linh-vuc-dao-tao', { params }).then((res) => res.data)
}

export function createLinhVuc(payload) {
  return api.post('/danh-muc/linh-vuc-dao-tao', payload).then((res) => res.data)
}

export function createLinhVucBulk(payload) {
  return api.post('/danh-muc/linh-vuc-dao-tao/bulk', payload).then((res) => res.data)
}

export function updateLinhVuc(id, payload) {
  return api.put(`/danh-muc/linh-vuc-dao-tao/${id}`, payload).then((res) => res.data)
}

export function deleteLinhVuc(id) {
  return api.delete(`/danh-muc/linh-vuc-dao-tao/${id}`)
}

export function deleteLinhVucMany(ids) {
  return api.delete('/danh-muc/linh-vuc-dao-tao', { data: { ids } }).then((res) => res.data)
}
