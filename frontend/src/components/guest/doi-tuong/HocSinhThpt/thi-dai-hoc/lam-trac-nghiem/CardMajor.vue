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
  /* Bảng màu của card, cùng tông với --app-primary (#1f7a4d). */
  --cm-primary: #1f7a4d;
  --cm-primary-deep: #145c38;
  --cm-surface-start: #e6f3ec;
  --cm-surface-mid: #eef6f1;
  --cm-surface-end: #fbfdfc;
  --cm-border: #d3e4da;
  --cm-text: #1f2d26;
  --cm-text-muted: #4a5f54;
  --cm-shadow: rgba(20, 70, 45, 0.08);
  --cm-shadow-hover: rgba(20, 70, 45, 0.16);

  position: relative;
  display: flex;
  margin: 0;
  min-height: 168px;
  padding: 14px;
  overflow: hidden;
  border: 1px solid var(--cm-border);
  border-radius: 12px;
  background: linear-gradient(
    100deg,
    var(--cm-surface-start) 0%,
    var(--cm-surface-mid) 50%,
    var(--cm-surface-end) 82%
  );
  box-shadow: 0 4px 14px var(--cm-shadow);
  transition:
    transform 0.25s ease,
    box-shadow 0.25s ease,
    border-color 0.25s ease;
}

/* Viền nhấn bên trái, hiện dần khi hover / được chọn. */
.card-major::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  z-index: 2;
  width: 4px;
  background: linear-gradient(180deg, var(--cm-primary), var(--cm-primary-deep));
  transform: scaleY(0);
  transform-origin: top;
  transition: transform 0.3s ease;
}

.card-major:hover,
.card-major:focus-within {
  border-color: color-mix(in srgb, var(--cm-primary) 45%, var(--cm-border));
  box-shadow: 0 12px 28px var(--cm-shadow-hover);
  transform: translateY(-4px);
}

.card-major:hover::before,
.card-major:focus-within::before,
.card-major.is-selected::before {
  transform: scaleY(1);
}

.card-major.is-selected {
  border-color: var(--cm-primary);
  box-shadow:
    0 0 0 2px var(--cm-primary),
    0 8px 22px var(--cm-shadow-hover);
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
  opacity: 0.92;
  transform-origin: right center;
  transition:
    transform 0.5s ease,
    opacity 0.3s ease;
}

.card-major:hover .card-major__image {
  opacity: 1;
  transform: scale(1.05);
}

.card-major__shade {
  position: absolute;
  inset: 0;
  z-index: 0;
  background: linear-gradient(
    90deg,
    rgba(20, 70, 45, 0.08) 0%,
    rgba(20, 70, 45, 0.04) 46%,
    transparent 70%
  );
  pointer-events: none;
  transition: opacity 0.3s ease;
}

.card-major:hover .card-major__shade {
  opacity: 0.6;
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
  border: 2px solid var(--cm-primary);
  border-radius: 4px;
  background: #fff;
  transition:
    background-color 0.2s ease,
    box-shadow 0.2s ease;
}

.card-major__check:hover .card-major__mark,
.card-major__check input:focus-visible + .card-major__mark {
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--cm-primary) 22%, transparent);
}

.card-major.is-selected .card-major__mark {
  background: var(--cm-primary);
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
  color: var(--cm-primary-deep);
  font-size: 1.15rem;
  font-weight: 700;
  line-height: 1.35;
  transition: color 0.2s ease;
}

.card-major:hover .card-major__name {
  color: var(--cm-primary);
}

.card-major__desc {
  display: -webkit-box;
  margin: 8px 0 0;
  overflow: hidden;
  color: var(--cm-text);
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
  color: var(--cm-text-muted);
  font-weight: 600;
}

.card-major__fact dd {
  color: var(--cm-text);
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
  transition:
    background-color 0.25s ease,
    color 0.25s ease,
    border-color 0.25s ease;
}

/* Hover cả card thì nút "Khám phá ngay" chuyển sang dạng đặc. */
.card-major:hover .card-major__footer :deep(.el-button) {
  border-color: var(--cm-primary);
  background-color: var(--cm-primary);
  color: #fff;
}

@media (prefers-reduced-motion: reduce) {
  .card-major,
  .card-major::before,
  .card-major__image {
    transition: none;
  }

  .card-major:hover,
  .card-major:focus-within,
  .card-major:hover .card-major__image {
    transform: none;
  }
}

</style>
