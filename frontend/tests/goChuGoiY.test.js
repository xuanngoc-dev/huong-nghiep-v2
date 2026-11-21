import { test } from 'node:test'
import assert from 'node:assert/strict'
import { TRANG_THAI_DAU, buocGoChu, chuDangHien } from '../src/utils/goChuGoiY.js'

const T = { go: 1, xoa: 2, dungSauGo: 10, dungSauXoa: 5 }

function chay(danhSach, soBuoc) {
  let trangThai = { ...TRANG_THAI_DAU }
  const ket = []
  for (let i = 0; i < soBuoc; i++) {
    const buoc = buocGoChu(trangThai, danhSach, T)
    trangThai = buoc.trangThai
    ket.push([chuDangHien(trangThai, danhSach), buoc.cho])
  }
  return ket
}

test('gõ từng ký tự, dừng lâu ở cuối, xóa hết rồi sang gợi ý kế tiếp', () => {
  assert.deepEqual(chay(['AB', 'C'], 8), [
    ['A', 1],
    ['AB', 10],
    ['AB', 2],
    ['A', 2],
    ['', 5],
    ['', 1],
    ['C', 10],
    ['C', 2],
  ])
})

test('vòng lại gợi ý đầu sau gợi ý cuối', () => {
  const sau = chay(['A', 'B'], 10).map(([chu]) => chu)
  assert.deepEqual(sau, ['A', 'A', '', '', 'B', 'B', '', '', 'A', 'A'])
})

test('đếm ký tự tiếng Việt có dấu đúng từng chữ', () => {
  assert.equal(chuDangHien({ chiSo: 0, soKyTu: 3 }, ['Học viện']), 'Học')
})

test('danh sách rỗng không lỗi', () => {
  assert.deepEqual(buocGoChu({ ...TRANG_THAI_DAU }, [], T).trangThai, TRANG_THAI_DAU)
  assert.equal(chuDangHien(TRANG_THAI_DAU, []), '')
})
