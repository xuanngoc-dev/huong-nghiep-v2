import api from '@/api/axios'

export function fetchPhuongThucTuyenSinh(params) {
  return api.get('/danh-muc/phuong-thuc-tuyen-sinh', { params }).then((res) => res.data)
}

export function createPhuongThucTuyenSinh(payload) {
  return api.post('/danh-muc/phuong-thuc-tuyen-sinh', payload).then((res) => res.data)
}

export function createPhuongThucTuyenSinhBulk(payload) {
  return api.post('/danh-muc/phuong-thuc-tuyen-sinh/bulk', payload).then((res) => res.data)
}

export function updatePhuongThucTuyenSinh(id, payload) {
  return api.put(`/danh-muc/phuong-thuc-tuyen-sinh/${id}`, payload).then((res) => res.data)
}

export function deletePhuongThucTuyenSinh(id) {
  return api.delete(`/danh-muc/phuong-thuc-tuyen-sinh/${id}`)
}

export function deletePhuongThucTuyenSinhMany(ids) {
  return api.delete('/danh-muc/phuong-thuc-tuyen-sinh', { data: { ids } }).then((res) => res.data)
}
