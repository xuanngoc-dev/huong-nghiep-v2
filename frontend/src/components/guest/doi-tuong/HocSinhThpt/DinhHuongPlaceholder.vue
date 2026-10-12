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

<style scoped>
.placeholder-card {
  padding: 15px;
  border: 1px solid rgba(var(--guest-primary-rgb), 0.28);
  border-radius: var(--guest-radius, 8px);
  background: #f6fbf7;
}

.placeholder-card__title {
  margin: 0 0 8px;
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1.35;
}

.placeholder-card__text,
.placeholder-card__note {
  margin: 0 0 8px;
  color: #3a4742;
  line-height: 1.5;
}

.placeholder-card__back {
  display: inline-block;
  margin-top: 8px;
  color: var(--guest-primary);
  font-weight: 500;
}
</style>
