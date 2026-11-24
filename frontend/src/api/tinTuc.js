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

// Trang tin tức cho khách (không cần đăng nhập): chỉ bài đã xuất bản thuộc nhóm đang hiển thị.
export const tinTucCongKhaiApi = {
  nhomTin: () => api.get('/tin-tuc/cong-khai/nhom-tin').then((res) => res.data),
  // params: { q, nhom (slug nhóm), is_noi_bat, page, page_size }
  baiViet: (params) => api.get('/tin-tuc/cong-khai/bai-viet', { params }).then((res) => res.data),
  // Xem chi tiết theo slug (tăng lượt xem), kèm bai_lien_quan.
  chiTiet: (slug) => api.get(`/tin-tuc/cong-khai/bai-viet/${encodeURIComponent(slug)}`).then((res) => res.data),
}
