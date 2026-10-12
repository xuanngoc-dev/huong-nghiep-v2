<script setup>
defineOptions({ name: 'DoiTuongCard' })

defineProps({
  image: { type: String, required: true },
  name: { type: String, required: true },
  description: { type: String, default: '' },
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
    <h2 class="audience-card__title">{{ name }}</h2>
    <p class="audience-card__text">{{ description }}</p>
  </article>
</template>

<style scoped>
.audience-card {
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 16px;
  border: 1px solid #d7eadf;
  border-radius: var(--guest-radius, 8px);
  background: #fff;
  transition: box-shadow 0.3s ease;
}

.audience-card:hover {
  box-shadow: 0 16px 32px rgba(31, 122, 77, 0.14);
  cursor: pointer;
}

.audience-card.is-selected {
  border-color: #1f7a4d;
  box-shadow: 0 0 0 1px #1f7a4d;
}

.audience-card.is-selected:hover {
  box-shadow:
    0 0 0 1px #1f7a4d,
    0 16px 32px rgba(31, 122, 77, 0.14);
}

.audience-card__media {
  position: relative;
  overflow: hidden;
  border-radius: var(--guest-radius-sm, 6px);
}

.audience-card__image {
  display: block;
  width: 100%;
  height: 190px;
  object-fit: cover;
}

.audience-card__title {
  margin: 18px 0 8px;
  color: #1f7a4d;
  font-size: 1.35rem;
  font-weight: 700;
  line-height: 1.35;
}

.audience-card__text {
  flex: 1;
  margin: 0;
  color: #8d97a2;
  font-size: 1rem;
  line-height: 1.5;
}

.audience-card__button {
  position: absolute;
  right: 12px;
  bottom: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  padding: 0;
  border: 0;
  border-radius: 50%;
  background: #3caf6a;
  color: #fff;
  font-size: 18px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.audience-card__button:hover {
  background: #349a5d;
}

@media (prefers-reduced-motion: reduce) {
  .audience-card,
  .audience-card__button {
    transition: none;
  }
}
</style>
