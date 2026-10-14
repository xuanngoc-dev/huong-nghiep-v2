<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { hoiChat, layDanhSachModel, layTaiLieu, taiTaiLieu, xoaTaiLieu } from '@/api/chat'

defineOptions({ name: 'DemoChat' })

const draft = ref('')
const listEl = ref(null)
const fileInput = ref(null)
const sending = ref(false)
const uploading = ref(false)
const models = ref([])
const modelId = ref('')
const taiLieu = ref([])
const messages = ref([
  {
    id: 1,
    role: 'bot',
    text: 'Xin chào. Mình trả lời theo các file .json và .txt bạn tải lên, hoặc file đã có trong thư mục tài liệu.',
  },
])

const suggestions = [
  'Tài liệu này nói về những hướng nào?',
  'Tóm tắt nội dung các file đã tải.',
  'Điều kiện nào được nêu trong tài liệu?',
]

const hasUserMessage = computed(() => messages.value.some((item) => item.role === 'user'))
const modelHienTai = computed(() => models.value.find((item) => item.id === modelId.value))

let nextId = 2

onMounted(async () => {
  await Promise.all([napModel(), napTaiLieu()])
})

async function napModel() {
  try {
    models.value = await layDanhSachModel()
    const sanSang = models.value.filter((item) => item.san_sang)
    const macDinh = sanSang.find((item) => !item.phi) || sanSang[0] || models.value[0]
    if (macDinh && !models.value.some((item) => item.id === modelId.value && item.san_sang)) {
      modelId.value = macDinh.id
    }
  } catch {
    models.value = []
  }
}

async function napTaiLieu() {
  try {
    taiLieu.value = await layTaiLieu()
  } catch {
    taiLieu.value = []
  }
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
    messages.value.push({
      id: nextId++,
      role: 'bot',
      text: 'Model này chưa có API key. Thêm GEMINI_API_KEY hoặc OPENAI_API_KEY vào backend/.env rồi chạy lại API.',
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
    const nguon = data.tai_lieu?.length ? data.tai_lieu.join(', ') : ''
    messages.value.push({
      id: nextId++,
      role: 'bot',
      text: data.tra_loi,
      meta: [data.model_ten, nguon].filter(Boolean).join(' · '),
    })
  } catch (error) {
    messages.value.push({
      id: nextId++,
      role: 'bot',
      text: loiChiTiet(error, 'Không hỏi được trợ lý. Hãy thử lại.'),
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

function moChonTep() {
  fileInput.value?.click()
}

async function chonTep(event) {
  const files = [...(event.target.files || [])]
  event.target.value = ''
  if (!files.length || uploading.value) return

  uploading.value = true
  try {
    for (const file of files) {
      await taiTaiLieu(file)
    }
    await napTaiLieu()
    ElMessage.success(files.length > 1 ? `Đã tải ${files.length} file` : 'Đã tải tài liệu')
  } catch (error) {
    ElMessage.error(loiChiTiet(error, 'Không tải được tài liệu.'))
    await napTaiLieu()
  } finally {
    uploading.value = false
  }
}

async function xoaTep(ten) {
  try {
    await ElMessageBox.confirm(`Xóa file ${ten}?`, 'Tài liệu', {
      confirmButtonText: 'Xóa',
      cancelButtonText: 'Hủy',
      type: 'warning',
    })
  } catch {
    return
  }

  try {
    await xoaTaiLieu(ten)
    await napTaiLieu()
  } catch (error) {
    ElMessage.error(loiChiTiet(error, 'Không xóa được tài liệu.'))
  }
}

function kichThuoc(bytes) {
  if (bytes < 1024) return `${bytes} B`
  const kb = bytes / 1024
  return `${kb.toFixed(kb < 10 ? 1 : 0)} KB`
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
            <h1>Trợ lý định hướng</h1>
            <p>Hỏi đáp theo tài liệu json/txt</p>
          </div>
        </div>
        <button type="button" class="btn btn-outline-success btn-sm" :disabled="!hasUserMessage" @click="xoaHoiThoai">
          Xóa hội thoại
        </button>
      </header>

      <div class="demo-chat__tools">
        <label class="visually-hidden" for="demo-chat-model">Model</label>
        <select id="demo-chat-model" v-model="modelId" class="demo-chat__model" :disabled="sending || !models.length">
          <option v-for="model in models" :key="model.id" :value="model.id" :disabled="!model.san_sang">
            {{ model.ten }} · {{ model.phi ? 'Có phí' : 'Miễn phí' }}{{ model.san_sang ? '' : ' · chưa có API key' }}
          </option>
        </select>
        <button type="button" class="btn btn-success btn-sm" :disabled="uploading" @click="moChonTep">
          {{ uploading ? 'Đang tải…' : 'Tải tài liệu' }}
        </button>
        <input
          ref="fileInput"
          class="visually-hidden"
          type="file"
          accept=".json,.txt,application/json,text/plain"
          multiple
          @change="chonTep"
        />
      </div>

      <div class="demo-chat__files" :class="{ 'is-empty': !taiLieu.length }">
        <p v-if="!taiLieu.length" class="demo-chat__empty">
          Chưa có file. Tải .json/.txt hoặc bỏ file vào backend/tai_lieu.
        </p>
        <span v-for="file in taiLieu" :key="file.ten" class="demo-chat__file">
          <span>{{ file.ten }}</span>
          <small>{{ kichThuoc(file.kich_thuoc) }}</small>
          <button type="button" :aria-label="`Xóa ${file.ten}`" @click="xoaTep(file.ten)">×</button>
        </span>
      </div>

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
            <p>{{ message.text }}</p>
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

      <div v-if="!hasUserMessage" class="demo-chat__suggestions">
        <button v-for="item in suggestions" :key="item" type="button" :disabled="sending" @click="guiTin(item)">
          {{ item }}
        </button>
      </div>

      <form class="demo-chat__composer" @submit.prevent="guiTin()">
        <label class="visually-hidden" for="demo-chat-input">Nội dung tin nhắn</label>
        <textarea
          id="demo-chat-input"
          v-model="draft"
          rows="2"
          placeholder="Hỏi theo tài liệu đã tải"
          @keydown="onKeydown"
        />
        <button class="demo-chat__send" type="submit" :disabled="!draft.trim() || sending" aria-label="Gửi">
          <el-icon :size="18"><Promotion /></el-icon>
        </button>
      </form>
    </div>
  </section>
</template>
