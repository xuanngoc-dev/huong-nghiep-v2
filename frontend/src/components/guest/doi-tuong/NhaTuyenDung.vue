<script setup>
defineOptions({ name: 'NhaTuyenDung' })

defineProps({
  audience: { type: Object, required: true },
})
</script>

<template>
  <section class="py-5">
    <div class="container">
      <p class="text-secondary mb-2">Mã {{ audience.ma }}</p>
      <h1 class="h2 mb-3">{{ audience.name }}</h1>
      <p class="col-lg-8 text-secondary mb-0">{{ audience.description }}</p>
    </div>
  </section>
</template>
