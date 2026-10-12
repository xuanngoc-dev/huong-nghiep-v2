<script setup>
import { usePageLoading } from '@/composables/usePageLoading'

const { visible } = usePageLoading()
</script>

<template>
  <Transition name="page-loading">
    <div
      v-if="visible"
      class="page-loading"
      role="status"
      aria-live="polite"
      aria-label="Đang tải trang"
    >
      <span class="page-loading__spin" />
    </div>
  </Transition>
</template>

<style scoped>
.page-loading {
  position: fixed;
  inset: 0;
  z-index: 2000;
  display: grid;
  place-items: center;
  background: color-mix(in srgb, var(--el-bg-color) 62%, transparent);
  backdrop-filter: blur(1px);
}

.page-loading__spin {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 3px solid color-mix(in srgb, var(--el-color-primary) 24%, transparent);
  border-top-color: var(--el-color-primary);
  animation: page-loading-spin 0.7s linear infinite;
}

.page-loading-enter-active,
.page-loading-leave-active {
  transition: opacity 0.16s ease;
}

.page-loading-enter-from,
.page-loading-leave-to {
  opacity: 0;
}

@keyframes page-loading-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
