<script setup>
import ApexCharts from 'apexcharts'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  categories: { type: Array, default: () => [] },
  values: { type: Array, default: () => [] },
  seriesName: { type: String, default: 'Điểm' },
  height: { type: Number, default: 240 },
})

const khung = ref(null)
let bieuDo = null
let quanSat = null
let kichThuocCu = 0

function diemCaoNhat() {
  return Math.max(0, ...props.values.map((item) => Number(item) || 0))
}

function buocTruc() {
  const caoNhat = diemCaoNhat()
  if (caoNhat <= 20) return 5
  if (caoNhat <= 50) return 10
  return 20
}

function trucY() {
  const buoc = buocTruc()
  const moc = Math.ceil((diemCaoNhat() + 1) / buoc) * buoc
  return { stepSize: buoc, max: Math.max(buoc, moc) }
}

function kichThuocRadar() {
  const rong = khung.value?.clientWidth || 360
  return Math.max(44, Math.min(140, Math.round((rong - 196) / 2)))
}

function mauNhan() {
  const mau = '#121a28'
  return props.categories.length ? props.categories.map(() => mau) : mau
}

function cauHinh() {
  return {
    series: [{ name: props.seriesName, data: props.values }],
    chart: {
      height: props.height,
      type: 'radar',
      toolbar: { show: false },
      fontFamily: 'inherit',
    },
    colors: ['#3f9643'],
    legend: { show: false },
    xaxis: {
      categories: props.categories,
      labels: {
        style: { colors: mauNhan(), fontSize: '14px', fontWeight: 600 },
      },
    },
    yaxis: {
      ...trucY(),
      labels: { style: { colors: '#1a2433', fontSize: '13px', fontWeight: 600 } },
    },
    stroke: { width: 2 },
    fill: { opacity: 0.22 },
    markers: {
      size: 4,
      colors: ['#3f9643'],
      strokeColors: '#fff',
      strokeWidth: 2,
    },
    plotOptions: {
      radar: {
        size: kichThuocRadar(),
        polygons: {
          strokeColors: '#d7ebe0',
          connectorColors: '#d7ebe0',
          fill: { colors: ['#f3faf5', '#fff'] },
        },
      },
    },
  }
}

function capNhat() {
  if (!bieuDo) return
  bieuDo.updateOptions(
    {
      xaxis: {
        categories: props.categories,
        labels: { style: { colors: mauNhan(), fontSize: '14px', fontWeight: 600 } },
      },
      yaxis: {
        ...trucY(),
        labels: { style: { colors: '#1a2433', fontSize: '13px', fontWeight: 600 } },
      },
    },
    false,
    true,
  )
  bieuDo.updateSeries([{ name: props.seriesName, data: props.values }])
}

function chinhKichThuoc() {
  const size = kichThuocRadar()
  if (!bieuDo || Math.abs(size - kichThuocCu) < 4) return
  kichThuocCu = size
  bieuDo.updateOptions({ plotOptions: { radar: { size } } }, false, true)
}

onMounted(() => {
  kichThuocCu = kichThuocRadar()
  bieuDo = new ApexCharts(khung.value, cauHinh())
  bieuDo.render()
  quanSat = new ResizeObserver(chinhKichThuoc)
  quanSat.observe(khung.value)
})

watch(() => [props.categories.join('|'), props.values.join('|'), props.seriesName], capNhat)

onBeforeUnmount(() => {
  quanSat?.disconnect()
  quanSat = null
  bieuDo?.destroy()
  bieuDo = null
})
</script>

<template>
  <div ref="khung" class="radar-chart" />
</template>

<style scoped>
.radar-chart {
  width: 100%;
  max-width: 440px;
  margin: 0 auto;
}

.radar-chart :deep(.apexcharts-canvas),
.radar-chart :deep(.apexcharts-svg) {
  overflow: visible;
}

.radar-chart :deep(.apexcharts-xaxis text) {
  fill: #121a28;
  font-size: 14px;
  font-weight: 600;
}

.radar-chart :deep(.apexcharts-yaxis text) {
  fill: #1a2433;
  font-size: 13px;
  font-weight: 600;
}
</style>
