import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { DOI_TUONG_THCS, TIEN_TO_HOC_SINH_THCS, doiTenRouteThcs } from './routes'

// Tên route theo nhánh đang đứng: viết tên nhánh học sinh (`hs-thcs-...`), tự đổi sang nhánh phụ huynh khi cần.
// `laPhuHuynh`: đang ở nhánh phụ huynh, dùng để đổi lời xưng hô (bạn → con).
// `tienTo`: truyền khi gọi từ trang gốc của nhánh (route gốc không có meta.tienTo).
export function useTenRouteThcs(tienTo) {
  const route = useRoute()
  const tienToHienTai = computed(() => tienTo || route.meta.tienTo || TIEN_TO_HOC_SINH_THCS)
  const goc = computed(() => route.meta.goc || DOI_TUONG_THCS)
  const laPhuHuynh = computed(() => tienToHienTai.value !== TIEN_TO_HOC_SINH_THCS)

  function tenRoute(ten) {
    return doiTenRouteThcs(ten, tienToHienTai.value)
  }

  return { goc, laPhuHuynh, tenRoute }
}
