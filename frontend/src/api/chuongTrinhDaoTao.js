import api from '@/api/axios'

export function fetchChuongTrinhDaoTao(params) {
  return api.get('/chuong-trinh-dao-tao', { params }).then((res) => res.data)
}

export function createChuongTrinhDaoTao(payload) {
  return api.post('/chuong-trinh-dao-tao', payload).then((res) => res.data)
}

export function importChuongTrinhDaoTao(payload, config) {
  return api.post('/chuong-trinh-dao-tao/import', payload, config).then((res) => res.data)
}

export function updateChuongTrinhDaoTao(id, payload) {
  return api.put(`/chuong-trinh-dao-tao/${id}`, payload).then((res) => res.data)
}

export function deleteChuongTrinhDaoTao(id) {
  return api.delete(`/chuong-trinh-dao-tao/${id}`)
}

export function deleteChuongTrinhDaoTaoMany(ids) {
  return api.delete('/chuong-trinh-dao-tao', { data: { ids } }).then((res) => res.data)
}
