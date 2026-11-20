"""Thứ tự ưu tiên loại câu hỏi được trùng: cùng thứ tự thì loại tạo trước đứng trước."""

import unittest
from datetime import datetime

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models.dm_loai_cau_hoi import THU_TU_LOAI_CAU_HOI, DmLoaiCauHoi


class TestThuTuLoaiCauHoi(unittest.TestCase):
    def test_trung_thu_tu_thi_tao_truoc_dung_truoc(self):
        engine = create_engine("sqlite://")
        Base.metadata.create_all(engine, tables=[DmLoaiCauHoi.__table__])
        with Session(engine) as db:
            db.add_all(
                [
                    DmLoaiCauHoi(ten_loai_cau_hoi="B tạo sau", thu_tu_uu_tien=2, created_at=datetime(2026, 1, 2)),
                    DmLoaiCauHoi(ten_loai_cau_hoi="A", thu_tu_uu_tien=1, created_at=datetime(2026, 1, 3)),
                    DmLoaiCauHoi(ten_loai_cau_hoi="B tạo trước", thu_tu_uu_tien=2, created_at=datetime(2026, 1, 1)),
                ]
            )
            db.commit()
            ten = [item.ten_loai_cau_hoi for item in db.scalars(select(DmLoaiCauHoi).order_by(*THU_TU_LOAI_CAU_HOI))]
        self.assertEqual(ten, ["A", "B tạo trước", "B tạo sau"])

    def test_khong_con_rang_buoc_unique(self):
        self.assertFalse(DmLoaiCauHoi.__table__.c.thu_tu_uu_tien.unique)


if __name__ == "__main__":
    unittest.main()
