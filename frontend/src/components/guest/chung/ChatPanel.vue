<template>
  <div class="ai-chat" :class="{ 'is-compact': compact }">
    <p v-if="chat.state.storageWarning" class="ai-chat__notice" role="status">{{ chat.state.storageWarning }}</p>
    <p v-if="chat.state.error" class="ai-chat__error" role="alert">
      {{ chat.state.error }}
      <RouterLink v-if="chat.state.hetToken" :to="{ name: 'nap-tien', query: { loai: 'token' } }">Nạp Token AI</RouterLink>
    </p>
    <p v-if="chat.state.daKetThuc" class="ai-chat__ended" role="status">
      Cuộc hội thoại này đã kết thúc. Bấm <button type="button" @click="chat.clear">Hội thoại mới</button> để tiếp tục hỏi đáp.
    </p>
    <div ref="list" class="ai-chat__thread" role="log" aria-label="Hội thoại tuyển sinh" aria-live="polite" aria-relevant="additions" :aria-busy="chat.state.sending" @scroll="onScroll">
      <ChatMessage v-for="(message, index) in chat.state.messages" :key="message.id" :message="message"
        :dau-nhom="!cungBen(chat.state.messages[index - 1], message)" :cuoi-nhom="!cungBen(chat.state.messages[index + 1], message)"
        :retryable="index === chat.state.messages.length - 1 && message.role === 'bot' && message.id !== 'welcome' && !message.local && !chat.state.sending && !chat.state.daKetThuc"
        @retry="chat.retry" />
      <!-- Hội thoại mới: mời chọn đối tượng (đã chọn sẵn theo trang đang xem); chọn xong hoặc gửi câu hỏi đầu thì ẩn.
           Đổi lại sau bằng nút cài đặt trên tiêu đề khung chat (tới khi gửi câu hỏi đầu). -->
      <div v-if="hienChonDoiTuong" class="ai-chat__chon-doi-tuong" role="group" aria-label="Chọn đối tượng người hỏi">
        <p>Bạn là ai? Chọn để trợ lý tư vấn đúng với hoàn cảnh của bạn:</p>
        <div class="ai-chat__chon-doi-tuong-ds">
          <button v-for="item in DOI_TUONG_HUONG_DEN" :key="item.ma" type="button"
            :class="{ 'is-active': item.ma === chat.state.doiTuongHuongDen }" :aria-pressed="item.ma === chat.state.doiTuongHuongDen"
            @click="chonDoiTuong(item.ma)">{{ item.label }}</button>
        </div>
      </div>
    </div>
    <div v-if="suggestions.length && !chat.state.daKetThuc" class="ai-chat__suggestions">
      <button v-for="question in suggestions" :key="question" type="button" :disabled="chat.state.sending" @click="submit(question)">{{ question }}</button>
    </div>
    <form class="ai-chat__composer" @submit.prevent="submit()">
      <div class="ai-chat__toolbar">
        <!-- Tạm ẩn chọn mô hình AI: luôn dùng mô hình mặc định (MODEL_MAC_DINH trong stores/chat.js).
        <label>Mô hình AI
          <select v-model="chat.state.modelId" :disabled="chat.state.sending || chat.state.loadingModels" aria-label="Chọn mô hình AI">
            <option v-if="!chat.state.models.length" value="">{{ chat.state.loadingModels ? 'Đang tải…' : 'Chưa có model' }}</option>
            <option v-for="model in chat.state.models" :key="model.id" :value="model.id">{{ model.ten }}{{ model.san_sang ? '' : ' · Chưa sẵn sàng' }}</option>
          </select>
        </label>
        -->
        <button v-if="!chat.state.models.length && !chat.state.loadingModels" type="button" @click="chat.loadModels">Tải lại trợ lý</button>
        <!-- <button type="button" :disabled="!hasUser && !chat.state.sending" @click="chat.clear">Hội thoại mới</button> -->
      </div>
      <div class="ai-chat__composer-row">
        <GoiYLenh :text="chat.state.draft" @chon="chonLenh" />
        <!-- :value + @input thay cho v-model: v-model bỏ qua chữ đang gõ dở của bộ gõ tiếng Việt (Telex/VNI) tới khi
             nhấn phím cách, nên nút Gửi bị khóa dù ô đã có chữ. -->
        <textarea ref="input" :value="chat.state.draft" maxlength="4000" :rows="compact ? 2 : 3" aria-label="Nội dung câu hỏi"
          @input="chat.state.draft = $event.target.value"
          :disabled="chat.state.daKetThuc"
          :placeholder="chat.state.daKetThuc ? 'Cuộc hội thoại đã kết thúc — mở hội thoại mới để hỏi tiếp.' : 'Hỏi về trường, ngành, tổ hợp, điểm…'"
          @keydown="keydown" />
        <!-- Khung chat nổi (compact): luôn có cả Gửi và Hủy xếp dọc bên phải; Hủy dừng câu trả lời đang chạy.
             Ô nhập trống và không đang trả lời thì Hủy thay bằng Kết thúc (kết thúc cuộc hội thoại, làm mới khung chat). -->
        <div v-if="compact" class="ai-chat__nut-gui">
          <button type="submit" :disabled="chat.state.sending || chat.state.daKetThuc || !chat.state.draft.trim() || !chat.state.modelId">Gửi</button>
          <button v-if="!chat.state.sending && !chat.state.draft.trim()" type="button" class="ai-chat__stop" :disabled="!hasUser && !chat.state.maPhien" @click="ketThuc">Kết thúc</button>
          <button v-else type="button" class="ai-chat__stop" :disabled="!chat.state.sending" @click="chat.stop()">Hủy</button>
        </div>
        <template v-else>
          <button v-if="chat.state.sending" type="button" class="ai-chat__stop" @click="chat.stop()">Dừng</button>
          <button v-else type="submit" :disabled="chat.state.daKetThuc || !chat.state.draft.trim() || !chat.state.modelId">Gửi</button>
        </template>
      </div>
    </form>
    <small class="ai-chat__hint">Enter để gửi · Shift + Enter để xuống dòng · Kiểm tra nguồn trước khi quyết định.</small>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useChatStore } from '@/stores/chat'
import ChatMessage from './ChatMessage.vue'
import GoiYLenh from './GoiYLenh.vue'
import { cuPhap, goiYLenh } from '@/utils/chatLenh'
import { DOI_TUONG_HUONG_DEN, cauHoiMau } from '@/constants/doiTuongHuongDen'

const props = defineProps({ compact: Boolean })
const chat = useChatStore()
const list = ref(null)
const input = ref(null)
const stickToBottom = ref(true)
const hasUser = computed(() => chat.state.messages.some(m => m.role === 'user'))
// Câu hỏi gợi ý khi chưa hỏi gì: theo đối tượng hướng đến (constants/doiTuongHuongDen.js).
const examples = computed(() => cauHoiMau(chat.state.doiTuongHuongDen))
const hienChonDoiTuong = computed(() => !chat.daChotDoiTuong && !chat.state.daChonDoiTuong && !chat.state.daKetThuc)
function chonDoiTuong(ma) {
  chat.chonDoiTuong(ma)
  input.value?.focus()
}
const suggestions = computed(() => chat.state.suggestions.length ? chat.state.suggestions : !hasUser.value ? examples.value : [])
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
async function ketThuc() {
  try {
    await ElMessageBox.confirm(
      'Kết thúc cuộc hội thoại này? Sau khi kết thúc bạn không thể hỏi tiếp trong cuộc này, khung chat sẽ được làm mới.',
      'Kết thúc hội thoại',
      { type: 'warning', confirmButtonText: 'Kết thúc', cancelButtonText: 'Hủy' },
    )
  } catch {
    return
  }
  try {
    await chat.ketThucHoiThoai()
    stickToBottom.value = true
    input.value?.focus()
  } catch (error) {
    ElMessage.error(error?.message || 'Không kết thúc được cuộc hội thoại. Vui lòng thử lại.')
  }
}
// Hai tin liền nhau cùng một bên (bạn / trợ lý) thì gộp nhóm như trang Danh sách hội thoại.
function cungBen(a, b) {
  return Boolean(a && b && a.role === b.role)
}
function chonLenh(lenh) {
  chat.state.draft = `/${lenh.ten}${lenh.thamSo ? ' ' : ''}`
  input.value?.focus()
}
function keydown(event) {
  // Tab: điền lệnh đầu tiên đang được gợi ý.
  const goiY = goiYLenh(chat.state.draft)
  if (event.key === 'Tab' && goiY.length && chat.state.draft !== cuPhap(goiY[0]).split(' ')[0]) {
    event.preventDefault()
    chonLenh(goiY[0])
    return
  }
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
    event.preventDefault()
    submit()
  }
}
watch(() => [chat.state.messages.length, chat.state.messages.at(-1)?.text, chat.state.sending], scroll)
onMounted(() => { chat.loadModels(); chat.kiemTraPhien(); scroll(); if (props.compact) input.value?.focus() })
</script>

<style lang="scss">
.ai-chat { display:flex; flex-direction:column; flex:1; min-height:0; color:#1c2b23; font-size:14px;
  button, select, textarea { font:inherit; }
  button { border:1px solid #c9ddd1; border-radius:8px; padding:6px 10px; background:#fff; color:#215b3d; cursor:pointer; }
  button:disabled { opacity:.5; cursor:not-allowed; }
  button:focus-visible, select:focus-visible, textarea:focus-visible, a:focus-visible { outline:2px solid #237b51; outline-offset:2px; }
  &__toolbar { display:flex; align-items:center; justify-content:flex-end; gap:10px; flex-wrap:wrap; }
  &__toolbar label { display:flex; align-items:center; gap:8px; margin:0; }
  select { max-width:260px; padding:6px; border:1px solid #c9ddd1; border-radius:6px; background:#fff; color:inherit; }
  /* Giống nội dung hội thoại ở trang Danh sách hội thoại (views/member/hoi-thoai/DanhSachHoiThoai.vue). */
  &__thread { display:flex; flex-direction:column; gap:6px; padding:18px; overflow-y:auto; flex:1; min-height:0; overscroll-behavior:contain; background:var(--el-fill-color-light, #f5f7fa); }
  &__nhom { display:flex; align-items:flex-start; gap:10px; }
  &__nhom.is-dau:not(:first-child) { margin-top:12px; }
  &__nhom.is-user { justify-content:flex-end; }
  &__than { display:flex; flex-direction:column; gap:4px; min-width:0; max-width:min(85%, 680px); }
  &__nhom.is-user &__than { align-items:flex-end; }
  /* Tin của trợ lý rộng hết khung chat, không có avatar để tiết kiệm diện tích. */
  &__nhom.is-bot &__than { flex:1; max-width:100%; }
  &__gio { color:var(--el-text-color-secondary, #607169); font-size:11px; }
  &__message { padding:9px 14px; border-radius:8px; background:var(--el-bg-color, #fff); box-shadow:0 1px 2px rgba(0,0,0,.06); color:var(--el-text-color-primary, #1c2b23); line-height:1.55; overflow-wrap:anywhere; }
  &__message.is-user { background:var(--el-color-primary, #237b51); color:#fff; }
  &__message.is-bot.is-error { background:var(--el-color-danger-light-9, #fef0f0); }
  &__user-text { white-space:pre-wrap; margin:0; }
  &__markdown p { margin:0 0 8px; white-space:pre-wrap; }
  &__markdown p:last-child { margin-bottom:0; }
  &__markdown ul, &__markdown ol { padding-left:22px; margin:8px 0; }
  &__markdown h3, &__markdown h4, &__markdown h5, &__markdown h6 { margin:12px 0 8px; font-size:1em; }
  /* Style code/pre của câu trả lời nằm ở ChatMarkdown.vue (dùng chung cho khung chat, trang quản trị, thành viên). */
  &__math { font-family: Cambria, 'Times New Roman', serif; font-size:1.04em; font-style:italic; white-space:normal; }
  &__math--display { display:block; margin:10px 0; padding:10px 14px; border-left:3px solid #80a991; border-radius:0 8px 8px 0; background:#edf5f0; font-size:1.08em; line-height:1.7; overflow-wrap:anywhere; }
  &__markdown blockquote { border-left:3px solid #80a991; padding-left:12px; }
  &__table-wrap { overflow-x:auto; max-width:100%; margin:10px 0; }
  table { border-collapse:collapse; font-size:13px; min-width:300px; }
  th, td { padding:8px 10px; border:1px solid #d3e3d9; vertical-align:top; }
  th { background:#e7f3ec; }
  &__error { color:#a33a26; margin:8px 14px; }
  &__ended { margin:0; padding:10px 14px; font-size:13px; color:#755622; background:#fff8e8; border-bottom:1px solid #f0e2bf; }
  &__ended button { padding:2px 8px; font-size:12px; }
  textarea:disabled { background:#f3f5f4; cursor:not-allowed; }
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
  &__chon-doi-tuong { margin-top:8px; padding:12px; border:1px solid #d3e3d9; border-radius:8px; background:var(--el-bg-color, #fff); box-shadow:0 1px 2px rgba(0,0,0,.06); }
  &__chon-doi-tuong p { margin:0 0 8px; }
  /* Nút dạng viên thuốc, đồng nhất với nút chọn đối tượng ở khung cài đặt (Chatbot.vue). */
  &__chon-doi-tuong-ds, &__suggestions { display:flex; flex-wrap:wrap; gap:6px; }
  &__chon-doi-tuong-ds button, &__suggestions button { font-size:12px; padding:5px 10px; border-radius:999px; text-align:left; }
  &__chon-doi-tuong-ds button:hover:not(:disabled), &__suggestions button:hover:not(:disabled) { border-color:#237b51; }
  &__chon-doi-tuong-ds button.is-active { background:#237b51; border-color:#237b51; color:#fff; }
  &__suggestions { padding:10px 14px; max-height:130px; overflow-y:auto; }
  &__composer { display:flex; flex-direction:column; gap:8px; align-items:stretch; padding:10px 14px 4px; border-top:1px solid #e2ece5; }
  &__composer-row { position:relative; display:flex; gap:10px; align-items:flex-end; }
  &__composer-row textarea { flex:1; min-width:0; resize:vertical; max-height:150px; padding:10px; border:1px solid #c9ddd1; border-radius:10px; }
  &__composer-row button { background:#237b51; color:#fff; padding:10px 16px; }
  &__composer-row &__stop { background:#fff; color:#a33a26; border-color:#dba999; }
  &__nut-gui { display:flex; flex-direction:column; gap:6px; }
  &.is-compact &__composer-row { align-items:stretch; }
  &.is-compact &__composer-row textarea { resize:none; }
  &.is-compact &__nut-gui button { padding:6px 14px; }
  &__hint { color:#607169; padding:5px 14px 10px; font-size:11px; }
  &.is-compact { font-size:13px; }
  &.is-compact &__thread { padding:10px; }
  &.is-compact &__nhom.is-user &__than { max-width:88%; }
  &.is-compact &__message { padding:8px 12px; }
  &.is-compact &__toolbar { gap:6px; }
  &.is-compact &__toolbar label { font-size:12px; }
  &.is-compact select { max-width:200px; font-size:12px; }
  &.is-compact &__hint { display:none; }
  @media(max-width:600px) { &__toolbar label { flex-wrap:wrap; } select { max-width:230px; } &__thread { padding:12px; } &__nhom.is-user &__than { max-width:90%; } }
}
</style>
