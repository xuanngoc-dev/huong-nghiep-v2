import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { GIAI_DOAN_CON_KEY, laGiaiDoanMo } from './capHoc'
import { routeNameGiaiDoanCon } from './routes'

// Giai đoạn của con phụ huynh đã chọn gần nhất (lưu sessionStorage) và chuyển sang màn tương ứng.
export function useGiaiDoanCon() {
  const router = useRouter()
  const giaiDoanDaChon = ref(sessionStorage.getItem(GIAI_DOAN_CON_KEY) || '')

  function chonGiaiDoan(giaiDoan) {
    if (!laGiaiDoanMo(giaiDoan)) return
    giaiDoanDaChon.value = giaiDoan
    sessionStorage.setItem(GIAI_DOAN_CON_KEY, giaiDoan)
    const name = routeNameGiaiDoanCon(giaiDoan)
    if (name) router.push({ name })
  }

  // Cấp học được tô chọn khi chính nó hoặc một lớp của nó là giai đoạn đã chọn.
  function laCapDangChon(cap) {
    return cap.giaiDoan === giaiDoanDaChon.value || !!cap.lop?.some((lop) => lop.giaiDoan === giaiDoanDaChon.value)
  }

  return { giaiDoanDaChon, chonGiaiDoan, laCapDangChon }
}
