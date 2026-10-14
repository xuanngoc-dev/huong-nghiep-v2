import api from '@/api/axios'

export function fetchThanhTichHocTapNghienCuu(params) {
  return api.get('/danh-muc/thanh-tich-hoc-tap-nghien-cuu', { params }).then((res) => res.data)
}

export function createThanhTichHocTapNghienCuu(payload) {
  return api.post('/danh-muc/thanh-tich-hoc-tap-nghien-cuu', payload).then((res) => res.data)
}

export function createThanhTichHocTapNghienCuuBulk(payload, config) {
  return api.post('/danh-muc/thanh-tich-hoc-tap-nghien-cuu/bulk', payload, config).then((res) => res.data)
}

export function updateThanhTichHocTapNghienCuu(id, payload) {
  return api.put(`/danh-muc/thanh-tich-hoc-tap-nghien-cuu/${id}`, payload).then((res) => res.data)
}

export function deleteThanhTichHocTapNghienCuu(id) {
  return api.delete(`/danh-muc/thanh-tich-hoc-tap-nghien-cuu/${id}`)
}

export function deleteThanhTichHocTapNghienCuuMany(ids) {
  return api.delete('/danh-muc/thanh-tich-hoc-tap-nghien-cuu', { data: { ids } }).then((res) => res.data)
}
