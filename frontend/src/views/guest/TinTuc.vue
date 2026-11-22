<template>
  <div class="landing">
    <section class="landing__section" aria-labelledby="tin-tuc-title">
      <div class="container-fluid">
        <div class="landing__head">
          <p class="landing__eyebrow">Tin tức</p>
          <h1 id="tin-tuc-title" class="landing__title">Tin tức tuyển sinh và hướng nghiệp</h1>
          <p class="landing__lead">
            Cập nhật thông tin tuyển sinh, chính sách giáo dục và thị trường lao động mới nhất.
          </p>
        </div>

        <!-- Chưa có dữ liệu tin tức: hiện thông báo, bổ sung danh sách tin sau. -->
        <div class="landing-explore__panel">
          <KhongCoDuLieu text="Tin tức đang được cập nhật." />
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import KhongCoDuLieu from '@/components/guest/chung/KhongCoDuLieu.vue'
import '@/components/guest/landing/landing.css'

defineOptions({ name: 'TinTuc' })
</script>
