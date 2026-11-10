const LOCAL_API = 'http://127.0.0.1:3060/api/v1'

/** Base URL của API, không có dấu / cuối. Dev mặc định gọi thẳng backend. */
export function apiBaseUrl() {
  const configured = String(import.meta.env.VITE_API_BASE_URL || '').trim()
  if (configured) return configured.replace(/\/$/, '')
  if (import.meta.env.DEV) return LOCAL_API
  return '/api/v1'
}

/** Origin của API khi base là URL tuyệt đối. Rỗng khi dùng đường dẫn tương đối. */
export function apiOrigin() {
  const base = apiBaseUrl()
  if (!/^https?:\/\//i.test(base)) return ''
  return new URL(base).origin
}

/** Đường dẫn /api/v1/... do backend trả về thành URL đúng domain API. */
export function apiAssetUrl(path) {
  if (!path) return ''
  if (/^https?:\/\//i.test(path)) return path
  const normalized = path.startsWith('/') ? path : `/${path}`
  const origin = apiOrigin()
  return origin ? `${origin}${normalized}` : normalized
}
