import api from '@/api/axios'

export function fetchMonHoc(params) {
  return api.get('/danh-muc/mon-hoc', { params }).then((res) => res.data)
}

export function createMonHoc(payload) {
  return api.post('/danh-muc/mon-hoc', payload).then((res) => res.data)
}

export function createMonHocBulk(payload) {
  return api.post('/danh-muc/mon-hoc/bulk', payload).then((res) => res.data)
}

export function updateMonHoc(id, payload) {
  return api.put(`/danh-muc/mon-hoc/${id}`, payload).then((res) => res.data)
}

export function deleteMonHoc(id) {
  return api.delete(`/danh-muc/mon-hoc/${id}`)
}

export function deleteMonHocMany(ids) {
  return api.delete('/danh-muc/mon-hoc', { data: { ids } }).then((res) => res.data)
}
