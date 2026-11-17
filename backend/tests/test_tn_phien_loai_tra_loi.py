"""Bài làm của phiên trả kèm loại trả lời và tiêu đề câu trả lời của từng loại câu hỏi."""

import unittest

from app.api.v1.endpoints.tn_phien_khao_sat import lay_de_bai
from tests import test_xoa_trac_nghiem as mau


class PhienLoaiTraLoiTests(unittest.TestCase):
    # Dữ liệu mẫu: phiên p1 có câu thuộc loại A và B; p2 chỉ có câu loại B.
    setUp = mau.XoaLoaiCauHoiTests.setUp
    tearDown = mau.XoaLoaiCauHoiTests.tearDown

    def test_tra_loai_cau_hoi_theo_thu_tu_va_khong_lap(self):
        self.loai_a.danh_sach_tieu_de_cau_tra_loi = [{"tieu_de": "Thích", "diem": 5}]
        self.loai_b.loai_tra_loi = "tinh_huong"
        self.db.commit()

        loai = lay_de_bai("p1", self.db).loai_cau_hoi
        self.assertEqual([x.id for x in loai], [self.loai_a.id, self.loai_b.id])
        self.assertEqual(loai[0].loai_tra_loi, "diem_so")
        self.assertEqual(loai[0].danh_sach_tieu_de_cau_tra_loi[0].model_dump(), {"tieu_de": "Thích", "diem": 5})
        self.assertEqual((loai[1].loai_tra_loi, loai[1].danh_sach_tieu_de_cau_tra_loi), ("tinh_huong", None))

        self.assertEqual([x.id for x in lay_de_bai("p2", self.db).loai_cau_hoi], [self.loai_b.id])


if __name__ == "__main__":
    unittest.main()
