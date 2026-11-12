<template>
  <footer class="landing-footer">
    <div class="container-fluid">
      <div class="row g-lp">
        <div class="col-lg-4">
          <RouterLink class="landing-footer__brand" :to="{ name: 'home' }">Định hướng nghề</RouterLink>
          <p class="landing-footer__desc">
            Nền tảng EdTech hỗ trợ khám phá bản thân, lựa chọn ngành học và kiến tạo lộ trình sự nghiệp
            phù hợp.
          </p>
          <div class="landing-footer__social" aria-label="Mạng xã hội">
            <a href="#" aria-label="Facebook"><el-icon><ChatDotRound /></el-icon></a>
            <a href="#" aria-label="YouTube"><el-icon><VideoCamera /></el-icon></a>
            <a href="mailto:hotro@dinhhuongnghe.vn" aria-label="Email">
              <el-icon><Message /></el-icon>
            </a>
          </div>
          <p class="mt-3 mb-0 small">
            Liên hệ: hotro@dinhhuongnghe.vn<br />
            Hotline: 1900 0000 (giả lập)
          </p>
        </div>

        <div class="col-lg-8">
          <div class="row g-lp">
            <div v-for="column in footerColumns" :key="column.title" class="col-6 col-md-4">
              <h3>{{ column.title }}</h3>
              <ul>
                <li v-for="link in column.links" :key="link.label">
                  <a v-if="link.href" :href="link.href">{{ link.label }}</a>
                  <RouterLink v-else :to="link.hash ? { ...link.to, hash: link.hash } : link.to">
                    {{ link.label }}
                  </RouterLink>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div class="landing-footer__bottom">
        <span>© {{ year }} Định hướng nghề. All rights reserved.</span>
        <div class="landing-footer__legal">
          <a href="#">Chính sách bảo mật</a>
          <a href="#">Điều khoản sử dụng</a>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { footerColumns } from '@/data/landing'

const year = new Date().getFullYear()
</script>
