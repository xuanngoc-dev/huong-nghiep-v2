<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  ssid: { type: String, required: true },
  buoc: { type: Array, required: true },
  hienTai: { type: [Number, String], required: true },
})

const router = useRouter()

function trangThai(step) {
  if (String(step.id) === String(props.hienTai)) return 'dang'
  if (step.xong || String(props.hienTai) === 'ket-qua') return 'xong'
  return 'chua'
}

function biKhoa(index) {
  const step = props.buoc[index]
  if (!step || String(step.id) === String(props.hienTai)) return false
  if (step.id === 'ket-qua') return props.buoc.slice(0, index).some((item) => !item.xong)
  const hienTai = props.buoc.findIndex((item) => String(item.id) === String(props.hienTai))
  if (hienTai < 0 || index <= hienTai) return false
  return !props.buoc[hienTai]?.xong
}

function mo(step, index) {
  if (biKhoa(index) || String(step.id) === String(props.hienTai)) return
  if (step.id === 'ket-qua') {
    router.push({ name: 'thpt-thi-dai-hoc-ket-qua', params: { ssid: props.ssid } })
    return
  }
  router.push({
    name: 'thpt-thi-dai-hoc-lam-trac-nghiem',
    params: { ssid: props.ssid, loaiCauHoiId: step.id },
  })
}
</script>

<template>
  <ol class="holland-path quiz-steps">
    <li
      v-for="(step, index) in buoc"
      :key="step.id"
      class="holland-path__item"
      :class="{
        'is-current': trangThai(step) === 'dang',
        'is-done': trangThai(step) === 'xong',
      }"
    >
      <button type="button" class="holland-path__link" :disabled="biKhoa(index)" @click="mo(step, index)">
        <span class="holland-path__index">
          <template v-if="trangThai(step) === 'dang'">
            <span class="quiz-ripple" aria-hidden="true" />
            <span class="quiz-ripple quiz-ripple--mid" aria-hidden="true" />
            <span class="quiz-ripple quiz-ripple--late" aria-hidden="true" />
          </template>
          {{ index + 1 }}
        </span>
        <span class="holland-path__label">{{ step.ten }}</span>
      </button>
    </li>
  </ol>
</template>

<style scoped>
.holland-path__link {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 8px 0 0;
  border: 0;
  background: transparent;
  color: inherit;
}

.holland-path__link:disabled {
  cursor: not-allowed;
}

ol.quiz-steps.holland-path {
  padding-top: 10px;
}

ol.quiz-steps.holland-path::before {
  top: 35px;
}

ol.quiz-steps .holland-path__item {
  transition: flex 0.55s cubic-bezier(0.22, 1, 0.36, 1);
}

ol.quiz-steps .holland-path__item.is-current {
  flex: 1.35;
}

ol.quiz-steps .holland-path__index {
  position: relative;
  z-index: 1;
  width: 36px;
  height: 36px;
  overflow: visible;
  transition:
    transform 0.55s cubic-bezier(0.22, 1, 0.36, 1),
    background-color 0.45s ease,
    border-color 0.45s ease,
    color 0.45s ease,
    box-shadow 0.55s ease;
}

ol.quiz-steps .holland-path__item.is-current .holland-path__index {
  transform: scale(1.18);
  box-shadow: 0 0 0 7px rgba(var(--guest-primary-rgb), 0.14);
}

ol.quiz-steps .holland-path__item.is-done .holland-path__index {
  border-color: var(--guest-primary);
  background: #d9f3dc;
  color: #1c2b23;
  font-weight: 700;
}

ol.quiz-steps .holland-path__label {
  font-weight: 500;
  transition: color 0.45s ease, font-weight 0.45s ease;
}

ol.quiz-steps .holland-path__item.is-done .holland-path__label {
  color: #1c2b23;
  font-weight: 700;
}

.quiz-ripple {
  position: absolute;
  inset: -2px;
  border: 2px solid rgba(var(--guest-primary-rgb), 0.45);
  border-radius: 50%;
  pointer-events: none;
  animation: quiz-ripple 2.8s cubic-bezier(0.22, 0.61, 0.36, 1) infinite;
}

.quiz-ripple--mid {
  animation-delay: 0.9s;
}

.quiz-ripple--late {
  animation-delay: 1.8s;
}

@keyframes quiz-ripple {
  0% {
    transform: scale(0.92);
    opacity: 0.55;
  }

  100% {
    transform: scale(2.45);
    opacity: 0;
  }
}

@media (max-width: 767px) {
  ol.quiz-steps.holland-path {
    display: flex;
    grid-template-columns: none;
  }

  ol.quiz-steps.holland-path::before {
    display: block;
  }
}

@media (prefers-reduced-motion: reduce) {
  .quiz-ripple {
    animation: none;
    opacity: 0;
  }

  ol.quiz-steps .holland-path__index,
  ol.quiz-steps .holland-path__item,
  ol.quiz-steps .holland-path__label {
    transition: none;
  }
}
</style>
