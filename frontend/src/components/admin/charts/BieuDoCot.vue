<script setup>
/**
 * BieuDoCot — biểu đồ cột dọc / thanh ngang.
 * series: [{ name: 'Lượt gợi ý', data: [120, 98, ...] }]
 * distributed: mỗi cột một màu (dùng khi chỉ có 1 series).
 */
import { BANG_MAU, cauHinhNen, useApexChart } from './useApexChart'

const props = defineProps({
  series: { type: Array, default: () => [] },
  categories: { type: Array, default: () => [] },
  height: { type: [Number, String], default: 300 },
  horizontal: { type: Boolean, default: false },
  stacked: { type: Boolean, default: false },
  distributed: { type: Boolean, default: false },
  colors: { type: Array, default: () => BANG_MAU },
  donVi: { type: String, default: '' },
})

function dinhDang(value) {
  return `${Number(value ?? 0).toLocaleString('vi-VN')}${props.donVi ? ` ${props.donVi}` : ''}`
}

function taoCauHinh() {
  const nen = cauHinhNen(props.height)
  const soLieu = { formatter: (v) => (typeof v === 'number' ? v.toLocaleString('vi-VN') : v) }
  return {
    ...nen,
    series: props.series,
    chart: { ...nen.chart, type: 'bar', stacked: props.stacked },
    colors: props.colors,
    plotOptions: {
      bar: {
        horizontal: props.horizontal,
        distributed: props.distributed,
        borderRadius: 4,
        borderRadiusApplication: 'end',
        columnWidth: '55%',
        barHeight: '60%',
      },
    },
    legend: { ...nen.legend, show: !props.distributed && props.series.length > 1 },
    xaxis: {
      categories: props.categories,
      axisBorder: { show: false },
      axisTicks: { show: false },
      labels: props.horizontal ? soLieu : {},
    },
    yaxis: { labels: props.horizontal ? { maxWidth: 200 } : soLieu },
    grid: {
      ...nen.grid,
      xaxis: { lines: { show: props.horizontal } },
      yaxis: { lines: { show: !props.horizontal } },
    },
    tooltip: { ...nen.tooltip, y: { formatter: dinhDang } },
  }
}

const { khung } = useApexChart(taoCauHinh, () => [
  props.series,
  props.categories,
  props.horizontal,
  props.stacked,
  props.colors,
])
</script>

<template>
  <div ref="khung" class="bieu-do" />
</template>

<style scoped>
.bieu-do {
  width: 100%;
  min-width: 0;
}
</style>
