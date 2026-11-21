<template>
  <!-- Bài viết chưa có trang nội dung: thẻ không bấm được nhưng vẫn hiện rõ (lam-mo=false). -->
  <HuongDiCard
    :image="bai.image"
    :title="bai.title"
    :description="bai.summary"
    :nhan="bai.category"
    :note="dinhDangNgay(bai.date)"
    locked
    :lam-mo="false"
    cta-khoa="Nội dung sắp ra mắt"
  />
</template>

<script setup>
import HuongDiCard from '@/components/guest/chung/HuongDiCard.vue'
import { dinhDangNgay } from '@/utils/thoiGian'

defineOptions({ name: 'TheBaiViet' })

defineProps({
  // Một phần tử của `articles` (data/landing.js): { id, category, title, summary, date, image }.
  bai: { type: Object, required: true },
})
</script>
