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

const emit = defineEmits(['chon'])

const anhLoi = ref(false)
const oChon = ref(null)

watch(
  () => props.hinhAnh,
  () => {
    anhLoi.value = false
  },
)

const anh = computed(() => (props.hinhAnh && !anhLoi.value ? props.hinhAnh : anhMacDinh))

function dongBoChon() {
  if (oChon.value) oChon.value.checked = props.chon
}

function khiChon() {
  emit('chon')
  nextTick(dongBoChon)
}

function khiAnhLoi() {
  anhLoi.value = true
}

watch(() => props.chon, () => nextTick(dongBoChon))
</script>

<template>
  <article class="card-major h-100" :class="{ 'is-selected': chon }">
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
    </div>
    <img
      class="card-major__image"
      :src="anh"
      :alt="`Hình minh họa ngành ${ten}`"
      @error="khiAnhLoi"
    />
  </article>
</template>

<style scoped>
.card-major {
  display: flex;
  align-items: stretch;
  gap: 12px;
  margin: 0;
  padding: 14px;
  border: 1px solid #c5d5cc;
  border-radius: 10px;
  background: #fff;
  box-shadow: 0 6px 16px rgba(28, 43, 35, 0.07);
}

.card-major.is-selected {
  border-color: #0c5c34;
  box-shadow: 0 0 0 2px #0c5c34;
}

.card-major__body {
  flex: 1;
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

.card-major__image {
  flex: 0 0 118px;
  width: 118px;
  align-self: stretch;
  min-height: 118px;
  object-fit: cover;
  border-radius: 8px;
  background: #e7edf2;
}

@media (max-width: 480px) {
  .card-major {
    flex-direction: column-reverse;
  }

  .card-major__image {
    flex-basis: auto;
    width: 100%;
    height: 140px;
  }
}
</style>
