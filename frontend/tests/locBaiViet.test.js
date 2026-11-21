import { test } from 'node:test'
import assert from 'node:assert/strict'
import { locBaiViet } from '../src/components/guest/cam-nang/locBaiViet.js'

const BAI = [
  { id: 'a', category: 'Tuyển sinh', title: 'Checklist hồ sơ xét tuyển', summary: 'Chuẩn bị trước kỳ xét tuyển', date: '2026-09-28' },
  { id: 'b', category: 'Hướng nghiệp', title: 'Đọc kết quả Holland', summary: 'Mã RIASEC', date: '2026-10-02' },
  { id: 'c', category: 'Tuyển sinh', title: 'Đăng ký nguyện vọng', summary: 'Các mốc thời gian', date: '2026-08-01' },
]

test('không lọc: đủ bài, mới nhất trước', () => {
  assert.deepEqual(locBaiViet(BAI).map((b) => b.id), ['b', 'a', 'c'])
})

test('lọc theo chủ đề', () => {
  assert.deepEqual(locBaiViet(BAI, { chuDe: 'Tuyển sinh' }).map((b) => b.id), ['a', 'c'])
})

test('từ khóa không phân biệt dấu, hoa thường; tìm cả tóm tắt', () => {
  assert.deepEqual(locBaiViet(BAI, { tuKhoa: 'ho so' }).map((b) => b.id), ['a'])
  assert.deepEqual(locBaiViet(BAI, { tuKhoa: 'DANG KY' }).map((b) => b.id), ['c'])
  assert.deepEqual(locBaiViet(BAI, { tuKhoa: 'riasec' }).map((b) => b.id), ['b'])
})

test('kết hợp chủ đề và từ khóa', () => {
  assert.deepEqual(locBaiViet(BAI, { chuDe: 'Hướng nghiệp', tuKhoa: 'hồ sơ' }), [])
})
