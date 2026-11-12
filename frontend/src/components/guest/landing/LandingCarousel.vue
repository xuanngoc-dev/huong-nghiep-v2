<template>
  <div
    class="lp-carousel"
    :class="`lp-carousel--${tone}`"
    role="region"
    aria-roledescription="carousel"
    :aria-label="label"
    :style="cssVars"
    @mouseenter="hovered = true"
    @mouseleave="hovered = false"
    @focusin="focused = true"
    @focusout="onFocusOut"
  >
    <div ref="track" class="lp-carousel__track" tabindex="0" @scroll.passive="onScroll" @keydown="onKeydown">
      <div
        v-for="(item, index) in items"
        :key="item[itemKey] ?? index"
        class="lp-carousel__slide"
        role="group"
        aria-roledescription="slide"
        :aria-label="`${index + 1} / ${items.length}`"
      >
        <slot :item="item" :index="index" />
      </div>
    </div>

    <div v-if="pageCount > 1" class="lp-carousel__controls">
      <div class="lp-carousel__dots">
        <button
          v-for="page in pageCount"
          :key="page"
          type="button"
          class="lp-carousel__dot"
          :class="{ 'is-active': page - 1 === active }"
          :aria-label="`Đến vị trí ${page}`"
          :aria-current="page - 1 === active ? 'true' : undefined"
          @click="goTo(page - 1)"
        ></button>
      </div>
      <div class="lp-carousel__nav">
        <button
          v-if="canAutoplay"
          type="button"
          class="lp-carousel__btn"
          :aria-label="stopped ? 'Tiếp tục tự chạy' : 'Tạm dừng tự chạy'"
          @click="stopped = !stopped"
        >
          <el-icon aria-hidden="true"><component :is="stopped ? 'VideoPlay' : 'VideoPause'" /></el-icon>
        </button>
        <button type="button" class="lp-carousel__btn" aria-label="Trước" @click="prev">
          <el-icon aria-hidden="true"><ArrowLeft /></el-icon>
        </button>
        <button type="button" class="lp-carousel__btn" aria-label="Tiếp theo" @click="next">
          <el-icon aria-hidden="true"><ArrowRight /></el-icon>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'

// Carousel nhẹ dựa trên CSS scroll-snap: vuốt trên mobile là native, JS chỉ lo nút điều hướng,
// chấm phân trang và autoplay.
const props = defineProps({
  items: { type: Array, required: true },
  itemKey: { type: String, default: 'id' },
  label: { type: String, required: true },
  perView: { type: Object, default: () => ({ base: 1, sm: 2, lg: 3 }) },
  autoplay: { type: Number, default: 0 },
  tone: { type: String, default: 'light' },
})

const track = ref(null)
const active = ref(0)
const visible = ref(1)
const hovered = ref(false)
const focused = ref(false)
const stopped = ref(false)
const inView = ref(false)
const pageVisible = ref(true)
const reduceMotion = ref(false)

const pageCount = computed(() => Math.max(props.items.length - visible.value + 1, 1))
const canAutoplay = computed(() => props.autoplay > 0 && !reduceMotion.value && pageCount.value > 1)
const running = computed(
  () => canAutoplay.value && !stopped.value && !hovered.value && !focused.value && inView.value && pageVisible.value,
)

// Số thẻ hiển thị theo breakpoint Bootstrap; breakpoint không khai báo kế thừa giá trị nhỏ hơn.
const BREAKPOINTS = ['base', 'sm', 'md', 'lg', 'xl', 'xxl']

const cssVars = computed(() => {
  let last = 1
  return Object.fromEntries(
    BREAKPOINTS.map((bp) => {
      last = props.perView[bp] ?? last
      return [`--pv-${bp}`, last]
    }),
  )
})

function step() {
  const el = track.value
  const slide = el?.firstElementChild
  if (!slide) return 0
  const gap = parseFloat(getComputedStyle(el).columnGap) || 0
  return slide.offsetWidth + gap
}

function measure() {
  const size = step()
  if (!size) return
  visible.value = Math.max(Math.round((track.value.clientWidth + 1) / size), 1)
  active.value = Math.min(Math.round(track.value.scrollLeft / size), pageCount.value - 1)
}

function goTo(index) {
  const total = pageCount.value
  const next = ((index % total) + total) % total
  track.value?.scrollTo({ left: next * step(), behavior: reduceMotion.value ? 'auto' : 'smooth' })
  active.value = next
}

const next = () => goTo(active.value + 1)
const prev = () => goTo(active.value - 1)

let scrollFrame = 0
function onScroll() {
  cancelAnimationFrame(scrollFrame)
  scrollFrame = requestAnimationFrame(measure)
}

function onKeydown(event) {
  if (event.key === 'ArrowRight') {
    event.preventDefault()
    next()
  } else if (event.key === 'ArrowLeft') {
    event.preventDefault()
    prev()
  }
}

function onFocusOut(event) {
  if (!event.currentTarget.contains(event.relatedTarget)) focused.value = false
}

let timer = null
watch(running, (value) => {
  clearInterval(timer)
  if (value) timer = setInterval(next, props.autoplay)
})

let resizeObserver = null
let viewObserver = null
const onVisibility = () => {
  pageVisible.value = !document.hidden
}

onMounted(() => {
  reduceMotion.value = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  measure()
  resizeObserver = new ResizeObserver(measure)
  resizeObserver.observe(track.value)
  viewObserver = new IntersectionObserver(([entry]) => {
    inView.value = entry.isIntersecting
  })
  viewObserver.observe(track.value)
  document.addEventListener('visibilitychange', onVisibility)
})

onUnmounted(() => {
  clearInterval(timer)
  cancelAnimationFrame(scrollFrame)
  resizeObserver?.disconnect()
  viewObserver?.disconnect()
  document.removeEventListener('visibilitychange', onVisibility)
})
</script>
