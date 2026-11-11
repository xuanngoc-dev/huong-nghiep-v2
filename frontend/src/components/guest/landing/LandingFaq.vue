<script setup>
import { ref } from 'vue'
import { faqs } from '@/data/landing'

const openId = ref(faqs[0].id)

function toggle(id) {
  openId.value = openId.value === id ? null : id
}
</script>

<template>
  <section id="hoi-dap" class="landing__section landing__section--alt" aria-labelledby="faq-title">
    <div class="container-fluid">
      <div class="row g-lp align-items-start">
        <div class="landing-faq__intro col-lg-5" data-reveal="left">
          <p class="landing__eyebrow">Câu hỏi thường gặp</p>
          <h2 id="faq-title" class="landing__title">Bạn còn băn khoăn?</h2>
          <p class="landing__lead">
            Những thắc mắc phổ biến về nền tảng, trắc nghiệm Holland và cách chúng tôi đồng hành cùng
            bạn. Chưa tìm thấy câu trả lời? Hãy hỏi trợ lý AI hoặc liên hệ với chúng tôi.
          </p>
          <div class="landing-faq__actions">
            <RouterLink class="landing__btn landing__btn--primary" :to="{ name: 'demo-chat' }">
              Hỏi trợ lý AI
            </RouterLink>
            <a class="landing__btn landing__btn--ghost" href="mailto:hotro@dinhhuongnghe.vn">Gửi email hỗ trợ</a>
          </div>
        </div>

        <div class="landing-faq__list col-lg-7" data-stagger>
          <div
            v-for="item in faqs"
            :key="item.id"
            class="landing-faq__item"
            :class="{ 'is-open': openId === item.id }"
          >
            <h3>
              <button
                :id="`faq-q-${item.id}`"
                type="button"
                class="landing-faq__question"
                :aria-expanded="openId === item.id"
                :aria-controls="`faq-a-${item.id}`"
                @click="toggle(item.id)"
              >
                <span>{{ item.question }}</span>
                <el-icon class="landing-faq__chevron" aria-hidden="true"><ArrowDown /></el-icon>
              </button>
            </h3>
            <div
              :id="`faq-a-${item.id}`"
              class="landing-faq__answer"
              role="region"
              :aria-labelledby="`faq-q-${item.id}`"
              :inert="openId !== item.id"
            >
              <div><p>{{ item.answer }}</p></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
