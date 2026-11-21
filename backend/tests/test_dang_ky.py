"""Đăng ký tài khoản: lưu đối tượng (nguoi_dung.doi_tuong) và tỉnh thành (nguoi_dung_thong_tin.tinh_thanh_id);
phiên chat mới của thành viên dùng đối tượng của tài khoản."""

import unittest

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import register
from app.api.v1.endpoints.chat import doi_tuong_cho_phien
from app.models.dm_doi_tuong_uu_tien import DmDoiTuongUuTien
from app.models.dm_khu_vuc_uu_tien import DmKhuVucUuTien
from app.models.dm_tinh_thanh import DmTinhThanh
from app.models.nguoi_dung import NguoiDung
from app.models.nguoi_dung_thong_tin import NguoiDungThongTin
from app.schemas.auth import RegisterRequest


def _yeu_cau(**kw) -> RegisterRequest:
    data = {"ho_ten": "Nguyễn Văn A", "email": "a@example.com", "mat_khau": "matkhau123"}
    data.update(kw)
    return RegisterRequest(**data)


class DangKyTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite://")
        for model in (DmTinhThanh, DmKhuVucUuTien, DmDoiTuongUuTien, NguoiDung, NguoiDungThongTin):
            model.__table__.create(engine)
        self.db = Session(engine)
        self.tinh = DmTinhThanh(ten_tinh="Hà Nội", ma_tinh="01")
        self.db.add(self.tinh)
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def _thong_tin(self, nguoi_dung_id):
        return self.db.scalar(select(NguoiDungThongTin).where(NguoiDungThongTin.nguoi_dung_id == nguoi_dung_id))

    def test_luu_doi_tuong_va_tinh_thanh(self):
        kq = register(_yeu_cau(doi_tuong="thpt-du-hoc", tinh_thanh_id=self.tinh.id), db=self.db)
        self.assertEqual(kq.user.doi_tuong, "thpt-du-hoc")
        self.assertEqual(self.db.get(NguoiDung, kq.user.id).doi_tuong, "thpt-du-hoc")
        self.assertEqual(self._thong_tin(kq.user.id).tinh_thanh_id, self.tinh.id)

    def test_khong_chon_thi_de_trong(self):
        kq = register(_yeu_cau(), db=self.db)
        self.assertIsNone(kq.user.doi_tuong)
        self.assertIsNone(self._thong_tin(kq.user.id))

    def test_doi_tuong_khong_hop_le(self):
        with self.assertRaises(ValidationError):
            _yeu_cau(doi_tuong="hoc-sinh")

    def test_doi_tuong_rong_coi_nhu_khong_chon(self):
        self.assertIsNone(_yeu_cau(doi_tuong="  ").doi_tuong)

    def test_tinh_thanh_khong_ton_tai_tra_400(self):
        with self.assertRaises(HTTPException) as ctx:
            register(_yeu_cau(tinh_thanh_id=999), db=self.db)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("999", ctx.exception.detail)
        self.assertIsNone(self.db.scalar(select(NguoiDung)))

    def test_phien_chat_dung_doi_tuong_tai_khoan(self):
        kq = register(_yeu_cau(doi_tuong="phu-huynh"), db=self.db)
        # Client gửi đối tượng khác (vd. theo trang đang xem) vẫn dùng đối tượng của tài khoản.
        self.assertEqual(doi_tuong_cho_phien(self.db, kq.user.id, "thpt-thi-dai-hoc"), "phu-huynh")

    def test_phien_chat_tai_khoan_chua_chon_dung_gia_tri_client(self):
        kq = register(_yeu_cau(email="b@example.com"), db=self.db)
        self.assertEqual(doi_tuong_cho_phien(self.db, kq.user.id, "sinh-vien"), "sinh-vien")
        self.assertEqual(doi_tuong_cho_phien(self.db, None, "sinh-vien"), "sinh-vien")


if __name__ == "__main__":
    unittest.main()
