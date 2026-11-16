import api from '@/api/axios'

// Hồ sơ xét tuyển (bảng hs_*) của thành viên; tham chiếu danh mục bằng mã.
export function fetchHoSoXetTuyen(config = {}) {
  return api.get('/ho-so-xet-tuyen/cua-toi', config).then((res) => res.data)
}

export function luuHoSoXetTuyen(payload) {
  return api.put('/ho-so-xet-tuyen/cua-toi', payload).then((res) => res.data)
}
