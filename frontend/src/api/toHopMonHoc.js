import api from '@/api/axios'

export function fetchToHopMonHoc(params) {
  return api.get('/danh-muc/to-hop-mon-hoc', { params }).then((res) => res.data)
}

export function createToHopMonHoc(payload) {
  return api.post('/danh-muc/to-hop-mon-hoc', payload).then((res) => res.data)
}

export function createToHopMonHocBulk(payload) {
  return api.post('/danh-muc/to-hop-mon-hoc/bulk', payload).then((res) => res.data)
}

export function updateToHopMonHoc(id, payload) {
  return api.put(`/danh-muc/to-hop-mon-hoc/${id}`, payload).then((res) => res.data)
}

export function deleteToHopMonHoc(id) {
  return api.delete(`/danh-muc/to-hop-mon-hoc/${id}`)
}

export function deleteToHopMonHocMany(ids) {
  return api.delete('/danh-muc/to-hop-mon-hoc', { data: { ids } }).then((res) => res.data)
}
