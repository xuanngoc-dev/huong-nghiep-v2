import api from '@/api/axios'

export function fetchNganHangThanhToan(params) {
  return api.get('/he-thong/ngan-hang-thanh-toan', { params }).then((res) => res.data)
}

export function fetchLuaChonNganHang() {
  return api.get('/he-thong/ngan-hang-thanh-toan/lua-chon').then((res) => res.data)
}

export function updateTrangThaiNganHangThanhToan(id, trangThai) {
  return api
    .patch(`/he-thong/ngan-hang-thanh-toan/${id}/trang-thai`, { trang_thai: trangThai }, { skipLoading: true })
    .then((res) => res.data)
}

export function createNganHangThanhToan(payload) {
  return api.post('/he-thong/ngan-hang-thanh-toan', payload).then((res) => res.data)
}

export function updateNganHangThanhToan(id, payload) {
  return api.put(`/he-thong/ngan-hang-thanh-toan/${id}`, payload).then((res) => res.data)
}

export function deleteNganHangThanhToan(id) {
  return api.delete(`/he-thong/ngan-hang-thanh-toan/${id}`)
}

export function deleteNganHangThanhToanMany(ids) {
  return api.delete('/he-thong/ngan-hang-thanh-toan', { data: { ids } }).then((res) => res.data)
}

export function fetchNganHangNhanTien() {
  return api.get('/he-thong/ngan-hang-thanh-toan/dang-hoat-dong', { skipLoading: true }).then((res) => res.data)
}
