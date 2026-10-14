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
    <HoTroNhanh v-if="showAssist" />
    <div v-if="showAssist" class="guest-dock">
      <LenDauTrang />
      <Chatbot />
    </div>
  </div>
</template>

<script setup>
import { computed, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import GuestHeader from '@/layouts/guest/GuestHeader.vue'
import HoTroNhanh from '@/components/guest/chung/HoTroNhanh.vue'
import LenDauTrang from '@/components/guest/chung/LenDauTrang.vue'
import Chatbot from '@/components/guest/chung/Chatbot.vue'
import { mountGuestBootstrap, unmountGuestBootstrap } from '@/layouts/guest/bootstrap'

const route = useRoute()
const showAssist = computed(() => !route.meta.hideAssist)

mountGuestBootstrap()
onUnmounted(unmountGuestBootstrap)
</script>
