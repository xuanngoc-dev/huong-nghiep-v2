import DOMPurify from 'dompurify'
import { apiOrigin } from '@/api/apiUrl'
import { anhTuyetDoi } from '@/utils/anhNoiDung'

// Nội dung bài có thể dán từ trang web khác: lọc trước khi v-html (bỏ script, sự kiện on*, javascript: …).
// Liên kết mở tab mới luôn kèm rel="noopener noreferrer".
DOMPurify.addHook('afterSanitizeAttributes', (node) => {
  if (node.tagName === 'A' && node.getAttribute('target') === '_blank') {
    node.setAttribute('rel', 'noopener noreferrer nofollow')
  }
  if (node.tagName === 'IMG') {
    node.setAttribute('loading', 'lazy')
    node.setAttribute('decoding', 'async')
  }
})

/** HTML nội dung bài viết → HTML an toàn để hiển thị; ảnh Thư viện (đường dẫn tương đối) ghép domain API. */
export function lamSachHtml(html) {
  return DOMPurify.sanitize(anhTuyetDoi(html, apiOrigin()), {
    USE_PROFILES: { html: true },
    ADD_ATTR: ['target'],
    FORBID_TAGS: ['style', 'form', 'input', 'button', 'textarea', 'select'],
    FORBID_ATTR: ['style'],
  })
}
