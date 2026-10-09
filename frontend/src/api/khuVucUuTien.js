import api from '@/api/axios'

export function fetchKhuVucUuTien(params) {
  return api.get('/danh-muc/khu-vuc-uu-tien', { params }).then((res) => res.data)
}

export function createKhuVucUuTien(payload) {
  return api.post('/danh-muc/khu-vuc-uu-tien', payload).then((res) => res.data)
}

export function createKhuVucUuTienBulk(payload) {
  return api.post('/danh-muc/khu-vuc-uu-tien/bulk', payload).then((res) => res.data)
}

export function updateKhuVucUuTien(id, payload) {
  return api.put(`/danh-muc/khu-vuc-uu-tien/${id}`, payload).then((res) => res.data)
}

export function deleteKhuVucUuTien(id) {
  return api.delete(`/danh-muc/khu-vuc-uu-tien/${id}`)
}

export function deleteKhuVucUuTienMany(ids) {
  return api.delete('/danh-muc/khu-vuc-uu-tien', { data: { ids } }).then((res) => res.data)
}
