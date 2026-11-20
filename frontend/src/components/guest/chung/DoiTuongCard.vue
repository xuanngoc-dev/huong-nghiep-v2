<template>
  <!-- Dùng chung giao diện thẻ hướng đi: ảnh trái - nội dung phải. -->
  <HuongDiCard
    :image="image"
    :title="name"
    :description="description"
    :nhan="nhan"
    :selected="selected"
    :locked="khoa"
    cta="Bắt đầu"
    cta-khoa="Đang phát triển..."
    @chon="emit('select')"
  />
</template>

<script setup>
import HuongDiCard from '@/components/guest/chung/HuongDiCard.vue'

defineOptions({ name: 'DoiTuongCard' })

defineProps({
  image: { type: String, required: true },
  name: { type: String, required: true },
  description: { type: String, default: '' },
  ma: { type: String, default: '' },
  nhan: { type: String, default: '' },
  selected: { type: Boolean, default: false },
  khoa: { type: Boolean, default: false },
})

const emit = defineEmits(['select'])
</script>
