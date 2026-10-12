<script setup>
import { ref } from 'vue'

defineOptions({ name: 'CauHoiThuongGap' })

const items = [
  {
    id: 'buoc-tiep',
    question: 'Sau khi chọn hướng, tôi làm gì tiếp theo?',
    answer:
      'Bạn giữ hướng vừa chọn, rồi làm trắc nghiệm tính cách để đối chiếu ngành học hoặc việc làm gần với điểm mạnh của mình.',
  },
  {
    id: 'doi-huong',
    question: 'Tôi có thể đổi hướng đã chọn không?',
    answer: 'Có. Bạn chọn lại một hướng khác bất cứ lúc nào. Lựa chọn mới sẽ thay cho hướng đang lưu.',
  },
  {
    id: 'trac-nghiem',
    question: 'Kết quả trắc nghiệm dùng để làm gì?',
    answer:
      'Kết quả cho thấy nhóm tính cách nổi bật, để bạn đối chiếu với ngành, trường và hướng đi sau tốt nghiệp.',
  },
  {
    id: 'phu-huynh',
    question: 'Phụ huynh có xem cùng được không?',
    answer: 'Được. Phụ huynh có thể chọn nhóm của mình để xem các gợi ý và cùng trao đổi với học sinh.',
  },
]

const openId = ref('')

function toggle(id) {
  openId.value = openId.value === id ? '' : id
}
</script>

<template>
  <section class="faq-card" aria-labelledby="cau-hoi-thuong-gap-title">
    <h2 id="cau-hoi-thuong-gap-title" class="faq-card__title">Câu hỏi thường gặp</h2>
    <div class="faq-list">
      <div v-for="item in items" :key="item.id" class="faq-item" :class="{ 'is-open': openId === item.id }">
        <h3 class="faq-item__heading">
          <button
            type="button"
            class="faq-item__button"
            :aria-expanded="openId === item.id"
            :aria-controls="`faq-${item.id}`"
            @click="toggle(item.id)"
          >
            <span>{{ item.question }}</span>
            <span class="faq-item__mark" aria-hidden="true">{{ openId === item.id ? '−' : '+' }}</span>
          </button>
        </h3>
        <div :id="`faq-${item.id}`" class="faq-item__panel" role="region">
          <div class="faq-item__inner">
            <p>{{ item.answer }}</p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.faq-card {
  padding: 15px;
  border: 1px solid rgba(var(--guest-primary-rgb), 0.28);
  border-radius: var(--guest-radius, 8px);
  background: #f6fbf7;
}

.faq-card__title {
  margin: 0 0 12px;
  font-size: 1.35rem;
  font-weight: 700;
  line-height: 1.35;
}

.faq-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.faq-item {
  border: 1px solid #d7eadf;
  border-radius: var(--guest-radius, 8px);
  background: #fff;
}

.faq-item__heading {
  margin: 0;
  font-size: 1rem;
}

.faq-item__button {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
  padding: 12px 15px;
  border: 0;
  border-radius: var(--guest-radius, 8px);
  background: transparent;
  color: #1c2b23;
  font-weight: 700;
  line-height: 1.4;
  text-align: left;
  cursor: pointer;
}

.faq-item__mark {
  flex: 0 0 auto;
  color: var(--guest-primary);
  font-size: 1.25rem;
  line-height: 1;
}

.faq-item__panel {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.25s ease;
}

.faq-item.is-open .faq-item__panel {
  grid-template-rows: 1fr;
}

.faq-item__inner {
  overflow: hidden;
}

.faq-item__inner p {
  margin: 0;
  padding: 0 15px 12px;
  color: #3a4742;
  line-height: 1.5;
}

@media (prefers-reduced-motion: reduce) {
  .faq-item__panel {
    transition: none;
  }
}
</style>
