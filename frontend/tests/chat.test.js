import test from 'node:test'
import assert from 'node:assert/strict'
import { renderToString } from 'vue/server-renderer'
import { h } from 'vue'
import { createChatSession, fromServerMessages, newConversation } from '../src/utils/chatSession.js'
import { createEventParser, readChatStream } from '../src/utils/chatStream.js'
import { renderMarkdown } from '../src/utils/chatMarkdown.js'
import { DOI_TUONG_HUONG_DEN, cauHoiMau, doiTuongTheoTrang } from '../src/constants/doiTuongHuongDen.js'

function fixture(stream = async () => {}, saved = null, loadProfile) {
  const data = new Map(saved ? [['test', JSON.stringify(saved)]] : [])
  const state = { messages: newConversation(), modelId: 'test-model', models: [{ id: 'test-model', ten: 'Test', san_sang: true }],
    draft: '', sending: false, error: '', suggestions: [], storageWarning: '' }
  const storage = { getItem: k => data.get(k), setItem: (k, v) => data.set(k, v) }
  const session = createChatSession(state, { stream, storage, storageKey: () => 'test', loadProfile })
  return { state, session, data }
}
function deferred() {
  let resolve
  const promise = new Promise(r => { resolve = r })
  return { promise, resolve }
}

test('restore retains saved conversation and draft instead of overwriting it', () => {
  const saved = { version: 2, modelId: 'test-model', draft: 'Hỏi tiếp', messages: [
    { id: 'one', role: 'user', text: 'Marketing NEU', status: 'done' },
    { id: 'two', role: 'bot', text: 'Câu trả lời đã lưu', status: 'done', sources: [{ id: 1, ten: 'NEU' }] },
  ] }
  const { state, session, data } = fixture(undefined, saved)
  session.restore()
  assert.equal(state.messages[1].text, 'Câu trả lời đã lưu')
  assert.equal(state.draft, 'Hỏi tiếp')
  assert.deepEqual(JSON.parse(data.get('test')), saved)
})

test('stream updates shared state, sources, actual model and saved history', async () => {
  const { state, session, data } = fixture(async (_, options) => {
    options.onEvent('meta', { nguon: [{ id: 1, ten: 'NEU' }] })
    options.onEvent('model', { model_ten: 'Fallback' })
    options.onEvent('delta', { text: 'Xin ' })
    options.onEvent('delta', { text: 'chào' })
    options.onEvent('done', { tra_loi: 'Xin chào', model_ten: 'Fallback', nguon: [{ id: 1, ten: 'NEU' }], ghi_chu: [], goi_y: [] })
  })
  state.draft = 'Marketing NEU'
  await session.send()
  assert.equal(state.sending, false)
  assert.equal(state.messages.at(-1).text, 'Xin chào')
  assert.equal(state.messages.at(-1).meta, 'Fallback')
  assert.equal(JSON.parse(data.get('test')).messages.at(-1).sources[0].ten, 'NEU')
})

test('logged-in profile is sent with the question and a guest request omits it', async () => {
  const profile = { trinh_do_hoc_van: { chung_chi_ngoai_ngu: [{ ma: 'IELTS', thanh_tich: '7.5' }] } }
  const seen = []
  const loggedIn = fixture(async (body, options) => {
    seen.push(body)
    options.onEvent('done', { tra_loi: 'Đã tính điểm cộng IELTS' })
  }, null, async () => profile)
  await loggedIn.session.send('Điểm SAT trường Bách khoa')
  assert.deepEqual(seen[0].ho_so, profile)
  const guest = fixture(async (body, options) => {
    seen.push(body)
    options.onEvent('done', { tra_loi: 'Điểm SAT' })
  })
  await guest.session.send('Điểm SAT trường Bách khoa')
  assert.equal(seen[1].ho_so, undefined)
})

test('stop while the profile is loading cancels before the question is sent', async () => {
  const gate = deferred()
  let calls = 0
  const { state, session } = fixture(async () => { calls += 1 }, null, () => gate.promise)
  const request = session.send('Điểm SAT trường Bách khoa')
  session.stop()
  gate.resolve({ trinh_do_hoc_van: { chung_chi_ngoai_ngu: [{ ma: 'IELTS', thanh_tich: '7.0' }] } })
  await request
  assert.equal(calls, 0)
  assert.equal(state.sending, false)
  assert.equal(state.messages.at(-1).status, 'cancelled')
})

test('structured school and major context is persisted and sent on follow-up', async () => {
  const scope = { ma_truong: ['NEU'], nganh: ['marketing'], nam: 2026, nam_du_tuyen: 2027,
    diem: 28, to_hop: ['A00'], khu_vuc: 'miền Bắc', nguon_diem: 'thi THPT', tom_tat: 'Thích phân tích dữ liệu, ưu tiên Hà Nội' }
  let calls = 0
  const { state, session, data } = fixture(async (payload, options) => {
    if (calls++) assert.deepEqual(payload.ngu_canh, scope)
    options.onEvent('done', { tra_loi: 'Kết quả', ngu_canh: scope })
  })
  await session.send('Marketing NEU')
  assert.deepEqual(JSON.parse(data.get('test')).context, scope)
  await session.send('Còn điều kiện?')
  session.restore()
  assert.deepEqual(state.context, scope)
  session.clear()
  assert.equal(state.context, null)
})

test('late response after clear cannot reappear or complete a newer request', async () => {
  const old = deferred()
  const newer = deferred()
  let calls = 0
  let oldSignal
  const { state, session } = fixture(async (_, options) => {
    if (++calls === 1) {
      oldSignal = options.signal
      await old.promise
      options.onEvent('delta', { text: 'Phản hồi cũ' })
    } else {
      await newer.promise
      options.onEvent('done', { tra_loi: 'Phản hồi mới' })
    }
  })
  const first = session.send('Câu cũ')
  session.clear()
  assert.equal(oldSignal.aborted, true)
  const second = session.send('Câu mới')
  old.resolve()
  await first
  assert.equal(state.sending, true)
  assert.equal(state.messages.at(-1).text, '')
  newer.resolve()
  await second
  assert.equal(state.messages.at(-1).text, 'Phản hồi mới')
  assert.equal(state.messages.some(m => m.text === 'Phản hồi cũ'), false)
})

test('stop preserves partial text and prevents later chunks', async () => {
  const pending = deferred()
  const { state, session } = fixture(async (_, options) => {
    options.onEvent('delta', { text: 'Một phần' })
    await pending.promise
    options.onEvent('delta', { text: ' cũ' })
  })
  const request = session.send('Câu hỏi')
  session.stop()
  pending.resolve()
  await request
  assert.equal(state.messages.at(-1).text, 'Một phần')
  assert.equal(state.messages.at(-1).status, 'cancelled')
  assert.equal(state.sending, false)
})

test('retry replaces failed turn and excludes failed bot output from history', async () => {
  let calls = 0
  const { state, session } = fixture(async (payload, options) => {
    if (++calls === 1) throw new Error('Thử lại sau')
    assert.equal(payload.lich_su.length, 0)
    options.onEvent('done', { tra_loi: 'Thành công' })
  })
  await session.send('Câu hỏi')
  assert.equal(state.messages.at(-1).status, 'error')
  await session.retry()
  assert.equal(state.messages.filter(m => m.role === 'user').length, 1)
  assert.equal(state.messages.at(-1).text, 'Thành công')
})

test('unavailable storage does not prevent chatting', async () => {
  const state = { messages: newConversation(), models: [], draft: '', modelId: '', sending: false }
  const session = createChatSession(state, { stream: async () => {}, storageKey: () => 'test',
    storage: { getItem() { throw new Error('denied') }, setItem() { throw new Error('quota') } } })
  session.restore()
  session.persist()
  assert.ok(state.storageWarning)
  assert.equal(state.messages.length, 1)
})

test('SSE handles fragmented delimiters, comments and CRLF', () => {
  const events = []
  const parser = createEventParser((event, data) => events.push([event, data]))
  parser.push(': keepalive\r\nevent: delta\r\ndata: {"text":"Chào"}\r')
  parser.push('\n\r')
  parser.push('\nevent: done\ndata: {"tra_loi":"Chào"}\n\n', true)
  assert.deepEqual(events.map(([event]) => event), ['delta', 'done'])
  assert.equal(events[0][1].text, 'Chào')
})

test('SSE decodes split UTF-8 characters and requires completion', async () => {
  const bytes = new TextEncoder().encode('event: delta\ndata: {"text":"Tiếng Việt"}\n\nevent: done\ndata: {"tra_loi":"Tiếng Việt"}\n\n')
  const response = new Response(new ReadableStream({ start(controller) {
    for (const byte of bytes) controller.enqueue(new Uint8Array([byte]))
    controller.close()
  } }))
  const events = []
  await readChatStream(response, (event, data) => events.push([event, data]))
  assert.equal(events[0][1].text, 'Tiếng Việt')
  await assert.rejects(readChatStream(new Response('event: delta\ndata: {"text":"Một phần"}\n\n'), () => {}), /Mất kết nối/)
})

test('SSE propagates server errors without marking partial output done', async () => {
  const response = new Response('event: delta\ndata: {"text":"Một phần"}\n\nevent: error\ndata: {"message":"Hết hạn mức"}\n\n')
  await assert.rejects(readChatStream(response, () => {}), /Hết hạn mức/)
})

test('math commands render as readable symbols instead of command names', async () => {
  const html = await renderToString(h('div', renderMarkdown('$\\mathbf{F} = m \\times a$, $\\alpha \\le \\frac{1}{2}$, $\\sqrt{x}$, $\\text{kg}$')))
  assert.match(html, /𝐅/)
  assert.match(html, /×/)
  assert.match(html, /α/)
  assert.match(html, /≤/)
  assert.match(html, /\(1\) \/ \(2\)/)
  assert.match(html, /√\(x\)/)
  assert.match(html, /kg/)
  assert.doesNotMatch(html, /mathbf|alpha|leq|frac|sqrt|text/)
})

test('Markdown renders tables and keeps HTML and javascript inert', async () => {
  const html = await renderToString(h('div', renderMarkdown('**Đậm**\n\n| Ngành | Điểm |\n| --- | --- |\n| Marketing | 20 |\n\n<script>alert(1)</script>\n[Nguy hiểm](javascript:alert)\n[Đề án](https://example.com)')))
  assert.match(html, /<strong>Đậm<\/strong>/)
  assert.match(html, /<table>/)
  assert.match(html, /&lt;script&gt;/)
  assert.doesNotMatch(html, /href="javascript:/)
  assert.match(html, /noopener noreferrer/)
})

test('mã phiên từ server được gửi lại ở câu sau và bỏ khi mở hội thoại mới', async () => {
  const payloads = []
  const { state, session, data } = fixture(async (payload, options) => {
    payloads.push(payload)
    options.onEvent('meta', { ma_phien: 'phien-1' })
    options.onEvent('done', { tra_loi: 'OK', ma_phien: 'phien-1' })
  })
  await session.send('Câu 1')
  await session.send('Câu 2')
  assert.deepEqual(payloads.map(p => p.ma_phien), [null, 'phien-1'])
  assert.equal(JSON.parse(data.get('test')).maPhien, 'phien-1')
  session.clear()
  assert.equal(state.maPhien, null)
  await session.send('Câu 3')
  assert.equal(payloads[2].ma_phien, null)
})

test('khách gửi kèm mã thiết bị', async () => {
  let payload
  const data = new Map()
  const state = { messages: newConversation(), modelId: 'm', models: [{ id: 'm', ten: 'M', san_sang: true }],
    draft: '', sending: false, error: '', suggestions: [], storageWarning: '' }
  const session = createChatSession(state, {
    stream: async (p) => { payload = p },
    storage: { getItem: k => data.get(k), setItem: (k, v) => data.set(k, v) },
    storageKey: () => 'test',
    guestId: () => 'thiet-bi-1',
  })
  await session.send('Xin chào')
  assert.equal(payload.ma_khach_vang_lai, 'thiet-bi-1')
})

test('server báo phiên đã kết thúc (409) thì khóa gửi tiếp tới khi mở hội thoại mới', async () => {
  let calls = 0
  const { state, session } = fixture(async () => {
    calls++
    throw Object.assign(new Error('Cuộc hội thoại này đã kết thúc.'), { status: 409 })
  })
  state.maPhien = '11111111-1111-4111-8111-111111111111'
  await session.send('Hỏi tiếp')
  assert.equal(state.daKetThuc, true)
  assert.equal(state.messages.at(-1).error, 'Cuộc hội thoại này đã kết thúc.')
  await session.send('Hỏi nữa')
  assert.equal(calls, 1)
  session.clear()
  assert.equal(state.daKetThuc, false)
  assert.equal(state.maPhien, null)
})

test('mở lại hội thoại đã lưu trên server: chuyển tin nhắn và nối tiếp đúng mã phiên', () => {
  const { state, session } = fixture()
  state.daKetThuc = true
  session.open('phien-cu', fromServerMessages([
    { id: 1, loai_nguoi_gui: 'user', noi_dung_tin_nhan: 'Ngành CNTT?', trang_thai: 'thanh_cong' },
    { id: 2, loai_nguoi_gui: 'bot', noi_dung_phan_hoi: 'CNTT học lập trình', nguon_tham_khao: [{ id: 1, ten: 'BKA' }], model_ai: 'm', trang_thai: 'thanh_cong' },
    { id: 3, loai_nguoi_gui: 'user', noi_dung_tin_nhan: 'Điểm chuẩn?', trang_thai: 'thanh_cong' },
    { id: 4, loai_nguoi_gui: 'bot', noi_dung_phan_hoi: null, loi_chi_tiet: 'Hết giờ', trang_thai: 'loi' },
  ]))
  assert.equal(state.maPhien, 'phien-cu')
  assert.equal(state.daKetThuc, false)
  assert.deepEqual(state.messages.map(m => [m.role, m.text, m.status]), [
    ['user', 'Ngành CNTT?', 'done'], ['bot', 'CNTT học lập trình', 'done'], ['user', 'Điểm chuẩn?', 'done'], ['bot', '', 'error']])
  assert.equal(state.messages[1].sources[0].ten, 'BKA')
  assert.equal(state.messages[3].error, 'Hết giờ')
})

test('tin nhắn lệnh cục bộ không gửi kèm lịch sử và không bị chọn khi hỏi lại', async () => {
  const payloads = []
  const { state, session } = fixture(async (payload, options) => {
    payloads.push(payload)
    options.onEvent('done', { tra_loi: 'Đáp', nguon: [] })
  })
  await session.send('Câu hỏi thật')
  state.messages.push({ id: 'l1', role: 'user', text: '/help', status: 'done', local: true },
    { id: 'l2', role: 'bot', text: 'Danh sách lệnh', status: 'done', local: true })
  await session.retry()
  assert.equal(payloads[1].cau_hoi, 'Câu hỏi thật')
  assert.ok(payloads[1].lich_su.every(m => m.noi_dung !== '/help' && m.noi_dung !== 'Danh sách lệnh'))
})

test('hết token AI (402): báo ở thanh lỗi, vẫn gửi lại được sau khi nạp', async () => {
  let calls = 0
  const { state, session } = fixture(async () => {
    calls++
    throw Object.assign(new Error('Bạn đã dùng hết token AI.'), { status: 402 })
  })
  await session.send('Hỏi')
  assert.equal(state.error, 'Bạn đã dùng hết token AI.')
  assert.equal(state.hetToken, true)
  assert.ok(!state.daKetThuc)
  await session.send('Hỏi lại')
  assert.equal(calls, 2)
})

test('gửi câu mới thì xóa cờ hết token của lượt trước', async () => {
  const { state, session } = fixture(async (_, options) => options.onEvent('done', { tra_loi: 'Đáp', nguon: [] }))
  state.hetToken = true
  await session.send('Hỏi')
  assert.equal(state.hetToken, false)
})

test('đối tượng hướng đến theo trang đang xem', () => {
  assert.equal(doiTuongTheoTrang({ dinhHuong: 'du-hoc' }), 'thpt-du-hoc')
  assert.equal(doiTuongTheoTrang({ dinhHuong: 'thi-dai-hoc', goc: 'phu-huynh-thpt-lop-12' }), 'phu-huynh')
  assert.equal(doiTuongTheoTrang({ giaiDoanCon: 'thcs' }), 'phu-huynh')
  assert.equal(doiTuongTheoTrang({ doiTuongCha: 'hoc-sinh-thcs' }), 'hoc-sinh-thcs')
  assert.equal(doiTuongTheoTrang({ doiTuong: 'hoc-sinh-thpt' }), 'thpt-thi-dai-hoc')
  assert.equal(doiTuongTheoTrang({}, 'phu-huynh'), 'phu-huynh')
  assert.equal(doiTuongTheoTrang({}, 'nha-tuyen-dung'), 'thpt-thi-dai-hoc')
})

test('gửi kèm đối tượng hướng đến; hội thoại mới lấy lại đối tượng theo trang', async () => {
  const payloads = []
  let trang = 'phu-huynh'
  const data = new Map()
  const state = { messages: newConversation(), modelId: 'm', models: [{ id: 'm', ten: 'M', san_sang: true }],
    draft: '', sending: false, error: '', suggestions: [], storageWarning: '' }
  const session = createChatSession(state, {
    stream: async (p) => { payloads.push(p) },
    storage: { getItem: k => data.get(k), setItem: (k, v) => data.set(k, v) },
    storageKey: () => 'test',
    doiTuongMacDinh: () => trang,
  })
  session.restore()
  assert.equal(state.doiTuongHuongDen, 'phu-huynh')
  state.modelId = 'm'
  state.doiTuongHuongDen = 'thpt-du-hoc'
  await session.send('Câu 1')
  assert.equal(payloads[0].doi_tuong_huong_den, 'thpt-du-hoc')
  assert.equal(JSON.parse(data.get('test')).doiTuongHuongDen, 'thpt-du-hoc')
  trang = 'hoc-sinh-thcs'
  session.clear()
  assert.equal(state.doiTuongHuongDen, 'hoc-sinh-thcs')
  session.open('phien-2', [], 'sinh-vien')
  assert.equal(state.doiTuongHuongDen, 'sinh-vien')
})

test('đã tự chọn đối tượng thì lưu lại; hội thoại mới thì hỏi chọn lại', () => {
  const data = new Map()
  const state = { messages: newConversation(), modelId: 'm', models: [], draft: '', sending: false, error: '', suggestions: [], storageWarning: '' }
  const session = createChatSession(state, {
    stream: async () => {},
    storage: { getItem: k => data.get(k), setItem: (k, v) => data.set(k, v) },
    storageKey: () => 'test',
    doiTuongMacDinh: () => 'thpt-thi-dai-hoc',
  })
  session.restore()
  assert.equal(state.daChonDoiTuong, false)
  state.doiTuongHuongDen = 'phu-huynh'
  state.daChonDoiTuong = true
  session.persist()
  session.restore()
  assert.deepEqual([state.doiTuongHuongDen, state.daChonDoiTuong], ['phu-huynh', true])
  session.clear()
  assert.deepEqual([state.doiTuongHuongDen, state.daChonDoiTuong], ['thpt-thi-dai-hoc', false])
})

test('câu hỏi gợi ý theo đối tượng hướng đến', () => {
  for (const { ma } of DOI_TUONG_HUONG_DEN) assert.equal(cauHoiMau(ma).length, 3)
  assert.notDeepEqual(cauHoiMau('phu-huynh'), cauHoiMau('thpt-thi-dai-hoc'))
  assert.deepEqual(cauHoiMau('khong-co'), cauHoiMau('thpt-thi-dai-hoc'))
})
