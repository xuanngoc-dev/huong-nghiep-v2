import test from 'node:test'
import assert from 'node:assert/strict'
import { renderToString } from 'vue/server-renderer'
import { h } from 'vue'
import { createChatSession, newConversation } from '../src/utils/chatSession.js'
import { createEventParser, readChatStream } from '../src/utils/chatStream.js'
import { renderMarkdown } from '../src/utils/chatMarkdown.js'

function fixture(stream = async () => {}, saved = null) {
  const data = new Map(saved ? [['test', JSON.stringify(saved)]] : [])
  const state = { messages: newConversation(), modelId: 'test-model', models: [{ id: 'test-model', ten: 'Test', san_sang: true }],
    draft: '', sending: false, error: '', suggestions: [], storageWarning: '' }
  const storage = { getItem: k => data.get(k), setItem: (k, v) => data.set(k, v) }
  const session = createChatSession(state, { stream, storage, storageKey: () => 'test' })
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
