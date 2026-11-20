import { test } from 'node:test'
import assert from 'node:assert/strict'
import { dinhDangNgay, dinhDangThoiGian, docThoiGian, thuTrongTuan } from '../src/utils/thoiGian.js'

test('chuỗi không kèm múi giờ hiểu theo giờ Việt Nam', () => {
  assert.equal(docThoiGian('2026-11-20T17:30:00').toISOString(), '2026-11-20T10:30:00.000Z')
  assert.equal(docThoiGian('2026-11-20 00:15:00.123456').toISOString(), '2026-11-19T17:15:00.123Z')
  assert.equal(docThoiGian('2026-11-20T10:30:00Z').toISOString(), '2026-11-20T10:30:00.000Z')
  assert.equal(docThoiGian(''), null)
  assert.equal(docThoiGian('abc'), null)
})

test('hiển thị theo giờ Việt Nam bất kể giờ máy', () => {
  assert.equal(dinhDangThoiGian('2026-11-20T23:30:00+00:00', { hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }), '06:30')
  assert.equal(dinhDangNgay('2026-11-20T23:30:00Z'), '21/11/2026')
  assert.equal(dinhDangThoiGian(null, undefined, '—'), '—')
  assert.equal(thuTrongTuan('2026-11-20T23:30:00Z'), 6)
})
