<template>
  <article class="audience-card h-100" :class="{ 'is-selected': selected, 'is-locked': khoa }">
    <div class="audience-card__media">
      <img class="audience-card__image" :src="image" :alt="name" />
      <span v-if="khoa" class="sap-ra-mat">Sắp ra mắt</span>
      <button
        type="button"
        class="audience-card__button"
        :aria-label="khoa ? `${name}: sắp ra mắt` : 'Bắt đầu'"
        :disabled="khoa"
        @click="emit('select')"
      >
        <ArrowRight />
      </button>
    </div>
    <!-- <p v-if="ma" class="audience-card__code">{{ ma }}</p> -->
    <h2 class="audience-card__title">{{ name }}</h2>
    <p class="audience-card__text">{{ description }}</p>
  </article>
</template>

<script setup>
defineOptions({ name: 'DoiTuongCard' })

defineProps({
  image: { type: String, required: true },
  name: { type: String, required: true },
  description: { type: String, default: '' },
  ma: { type: String, default: '' },
  selected: { type: Boolean, default: false },
  khoa: { type: Boolean, default: false },
})

const emit = defineEmits(['select'])
</script>
