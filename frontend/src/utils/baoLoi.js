import { h } from 'vue'
import { ElMessageBox } from 'element-plus'
import { tachLoi } from '@/utils/tachLoi'

/**
 * Báo lỗi bằng dialog (thay cho ElMessage.error) để đọc kỹ được thông báo dài; thông báo nhiều lỗi
 * ("... có N lỗi: a; b; c") hiện thành danh sách cuộn được. Trả Promise xong khi người dùng đóng dialog.
 */
export function baoLoi(noiDung, tieuDe = 'Có lỗi xảy ra') {
  const { dau, ds } = tachLoi(noiDung)
  const message = ds.length
    ? h('div', [
        h('p', { style: 'margin: 0 0 8px' }, dau),
        h(
          'ol',
          { style: 'margin: 0; padding-left: 20px; max-height: 50vh; overflow: auto; word-break: break-word' },
          ds.map((dong) => h('li', { style: 'margin-bottom: 4px' }, dong)),
        ),
      ])
    : dau
  return ElMessageBox.alert(message, tieuDe, {
    type: 'error',
    confirmButtonText: 'Đóng',
    customStyle: { maxWidth: 'min(720px, calc(100vw - 32px))', width: '720px' },
  }).catch(() => {})
}
