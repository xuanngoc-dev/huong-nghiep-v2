<template>
  <div ref="khung" class="bieu-do" />
</template>

<script setup>
/**
 * BieuDoTron — biểu đồ tròn / vành khuyên thể hiện tỷ trọng.
 * labels: ['Kỹ thuật (R)', ...], values: [320, 210, ...]
 * nhanTong: nhãn hiển thị giữa vành khuyên (chỉ với type="donut").
 */
import { BANG_MAU, cauHinhNen, mauGiaoDien, useApexChart } from './useApexChart'

const props = defineProps({
  labels: { type: Array, default: () => [] },
  values: { type: Array, default: () => [] },
  type: { type: String, default: 'donut', validator: (v) => ['donut', 'pie'].includes(v) },
  height: { type: [Number, String], default: 300 },
  colors: { type: Array, default: () => BANG_MAU },
  donVi: { type: String, default: '' },
  nhanTong: { type: String, default: 'Tổng' },
})

function dinhDang(value) {
  return `${Number(value ?? 0).toLocaleString('vi-VN')}${props.donVi ? ` ${props.donVi}` : ''}`
}

function taoCauHinh() {
  const nen = cauHinhNen(props.height)
  const mau = mauGiaoDien()
  return {
    ...nen,
    series: props.values,
    labels: props.labels,
    chart: { ...nen.chart, type: props.type },
    colors: props.colors,
    stroke: { width: 2, colors: [mau.nen] },
    dataLabels: {
      enabled: true,
      formatter: (percent) => `${Math.round(percent)}%`,
      dropShadow: { enabled: false },
    },
    legend: { position: 'bottom', fontSize: '13px' },
    plotOptions: {
      pie: {
        donut: {
          size: '64%',
          labels: {
            show: true,
            total: {
              show: true,
              label: props.nhanTong,
              color: mau.chu,
              formatter: (w) =>
                w.globals.seriesTotals.reduce((a, b) => a + b, 0).toLocaleString('vi-VN'),
            },
            value: { color: mau.chuDam, formatter: (v) => Number(v).toLocaleString('vi-VN') },
          },
        },
      },
    },
    tooltip: { ...nen.tooltip, y: { formatter: dinhDang } },
  }
}

const { khung } = useApexChart(taoCauHinh, () => [props.labels, props.values, props.type, props.colors])
</script>

<style scoped>
.bieu-do {
  width: 100%;
  min-width: 0;
}
</style>
