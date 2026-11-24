import api from '@/api/axios'

// Tin tức (khu quản trị): cùng dạng { fetch, get, create, update, remove, removeMany } để dùng với useBangDuHoc.
function taoApi(duongDan) {
  return {
    fetch: (params) => api.get(duongDan, { params }).then((res) => res.data),
    get: (id) => api.get(`${duongDan}/${id}`).then((res) => res.data),
    create: (payload) => api.post(duongDan, payload).then((res) => res.data),
    update: (id, payload) => api.put(`${duongDan}/${id}`, payload).then((res) => res.data),
    remove: (id) => api.delete(`${duongDan}/${id}`),
    removeMany: (ids) => api.delete(duongDan, { data: { ids } }).then((res) => res.data),
  }
}

export const nhomTinApi = taoApi('/tin-tuc/nhom-tin')

export const baiVietApi = {
  ...taoApi('/tin-tuc/bai-viet'),
  // Đổi nhanh trạng thái xuất bản / nổi bật: { trang_thai?, is_noi_bat? }.
  hienThi: (id, payload) => api.patch(`/tin-tuc/bai-viet/${id}/hien-thi`, payload).then((res) => res.data),
}
