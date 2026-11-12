<template>
  <div class="khong-co-du-lieu" role="status">
    <svg class="khong-co-du-lieu__image" viewBox="0 0 160 120" aria-hidden="true">
      <circle cx="80" cy="58" r="46" fill="#e8f5ec" />
      <rect x="46" y="28" width="58" height="70" rx="8" fill="#fff" stroke="#7eae8c" stroke-width="2" />
      <path d="M88 28h8a8 8 0 0 1 8 8v8H96a8 8 0 0 1-8-8V28z" fill="#d7eadc" stroke="#7eae8c" stroke-width="2" />
      <path d="M58 52h34M58 64h28M58 76h20" stroke="#b7d4c0" stroke-width="3" stroke-linecap="round" />
      <circle cx="108" cy="78" r="16" fill="#3f9643" />
      <circle cx="108" cy="78" r="7" fill="none" stroke="#fff" stroke-width="2" />
      <path d="M113.5 83.5 120 90" stroke="#fff" stroke-width="2" stroke-linecap="round" />
    </svg>
    <p class="khong-co-du-lieu__text">{{ text }}</p>
  </div>
</template>

<script setup>
defineOptions({ name: 'KhongCoDuLieu' })

defineProps({
  text: { type: String, default: 'Không có dữ liệu.' },
})
</script>

<style scoped>
.khong-co-du-lieu {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 24px 16px;
  text-align: center;
}

.khong-co-du-lieu__image {
  width: 160px;
  height: 120px;
}

.khong-co-du-lieu__text {
  margin: 0;
  max-width: 360px;
  color: #5c6b62;
  font-weight: 400;
  line-height: 1.5;
}
</style>
