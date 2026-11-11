<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { audiences, heroSlides, hollandGroups, steps, studyPaths } from '@/data/landing'
import LandingCounter from './LandingCounter.vue'

const INTERVAL = 6500

const active = ref(0)
const hovered = ref(false)
const focused = ref(false)
const stopped = ref(false)
const pageHidden = ref(false)
const reduceMotion = ref(false)

const paused = computed(
  () => stopped.value || hovered.value || focused.value || pageHidden.value || reduceMotion.value,
)

const stats = [
  { value: audiences.length, label: 'Nhóm đối tượng được hỗ trợ' },
  { value: hollandGroups.length, label: 'Nhóm tính cách Holland' },
  { value: studyPaths.length, label: 'Lộ trình sau tốt nghiệp THPT' },
  { value: steps.length, label: 'Bước định hướng rõ ràng' },
]

function goTo(index) {
  const total = heroSlides.length
  active.value = ((index % total) + total) % total
}

const next = () => goTo(active.value + 1)
const prev = () => goTo(active.value - 1)

function linkTo(link) {
  return link.hash ? { ...link.to, hash: link.hash } : link.to
}

function onKeydown(event) {
  if (event.key === 'ArrowRight') next()
  else if (event.key === 'ArrowLeft') prev()
}

function onFocusOut(event) {
  if (!event.currentTarget.contains(event.relatedTarget)) focused.value = false
}

let startX = null
function onPointerDown(event) {
  startX = event.clientX
}
function onPointerUp(event) {
  if (startX === null) return
  const delta = event.clientX - startX
  startX = null
  if (Math.abs(delta) < 50) return
  delta < 0 ? next() : prev()
}

const onVisibility = () => {
  pageHidden.value = document.hidden
}

onMounted(() => {
  reduceMotion.value = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  document.addEventListener('visibilitychange', onVisibility)
})

onUnmounted(() => {
  document.removeEventListener('visibilitychange', onVisibility)
})
</script>

<template>
  <section class="landing-hero" aria-labelledby="landing-hero-title">
    <h1 id="landing-hero-title" class="visually-hidden">
      Định hướng nghề – Nền tảng định hướng nghề nghiệp cho học sinh, sinh viên, phụ huynh và tổ chức
    </h1>

    <div class="container-fluid">
      <div
        class="landing-hero__slider"
        :class="{ 'is-paused': paused }"
        :style="{ '--hero-interval': `${INTERVAL}ms` }"
        role="region"
        aria-roledescription="carousel"
        aria-label="Nội dung nổi bật"
        @mouseenter="hovered = true"
        @mouseleave="hovered = false"
        @focusin="focused = true"
        @focusout="onFocusOut"
        @keydown="onKeydown"
        @pointerdown="onPointerDown"
        @pointerup="onPointerUp"
        @pointercancel="startX = null"
      >
        <div
          v-for="(slide, index) in heroSlides"
          :key="slide.id"
          class="landing-hero__slide"
          :class="{ 'is-active': index === active }"
          role="group"
          aria-roledescription="slide"
          :aria-label="`${index + 1} / ${heroSlides.length}: ${slide.eyebrow}`"
          :aria-hidden="index !== active"
          :inert="index !== active"
        >
          <img
            class="landing-hero__bg"
            :src="slide.image"
            :alt="slide.alt"
            :loading="index === 0 ? 'eager' : 'lazy'"
            :fetchpriority="index === 0 ? 'high' : undefined"
            decoding="async"
            draggable="false"
          />
          <div class="landing-hero__content">
            <p class="landing-hero__eyebrow">{{ slide.eyebrow }}</p>
            <h2 class="landing-hero__headline">{{ slide.title }}</h2>
            <p class="landing-hero__text">{{ slide.text }}</p>
            <div class="landing-hero__actions">
              <RouterLink class="landing__btn landing__btn--primary" :to="linkTo(slide.primary)">
                {{ slide.primary.label }}
                <el-icon aria-hidden="true"><Right /></el-icon>
              </RouterLink>
              <RouterLink class="landing__btn landing__btn--glass" :to="linkTo(slide.secondary)">
                {{ slide.secondary.label }}
              </RouterLink>
            </div>
          </div>
        </div>

        <div class="landing-hero__controls">
          <div class="landing-hero__tabs">
            <button
              v-for="(slide, index) in heroSlides"
              :key="slide.id"
              type="button"
              class="landing-hero__tab"
              :class="{ 'is-active': index === active }"
              :aria-label="`Chuyển đến: ${slide.eyebrow}`"
              :aria-current="index === active ? 'true' : undefined"
              @click="goTo(index)"
            >
              <span class="landing-hero__tab-label">{{ slide.eyebrow }}</span>
              <span class="landing-hero__tab-bar">
                <span
                  v-if="index === active"
                  class="landing-hero__tab-fill"
                  @animationend="next"
                ></span>
              </span>
            </button>
          </div>
          <div class="landing-hero__nav">
            <button
              v-if="!reduceMotion"
              type="button"
              class="landing-hero__btn"
              :aria-label="stopped ? 'Tiếp tục tự chuyển' : 'Tạm dừng tự chuyển'"
              @click="stopped = !stopped"
            >
              <el-icon aria-hidden="true"><component :is="stopped ? 'VideoPlay' : 'VideoPause'" /></el-icon>
            </button>
            <button type="button" class="landing-hero__btn" aria-label="Slide trước" @click="prev">
              <el-icon aria-hidden="true"><ArrowLeft /></el-icon>
            </button>
            <button type="button" class="landing-hero__btn" aria-label="Slide tiếp theo" @click="next">
              <el-icon aria-hidden="true"><ArrowRight /></el-icon>
            </button>
          </div>
        </div>
      </div>

      <ul
        class="landing-hero__stats row g-lp row-cols-2 row-cols-lg-4 list-unstyled"
        aria-label="Nền tảng trong con số"
        data-stagger
      >
        <li v-for="item in stats" :key="item.label" class="col">
          <div class="landing-hero__stat h-100">
            <strong><LandingCounter :value="item.value" /></strong>
            <span>{{ item.label }}</span>
          </div>
        </li>
      </ul>
    </div>
  </section>
</template>
