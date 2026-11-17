"""Quản trị xóa phiên trắc nghiệm (một hoặc nhiều), kèm câu trả lời của phiên."""

import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.api.v1.endpoints.tn_phien_khao_sat import xoa_nhieu_phien_quan_tri, xoa_phien_quan_tri
from app.models.tn_chi_tiet_tra_loi import TnChiTietTraLoi
from app.models.tn_phien_khao_sat import TnPhienKhaoSat
from app.schemas.tn_phien_khao_sat import TnPhienDeleteMany


class XoaPhienTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite://")
        for model in (TnPhienKhaoSat, TnChiTietTraLoi):
            model.__table__.create(engine)
        self.db = Session(engine)
        self.phien = [TnPhienKhaoSat(ssid=f"ssid{i}") for i in range(3)]
        self.db.add_all(self.phien)
        self.db.add_all(
            TnChiTietTraLoi(ssid=p.ssid, loai_cau_hoi_id=1, cau_hoi_id=1) for p in self.phien for _ in range(2)
        )
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def _dem(self, model):
        return self.db.scalar(select(func.count()).select_from(model))

    def test_xoa_mot_phien_xoa_ca_cau_tra_loi(self):
        xoa_phien_quan_tri(self.phien[0].id, self.db)
        self.assertEqual(self._dem(TnPhienKhaoSat), 2)
        self.assertEqual(self._dem(TnChiTietTraLoi), 4)

    def test_xoa_phien_khong_ton_tai_tra_400(self):
        with self.assertRaises(HTTPException) as caught:
            xoa_phien_quan_tri(999, self.db)
        self.assertEqual(caught.exception.status_code, 400)
        self.assertIn("999", caught.exception.detail)

    def test_xoa_nhieu_bo_qua_id_khong_ton_tai(self):
        ket_qua = xoa_nhieu_phien_quan_tri(TnPhienDeleteMany(ids=[self.phien[0].id, self.phien[1].id, 999]), self.db)
        self.assertEqual(ket_qua.deleted, 2)
        self.assertEqual(self._dem(TnPhienKhaoSat), 1)
        self.assertEqual(self._dem(TnChiTietTraLoi), 2)
        self.assertEqual(xoa_nhieu_phien_quan_tri(TnPhienDeleteMany(ids=[999]), self.db).deleted, 0)


if __name__ == "__main__":
    unittest.main()
