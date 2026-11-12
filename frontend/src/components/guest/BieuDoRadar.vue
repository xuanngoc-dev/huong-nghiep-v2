<template>
  <div ref="khung" class="radar-chart" />
</template>

<script setup>
import ApexCharts from 'apexcharts'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  categories: { type: Array, default: () => [] },
  values: { type: Array, default: () => [] },
  seriesName: { type: String, default: 'Điểm' },
  height: { type: Number, default: 240 },
  // Vị trí (index) các trục cần làm nổi bật, ví dụ 3 nhóm điểm cao nhất.
  noiBat: { type: Array, default: () => [] },
})

const MAU_CHINH = '#1f7a4d'
const MAU_NHAN = '#1f2d26'
const MAU_NHAN_MO = '#8a9a92'
const MAU_LUOI = '#dfece4'

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
  return Math.max(44, Math.min(150, Math.round((rong - 170) / 2)))
}

function mauNhan() {
  if (!props.noiBat.length) return props.categories.map(() => MAU_NHAN)
  return props.categories.map((_, index) => (props.noiBat.includes(index) ? MAU_NHAN : MAU_NHAN_MO))
}

function diemNoiBat() {
  return props.noiBat.map((index) => ({
    seriesIndex: 0,
    dataPointIndex: index,
    fillColor: MAU_CHINH,
    strokeColor: '#fff',
    size: 6,
  }))
}

function tuyChonTruc() {
  return {
    xaxis: {
      categories: props.categories,
      labels: { style: { colors: mauNhan(), fontSize: '13px', fontWeight: 600 } },
    },
    yaxis: {
      ...trucY(),
      labels: { style: { colors: MAU_NHAN_MO, fontSize: '11px', fontWeight: 400 } },
    },
    markers: {
      size: 3,
      colors: ['#fff'],
      strokeColors: MAU_CHINH,
      strokeWidth: 2,
      hover: { size: 6 },
      discrete: diemNoiBat(),
    },
  }
}

function cauHinh() {
  return {
    series: [{ name: props.seriesName, data: props.values }],
    chart: {
      height: props.height,
      type: 'radar',
      toolbar: { show: false },
      fontFamily: 'inherit',
      animations: { speed: 500 },
    },
    colors: [MAU_CHINH],
    legend: { show: false },
    ...tuyChonTruc(),
    stroke: { width: 2 },
    fill: { opacity: 0.18 },
    tooltip: { y: { formatter: (value) => `${value} điểm` } },
    plotOptions: {
      radar: {
        size: kichThuocRadar(),
        polygons: {
          strokeColors: MAU_LUOI,
          connectorColors: MAU_LUOI,
          fill: { colors: ['#f7fbf8', '#fff'] },
        },
      },
    },
  }
}

function capNhat() {
  if (!bieuDo) return
  bieuDo.updateOptions(tuyChonTruc(), false, true)
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

watch(
  () => [props.categories.join('|'), props.values.join('|'), props.noiBat.join('|'), props.seriesName],
  capNhat,
)

onBeforeUnmount(() => {
  quanSat?.disconnect()
  quanSat = null
  bieuDo?.destroy()
  bieuDo = null
})
</script>

<style scoped>
.radar-chart {
  width: 100%;
  max-width: 480px;
  margin: 0 auto;
}

.radar-chart :deep(.apexcharts-canvas),
.radar-chart :deep(.apexcharts-svg) {
  overflow: visible;
}
</style>
