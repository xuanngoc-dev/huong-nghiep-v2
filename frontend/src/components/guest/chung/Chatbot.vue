<script setup>
import { nextTick, ref } from 'vue'

defineOptions({ name: 'Chatbot' })

const open = ref(false)
const draft = ref('')
const listEl = ref(null)
const messages = ref([
  {
    id: 1,
    role: 'bot',
    text: 'Xin chào, bạn cần hỗ trợ định hướng nghề gì?',
  },
])

let nextId = 2

function toggle() {
  open.value = !open.value
}

async function scrollToEnd() {
  await nextTick()
  if (listEl.value) listEl.value.scrollTop = listEl.value.scrollHeight
}

function guiTin() {
  const text = draft.value.trim()
  if (!text) return
  messages.value.push({ id: nextId++, role: 'user', text })
  draft.value = ''
  scrollToEnd()
  window.setTimeout(() => {
    messages.value.push({
      id: nextId++,
      role: 'bot',
      text: 'Mình đã nhận câu hỏi. Kênh trò chuyện sẽ được kết nối sau.',
    })
    scrollToEnd()
  }, 400)
}
</script>

<template>
  <div class="chatbot">
    <section v-if="open" id="chatbot-panel" class="chatbot__panel" aria-label="Khung chat">
      <header class="chatbot__header">
        <strong>Trợ lý định hướng</strong>
        <button type="button" class="chatbot__close" aria-label="Đóng khung chat" @click="open = false">
          <el-icon :size="16"><Close /></el-icon>
        </button>
      </header>
      <div ref="listEl" class="chatbot__list">
        <p
          v-for="message in messages"
          :key="message.id"
          class="chatbot__message"
          :class="`is-${message.role}`"
        >
          {{ message.text }}
        </p>
      </div>
      <form class="chatbot__form" @submit.prevent="guiTin">
        <label class="visually-hidden" for="chatbot-input">Nội dung tin nhắn</label>
        <input
          id="chatbot-input"
          v-model="draft"
          class="chatbot__input"
          type="text"
          placeholder="Nhập câu hỏi"
          autocomplete="off"
        />
        <button type="submit" class="chatbot__send">Gửi</button>
      </form>
    </section>
    <button
      type="button"
      class="guest-fab"
      aria-label="Mở chatbot"
      aria-controls="chatbot-panel"
      :aria-expanded="open"
      @click="toggle"
    >
      <el-icon :size="22"><ChatDotRound /></el-icon>
    </button>
  </div>
</template>
