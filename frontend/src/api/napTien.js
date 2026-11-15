import api from '@/api/axios'

// ---------- Thành viên ----------

export function fetchNapTienCuaToi(params) {
  return api.get('/tai-khoan/nap-tien', { params }).then((res) => res.data)
}

// Đăng ký gói: tạo (hoặc dùng lại) giao dịch chờ thanh toán.
export function taoNapTien(payload) {
  return api.post('/tai-khoan/nap-tien', payload).then((res) => res.data)
}

// Đổi ngân hàng chuyển khoản hoặc báo đã chuyển khoản.
export function capNhatNapTien(id, payload, config = {}) {
  return api.patch(`/tai-khoan/nap-tien/${id}`, payload, config).then((res) => res.data)
}

export function huyNapTien(id) {
  return api.post(`/tai-khoan/nap-tien/${id}/huy`).then((res) => res.data)
}

// ---------- Admin ----------

export function fetchLichSuNapTien(params) {
  return api.get('/he-thong/lich-su-nap-tien', { params }).then((res) => res.data)
}

export function xacNhanNapTien(id, payload) {
  return api.post(`/he-thong/lich-su-nap-tien/${id}/xac-nhan`, payload).then((res) => res.data)
}

export function tuChoiNapTien(id, payload) {
  return api.post(`/he-thong/lich-su-nap-tien/${id}/tu-choi`, payload).then((res) => res.data)
}

export function fetchGiaoDichNganHang(params) {
  return api.get('/he-thong/giao-dich-ngan-hang', { params }).then((res) => res.data)
}
