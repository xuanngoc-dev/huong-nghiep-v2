<template>
  <section id="cam-nang" class="landing__section" aria-labelledby="resources-title">
    <div class="container-fluid">
      <div class="landing__head landing-resources__head" data-reveal>
        <div>
          <p class="landing__eyebrow">Cẩm nang hướng nghiệp</p>
          <h2 id="resources-title" class="landing__title">Bài viết và tài nguyên hữu ích</h2>
          <!-- <p class="landing__lead">
            Cập nhật kiến thức về hướng nghiệp, tuyển sinh, phát triển nghề nghiệp và xu hướng thị trường
            lao động.
          </p> -->
        </div>
        <RouterLink class="landing__btn landing__btn--ghost" :to="{ name: 'cam-nang' }">
          Xem tất cả
          <el-icon aria-hidden="true"><Right /></el-icon>
        </RouterLink>
      </div>

      <!-- Cùng kiểu thẻ với trang chọn đối tượng (HuongDiCard): ảnh trái, nội dung phải. -->
      <div class="row g-lp" data-stagger>
        <div v-for="item in articles.slice(0, SO_BAI_TRANG_CHU)" :key="item.id" class="col-12 col-lg-6">
          <TheBaiViet :bai="item" />
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { articles } from '@/data/landing'
import TheBaiViet from '@/components/guest/cam-nang/TheBaiViet.vue'

// Trang chủ chỉ hiện vài bài mới nhất; đầy đủ ở trang /cam-nang.
const SO_BAI_TRANG_CHU = 4
</script>
