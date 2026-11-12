import api from '@/api/axios'

export function fetchLuotTimTruong() {
  return api.get('/tim-truong-phu-hop/luot', { skipLoading: true }).then((res) => res.data)
}

export function timTruongPhuHop(payload) {
  return api.post('/tim-truong-phu-hop', payload, { skipLoading: true }).then((res) => res.data)
}
