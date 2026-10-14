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
        <div class="ms-lg-auto d-grid gap-2 d-lg-flex align-items-lg-center mt-3 mt-lg-0">
          <div class="dropdown">
            <button
              class="btn btn-outline-success dropdown-toggle"
              type="button"
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              {{ menuLabel }}
            </button>
            <ul class="dropdown-menu">
              <li v-for="item in doiTuongItems" :key="item.index">
                <RouterLink
                  class="dropdown-item"
                  :class="{ active: route.path === item.index }"
                  :to="item.index"
                >
                  {{ item.title }}
                </RouterLink>
              </li>
            </ul>
          </div>
          <RouterLink class="btn btn-outline-success" to="/demo-chat">
            <el-icon class="me-1"><ChatDotRound /></el-icon>
            Trợ lý AI
          </RouterLink>
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
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import menuData from '@/data/menu.json'
import 'bootstrap/js/dist/collapse'
import 'bootstrap/js/dist/dropdown'

const auth = useAuthStore()
const route = useRoute()
const doiTuongItems = menuData['doi-tuong']?.flatMap((group) => group.items || []) || []
const menuLabel = computed(
  () => doiTuongItems.find((item) => item.index === route.path)?.title || 'Chọn đối tượng',
)
</script>
