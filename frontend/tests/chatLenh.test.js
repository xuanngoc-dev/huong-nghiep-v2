import test from 'node:test'
import assert from 'node:assert/strict'
import { goiYLenh, phanTichLenh, taoBoChayLenh, timModel } from '../src/utils/chatLenh.js'

function boChay(over = {}) {
  const state = { models: [{ id: 'gemini-flash', ten: 'Gemini Flash', san_sang: true }, { id: 'gpt-4o', ten: 'GPT 4o', san_sang: false }],
    modelId: 'gemini-flash', maPhien: 'p1', daKetThuc: false }
  const goi = { ketThuc: [], saoChep: [] }
  const chay = taoBoChayLenh({
    state,
    loadModels: async () => {},
    ketThucPhien: async (ma) => { goi.ketThuc.push(ma) },
    saoChep: async (vanBan) => { goi.saoChep.push(vanBan) },
    ...over,
  })
  return { state, goi, chay }
}

test('phân tích lệnh: tên, bí danh tiếng Việt, tham số; tin thường không phải lệnh', () => {
  assert.equal(phanTichLenh('Điểm chuẩn NEU?'), null)
  assert.equal(phanTichLenh('/HELP').lenh.ten, 'help')
  assert.equal(phanTichLenh('/ketthuc').lenh.ten, 'end')
  assert.deepEqual([phanTichLenh('/model  gpt 4o').lenh.ten, phanTichLenh('/model  gpt 4o').thamSo], ['model', 'gpt 4o'])
  assert.equal(phanTichLenh('/abc').lenh, undefined)
  assert.equal(phanTichLenh('/').lenh.ten, 'help')
})

test('gợi ý lệnh theo phần đang gõ, hết gợi ý khi đã gõ tham số', () => {
  assert.deepEqual(goiYLenh('/e').map((l) => l.ten), ['end'])
  assert.ok(goiYLenh('/').length > 5)
  assert.deepEqual(goiYLenh('/model gpt'), [])
  assert.deepEqual(goiYLenh('hỏi'), [])
})

test('tìm mô hình theo id hoặc tên, không phân biệt hoa thường', () => {
  const { state } = boChay()
  assert.equal(timModel(state.models, 'GPT').id, 'gpt-4o')
  assert.equal(timModel(state.models, 'gemini flash').id, 'gemini-flash')
  assert.equal(timModel(state.models, 'claude'), null)
})

test('/end kết thúc phiên đang mở và báo cho trang; chưa có phiên thì không gọi API', async () => {
  const { state, goi, chay } = boChay()
  let daBao = false
  assert.match(await chay('/end', { maPhien: null }), /chưa có câu hỏi/)
  assert.deepEqual(goi.ketThuc, [])
  assert.match(await chay('/end', { maPhien: 'p1', sauKetThuc: () => { daBao = true } }), /Đã kết thúc/)
  assert.deepEqual([goi.ketThuc, state.daKetThuc, daBao], [['p1'], true, true])
})

test('/end lỗi từ server thì trả lời bằng nội dung lỗi, không khóa hội thoại', async () => {
  const { state, chay } = boChay({ ketThucPhien: async () => { throw new Error('Không tìm thấy phiên') } })
  assert.equal(await chay('/end', { maPhien: 'p1' }), 'Không tìm thấy phiên')
  assert.equal(state.daKetThuc, false)
})

test('/model đổi mô hình, cảnh báo khi chưa sẵn sàng; /copy, /new, /retry và lệnh lạ', async () => {
  const { state, goi, chay } = boChay()
  assert.match(await chay('/model'), /Gemini Flash/)
  assert.match(await chay('/model gpt'), /chưa sẵn sàng/)
  assert.equal(state.modelId, 'gpt-4o')
  assert.match(await chay('/copy', { tinNhan: [{ role: 'user', text: 'Hỏi' }, { role: 'bot', text: 'Đáp' }] }), /2 tin nhắn/)
  assert.equal(goi.saoChep[0], 'Bạn: Hỏi\n\nTrợ lý: Đáp')
  let moi = false
  assert.equal(await chay('/new', { moi: () => { moi = true } }), null)
  assert.ok(moi)
  assert.equal(await chay('/retry', { thuLai: () => 'Chưa có câu hỏi nào để hỏi lại.' }), 'Chưa có câu hỏi nào để hỏi lại.')
  assert.match(await chay('/xyz'), /Không có lệnh/)
  assert.match(await chay('/help'), /\/end/)
})
