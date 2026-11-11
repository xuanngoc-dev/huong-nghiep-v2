import api from '@/api/axios'

export function fetchNguoiDung(params) {
  return api.get('/he-thong/nguoi-dung', { params }).then((res) => res.data)
}

export function createNguoiDung(payload) {
  return api.post('/he-thong/nguoi-dung', payload).then((res) => res.data)
}

export function updateNguoiDung(id, payload) {
  return api.put(`/he-thong/nguoi-dung/${id}`, payload).then((res) => res.data)
}

export function deleteNguoiDung(id) {
  return api.delete(`/he-thong/nguoi-dung/${id}`)
}

export function deleteNguoiDungMany(ids) {
  return api.delete('/he-thong/nguoi-dung', { data: { ids } }).then((res) => res.data)
}
