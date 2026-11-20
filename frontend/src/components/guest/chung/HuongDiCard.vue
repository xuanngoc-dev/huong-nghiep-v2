<template>
  <!-- Hướng đi chưa mở: hiển thị mờ, không bấm được. -->
  <div v-if="locked" class="huong-card is-locked h-100" aria-disabled="true">
    <span class="huong-card__media">
      <img class="huong-card__anh" :src="image" alt="" loading="lazy" decoding="async" />
      <span class="sap-ra-mat">Sắp ra mắt</span>
    </span>
    <span class="huong-card__body">
      <span class="huong-card__ten">{{ title }}</span>
      <span class="huong-card__mo-ta">{{ description }}</span>
      <span v-if="note" class="huong-card__ghi-chu">{{ note }}</span>
    </span>
  </div>
  <component
    :is="to ? RouterLink : 'button'"
    v-else
    class="huong-card h-100"
    :class="{ 'is-selected': selected }"
    :to="to || undefined"
    :type="to ? undefined : 'button'"
    @click="emit('chon')"
  >
    <span class="huong-card__media">
      <img class="huong-card__anh" :src="image" alt="" loading="lazy" decoding="async" />
    </span>
    <span class="huong-card__body">
      <span class="huong-card__ten">{{ title }}</span>
      <span class="huong-card__mo-ta">{{ description }}</span>
      <span v-if="note" class="huong-card__ghi-chu">{{ note }}</span>
      <span class="huong-card__xem">{{ cta }} →</span>
    </span>
  </component>
</template>

<script setup>
import { RouterLink } from 'vue-router'

// Thẻ hướng đi: ảnh bên trái, tên, mô tả và lời mời bấm bên phải.
// Có `to` thì là liên kết; không có thì là nút và phát sự kiện `chon` (trang tự xử lý chuyển trang).
defineOptions({ name: 'HuongDiCard' })

defineProps({
  image: { type: String, required: true },
  title: { type: String, required: true },
  description: { type: String, default: '' },
  // Dòng phụ dưới mô tả, ví dụ chi phí dự kiến.
  note: { type: String, default: '' },
  to: { type: [Object, String], default: null },
  cta: { type: String, default: 'Xem chi tiết' },
  selected: { type: Boolean, default: false },
  locked: { type: Boolean, default: false },
})

const emit = defineEmits(['chon'])
</script>

<style scoped>
/* Ảnh bên trái, nội dung bên phải; ảnh cao theo nội dung. */
.huong-card {
  display: flex;
  width: 100%;
  overflow: hidden;
  padding: 0;
  border: 1px solid #d7eadf;
  border-radius: var(--guest-radius);
  background: #fff;
  color: inherit;
  font: inherit;
  text-align: left;
  text-decoration: none;
  cursor: pointer;
  transition: box-shadow 0.3s ease;
}

.huong-card:hover {
  box-shadow: 0 12px 24px rgba(31, 122, 77, 0.12);
}

.huong-card.is-selected {
  border-color: var(--guest-primary);
  box-shadow: 0 0 0 1px var(--guest-primary);
}

.huong-card.is-locked {
  cursor: not-allowed;
}

.huong-card.is-locked:hover {
  box-shadow: none;
}

.huong-card.is-locked :is(.huong-card__anh, .huong-card__ten, .huong-card__mo-ta, .huong-card__ghi-chu) {
  opacity: 0.55;
  filter: grayscale(0.6);
}

.huong-card__media {
  position: relative;
  flex: 0 0 38%;
  min-height: 170px;
  overflow: hidden;
  background: #e3efe7;
}

.huong-card__anh {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s ease;
}

.huong-card:not(.is-locked):hover .huong-card__anh {
  transform: scale(1.05);
}

.huong-card__body {
  display: flex;
  flex: 1;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
  min-width: 0;
  padding: 14px 16px;
}

.huong-card__ten {
  color: #1c2b23;
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1.35;
}

.huong-card__mo-ta {
  display: -webkit-box;
  overflow: hidden;
  color: #3a4742;
  font-size: 0.9rem;
  line-height: 1.5;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  line-clamp: 3;
}

.huong-card__ghi-chu {
  color: #6b7780;
  font-size: 0.82rem;
}

.huong-card__xem {
  margin-top: auto;
  color: var(--guest-primary);
  font-size: 0.875rem;
  font-weight: 500;
}

.huong-card:focus-visible {
  outline: 2px solid var(--guest-primary);
  outline-offset: 2px;
}

@media (max-width: 575.98px) {
  .huong-card__media {
    flex-basis: 34%;
    min-height: 150px;
  }

  .huong-card__body {
    padding: 12px;
  }

  .huong-card__mo-ta {
    -webkit-line-clamp: 2;
    line-clamp: 2;
  }
}
</style>
