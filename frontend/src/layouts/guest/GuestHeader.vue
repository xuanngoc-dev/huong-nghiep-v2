<template>
  <nav class="navbar navbar-expand-lg bg-white border-bottom sticky-top">
    <div class="container">
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
          <RouterLink class="btn btn-outline-success" to="/login">Đăng nhập</RouterLink>
          <RouterLink class="btn btn-success" to="/register">Đăng ký</RouterLink>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import 'bootstrap/js/dist/collapse'
</script>
