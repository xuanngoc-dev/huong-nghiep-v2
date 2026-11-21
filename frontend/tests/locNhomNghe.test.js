import { test } from 'node:test'
import assert from 'node:assert/strict'
import { locNgheCuThe } from '../src/components/guest/doi-tuong/HocSinhThpt/di-lam/nhomNghe.js'

// Lương từ API là chuỗi Decimal ("6.00").
const NHOM = {
  1: { id: 1, ma_nhom: 'BAN_HANG', ten_nhom: 'Bán hàng', nhom_muc_tieu: 'kiem_tien_ngay',
    luong_khoi_diem_min: '6.00', luong_kinh_nghiem_max: '20.00' },
  2: { id: 2, ma_nhom: 'Y_TE', ten_nhom: 'Y tế, chăm sóc sức khỏe', nhom_muc_tieu: 'nghe_vung_chac',
    luong_khoi_diem_min: '8.00', luong_kinh_nghiem_max: '40.00' },
}
const NGHE = [
  { id: 1, nhom_nghe_di_lam_id: 1, ten_nghe: 'Nhân viên bán hàng', mo_ta_ngan: 'Tư vấn tại siêu thị' },
  { id: 2, nhom_nghe_di_lam_id: 1, ten_nghe: 'Tư vấn bảo hiểm', yeu_cau_bang_cap: 'Chứng chỉ đại lý' },
  { id: 3, nhom_nghe_di_lam_id: 2, ten_nghe: 'Hộ lý', mo_ta_ngan: 'Chăm sóc người bệnh' },
  { id: 4, nhom_nghe_di_lam_id: 2, ten_nghe: 'Bác sĩ', yeu_cau_bang_cap: 'Bằng bác sĩ', bat_buoc_dao_tao_chinh_quy: 1 },
  { id: 5, nhom_nghe_di_lam_id: 99, ten_nghe: 'Nghề của nhóm đã tắt' },
]

const id = (kw) => locNgheCuThe(NGHE, NHOM, kw).map((n) => n.id)

test('bỏ nghề bắt buộc chính quy và nghề của nhóm đã tắt; nghề cần chứng chỉ vẫn giữ', () => {
  assert.deepEqual(id({}), [1, 2, 3])
})

test('từ khóa không dấu: tên nghề, mô tả và tên nhóm', () => {
  assert.deepEqual(id({ tuKhoa: 'sieu thi' }), [1])
  assert.deepEqual(id({ tuKhoa: 'Y TẾ' }), [3])
  assert.deepEqual(id({ tuKhoa: 'bac si' }), [])
})

test('lọc theo nhóm, mục tiêu, mức lương của nhóm', () => {
  assert.deepEqual(id({ nhomId: 2 }), [3])
  assert.deepEqual(id({ mucTieu: 'kiem_tien_ngay' }), [1, 2])
  assert.deepEqual(id({ mucLuong: 'kd_8' }), [3])
  assert.deepEqual(id({ mucLuong: 'kn_30' }), [3])
})

test('kết hợp nhiều bộ lọc', () => {
  assert.deepEqual(id({ nhomId: 1, tuKhoa: 'bao hiem' }), [2])
  assert.deepEqual(id({ mucTieu: 'kiem_tien_ngay', mucLuong: 'kd_8' }), [])
})
