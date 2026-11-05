<script setup>
import { computed } from 'vue'
import anhThpt from '@/assets/guest/thpt.jpg'
import anhSinhVien from '@/assets/guest/sinh-vien.jpg'
import anhThcs from '@/assets/guest/thcs.jpg'
import anhThanhNien from '@/assets/guest/thanh-nien.jpg'
import anhPhuHuynh from '@/assets/guest/phu-huynh.jpg'
import anhNhaTruong from '@/assets/guest/nha-truong.jpg'
import anhNhaTuyenDung from '@/assets/guest/nha-tuyen-dung.jpg'

defineOptions({ name: 'CardNganhDaoTao' })

const ANH_DU_PHONG = [
  anhThpt,
  anhSinhVien,
  anhThcs,
  anhThanhNien,
  anhPhuHuynh,
  anhNhaTruong,
  anhNhaTuyenDung,
]

const props = defineProps({
  ma: { type: String, default: '' },
  nhan: { type: String, default: '' },
  ten: { type: String, default: '' },
  tenTiengAnh: { type: String, default: '' },
  moTa: { type: String, default: '' },
  hinhAnh: { type: String, default: '' },
  hanhDong: { type: String, default: '' },
  khoa: { type: [String, Number], default: '' },
})

const emit = defineEmits(['chon'])

const anh = computed(() => {
  const tuProps = typeof props.hinhAnh === 'string' ? props.hinhAnh.trim() : ''
  if (tuProps) return tuProps
  return ANH_DU_PHONG[bamBanGhi() % ANH_DU_PHONG.length]
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
  const khoa = String(props.khoa || props.ma || '')
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
</script>

<template>
  <article class="card-dao-tao" :class="{ 'card-dao-tao--co-anh': anh }">
    <span v-if="anh" class="card-dao-tao__bg" :style="styleNen" aria-hidden="true" />
    <p class="card-dao-tao__code">{{ ma }}</p>
    <div class="card-dao-tao__main">
      <!-- <p class="card-dao-tao__field">{{ nhan }}</p> -->
      <h3 class="card-dao-tao__name">{{ ten }}</h3>
      <p class="card-dao-tao__en">{{ tenTiengAnh }}</p>
      <p v-if="moTa" class="card-dao-tao__text">{{ moTa }}</p>
    </div>
    <button v-if="hanhDong" type="button" class="card-dao-tao__action" @click="emit('chon')">
      {{ hanhDong }}
    </button>
  </article>
</template>

<style scoped>
.card-dao-tao {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 0;
  min-height: 200px;
  padding: 16px;
  overflow: hidden;
  border: 2px solid #7eae8c;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 10px 24px rgba(31, 122, 77, 0.16);
}

.card-dao-tao__bg {
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

.card-dao-tao--co-anh :is(.card-dao-tao__field, .card-dao-tao__name, .card-dao-tao__en, .card-dao-tao__text) {
  width: fit-content;
  max-width: 100%;
  padding: 0 4px;
  border-radius: 4px;
  /* background-color: rgba(255, 255, 255, 0.88); */
  box-decoration-break: clone;
  -webkit-box-decoration-break: clone;
  text-shadow: 0 0 10px #fff, 0 0 5px #fff;
}

.card-dao-tao__main {
  position: relative;
  z-index: 1;
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
  padding-right: 28px;
}

.card-dao-tao__code {
  position: absolute;
  top: 5px;
  right: -45px;
  z-index: 2;
  width: 118px;
  margin: 0;
  padding: 4px 0;
  background: var(--guest-primary);
  box-shadow: 0 2px 6px rgba(28, 43, 35, 0.2);
  color: #fff;
  font-size: 0.72rem;
  font-weight: 400;
  letter-spacing: 0.04em;
  line-height: 1.2;
  text-align: center;
  transform: rotate(45deg);
}

.card-dao-tao__action {
  position: relative;
  z-index: 1;
  align-self: flex-end;
  border: 0;
  border-radius: 8px;
  padding: 6px 12px;
  background: var(--guest-primary);
  color: #fff;
  font-size: 0.8125rem;
  font-weight: 400;
  line-height: 1.2;
  cursor: pointer;
}

.card-dao-tao__action:hover {
  background: var(--guest-primary-hover);
}

.card-dao-tao__field {
  margin: 0;
  color: var(--guest-primary);
  font-size: 0.78rem;
  font-weight: 400;
  letter-spacing: 0.02em;
  line-height: 1.35;
  text-transform: uppercase;
}

.card-dao-tao__name {
  margin: 0;
  color: #1a66d1;
  font-size: 1.32rem;
  font-weight: 400;
  line-height: 1.35;
}

.card-dao-tao__en,
.card-dao-tao__text {
  margin: 0;
  color: #3b82e0;
  font-size: 1.05rem;
  font-weight: 400;
  line-height: 1.45;
}

.card-dao-tao__text {
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}
</style>
