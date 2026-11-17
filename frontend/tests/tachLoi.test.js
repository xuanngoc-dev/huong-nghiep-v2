import test from 'node:test'
import assert from 'node:assert/strict'
import { tachLoi } from '../src/utils/tachLoi.js'

test('tách thông báo nhiều lỗi thành danh sách', () => {
  const kq = tachLoi('quy_tac_xet_tuyen có 3 lỗi: cong_thuc/5: Value error, a; cong_thuc/6: b; cong_thuc/8: c')
  assert.equal(kq.dau, 'quy_tac_xet_tuyen có 3 lỗi:')
  assert.deepEqual(kq.ds, ['cong_thuc/5: Value error, a', 'cong_thuc/6: b', 'cong_thuc/8: c'])
})

test('thông báo một lỗi hoặc thường giữ nguyên', () => {
  assert.deepEqual(tachLoi('Không tìm thấy đề án có id = 5'), { dau: 'Không tìm thấy đề án có id = 5', ds: [] })
  assert.deepEqual(tachLoi('quy_tac_xet_tuyen có 1 lỗi: chỉ một'), { dau: 'quy_tac_xet_tuyen có 1 lỗi: chỉ một', ds: [] })
  assert.deepEqual(tachLoi(undefined), { dau: '', ds: [] })
})

test('object lỗi của API quy tắc xét tuyển', () => {
  assert.deepEqual(tachLoi({ thong_bao: 'File có 2 lỗi', loi: ['a', 'b'] }), { dau: 'File có 2 lỗi', ds: ['a', 'b'] })
})
