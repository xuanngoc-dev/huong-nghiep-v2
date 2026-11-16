"""Bước 5.4: chạy thử quy tắc của một đề án bất kể trạng thái, kết quả cùng dạng bộ test hồi quy."""

import json
import unittest
from datetime import date

from fastapi import HTTPException
from sqlalchemy import select

import app.models as M
from app.api.v1.endpoints.xt_quy_tac import chay_thu_quy_tac
from app.schemas.xt_quy_tac import XtChayThuRequest
from app.services.xet_tuyen.chuyen_ho_so import tu_ho_so_hs
from tests import test_xet_tuyen_danh_gia as danh_gia
from tests.hoi_quy_xet_tuyen import THU_MUC, ho_so_tu_dict
from tests.test_xet_tuyen_ho_so_hs import HO_SO_A


class ChayThuTests(unittest.TestCase):
    setUpClass = classmethod(danh_gia.DanhGiaTuCsdlTests.setUpClass.__func__)
    tearDownClass = classmethod(danh_gia.DanhGiaTuCsdlTests.tearDownClass.__func__)

    def _de_an(self, ma_truong: str) -> M.DatsTuyenSinh:
        return self.db.scalars(select(M.DatsTuyenSinh).where(M.DatsTuyenSinh.ma_truong == ma_truong)).one()

    def test_de_an_thu_nghiem_chay_thu_khop_bo_hoi_quy(self):
        bka = self._de_an("BKA")
        bka.trang_thai_xet_tuyen = 1
        self.db.commit()
        try:
            kq = chay_thu_quy_tac(bka.id, XtChayThuRequest(ho_so=HO_SO_A, hom_nay=date(2026, 7, 1)), self.db)
        finally:
            bka.trang_thai_xet_tuyen = 2
            self.db.commit()
        self.assertEqual((kq.ma_truong, kq.trang_thai_xet_tuyen, kq.gia_dinh), ("BKA", 1, []))
        # Chỉ tính chương trình của đề án được chọn.
        mong_doi = json.loads((THU_MUC / "BKA_2026" / "ket_qua" / "A.json").read_text(encoding="utf-8"))
        thuc = kq.ket_qua.model_dump()
        self.assertEqual((thuc["so_phuong_an"], thuc["phuong_an"]), (mong_doi["so_phuong_an"], mong_doi["phuong_an"]))
        # Hồ sơ trả về đọc lại được như hồ sơ mẫu của bộ test hồi quy.
        hs = ho_so_tu_dict(json.loads(json.dumps(kq.ho_so_bo_tinh)))
        self.assertEqual(hs, tu_ho_so_hs(HO_SO_A, nam_tuyen_sinh=2026).ho_so)

    def test_de_an_chua_co_quy_tac(self):
        de_an = M.DatsTuyenSinh(ma_truong="NTH", nam_tuyen_sinh=2025, ten_de_an="Đề án 2025")
        self.db.add(de_an)
        self.db.commit()
        with self.assertRaises(HTTPException) as ctx:
            chay_thu_quy_tac(de_an.id, XtChayThuRequest(ho_so=HO_SO_A), self.db)
        self.assertEqual(ctx.exception.status_code, 400)
        with self.assertRaises(HTTPException) as ctx:
            chay_thu_quy_tac(987654, XtChayThuRequest(ho_so=HO_SO_A), self.db)
        self.assertIn("987654", ctx.exception.detail)


if __name__ == "__main__":
    unittest.main()
