"""Bước 5.3: dọn kết quả đánh giá xét tuyển cũ."""

import unittest
from datetime import datetime, timedelta

from sqlalchemy import create_engine, func, select
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, SMALLINT
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session

import app.models as M
from app.scripts.don_ket_qua_xet_tuyen import don

BAY_GIO = datetime(2026, 11, 20, 3, 0)


@compiles(BIGINT, "sqlite")
@compiles(INTEGER, "sqlite")
@compiles(SMALLINT, "sqlite")
def _so_nguyen_sqlite(type_, compiler, **kw):
    return "INTEGER"


class DonKetQuaTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite://")
        for model in (M.NguoiDung, M.XtBoTieuChi, M.XtLanDanhGia, M.XtKetQuaPhuongAn, M.XtKetQuaChuongTrinh):
            model.__table__.create(engine)
        self.db = Session(engine)
        self.db.add(M.XtBoTieuChi(id=1, ma_bo="MD", ten_bo="Mặc định"))
        self.db.add(M.NguoiDung(id=7, ho_ten="HS", email="hs7@vd.vn", mat_khau="x"))
        self.db.commit()
        self.ids = {}

    def tearDown(self):
        self.db.close()

    def _lan(self, ten: str, ngay_truoc: int, nguoi_dung_id: int | None = None, nam: int = 2026) -> None:
        lan = M.XtLanDanhGia(
            nguoi_dung_id=nguoi_dung_id,
            ma_thiet_bi=None if nguoi_dung_id else "thiet-bi",
            nam_tuyen_sinh=nam,
            bo_tieu_chi_id=1,
            tao_luc=BAY_GIO - timedelta(days=ngay_truoc),
        )
        self.db.add(lan)
        self.db.flush()
        pa = M.XtKetQuaPhuongAn(
            lan_danh_gia_id=lan.id, phuong_an_id=1, de_an_chuong_trinh_id=1, cong_thuc_id=1, kieu_tinh="TONG", thang_diem=30
        )
        self.db.add(pa)
        self.db.flush()
        self.db.add(
            M.XtKetQuaChuongTrinh(lan_danh_gia_id=lan.id, de_an_chuong_trinh_id=1, ma_truong="BKA", ket_qua_phuong_an_id=pa.id)
        )
        self.db.commit()
        self.ids[ten] = lan.id

    def _con_lai(self) -> set[str]:
        con = set(self.db.scalars(select(M.XtLanDanhGia.id)))
        return {ten for ten, i in self.ids.items() if i in con}

    def test_chay_thu_roi_xoa_that(self):
        self._lan("khach_moi", 5)
        self._lan("khach_cu", 40)
        self._lan("tv_cu_2026", 400, 7)
        self._lan("tv_moi_nhat_cu_2026", 300, 7)  # cũ nhưng là lần mới nhất của năm 2026: giữ
        self._lan("tv_moi", 10, 7, nam=2027)

        thu = don(self.db, xoa=False, bay_gio=BAY_GIO)
        self.assertEqual((thu.so_lan_khach, thu.so_lan_thanh_vien, thu.so_dong_ket_qua), (1, 1, 4))
        self.assertEqual(len(self._con_lai()), 5)

        don(self.db, xoa=True, bay_gio=BAY_GIO, lo=1)
        self.assertEqual(self._con_lai(), {"khach_moi", "tv_moi_nhat_cu_2026", "tv_moi"})
        self.assertEqual(self.db.scalar(select(func.count()).select_from(M.XtKetQuaPhuongAn)), 3)
        self.assertEqual(self.db.scalar(select(func.count()).select_from(M.XtKetQuaChuongTrinh)), 3)

    def test_khong_co_gi_de_xoa(self):
        kq = don(self.db, xoa=True, bay_gio=BAY_GIO)
        self.assertEqual((kq.so_lan, kq.so_dong_ket_qua), (0, 0))


if __name__ == "__main__":
    unittest.main()
