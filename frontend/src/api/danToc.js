import api from '@/api/axios'

export function fetchDanToc(params) {
  return api.get('/danh-muc/dan-toc', { params }).then((res) => res.data)
}

export function createDanToc(payload) {
  return api.post('/danh-muc/dan-toc', payload).then((res) => res.data)
}

export function createDanTocBulk(payload) {
  return api.post('/danh-muc/dan-toc/bulk', payload).then((res) => res.data)
}

export function updateDanToc(id, payload) {
  return api.put(`/danh-muc/dan-toc/${id}`, payload).then((res) => res.data)
}

export function deleteDanToc(id) {
  return api.delete(`/danh-muc/dan-toc/${id}`)
}

export function deleteDanTocMany(ids) {
  return api.delete('/danh-muc/dan-toc', { data: { ids } }).then((res) => res.data)
}
