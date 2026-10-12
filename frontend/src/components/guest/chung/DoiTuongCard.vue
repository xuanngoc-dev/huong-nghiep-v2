<script setup>
defineOptions({ name: 'DoiTuongCard' })

defineProps({
  image: { type: String, required: true },
  name: { type: String, required: true },
  description: { type: String, default: '' },
  ma: { type: String, default: '' },
  selected: { type: Boolean, default: false },
})

const emit = defineEmits(['select'])
</script>

<template>
  <article class="audience-card h-100" :class="{ 'is-selected': selected }">
    <div class="audience-card__media">
      <img class="audience-card__image" :src="image" :alt="name" />
      <button type="button" class="audience-card__button" aria-label="Bắt đầu" @click="emit('select')">
        <ArrowRight />
      </button>
    </div>
    <!-- <p v-if="ma" class="audience-card__code">{{ ma }}</p> -->
    <h2 class="audience-card__title">{{ name }}</h2>
    <p class="audience-card__text">{{ description }}</p>
  </article>
</template>
