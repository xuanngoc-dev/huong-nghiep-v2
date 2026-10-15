<script setup>
defineOptions({ name: 'CardMajor' })

defineProps({
  ten: { type: String, required: true },
  ma: { type: String, default: '' },
})
</script>

<template>
  <article class="card-major h-100">
    <h4 class="card-major__name">{{ ten }}</h4>
    <p v-if="ma" class="card-major__code">{{ ma }}</p>
  </article>
</template>

<style scoped>
.card-major {
  margin: 0;
  padding: 12px 14px;
  border: 1px solid #e3ebe6;
  border-radius: 10px;
  background: #fff;
  box-shadow: 0 6px 16px rgba(28, 43, 35, 0.07);
}

.card-major__name {
  margin: 0;
  color: #243044;
  font-size: 0.95rem;
  font-weight: 500;
  line-height: 1.4;
}

.card-major__code {
  margin: 6px 0 0;
  color: #5c6b7a;
  font-size: 0.82rem;
  font-weight: 400;
}
</style>
