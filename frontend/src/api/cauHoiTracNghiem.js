import api from '@/api/axios'

export function fetchCauHoi(params) {
  return api.get('/trac-nghiem/cau-hoi', { params }).then((res) => res.data)
}

export function createCauHoi(payload) {
  return api.post('/trac-nghiem/cau-hoi', payload).then((res) => res.data)
}

export function createCauHoiBulk(payload) {
  return api.post('/trac-nghiem/cau-hoi/bulk', payload).then((res) => res.data)
}

export function updateCauHoi(id, payload) {
  return api.put(`/trac-nghiem/cau-hoi/${id}`, payload).then((res) => res.data)
}

export function deleteCauHoi(id) {
  return api.delete(`/trac-nghiem/cau-hoi/${id}`)
}

export function deleteCauHoiMany(ids) {
  return api.delete('/trac-nghiem/cau-hoi', { data: { ids } }).then((res) => res.data)
}

export function createCauTraLoi(cauHoiId, payload) {
  return api.post(`/trac-nghiem/cau-hoi/${cauHoiId}/cau-tra-loi`, payload).then((res) => res.data)
}

export function updateCauTraLoi(cauHoiId, answerId, payload) {
  return api.put(`/trac-nghiem/cau-hoi/${cauHoiId}/cau-tra-loi/${answerId}`, payload).then((res) => res.data)
}

export function deleteCauTraLoi(cauHoiId, answerId) {
  return api.delete(`/trac-nghiem/cau-hoi/${cauHoiId}/cau-tra-loi/${answerId}`)
}
