<script setup>
import { ref } from 'vue'
import ChatMarkdown from './ChatMarkdown.vue'
import { safeLink } from '@/utils/chatMarkdown'

defineProps({ message: { type: Object, required: true }, retryable: Boolean })
defineEmits(['retry'])
const copyStatus = ref('')
async function copy(text) {
  try { await navigator.clipboard.writeText(text); copyStatus.value = 'Đã sao chép' }
  catch { copyStatus.value = 'Không thể sao chép' }
}
function dataLink(source) {
  if (!source.duong_dan?.startsWith('/')) return null
  const base = import.meta.env.VITE_API_BASE_URL
  return safeLink(base?.startsWith('http') ? new URL(source.duong_dan, base).href : source.duong_dan)
}
function date(value) {
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? '' : parsed.toLocaleDateString('vi-VN')
}
</script>

<template>
  <article class="ai-chat__message" :class="[`is-${message.role}`, `is-${message.status}`]">
    <ChatMarkdown v-if="message.role === 'bot'" :text="message.text" />
    <p v-else class="ai-chat__user-text">{{ message.text }}</p>
    <p v-if="message.status === 'streaming' && !message.text" class="ai-chat__pending" role="status">Đang tìm thông tin và soạn câu trả lời…</p>
    <p v-if="message.error" class="ai-chat__error" role="status">{{ message.error }}</p>
    <p v-else-if="message.status === 'cancelled' && message.text !== 'Đã dừng trả lời.'" class="ai-chat__muted">Đã dừng trả lời.</p>
    <ul v-if="message.notes?.length" class="ai-chat__notes">
      <li v-for="note in message.notes" :key="note">{{ note }}</li>
    </ul>
    <details v-if="message.sources?.length" class="ai-chat__sources">
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
    <footer v-if="message.role === 'bot' && message.id !== 'welcome'" class="ai-chat__message-actions">
      <small>{{ message.meta }}</small>
      <button v-if="message.text" type="button" @click="copy(message.text)">{{ copyStatus || 'Sao chép' }}</button>
      <button v-if="retryable" type="button" @click="$emit('retry')">Thử lại</button>
    </footer>
  </article>
</template>
