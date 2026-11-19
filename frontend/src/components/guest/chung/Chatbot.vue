<template>
  <!-- Trang /demo-chat đã tạm bỏ: <div v-if="route.name !== 'demo-chat'" class="chatbot"> -->
  <div class="chatbot">
    <section v-if="chat.khungMo" id="chatbot-panel" class="chatbot__panel" aria-label="Trợ lý tuyển sinh">
      <header class="chatbot__header">
        <strong>Trợ lý tuyển sinh</strong>
        <div class="chatbot__header-actions">
          <!-- Trang /demo-chat đã tạm bỏ:
          <button type="button" class="chatbot__btn-icon" aria-label="Mở trang đầy đủ" title="Mở trang đầy đủ" @click="expand">
            <el-icon :size="16"><FullScreen /></el-icon>
          </button>
          -->
          <!-- Thành viên: mở hội thoại đang chat trong trang Danh sách hội thoại (khách không có danh sách này). -->
          <button
            v-if="auth.isAuthenticated"
            type="button"
            class="chatbot__btn-icon"
            aria-label="Mở trong Danh sách hội thoại"
            title="Mở trong Danh sách hội thoại"
            :disabled="chat.state.sending"
            @click="moDanhSachHoiThoai"
          >
            <el-icon :size="16"><FullScreen /></el-icon>
          </button>
          <button type="button" class="chatbot__close" aria-label="Đóng khung chat" @click="chat.khungMo = false">
            <el-icon :size="16"><Close /></el-icon>
          </button>
        </div>
      </header>
      <ChatPanel compact />
    </section>
    <button type="button" class="guest-fab" aria-label="Mở chatbot" aria-controls="chatbot-panel" :aria-expanded="chat.khungMo" @click="chat.khungMo = !chat.khungMo">
      <el-icon :size="22"><ChatDotRound /></el-icon>
    </button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import ChatPanel from './ChatPanel.vue'

defineOptions({ name: 'Chatbot' })
// Trạng thái mở khung nằm trong store để các nút "Hỏi trợ lý AI" ở trang khác mở được khung này.
const chat = useChatStore()
const auth = useAuthStore()
const router = useRouter()
// Hội thoại đã có câu hỏi (đã lưu, có mã phiên) mở đúng hội thoại đó; chưa hỏi gì thì mở hội thoại mới.
function moDanhSachHoiThoai() {
  chat.khungMo = false
  router.push(chat.state.maPhien ? { name: 'danh-sach-hoi-thoai', query: { phien: chat.state.maPhien } } : { name: 'hoi-thoai-moi' })
}
// Trang /demo-chat đã tạm bỏ:
// const route = useRoute()
// function expand() {
//   chat.khungMo = false
//   router.push('/demo-chat')
// }
</script>

<style scoped>
.chatbot__panel { height: min(680px, calc(100dvh - 110px)) !important; width: min(440px, calc(100vw - 24px)) !important; }
</style>
