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
  --bs-success: #1f7a4d;
  --bs-success-rgb: 31, 122, 77;
  --guest-radius: 8px;
  --guest-radius-sm: 6px;
  --bs-border-radius-xl: var(--guest-radius);
  --bs-border-radius-xxl: 12px;
  background: #f4f7f5;
  color: #1c2b23;
  font-family: var(--app-font-family);
}

.guest-layout .btn-success {
  --bs-btn-bg: #1f7a4d;
  --bs-btn-border-color: #1f7a4d;
  --bs-btn-hover-bg: #18643e;
  --bs-btn-hover-border-color: #18643e;
  --bs-btn-active-bg: #145536;
  --bs-btn-active-border-color: #145536;
  --bs-btn-disabled-bg: #1f7a4d;
  --bs-btn-disabled-border-color: #1f7a4d;
}

.guest-layout .btn-outline-success {
  --bs-btn-color: #1f7a4d;
  --bs-btn-border-color: #1f7a4d;
  --bs-btn-hover-bg: #1f7a4d;
  --bs-btn-hover-border-color: #1f7a4d;
  --bs-btn-hover-color: #fff;
  --bs-btn-active-bg: #18643e;
  --bs-btn-active-border-color: #18643e;
  --bs-btn-active-color: #fff;
}
</style>
