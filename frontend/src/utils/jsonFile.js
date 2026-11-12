import { ElMessage } from 'element-plus'

export const JSON_FILE_MAX_MB = 5

/**
 * Đọc nội dung một file .json người dùng chọn hoặc kéo thả.
 * Trả về chuỗi nội dung, hoặc null nếu file không hợp lệ/không đọc được (đã báo lỗi).
 */
export async function docFileJson(file, maxMb = JSON_FILE_MAX_MB) {
  if (!file) return null
  if (!/\.json$/i.test(file.name) && file.type !== 'application/json') {
    ElMessage.error('Chỉ nhận file .json')
    return null
  }
  if (file.size > maxMb * 1024 * 1024) {
    ElMessage.error(`File JSON tối đa ${maxMb}MB`)
    return null
  }
  try {
    const text = await file.text()
    ElMessage.success(`Đã đọc file ${file.name}`)
    return text
  } catch {
    ElMessage.error('Không đọc được file')
    return null
  }
}
