<template>
  <section id="lo-trinh-hoc" class="landing__section landing__section--alt" aria-labelledby="study-paths-title">
    <div class="container-fluid">
      <div class="landing__head row align-items-end" data-reveal>
        <div class="col-lg-7">
          <p class="landing__eyebrow">Trường học & ngành đào tạo</p>
          <h2 id="study-paths-title" class="landing__title">Chọn con đường phù hợp sau tốt nghiệp</h2>
        </div>
        <!-- <p class="landing__lead col-lg-5">
          Đại học, du học, học nghề, đi làm hay khởi nghiệp — mỗi lựa chọn đều có lộ trình và công cụ
          tra cứu riêng giúp bạn tự tin quyết định.
        </p> -->
      </div>

      <div data-reveal>
        <LandingCarousel
          :items="studyPaths"
          label="Các lộ trình học tập và nghề nghiệp"
          :per-view="{ base: 1.1, sm: 2, md: 3, lg: 4, xxl: 5 }"
        >
          <template #default="{ item }">
            <RouterLink :to="item.to" class="lp-media-card landing-paths__card">
              <LandingImage :src="item.image" :fallback="item.fallback" :alt="item.alt" ratio="3 / 2">
                <span class="lp-tag lp-tag--float">{{ item.tag }}</span>
              </LandingImage>
              <div class="lp-media-card__body">
                <h3>{{ item.title }}</h3>
                <p>{{ item.text }}</p>
                <span class="lp-link">Xem lộ trình <el-icon aria-hidden="true"><Right /></el-icon></span>
              </div>
            </RouterLink>
          </template>
        </LandingCarousel>
      </div>
    </div>
  </section>
</template>

<script setup>
import { studyPaths } from '@/data/landing'
import LandingCarousel from './LandingCarousel.vue'
import LandingImage from './LandingImage.vue'
</script>
