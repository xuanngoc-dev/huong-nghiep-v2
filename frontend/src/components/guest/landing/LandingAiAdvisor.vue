<template>
  <section id="tu-van-ai" class="landing__section" aria-labelledby="ai-title">
    <div class="container-fluid">
      <div class="row g-lp align-items-center">
        <div class="col-lg-6" data-reveal="left">
          <span class="landing-ai__badge">Xem trước tính năng</span>
          <p class="landing__eyebrow">Trợ lý hướng nghiệp AI</p>
          <h2 id="ai-title" class="landing__title">Tư vấn nghề nghiệp thông minh, gần gũi và tức thì</h2>
          <p class="landing__lead">
            Đặt câu hỏi về ngành học, kỹ năng, lộ trình nghề nghiệp và nhận gợi ý định hướng mang tính
            cá nhân hóa.
          </p>
          <div class="landing-ai__prompts" aria-label="Gợi ý câu hỏi">
            <!-- Trang /demo-chat đã tạm bỏ: mở khung chat nổi với câu hỏi gợi ý điền sẵn
              (trước đây: <RouterLink class="landing-ai__prompt" :to="{ name: 'demo-chat' }">). -->
            <button
              v-for="prompt in aiPrompts"
              :key="prompt"
              type="button"
              class="landing-ai__prompt"
              @click="chat.moKhungChat(prompt)"
            >
              {{ prompt }}
            </button>
          </div>
          <div class="mt-4">
            <!-- Trước đây: <RouterLink :to="{ name: 'demo-chat' }"> (trang /demo-chat đã tạm bỏ). -->
            <button type="button" class="landing__btn landing__btn--primary" @click="chat.moKhungChat()">
              Trò chuyện với AI
              <el-icon aria-hidden="true"><ChatDotRound /></el-icon>
            </button>
          </div>
        </div>

        <div class="col-lg-6" data-reveal="right">
          <div class="landing-ai__chat" aria-label="Giao diện chat minh họa">
            <div class="landing-ai__chat-top">
              <div class="landing-ai__avatar" aria-hidden="true">AI</div>
              <div>
                <strong>Trợ lý định hướng</strong>
                <span><i class="landing-ai__online" aria-hidden="true"></i>Luôn sẵn sàng hỗ trợ bạn</span>
              </div>
            </div>
            <div
              v-for="(message, index) in aiMessages"
              :key="index"
              class="landing-ai__bubble"
              :class="message.role === 'user' ? 'landing-ai__bubble--user' : 'landing-ai__bubble--assistant'"
            >
              {{ message.text }}
            </div>
            <div class="landing-ai__typing" aria-hidden="true"><span></span><span></span><span></span></div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { aiMessages, aiPrompts } from '@/data/landing'
import { useChatStore } from '@/stores/chat'

const chat = useChatStore()
</script>
