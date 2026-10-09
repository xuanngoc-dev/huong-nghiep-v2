import axios from 'axios'
import { ElLoading, ElMessage } from 'element-plus'

/**
 * Axios instance dùng chung cho toàn bộ API.
 * - baseURL lấy từ .env (mặc định /api/v1 — Vite proxy sang backend)
 * - Tự gắn Bearer token từ localStorage khi có
 */
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 15000,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
})

const LOADING_FLAG = '__fullscreenLoading'
let pendingRequests = 0
let loadingInstance = null

function startLoading(config) {
  if (config.skipLoading) return config
  config[LOADING_FLAG] = true
  pendingRequests += 1
  if (!loadingInstance) {
    loadingInstance = ElLoading.service({
      lock: true,
      fullscreen: true,
      text: 'Đang tải…',
      background: 'rgba(0, 0, 0, 0.35)',
    })
  }
  return config
}

function stopLoading(config) {
  if (!config?.[LOADING_FLAG]) return
  config[LOADING_FLAG] = false
  pendingRequests = Math.max(0, pendingRequests - 1)
  if (pendingRequests === 0 && loadingInstance) {
    loadingInstance.close()
    loadingInstance = null
  }
}

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${token}`
    }

    if (typeof FormData !== 'undefined' && config.data instanceof FormData) {
      if (config.headers) {
        delete config.headers['Content-Type']
      }
    }

    return startLoading(config)
  },
  (error) => {
    stopLoading(error.config)
    return Promise.reject(error)
  },
)

api.interceptors.response.use(
  (response) => {
    stopLoading(response.config)
    return response
  },
  (error) => {
    stopLoading(error.config)
    const status = error.response?.status
    const detail =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message

    if (status === 401) {
      localStorage.removeItem('token')
      ElMessage.error('Phiên đăng nhập hết hạn.')
    } else if (status === 403) {
      ElMessage.error('Bạn không có quyền thực hiện thao tác này.')
    } else if (status === 422) {
      ElMessage.warning(typeof detail === 'string' ? detail : 'Dữ liệu không hợp lệ.')
    } else if (status && status >= 500) {
      ElMessage.error('Lỗi máy chủ. Vui lòng thử lại sau.')
    }

    return Promise.reject(error)
  },
)

export default api
