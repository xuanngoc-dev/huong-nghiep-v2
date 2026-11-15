import api from '@/api/axios'

export function fetchHoSo(config = {}) {
  return api.get('/tai-khoan/ho-so', config).then((res) => res.data)
}

export function updateHoSo(payload) {
  return api.put('/tai-khoan/ho-so', payload).then((res) => res.data)
}

// Chỉ cập nhật thông tin cá nhân, giữ nguyên hồ sơ năng lực.
export function updateThongTinCaNhan(payload) {
  return api.put('/tai-khoan/thong-tin-ca-nhan', payload).then((res) => res.data)
}
