import api from '@/api/axios'

// Kết quả đánh giá xét tuyển của một lượt tìm trường. Khách gửi kèm ma_thiet_bi để được xem.
const cauHinh = (params) => ({ params, skipLoading: true })

export function fetchLanDanhGia(lanId, maThietBi) {
  return api.get(`/xet-tuyen/danh-gia/${lanId}`, cauHinh({ ma_thiet_bi: maThietBi || undefined })).then((res) => res.data)
}

export function fetchKetQuaChuongTrinh(lanId, params) {
  return api.get(`/xet-tuyen/danh-gia/${lanId}/chuong-trinh`, cauHinh(params)).then((res) => res.data)
}

export function fetchKetQuaTruong(lanId, maThietBi) {
  return api
    .get(`/xet-tuyen/danh-gia/${lanId}/truong`, cauHinh({ ma_thiet_bi: maThietBi || undefined }))
    .then((res) => res.data)
}

export function fetchPhuongAnChuongTrinh(lanId, chuongTrinhId, maThietBi) {
  return api
    .get(
      `/xet-tuyen/danh-gia/${lanId}/chuong-trinh/${chuongTrinhId}/phuong-an`,
      cauHinh({ ma_thiet_bi: maThietBi || undefined }),
    )
    .then((res) => res.data)
}
