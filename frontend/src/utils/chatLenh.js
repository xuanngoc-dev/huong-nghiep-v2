// Lệnh gõ trong khung chat, bắt đầu bằng "/" (vd. /help, /end). Lệnh xử lý ngay trên trình duyệt (riêng /end gọi API),
// không gửi tới trợ lý AI và không tính vào lịch sử hội thoại gửi kèm câu hỏi.

export const LENH = [
  { ten: 'help', bietDanh: ['trogiup'], moTa: 'Xem danh sách lệnh' },
  { ten: 'new', bietDanh: ['moi'], moTa: 'Bắt đầu cuộc hội thoại mới' },
  { ten: 'end', bietDanh: ['ketthuc'], moTa: 'Kết thúc cuộc hội thoại hiện tại, sau đó không hỏi tiếp được' },
  { ten: 'retry', bietDanh: ['thulai'], moTa: 'Hỏi lại câu hỏi gần nhất' },
  { ten: 'model', bietDanh: ['mohinh'], thamSo: '[tên]', moTa: 'Xem các mô hình AI hoặc đổi sang mô hình khác' },
  { ten: 'goiy', bietDanh: ['suggest'], moTa: 'Gợi ý một số câu hỏi mẫu' },
  { ten: 'copy', bietDanh: ['saochep'], moTa: 'Sao chép nội dung cuộc hội thoại' },
]

export const CAU_HOI_MAU = [
  'Phương thức xét tuyển ngành Marketing trường NEU 2026?',
  'Bách khoa Hà Nội có những ngành nào?',
  'Những trường nào có ngành Công nghệ thông tin hoặc Logistics?',
  'Điểm chuẩn ngành Y đa khoa các trường năm gần nhất?',
  'Tổ hợp A00 xét tuyển được những ngành nào?',
]

function timLenh(ten) {
  return LENH.find((lenh) => lenh.ten === ten || lenh.bietDanh.includes(ten))
}

/** "/model gemini" → { ten: 'model', lenh, thamSo: 'gemini' }; không bắt đầu bằng "/" → null; lệnh lạ → lenh = undefined. */
export function phanTichLenh(text) {
  const t = String(text || '').trim()
  if (!t.startsWith('/')) return null
  const [dau, ...con] = t.slice(1).split(/\s+/)
  const ten = dau.toLowerCase()
  return { ten, lenh: ten ? timLenh(ten) : LENH[0], thamSo: con.join(' ') }
}

/** Lệnh khớp phần đang gõ (chỉ khi mới gõ "/..." và chưa có khoảng trắng) để hiện gợi ý. */
export function goiYLenh(text) {
  const t = String(text || '')
  if (!/^\/\S*$/.test(t)) return []
  const dau = t.slice(1).toLowerCase()
  return LENH.filter((lenh) => lenh.ten.startsWith(dau) || lenh.bietDanh.some((b) => b.startsWith(dau)))
}

export function cuPhap(lenh) {
  return `/${lenh.ten}${lenh.thamSo ? ` ${lenh.thamSo}` : ''}`
}

export function noiDungTroGiup() {
  const dong = LENH.map((lenh) => `- \`${cuPhap(lenh)}\` (hoặc \`/${lenh.bietDanh[0]}\`): ${lenh.moTa}`)
  return ['**Các lệnh dùng trong khung chat**', '', ...dong].join('\n')
}

function boDau(text) {
  return String(text || '')
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/đ/g, 'd')
    .replace(/Đ/g, 'D')
    .toLowerCase()
}

/** Tìm mô hình theo id hoặc tên (không phân biệt hoa thường, dấu); khớp đúng id trước, rồi tới chứa chuỗi. */
export function timModel(models, thamSo) {
  const tu = boDau(thamSo).trim()
  if (!tu) return null
  return models.find((m) => boDau(m.id) === tu) || models.find((m) => boDau(m.id).includes(tu) || boDau(m.ten).includes(tu)) || null
}

/** Nội dung hội thoại dạng văn bản để sao chép. tinNhan: [{ role: 'user' | 'bot', text }]. */
export function vanBanHoiThoai(tinNhan) {
  return tinNhan
    .filter((m) => m.text)
    .map((m) => `${m.role === 'user' ? 'Bạn' : 'Trợ lý'}: ${m.text}`)
    .join('\n\n')
}

/**
 * Bộ chạy lệnh dùng chung cho khung chat nổi và trang hội thoại của thành viên.
 * Phụ thuộc truyền vào để test được: state (chat store), loadModels(), ketThucPhien(maPhien), saoChep(vanBan).
 * nguCanh của từng lần chạy: { maPhien, tinNhan: [{ role, text }], moi(), thuLai() → câu báo | void, sauKetThuc() }.
 * Trả câu trả lời (markdown) để hiện như tin nhắn của trợ lý, hoặc null khi lệnh không cần trả lời (/new, /retry).
 */
export function taoBoChayLenh({ state, loadModels, ketThucPhien, saoChep }) {
  async function lenhModel(thamSo) {
    await loadModels()
    if (!state.models.length) return 'Chưa tải được danh sách mô hình AI. Vui lòng thử lại sau.'
    if (!thamSo) {
      const hienTai = state.models.find((m) => m.id === state.modelId)
      return [
        `**Mô hình đang dùng:** ${hienTai?.ten || 'chưa chọn'}`,
        '',
        ...state.models.map((m) => `- \`${m.id}\`: ${m.ten}${m.san_sang ? '' : ' (chưa sẵn sàng)'}`),
        '',
        'Gõ `/model <tên>` để đổi mô hình.',
      ].join('\n')
    }
    const model = timModel(state.models, thamSo)
    if (!model) return `Không tìm thấy mô hình "${thamSo}". Gõ \`/model\` để xem danh sách.`
    state.modelId = model.id
    return `Đã chuyển sang mô hình **${model.ten}**.${
      model.san_sang ? '' : ' Mô hình này chưa sẵn sàng (chưa có API key) nên có thể không trả lời được.'
    }`
  }

  async function lenhKetThuc(nguCanh) {
    if (!nguCanh.maPhien) return 'Cuộc hội thoại chưa có câu hỏi nào nên chưa cần kết thúc.'
    try {
      await ketThucPhien(nguCanh.maPhien)
    } catch (error) {
      return error?.message || 'Không kết thúc được cuộc hội thoại. Vui lòng thử lại.'
    }
    if (state.maPhien === nguCanh.maPhien) state.daKetThuc = true
    nguCanh.sauKetThuc?.()
    return 'Đã kết thúc cuộc hội thoại. Bạn không thể hỏi tiếp trong cuộc này; hãy bắt đầu cuộc hội thoại mới.'
  }

  async function lenhSaoChep(tinNhan) {
    const vanBan = vanBanHoiThoai(tinNhan || [])
    if (!vanBan) return 'Cuộc hội thoại chưa có nội dung để sao chép.'
    try {
      await saoChep(vanBan)
    } catch {
      return 'Trình duyệt không cho phép sao chép tự động. Bạn hãy bôi đen nội dung để sao chép.'
    }
    return `Đã sao chép ${tinNhan.filter((m) => m.text).length} tin nhắn vào bộ nhớ tạm.`
  }

  return async function chayLenh(text, nguCanh = {}) {
    const lenh = phanTichLenh(text)
    if (!lenh) return null
    if (!lenh.lenh) return `Không có lệnh \`/${lenh.ten}\`. Gõ \`/help\` để xem các lệnh.`
    switch (lenh.lenh.ten) {
      case 'help':
        return noiDungTroGiup()
      case 'goiy':
        return ['**Một số câu hỏi mẫu**', '', ...CAU_HOI_MAU.map((cau) => `- ${cau}`)].join('\n')
      case 'new':
        await nguCanh.moi?.()
        return null
      case 'retry':
        return (await nguCanh.thuLai?.()) || null
      case 'model':
        return lenhModel(lenh.thamSo)
      case 'copy':
        return lenhSaoChep(nguCanh.tinNhan)
      case 'end':
        return lenhKetThuc(nguCanh)
      default:
        return null
    }
  }
}
