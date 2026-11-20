"""Danh mục hướng đi sau THCS: hướng đi, ưu/nhược điểm, tiêu chí, điểm phù hợp theo tiêu chí, lời khuyên lưu ý."""

import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine, event
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session

import app.models as M
from app.api.v1.endpoints import (
    dm_thcs_huong_di as huong_di,
    dm_thcs_huong_di_tieu_chi as huong_di_tieu_chi,
    dm_thcs_loi_khuyen_luu_y as loi_khuyen,
    dm_thcs_tieu_chi as tieu_chi,
    dm_thcs_uu_nhuoc_diem as uu_nhuoc,
)
from app.db.base import Base
from app.schemas.dm_thcs_huong_di import (
    DmThcsDeleteMany,
    DmThcsHuongDiTieuChiDeleteMany,
    DmThcsHuongDiTieuChiUpdate,
    DmThcsHuongDiTieuChiWrite,
    DmThcsHuongDiWrite,
    DmThcsLoiKhuyenLuuYWrite,
    DmThcsTieuChiWrite,
    DmThcsUuNhuocDiemWrite,
)


@compiles(TINYINT, "sqlite")
def _so_nguyen_sqlite(type_, compiler, **kw):
    return "INTEGER"


_BANG = [M.DmThcsHuongDi, M.DmThcsUuNhuocDiem, M.DmThcsTieuChi, M.DmThcsHuongDiTieuChi, M.DmThcsLoiKhuyenLuuY]
_TRANG = {"page": 1, "page_size": 10}


def _ds_huong(db, **kw):
    return huong_di.list_thcs_huong_di(**{"q": None, "trang_thai": None, "muc_do_ap_luc_hoc_tap": None, **_TRANG, **kw},
                                       db=db)


def _ds_uu_nhuoc(db, **kw):
    return uu_nhuoc.list_thcs_uu_nhuoc_diem(**{"q": None, "thcs_huong_di_id": None, "loai": None, **_TRANG, **kw}, db=db)


def _ds_tieu_chi(db, **kw):
    return tieu_chi.list_thcs_tieu_chi(**{"q": None, "nhom_tieu_chi": None, **_TRANG, **kw}, db=db)


def _ds_diem(db, **kw):
    return huong_di_tieu_chi.list_thcs_huong_di_tieu_chi(
        **{"q": None, "thcs_huong_di_id": None, "thcs_tieu_chi_id": None, **_TRANG, **kw}, db=db
    )


def _ds_loi_khuyen(db, **kw):
    return loi_khuyen.list_thcs_loi_khuyen_luu_y(
        **{"q": None, "thcs_huong_di_id": None, "doi_tuong_nhan": None, **_TRANG, **kw}, db=db
    )


class TestDmThcsHuongDi(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite://")
        event.listen(engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
        Base.metadata.create_all(engine, tables=[m.__table__ for m in _BANG])
        self.db = Session(engine)

    def tearDown(self):
        self.db.close()

    def _huong(self, ma="thpt_cong_lap", ten="THPT công lập", **kw):
        return huong_di.create_thcs_huong_di(
            DmThcsHuongDiWrite(ma_huong=f" {ma} ", ten_huong=ten, mo_ta_tong_quan="X", **kw), db=self.db, _=None
        )

    def _tieu_chi(self, ma="hoc_luc", ten="Học lực", nhom="Năng lực"):
        return tieu_chi.create_thcs_tieu_chi(
            DmThcsTieuChiWrite(ma_tieu_chi=ma, ten_tieu_chi=ten, nhom_tieu_chi=nhom), db=self.db, _=None
        )

    def test_danh_sach_rong_tra_dung_cau_truc(self):
        for ds in (_ds_huong, _ds_uu_nhuoc, _ds_tieu_chi, _ds_diem, _ds_loi_khuyen):
            with self.subTest(ds=ds.__name__):
                page = ds(self.db)
                self.assertEqual((page.items, page.total, page.page, page.page_size), ([], 0, 1, 10))
        self.assertEqual(tieu_chi.list_thcs_nhom_tieu_chi(db=self.db), [])

    def test_id_khong_ton_tai_tra_400(self):
        for module, ham in ((huong_di, "get_thcs_huong_di"), (uu_nhuoc, "get_thcs_uu_nhuoc_diem"),
                            (tieu_chi, "get_thcs_tieu_chi"), (loi_khuyen, "get_thcs_loi_khuyen_luu_y")):
            with self.subTest(ham=ham), self.assertRaises(HTTPException) as ctx:
                getattr(module, ham)(4242, db=self.db, _=None)
            self.assertEqual(ctx.exception.status_code, 400)
            self.assertIn("4242", ctx.exception.detail)
        with self.assertRaises(HTTPException) as ctx:
            huong_di_tieu_chi.get_thcs_huong_di_tieu_chi(4242, 7, db=self.db, _=None)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("4242", ctx.exception.detail)

    def test_chuan_hoa_ma_va_tu_choi_trung(self):
        h = self._huong(ma_holland=" rie ")
        self.assertEqual((h.ma_huong, h.ma_holland, h.muc_do_ap_luc_hoc_tap), ("THPT_CONG_LAP", "RIE", "trung_binh"))
        with self.assertRaises(HTTPException) as ctx:
            huong_di.create_thcs_huong_di_bulk(
                [DmThcsHuongDiWrite(ma_huong="THPT_CONG_LAP", ten_huong="A", mo_ta_tong_quan="B")], db=self.db, _=None
            )
        self.assertIn("THPT_CONG_LAP", ctx.exception.detail)
        self._tieu_chi()
        with self.assertRaises(HTTPException) as ctx:
            tieu_chi.create_thcs_tieu_chi_bulk(
                [DmThcsTieuChiWrite(ma_tieu_chi="X", ten_tieu_chi="A"), DmThcsTieuChiWrite(ma_tieu_chi="x", ten_tieu_chi="B")],
                db=self.db, _=None,
            )
        self.assertIn("bị trùng", ctx.exception.detail)

    def test_gia_tri_khong_hop_le_bi_tu_choi(self):
        with self.assertRaises(ValueError):
            DmThcsHuongDiWrite(ma_huong="A", ten_huong="A", mo_ta_tong_quan="A", chi_phi_thang_min=5, chi_phi_thang_max=1)
        with self.assertRaises(ValueError):
            DmThcsHuongDiWrite(ma_huong="A", ten_huong="A", mo_ta_tong_quan="A", muc_do_ap_luc_hoc_tap="rat_cao")
        with self.assertRaises(ValueError):
            DmThcsHuongDiTieuChiWrite(thcs_huong_di_id=1, thcs_tieu_chi_id=1, diem_phu_hop=6)
        with self.assertRaises(ValueError):
            DmThcsUuNhuocDiemWrite(thcs_huong_di_id=1, loai="uu_diem", tieu_de="  ", noi_dung_chi_tiet="A")

    def test_bang_con_kiem_tra_huong_di_va_loc(self):
        h = self._huong()
        with self.assertRaises(HTTPException) as ctx:
            uu_nhuoc.create_thcs_uu_nhuoc_diem_bulk(
                [DmThcsUuNhuocDiemWrite(thcs_huong_di_id=77, loai="uu_diem", tieu_de="A", noi_dung_chi_tiet="B")],
                db=self.db, _=None,
            )
        self.assertIn("77", ctx.exception.detail)
        for loai, tieu_de in (("nhuoc_diem", "Áp lực thi"), ("uu_diem", "Lộ trình rõ")):
            item = uu_nhuoc.create_thcs_uu_nhuoc_diem(
                DmThcsUuNhuocDiemWrite(thcs_huong_di_id=h.id, loai=loai, tieu_de=tieu_de, noi_dung_chi_tiet="X"),
                db=self.db, _=None,
            )
        self.assertEqual(item.ten_huong, "THPT công lập")
        self.assertEqual([i.tieu_de for i in _ds_uu_nhuoc(self.db).items], ["Lộ trình rõ", "Áp lực thi"])
        self.assertEqual(_ds_uu_nhuoc(self.db, loai="nhuoc_diem").total, 1)
        lk = loi_khuyen.create_thcs_loi_khuyen_luu_y(
            DmThcsLoiKhuyenLuuYWrite(thcs_huong_di_id=h.id, noi_dung_luu_y="Ôn thi sớm"), db=self.db, _=None
        )
        self.assertEqual(lk.doi_tuong_nhan, "ca_hai")
        self.assertEqual(_ds_loi_khuyen(self.db, q="công lập").total, 1)
        self.assertEqual(_ds_loi_khuyen(self.db, doi_tuong_nhan="phu_huynh").total, 0)

    def test_diem_phu_hop_theo_khoa_ghep(self):
        h, tc = self._huong(), self._tieu_chi()
        self._tieu_chi("tai_chinh", "Tài chính gia đình", "Hoàn cảnh")
        diem = huong_di_tieu_chi.create_thcs_huong_di_tieu_chi(
            DmThcsHuongDiTieuChiWrite(thcs_huong_di_id=h.id, thcs_tieu_chi_id=tc.id), db=self.db, _=None
        )
        self.assertEqual((diem.diem_phu_hop, diem.ma_tieu_chi, diem.ma_huong), (3, "HOC_LUC", "THPT_CONG_LAP"))
        with self.assertRaises(HTTPException) as ctx:
            huong_di_tieu_chi.create_thcs_huong_di_tieu_chi_bulk(
                [DmThcsHuongDiTieuChiWrite(thcs_huong_di_id=h.id, thcs_tieu_chi_id=tc.id, diem_phu_hop=5)],
                db=self.db, _=None,
            )
        self.assertIn("đã có điểm", ctx.exception.detail)
        sua = huong_di_tieu_chi.update_thcs_huong_di_tieu_chi(
            h.id, tc.id, DmThcsHuongDiTieuChiUpdate(diem_phu_hop=5, nhan_dinh_tu_van=" Rất hợp "), db=self.db, _=None
        )
        self.assertEqual((sua.diem_phu_hop, sua.nhan_dinh_tu_van), (5, "Rất hợp"))
        self.assertEqual(tieu_chi.list_thcs_nhom_tieu_chi(db=self.db), ["Hoàn cảnh", "Năng lực"])
        kq = huong_di_tieu_chi.delete_thcs_huong_di_tieu_chi_many(
            DmThcsHuongDiTieuChiDeleteMany(items=[{"thcs_huong_di_id": h.id, "thcs_tieu_chi_id": tc.id},
                                                  {"thcs_huong_di_id": 9, "thcs_tieu_chi_id": 9}]),
            db=self.db, _=None,
        )
        self.assertEqual(kq.deleted, 1)

    def test_xoa_huong_di_xoa_theo_du_lieu_con(self):
        h, tc = self._huong(), self._tieu_chi()
        uu_nhuoc.create_thcs_uu_nhuoc_diem(
            DmThcsUuNhuocDiemWrite(thcs_huong_di_id=h.id, loai="uu_diem", tieu_de="A", noi_dung_chi_tiet="B"),
            db=self.db, _=None,
        )
        huong_di_tieu_chi.create_thcs_huong_di_tieu_chi(
            DmThcsHuongDiTieuChiWrite(thcs_huong_di_id=h.id, thcs_tieu_chi_id=tc.id), db=self.db, _=None
        )
        kq = huong_di.delete_thcs_huong_di_many(DmThcsDeleteMany(ids=[h.id, 999]), db=self.db, _=None)
        self.assertEqual(kq.deleted, 1)
        self.assertEqual((_ds_uu_nhuoc(self.db).total, _ds_diem(self.db).total, _ds_tieu_chi(self.db).total), (0, 0, 1))

    def test_xoa_nhieu_id_khong_ton_tai_tra_0(self):
        kq = loi_khuyen.delete_thcs_loi_khuyen_luu_y_many(DmThcsDeleteMany(ids=[5]), db=self.db, _=None)
        self.assertEqual(kq.deleted, 0)


if __name__ == "__main__":
    unittest.main()
