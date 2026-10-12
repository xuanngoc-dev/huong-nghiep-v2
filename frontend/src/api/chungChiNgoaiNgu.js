import api from '@/api/axios'

export function fetchChungChiNgoaiNgu(params) {
  return api.get('/danh-muc/chung-chi-ngoai-ngu', { params }).then((res) => res.data)
}

export function createChungChiNgoaiNgu(payload) {
  return api.post('/danh-muc/chung-chi-ngoai-ngu', payload).then((res) => res.data)
}

export function createChungChiNgoaiNguBulk(payload) {
  return api.post('/danh-muc/chung-chi-ngoai-ngu/bulk', payload).then((res) => res.data)
}

export function updateChungChiNgoaiNgu(id, payload) {
  return api.put(`/danh-muc/chung-chi-ngoai-ngu/${id}`, payload).then((res) => res.data)
}

export function deleteChungChiNgoaiNgu(id) {
  return api.delete(`/danh-muc/chung-chi-ngoai-ngu/${id}`)
}

export function deleteChungChiNgoaiNguMany(ids) {
  return api.delete('/danh-muc/chung-chi-ngoai-ngu', { data: { ids } }).then((res) => res.data)
}
