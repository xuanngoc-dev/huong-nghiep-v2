import { test } from 'node:test'
import assert from 'node:assert/strict'
import {
  chuanHoaLoTrinh,
  dsLoTrinh,
  loiLoTrinh,
  tenLoTrinh,
} from '../src/components/admin/nghe-cu-the/truongNghe.js'

test('lộ trình từ API → form: nhận mảng và chuỗi cũ', () => {
  assert.deepEqual(dsLoTrinh([{ giai_doan: 'Thợ phụ', luong_trung_binh_min: '7000000', mo_ta_cong_viec: null }]), [
    { giai_doan: 'Thợ phụ', mo_ta_cong_viec: '', luong_trung_binh_min: 7000000, luong_trung_binh_max: null, ghi_chu: '' },
  ])
  assert.deepEqual(
    dsLoTrinh('Thợ phụ → Thợ hàn 3G -> Tổ trưởng.').map((b) => b.giai_doan),
    ['Thợ phụ', 'Thợ hàn 3G', 'Tổ trưởng'],
  )
  assert.deepEqual(dsLoTrinh(null), [])
  assert.equal(tenLoTrinh([{ giai_doan: 'A' }, { giai_doan: 'B' }]), 'A → B')
})

test('lộ trình form → payload: bỏ dòng trống, chữ rỗng thành null', () => {
  assert.deepEqual(
    chuanHoaLoTrinh([
      { giai_doan: ' Thợ phụ ', mo_ta_cong_viec: '  ', luong_trung_binh_min: 7000000, luong_trung_binh_max: null, ghi_chu: '' },
      { giai_doan: '', mo_ta_cong_viec: '', luong_trung_binh_min: null, luong_trung_binh_max: null, ghi_chu: '' },
    ]),
    [{ giai_doan: 'Thợ phụ', mo_ta_cong_viec: null, luong_trung_binh_min: 7000000, luong_trung_binh_max: null, ghi_chu: null }],
  )
  assert.equal(chuanHoaLoTrinh([]), null)
  assert.equal(chuanHoaLoTrinh('  '), null)
  assert.equal(chuanHoaLoTrinh('A → B'), 'A → B')
})

test('kiểm tra lộ trình trên form', () => {
  assert.equal(loiLoTrinh([]), '')
  assert.equal(loiLoTrinh([{ giai_doan: '', mo_ta_cong_viec: 'x' }]), 'Giai đoạn 1: vui lòng nhập tên giai đoạn')
  assert.equal(
    loiLoTrinh([{ giai_doan: 'A' }, { giai_doan: 'B', luong_trung_binh_min: 10, luong_trung_binh_max: 5 }]),
    'Giai đoạn 2: lương trung bình từ phải ≤ đến',
  )
})
