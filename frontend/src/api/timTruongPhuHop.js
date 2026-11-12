import api from '@/api/axios'

export function fetchLuotTimTruong(params = {}) {
  return api.get('/tim-truong-phu-hop/luot', { params, skipLoading: true }).then((res) => res.data)
}

export function timTruongPhuHop(payload) {
  return api.post('/tim-truong-phu-hop', payload, { skipLoading: true }).then((res) => res.data)
}

export function fetchLichSuTimTruongQuanTri(params) {
  return api.get('/tim-truong-phu-hop/quan-tri', { params }).then((res) => res.data)
}

export function fetchChiTietLichSuTimTruong(id) {
  return api.get(`/tim-truong-phu-hop/quan-tri/${id}`).then((res) => res.data)
}

export function fetchTruongPhuHop(params, config = {}) {
  return api.get('/tim-truong-phu-hop/truong', { ...config, params }).then((res) => res.data)
}

export function fetchLichSuTimTruongCuaToi(params) {
  return api.get('/tim-truong-phu-hop/cua-toi', { params }).then((res) => res.data)
}

export function fetchChiTietLichSuTimTruongCuaToi(id) {
  return api.get(`/tim-truong-phu-hop/cua-toi/${id}`).then((res) => res.data)
}
