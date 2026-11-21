<template>
  <section id="to-chuc" class="landing__section landing__section--alt" aria-labelledby="institutions-title">
    <div class="container-fluid">
      <div class="landing__head row g-lp align-items-end" data-reveal>
        <div class="col-lg-7">
          <p class="landing__eyebrow">Dành cho tổ chức</p>
          <h2 id="institutions-title" class="landing__title">Giải pháp cho nhà trường và nhà tuyển dụng</h2>
        </div>
      </div>

      <!-- Cùng bố cục thẻ với trang chọn đối tượng (HuongDiCard): ảnh trái, nội dung phải. -->
      <div class="row g-lp">
        <div class="col-lg-6">
          <article class="landing-institutions__card h-100" data-reveal="left">
            <div class="landing-institutions__media">
              <img :src="nhaTruongImage" alt="Ban giám hiệu và giáo viên họp bàn kế hoạch hướng nghiệp" loading="lazy" decoding="async" />
            </div>
            <div class="landing-institutions__body">
              <p class="landing__eyebrow">Nhà trường</p>
              <h3>Nâng cao hiệu quả hướng nghiệp học đường</h3>
              <ul>
                <li v-for="item in schoolBenefits" :key="item">{{ item }}</li>
              </ul>
              <!-- Chưa làm tính năng cho nhà trường (trước đây: RouterLink tới 'nha-truong', "Tìm hiểu giải pháp nhà trường"). -->
              <span class="landing__btn is-disabled" aria-disabled="true">Sắp ra mắt</span>
            </div>
          </article>
        </div>

        <div class="col-lg-6">
          <article class="landing-institutions__card h-100" data-reveal="right">
            <div class="landing-institutions__media">
              <img :src="nhaTuyenDungImage" alt="Nhà tuyển dụng trao đổi cùng ứng viên trẻ" loading="lazy" decoding="async" />
            </div>
            <div class="landing-institutions__body">
              <p class="landing__eyebrow">Nhà tuyển dụng</p>
              <h3>Kết nối với học sinh, sinh viên đang chọn nghề</h3>
              <ul>
                <li v-for="item in employerBenefits" :key="item">{{ item }}</li>
              </ul>
              <!-- Chưa làm tính năng cho nhà tuyển dụng (trước đây: RouterLink tới 'nha-tuyen-dung', "Kết nối với nền tảng"). -->
              <span class="landing__btn is-disabled" aria-disabled="true">Sắp ra mắt</span>
            </div>
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
