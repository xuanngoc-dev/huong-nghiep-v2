<template>
  <header class="guest-header">
    <RouterLink to="/" class="guest-header__brand">Định hướng nghề</RouterLink>

    <nav class="guest-header__nav" aria-label="Điều hướng khách">
      <button type="button" class="guest-header__login" @click="router.push('/login')">
        Đăng nhập
      </button>
      <button type="button" class="guest-header__register" @click="router.push('/register')">
        Đăng ký
      </button>
    </nav>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<style scoped lang="scss">
.guest-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  min-height: 72px;
  padding: 16px 28px;
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-lighter);
  color: var(--el-text-color-primary);
  font-family: var(--app-font-family);
}

.guest-header__brand {
  color: var(--el-color-primary);
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.2;
  text-decoration: none;
  white-space: nowrap;
}

.guest-header__nav {
  display: flex;
  align-items: center;
  gap: 8px;
}

.guest-header__login,
.guest-header__register {
  appearance: none;
  border-radius: 999px;
  padding: 8px 16px;
  font: inherit;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.2;
  cursor: pointer;
}

.guest-header__login {
  border: 1px solid transparent;
  background: transparent;
  color: var(--el-color-primary);
}

.guest-header__login:hover {
  background: var(--el-color-primary-light-9);
}

.guest-header__register {
  border: 1px solid var(--el-color-primary);
  background: var(--el-color-primary);
  color: #fff;
}

.guest-header__register:hover {
  filter: brightness(0.92);
}

@media (max-width: 640px) {
  .guest-header {
    padding: 12px 16px;
  }

  .guest-header__brand {
    font-size: 16px;
  }

  .guest-header__login,
  .guest-header__register {
    padding: 8px 12px;
  }
}
</style>
