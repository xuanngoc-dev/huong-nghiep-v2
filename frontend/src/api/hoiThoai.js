import api from '@/api/axios'

export function fetchPhienHoiThoai(params, config = {}) {
  return api.get('/hoi-thoai/phien', { ...config, params }).then((res) => res.data)
}

export function fetchChiTietPhienHoiThoai(id, config = {}) {
  return api.get(`/hoi-thoai/phien/${id}`, config).then((res) => res.data)
}
