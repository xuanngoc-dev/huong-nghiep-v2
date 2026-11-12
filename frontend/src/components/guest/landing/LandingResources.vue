<template>
  <section id="cam-nang" class="landing__section" aria-labelledby="resources-title">
    <div class="container-fluid">
      <div class="landing__head row g-lp align-items-end" data-reveal>
        <div class="col-lg-7">
          <p class="landing__eyebrow">Cẩm nang hướng nghiệp</p>
          <h2 id="resources-title" class="landing__title">Bài viết và tài nguyên hữu ích</h2>
        </div>
        <p class="landing__lead col-lg-5">
          Cập nhật kiến thức về hướng nghiệp, tuyển sinh, phát triển nghề nghiệp và xu hướng thị trường
          lao động.
        </p>
      </div>

      <div class="row g-lp row-cols-1 row-cols-sm-2 row-cols-xl-4" data-stagger>
        <div v-for="item in articles" :key="item.id" class="col">
          <article class="lp-media-card landing-resources__card">
            <LandingImage :src="item.image" :alt="item.title" ratio="16 / 10" />
            <div class="landing-resources__body">
              <span class="landing-resources__cat">{{ item.category }}</span>
              <h3>{{ item.title }}</h3>
              <p>{{ item.summary }}</p>
              <time :datetime="item.date">{{ formatDate(item.date) }}</time>
            </div>
          </article>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { articles } from '@/data/landing'
import LandingImage from './LandingImage.vue'

function formatDate(value) {
  const [year, month, day] = String(value).split('-')
  if (!year || !month || !day) return value
  return `${day}/${month}/${year}`
}
</script>
