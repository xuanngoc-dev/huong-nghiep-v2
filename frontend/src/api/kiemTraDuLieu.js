import api from '@/api/axios'

const tuyChon = { timeout: 120000, skipLoading: true }

export function danhSachTruong() {
  return api.get('/kiem-tra-du-lieu/truong', tuyChon).then((res) => res.data)
}

export function noiDungTruong(tenTep) {
  return api
    .get('/kiem-tra-du-lieu/noi-dung', { ...tuyChon, params: { ten_tep: tenTep } })
    .then((res) => res.data)
}
