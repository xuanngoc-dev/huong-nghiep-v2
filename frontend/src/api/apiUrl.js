const DEFAULT_API = 'https://huongnghiepapi.dtsgroup.com.vn/api/v1'

/** Base URL của API, không có dấu / cuối. */
export function apiBaseUrl() {
  const configured = String(import.meta.env.VITE_API_BASE_URL || '').trim()
  if (configured) return configured.replace(/\/$/, '')
  return DEFAULT_API
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
