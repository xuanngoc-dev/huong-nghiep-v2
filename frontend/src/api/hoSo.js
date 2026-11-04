import api from '@/api/axios'

export function fetchHoSo(config = {}) {
  return api.get('/tai-khoan/ho-so', config).then((res) => res.data)
}

export function updateHoSo(payload) {
  return api.put('/tai-khoan/ho-so', payload).then((res) => res.data)
}
