<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const title = computed(() => route.meta?.title || 'Trang')
</script>

<template>
  <el-card shadow="never" class="placeholder-card">
    <!-- <template #header>
      <strong>{{ title }}</strong>
    </template> -->
    <el-empty description="Nội dung sẽ được bổ sung sau." />
  </el-card>
</template>

<style scoped>
.placeholder-card {
  border-radius: 12px;
}
</style>
