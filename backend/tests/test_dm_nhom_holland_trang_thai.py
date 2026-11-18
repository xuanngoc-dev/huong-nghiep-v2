"""Bật/tắt nhanh trạng thái nhóm tính cách Holland (một và nhiều)."""

import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.v1.endpoints.dm_nhom_tinh_cach_holland import (
    update_trang_thai_nhom_tinh_cach_holland,
    update_trang_thai_nhom_tinh_cach_holland_many,
)
from app.models.dm_nhom_tinh_cach_holland import DmNhomTinhCachHolland
from app.schemas.dm_nhom_tinh_cach_holland import (
    DmNhomTinhCachHollandTrangThai,
    DmNhomTinhCachHollandTrangThaiMany,
)


class TrangThaiNhomHollandTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite://")
        DmNhomTinhCachHolland.__table__.create(engine)
        self.db = Session(engine)
        self.r = DmNhomTinhCachHolland(ma_nhom="R", ten_nhom="Kỹ thuật", ten_tieng_anh="Realistic", mo_ta="x")
        self.i = DmNhomTinhCachHolland(ma_nhom="I", ten_nhom="Nghiên cứu", ten_tieng_anh="Investigative")
        self.db.add_all([self.r, self.i])
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_tat_mot_nhom_giu_nguyen_thong_tin(self):
        item = update_trang_thai_nhom_tinh_cach_holland(
            self.r.id, DmNhomTinhCachHollandTrangThai(trang_thai=0), self.db
        )
        self.assertEqual((item.trang_thai, item.mo_ta), (0, "x"))

    def test_nhom_khong_ton_tai_tra_400(self):
        with self.assertRaises(HTTPException) as caught:
            update_trang_thai_nhom_tinh_cach_holland(999, DmNhomTinhCachHollandTrangThai(trang_thai=0), self.db)
        self.assertEqual(caught.exception.status_code, 400)

    def test_doi_nhieu_bo_qua_id_khong_ton_tai(self):
        payload = DmNhomTinhCachHollandTrangThaiMany(ids=[self.r.id, self.i.id, 999], trang_thai=0)
        self.assertEqual(update_trang_thai_nhom_tinh_cach_holland_many(payload, self.db).updated, 2)


if __name__ == "__main__":
    unittest.main()
