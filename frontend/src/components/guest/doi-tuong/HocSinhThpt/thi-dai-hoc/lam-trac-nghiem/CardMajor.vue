<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import anhMacDinh from '@/assets/guest/sinh-vien.jpg'

defineOptions({ name: 'CardMajor' })

const props = defineProps({
  ten: { type: String, required: true },
  moTa: { type: String, default: '' },
  mucLuong: { type: String, default: '' },
  thoiGian: { type: String, default: '' },
  hinhAnh: { type: String, default: '' },
  chon: { type: Boolean, default: false },
})

const emit = defineEmits(['chon', 'khamPha'])

const anhLoi = ref(false)
const oChon = ref(null)

watch(
  () => props.hinhAnh,
  (url) => {
    anhLoi.value = false
    const text = typeof url === 'string' ? url.trim() : ''
    if (!text) return
    const probe = new Image()
    probe.onerror = () => {
      if ((props.hinhAnh || '').trim() === text) anhLoi.value = true
    }
    probe.src = text
  },
  { immediate: true },
)

const anh = computed(() => {
  const tuProps = typeof props.hinhAnh === 'string' ? props.hinhAnh.trim() : ''
  if (tuProps && !anhLoi.value) return tuProps
  return anhMacDinh
})

const styleNen = computed(() => {
  if (!anh.value) return undefined
  const mat = matTiepGiap(bamBanGhi())
  const url = anh.value.replace(/["\\\n\r\f]/g, '')
  return {
    backgroundImage: `url("${url}")`,
    WebkitMaskImage: mat,
    maskImage: mat,
  }
})

function bamBanGhi() {
  const khoa = String(props.ten || '')
  let hash = 2166136261
  for (let i = 0; i < khoa.length; i += 1) {
    hash ^= khoa.charCodeAt(i)
    hash = Math.imul(hash, 16777619)
  }
  return hash >>> 0
}

function matSong(hash) {
  const truc = 34 + (hash % 8)
  const bienDo = 2.5 + ((hash >>> 4) % 6)
  const soSong = 1 + ((hash >>> 8) % 3)
  const lech = ((hash >>> 11) % 9) - 4
  const phase = ((hash >>> 16) % 628) / 100
  const beRong = 1.15 + ((hash >>> 6) % 3) * 0.35
  const soLop = 14
  const ys = []
  for (let y = -20; y <= 120; y += 10) ys.push(y)

  function xTai(y, shift) {
    const ty = (y + 20) / 140
    const x = truc + shift + lech * ty + Math.sin(phase + ty * Math.PI * 2 * soSong) * bienDo
    return 100 - x
  }

  function vien(shift) {
    return ys.map((y) => `${xTai(y, shift).toFixed(2)},${y}`).join(' L')
  }

  let shapes = `<path d='M130,-20 L${vien(0)} L130,120 Z' fill='white'/>`
  for (let i = 0; i < soLop; i += 1) {
    const mo = ((1 - (i + 1) / soLop) ** 1.35).toFixed(3)
    const a = vien(i * beRong).split(' L')
    const b = vien((i + 1) * beRong).split(' L')
    shapes += `<path d='M${a.join(' L')} L${b.reverse().join(' L')} Z' fill='white' fill-opacity='${mo}'/>`
  }

  const svg =
    `<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' preserveAspectRatio='none'>${shapes}</svg>`
  return `url("data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}")`
}

function matTiepGiap(hash) {
  const kieu = hash % 6
  const neo = 36 + (hash % 8)
  const het = neo + 16 + ((hash >>> 5) % 12)
  const goc = 76 + ((hash >>> 9) % 29)
  if (kieu === 0) return `linear-gradient(${goc + 180}deg, #000 ${neo}%, transparent ${het}%)`
  if (kieu === 1) return `linear-gradient(${360 - goc}deg, #000 ${neo}%, transparent ${het}%)`
  if (kieu === 2) {
    const y = (hash >>> 12) % 101
    return `radial-gradient(145% 180% at 106% ${y}%, #000 ${neo}%, transparent ${het}%)`
  }
  if (kieu === 3) {
    const giua = neo + Math.round((het - neo) * 0.45)
    return `linear-gradient(${goc + 180}deg, #000 ${neo}%, rgba(0,0,0,.62) ${giua}%, transparent ${het}%)`
  }
  return matSong(hash)
}

function dongBoChon() {
  if (oChon.value) oChon.value.checked = props.chon
}

function khiChon() {
  emit('chon')
  nextTick(dongBoChon)
}

watch(() => props.chon, () => nextTick(dongBoChon))
</script>

<template>
  <article class="card-major h-100" :class="{ 'is-selected': chon, 'card-major--co-anh': anh }">
    <span v-if="anh" class="card-major__image" :style="styleNen" aria-hidden="true" />
    <span class="card-major__shade" aria-hidden="true" />
    <div class="card-major__body">
      <div class="card-major__heading">
        <label class="card-major__check">
          <input
            ref="oChon"
            type="checkbox"
            :checked="chon"
            :aria-label="`Chọn so sánh ${ten}`"
            @change="khiChon"
          />
          <span class="card-major__mark" aria-hidden="true"></span>
        </label>
        <h4 class="card-major__name">{{ ten }}</h4>
      </div>
      <p class="card-major__desc">{{ moTa || 'Chưa có mô tả.' }}</p>
      <dl class="card-major__facts">
        <div class="card-major__fact">
          <dt>Dải lương</dt>
          <dd>{{ mucLuong || '—' }}</dd>
        </div>
        <div class="card-major__fact">
          <dt>Thời gian đào tạo</dt>
          <dd>{{ thoiGian || '—' }}</dd>
        </div>
      </dl>
      <div class="card-major__footer">
        <CustomButton type="primary" plain @click.stop="emit('khamPha')">Khám phá ngay</CustomButton>
      </div>
    </div>
  </article>
</template>

<style scoped>
.card-major {
  position: relative;
  display: flex;
  margin: 0;
  min-height: 168px;
  padding: 14px;
  overflow: hidden;
  border: 1px solid #c5d5cc;
  border-radius: 10px;
  background: linear-gradient(90deg, #cfffe5 0%, #cfe0d7 52%, #f4f8f6 80%);
  box-shadow: 0 6px 16px rgba(28, 43, 35, 0.07);
}

.card-major.is-selected {
  border-color: #0c5c34;
  box-shadow: 0 0 0 2px #0c5c34;
}

.card-major__image {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
  width: 100%;
  background-position: right center;
  background-repeat: no-repeat;
  background-size: cover;
  pointer-events: none;
  -webkit-mask-position: right center;
  mask-position: right center;
  -webkit-mask-repeat: no-repeat;
  mask-repeat: no-repeat;
  -webkit-mask-size: 100% 100%;
  mask-size: 100% 100%;
}

.card-major__shade {
  position: absolute;
  inset: 0;
  z-index: 0;
  background: linear-gradient(90deg, rgba(16, 62, 42, 0.16) 0%, rgba(16, 62, 42, 0.1) 46%, transparent 70%);
  pointer-events: none;
}

.card-major--co-anh :is(.card-major__name, .card-major__desc) {
  border-radius: 4px;
  box-decoration-break: clone;
  -webkit-box-decoration-break: clone;
}

.card-major--co-anh .card-major__desc {
  width: fit-content;
  max-width: 100%;
  padding: 0 4px;
}

.card-major__body {
  position: relative;
  z-index: 1;
  display: flex;
  flex: 1;
  flex-direction: column;
  min-width: 0;
}

.card-major__heading {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.card-major__check {
  position: relative;
  flex: 0 0 auto;
  width: 18px;
  height: 18px;
  margin-top: 2px;
  cursor: pointer;
}

.card-major__check input {
  position: absolute;
  inset: 0;
  margin: 0;
  opacity: 0;
  cursor: pointer;
}

.card-major__mark {
  display: block;
  width: 18px;
  height: 18px;
  border: 2px solid #0c5c34;
  border-radius: 4px;
  background: #fff;
}

.card-major.is-selected .card-major__mark {
  background: #0c5c34;
}

.card-major.is-selected .card-major__mark::after {
  content: '';
  display: block;
  width: 5px;
  height: 9px;
  margin: 1px 0 0 5px;
  border: solid #fff;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.card-major__name {
  flex: 1;
  min-width: 0;
  margin: 0;
  color: #0c5c34;
  font-size: 1.15rem;
  font-weight: 700;
  line-height: 1.35;
}

.card-major__desc {
  display: -webkit-box;
  margin: 8px 0 0;
  overflow: hidden;
  color: #1c2836;
  font-size: 1rem;
  font-weight: 400;
  line-height: 1.5;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}

.card-major__facts {
  display: grid;
  gap: 4px;
  margin: 10px 0 0;
}

.card-major__fact {
  display: grid;
  grid-template-columns: max-content minmax(0, 1fr);
  gap: 8px;
  align-items: baseline;
}

.card-major__fact dt,
.card-major__fact dd {
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.45;
}

.card-major__fact dt {
  color: #31483d;
  font-weight: 600;
}

.card-major__fact dd {
  color: #121a28;
  font-weight: 500;
}

.card-major__footer {
  display: flex;
  justify-content: flex-end;
  margin-top: auto;
  padding-top: 12px;
}

.card-major__footer :deep(.el-button) {
  margin: 0;
}

</style>
