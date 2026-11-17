"""Xóa loại câu hỏi / câu hỏi: xem trước ảnh hưởng, chặn khi còn dữ liệu liên quan, xóa kèm khi được xác nhận."""

import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.api.v1.endpoints.dm_loai_cau_hoi import (
    anh_huong_xoa_loai_cau_hoi,
    delete_loai_cau_hoi,
    delete_loai_cau_hoi_many,
)
from app.api.v1.endpoints.tn_cau_hoi import anh_huong_xoa_cau_hoi, delete_cau_hoi, delete_cau_hoi_many
from app.models.dm_loai_cau_hoi import DmLoaiCauHoi
from app.models.tn_cau_hoi_trac_nghiem import TnCauHoiTracNghiem
from app.models.tn_cau_tra_loi import TnCauTraLoi
from app.models.tn_chi_tiet_tra_loi import TnChiTietTraLoi
from app.models.tn_phien_khao_sat import TnPhienKhaoSat
from app.schemas.dm_loai_cau_hoi import DmLoaiCauHoiDeleteMany
from app.schemas.tn_cau_hoi_trac_nghiem import TnCauHoiTracNghiemDeleteMany

_BANG = (DmLoaiCauHoi, TnCauHoiTracNghiem, TnCauTraLoi, TnPhienKhaoSat, TnChiTietTraLoi)


class XoaLoaiCauHoiTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite://")
        for model in _BANG:
            model.__table__.create(engine)
        self.db = db = Session(engine)
        self.loai_a = DmLoaiCauHoi(ten_loai_cau_hoi="A", thu_tu_uu_tien=1)
        self.loai_b = DmLoaiCauHoi(ten_loai_cau_hoi="B", thu_tu_uu_tien=2)
        self.loai_trong = DmLoaiCauHoi(ten_loai_cau_hoi="Trống", thu_tu_uu_tien=3)
        db.add_all([self.loai_a, self.loai_b, self.loai_trong])
        db.flush()
        self.ch_a = TnCauHoiTracNghiem(ma_holand="R", loai_cau_hoi_id=self.loai_a.id, noi_dung_cau_hoi="a")
        self.ch_b = TnCauHoiTracNghiem(ma_holand="I", loai_cau_hoi_id=self.loai_b.id, noi_dung_cau_hoi="b")
        db.add_all([self.ch_a, self.ch_b])
        db.flush()
        db.add_all(
            TnCauTraLoi(cau_hoi_id=ch.id, noi_dung_cau_tra_loi="x", diem=1) for ch in (self.ch_a, self.ch_a, self.ch_b)
        )
        # Phiên 1 có câu loại A và B; phiên 2 chỉ có câu loại B.
        db.add_all([TnPhienKhaoSat(ssid="p1"), TnPhienKhaoSat(ssid="p2")])
        db.add_all(
            [
                TnChiTietTraLoi(ssid="p1", loai_cau_hoi_id=self.loai_a.id, cau_hoi_id=self.ch_a.id),
                TnChiTietTraLoi(ssid="p1", loai_cau_hoi_id=self.loai_b.id, cau_hoi_id=self.ch_b.id),
                TnChiTietTraLoi(ssid="p2", loai_cau_hoi_id=self.loai_b.id, cau_hoi_id=self.ch_b.id),
            ]
        )
        db.commit()

    def tearDown(self):
        self.db.close()

    def _dem(self, model):
        return self.db.scalar(select(func.count()).select_from(model))

    def test_xem_truoc_anh_huong(self):
        kq = anh_huong_xoa_loai_cau_hoi(DmLoaiCauHoiDeleteMany(ids=[self.loai_a.id, 999]), self.db)
        self.assertEqual(kq.model_dump(), {"so_loai": 1, "so_cau_hoi": 1, "so_dap_an": 2, "so_phien": 1})

    def test_chua_xac_nhan_thi_chan_va_khong_xoa_gi(self):
        with self.assertRaises(HTTPException) as caught:
            delete_loai_cau_hoi(self.loai_a.id, False, self.db)
        self.assertEqual(caught.exception.status_code, 400)
        self.assertIn("1 câu hỏi", caught.exception.detail)
        self.assertEqual(self._dem(DmLoaiCauHoi), 3)

    def test_loai_khong_lien_quan_xoa_binh_thuong(self):
        delete_loai_cau_hoi(self.loai_trong.id, False, self.db)
        self.assertEqual(self._dem(DmLoaiCauHoi), 2)

    def test_xac_nhan_xoa_kem_cau_hoi_dap_an_va_ca_phien(self):
        delete_loai_cau_hoi(self.loai_a.id, True, self.db)
        self.assertEqual(self._dem(DmLoaiCauHoi), 2)
        self.assertEqual(self._dem(TnCauHoiTracNghiem), 1)
        self.assertEqual(self._dem(TnCauTraLoi), 1)
        # Phiên p1 bị xóa trọn (cả câu trả lời loại B); phiên p2 giữ nguyên.
        self.assertEqual(self.db.scalars(select(TnPhienKhaoSat.ssid)).all(), ["p2"])
        self.assertEqual(self._dem(TnChiTietTraLoi), 1)

    def test_xoa_nhieu_kem_lien_quan(self):
        kq = delete_loai_cau_hoi_many(DmLoaiCauHoiDeleteMany(ids=[self.loai_a.id, self.loai_b.id]), True, self.db)
        self.assertEqual(kq.deleted, 2)
        for model in (TnCauHoiTracNghiem, TnCauTraLoi, TnPhienKhaoSat, TnChiTietTraLoi):
            self.assertEqual(self._dem(model), 0)


class XoaCauHoiTests(unittest.TestCase):
    # Dùng chung dữ liệu: câu A (2 đáp án) ở phiên p1; câu B (1 đáp án) ở phiên p1, p2.
    setUp = XoaLoaiCauHoiTests.setUp
    tearDown = XoaLoaiCauHoiTests.tearDown
    _dem = XoaLoaiCauHoiTests._dem

    def test_xem_truoc_anh_huong(self):
        kq = anh_huong_xoa_cau_hoi(TnCauHoiTracNghiemDeleteMany(ids=[self.ch_b.id, 999]), self.db)
        self.assertEqual(kq.model_dump(), {"so_cau_hoi": 1, "so_dap_an": 1, "so_phien": 2})

    def test_chua_xac_nhan_thi_chan(self):
        with self.assertRaises(HTTPException) as caught:
            delete_cau_hoi(self.ch_a.id, False, self.db)
        self.assertIn("1 phiên", caught.exception.detail)
        self.assertEqual(self._dem(TnCauHoiTracNghiem), 2)

    def test_cau_hoi_chua_ai_lam_xoa_binh_thuong(self):
        moi = TnCauHoiTracNghiem(ma_holand="A", loai_cau_hoi_id=self.loai_trong.id, noi_dung_cau_hoi="c")
        self.db.add(moi)
        self.db.commit()
        delete_cau_hoi(moi.id, False, self.db)
        self.assertEqual(self._dem(TnCauHoiTracNghiem), 2)

    def test_xac_nhan_xoa_kem_dap_an_va_phien(self):
        delete_cau_hoi(self.ch_a.id, True, self.db)
        self.assertEqual(self._dem(TnCauHoiTracNghiem), 1)
        self.assertEqual(self._dem(TnCauTraLoi), 1)
        self.assertEqual(self.db.scalars(select(TnPhienKhaoSat.ssid)).all(), ["p2"])
        # Loại câu hỏi giữ nguyên.
        self.assertEqual(self._dem(DmLoaiCauHoi), 3)

    def test_xoa_nhieu_kem_lien_quan(self):
        kq = delete_cau_hoi_many(TnCauHoiTracNghiemDeleteMany(ids=[self.ch_a.id, self.ch_b.id]), True, self.db)
        self.assertEqual(kq.deleted, 2)
        for model in (TnCauHoiTracNghiem, TnCauTraLoi, TnPhienKhaoSat, TnChiTietTraLoi):
            self.assertEqual(self._dem(model), 0)


if __name__ == "__main__":
    unittest.main()
