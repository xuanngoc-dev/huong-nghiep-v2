<script setup>
import { steps } from '@/data/landing'
</script>

<template>
  <section id="cach-hoat-dong" class="landing__section" aria-labelledby="steps-title">
    <div class="container-fluid">
      <div class="landing__head landing__head--center" data-reveal>
        <p class="landing__eyebrow">Quy trình rõ ràng</p>
        <h2 id="steps-title" class="landing__title">4 bước kiến tạo tương lai của bạn</h2>
        <p class="landing__lead">
          Một lộ trình đơn giản giúp bạn chuyển từ băn khoăn sang quyết định có căn cứ.
        </p>
      </div>

      <ol class="landing-steps__track row g-lp row-cols-1 row-cols-md-2 row-cols-lg-4 list-unstyled mb-0" data-stagger>
        <li v-for="item in steps" :key="item.step" class="col">
          <div class="landing-steps__item h-100">
            <div class="landing-steps__badge" aria-hidden="true">
              <el-icon><component :is="item.icon" /></el-icon>
            </div>
            <span class="landing-steps__num">Bước {{ item.step }}</span>
            <h3>{{ item.title }}</h3>
            <p>{{ item.text }}</p>
          </div>
        </li>
      </ol>
    </div>
  </section>
</template>
