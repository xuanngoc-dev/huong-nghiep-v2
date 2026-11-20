import api from '@/api/axios'

// Danh mục hướng đi sau THCS: mỗi bảng có cùng bộ API danh sách, thêm (một/nhiều), sửa, xóa (một/nhiều).
function taoApi(base) {
  return {
    fetch: (params, config = {}) => api.get(base, { ...config, params }).then((res) => res.data),
    create: (payload) => api.post(base, payload).then((res) => res.data),
    createBulk: (payload, config) => api.post(`${base}/bulk`, payload, config).then((res) => res.data),
    update: (id, payload) => api.put(`${base}/${id}`, payload).then((res) => res.data),
    remove: (id) => api.delete(`${base}/${id}`),
    removeMany: (ids) => api.delete(base, { data: { ids } }).then((res) => res.data),
  }
}

const HUONG_DI = '/danh-muc/thcs/huong-di'

export const huongDiApi = {
  ...taoApi(HUONG_DI),
  updateTrangThai: (id, trangThai) =>
    api.patch(`${HUONG_DI}/${id}/trang-thai`, { trang_thai: trangThai }).then((res) => res.data),
  updateTrangThaiMany: (ids, trangThai) =>
    api.patch(`${HUONG_DI}/trang-thai`, { ids, trang_thai: trangThai }).then((res) => res.data),
}

const TIEU_CHI = '/danh-muc/thcs/tieu-chi'

export const tieuChiApi = {
  ...taoApi(TIEU_CHI),
  fetchNhom: () => api.get(`${TIEU_CHI}/nhom`).then((res) => res.data),
}

export const uuNhuocDiemApi = taoApi('/danh-muc/thcs/uu-nhuoc-diem')
export const loiKhuyenLuuYApi = taoApi('/danh-muc/thcs/loi-khuyen-luu-y')

// Điểm phù hợp hướng đi - tiêu chí: khóa ghép (thcs_huong_di_id, thcs_tieu_chi_id).
const HUONG_DI_TIEU_CHI = '/danh-muc/thcs/huong-di-tieu-chi'

export const huongDiTieuChiApi = {
  fetch: (params, config = {}) => api.get(HUONG_DI_TIEU_CHI, { ...config, params }).then((res) => res.data),
  create: (payload) => api.post(HUONG_DI_TIEU_CHI, payload).then((res) => res.data),
  createBulk: (payload, config) => api.post(`${HUONG_DI_TIEU_CHI}/bulk`, payload, config).then((res) => res.data),
  update: (huongId, tieuChiId, payload) =>
    api.put(`${HUONG_DI_TIEU_CHI}/${huongId}/${tieuChiId}`, payload).then((res) => res.data),
  remove: (huongId, tieuChiId) => api.delete(`${HUONG_DI_TIEU_CHI}/${huongId}/${tieuChiId}`),
  removeMany: (items) => api.delete(HUONG_DI_TIEU_CHI, { data: { items } }).then((res) => res.data),
}
