<script setup>
defineOptions({ name: 'NotFound' })
</script>

<template>
  <section class="not-found py-5">
    <div class="container-fluid">
      <div class="not-found__card">
        <p class="not-found__code">404</p>
        <h1>Không tìm thấy trang</h1>
        <p>Đường dẫn này chưa được khai báo hoặc không còn tồn tại.</p>
        <RouterLink class="btn btn-success" to="/">Về trang chủ</RouterLink>
      </div>
    </div>
  </section>
</template>
