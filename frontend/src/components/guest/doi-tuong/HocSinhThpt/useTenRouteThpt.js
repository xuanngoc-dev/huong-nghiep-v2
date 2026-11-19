import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { TIEN_TO_HOC_SINH, doiTenRouteThpt } from './routes'

// Tên route theo nhánh đang đứng: viết tên nhánh học sinh (`thpt-...`), tự đổi sang nhánh phụ huynh khi cần.
export function useTenRouteThpt() {
  const route = useRoute()
  const tienTo = computed(() => route.meta.tienTo || TIEN_TO_HOC_SINH)
  const goc = computed(() => route.meta.goc || 'hoc-sinh-thpt')

  function tenRoute(ten) {
    return doiTenRouteThpt(ten, tienTo.value)
  }

  return { tienTo, goc, tenRoute }
}
