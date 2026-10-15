<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ChatPanel from './ChatPanel.vue'

defineOptions({ name: 'Chatbot' })
const open = ref(false)
const route = useRoute()
const router = useRouter()
function expand() {
  open.value = false
  router.push('/demo-chat')
}
</script>

<template>
  <div v-if="route.name !== 'demo-chat'" class="chatbot">
    <section v-if="open" id="chatbot-panel" class="chatbot__panel" aria-label="Trợ lý tuyển sinh">
      <header class="chatbot__header">
        <strong>Trợ lý tuyển sinh</strong>
        <div class="chatbot__header-actions">
          <button type="button" class="chatbot__btn-icon" aria-label="Mở trang đầy đủ" title="Mở trang đầy đủ" @click="expand">
            <el-icon :size="16"><FullScreen /></el-icon>
          </button>
          <button type="button" class="chatbot__close" aria-label="Đóng khung chat" @click="open = false">
            <el-icon :size="16"><Close /></el-icon>
          </button>
        </div>
      </header>
      <ChatPanel compact />
    </section>
    <button type="button" class="guest-fab" aria-label="Mở chatbot" aria-controls="chatbot-panel" :aria-expanded="open" @click="open = !open">
      <el-icon :size="22"><ChatDotRound /></el-icon>
    </button>
  </div>
</template>

<style scoped>
.chatbot__panel { height: min(680px, calc(100dvh - 110px)) !important; width: min(440px, calc(100vw - 24px)) !important; }
</style>
