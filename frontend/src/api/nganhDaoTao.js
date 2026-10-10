import api from '@/api/axios'

export function fetchNganh(params) {
  return api.get('/danh-muc/nganh-dao-tao', { params }).then((res) => res.data)
}

export function createNganh(payload) {
  return api.post('/danh-muc/nganh-dao-tao', payload).then((res) => res.data)
}

export function createNganhBulk(payload) {
  return api.post('/danh-muc/nganh-dao-tao/bulk', payload).then((res) => res.data)
}

export function updateNganh(id, payload) {
  return api.put(`/danh-muc/nganh-dao-tao/${id}`, payload).then((res) => res.data)
}

export function deleteNganh(id) {
  return api.delete(`/danh-muc/nganh-dao-tao/${id}`)
}

export function deleteNganhMany(ids) {
  return api.delete('/danh-muc/nganh-dao-tao', { data: { ids } }).then((res) => res.data)
}
