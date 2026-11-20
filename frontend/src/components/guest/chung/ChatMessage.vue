<template>
  <!-- Giao diện như nội dung hội thoại ở trang Danh sách hội thoại; tin liên tiếp cùng một bên gộp nhóm (giờ dưới
       tin cuối nhóm). Tin của trợ lý rộng hết khung chat, không có avatar để tiết kiệm diện tích; tin của bạn bên phải. -->
  <div class="ai-chat__nhom" :class="[`is-${message.role}`, { 'is-dau': dauNhom }]">
    <div class="ai-chat__than">
      <article class="ai-chat__message" :class="[`is-${message.role}`, `is-${message.status}`]">
        <ChatMarkdown v-if="message.role === 'bot'" :text="message.text" />
        <p v-else class="ai-chat__user-text">{{ message.text }}</p>
        <DangSoanTraLoi v-if="message.status === 'streaming' && !message.text" class="ai-chat__pending" />
        <!-- Tin hệ thống báo hết token: thành viên mời nạp gói Token AI; khách vãng lai mời đăng nhập / tạo tài khoản. -->
        <div v-if="message.hetToken" class="ai-chat__het-token">
          <template v-if="!auth.isAuthenticated">
            <RouterLink class="is-chinh" :to="{ name: 'login', query: { redirect: route.fullPath } }">Đăng nhập</RouterLink>
            <RouterLink :to="{ name: 'register' }">Tạo tài khoản</RouterLink>
          </template>
          <RouterLink v-else class="is-chinh" :to="{ name: 'nap-tien', query: { loai: 'token' } }">Nạp Token AI</RouterLink>
        </div>
        <p v-if="message.error" class="ai-chat__error" role="status">{{ message.error }}</p>
        <p v-else-if="message.status === 'cancelled' && message.text !== 'Đã dừng trả lời.'" class="ai-chat__muted">Đã dừng trả lời.</p>
        <ul v-if="message.notes?.length" class="ai-chat__notes">
          <li v-for="note in message.notes" :key="note">{{ note }}</li>
        </ul>
        <details v-if="message.sources?.length && false" class="ai-chat__sources">
          <summary>Nguồn tham khảo ({{ message.sources.length }})</summary>
          <ol>
            <li v-for="source in message.sources" :key="source.id">
              <strong>[{{ source.id }}] {{ source.ten }}</strong>
              <span v-if="source.nam"> · Tuyển sinh {{ source.nam }}</span>
              <small v-if="source.cap_nhat">Dữ liệu cập nhật {{ date(source.cap_nhat) }}</small>
              <a v-if="dataLink(source)" :href="dataLink(source)" target="_blank" rel="noopener noreferrer">Xem dữ liệu tham khảo</a>
              <a v-if="source.url_goc && safeLink(source.url_goc)" :href="source.url_goc" target="_blank" rel="noopener noreferrer">Đề án gốc</a>
            </li>
          </ol>
        </details>
        <footer v-if="message.role === 'bot' && message.id !== 'welcome' && false" class="ai-chat__message-actions">
          <small>{{ message.meta }}</small>
          <button v-if="message.text" type="button" @click="copy(message.text)">{{ copyStatus || 'Sao chép' }}</button>
          <button v-if="retryable" type="button" @click="$emit('retry')">Thử lại</button>
        </footer>
      </article>
      <small v-if="cuoiNhom && gio(message.at)" class="ai-chat__gio">{{ gio(message.at) }}</small>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import ChatMarkdown from './ChatMarkdown.vue'
import DangSoanTraLoi from './DangSoanTraLoi.vue'
import { apiAssetUrl } from '@/api/apiUrl'
import { safeLink } from '@/utils/chatMarkdown'
import { dinhDangNgay, dinhDangThoiGian } from '@/utils/thoiGian'

// dauNhom / cuoiNhom: tin đầu / cuối của một nhóm tin liên tiếp cùng một bên.
defineProps({
  message: { type: Object, required: true },
  retryable: Boolean,
  dauNhom: { type: Boolean, default: true },
  cuoiNhom: { type: Boolean, default: true },
})
defineEmits(['retry'])
const auth = useAuthStore()
const route = useRoute()
const copyStatus = ref('')
async function copy(text) {
  try { await navigator.clipboard.writeText(text); copyStatus.value = 'Đã sao chép' }
  catch { copyStatus.value = 'Không thể sao chép' }
}
function dataLink(source) {
  if (!source.duong_dan?.startsWith('/')) return null
  return safeLink(apiAssetUrl(source.duong_dan))
}
function gio(value) {
  return dinhDangThoiGian(value, { hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit' })
}
function date(value) {
  return dinhDangNgay(value)
}
</script>
