<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { hoiChat, layDanhSachModel } from '@/api/chat'

defineOptions({ name: 'DemoChat' })

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
    text: 'Xin chào! Mình là trợ lý tuyển sinh và định hướng nghề nghiệp 2026. Bạn có thể hỏi về đề án tuyển sinh, phương thức xét tuyển, điểm sàn, tổ hợp môn hoặc chỉ tiêu của các trường đại học.',
  },
])

const suggestions = [
  'Phương thức xét tuyển ngành Marketing trường NEU 2026?',
  'Đại học Bách khoa Hà Nội tuyển sinh những ngành nào và chỉ tiêu ra sao?',
  'Những trường nào có ngành Công nghệ thông tin hoặc Logistics?',
  'Điều kiện tuyển sinh chung của trường Sư phạm Kỹ thuật TP.HCM UTE là gì?',
]

const hasUserMessage = computed(() => messages.value.some((item) => item.role === 'user'))

const modelHienTai = computed(() => models.value.find((item) => item.id === modelId.value))

const geminiReady = computed(() =>
  models.value.some((item) => (item.provider === 'gemini' || item.id.includes('gemini')) && item.san_sang),
)
const openaiReady = computed(() =>
  models.value.some((item) => (item.provider === 'openai' || item.id.includes('gpt')) && item.san_sang),
)

let nextId = 2

onMounted(async () => {
  await napModel()
})

async function napModel() {
  try {
    models.value = await layDanhSachModel()
    // Tự động chọn model có key sẵn hoặc model đầu tiên
    const ready = models.value.find((item) => item.san_sang)
    const selected = ready || models.value[0]
    if (selected) {
      modelId.value = selected.id
      activeProvider.value = selected.provider || (selected.id.includes('gemini') ? 'gemini' : 'openai')
    }
  } catch {
    models.value = []
  }
}

function chonModel(model) {
  modelId.value = model.id
  activeProvider.value = model.provider || (model.id.includes('gemini') ? 'gemini' : 'openai')
}

async function scrollToEnd() {
  await nextTick()
  if (listEl.value) listEl.value.scrollTop = listEl.value.scrollHeight
}

function loiChiTiet(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    const text = detail.map((item) => item?.msg).filter(Boolean).join(', ')
    if (text) return text
  }
  return fallback
}

async function guiTin(text) {
  const content = (typeof text === 'string' ? text : draft.value).trim()
  if (!content || sending.value) return

  const model = modelHienTai.value
  if (!model?.san_sang) {
    const envKey = activeProvider.value === 'gemini' ? 'GEMINI_API_KEY' : 'OPENAI_API_KEY'
    messages.value.push({
      id: nextId++,
      role: 'bot',
      text: `Model này chưa có API key. Bạn hãy thêm ${envKey} vào file .env rồi thử lại nhé!`,
    })
    await scrollToEnd()
    return
  }

  const lichSu = messages.value
    .filter((item) => item.id !== 1)
    .slice(-12)
    .map((item) => ({
      vai_tro: item.role === 'user' ? 'user' : 'bot',
      noi_dung: item.text,
    }))

  messages.value.push({ id: nextId++, role: 'user', text: content })
  draft.value = ''
  sending.value = true
  await scrollToEnd()

  try {
    const data = await hoiChat({
      cau_hoi: content,
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
    messages.value.push({
      id: nextId++,
      role: 'bot',
      text: loiChiTiet(error, 'Không nhận được phản hồi từ AI. Hãy thử lại hoặc đổi model khác.'),
    })
  } finally {
    sending.value = false
    await scrollToEnd()
  }
}

function onKeydown(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    guiTin()
  }
}

function xoaHoiThoai() {
  messages.value = messages.value.slice(0, 1)
  draft.value = ''
  sending.value = false
}
</script>

<template>
  <section class="demo-chat">
    <div class="demo-chat__shell">
      <header class="demo-chat__header">
        <div class="demo-chat__identity">
          <span class="demo-chat__avatar" aria-hidden="true">
            <el-icon :size="22"><ChatDotRound /></el-icon>
          </span>
          <div>
            <h1>Trợ lý tư vấn tuyển sinh & định hướng</h1>
            <p>Hỏi đáp thông minh về tuyển sinh đại học & định hướng nghề nghiệp 2026</p>
          </div>
        </div>
        <button type="button" class="btn btn-outline-success btn-sm" :disabled="!hasUserMessage" @click="xoaHoiThoai">
          Xóa hội thoại
        </button>
      </header>

      <!-- Thanh chọn Model hỏi đáp -->
      <div class="demo-chat__model-bar">
        <div class="demo-chat__model-label">
          <el-icon class="me-1"><Cpu /></el-icon>
          <span>Mô hình AI:</span>
        </div>

        <div class="demo-chat__provider-tabs" role="tablist">
          <button
            v-for="item in models"
            :key="item.id"
            type="button"
            class="demo-chat__tab"
            :class="{ 'is-active': modelId === item.id }"
            @click="chonModel(item)"
          >
            <span class="tab-indicator" :class="{ 'is-ready': item.san_sang }"></span>
            <strong>{{ item.ten }}</strong>
            <span class="tab-badge" :class="item.phi ? 'is-paid' : 'is-free'">
              {{ item.phi ? 'OpenAI' : 'Miễn phí' }}
            </span>
            <span class="tab-status">{{ item.san_sang ? 'Sẵn sàng' : 'Chưa có key' }}</span>
          </button>
        </div>

        <div v-if="modelHienTai?.mo_ta" class="demo-chat__model-desc">
          <small class="text-muted">{{ modelHienTai.mo_ta }}</small>
        </div>
      </div>

      <!-- Khung hội thoại chat -->
      <div ref="listEl" class="demo-chat__thread" role="log" aria-live="polite" aria-relevant="additions">
        <article
          v-for="message in messages"
          :key="message.id"
          class="demo-chat__row"
          :class="`is-${message.role}`"
        >
          <span v-if="message.role === 'bot'" class="demo-chat__mark" aria-hidden="true">
            <el-icon :size="16"><ChatDotRound /></el-icon>
          </span>
          <div class="demo-chat__bubble">
            <p style="white-space: pre-wrap;">{{ message.text }}</p>
            <small v-if="message.meta" class="demo-chat__meta">{{ message.meta }}</small>
          </div>
        </article>
        <article v-if="sending" class="demo-chat__row is-bot">
          <span class="demo-chat__mark" aria-hidden="true">
            <el-icon :size="16"><ChatDotRound /></el-icon>
          </span>
          <p class="demo-chat__bubble demo-chat__typing" aria-label="Đang soạn câu trả lời">
            <span></span>
            <span></span>
            <span></span>
          </p>
        </article>
      </div>

      <!-- Câu hỏi gợi ý -->
      <div v-if="!hasUserMessage" class="demo-chat__suggestions">
        <button v-for="item in suggestions" :key="item" type="button" :disabled="sending" @click="guiTin(item)">
          {{ item }}
        </button>
      </div>

      <!-- Khung nhập tin nhắn -->
      <form class="demo-chat__composer" @submit.prevent="guiTin()">
        <label class="visually-hidden" for="demo-chat-input">Nội dung tin nhắn</label>
        <textarea
          id="demo-chat-input"
          v-model="draft"
          rows="2"
          placeholder="Hỏi về ngành học, trường đại học, chỉ tiêu, điểm sàn tuyển sinh 2026... (Enter để gửi)"
          @keydown="onKeydown"
        />
        <button class="demo-chat__send" type="submit" :disabled="!draft.trim() || sending" aria-label="Gửi">
          <el-icon :size="18"><Promotion /></el-icon>
        </button>
      </form>
    </div>
  </section>
</template>
