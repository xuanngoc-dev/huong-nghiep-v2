import api from '@/api/axios'

export function fetchNhomNganh(params) {
  return api.get('/danh-muc/nhom-nganh-dao-tao', { params }).then((res) => res.data)
}

export function createNhomNganh(payload) {
  return api.post('/danh-muc/nhom-nganh-dao-tao', payload).then((res) => res.data)
}

export function createNhomNganhBulk(payload) {
  return api.post('/danh-muc/nhom-nganh-dao-tao/bulk', payload).then((res) => res.data)
}

export function updateNhomNganh(id, payload) {
  return api.put(`/danh-muc/nhom-nganh-dao-tao/${id}`, payload).then((res) => res.data)
}

export function deleteNhomNganh(id) {
  return api.delete(`/danh-muc/nhom-nganh-dao-tao/${id}`)
}

export function deleteNhomNganhMany(ids) {
  return api.delete('/danh-muc/nhom-nganh-dao-tao', { data: { ids } }).then((res) => res.data)
}
