import api from '@/api/axios'

export function fetchTruSo(params) {
  return api.get('/tru-so', { params }).then((res) => res.data)
}

export function createTruSo(payload) {
  return api.post('/tru-so', payload).then((res) => res.data)
}

export function importTruSo(payload, config) {
  return api.post('/tru-so/import', payload, config).then((res) => res.data)
}

export function updateTruSo(id, payload) {
  return api.put(`/tru-so/${id}`, payload).then((res) => res.data)
}

export function deleteTruSo(id) {
  return api.delete(`/tru-so/${id}`)
}

export function deleteTruSoMany(ids) {
  return api.delete('/tru-so', { data: { ids } }).then((res) => res.data)
}
