import api from '@/api/axios'

export function fetchNganhHocTheoTruong(params) {
  return api.get('/danh-muc/nganh-hoc-theo-truong', { params }).then((res) => res.data)
}

export function fetchNamHocNganhTheoTruong() {
  return api.get('/danh-muc/nganh-hoc-theo-truong/nam-hoc').then((res) => res.data)
}

export function createNganhHocTheoTruong(payload) {
  return api.post('/danh-muc/nganh-hoc-theo-truong', payload).then((res) => res.data)
}

export function updateNganhHocTheoTruong(id, payload) {
  return api.put(`/danh-muc/nganh-hoc-theo-truong/${id}`, payload).then((res) => res.data)
}

export function deleteNganhHocTheoTruong(id) {
  return api.delete(`/danh-muc/nganh-hoc-theo-truong/${id}`)
}

export function deleteNganhHocTheoTruongMany(ids) {
  return api.delete('/danh-muc/nganh-hoc-theo-truong', { data: { ids } }).then((res) => res.data)
}

export function importNganhHocTheoTruong(items, config) {
  return api.post('/danh-muc/nganh-hoc-theo-truong/bulk', items, config).then((res) => res.data)
}

export function kiemTraTruongImport(maTruong) {
  return api
    .post('/danh-muc/nganh-hoc-theo-truong/bulk/kiem-tra', { ma_truong: maTruong }, { skipLoading: true })
    .then((res) => res.data)
}
