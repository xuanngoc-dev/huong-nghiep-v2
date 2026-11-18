import api from '@/api/axios'

export function fetchLoaiCauHoi(params) {
  return api.get('/danh-muc/loai-cau-hoi', { params }).then((res) => res.data)
}

export function createLoaiCauHoi(payload) {
  return api.post('/danh-muc/loai-cau-hoi', payload).then((res) => res.data)
}

export function createLoaiCauHoiBulk(payload, config) {
  return api.post('/danh-muc/loai-cau-hoi/bulk', payload, config).then((res) => res.data)
}

export function updateLoaiCauHoi(id, payload) {
  return api.put(`/danh-muc/loai-cau-hoi/${id}`, payload).then((res) => res.data)
}

// xoaLienQuan: xóa kèm câu hỏi, đáp án và các phiên khảo sát có câu hỏi thuộc loại này.
export function deleteLoaiCauHoi(id, xoaLienQuan = false) {
  return api.delete(`/danh-muc/loai-cau-hoi/${id}`, { params: { xoa_lien_quan: xoaLienQuan } })
}

export function deleteLoaiCauHoiMany(ids, xoaLienQuan = false) {
  return api
    .delete('/danh-muc/loai-cau-hoi', { data: { ids }, params: { xoa_lien_quan: xoaLienQuan } })
    .then((res) => res.data)
}

export function updateTrangThaiLoaiCauHoi(id, trangThai) {
  return api.patch(`/danh-muc/loai-cau-hoi/${id}/trang-thai`, { trang_thai: trangThai }).then((res) => res.data)
}

export function updateTrangThaiLoaiCauHoiMany(ids, trangThai) {
  return api.patch('/danh-muc/loai-cau-hoi/trang-thai', { ids, trang_thai: trangThai }).then((res) => res.data)
}

export function fetchAnhHuongXoaLoaiCauHoi(ids) {
  return api.post('/danh-muc/loai-cau-hoi/anh-huong-xoa', { ids }).then((res) => res.data)
}
