<template>
  <section id="tinh-nang" class="landing__section" aria-labelledby="features-title">
    <div class="container-fluid">
      <div class="landing__head row g-lp align-items-end" data-reveal>
        <div class="col-lg-7">
          <p class="landing__eyebrow">Tính năng cốt lõi</p>
          <h2 id="features-title" class="landing__title">Công cụ đồng hành trên mọi bước định hướng</h2>
        </div>
      </div>

      <div class="row g-lp" data-stagger>
        <div v-for="(item, index) in features" :key="item.id" :class="colClass(index)">
          <RouterLink :to="item.to" class="lp-media-card landing-features__card">
            <LandingImage :src="item.image" :alt="item.alt" ratio="auto" class="landing-features__bg" />
            <div class="landing-features__content">
              <span class="landing-features__icon" aria-hidden="true">
                <el-icon><component :is="item.icon" /></el-icon>
              </span>
              <h3>{{ item.title }}</h3>
              <p>{{ item.description }}</p>
              <span class="lp-link">Tìm hiểu thêm <el-icon aria-hidden="true"><Right /></el-icon></span>
            </div>
          </RouterLink>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { features } from '@/data/landing'
import LandingImage from './LandingImage.vue'

// Bố cục so le trên desktop: thẻ 1, 4, 5 rộng gấp đôi.
const WIDE = [0, 3, 4]

function colClass(index) {
  if (index === 0) return 'col-12 col-lg-8'
  return WIDE.includes(index) ? 'col-md-6 col-lg-8' : 'col-md-6 col-lg-4'
}
</script>
