"""Loại câu hỏi: loại trả lời (điểm số / tình huống) và danh sách tiêu đề câu trả lời."""

import unittest

from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.v1.endpoints.dm_loai_cau_hoi import create_loai_cau_hoi, update_loai_cau_hoi
from app.models.dm_loai_cau_hoi import DmLoaiCauHoi
from app.schemas.dm_loai_cau_hoi import DmLoaiCauHoiPublic, DmLoaiCauHoiWrite


class LoaiTraLoiTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite://")
        DmLoaiCauHoi.__table__.create(engine)
        self.db = Session(engine)

    def tearDown(self):
        self.db.close()

    def test_mac_dinh_diem_so_va_khong_co_tieu_de(self):
        item = create_loai_cau_hoi(DmLoaiCauHoiWrite(ten_loai_cau_hoi="A", thu_tu_uu_tien=1), self.db)
        public = DmLoaiCauHoiPublic.model_validate(item)
        self.assertEqual((public.loai_tra_loi, public.danh_sach_tieu_de_cau_tra_loi), ("diem_so", None))

    def test_luu_va_sua_tieu_de(self):
        payload = DmLoaiCauHoiWrite(
            ten_loai_cau_hoi="A",
            thu_tu_uu_tien=1,
            danh_sach_tieu_de_cau_tra_loi=[" Rất không thích ", "", "Rất thích"],
        )
        item = create_loai_cau_hoi(payload, self.db)
        self.assertEqual(item.danh_sach_tieu_de_cau_tra_loi, ["Rất không thích", "Rất thích"])
        sua = DmLoaiCauHoiWrite(ten_loai_cau_hoi="A", thu_tu_uu_tien=1, loai_tra_loi="tinh_huong")
        item = update_loai_cau_hoi(item.id, sua, self.db)
        self.assertEqual((item.loai_tra_loi, item.danh_sach_tieu_de_cau_tra_loi), ("tinh_huong", None))

    def test_tu_choi_loai_tra_loi_la(self):
        with self.assertRaises(ValidationError):
            DmLoaiCauHoiWrite(ten_loai_cau_hoi="A", thu_tu_uu_tien=1, loai_tra_loi="khac")


if __name__ == "__main__":
    unittest.main()
