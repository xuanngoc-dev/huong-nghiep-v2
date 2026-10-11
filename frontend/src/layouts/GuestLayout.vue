<template>
  <div class="guest-layout">
    <GuestHeader />
    <main class="guest-layout__main">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import GuestHeader from '@/layouts/guest/GuestHeader.vue'
</script>

<style scoped lang="scss">
.guest-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--el-bg-color-page);
  color: var(--el-text-color-primary);
}

.guest-layout__main {
  flex: 1;
  padding: 28px;
}

@media (max-width: 640px) {
  .guest-layout__main {
    padding: 16px;
  }
}
</style>
