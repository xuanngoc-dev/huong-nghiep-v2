<template>
  <div ref="khung" class="bieu-do" />
</template>

<script setup>
/**
 * BieuDoDuong — biểu đồ đường / vùng theo thời gian.
 * series: [{ name: 'Lượt làm bài', data: [12, 30, ...] }]
 * sparkline: ẩn trục, lưới, chú thích để dùng trong thẻ thống kê.
 */
import { BANG_MAU, cauHinhNen, useApexChart } from './useApexChart'

const props = defineProps({
  series: { type: Array, default: () => [] },
  categories: { type: Array, default: () => [] },
  type: { type: String, default: 'area', validator: (v) => ['area', 'line'].includes(v) },
  height: { type: [Number, String], default: 300 },
  colors: { type: Array, default: () => BANG_MAU },
  donVi: { type: String, default: '' },
  sparkline: { type: Boolean, default: false },
})

function dinhDang(value) {
  return `${Number(value ?? 0).toLocaleString('vi-VN')}${props.donVi ? ` ${props.donVi}` : ''}`
}

function taoCauHinh() {
  const nen = cauHinhNen(props.height)
  return {
    ...nen,
    series: props.series,
    chart: { ...nen.chart, type: props.type, sparkline: { enabled: props.sparkline } },
    colors: props.colors,
    stroke: { curve: 'smooth', width: props.sparkline ? 2 : 2.5 },
    fill:
      props.type === 'area'
        ? { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.35, opacityTo: 0.02 } }
        : { opacity: 1 },
    markers: { size: 0, hover: { size: 5 } },
    xaxis: {
      categories: props.categories,
      axisBorder: { show: false },
      axisTicks: { show: false },
    },
    yaxis: { labels: { formatter: (v) => Number(v).toLocaleString('vi-VN') } },
    tooltip: { ...nen.tooltip, y: { formatter: dinhDang } },
  }
}

const { khung } = useApexChart(taoCauHinh, () => [props.series, props.categories, props.type, props.colors])
</script>

<style scoped>
.bieu-do {
  width: 100%;
  min-width: 0;
}
</style>
