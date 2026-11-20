import api from '@/api/axios'

// Danh mục xuất khẩu lao động THPT: mỗi bảng có cùng bộ API danh sách, thêm (một/nhiều), sửa, xóa (một/nhiều).
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

const NHOM_NGHE = '/danh-muc/thpt-xkld/nhom-nghe'

export const nhomNgheApi = {
  ...taoApi(NHOM_NGHE),
  updateTrangThai: (id, trangThai) =>
    api.patch(`${NHOM_NGHE}/${id}/trang-thai`, { trang_thai: trangThai }).then((res) => res.data),
  updateTrangThaiMany: (ids, trangThai) =>
    api.patch(`${NHOM_NGHE}/trang-thai`, { ids, trang_thai: trangThai }).then((res) => res.data),
}

export const thiTruongApi = taoApi('/danh-muc/thpt-xkld/thi-truong')
export const ngheCuTheApi = taoApi('/danh-muc/thpt-xkld/nghe-cu-the')
export const chiPhiApi = taoApi('/danh-muc/thpt-xkld/chi-phi')
export const thuTucApi = taoApi('/danh-muc/thpt-xkld/thu-tuc')
export const kenhKetNoiApi = taoApi('/danh-muc/thpt-xkld/kenh-ket-noi')
