import ApexCharts from 'apexcharts'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

// Bảng màu chung cho biểu đồ quản trị; phần tử đầu là màu thương hiệu.
export const BANG_MAU = ['#1f7a4d', '#2f6fdb', '#e0a526', '#d9534f', '#7b61c9', '#1a9fb0', '#8a9199']

// Cấu hình nền dùng chung: font, toolbar, lưới, tooltip.
export function cauHinhNen(height) {
  return {
    chart: {
      height,
      fontFamily: 'inherit',
      toolbar: { show: false },
      zoom: { enabled: false },
      animations: { speed: 400 },
      foreColor: '#6b7280',
    },
    dataLabels: { enabled: false },
    grid: { borderColor: '#eef0f3', strokeDashArray: 4 },
    legend: { position: 'top', horizontalAlign: 'right', fontSize: '13px' },
    tooltip: { theme: 'light' },
  }
}

/**
 * Gắn một biểu đồ ApexCharts vào phần tử `khung`, tự vẽ lại khi props đổi.
 * @param {() => object} taoCauHinh hàm trả về toàn bộ options (gồm series)
 * @param {() => unknown} nguon giá trị theo dõi để cập nhật biểu đồ
 */
export function useApexChart(taoCauHinh, nguon) {
  const khung = ref(null)
  let bieuDo = null

  onMounted(() => {
    bieuDo = new ApexCharts(khung.value, taoCauHinh())
    bieuDo.render()
  })

  watch(
    nguon,
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
