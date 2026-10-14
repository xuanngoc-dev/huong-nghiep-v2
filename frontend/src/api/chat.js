import api from '@/api/axios'

const quiet = { skipLoading: true }

export function layDanhSachModel() {
  return api.get('/chat/model', quiet).then((res) => res.data)
}

export function hoiChat(payload) {
  return api.post('/chat/hoi', payload, { ...quiet, timeout: 90000 }).then((res) => res.data)
}

export function layTaiLieu() {
  return api.get('/tai-lieu', quiet).then((res) => res.data)
}

export function taiTaiLieu(tep) {
  const form = new FormData()
  form.append('tep', tep)
  return api.post('/tai-lieu', form, quiet).then((res) => res.data)
}

export function xoaTaiLieu(ten) {
  return api.delete(`/tai-lieu/${encodeURIComponent(ten)}`, quiet)
}
