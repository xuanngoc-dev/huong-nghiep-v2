export const WELCOME = 'Xin chào! Mình có thể giúp bạn tra cứu ngành học, trường, tổ hợp, điểm và điều kiện tuyển sinh. Bạn muốn tìm hiểu trường hoặc ngành nào?'
export const newConversation = () => [{ id: 'welcome', role: 'bot', text: WELCOME, status: 'done', sources: [], notes: [] }]

/** Tin nhắn đã lưu trên server (chat_messages) → tin nhắn của khung chat, để mở lại hội thoại cũ. */
export function fromServerMessages(tinNhan) {
  const messages = []
  for (const m of Array.isArray(tinNhan) ? tinNhan : []) {
    if (m.loai_nguoi_gui === 'user') {
      if (m.noi_dung_tin_nhan) messages.push({ id: `s${m.id}`, role: 'user', text: m.noi_dung_tin_nhan.slice(0, 16000), status: 'done', at: m.created_at })
      continue
    }
    const loi = m.trang_thai === 'loi'
    messages.push({ id: `s${m.id}`, role: 'bot', text: (m.noi_dung_phan_hoi || '').slice(0, 16000), status: loi ? 'error' : 'done',
      ...(loi ? { error: m.loi_chi_tiet || 'Không trả lời được.' } : {}),
      sources: Array.isArray(m.nguon_tham_khao) ? m.nguon_tham_khao : [], notes: [], meta: m.model_ai || undefined, at: m.created_at })
  }
  return messages.slice(-100)
}

/** One request owner per shared conversation; stale requests cannot update a new conversation. */
// state.maPhien: mã phiên hội thoại phía server (chat_conversations.ma_dinh_danh), nhận ở sự kiện meta/done của câu hỏi
// đầu và gửi lại ở các câu sau để cùng một phiên; hội thoại mới thì bỏ. guestId(): mã thiết bị khi là khách.
// state.daKetThuc: phiên đã bị quản trị kết thúc (server trả 409) — không gửi tiếp, phải mở hội thoại mới.
// Tin nhắn có local: true là lệnh "/..." và câu trả lời của lệnh (utils/chatLenh.js): chỉ hiện, không gửi kèm lịch sử.
// state.doiTuongHuongDen: đối tượng hướng đến (constants/doiTuongHuongDen.js) gửi kèm câu hỏi; server chốt vào phiên ở câu
// đầu. doiTuongMacDinh(): đối tượng cho hội thoại mới (theo trang đang xem). state.daChonDoiTuong: người dùng đã tự chọn
// đối tượng trong hội thoại này (khung chat thôi hiện thẻ chọn đối tượng).
export function createChatSession(state, { stream, storage, storageKey, loadProfile, guestId, doiTuongMacDinh }) {
  let controller = null
  let revision = 0
  let saveTimer = null
  const id = () => `${Date.now()}-${Math.random().toString(36).slice(2)}`
  const macDinh = () => (typeof doiTuongMacDinh === 'function' ? doiTuongMacDinh() : '') || ''
  function persist() {
    clearTimeout(saveTimer)
    try {
      storage.setItem(storageKey(), JSON.stringify({ version: 2, modelId: state.modelId, draft: state.draft, context: state.context,
        ...(state.maPhien ? { maPhien: state.maPhien } : {}),
        ...(state.doiTuongHuongDen ? { doiTuongHuongDen: state.doiTuongHuongDen } : {}),
        ...(state.daChonDoiTuong ? { daChonDoiTuong: true } : {}),
        messages: state.messages.slice(-100).map(m => ({ ...m, status: m.status === 'streaming' ? 'cancelled' : m.status })) }))
      state.storageWarning = ''
    } catch {
      state.storageWarning = 'Trình duyệt không lưu được hội thoại. Bạn vẫn có thể tiếp tục trò chuyện.'
    }
  }
  function restore() {
    stop(false)
    state.messages = newConversation()
    state.draft = ''
    state.modelId = ''
    state.context = null
    state.maPhien = null
    state.daKetThuc = false
    state.doiTuongHuongDen = macDinh()
    state.daChonDoiTuong = false
    state.suggestions = []
    state.error = ''
    try {
      const saved = JSON.parse(storage.getItem(storageKey()) || 'null')
      if (saved?.version !== 2 || !Array.isArray(saved.messages)) return
      const valid = saved.messages.filter(m => m && ['bot', 'user'].includes(m.role) && typeof m.text === 'string' && m.text.length <= 16000).slice(-100)
      state.messages = valid.length ? valid.map(m => ({ ...m, status: m.status === 'streaming' ? 'cancelled' : m.status,
        sources: Array.isArray(m.sources) ? m.sources : [], notes: Array.isArray(m.notes) ? m.notes : [] })) : newConversation()
      state.modelId = typeof saved.modelId === 'string' ? saved.modelId : ''
      if (typeof saved.maPhien === 'string' && saved.maPhien.length <= 36) state.maPhien = saved.maPhien
      if (typeof saved.doiTuongHuongDen === 'string' && saved.doiTuongHuongDen.length <= 50) state.doiTuongHuongDen = saved.doiTuongHuongDen
      state.daChonDoiTuong = saved.daChonDoiTuong === true
      state.draft = typeof saved.draft === 'string' ? saved.draft.slice(0, 4000) : ''
      if (saved.context && typeof saved.context === 'object' && !Array.isArray(saved.context)) {
        state.context = {
          ma_truong: Array.isArray(saved.context.ma_truong) ? saved.context.ma_truong.filter(x => typeof x === 'string' && x.length <= 32).slice(0, 50) : [],
          nganh: Array.isArray(saved.context.nganh) ? saved.context.nganh.filter(x => typeof x === 'string' && x.length <= 500).slice(0, 20) : [],
          nam: Number.isInteger(saved.context.nam) && saved.context.nam >= 1900 && saved.context.nam <= 2200 ? saved.context.nam : null,
        }
        if (Number.isFinite(saved.context.diem) && saved.context.diem >= 0 && saved.context.diem <= 100000) state.context.diem = saved.context.diem
        if (Array.isArray(saved.context.to_hop)) state.context.to_hop = saved.context.to_hop.filter(x => typeof x === 'string' && /^[A-Z]\d{2}$/.test(x)).slice(0, 10)
        if (typeof saved.context.khu_vuc === 'string' && saved.context.khu_vuc.length <= 200) state.context.khu_vuc = saved.context.khu_vuc
        if (typeof saved.context.nguon_diem === 'string' && saved.context.nguon_diem.length <= 100) state.context.nguon_diem = saved.context.nguon_diem
        if (typeof saved.context.tom_tat === 'string' && saved.context.tom_tat.length <= 2000) state.context.tom_tat = saved.context.tom_tat
        if (Number.isInteger(saved.context.nam_du_tuyen) && saved.context.nam_du_tuyen >= 1900 && saved.context.nam_du_tuyen <= 2200) state.context.nam_du_tuyen = saved.context.nam_du_tuyen
      }
    } catch {
      state.storageWarning = 'Không đọc được lịch sử đã lưu. Một hội thoại mới đã được mở.'
    }
  }
  function stop(save = true) {
    revision++
    clearTimeout(saveTimer)
    controller?.abort()
    controller = null
    for (const message of state.messages) {
      if (message.status === 'streaming') {
        message.status = 'cancelled'
        if (!message.text) message.text = 'Đã dừng trả lời.'
      }
    }
    state.sending = false
    if (save) persist()
  }
  function clear() {
    stop()
    state.messages = newConversation()
    state.draft = ''
    state.context = null
    state.maPhien = null
    state.daKetThuc = false
    state.doiTuongHuongDen = macDinh()
    state.daChonDoiTuong = false
    persist()
  }
  // Mở lại một phiên đã lưu trên server (trang Danh sách hội thoại) để hỏi tiếp trong cùng phiên.
  function open(maPhien, messages, doiTuongHuongDen) {
    stop(false)
    state.messages = messages.length ? messages : newConversation()
    state.maPhien = maPhien
    state.daKetThuc = false
    state.doiTuongHuongDen = doiTuongHuongDen || macDinh()
    state.daChonDoiTuong = true
    state.context = null
    state.suggestions = []
    state.draft = ''
    state.error = ''
    persist()
  }
  async function send(input, retry = false) {
    const text = (typeof input === 'string' ? input : state.draft).trim()
    if (!text || state.sending || state.daKetThuc) return
    if (text.length > 4000) {
      state.error = 'Câu hỏi tối đa 4.000 ký tự.'
      return
    }
    const model = state.models.find(m => m.id === state.modelId)
    if (!model) {
      state.error = 'Chưa tải được danh sách model. Vui lòng thử tải lại.'
      return
    }
    state.error = ''
    state.hetToken = false
    state.suggestions = []
    if (retry) {
      const lastUserIndex = state.messages.findLastIndex(m => m.role === 'user' && !m.local)
      if (lastUserIndex < 0) return
      state.messages = state.messages.slice(0, lastUserIndex)
    }
    const history = []
    let budget = 24000
    for (const message of [...state.messages].reverse()) {
      if (history.length >= 30) break
      if (message.id === 'welcome' || message.local || (message.role === 'bot' && message.status !== 'done')) continue
      if (message.text.length > budget) break
      history.unshift({ vai_tro: message.role === 'user' ? 'user' : 'bot', noi_dung: message.text })
      budget -= message.text.length
    }
    const botId = id()
    // at: thời điểm gửi, để trang Danh sách hội thoại hiện giờ của tin nhắn đang gửi.
    const at = new Date().toISOString()
    state.messages.push({ id: id(), role: 'user', text, status: 'done', at },
      { id: botId, role: 'bot', text: '', status: 'streaming', sources: [], notes: [], meta: model.ten, at })
    state.messages = state.messages.slice(-100)
    state.draft = ''
    state.sending = true
    const owner = ++revision
    const requestController = new AbortController()
    controller = requestController
    persist()
    let hoSo = null
    if (typeof loadProfile === 'function') {
      try {
        hoSo = await loadProfile()
      } catch {
        hoSo = null
      }
    }
    if (owner !== revision) return
    const payload = { cau_hoi: text, model_id: model.id, lich_su: history, ngu_canh: state.context || null,
      ma_phien: state.maPhien || null, doi_tuong_huong_den: state.doiTuongHuongDen || null }
    const maKhach = typeof guestId === 'function' ? guestId() : null
    if (maKhach) payload.ma_khach_vang_lai = maKhach
    if (hoSo) payload.ho_so = hoSo
    try {
      await stream(payload, {
        signal: requestController.signal,
        timeoutMs: (model.timeout_giay || 75) * 1000 + 15000,
        onEvent(event, data) {
          if (owner !== revision) return
          const bot = state.messages.find(m => m.id === botId)
          if (!bot) return
          if (event === 'meta' || event === 'done') {
            if (typeof data.ma_phien === 'string' && data.ma_phien) state.maPhien = data.ma_phien
            if (data.ngu_canh && typeof data.ngu_canh === 'object') state.context = data.ngu_canh
            bot.sources = data.nguon || []
            bot.notes = data.ghi_chu || []
            bot.meta = data.model_ten || bot.meta
            state.suggestions = data.goi_y || []
          }
          if (event === 'model') bot.meta = data.model_ten
          if (event === 'delta') bot.text = (bot.text + data.text).slice(0, 16000)
          if (event === 'done') {
            bot.text = data.tra_loi
            bot.status = 'done'
          }
          clearTimeout(saveTimer)
          saveTimer = setTimeout(persist, 300)
        },
      })
    } catch (error) {
      if (owner !== revision) return
      if (error?.status === 409) {
        state.daKetThuc = true
        state.suggestions = []
      }
      // 402: thành viên hết token AI — báo ở thanh lỗi, giao diện mời nạp gói Token AI (state.hetToken).
      if (error?.status === 402) {
        state.error = error.message
        state.hetToken = true
      }
      const bot = state.messages.find(m => m.id === botId)
      if (bot) {
        bot.status = requestController.signal.aborted ? 'cancelled' : 'error'
        bot.error = requestController.signal.aborted ? 'Đã dừng trả lời.' : error.message || 'Không thể kết nối với trợ lý AI.'
      }
    } finally {
      if (owner === revision) {
        state.sending = false
        controller = null
        persist()
      }
    }
  }
  function retry() {
    const last = [...state.messages].reverse().find(m => m.role === 'user' && !m.local)
    if (last) return send(last.text, true)
  }
  return { send, retry, stop, clear, restore, persist, open }
}
