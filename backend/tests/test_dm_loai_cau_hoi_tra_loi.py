"""Loại câu hỏi: loại trả lời (điểm số / tình huống) và danh sách tiêu đề câu trả lời."""

import unittest

from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.v1.endpoints.dm_loai_cau_hoi import (
    create_loai_cau_hoi,
    update_loai_cau_hoi,
    update_trang_thai_loai_cau_hoi,
    update_trang_thai_loai_cau_hoi_many,
)
from app.models.dm_loai_cau_hoi import DmLoaiCauHoi
from app.schemas.dm_loai_cau_hoi import (
    DmLoaiCauHoiPublic,
    DmLoaiCauHoiTrangThai,
    DmLoaiCauHoiTrangThaiMany,
    DmLoaiCauHoiWrite,
)


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
            danh_sach_tieu_de_cau_tra_loi=[
                {"tieu_de": " Rất không thích ", "diem": 1},
                {"tieu_de": "", "diem": 2},
                {"tieu_de": "Rất thích", "diem": 5},
            ],
        )
        item = create_loai_cau_hoi(payload, self.db)
        self.assertEqual(
            item.danh_sach_tieu_de_cau_tra_loi,
            [{"tieu_de": "Rất không thích", "diem": 1}, {"tieu_de": "Rất thích", "diem": 5}],
        )
        sua = DmLoaiCauHoiWrite(ten_loai_cau_hoi="A", thu_tu_uu_tien=1, loai_tra_loi="tinh_huong")
        item = update_loai_cau_hoi(item.id, sua, self.db)
        self.assertEqual((item.loai_tra_loi, item.danh_sach_tieu_de_cau_tra_loi), ("tinh_huong", None))

    def test_doc_duoc_du_lieu_cu_dang_chuoi(self):
        item = DmLoaiCauHoi(ten_loai_cau_hoi="A", thu_tu_uu_tien=1, danh_sach_tieu_de_cau_tra_loi=["Thích"])
        self.db.add(item)
        self.db.commit()
        public = DmLoaiCauHoiPublic.model_validate(item)
        self.assertEqual(public.model_dump()["danh_sach_tieu_de_cau_tra_loi"], [{"tieu_de": "Thích", "diem": None}])

    def test_bat_tat_giu_nguyen_cau_hinh_tra_loi(self):
        payload = DmLoaiCauHoiWrite(
            ten_loai_cau_hoi="A",
            thu_tu_uu_tien=1,
            loai_tra_loi="tinh_huong",
            danh_sach_tieu_de_cau_tra_loi=[{"tieu_de": "Có", "diem": 1}],
        )
        item = create_loai_cau_hoi(payload, self.db)
        item = update_trang_thai_loai_cau_hoi(item.id, DmLoaiCauHoiTrangThai(trang_thai=0), self.db)
        self.assertEqual(
            (item.trang_thai, item.loai_tra_loi, item.danh_sach_tieu_de_cau_tra_loi),
            (0, "tinh_huong", [{"tieu_de": "Có", "diem": 1}]),
        )
        nhieu = DmLoaiCauHoiTrangThaiMany(ids=[item.id, 999], trang_thai=1)
        self.assertEqual(update_trang_thai_loai_cau_hoi_many(nhieu, self.db).updated, 1)

    def test_tu_choi_loai_tra_loi_la(self):
        with self.assertRaises(ValidationError):
            DmLoaiCauHoiWrite(ten_loai_cau_hoi="A", thu_tu_uu_tien=1, loai_tra_loi="khac")


if __name__ == "__main__":
    unittest.main()
