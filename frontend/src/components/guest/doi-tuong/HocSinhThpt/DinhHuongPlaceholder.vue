<script setup>
defineOptions({ name: 'DinhHuongPlaceholder' })

defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
})
</script>

<template>
  <section class="py-4">
    <div class="container-fluid">
      <article class="placeholder-card">
        <h1 class="placeholder-card__title">{{ title }}</h1>
        <p v-if="description" class="placeholder-card__text">{{ description }}</p>
        <p class="placeholder-card__note">Nội dung sẽ được bổ sung sau.</p>
        <RouterLink class="placeholder-card__back" to="/hoc-sinh-thpt">Quay lại chọn hướng</RouterLink>
      </article>
    </div>
  </section>
</template>
