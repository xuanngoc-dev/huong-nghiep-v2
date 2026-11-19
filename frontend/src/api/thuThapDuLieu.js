import api from '@/api/axios'
import { createEventParser } from '@/utils/chatStream'

const BASE = '/thu-thap-du-lieu'

// Cấu hình AI: Prompt trên OpenAI (quy tắc + model quản lý ở OpenAI) hoặc quy tắc mặc định.
export function fetchCauHinhThuThap(config = {}) {
  return api.get(`${BASE}/cau-hinh`, config).then((res) => res.data)
}

// Phiên thu thập
export function fetchPhienThuThap(params, config = {}) {
  return api.get(`${BASE}/phien`, { ...config, params }).then((res) => res.data)
}

export function createPhienThuThap(payload = {}) {
  return api.post(`${BASE}/phien`, payload).then((res) => res.data)
}

export function fetchChiTietPhienThuThap(id, config = {}) {
  return api.get(`${BASE}/phien/${id}`, config).then((res) => res.data)
}

export function updatePhienThuThap(id, payload) {
  return api.patch(`${BASE}/phien/${id}`, payload).then((res) => res.data)
}

export function deletePhienThuThap(id) {
  return api.delete(`${BASE}/phien/${id}`)
}

export function taiTepThuThap(phienId, tep) {
  const form = new FormData()
  form.append('tep', tep)
  return api.post(`${BASE}/phien/${phienId}/tep`, form, { skipLoading: true, timeout: 120000 }).then((res) => res.data)
}

export function deleteTepThuThap(phienId, tepId) {
  return api.delete(`${BASE}/phien/${phienId}/tep/${tepId}`)
}

export function luuBanNhapThuThap(phienId, duLieu) {
  return api.put(`${BASE}/phien/${phienId}/ban-nhap`, { du_lieu: duLieu }, { timeout: 120000 }).then((res) => res.data)
}

export function kiemTraBanNhapThuThap(phienId) {
  return api.post(`${BASE}/phien/${phienId}/kiem-tra`, null, { timeout: 120000 }).then((res) => res.data)
}

export function nhapBanNhapThuThap(phienId) {
  return api.post(`${BASE}/phien/${phienId}/nhap`, null, { timeout: 120000 }).then((res) => res.data)
}

/**
 * Gửi yêu cầu cho AI thu thập (SSE). onEvent(event, data) với event: cong_cu, ban_nhap, tra_loi, xong, loi.
 * Một lượt có thể kéo dài nhiều phút (AI tìm web, đọc nhiều trang, tạo bản nháp).
 */
export async function guiTinNhanThuThap(phienId, noiDung, { signal, onEvent }) {
  const token = localStorage.getItem('token')
  const response = await fetch(`${api.defaults.baseURL.replace(/\/$/, '')}${BASE}/phien/${phienId}/tin-nhan`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ noi_dung: noiDung }),
    signal,
  })
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(typeof body.detail === 'string' ? body.detail : 'Không gửi được yêu cầu cho AI.')
  }
  if (!response.body) throw new Error('Trình duyệt chưa hỗ trợ nhận phản hồi trực tiếp.')
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  const parser = createEventParser(onEvent)
  while (true) {
    const { value, done } = await reader.read()
    if (done) {
      parser.push(decoder.decode(), true)
      return
    }
    parser.push(decoder.decode(value, { stream: true }))
  }
}
