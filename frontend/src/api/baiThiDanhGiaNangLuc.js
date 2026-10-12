import api from '@/api/axios'

export function fetchBaiThiDanhGiaNangLuc(params) {
  return api.get('/danh-muc/bai-thi-danh-gia-nang-luc', { params }).then((res) => res.data)
}

export function createBaiThiDanhGiaNangLuc(payload) {
  return api.post('/danh-muc/bai-thi-danh-gia-nang-luc', payload).then((res) => res.data)
}

export function createBaiThiDanhGiaNangLucBulk(payload) {
  return api.post('/danh-muc/bai-thi-danh-gia-nang-luc/bulk', payload).then((res) => res.data)
}

export function updateBaiThiDanhGiaNangLuc(id, payload) {
  return api.put(`/danh-muc/bai-thi-danh-gia-nang-luc/${id}`, payload).then((res) => res.data)
}

export function deleteBaiThiDanhGiaNangLuc(id) {
  return api.delete(`/danh-muc/bai-thi-danh-gia-nang-luc/${id}`)
}

export function deleteBaiThiDanhGiaNangLucMany(ids) {
  return api.delete('/danh-muc/bai-thi-danh-gia-nang-luc', { data: { ids } }).then((res) => res.data)
}
