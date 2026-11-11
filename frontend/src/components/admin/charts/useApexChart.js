import ApexCharts from 'apexcharts'
import { storeToRefs } from 'pinia'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useLayoutStore } from '@/stores/layout'

// Bảng màu chung cho biểu đồ quản trị; phần tử đầu là màu thương hiệu.
export const BANG_MAU = ['#1f7a4d', '#2f6fdb', '#e0a526', '#d9534f', '#7b61c9', '#1a9fb0', '#8a9199']

// Màu chữ, lưới, nền khớp với token sáng / tối trong styles/index.scss.
const GIAO_DIEN = {
  sang: { chu: '#6b7280', chuDam: '#1f2937', luoi: '#eef0f3', nen: '#ffffff', tooltip: 'light' },
  toi: { chu: '#919d97', chuDam: '#e4ebe7', luoi: '#252e2a', nen: '#161d1a', tooltip: 'dark' },
}

export function mauGiaoDien() {
  return useLayoutStore().isDark ? GIAO_DIEN.toi : GIAO_DIEN.sang
}

// Cấu hình nền dùng chung: font, toolbar, lưới, tooltip.
export function cauHinhNen(height) {
  const mau = mauGiaoDien()
  return {
    chart: {
      height,
      fontFamily: 'inherit',
      background: 'transparent',
      toolbar: { show: false },
      zoom: { enabled: false },
      animations: { speed: 400 },
      foreColor: mau.chu,
    },
    theme: { mode: mau.tooltip },
    dataLabels: { enabled: false },
    grid: { borderColor: mau.luoi, strokeDashArray: 4 },
    legend: { position: 'top', horizontalAlign: 'right', fontSize: '13px' },
    tooltip: { theme: mau.tooltip },
  }
}

/**
 * Gắn một biểu đồ ApexCharts vào phần tử `khung`, tự vẽ lại khi props hoặc chế độ sáng / tối đổi.
 * @param {() => object} taoCauHinh hàm trả về toàn bộ options (gồm series)
 * @param {() => unknown} nguon giá trị theo dõi để cập nhật biểu đồ
 */
export function useApexChart(taoCauHinh, nguon) {
  const khung = ref(null)
  const { isDark } = storeToRefs(useLayoutStore())
  let bieuDo = null

  onMounted(() => {
    bieuDo = new ApexCharts(khung.value, taoCauHinh())
    bieuDo.render()
  })

  watch(
    [nguon, isDark],
    () => {
      if (!bieuDo) return
      const { series, ...options } = taoCauHinh()
      bieuDo.updateOptions(options, false, true)
      bieuDo.updateSeries(series)
    },
    { deep: true },
  )

  onBeforeUnmount(() => {
    bieuDo?.destroy()
    bieuDo = null
  })

  return { khung }
}
