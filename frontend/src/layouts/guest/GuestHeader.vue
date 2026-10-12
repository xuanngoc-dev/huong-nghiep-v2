<template>
  <nav class="navbar navbar-expand-lg bg-white border-bottom sticky-top">
    <div class="container-fluid">
      <RouterLink class="navbar-brand fw-bold text-success" to="/">Định hướng nghề</RouterLink>
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#guestNav"
        aria-controls="guestNav"
        aria-expanded="false"
        aria-label="Mở menu"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      <div id="guestNav" class="collapse navbar-collapse">
        <div class="ms-lg-auto d-grid gap-2 d-lg-flex mt-3 mt-lg-0">
          <template v-if="auth.isAuthenticated">
            <RouterLink class="btn btn-success" to="/member">Khu vực thành viên</RouterLink>
            <RouterLink v-if="auth.isAdmin" class="btn btn-outline-success" to="/admin">Quản trị</RouterLink>
          </template>
          <template v-else>
            <RouterLink class="btn btn-outline-success" to="/login">Đăng nhập</RouterLink>
            <RouterLink class="btn btn-success" to="/register">Đăng ký</RouterLink>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import 'bootstrap/js/dist/collapse'

const auth = useAuthStore()
</script>
