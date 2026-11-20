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

// Kiểm tra giao dịch đang chờ đã có tiền về chưa; khớp thì backend xác nhận và cộng số dư.
export function kiemTraThanhToan(id, config = {}) {
  return api.post(`/tai-khoan/nap-tien/${id}/kiem-tra-thanh-toan`, null, config).then((res) => res.data)
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

// Thống kê tài chính cho dashboard: doanh thu theo kỳ, 30 ngày, 12 tháng, theo loại, giao dịch chờ.
export function fetchThongKeNapTien() {
  return api.get('/he-thong/lich-su-nap-tien/thong-ke').then((res) => res.data)
}
