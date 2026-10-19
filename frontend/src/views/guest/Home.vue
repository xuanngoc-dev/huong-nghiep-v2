<script setup>
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
</script>

<template>
  <section class="home-gate">
    <div class="home-gate__row">
      <RouterLink class="btn btn-success btn-lg" to="/chon-doi-tuong">Bắt đầu ngay</RouterLink>
      <RouterLink v-if="!auth.isAuthenticated" class="btn btn-outline-success btn-lg" to="/register">Đăng ký tài khoản</RouterLink>
      <RouterLink class="btn btn-outline-success btn-lg" to="/demo-chat">Chat với AI</RouterLink>
      <RouterLink class="btn btn-outline-success btn-lg" to="/validate-data">Kiểm tra dữ liệu</RouterLink>
      <RouterLink v-if="auth.isAuthenticated" class="btn btn-outline-success btn-lg" :to="{ name: 'ho-so' }">Hồ sơ cá nhân</RouterLink>
    </div>
  </section>
</template>

<style scoped>
.home-gate {
  display: grid;
  place-items: center;
  min-height: calc(100dvh - 220px);
  padding: 32px 16px;
}

.home-gate__row {
  display: flex;
  flex-flow: row nowrap;
  gap: 16px;
  width: max-content;
  max-width: 100%;
  overflow-x: auto;
}

.home-gate__row a {
  flex: 0 0 auto;
  white-space: nowrap;
}
</style>
