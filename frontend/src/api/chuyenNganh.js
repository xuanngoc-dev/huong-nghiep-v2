import api from '@/api/axios'

export function fetchChuyenNganh(params) {
  return api.get('/danh-muc/chuyen-nganh', { params }).then((res) => res.data)
}

export function createChuyenNganh(payload) {
  return api.post('/danh-muc/chuyen-nganh', payload).then((res) => res.data)
}

export function createChuyenNganhBulk(payload) {
  return api.post('/danh-muc/chuyen-nganh/bulk', payload).then((res) => res.data)
}

export function updateChuyenNganh(id, payload) {
  return api.put(`/danh-muc/chuyen-nganh/${id}`, payload).then((res) => res.data)
}

export function deleteChuyenNganh(id) {
  return api.delete(`/danh-muc/chuyen-nganh/${id}`)
}

export function deleteChuyenNganhMany(ids) {
  return api.delete('/danh-muc/chuyen-nganh', { data: { ids } }).then((res) => res.data)
}
