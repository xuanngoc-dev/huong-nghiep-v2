import api from '@/api/axios'

export function fetchCauHoi(params) {
  return api.get('/trac-nghiem/cau-hoi', { params }).then((res) => res.data)
}

export function createCauHoi(payload) {
  return api.post('/trac-nghiem/cau-hoi', payload).then((res) => res.data)
}

export function createCauHoiBulk(payload, config) {
  return api.post('/trac-nghiem/cau-hoi/bulk', payload, config).then((res) => res.data)
}

export function updateCauHoi(id, payload) {
  return api.put(`/trac-nghiem/cau-hoi/${id}`, payload).then((res) => res.data)
}

// xoaLienQuan: xóa kèm các phiên khảo sát đã trả lời câu hỏi (đáp án luôn bị xóa theo câu hỏi).
export function deleteCauHoi(id, xoaLienQuan = false) {
  return api.delete(`/trac-nghiem/cau-hoi/${id}`, { params: { xoa_lien_quan: xoaLienQuan } })
}

export function deleteCauHoiMany(ids, xoaLienQuan = false) {
  return api
    .delete('/trac-nghiem/cau-hoi', { data: { ids }, params: { xoa_lien_quan: xoaLienQuan } })
    .then((res) => res.data)
}

export function updateTrangThaiCauHoi(id, trangThai) {
  return api.patch(`/trac-nghiem/cau-hoi/${id}/trang-thai`, { trang_thai: trangThai }).then((res) => res.data)
}

export function updateTrangThaiCauHoiMany(ids, trangThai) {
  return api.patch('/trac-nghiem/cau-hoi/trang-thai', { ids, trang_thai: trangThai }).then((res) => res.data)
}

export function fetchAnhHuongXoaCauHoi(ids) {
  return api.post('/trac-nghiem/cau-hoi/anh-huong-xoa', { ids }).then((res) => res.data)
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
