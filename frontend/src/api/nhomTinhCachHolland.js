import api from '@/api/axios'

export function fetchNhomHolland(params, config = {}) {
  return api.get('/danh-muc/nhom-tinh-cach-holland', { ...config, params }).then((res) => res.data)
}

export function createNhomHolland(payload) {
  return api.post('/danh-muc/nhom-tinh-cach-holland', payload).then((res) => res.data)
}

export function createNhomHollandBulk(payload, config) {
  return api.post('/danh-muc/nhom-tinh-cach-holland/bulk', payload, config).then((res) => res.data)
}

export function updateNhomHolland(id, payload) {
  return api.put(`/danh-muc/nhom-tinh-cach-holland/${id}`, payload).then((res) => res.data)
}

export function updateTrangThaiNhomHolland(id, trangThai) {
  return api
    .patch(`/danh-muc/nhom-tinh-cach-holland/${id}/trang-thai`, { trang_thai: trangThai })
    .then((res) => res.data)
}

export function updateTrangThaiNhomHollandMany(ids, trangThai) {
  return api
    .patch('/danh-muc/nhom-tinh-cach-holland/trang-thai', { ids, trang_thai: trangThai })
    .then((res) => res.data)
}

export function deleteNhomHolland(id) {
  return api.delete(`/danh-muc/nhom-tinh-cach-holland/${id}`)
}

export function deleteNhomHollandMany(ids) {
  return api.delete('/danh-muc/nhom-tinh-cach-holland', { data: { ids } }).then((res) => res.data)
}
