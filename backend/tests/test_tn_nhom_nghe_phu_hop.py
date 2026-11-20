"""Gợi ý nhóm nghề đi làm theo kết quả Holland: chỉ xét 3 mã nổi bật, trọng số 3/2/1."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session

from app.api.v1.endpoints import tn_phien_khao_sat as phien_api
from app.db.base import Base
from app.models.dm_nhom_nghe_di_lam import DmNhomNgheDiLam
from app.schemas.tn_phien_khao_sat import TnPhienDiemHolland


@compiles(TINYINT, "sqlite")
def _so_nguyen_sqlite(type_, compiler, **kw):
    return "INTEGER"


def _diem(ma, diem):
    return TnPhienDiemHolland(ma_nhom=ma, ten_nhom=ma, diem=diem)


class TestNhomNghePhuHop(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite://")
        Base.metadata.create_all(engine, tables=[DmNhomNgheDiLam.__table__])
        self.db = Session(engine)
        for ma, holland, trang_thai in [
            ("BEP", "RAS", 1),
            ("CONG_NHAN", "RC", 1),
            ("SANG_TAO", "AIE", 1),
            ("TAT", "RSC", 0),
        ]:
            self.db.add(
                DmNhomNgheDiLam(ma_nhom=ma, ten_nhom=ma, mo_ta_dac_diem="x", ma_holland=holland, trang_thai=trang_thai)
            )
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def _goi(self, nhom):
        # Kết quả Holland của phiên: sắp giảm dần theo điểm như _thong_ke_phien trả về.
        with (
            patch.object(phien_api, "_phien_or_400", return_value=SimpleNamespace(ssid="s", ma_giao_dich=None)),
            patch.object(phien_api, "_thong_ke_phien", return_value=(10, 10, nhom, [])),
        ):
            return phien_api.lay_nhom_nghe_phu_hop("s", db=self.db)

    def test_chi_xet_3_ma_noi_bat_va_bo_nhom_ngung(self):
        kq = self._goi([_diem("R", 9), _diem("S", 8), _diem("C", 7), _diem("I", 3), _diem("E", 2), _diem("A", 1)])
        self.assertEqual(kq.ma_noi_bat, "RSC")
        # RAS khớp R(3)+S(2)=5; RC khớp R(3)+C(1)=4; AIE không khớp mã nổi bật; RSC đang ngừng sử dụng.
        self.assertEqual([(n.ma_nhom, n.diem_khop, n.ma_khop) for n in kq.nhom_nghe], [
            ("BEP", 5, ["R", "S"]),
            ("CONG_NHAN", 4, ["R", "C"]),
        ])
        self.assertTrue(kq.da_xong)

    def test_chua_co_diem_thi_khong_goi_y(self):
        kq = self._goi([_diem("R", 0), _diem("A", 0)])
        self.assertEqual((kq.ma_noi_bat, kq.nhom_nghe), ("", []))


if __name__ == "__main__":
    unittest.main()
