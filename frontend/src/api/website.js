import api from '@/api/axios'

export function fetchWebsite(params) {
  return api.get('/website', { params }).then((res) => res.data)
}

export function createWebsite(payload) {
  return api.post('/website', payload).then((res) => res.data)
}

export function importWebsite(payload, config) {
  return api.post('/website/import', payload, config).then((res) => res.data)
}

export function updateWebsite(id, payload) {
  return api.put(`/website/${id}`, payload).then((res) => res.data)
}

export function deleteWebsite(id) {
  return api.delete(`/website/${id}`)
}

export function deleteWebsiteMany(ids) {
  return api.delete('/website', { data: { ids } }).then((res) => res.data)
}
