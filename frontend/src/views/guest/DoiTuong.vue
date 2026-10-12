<script setup>
import { computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { DOI_TUONG_KEY, doiTuongList } from '@/data/doiTuong'

const route = useRoute()

const audience = computed(() => doiTuongList.find((item) => item.code === route.meta.doiTuong))

watch(
  () => route.meta.doiTuong,
  (code) => {
    if (code) sessionStorage.setItem(DOI_TUONG_KEY, code)
  },
  { immediate: true },
)
</script>

<template>
  <section class="py-5">
    <div class="container">
      <p class="text-secondary mb-2">Đối tượng đã chọn</p>
      <h1 class="h2 mb-3">{{ audience?.name }}</h1>
      <p class="col-lg-8 text-secondary">{{ audience?.description }}</p>
      <RouterLink class="btn btn-outline-success mt-3" to="/chon-doi-tuong">Chọn đối tượng khác</RouterLink>
    </div>
  </section>
</template>
