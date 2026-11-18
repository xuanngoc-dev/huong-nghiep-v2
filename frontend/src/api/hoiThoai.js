import api from '@/api/axios'

export function fetchPhienHoiThoai(params, config = {}) {
  return api.get('/hoi-thoai/phien', { ...config, params }).then((res) => res.data)
}

export function doiTrangThaiPhienHoiThoai(id, trangThai) {
  return api.patch(`/hoi-thoai/phien/${id}/trang-thai`, { trang_thai: trangThai }).then((res) => res.data)
}

export function deletePhienHoiThoai(id) {
  return api.delete(`/hoi-thoai/phien/${id}`)
}

// Thành viên: hội thoại của chính mình.
export function fetchHoiThoaiCuaToi(params, config = {}) {
  return api.get('/hoi-thoai/cua-toi', { ...config, params }).then((res) => res.data)
}

export function fetchChiTietHoiThoaiCuaToi(maPhien, config = {}) {
  return api.get(`/hoi-thoai/cua-toi/${encodeURIComponent(maPhien)}`, config).then((res) => res.data)
}

export function fetchChiTietPhienHoiThoai(id, config = {}) {
  return api.get(`/hoi-thoai/phien/${id}`, config).then((res) => res.data)
}
