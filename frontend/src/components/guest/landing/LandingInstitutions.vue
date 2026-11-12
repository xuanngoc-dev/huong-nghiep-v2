<template>
  <section id="to-chuc" class="landing__section landing__section--alt" aria-labelledby="institutions-title">
    <div class="container-fluid">
      <div class="landing__head row g-lp align-items-end" data-reveal>
        <div class="col-lg-7">
          <p class="landing__eyebrow">Dành cho tổ chức</p>
          <h2 id="institutions-title" class="landing__title">Giải pháp cho nhà trường và nhà tuyển dụng</h2>
        </div>
        <!-- <p class="landing__lead col-lg-5">
          Kết nối giáo dục với thế giới việc làm, hỗ trợ tư vấn học sinh và lan tỏa cơ hội nghề nghiệp
          thực tế.
        </p> -->
      </div>

      <div class="row g-lp">
        <div class="col-md-6">
          <article class="landing-institutions__card landing-institutions__card--school h-100" data-reveal="left">
            <div class="landing-institutions__media">
              <img :src="nhaTruongImage" alt="Ban giám hiệu và giáo viên họp bàn kế hoạch hướng nghiệp" loading="lazy" decoding="async" />
            </div>
            <p class="landing__eyebrow">Nhà trường</p>
            <h3 class="h4">Nâng cao hiệu quả hướng nghiệp học đường</h3>
            <ul>
              <li v-for="item in schoolBenefits" :key="item">{{ item }}</li>
            </ul>
            <RouterLink class="landing__btn landing__btn--primary" :to="{ name: 'nha-truong' }">
              Tìm hiểu giải pháp nhà trường
            </RouterLink>
          </article>
        </div>

        <div class="col-md-6">
          <article class="landing-institutions__card landing-institutions__card--employer h-100" data-reveal="right">
            <div class="landing-institutions__media">
              <img :src="nhaTuyenDungImage" alt="Nhà tuyển dụng trao đổi cùng ứng viên trẻ" loading="lazy" decoding="async" />
            </div>
            <p class="landing__eyebrow">Nhà tuyển dụng</p>
            <h3 class="h4">Đồng hành kiến tạo nguồn nhân lực tương lai</h3>
            <ul>
              <li v-for="item in employerBenefits" :key="item">{{ item }}</li>
            </ul>
            <RouterLink class="landing__btn landing__btn--soft" :to="{ name: 'nha-tuyen-dung' }">
              Kết nối với nền tảng
            </RouterLink>
          </article>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import nhaTruongImage from '@/assets/guest/nha-truong.jpg'
import nhaTuyenDungImage from '@/assets/guest/nha-tuyen-dung.jpg'
import { employerBenefits, schoolBenefits } from '@/data/landing'
</script>
