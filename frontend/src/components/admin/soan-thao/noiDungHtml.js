// Xử lý HTML cho trình soạn thảo nội dung (SoanThaoNoiDung.vue). Tách khỏi .vue để test được bằng node --test.

/**
 * HTML dán từ trang web khác, trước khi Tiptap đọc theo schema (thẻ / thuộc tính lạ Tiptap tự bỏ):
 * - h1 → h2: tiêu đề bài đã là h1 của trang, trình soạn thảo chỉ dùng h2–h4; h5, h6 → h4.
 * - Bỏ <script>, <style>, <meta>, comment (Word, Google Docs hay chèn kèm).
 */
export function chuanHoaHtmlDan(html) {
  return String(html || '')
    .replace(/<!--[\s\S]*?-->/g, '')
    .replace(/<(script|style)\b[\s\S]*?<\/\1>/gi, '')
    .replace(/<meta\b[^>]*>/gi, '')
    .replace(/<(\/?)h1(\s|>)/gi, '<$1h2$2')
    .replace(/<(\/?)h[56](\s|>)/gi, '<$1h4$2')
}

/** Nội dung rỗng của Tiptap ("<p></p>") lưu thành chuỗi rỗng. */
export function htmlHoacRong(html) {
  const text = String(html || '').trim()
  return text === '<p></p>' ? '' : text
}

/**
 * Ảnh nằm ở trang web khác (không phải Thư viện của hệ thống): URL http(s) khác origin API `goc`.
 * Đường dẫn tương đối và ảnh data: (base64) không tính.
 */
export function laAnhNgoai(src, goc) {
  const url = String(src || '')
  if (!/^https?:\/\//i.test(url)) return false
  return !(goc && url.startsWith(`${goc}/`))
}

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
