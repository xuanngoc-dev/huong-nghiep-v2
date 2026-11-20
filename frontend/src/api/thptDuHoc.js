import api from '@/api/axios'

// Danh mục du học THPT: mỗi bảng có cùng bộ API danh sách, thêm (một/nhiều), sửa, xóa (một/nhiều).
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

const HUONG_DI = '/danh-muc/thpt-du-hoc/huong-di'

export const huongDiApi = {
  ...taoApi(HUONG_DI),
  updateTrangThai: (id, trangThai) =>
    api.patch(`${HUONG_DI}/${id}/trang-thai`, { trang_thai: trangThai }).then((res) => res.data),
  updateTrangThaiMany: (ids, trangThai) =>
    api.patch(`${HUONG_DI}/trang-thai`, { ids, trang_thai: trangThai }).then((res) => res.data),
}

export const quocGiaApi = taoApi('/danh-muc/thpt-du-hoc/quoc-gia')
export const nganhApi = taoApi('/danh-muc/thpt-du-hoc/nganh')
export const chiPhiApi = taoApi('/danh-muc/thpt-du-hoc/chi-phi')
export const thuTucApi = taoApi('/danh-muc/thpt-du-hoc/thu-tuc')
export const kenhKetNoiApi = taoApi('/danh-muc/thpt-du-hoc/kenh-ket-noi')
