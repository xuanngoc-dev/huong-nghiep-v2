import { test } from 'node:test'
import assert from 'node:assert/strict'
import { laNgheDiLamNgay, loaiNghe } from '../src/components/guest/doi-tuong/HocSinhThpt/di-lam/nhomNghe.js'

const DS = [
  { ten_nghe: 'Hộ lý', yeu_cau_bang_cap: null, bat_buoc_dao_tao_chinh_quy: null },
  { ten_nghe: 'Phụ quầy', yeu_cau_bang_cap: '  ', bat_buoc_dao_tao_chinh_quy: 0 },
  { ten_nghe: 'Lái xe tải', yeu_cau_bang_cap: 'Giấy phép lái xe hạng C', bat_buoc_dao_tao_chinh_quy: null },
  { ten_nghe: 'Bác sĩ', yeu_cau_bang_cap: 'Bằng bác sĩ', bat_buoc_dao_tao_chinh_quy: 1 },
]

test('phân loại nghề: chính quy ưu tiên hơn bằng cấp; bằng cấp rỗng, 0 coi như không yêu cầu', () => {
  assert.deepEqual(DS.map(loaiNghe), ['di_lam_ngay', 'di_lam_ngay', 'can_bang_cap', 'chinh_quy'])
})

test('hướng đi làm ngay chỉ bỏ nghề bắt buộc chính quy; nghề cần chứng chỉ, giấy phép vẫn giữ', () => {
  assert.deepEqual(DS.filter(laNgheDiLamNgay).map((n) => n.ten_nghe), ['Hộ lý', 'Phụ quầy', 'Lái xe tải'])
})
