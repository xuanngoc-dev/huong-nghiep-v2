<template>
  <UserLayout v-if="auth.isAuthenticated" />
  <GuestLayout v-else />
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import GuestLayout from '@/layouts/GuestLayout.vue'
import UserLayout from '@/layouts/UserLayout.vue'

const auth = useAuthStore()
</script>
