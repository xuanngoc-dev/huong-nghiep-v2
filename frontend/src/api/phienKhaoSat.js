import api from '@/api/axios'

export function batDauPhienHolland() {
  return api.post('/trac-nghiem/phien').then((res) => res.data)
}

export function fetchPhienLamBai(ssid) {
  return api.get(`/trac-nghiem/phien/${encodeURIComponent(ssid)}`).then((res) => res.data)
}

export function luuTraLoi(ssid, chiTietId, cauTraLoiId) {
  return api
    .put(
      `/trac-nghiem/phien/${encodeURIComponent(ssid)}/chi-tiet/${chiTietId}`,
      { cau_tra_loi_id: cauTraLoiId },
      { skipLoading: true },
    )
    .then((res) => res.data)
}

export function fetchKetQua(ssid) {
  return api.get(`/trac-nghiem/phien/${encodeURIComponent(ssid)}/ket-qua`).then((res) => res.data)
}

export function fetchNganhPhuHop(ssid) {
  return api
    .get(`/trac-nghiem/phien/${encodeURIComponent(ssid)}/nganh-phu-hop`, { skipLoading: true })
    .then((res) => res.data)
}

export function fetchPhienKhaoSatQuanTri(params, config = {}) {
  return api.get('/trac-nghiem/phien/quan-tri', { ...config, params }).then((res) => res.data)
}

export function fetchLichSuKhaoSat(params, config = {}) {
  return api.get('/trac-nghiem/phien/lich-su', { ...config, params }).then((res) => res.data)
}

export function deletePhienKhaoSatQuanTri(id) {
  return api.delete(`/trac-nghiem/phien/quan-tri/${id}`)
}

export function deletePhienKhaoSatQuanTriMany(ids) {
  return api.delete('/trac-nghiem/phien/quan-tri', { data: { ids } }).then((res) => res.data)
}
