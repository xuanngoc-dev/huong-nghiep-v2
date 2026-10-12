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
