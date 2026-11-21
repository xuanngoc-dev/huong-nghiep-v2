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
  })
})

test('chi tiết: nối danh sách, bỏ dòng rỗng, đánh dấu link', () => {
  const dong = timLoaiTraCuu('truong').chiTiet({
    ma_truong: 'BKA',
    ten_viet_tat: '  ',
    bac_dao_tao: ['Đại học', 'Thạc sĩ'],
    linh_vuc_dao_tao_chinh: [],
    website: 'https://hust.edu.vn',
  })
  assert.deepEqual(dong, [
    { label: 'Mã trường', value: 'BKA', link: false },
    { label: 'Bậc đào tạo', value: 'Đại học, Thạc sĩ', link: false },
    { label: 'Website', value: 'https://hust.edu.vn', link: true },
  ])
})

test('chi tiết chứng chỉ: thêm đơn vị cho thời hạn, giữ giá trị 0', () => {
  const dong = timLoaiTraCuu('chung-chi').chiTiet({ thoi_han_hieu_luc_thang: 24 })
  assert.deepEqual(dong, [{ label: 'Thời hạn hiệu lực', value: '24 tháng', link: false }])
  const dong0 = timLoaiTraCuu('bai-thi').chiTiet({ thoi_luong_phut: 0 })
  assert.deepEqual(dong0, [{ label: 'Thời lượng', value: '0 phút', link: false }])
})

test('loại cơ sở: ưu tiên giá trị khai báo, chưa có thì đoán từ tên', () => {
  assert.equal(loaiCoSo({ loai_co_so: 'Trường đại học', ten_truong: 'Học viện Ngân hàng' }), 'Trường đại học')
  assert.equal(loaiCoSo({ ten_truong: 'Học viện Ngân hàng' }), 'Học viện')
  assert.equal(loaiCoSo({ ten_truong: 'Cao đẳng Thương mại' }), 'Cao đẳng')
  assert.equal(loaiCoSo({ ten_truong: 'Đại học Thái Nguyên' }), 'Đại học')
  assert.equal(loaiCoSo({ ten_truong: 'Trường Sĩ quan Lục quân' }), null)
})
