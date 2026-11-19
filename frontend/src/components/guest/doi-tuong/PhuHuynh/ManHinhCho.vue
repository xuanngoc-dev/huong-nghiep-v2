<template>
  <section class="py-4">
    <div class="container-fluid">
      <article class="placeholder-card">
        <h1 class="placeholder-card__title">{{ title }}</h1>
        <p v-if="description" class="placeholder-card__text">{{ description }}</p>
        <p class="placeholder-card__note">Nội dung sẽ được bổ sung sau.</p>
        <RouterLink class="placeholder-card__back" :to="quayLai.to">{{ quayLai.label }}</RouterLink>
      </article>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

defineOptions({ name: 'PhuHuynhManHinhCho' })

defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
})

const route = useRoute()

// Màn của một lớp THPT quay về màn chọn lớp; còn lại về trang chọn giai đoạn.
const quayLai = computed(() =>
  route.meta.capHoc === 'thpt'
    ? { to: { name: 'phu-huynh-thpt' }, label: 'Quay lại chọn lớp của con' }
    : { to: { name: 'phu-huynh' }, label: 'Quay lại chọn giai đoạn của con' },
)
</script>
