import test from 'node:test'
import assert from 'node:assert/strict'
import {
  docQuanTam,
  ghiQuanTam,
  khoangCach,
  ngheGoiY,
  nhanXetTongQuan,
  theoThuTuRiasec,
  xepHang,
} from '../src/utils/ketQuaHolland.js'

const nhom = (diem) =>
  Object.entries(diem).map(([ma_nhom, d]) => ({ ma_nhom, ten_nhom: `Nhóm ${ma_nhom}`, diem: d }))

test('xếp hạng bỏ nhóm 0 điểm, bằng điểm theo thứ tự RIASEC', () => {
  const top = xepHang(nhom({ C: 5, I: 9, R: 9, A: 0 }))
  assert.deepEqual(top.map((x) => x.ma_nhom), ['R', 'I', 'C'])
  assert.deepEqual(theoThuTuRiasec(nhom({ S: 3 })).map((x) => x.diem), [0, 0, 0, 3, 0, 0])
})

test('khoảng cách trên lục giác Holland', () => {
  assert.equal(khoangCach('R', 'I'), 1)
  assert.equal(khoangCach('R', 'C'), 1)
  assert.equal(khoangCach('R', 'S'), 3)
  assert.equal(khoangCach('I', 'E'), 3)
})

test('nhận xét: nhóm nổi bật, hai nhóm đầu cạnh nhau, luôn nhắc không phải năng lực', () => {
  const doan = nhanXetTongQuan(nhom({ R: 20, I: 15, A: 4, S: 3, E: 2, C: 5 }))
  assert.match(doan[0], /Nhóm R \(R\).*Nhóm I \(I\) và Nhóm C \(C\)/)
  assert.ok(doan.some((d) => d.includes('nổi bật hơn hẳn')))
  assert.ok(doan.some((d) => d.includes('nhất quán')))
  assert.match(doan.at(-1), /không phải thước đo năng lực/)
})

test('nhận xét: điểm đồng đều và hai nhóm đối diện', () => {
  const doan = nhanXetTongQuan(nhom({ R: 10, I: 9, A: 9, S: 10, E: 9, C: 9 }))
  assert.ok(doan.some((d) => d.includes('khá đồng đều')))
  assert.ok(doan.some((d) => d.includes('khá khác nhau')))
  assert.equal(nhanXetTongQuan(nhom({ R: 0 })).length, 1)
})

test('nghề gợi ý tách từ ví dụ nghề, không lặp giữa các nhóm', () => {
  const danhMuc = [
    { ma_nhom: 'I', vi_du_nghe_nghiep: 'bác sĩ, kỹ sư phần mềm, nhà nghiên cứu' },
    { ma_nhom: 'S', vi_du_nghe_nghiep: 'Giáo viên, Bác sĩ, y tá' },
  ]
  const nghe = ngheGoiY(nhom({ I: 9, S: 5 }), danhMuc, 2)
  assert.deepEqual(nghe.map((x) => [x.ten, x.ma_nhom]), [
    ['Bác sĩ', 'I'],
    ['Kỹ sư phần mềm', 'I'],
    ['Giáo viên', 'S'],
    ['Y tá', 'S'],
  ])
  assert.ok(nghe[0].mo_ta)
})

test('danh sách quan tâm đọc / ghi an toàn khi bộ nhớ lỗi', () => {
  const data = new Map()
  const storage = { getItem: (k) => data.get(k), setItem: (k, v) => data.set(k, v) }
  assert.deepEqual(docQuanTam(storage, 'abc'), { nganh: [], truong: [] })
  ghiQuanTam(storage, 'abc', { nganh: [{ ma_nganh: '7480201' }], truong: [] })
  assert.equal(docQuanTam(storage, 'abc').nganh[0].ma_nganh, '7480201')
  const hong = { getItem: () => { throw new Error('x') }, setItem: () => { throw new Error('x') } }
  assert.deepEqual(docQuanTam(hong, 'abc'), { nganh: [], truong: [] })
  assert.equal(ghiQuanTam(hong, 'abc', {}), false)
})
