<template>
  <div class="guest-layout d-flex flex-column min-vh-100">
    <GuestHeader />
    <main class="flex-grow-1">
      <RouterView />
    </main>
    <footer class="border-top bg-white py-4">
      <div class="container-fluid d-flex flex-column flex-md-row justify-content-between gap-2 small text-secondary">
        <span>Định hướng nghề</span>
        <span>Trắc nghiệm tính cách và gợi ý ngành học</span>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { onUnmounted } from 'vue'
import GuestHeader from '@/layouts/guest/GuestHeader.vue'
import { mountGuestBootstrap, unmountGuestBootstrap } from '@/layouts/guest/bootstrap'

mountGuestBootstrap()
onUnmounted(unmountGuestBootstrap)
</script>

<style>
.guest-layout {
  --guest-primary: #3f9643;
  --guest-primary-rgb: 63, 150, 67;
  --guest-primary-hover: #37843b;
  --bs-success: var(--guest-primary);
  --bs-success-rgb: 63, 150, 67;
  --guest-radius: 8px;
  --guest-radius-sm: 6px;
  --bs-border-radius-xl: var(--guest-radius);
  --bs-border-radius-xxl: 12px;
  background: #fff;
  color: #1c2b23;
  font-family: var(--app-font-family);
}

.guest-layout h1,
.guest-layout h2,
.guest-layout h3,
.guest-layout h4,
.guest-layout h5,
.guest-layout h6 {
  color: var(--guest-primary);
}

.guest-layout .guest-banner :is(h1, h2, h3, h4, h5, h6),
.guest-layout .guest-slide :is(h1, h2, h3, h4, h5, h6) {
  color: inherit;
}

.guest-layout .btn-success {
  --bs-btn-bg: var(--guest-primary);
  --bs-btn-border-color: var(--guest-primary);
  --bs-btn-hover-bg: var(--guest-primary-hover);
  --bs-btn-hover-border-color: var(--guest-primary-hover);
  --bs-btn-active-bg: var(--guest-primary-hover);
  --bs-btn-active-border-color: var(--guest-primary-hover);
  --bs-btn-disabled-bg: var(--guest-primary);
  --bs-btn-disabled-border-color: var(--guest-primary);
}

.guest-layout .btn-outline-success {
  --bs-btn-color: var(--guest-primary);
  --bs-btn-border-color: var(--guest-primary);
  --bs-btn-hover-bg: var(--guest-primary);
  --bs-btn-hover-border-color: var(--guest-primary);
  --bs-btn-hover-color: #fff;
  --bs-btn-active-bg: var(--guest-primary-hover);
  --bs-btn-active-border-color: var(--guest-primary-hover);
  --bs-btn-active-color: #fff;
}
</style>
