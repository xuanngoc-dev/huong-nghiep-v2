"""Bật/tắt nhanh trạng thái câu hỏi trắc nghiệm (một và nhiều)."""

import unittest

from fastapi import HTTPException

from app.api.v1.endpoints.tn_cau_hoi import update_trang_thai_cau_hoi, update_trang_thai_cau_hoi_many
from app.schemas.tn_cau_hoi_trac_nghiem import TnCauHoiTrangThai, TnCauHoiTrangThaiMany
from tests import test_xoa_trac_nghiem as mau


class TrangThaiCauHoiTests(unittest.TestCase):
    # Dữ liệu mẫu: câu hỏi ch_a (loại A), ch_b (loại B), đều đang hoạt động.
    setUp = mau.XoaLoaiCauHoiTests.setUp
    tearDown = mau.XoaLoaiCauHoiTests.tearDown

    def test_tat_mot_cau_hoi_giu_nguyen_noi_dung(self):
        kq = update_trang_thai_cau_hoi(self.ch_a.id, TnCauHoiTrangThai(trang_thai=0), self.db)
        self.assertEqual((kq.id, kq.trang_thai), (self.ch_a.id, 0))
        self.db.refresh(self.ch_a)
        self.assertEqual((self.ch_a.trang_thai, self.ch_a.noi_dung_cau_hoi), (0, "a"))

    def test_cau_hoi_khong_ton_tai_tra_400(self):
        with self.assertRaises(HTTPException) as caught:
            update_trang_thai_cau_hoi(999, TnCauHoiTrangThai(trang_thai=0), self.db)
        self.assertEqual(caught.exception.status_code, 400)

    def test_doi_nhieu_bo_qua_id_khong_ton_tai(self):
        payload = TnCauHoiTrangThaiMany(ids=[self.ch_a.id, self.ch_b.id, 999], trang_thai=0)
        self.assertEqual(update_trang_thai_cau_hoi_many(payload, self.db).updated, 2)
        for ch in (self.ch_a, self.ch_b):
            self.db.refresh(ch)
            self.assertEqual(ch.trang_thai, 0)


if __name__ == "__main__":
    unittest.main()
