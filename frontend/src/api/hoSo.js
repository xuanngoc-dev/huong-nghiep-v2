import api from '@/api/axios'

export function fetchHoSo() {
  return api.get('/tai-khoan/ho-so').then((res) => res.data)
}

export function updateHoSo(payload) {
  return api.put('/tai-khoan/ho-so', payload).then((res) => res.data)
}
