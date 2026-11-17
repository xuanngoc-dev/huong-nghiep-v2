<template>
  <span class="meo-nho">
    <strong>Mẹo nhỏ:</strong>
    <span class="visually-hidden" aria-live="polite">{{ meo }}</span>
    <!-- Câu đầy đủ ẩn giữ chỗ để khung không giật khi gõ; trình đọc màn hình chỉ đọc câu đầy đủ ở trên. -->
    <span class="meo-nho__khung" aria-hidden="true">
      <span class="meo-nho__giu-cho">{{ meo }}</span>
      <span class="meo-nho__go">{{ daGo }}<span v-if="dangGo" class="meo-nho__con-tro" /></span>
    </span>
  </span>
</template>

<script setup>
/** Mẹo nhỏ ở trang Trường phù hợp: gõ từng ký tự, giữ nguyên 5 giây rồi đổi sang mẹo ngẫu nhiên khác. */
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { MEO_TIM_TRUONG, meoNgauNhien } from '@/data/meoTimTruong'

const GIU_MS = 5000
const GO_MS = 30

const meo = ref('')
const daGo = ref('')
const dangGo = ref(false)
let hen = null

function datHen(fn, ms) {
  clearTimeout(hen)
  hen = setTimeout(fn, ms)
}

function hienMeo(noiDung) {
  meo.value = noiDung
  // Người dùng chọn giảm chuyển động: hiện ngay cả câu, không gõ.
  if (globalThis.matchMedia?.('(prefers-reduced-motion: reduce)').matches) {
    daGo.value = noiDung
    datHen(() => hienMeo(meoNgauNhien(MEO_TIM_TRUONG, noiDung)), GIU_MS)
    return
  }
  daGo.value = ''
  dangGo.value = true
  const go = () => {
    daGo.value = noiDung.slice(0, daGo.value.length + 1)
    if (daGo.value.length < noiDung.length) {
      datHen(go, GO_MS)
    } else {
      dangGo.value = false
      datHen(() => hienMeo(meoNgauNhien(MEO_TIM_TRUONG, noiDung)), GIU_MS)
    }
  }
  datHen(go, GO_MS)
}

onMounted(() => hienMeo(meoNgauNhien()))
onBeforeUnmount(() => clearTimeout(hen))
</script>

<style scoped>
.meo-nho {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 4px;
  text-align: left;
}

.meo-nho__khung {
  display: inline-grid;
  flex: 1 1 0;
  min-width: min(100%, 240px);
}

.meo-nho__giu-cho,
.meo-nho__go {
  grid-area: 1 / 1;
}

.meo-nho__giu-cho {
  visibility: hidden;
}

.meo-nho__con-tro {
  display: inline-block;
  width: 2px;
  height: 1em;
  margin-left: 1px;
  background: currentColor;
  vertical-align: text-bottom;
  animation: meo-nho-nhay 0.8s steps(1) infinite;
}

@keyframes meo-nho-nhay {
  50% {
    opacity: 0;
  }
}
</style>
