import { computed, reactive, ref, watch } from 'vue'
import { defineStore } from 'pinia'
import { hoiChatStream, layDanhSachModel, layTrangThaiPhien } from '@/api/chat'
import { fetchHoSo } from '@/api/hoSo'
import { createChatSession, fromServerMessages, newConversation } from '@/utils/chatSession'
import { clearHoSoCache, loadHoSo, toChatProfile } from '@/utils/hoSoCache'
import { maThietBi } from '@/utils/maThietBi'
import { useAuthStore } from '@/stores/auth'

export const useChatStore = defineStore('chat', () => {
  const auth = useAuthStore()
  const state = reactive({ messages: newConversation(), draft: '', sending: false, models: [], modelId: '',
    suggestions: [], error: '', loadingModels: false, storageWarning: '', context: null, maPhien: null, daKetThuc: false })
  const key = () => `huong-nghiep-chat-v2:${auth.user?.id || 'guest'}`
  function warmProfile() {
    const userId = auth.user?.id
    if (!auth.isAuthenticated || !userId) return
    loadHoSo(userId, fetchHoSo).catch(() => {})
  }
  async function loadProfile() {
    const userId = auth.user?.id
    if (!auth.isAuthenticated || !userId) return null
    try {
      return toChatProfile(await loadHoSo(userId, fetchHoSo))
    } catch {
      return null
    }
  }
  const session = createChatSession(state, { stream: hoiChatStream, storage: localStorage, storageKey: key, loadProfile,
    guestId: () => (auth.isAuthenticated ? null : maThietBi()) })
  // Phiên đang mở có thể đã bị quản trị kết thúc: hỏi server để khóa ô nhập ngay, không chờ tới lúc gửi.
  async function kiemTraPhien() {
    const ma = state.maPhien
    if (!ma) return
    try {
      const data = await layTrangThaiPhien(ma, auth.isAuthenticated ? null : maThietBi())
      if (state.maPhien === ma) state.daKetThuc = Boolean(data?.da_ket_thuc)
    } catch {
      // Không kiểm tra được thì để lần gửi sau server báo (409).
    }
  }
  session.restore()
  kiemTraPhien()
  // tinNhan: tin nhắn của phiên lấy từ API hội thoại của thành viên.
  function moHoiThoai(maPhien, tinNhan) {
    session.open(maPhien, fromServerMessages(tinNhan))
  }
  // Khung chat nổi (Chatbot.vue) — các nút "Hỏi trợ lý AI" mở khung này (trang /demo-chat đã tạm bỏ).
  const khungMo = ref(false)
  function moKhungChat(cauHoi) {
    if (typeof cauHoi === 'string' && cauHoi.trim() && !state.sending) state.draft = cauHoi
    khungMo.value = true
  }
  const model = computed(() => state.models.find(m => m.id === state.modelId))
  let loading = null
  async function loadModels() {
    if (loading) return loading
    state.loadingModels = true
    loading = (async () => {
      try {
        state.models = await layDanhSachModel()
        if (!state.models.some(m => m.id === state.modelId)) {
          state.modelId = (state.models.find(m => m.san_sang) || state.models[0])?.id || ''
        }
        state.error = ''
        session.persist()
      } catch {
        state.error = 'Không tải được danh sách model. Vui lòng thử tải lại.'
      } finally {
        state.loadingModels = false
        loading = null
      }
    })()
    return loading
  }
  warmProfile()
  watch(() => auth.user?.id, (userId, previousId) => {
    if (previousId && previousId !== userId) clearHoSoCache(previousId)
    session.restore()
    kiemTraPhien()
    loadModels()
    if (userId) warmProfile()
  })
  watch(() => [state.draft, state.modelId], () => session.persist())
  return { state, model, khungMo, moKhungChat, loadModels, kiemTraPhien, moHoiThoai, send: session.send, stop: session.stop, clear: session.clear, retry: session.retry }
})
