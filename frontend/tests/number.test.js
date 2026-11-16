import { test } from 'node:test'
import assert from 'node:assert/strict'
import { formatSoNhap, parseSoNhap } from '../src/utils/number.js'

test('formatSoNhap phân tách hàng nghìn, thập phân dùng dấu phẩy', () => {
  assert.equal(formatSoNhap('10000'), '10.000')
  assert.equal(formatSoNhap('1234567.5'), '1.234.567,5')
  assert.equal(formatSoNhap('-9999'), '-9.999')
  assert.equal(formatSoNhap('8.'), '8,')
  assert.equal(formatSoNhap('999'), '999')
  assert.equal(formatSoNhap(''), '')
  assert.equal(formatSoNhap(null), '')
})

test('parseSoNhap trả chuỗi số thô để gửi API', () => {
  assert.equal(parseSoNhap('10.000'), '10000')
  assert.equal(parseSoNhap('1.234.567,5'), '1234567.5')
  assert.equal(parseSoNhap('-9.999'), '-9999')
  assert.equal(parseSoNhap(''), '')
})

test('gõ tiếp sau số đã định dạng vẫn là hàng nghìn', () => {
  // "1.000" gõ thêm "0" → "1.0000" phải thành 10000, không phải 1,0000
  assert.equal(parseSoNhap('1.0000'), '10000')
  assert.equal(formatSoNhap(parseSoNhap('1.0000')), '10.000')
})

test('dấu chấm vừa gõ ở cuối được hiểu là dấu thập phân', () => {
  assert.equal(parseSoNhap('8.'), '8.')
  assert.equal(formatSoNhap(parseSoNhap('8.')), '8,')
  assert.equal(parseSoNhap('0,25'), '0.25')
  assert.equal(parseSoNhap('1.234,'), '1234.')
})
