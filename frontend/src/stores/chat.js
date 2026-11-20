import { computed, reactive, ref, watch } from 'vue'
import { defineStore } from 'pinia'
import { hoiChatStream, ketThucPhienChat, layDanhSachModel, layTrangThaiPhien } from '@/api/chat'
import { fetchHoSo } from '@/api/hoSo'
import { DOI_TUONG_HUONG_DEN_MAC_DINH, laDoiTuongHuongDen } from '@/constants/doiTuongHuongDen'
import { phanTichLenh, taoBoChayLenh } from '@/utils/chatLenh'
import { createChatSession, fromServerMessages, newConversation } from '@/utils/chatSession'
import { clearHoSoCache, loadHoSo, toChatProfile } from '@/utils/hoSoCache'
import { maThietBi } from '@/utils/maThietBi'
import { useAuthStore } from '@/stores/auth'

// Mô hình AI luôn dùng (đã ẩn phần chọn mô hình); backend không có thì lấy mô hình sẵn sàng đầu tiên.
export const MODEL_MAC_DINH = 'gemini-3.8-flash'

export const useChatStore = defineStore('chat', () => {
  const auth = useAuthStore()
  const state = reactive({ messages: newConversation(), draft: '', sending: false, models: [], modelId: '',
    suggestions: [], error: '', loadingModels: false, storageWarning: '', context: null, maPhien: null, daKetThuc: false, hetToken: false,
    doiTuongHuongDen: DOI_TUONG_HUONG_DEN_MAC_DINH, daChonDoiTuong: false })
  const key = () => `huong-nghiep-chat-v2:${auth.user?.id || 'guest'}`
  function warmProfile() {
    const userId = auth.user?.id
    if (!auth.isAuthenticated || !userId) return
    loadHoSo(userId, fetchHoSo).catch(() => {})
  }
  // Hồ sơ cá nhân chỉ gửi kèm khi đối tượng là học sinh THPT (backend chỉ dùng hồ sơ cho nhóm này).
  async function loadProfile() {
    const userId = auth.user?.id
    if (!auth.isAuthenticated || !userId || !String(state.doiTuongHuongDen || '').startsWith('thpt-')) return null
    try {
      return toChatProfile(await loadHoSo(userId, fetchHoSo))
    } catch {
      return null
    }
  }
  // Đối tượng hướng đến theo trang đang xem (Chatbot.vue cập nhật khi đổi trang): mặc định cho hội thoại mới.
  const doiTuongTrang = ref(DOI_TUONG_HUONG_DEN_MAC_DINH)
  const session = createChatSession(state, { stream: hoiChatStream, storage: localStorage, storageKey: key, loadProfile,
    guestId: () => (auth.isAuthenticated ? null : maThietBi()), doiTuongMacDinh: () => doiTuongTrang.value })
  // Đã hỏi câu đầu (server đã chốt đối tượng vào phiên) thì không đổi đối tượng nữa.
  const daChotDoiTuong = computed(() => Boolean(state.maPhien) || state.messages.some(m => m.role === 'user' && !m.local))
  function datDoiTuongTrang(ma) {
    if (!laDoiTuongHuongDen(ma)) return
    doiTuongTrang.value = ma
    if (!daChotDoiTuong.value && !state.daChonDoiTuong && !state.sending) state.doiTuongHuongDen = ma
  }
  // Người dùng tự chọn đối tượng (thẻ chọn đầu khung chat / nút cài đặt): giữ lựa chọn này dù đổi trang.
  function chonDoiTuong(ma) {
    if (!laDoiTuongHuongDen(ma) || daChotDoiTuong.value || state.sending) return
    state.doiTuongHuongDen = ma
    state.daChonDoiTuong = true
  }
  // Phiên đang mở có thể đã bị quản trị kết thúc: hỏi server để khóa ô nhập ngay, không chờ tới lúc gửi.
  async function kiemTraPhien() {
    const ma = state.maPhien
    if (!ma) return
    try {
      const data = await layTrangThaiPhien(ma, auth.isAuthenticated ? null : maThietBi())
      if (state.maPhien !== ma) return
      state.daKetThuc = Boolean(data?.da_ket_thuc)
      if (laDoiTuongHuongDen(data?.doi_tuong_huong_den)) state.doiTuongHuongDen = data.doi_tuong_huong_den
    } catch {
      // Không kiểm tra được thì để lần gửi sau server báo (409).
    }
  }
  session.restore()
  kiemTraPhien()
  // tinNhan: tin nhắn của phiên lấy từ API hội thoại của thành viên; doiTuong: đối tượng hướng đến đã chốt của phiên.
  function moHoiThoai(maPhien, tinNhan, doiTuong) {
    session.open(maPhien, fromServerMessages(tinNhan), laDoiTuongHuongDen(doiTuong) ? doiTuong : null)
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
        // Luôn đặt lại về mô hình mặc định (kể cả khi trình duyệt còn lưu mô hình chọn trước đây).
        state.modelId = (state.models.find(m => m.id === MODEL_MAC_DINH) || state.models.find(m => m.san_sang)
          || state.models[0])?.id || ''
        // Trước đây giữ mô hình người dùng đã chọn:
        // if (!state.models.some(m => m.id === state.modelId)) {
        //   state.modelId = (state.models.find(m => m.san_sang) || state.models[0])?.id || ''
        // }
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
  async function ketThucPhien(ma) {
    try {
      return await ketThucPhienChat(ma, auth.isAuthenticated ? null : maThietBi())
    } catch (error) {
      const detail = error?.response?.data?.detail
      throw new Error(typeof detail === 'string' ? detail : 'Không kết thúc được cuộc hội thoại. Vui lòng thử lại.')
    }
  }
  // Nút "Kết thúc" ở khung chat nổi: kết thúc phiên trên server (nếu đã có phiên, chưa kết thúc) rồi làm mới khung chat.
  async function ketThucHoiThoai() {
    if (state.maPhien && !state.daKetThuc) await ketThucPhien(state.maPhien)
    session.clear()
  }
  // Lệnh "/..." trong khung chat (utils/chatLenh.js).
  const chayLenh = taoBoChayLenh({
    state,
    loadModels,
    ketThucPhien,
    saoChep: (vanBan) => navigator.clipboard.writeText(vanBan),
  })
  // Gửi từ khung chat nổi: tin bắt đầu bằng "/" là lệnh, chạy tại chỗ và hiện câu trả lời như tin nhắn cục bộ.
  async function send(input, retry = false) {
    const text = (typeof input === 'string' ? input : state.draft).trim()
    if (retry || state.sending || !phanTichLenh(text)) return session.send(input, retry)
    state.draft = ''
    state.error = ''
    const at = new Date().toISOString()
    const tinNhan = state.messages.filter(m => m.id !== 'welcome' && !m.local).map(m => ({ role: m.role, text: m.text }))
    const traLoi = await chayLenh(text, {
      maPhien: state.maPhien,
      tinNhan,
      moi: session.clear,
      thuLai() {
        if (!tinNhan.some(m => m.role === 'user')) return 'Chưa có câu hỏi nào để hỏi lại.'
        session.retry()
      },
    })
    if (!traLoi) return
    const id = () => `lenh-${Date.now()}-${Math.random().toString(36).slice(2)}`
    state.messages.push({ id: id(), role: 'user', text, status: 'done', local: true, at },
      { id: id(), role: 'bot', text: traLoi, status: 'done', local: true, sources: [], notes: [], meta: 'Trả lời lệnh', at })
    state.messages = state.messages.slice(-100)
    session.persist()
  }
  warmProfile()
  watch(() => auth.user?.id, (userId, previousId) => {
    if (previousId && previousId !== userId) clearHoSoCache(previousId)
    session.restore()
    kiemTraPhien()
    loadModels()
    if (userId) warmProfile()
  })
  watch(() => [state.draft, state.modelId, state.doiTuongHuongDen, state.daChonDoiTuong], () => session.persist())
  return { state, model, khungMo, moKhungChat, loadModels, kiemTraPhien, moHoiThoai, daChotDoiTuong, datDoiTuongTrang, chonDoiTuong, chayLenh, ketThucHoiThoai, send, stop: session.stop, clear: session.clear, retry: session.retry }
})
