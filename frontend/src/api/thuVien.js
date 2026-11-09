import api from '@/api/axios'

export function fetchThuVien(thuMuc = '') {
  const params = {}
  if (thuMuc) params.thu_muc = thuMuc
  return api.get('/thu-vien', { params }).then((res) => res.data)
}

export function importThuVienUrl(url, thuMuc = '') {
  return api
    .post('/thu-vien/tu-url', { url, thu_muc: thuMuc || '' }, { timeout: 10 * 60 * 1000, skipLoading: true })
    .then((res) => res.data)
}

export function uploadThuVien(file, thuMuc = '') {
  const data = new FormData()
  data.append('tep', file)
  data.append('thu_muc', thuMuc || '')
  return api
    .post('/thu-vien', data, { timeout: 10 * 60 * 1000, skipLoading: true })
    .then((res) => res.data)
}

export function createThuMuc(thuMuc, ten) {
  return api.post('/thu-vien/thu-muc', { thu_muc: thuMuc || '', ten }).then((res) => res.data)
}

export function renameThuVien(duongDan, tenMoi) {
  return api.post('/thu-vien/doi-ten', { duong_dan: duongDan, ten_moi: tenMoi }).then((res) => res.data)
}

export function compressThuVien(thuMuc, danhSach, tenTep) {
  return api
    .post('/thu-vien/nen', { thu_muc: thuMuc || '', danh_sach: danhSach, ten_tep: tenTep })
    .then((res) => res.data)
}

export function extractThuVien(duongDan) {
  return api.post('/thu-vien/giai-nen', { duong_dan: duongDan }).then((res) => res.data)
}

export function deleteThuVien(duongDan) {
  return api.delete('/thu-vien', { params: { duong_dan: duongDan } })
}

export function copyThuVien(danhSach, thuMucDich = '') {
  return api
    .post('/thu-vien/sao-chep', { danh_sach: danhSach, thu_muc_dich: thuMucDich || '' })
    .then((res) => res.data)
}

export function moveThuVien(danhSach, thuMucDich = '') {
  return api
    .post('/thu-vien/di-chuyen', { danh_sach: danhSach, thu_muc_dich: thuMucDich || '' })
    .then((res) => res.data)
}

export function deleteThuVienMany(danhSach) {
  return api.post('/thu-vien/xoa', { danh_sach: danhSach }).then((res) => res.data)
}
