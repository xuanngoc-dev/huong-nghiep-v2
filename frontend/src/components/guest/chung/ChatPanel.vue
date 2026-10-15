<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useChatStore } from '@/stores/chat'
import ChatMessage from './ChatMessage.vue'

const props = defineProps({ compact: Boolean })
const chat = useChatStore()
const list = ref(null)
const input = ref(null)
const stickToBottom = ref(true)
const hasUser = computed(() => chat.state.messages.some(m => m.role === 'user'))
const examples = ['Phương thức xét tuyển ngành Marketing trường NEU 2026?', 'Bách khoa Hà Nội có những ngành nào?', 'Những trường nào có ngành Công nghệ thông tin hoặc Logistics?']
const suggestions = computed(() => chat.state.suggestions.length ? chat.state.suggestions : !hasUser.value ? examples : [])
function onScroll() {
  const el = list.value
  if (el) stickToBottom.value = el.scrollHeight - el.scrollTop - el.clientHeight < 90
}
async function scroll() {
  await nextTick()
  if (list.value && stickToBottom.value) list.value.scrollTop = list.value.scrollHeight
}
function submit(text) {
  stickToBottom.value = true
  chat.send(typeof text === 'string' ? text : undefined)
}
function keydown(event) {
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
    event.preventDefault()
    submit()
  }
}
watch(() => [chat.state.messages.length, chat.state.messages.at(-1)?.text, chat.state.sending], scroll)
onMounted(() => { chat.loadModels(); scroll(); if (props.compact) input.value?.focus() })
</script>

<template>
  <div class="ai-chat" :class="{ 'is-compact': compact }">
    <div class="ai-chat__toolbar">
      <label>Mô hình AI
        <select v-model="chat.state.modelId" :disabled="chat.state.sending || chat.state.loadingModels" aria-label="Chọn mô hình AI">
          <option v-if="!chat.state.models.length" value="">{{ chat.state.loadingModels ? 'Đang tải…' : 'Chưa có model' }}</option>
          <option v-for="model in chat.state.models" :key="model.id" :value="model.id">{{ model.ten }}{{ model.san_sang ? '' : ' · Chưa sẵn sàng' }}</option>
        </select>
      </label>
      <button v-if="!chat.state.models.length && !chat.state.loadingModels" type="button" @click="chat.loadModels">Tải lại</button>
      <button type="button" :disabled="!hasUser && !chat.state.sending" @click="chat.clear">Hội thoại mới</button>
    </div>
    <p v-if="chat.state.storageWarning" class="ai-chat__notice" role="status">{{ chat.state.storageWarning }}</p>
    <p v-if="chat.state.error" class="ai-chat__error" role="alert">{{ chat.state.error }}</p>
    <div ref="list" class="ai-chat__thread" role="log" aria-label="Hội thoại tuyển sinh" aria-live="polite" aria-relevant="additions" :aria-busy="chat.state.sending" @scroll="onScroll">
      <ChatMessage v-for="(message, index) in chat.state.messages" :key="message.id" :message="message"
        :retryable="index === chat.state.messages.length - 1 && message.role === 'bot' && message.id !== 'welcome' && !chat.state.sending"
        @retry="chat.retry" />
    </div>
    <div v-if="suggestions.length" class="ai-chat__suggestions">
      <button v-for="question in suggestions" :key="question" type="button" :disabled="chat.state.sending" @click="submit(question)">{{ question }}</button>
    </div>
    <form class="ai-chat__composer" @submit.prevent="submit()">
      <textarea ref="input" v-model="chat.state.draft" maxlength="4000" :rows="compact ? 2 : 3" aria-label="Nội dung câu hỏi"
        placeholder="Hỏi về trường, ngành, tổ hợp, điểm hoặc điều kiện xét tuyển…" @keydown="keydown" />
      <button v-if="chat.state.sending" type="button" class="ai-chat__stop" @click="chat.stop()">Dừng</button>
      <button v-else type="submit" :disabled="!chat.state.draft.trim() || !chat.state.modelId">Gửi</button>
    </form>
    <small class="ai-chat__hint">Enter để gửi · Shift + Enter để xuống dòng · Kiểm tra nguồn trước khi quyết định.</small>
  </div>
</template>

<style lang="scss">
.ai-chat { display:flex; flex-direction:column; flex:1; min-height:0; color:#1c2b23; font-size:14px;
  button, select, textarea { font:inherit; }
  button { border:1px solid #c9ddd1; border-radius:8px; padding:6px 10px; background:#fff; color:#215b3d; cursor:pointer; }
  button:disabled { opacity:.5; cursor:not-allowed; }
  button:focus-visible, select:focus-visible, textarea:focus-visible, a:focus-visible { outline:2px solid #237b51; outline-offset:2px; }
  &__toolbar { display:flex; align-items:center; justify-content:space-between; gap:10px; padding:10px 14px; border-bottom:1px solid #e2ece5; flex-wrap:wrap; }
  &__toolbar label { display:flex; align-items:center; gap:8px; margin:0; }
  select { max-width:260px; padding:6px; border:1px solid #c9ddd1; border-radius:6px; background:#fff; color:inherit; }
  &__thread { display:flex; flex-direction:column; gap:16px; padding:18px; overflow-y:auto; flex:1; min-height:0; overscroll-behavior:contain; }
  &__message { max-width:95%; align-self:flex-start; padding:12px 16px; border-radius:12px; border:1px solid #e1ece5; background:#f6fbf8; overflow-wrap:anywhere; }
  &__message.is-user { align-self:flex-end; background:#237b51; color:#fff; max-width:85%; }
  &__user-text { white-space:pre-wrap; margin:0; }
  &__markdown p { margin:0 0 8px; white-space:pre-wrap; }
  &__markdown p:last-child { margin-bottom:0; }
  &__markdown ul, &__markdown ol { padding-left:22px; margin:8px 0; }
  &__markdown h3, &__markdown h4, &__markdown h5, &__markdown h6 { margin:12px 0 8px; font-size:1em; }
  &__markdown pre { max-width:100%; overflow-x:auto; padding:12px; background:#edf3ef; border-radius:8px; }
  &__markdown code { font-size:.9em; }
  &__math { font-family: Cambria, 'Times New Roman', serif; font-size:1.04em; font-style:italic; white-space:normal; }
  &__math--display { display:block; margin:10px 0; padding:10px 14px; border-left:3px solid #80a991; border-radius:0 8px 8px 0; background:#edf5f0; font-size:1.08em; line-height:1.7; overflow-wrap:anywhere; }
  &__markdown blockquote { border-left:3px solid #80a991; padding-left:12px; }
  &__table-wrap { overflow-x:auto; max-width:100%; margin:10px 0; }
  table { border-collapse:collapse; font-size:13px; min-width:300px; }
  th, td { padding:8px 10px; border:1px solid #d3e3d9; vertical-align:top; }
  th { background:#e7f3ec; }
  &__error { color:#a33a26; margin:8px 14px; }
  &__message &__error { margin:8px 0; }
  &__muted, &__pending { color:#607169; margin:4px 0; }
  &__notice, &__notes { padding:8px 14px; font-size:12px; color:#755622; background:#fff8e8; }
  &__notes { padding-left:26px; margin-top:10px; }
  &__sources { margin-top:12px; font-size:12px; }
  &__sources summary { cursor:pointer; color:#276246; }
  &__sources ol { padding-left:18px; }
  &__sources li { margin:10px 0; }
  &__sources small { display:block; color:#607169; }
  &__sources a { display:inline-block; margin:4px 12px 0 0; }
  &__message-actions { display:flex; gap:8px; align-items:center; flex-wrap:wrap; margin-top:10px; }
  &__message-actions small { flex:1; color:#607169; }
  &__message-actions button { font-size:12px; padding:3px 7px; }
  &__suggestions { display:flex; flex-wrap:wrap; gap:8px; padding:10px 14px; max-height:130px; overflow-y:auto; }
  &__suggestions button { text-align:left; font-size:13px; }
  &__composer { display:flex; gap:10px; align-items:flex-end; padding:12px 14px 4px; border-top:1px solid #e2ece5; }
  &__composer textarea { flex:1; min-width:0; resize:vertical; max-height:150px; padding:10px; border:1px solid #c9ddd1; border-radius:10px; }
  &__composer button { background:#237b51; color:#fff; padding:10px 16px; }
  &__composer &__stop { background:#fff; color:#a33a26; border-color:#dba999; }
  &__hint { color:#607169; padding:5px 14px 10px; font-size:11px; }
  &.is-compact { font-size:13px; }
  &.is-compact &__thread { padding:10px; gap:10px; }
  &.is-compact &__message { padding:10px; max-width:100%; }
  &.is-compact &__toolbar { padding:8px; gap:6px; }
  &.is-compact &__toolbar label { font-size:12px; }
  &.is-compact select { max-width:200px; font-size:12px; }
  &.is-compact &__hint { display:none; }
  @media(max-width:600px) { &__toolbar label { flex-wrap:wrap; } select { max-width:230px; } &__thread { padding:12px; } &__message { max-width:100%; } }
}
</style>
