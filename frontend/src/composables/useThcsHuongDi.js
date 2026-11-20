import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { huongDiApi } from '@/api/thcsHuongDi'
import { errorMessage, loadAll } from '@/composables/useThptDuHoc'

// Bảng danh sách, đọc JSON, chuẩn hóa giá trị dùng chung với danh mục du học THPT.
export {
  docMangJson,
  errorMessage,
  giaTriTuyChon,
  loadAll,
  useBangDuHoc as useBangThcs,
} from '@/composables/useThptDuHoc'

/** Danh sách hướng đi để chọn/lọc ở các trang danh mục con của hướng đi sau THCS. */
export function useHuongDiThcs() {
  const huongOptions = ref([])

  async function loadHuongOptions() {
    try {
      huongOptions.value = await loadAll(huongDiApi.fetch)
    } catch (error) {
      ElMessage.error(errorMessage(error, 'Không tải được danh sách hướng đi'))
    }
  }

  function nhanHuong(item) {
    return `${item.ten_huong} (${item.ma_huong})`
  }

  /** Đọc hướng đi của một phần tử JSON: nhận thcs_huong_di_id hoặc ma_huong. */
  function huongTuJson(item, line) {
    const id = Number(item.thcs_huong_di_id) || null
    if (id) return id
    if (!item.ma_huong) throw new Error(`Phần tử thứ ${line} thiếu ma_huong hoặc thcs_huong_di_id`)
    const ma = String(item.ma_huong).trim().toUpperCase()
    const found = huongOptions.value.find((h) => h.ma_huong === ma)
    if (!found) throw new Error(`Phần tử thứ ${line}: không tìm thấy hướng đi có mã ${ma}`)
    return found.id
  }

  return { huongOptions, loadHuongOptions, nhanHuong, huongTuJson }
}
