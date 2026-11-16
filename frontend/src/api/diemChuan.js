import api from '@/api/axios'

export function fetchDiemChuan(params) {
  return api.get('/diem-chuan', { params }).then((res) => res.data)
}

export function createDiemChuan(payload) {
  return api.post('/diem-chuan', payload).then((res) => res.data)
}

export function createDiemChuanBulk(payload, config) {
  return api.post('/diem-chuan/bulk', payload, config).then((res) => res.data)
}

export function updateDiemChuan(id, payload) {
  return api.put(`/diem-chuan/${id}`, payload).then((res) => res.data)
}

export function deleteDiemChuan(id) {
  return api.delete(`/diem-chuan/${id}`)
}

export function deleteDiemChuanMany(ids) {
  return api.delete('/diem-chuan', { data: { ids } }).then((res) => res.data)
}
