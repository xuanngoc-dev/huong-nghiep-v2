import { test } from 'node:test'
import assert from 'node:assert/strict'
import {
  dongTuDanhSach,
  duongDan,
  khoangNam,
  locNhan,
  loiTat,
  o,
  oLink,
} from '../src/components/guest/tra-cuu/chi-tiet/phanChiTiet.js'

test('dòng thông tin: nối danh sách, thêm đơn vị, giữ giá trị 0', () => {
  assert.deepEqual(o('Bậc đào tạo', ['Đại học', '', null, 'Thạc sĩ']), { label: 'Bậc đào tạo', giaTri: 'Đại học, Thạc sĩ' })
  assert.equal(o('Thời hạn', 24, { donVi: 'tháng' }).giaTri, '24 tháng')
  assert.equal(o('Thời lượng', 0, { donVi: 'phút' }).giaTri, '0 phút')
  assert.equal(o('Thời lượng', null, { donVi: 'phút' }).giaTri, null)
  assert.deepEqual(locNhan(['Hà Nội', '', '  ', null, 'Công lập']), ['Hà Nội', 'Công lập'])
})

test('link: thêm https://, mailto:, tel: bỏ ký tự thừa; bỏ lối tắt không có link', () => {
  assert.equal(duongDan('hust.edu.vn'), 'https://hust.edu.vn')
  assert.equal(duongDan(' http://a.vn '), 'http://a.vn')
  assert.equal(oLink('Email', 'a@b.vn', 'email').href, 'mailto:a@b.vn')
  assert.equal(oLink('Hotline', '024 3869.4242', 'tel').href, 'tel:02438694242')
  assert.equal(oLink('Website', '', 'web').href, undefined)
  assert.deepEqual(loiTat([{ label: 'Website', url: 'act.org' }, { label: 'Nguồn', url: null }]), [
    { label: 'Website', href: 'https://act.org' },
  ])
})

test('danh sách mô tả của ngành → dòng, bỏ mục không có nội dung', () => {
  assert.deepEqual(
    dongTuDanhSach([
      { name: 'Nhiệm vụ', value: 'Phát triển phần mềm', ghi_chu: 'Tham khảo' },
      { name: 'Trống', value: '' },
      null,
    ]),
    [{ label: 'Nhiệm vụ', giaTri: 'Phát triển phần mềm', ghiChu: 'Tham khảo' }],
  )
  assert.deepEqual(dongTuDanhSach(null), [])
})

test('năm áp dụng', () => {
  assert.equal(khoangNam(2026, null), 'Từ 2026')
  assert.equal(khoangNam(2026, 2028), '2026 – 2028')
  assert.equal(khoangNam(2026, 2026), '2026')
  assert.equal(khoangNam(null, 2028), 'Đến 2028')
  assert.equal(khoangNam(null, undefined), null)
})
