<template>
  <div class="guest-layout d-flex flex-column min-vh-100">
    <GuestHeader />
    <GuestBreadcrumb />
    <main class="flex-grow-1">
      <RouterView />
    </main>
    <LandingFooter />
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
import GuestBreadcrumb from '@/layouts/guest/GuestBreadcrumb.vue'
import LandingFooter from '@/components/guest/landing/LandingFooter.vue'
import '@/layouts/guest/guest-layout.css'
import '@/components/guest/landing/landing.css'
import HoTroNhanh from '@/components/guest/chung/HoTroNhanh.vue'
import LenDauTrang from '@/components/guest/chung/LenDauTrang.vue'
import Chatbot from '@/components/guest/chung/Chatbot.vue'
import { mountGuestBootstrap, unmountGuestBootstrap } from '@/layouts/guest/bootstrap'

const route = useRoute()
const showAssist = computed(() => !route.meta.hideAssist)

mountGuestBootstrap()
onUnmounted(unmountGuestBootstrap)
</script>
