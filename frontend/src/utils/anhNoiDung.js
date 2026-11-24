// Đường dẫn ảnh trong nội dung HTML bài viết: dùng chung cho trình soạn thảo (quản trị) và trang tin tức (khách).

/**
 * Ảnh Thư viện lưu trong nội dung bằng đường dẫn tương đối ("/api/v1/thu-vien/..."), không gắn domain API của môi
 * trường đang soạn (dev / production). Trình soạn thảo cần URL đầy đủ để hiện ảnh: đổi qua lại khi nạp / lưu.
 */
export function anhTuyetDoi(html, goc) {
  if (!goc) return String(html || '')
  return String(html || '').replace(/(<img\b[^>]*\bsrc=")(\/[^/"][^"]*)"/gi, `$1${goc}$2"`)
}

export function anhTuongDoi(html, goc) {
  if (!goc) return String(html || '')
  const thoat = goc.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return String(html || '').replace(new RegExp(`(<img\\b[^>]*\\bsrc=")${thoat}(/[^"]*)"`, 'gi'), '$1$2"')
}
