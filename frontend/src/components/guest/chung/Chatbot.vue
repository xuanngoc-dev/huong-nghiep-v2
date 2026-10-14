<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { hoiChat, layDanhSachModel } from '@/api/chat'

defineOptions({ name: 'Chatbot' })

const router = useRouter()
const open = ref(false)
const draft = ref('')
const listEl = ref(null)
const sending = ref(false)
const models = ref([])
const activeProvider = ref('gemini') // 'gemini' | 'openai'
const modelId = ref('')

const messages = ref([
  {
    id: 1,
    role: 'bot',
    text: 'Xin chào! Mình là trợ lý AI tuyển sinh 2026. Bạn có thể hỏi về các trường ĐH, ngành học, chỉ tiêu hoặc phương thức xét tuyển.',
  },
])

let nextId = 2

const geminiReady = computed(() =>
  models.value.some((item) => (item.provider === 'gemini' || item.id.includes('gemini')) && item.san_sang),
)
const openaiReady = computed(() =>
  models.value.some((item) => (item.provider === 'openai' || item.id.includes('gpt')) && item.san_sang),
)

const currentModel = computed(() => models.value.find((item) => item.id === modelId.value))
const geminiModel = computed(() => models.value.find((item) => item.provider === 'gemini' || item.id.includes('gemini')))
const openaiModel = computed(() => models.value.find((item) => item.provider === 'openai' || item.id.includes('gpt')))

onMounted(() => {
  napModel()
})

watch(open, (isOpen) => {
  if (isOpen) {
    if (!models.value.length) {
      napModel()
    }
    scrollToEnd()
  }
})

async function napModel() {
  try {
    models.value = await layDanhSachModel()
    if (geminiReady.value) {
      chonProvider('gemini')
    } else if (openaiReady.value) {
      chonProvider('openai')
    } else {
      chonProvider('gemini')
    }
  } catch {
    models.value = []
  }
}

function chonProvider(provider) {
  activeProvider.value = provider
  const list = models.value.filter((item) => {
    const prov = item.provider || (item.id.includes('gemini') ? 'gemini' : 'openai')
    return prov === provider
  })
  const ready = list.find((item) => item.san_sang)
  modelId.value = (ready || list[0])?.id || ''
}

function toggle() {
  open.value = !open.value
}

async function scrollToEnd() {
  await nextTick()
  if (listEl.value) listEl.value.scrollTop = listEl.value.scrollHeight
}

function xoaHoiThoai() {
  messages.value = messages.value.slice(0, 1)
  draft.value = ''
  sending.value = false
}

function moTrangDayDu() {
  open.value = false
  router.push('/demo-chat')
}

async function guiTin() {
  const text = draft.value.trim()
  if (!text || sending.value) return

  const model = currentModel.value
  if (!model?.san_sang) {
    const envKey = activeProvider.value === 'gemini' ? 'GEMINI_API_KEY' : 'OPENAI_API_KEY'
    messages.value.push({
      id: nextId++,
      role: 'bot',
      text: `Chưa có ${envKey} trong file .env. Bạn hãy cấu hình key trong .env để trò chuyện nhé!`,
    })
    await scrollToEnd()
    return
  }

  const lichSu = messages.value
    .filter((item) => item.id !== 1)
    .slice(-10)
    .map((item) => ({
      vai_tro: item.role === 'user' ? 'user' : 'bot',
      noi_dung: item.text,
    }))

  messages.value.push({ id: nextId++, role: 'user', text })
  draft.value = ''
  sending.value = true
  await scrollToEnd()

  try {
    const data = await hoiChat({
      cau_hoi: text,
      model_id: model.id,
      lich_su: lichSu,
    })
    messages.value.push({
      id: nextId++,
      role: 'bot',
      text: data.tra_loi,
      meta: data.model_ten || model.ten,
    })
  } catch (error) {
    const detail = error?.response?.data?.detail
    const msg = typeof detail === 'string' ? detail : 'Không thể kết nối với trợ lý AI. Vui lòng thử lại.'
    messages.value.push({
      id: nextId++,
      role: 'bot',
      text: msg,
    })
  } finally {
    sending.value = false
    await scrollToEnd()
  }
}
</script>

<template>
  <div class="chatbot">
    <section v-if="open" id="chatbot-panel" class="chatbot__panel" aria-label="Khung chat">
      <header class="chatbot__header">
        <div class="chatbot__title-wrap">
          <el-icon :size="18"><ChatDotRound /></el-icon>
          <strong>Trợ lý Tuyển sinh 2026</strong>
        </div>
        <div class="chatbot__header-actions">
          <button
            type="button"
            class="chatbot__btn-icon"
            title="Mở toàn màn hình / chi tiết"
            aria-label="Mở trang đầy đủ"
            @click="moTrangDayDu"
          >
            <el-icon :size="15"><FullScreen /></el-icon>
          </button>
          <button
            type="button"
            class="chatbot__btn-icon"
            title="Xóa hội thoại"
            aria-label="Xóa hội thoại"
            @click="xoaHoiThoai"
          >
            <el-icon :size="15"><Delete /></el-icon>
          </button>
          <button
            type="button"
            class="chatbot__close"
            title="Đóng khung chat"
            aria-label="Đóng khung chat"
            @click="open = false"
          >
            <el-icon :size="16"><Close /></el-icon>
          </button>
        </div>
      </header>

      <!-- Thanh chọn AI: Gemini hoặc OpenAI -->
      <div class="chatbot__provider-bar">
        <button
          type="button"
          class="chatbot__provider-btn"
          :class="{ 'is-active': activeProvider === 'gemini' }"
          @click="chonProvider('gemini')"
        >
          <span class="provider-dot" :class="{ 'is-ready': geminiReady }"></span>
          {{ geminiModel?.ten || 'Google Gemini' }}
          <small v-if="!geminiReady">(chưa có key)</small>
        </button>
        <button
          type="button"
          class="chatbot__provider-btn"
          :class="{ 'is-active': activeProvider === 'openai' }"
          @click="chonProvider('openai')"
        >
          <span class="provider-dot" :class="{ 'is-ready': openaiReady }"></span>
          {{ openaiModel?.ten || 'OpenAI GPT' }}
          <small v-if="!openaiReady">(chưa có key)</small>
        </button>
      </div>

      <!-- Danh sách tin nhắn -->
      <div ref="listEl" class="chatbot__list">
        <div
          v-for="message in messages"
          :key="message.id"
          class="chatbot__message"
          :class="`is-${message.role}`"
        >
          <p style="white-space: pre-wrap; margin: 0;">{{ message.text }}</p>
          <small v-if="message.meta" class="chatbot__meta">{{ message.meta }}</small>
        </div>
        <div v-if="sending" class="chatbot__message is-bot chatbot__typing">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>

      <!-- Form nhập câu hỏi -->
      <form class="chatbot__form" @submit.prevent="guiTin">
        <label class="visually-hidden" for="chatbot-input">Nội dung tin nhắn</label>
        <input
          id="chatbot-input"
          v-model="draft"
          class="chatbot__input"
          type="text"
          placeholder="Hỏi về tuyển sinh 2026..."
          autocomplete="off"
          :disabled="sending"
        />
        <button type="submit" class="chatbot__send" :disabled="!draft.trim() || sending">
          <el-icon :size="14"><Promotion /></el-icon>
        </button>
      </form>
    </section>

    <!-- Nút tròn nổi mở chatbot -->
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
