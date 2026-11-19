import { test } from 'node:test'
import assert from 'node:assert/strict'
import { bangDiemTheoTruong, namMoiNhat } from '../src/utils/diemChuanTheoTruong.js'

const chuongTrinh = [
  {
    id: 2,
    ma_xet_tuyen: 'IT10',
    ten_chuong_trinh: 'Kỹ thuật phần mềm',
    chi_tieu_tuyen_sinh: 80,
    phuong_thuc: [{ ma_phuong_thuc_cua_bo: '100', to_hop_mon_hoc: ['A00'] }],
  },
  {
    id: 1,
    ma_xet_tuyen: 'IT1',
    ten_chuong_trinh: 'Khoa học máy tính',
    chi_tieu_tuyen_sinh: 200,
    phuong_thuc: [
      { ma_phuong_thuc_cua_bo: '100', to_hop_mon_hoc: ['A00', 'A01'] },
      { ma_phuong_thuc_cua_bo: '200', ma_phuong_thuc_cua_truong: 'XTHB', ten_phuong_thuc_cua_truong: 'Xét học bạ' },
    ],
  },
]

const diem = (ma, pt, giaTri, extra = {}) => ({ ma_xet_tuyen: ma, ma_phuong_thuc_cua_bo: pt, diem_chuan: giaTri, ...extra })

test('bangDiemTheoTruong: hàng theo chương trình, mỗi phương thức một cột kèm tổ hợp và điểm', () => {
  const { cotPhuongThuc, hang } = bangDiemTheoTruong({
    chuongTrinh,
    diemChuan: [diem('IT1', '100', 28, { ma_to_hop: 'A01' }), diem('IT1', '100', 27.5, { ma_to_hop: 'A00' })],
    danhMucPhuongThuc: [{ ma_phuong_thuc: '200', ten_phuong_thuc: 'Học bạ' }],
  })
  assert.deepEqual(cotPhuongThuc, [
    { ma: '100', nhan: '100', chiTiet: { ten: '', maTruong: [], tenTruong: [] } },
    { ma: '200', nhan: '200', chiTiet: { ten: 'Học bạ', maTruong: ['XTHB'], tenTruong: ['Xét học bạ'] } },
  ])
  assert.deepEqual(hang.map((h) => [h.ma_xet_tuyen, h.chi_tieu]), [['IT1', 200], ['IT10', 80]])
  const o = hang[0].o['100']
  assert.equal(o.dung, true)
  assert.deepEqual(o.toHop, ['A00', 'A01'])
  assert.deepEqual(o.diem.map((d) => d.diem_chuan), [27.5, 28])
  assert.deepEqual(hang[0].o['200'], { dung: true, toHop: [], diem: [] })
  assert.equal(hang[1].o['200'], undefined)
})

test('bangDiemTheoTruong: mã có điểm chuẩn ngoài đề án thành hàng riêng; điểm không phương thức vào cột chung', () => {
  const { cotPhuongThuc, hang } = bangDiemTheoTruong({
    chuongTrinh,
    diemChuan: [diem('EE1', null, 24, { ten_chuong_trinh: 'Điện' }), diem('IT1', '301', 90, { ten_phuong_thuc: 'Tuyển thẳng' })],
  })
  assert.deepEqual(cotPhuongThuc.map((c) => [c.ma, c.nhan]), [['', 'Mọi phương thức'], ['100', '100'], ['200', '200'], ['301', '301']])
  assert.equal(cotPhuongThuc[3].chiTiet.ten, 'Tuyển thẳng')
  assert.deepEqual(hang.map((h) => h.ma_xet_tuyen), ['EE1', 'IT1', 'IT10'])
  assert.equal(hang[0].ten_chuong_trinh, 'Điện')
  assert.equal(hang[0].chi_tieu, null)
  assert.equal(hang[1].o['301'].dung, false)
})

test('bangDiemTheoTruong: lọc từ khóa không dấu và lọc một phương thức', () => {
  assert.deepEqual(bangDiemTheoTruong({ chuongTrinh, q: 'phan mem' }).hang.map((h) => h.ma_xet_tuyen), ['IT10'])
  const loc = bangDiemTheoTruong({ chuongTrinh, maPhuongThuc: '200' })
  assert.deepEqual(loc.cotPhuongThuc.map((c) => c.ma), ['200'])
  assert.deepEqual(loc.hang.map((h) => h.ma_xet_tuyen), ['IT1'])
})

test('bangDiemTheoTruong: tiêu chí phụ gom theo nội dung, ghi kèm phương thức', () => {
  const { hang } = bangDiemTheoTruong({
    chuongTrinh,
    diemChuan: [
      diem('IT1', '200', 26, { tieu_chi_phu: 'Toán >= 8' }),
      diem('IT1', '100', 28, { ma_to_hop: 'A00', tieu_chi_phu: 'Toán >= 8' }),
      diem('IT1', '100', 27, { ma_to_hop: 'A01', tieu_chi_phu: ' ' }),
      diem('IT1', null, 25, { tieu_chi_phu: 'Thứ tự nguyện vọng <= 3' }),
    ],
  })
  assert.deepEqual(hang[0].tieuChiPhu, [
    { noiDung: 'Thứ tự nguyện vọng <= 3', phuongThuc: [''] },
    { noiDung: 'Toán >= 8', phuongThuc: ['100', '200'] },
  ])
  assert.deepEqual(hang[1].tieuChiPhu, [])
  const loc = bangDiemTheoTruong({ chuongTrinh, diemChuan: [diem('IT1', '200', 26, { tieu_chi_phu: 'X' })], maPhuongThuc: '100' })
  assert.deepEqual(loc.hang[0].tieuChiPhu, [])
})

test('namMoiNhat và dữ liệu rỗng', () => {
  assert.equal(namMoiNhat([{ nam_tuyen_sinh: 2024 }], [{ nam_tuyen_sinh: 2025 }]), 2025)
  assert.equal(namMoiNhat([], []), null)
  assert.deepEqual(bangDiemTheoTruong(), { cotPhuongThuc: [], hang: [] })
})
