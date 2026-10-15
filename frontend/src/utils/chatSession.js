export const WELCOME = 'Xin chào! Mình có thể giúp bạn tra cứu ngành học, trường, tổ hợp, điểm và điều kiện tuyển sinh. Bạn muốn tìm hiểu trường hoặc ngành nào?'
export const newConversation = () => [{ id: 'welcome', role: 'bot', text: WELCOME, status: 'done', sources: [], notes: [] }]

/** One request owner per shared conversation; stale requests cannot update a new conversation. */
export function createChatSession(state, { stream, storage, storageKey, loadProfile }) {
  let controller = null
  let revision = 0
  let saveTimer = null
  const id = () => `${Date.now()}-${Math.random().toString(36).slice(2)}`
  function persist() {
    clearTimeout(saveTimer)
    try {
      storage.setItem(storageKey(), JSON.stringify({ version: 2, modelId: state.modelId, draft: state.draft, context: state.context,
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
    state.suggestions = []
    state.error = ''
    try {
      const saved = JSON.parse(storage.getItem(storageKey()) || 'null')
      if (saved?.version !== 2 || !Array.isArray(saved.messages)) return
      const valid = saved.messages.filter(m => m && ['bot', 'user'].includes(m.role) && typeof m.text === 'string' && m.text.length <= 16000).slice(-100)
      state.messages = valid.length ? valid.map(m => ({ ...m, status: m.status === 'streaming' ? 'cancelled' : m.status,
        sources: Array.isArray(m.sources) ? m.sources : [], notes: Array.isArray(m.notes) ? m.notes : [] })) : newConversation()
      state.modelId = typeof saved.modelId === 'string' ? saved.modelId : ''
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
    persist()
  }
  async function send(input, retry = false) {
    const text = (typeof input === 'string' ? input : state.draft).trim()
    if (!text || state.sending) return
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
    state.suggestions = []
    if (retry) {
      const lastUserIndex = state.messages.findLastIndex(m => m.role === 'user')
      if (lastUserIndex < 0) return
      state.messages = state.messages.slice(0, lastUserIndex)
    }
    const history = []
    let budget = 24000
    for (const message of [...state.messages].reverse()) {
      if (history.length >= 30) break
      if (message.id === 'welcome' || (message.role === 'bot' && message.status !== 'done')) continue
      if (message.text.length > budget) break
      history.unshift({ vai_tro: message.role === 'user' ? 'user' : 'bot', noi_dung: message.text })
      budget -= message.text.length
    }
    const botId = id()
    state.messages.push({ id: id(), role: 'user', text, status: 'done' },
      { id: botId, role: 'bot', text: '', status: 'streaming', sources: [], notes: [], meta: model.ten })
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
    const payload = { cau_hoi: text, model_id: model.id, lich_su: history, ngu_canh: state.context || null }
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
    const last = [...state.messages].reverse().find(m => m.role === 'user')
    if (last) return send(last.text, true)
  }
  return { send, retry, stop, clear, restore, persist }
}
