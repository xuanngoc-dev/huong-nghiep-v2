import { test } from 'node:test'
import assert from 'node:assert/strict'
import { LOAI_TRA_CUU, loaiCoSo, timLoaiTraCuu } from '../src/components/guest/tra-cuu/loaiTraCuu.js'

test('id loại tra cứu không trùng; id lạ trả về loại mặc định', () => {
  const ids = LOAI_TRA_CUU.map((loai) => loai.id)
  assert.equal(new Set(ids).size, ids.length)
  assert.equal(timLoaiTraCuu('to-hop').id, 'to-hop')
  assert.equal(timLoaiTraCuu('khong-co').id, LOAI_TRA_CUU[0].id)
  assert.equal(timLoaiTraCuu(undefined).id, LOAI_TRA_CUU[0].id)
})

test('thẻ trường: bỏ tag rỗng', () => {
  const the = timLoaiTraCuu('truong').the({
    ten_truong: 'Đại học Bách khoa Hà Nội',
    ma_truong: 'BKA',
    loai_co_so: 'Đại học',
    loai_hinh: null,
    ten_tinh_thanh: 'Hà Nội',
  })
  assert.deepEqual(the, {
    tieuDe: 'Đại học Bách khoa Hà Nội',
    ma: 'BKA',
    tags: ['Đại học', 'Hà Nội'],
    moTa: undefined,
    anh: null,
  })
})

test('loại cơ sở: ưu tiên giá trị khai báo, chưa có thì đoán từ tên', () => {
  assert.equal(loaiCoSo({ loai_co_so: 'Trường đại học', ten_truong: 'Học viện Ngân hàng' }), 'Trường đại học')
  assert.equal(loaiCoSo({ ten_truong: 'Học viện Ngân hàng' }), 'Học viện')
  assert.equal(loaiCoSo({ ten_truong: 'Cao đẳng Thương mại' }), 'Cao đẳng')
  assert.equal(loaiCoSo({ ten_truong: 'Đại học Thái Nguyên' }), 'Đại học')
  assert.equal(loaiCoSo({ ten_truong: 'Trường Sĩ quan Lục quân' }), null)
})
