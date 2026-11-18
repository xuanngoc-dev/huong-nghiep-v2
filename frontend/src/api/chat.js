import api from '@/api/axios'
import { readChatStream } from '@/utils/chatStream'

const quiet = { skipLoading: true }

export function layDanhSachModel() {
  return api.get('/chat/model', quiet).then((res) => res.data)
}

export function hoiChat(payload) {
  return api.post('/chat/hoi', payload, { ...quiet, timeout: 90000 }).then((res) => res.data)
}

export async function hoiChatStream(payload, { signal, onEvent, timeoutMs = 95000 }) {
  const controller = new AbortController()
  const cancel = () => controller.abort()
  let timedOut = false
  const timeout = setTimeout(() => {
    timedOut = true
    controller.abort()
  }, timeoutMs)
  signal?.addEventListener('abort', cancel, { once: true })
  if (signal?.aborted) cancel()
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`${api.defaults.baseURL.replace(/\/$/, '')}/chat/hoi/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'text/event-stream',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(payload),
      signal: controller.signal,
    })
    if (!response.ok) {
      const body = await response.json().catch(() => ({}))
      const detail = typeof body.detail === 'string' ? body.detail : 'Không thể gửi câu hỏi. Vui lòng thử lại.'
      const retry = response.headers.get('Retry-After')
      // status để nơi gọi nhận biết 409 (phiên hội thoại đã kết thúc).
      throw Object.assign(new Error(`${detail}${retry ? ` Thử lại sau khoảng ${retry} giây.` : ''}`), { status: response.status })
    }
    await readChatStream(response, onEvent)
  } catch (error) {
    if (timedOut) throw new Error('AI phản hồi quá lâu. Vui lòng thử lại hoặc chọn model khác.')
    throw error
  } finally {
    clearTimeout(timeout)
    signal?.removeEventListener('abort', cancel)
  }
}

/** Trạng thái phiên hội thoại của người đang hỏi: { trang_thai, da_ket_thuc }. */
export function layTrangThaiPhien(maPhien, maKhach) {
  const params = maKhach ? { ma_khach_vang_lai: maKhach } : {}
  return api.get(`/chat/phien/${encodeURIComponent(maPhien)}`, { ...quiet, params }).then((res) => res.data)
}

/** Người hỏi tự kết thúc phiên của mình (lệnh /end). */
export function ketThucPhienChat(maPhien, maKhach) {
  const payload = maKhach ? { ma_khach_vang_lai: maKhach } : {}
  return api.post(`/chat/phien/${encodeURIComponent(maPhien)}/ket-thuc`, payload, quiet).then((res) => res.data)
}

export function layTaiLieu() {
  return api.get('/tai-lieu', quiet).then((res) => res.data)
}

export function taiTaiLieu(tep) {
  const form = new FormData()
  form.append('tep', tep)
  return api.post('/tai-lieu', form, quiet).then((res) => res.data)
}

export function xoaTaiLieu(ten) {
  return api.delete(`/tai-lieu/${encodeURIComponent(ten)}`, quiet)
}
