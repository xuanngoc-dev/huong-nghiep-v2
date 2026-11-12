<template>
  <section id="cau-chuyen" class="landing__section landing__section--alt" aria-labelledby="testimonials-title">
    <div class="container-fluid">
      <div class="landing__head row g-lp align-items-end" data-reveal>
        <div class="col-lg-7">
          <p class="landing__eyebrow">Câu chuyện minh họa</p>
          <h2 id="testimonials-title" class="landing__title">Người dùng nói gì về hành trình định hướng</h2>
        </div>
        <!-- <p class="landing__lead col-lg-5">
          Các nội dung dưới đây là ví dụ minh họa trải nghiệm, không phải đánh giá đã xác minh từ khách
          hàng.
        </p> -->
      </div>

      <div data-reveal>
        <LandingCarousel
          :items="testimonials"
          label="Câu chuyện minh họa từ người dùng"
          :per-view="{ base: 1, md: 2, xxl: 3 }"
          :autoplay="7000"
        >
          <template #default="{ item }">
            <article class="landing-testimonials__card row g-0">
              <div class="landing-testimonials__media col-lg-5">
                <img :src="item.image" :alt="`Bối cảnh minh họa: ${item.role}`" loading="lazy" decoding="async" />
              </div>
              <div class="landing-testimonials__body col-lg-7">
                <span class="landing-testimonials__note">{{ item.note }}</span>
                <blockquote>“{{ item.quote }}”</blockquote>
                <footer class="landing-testimonials__meta">
                  <div class="landing-testimonials__avatar" aria-hidden="true">{{ initials(item.name) }}</div>
                  <div>
                    <strong>{{ item.name }}</strong>
                    <span>{{ item.role }}</span>
                  </div>
                </footer>
              </div>
            </article>
          </template>
        </LandingCarousel>
      </div>
    </div>
  </section>
</template>

<script setup>
import { testimonials } from '@/data/landing'
import LandingCarousel from './LandingCarousel.vue'

function initials(name) {
  return String(name || '')
    .split(' ')
    .filter(Boolean)
    .slice(-2)
    .map((part) => part[0])
    .join('')
    .toUpperCase()
}
</script>
