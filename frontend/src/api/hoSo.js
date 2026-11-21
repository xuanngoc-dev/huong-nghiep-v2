import api from '@/api/axios'

export function fetchHoSo(config = {}) {
  return api.get('/tai-khoan/ho-so', config).then((res) => res.data)
}

export function updateHoSo(payload) {
  return api.put('/tai-khoan/ho-so', payload).then((res) => res.data)
}

// Chỉ cập nhật thông tin cá nhân, giữ nguyên hồ sơ năng lực.
// Lượt dùng chức năng theo ngày của tài khoản đang đăng nhập (trang tổng quan thành viên).
export function fetchThongKeSuDung(params = {}, config = {}) {
  return api.get('/tai-khoan/thong-ke-su-dung', { ...config, params }).then((res) => res.data)
}

// Đổi mật khẩu đăng nhập của tài khoản đang đăng nhập.
export function doiMatKhau(payload) {
  return api.post('/tai-khoan/doi-mat-khau', payload).then((res) => res.data)
}

export function updateThongTinCaNhan(payload) {
  return api.put('/tai-khoan/thong-tin-ca-nhan', payload).then((res) => res.data)
}

// Chỉ đổi đối tượng của tài khoản (nguoi_dung.doi_tuong), dùng khi chọn "Bạn là" trong khung chat.
export function capNhatDoiTuong(doiTuong) {
  return api.patch('/tai-khoan/doi-tuong', { doi_tuong: doiTuong || null }, { skipLoading: true }).then((res) => res.data)
}
