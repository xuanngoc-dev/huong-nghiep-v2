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
