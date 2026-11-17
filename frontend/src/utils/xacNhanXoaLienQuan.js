import { h } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

/**
 * Hỏi xác nhận xóa, có xem trước dữ liệu liên quan sẽ bị xóa kèm.
 *
 * - `taiAnhHuong()`: gọi API xem trước số lượng (anh-huong-xoa).
 * - `dongLienQuan(anhHuong)`: các dòng liệt kê dữ liệu sẽ bị xóa kèm; mảng rỗng = không có gì liên quan.
 *
 * Trả `null` nếu người dùng hủy hoặc không xem trước được; ngược lại `{ xoaLienQuan }` để gửi kèm lệnh xóa.
 */
export async function xacNhanXoaLienQuan({ tieuDe, taiAnhHuong, dongLienQuan }) {
  let dong
  try {
    dong = dongLienQuan(await taiAnhHuong())
  } catch (error) {
    const detail = error?.response?.data?.detail
    ElMessage.error(typeof detail === 'string' ? detail : 'Không kiểm tra được dữ liệu liên quan')
    return null
  }
  const xoaLienQuan = dong.length > 0
  const message = xoaLienQuan
    ? h('div', [
        h('p', `${tieuDe}? Thao tác này sẽ xóa luôn:`),
        h('ul', { style: 'margin: 8px 0; padding-left: 20px' }, dong.map((text) => h('li', text))),
        h('p', { style: 'color: var(--el-color-danger)' }, 'Dữ liệu đã xóa không thể khôi phục.'),
      ])
    : `${tieuDe}?`
  try {
    await ElMessageBox.confirm(message, 'Xác nhận xóa', {
      type: 'warning',
      confirmButtonText: xoaLienQuan ? 'Đồng ý xóa tất cả' : 'Xóa',
      cancelButtonText: 'Hủy',
      confirmButtonClass: 'el-button--danger',
    })
  } catch {
    return null
  }
  return { xoaLienQuan }
}
