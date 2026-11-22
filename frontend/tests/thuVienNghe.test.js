import test from 'node:test'
import assert from 'node:assert/strict'
import { daiLuong, khoangTrieu, tachDanhSach } from '../src/components/guest/thu-vien/nghe.js'

test('dải lương lấy từ khởi điểm thấp nhất đến mức cao nhất của nghề', () => {
  const nghe = { luong_khoi_diem_min: '7000000.00', luong_khoi_diem_max: '8500000.00', luong_cao_max: '13000000.00' }
  assert.equal(daiLuong(nghe, null), '7 - 13 triệu/tháng')
  assert.equal(daiLuong({ luong_khoi_diem_min: 7_000_000, luong_trung_binh_max: 10_000_000 }, null), '7 - 10 triệu/tháng')
})

test('nghề chưa có lương thì lấy lương nhóm, không có gì thì "Đang cập nhật"', () => {
  assert.equal(daiLuong({}, { muc_luong_text: '6 - 8 triệu/tháng' }), '6 - 8 triệu/tháng')
  assert.equal(daiLuong({}, { luong_khoi_diem_min: '6.00', luong_kinh_nghiem_max: '15.00' }), '6 - 15 triệu/tháng')
  assert.equal(daiLuong({}, {}), 'Đang cập nhật')
  assert.equal(daiLuong({}, null), 'Đang cập nhật')
})

test('lương không phải VND/tháng thì không đổi ra triệu/tháng', () => {
  assert.equal(khoangTrieu({ chu_ky_luong: 'gio' }, 30000, 50000), '')
  assert.equal(khoangTrieu({}, 8_000_000, 8_000_000), '8 triệu/tháng')
})

test('tách danh sách theo dấu chấm phẩy, bỏ mục rỗng', () => {
  assert.deepEqual(tachDanhSach(' Hàn TIG; ; cơ khí ;'), ['Hàn TIG', 'cơ khí'])
  assert.deepEqual(tachDanhSach(null), [])
})
