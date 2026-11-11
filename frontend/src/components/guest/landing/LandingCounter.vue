<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

const props = defineProps({
  value: { type: Number, required: true },
  suffix: { type: String, default: '' },
  duration: { type: Number, default: 1400 },
})

const root = ref(null)
const display = ref(0)
let observer = null
let frame = 0

function run() {
  const start = performance.now()
  const tick = (now) => {
    const progress = Math.min((now - start) / props.duration, 1)
    const eased = 1 - Math.pow(1 - progress, 3)
    display.value = Math.round(props.value * eased)
    if (progress < 1) frame = requestAnimationFrame(tick)
  }
  frame = requestAnimationFrame(tick)
}

onMounted(() => {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    display.value = props.value
    return
  }
  observer = new IntersectionObserver(
    ([entry]) => {
      if (!entry.isIntersecting) return
      observer?.disconnect()
      run()
    },
    { threshold: 0.6 },
  )
  observer.observe(root.value)
})

onUnmounted(() => {
  observer?.disconnect()
  cancelAnimationFrame(frame)
})
</script>

<template>
  <span ref="root" class="lp-counter">
    <span aria-hidden="true">{{ display }}{{ suffix }}</span>
    <span class="visually-hidden">{{ value }}{{ suffix }}</span>
  </span>
</template>
