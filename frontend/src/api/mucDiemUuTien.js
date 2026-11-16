import api from '@/api/axios'

// Mức điểm cộng khu vực / đối tượng ưu tiên theo năm tuyển sinh.
export function fetchMucDiemUuTien(params) {
  return api.get('/danh-muc/muc-diem-uu-tien', { params }).then((res) => res.data)
}

export function createMucDiemUuTien(payload) {
  return api.post('/danh-muc/muc-diem-uu-tien', payload).then((res) => res.data)
}

export function updateMucDiemUuTien(id, payload) {
  return api.put(`/danh-muc/muc-diem-uu-tien/${id}`, payload).then((res) => res.data)
}

export function deleteMucDiemUuTien(id) {
  return api.delete(`/danh-muc/muc-diem-uu-tien/${id}`)
}

export function deleteMucDiemUuTienMany(ids) {
  return api.delete('/danh-muc/muc-diem-uu-tien', { data: { ids } }).then((res) => res.data)
}
