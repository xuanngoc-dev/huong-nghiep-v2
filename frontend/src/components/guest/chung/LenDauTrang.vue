<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

defineOptions({ name: 'LenDauTrang' })

const visible = ref(false)

function onScroll() {
  visible.value = window.scrollY > 240
}

function lenDauTrang() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  onScroll()
  window.addEventListener('scroll', onScroll, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
})
</script>

<template>
  <button
    v-show="visible"
    type="button"
    class="guest-fab"
    aria-label="Lên đầu trang"
    @click="lenDauTrang"
  >
    <el-icon :size="22"><Top /></el-icon>
  </button>
</template>
