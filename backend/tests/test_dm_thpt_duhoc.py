"""Danh mục du học THPT: hướng đi, quốc gia, ngành, chi phí, thủ tục, kênh kết nối."""

import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine, event
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session

import app.models as M
from app.api.v1.endpoints import (
    dm_thpt_duhoc_chi_phi as chi_phi,
    dm_thpt_duhoc_huong_di as huong_di,
    dm_thpt_duhoc_kenh_ket_noi as kenh,
    dm_thpt_duhoc_nganh as nganh,
    dm_thpt_duhoc_quoc_gia as quoc_gia,
    dm_thpt_duhoc_thu_tuc as thu_tuc,
)
from app.db.base import Base
from app.schemas.dm_thpt_duhoc import (
    DmThptDuhocChiPhiWrite,
    DmThptDuhocDeleteMany,
    DmThptDuhocHuongDiWrite,
    DmThptDuhocNganhWrite,
    DmThptDuhocQuocGiaWrite,
    DmThptDuhocThuTucWrite,
)


@compiles(TINYINT, "sqlite")
def _so_nguyen_sqlite(type_, compiler, **kw):
    return "INTEGER"


_BANG = [
    M.DmThptDuhocHuongDi, M.DmThptDuhocQuocGia, M.DmThptDuhocNganh, M.DmThptDuhocChiPhi, M.DmThptDuhocThuTuc,
    M.DmThptDuhocKenhKetNoi,
]
_LOC_CON = {"q": None, "thpt_duhoc_huong_di_id": None, "thpt_duhoc_quoc_gia_id": None, "page": 1, "page_size": 10}


def _ds_huong(db, **kw):
    return huong_di.list_thpt_duhoc_huong_di(
        **{"q": None, "trang_thai": None, "loai_hinh": None, "page": 1, "page_size": 10, **kw}, db=db
    )


def _ds_quoc_gia(db, **kw):
    return quoc_gia.list_thpt_duhoc_quoc_gia(
        **{"q": None, "thpt_duhoc_huong_di_id": None, "page": 1, "page_size": 10, **kw}, db=db
    )


def _ds_nganh(db, **kw):
    return nganh.list_thpt_duhoc_nganh(**{**_LOC_CON, **kw}, db=db)


def _ds_chi_phi(db, **kw):
    return chi_phi.list_thpt_duhoc_chi_phi(**{**_LOC_CON, "loai_chi_phi": None, **kw}, db=db)


def _ds_thu_tuc(db, **kw):
    return thu_tuc.list_thpt_duhoc_thu_tuc(**{**_LOC_CON, **kw}, db=db)


def _ds_kenh(db, **kw):
    return kenh.list_thpt_duhoc_kenh_ket_noi(**{**_LOC_CON, "loai_kenh": None, **kw}, db=db)


class TestDmThptDuhoc(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite://")
        event.listen(engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
        Base.metadata.create_all(engine, tables=[m.__table__ for m in _BANG])
        self.db = Session(engine)

    def tearDown(self):
        self.db.close()

    def _huong(self, ma="du_hoc_nghe", ten="Du học nghề"):
        return huong_di.create_thpt_duhoc_huong_di(
            DmThptDuhocHuongDiWrite(ma_huong=f" {ma} ", ten_huong=ten, loai_hinh="du_hoc_nghe", mo_ta_dac_diem="X"),
            db=self.db, _=None,
        )

    def _quoc_gia(self, huong_id, ma="de", ten="Đức"):
        return quoc_gia.create_thpt_duhoc_quoc_gia(
            DmThptDuhocQuocGiaWrite(thpt_duhoc_huong_di_id=huong_id, ma_quoc_gia=ma, ten_quoc_gia=ten),
            db=self.db, _=None,
        )

    def test_danh_sach_rong_tra_dung_cau_truc(self):
        for ds in (_ds_huong, _ds_quoc_gia, _ds_nganh, _ds_chi_phi, _ds_thu_tuc, _ds_kenh):
            with self.subTest(ds=ds.__name__):
                page = ds(self.db)
                self.assertEqual((page.items, page.total, page.page, page.page_size), ([], 0, 1, 10))

    def test_id_khong_ton_tai_tra_400(self):
        for module, ham in ((huong_di, "get_thpt_duhoc_huong_di"), (quoc_gia, "get_thpt_duhoc_quoc_gia"),
                            (nganh, "get_thpt_duhoc_nganh"), (kenh, "get_thpt_duhoc_kenh_ket_noi")):
            with self.subTest(ham=ham), self.assertRaises(HTTPException) as ctx:
                getattr(module, ham)(4242, db=self.db, _=None)
            self.assertEqual(ctx.exception.status_code, 400)
            self.assertIn("4242", ctx.exception.detail)

    def test_chuan_hoa_ma_va_tu_choi_trung(self):
        self.assertEqual(self._huong().ma_huong, "DU_HOC_NGHE")
        with self.assertRaises(HTTPException) as ctx:
            huong_di.create_thpt_duhoc_huong_di_bulk(
                [DmThptDuhocHuongDiWrite(ma_huong="DU_HOC_NGHE", ten_huong="A", loai_hinh="chuyen_tiep",
                                         mo_ta_dac_diem="B")],
                db=self.db, _=None,
            )
        self.assertIn("DU_HOC_NGHE", ctx.exception.detail)

    def test_khoang_nguoc_bi_tu_choi(self):
        with self.assertRaises(ValueError):
            DmThptDuhocChiPhiWrite(thpt_duhoc_huong_di_id=1, loai_chi_phi="truoc_khi_bay", ten_khoan_chi="A",
                                   chi_phi_min=10, chi_phi_max=5)
        with self.assertRaises(ValueError):
            DmThptDuhocHuongDiWrite(ma_huong="A", ten_huong="A", loai_hinh="chuyen_tiep", mo_ta_dac_diem="A",
                                    thoi_gian_chuan_bi_thang_min=12, thoi_gian_chuan_bi_thang_max=3)

    def test_quoc_gia_phai_thuoc_huong_di(self):
        h1, h2 = self._huong(), self._huong("DU_HOC_DH", "Du học đại học")
        qg = self._quoc_gia(h1.id)
        self.assertEqual((qg.ma_quoc_gia, qg.ten_huong), ("DE", "Du học nghề"))
        with self.assertRaises(HTTPException) as ctx:
            nganh.create_thpt_duhoc_nganh(
                DmThptDuhocNganhWrite(thpt_duhoc_huong_di_id=h2.id, thpt_duhoc_quoc_gia_id=qg.id, ten_nganh="CNTT"),
                db=self.db, _=None,
            )
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("không thuộc hướng đi", ctx.exception.detail)
        with self.assertRaises(HTTPException) as ctx:
            thu_tuc.create_thpt_duhoc_thu_tuc_bulk(
                [DmThptDuhocThuTucWrite(thpt_duhoc_huong_di_id=h1.id, thpt_duhoc_quoc_gia_id=77, buoc_so=1,
                                        ten_buoc="A", mo_ta_thu_tuc="B")],
                db=self.db, _=None,
            )
        self.assertIn("77", ctx.exception.detail)

    def test_dong_chung_xep_truoc_va_ghep_ten(self):
        h = self._huong()
        qg = self._quoc_gia(h.id)
        for qg_id, ten in ((qg.id, "Điều dưỡng"), (None, "CNTT ứng dụng")):
            nganh.create_thpt_duhoc_nganh(
                DmThptDuhocNganhWrite(thpt_duhoc_huong_di_id=h.id, thpt_duhoc_quoc_gia_id=qg_id, ten_nganh=ten),
                db=self.db, _=None,
            )
        items = _ds_nganh(self.db).items
        self.assertEqual([(i.ten_nganh, i.ten_quoc_gia) for i in items],
                         [("CNTT ứng dụng", None), ("Điều dưỡng", "Đức")])
        self.assertEqual(_ds_nganh(self.db, q="Đức").total, 1)
        self.assertEqual(_ds_nganh(self.db, thpt_duhoc_quoc_gia_id=qg.id).total, 1)

    def test_khong_doi_huong_di_khi_quoc_gia_co_du_lieu_con(self):
        h1, h2 = self._huong(), self._huong("DU_HOC_DH", "Du học đại học")
        qg = self._quoc_gia(h1.id)
        payload = DmThptDuhocQuocGiaWrite(thpt_duhoc_huong_di_id=h2.id, ma_quoc_gia="DE", ten_quoc_gia="Đức")
        self.assertEqual(quoc_gia.update_thpt_duhoc_quoc_gia(qg.id, payload, db=self.db, _=None).ten_huong,
                         "Du học đại học")
        chi_phi.create_thpt_duhoc_chi_phi(
            DmThptDuhocChiPhiWrite(thpt_duhoc_huong_di_id=h2.id, thpt_duhoc_quoc_gia_id=qg.id,
                                   loai_chi_phi="tai_nuoc_so_tai", ten_khoan_chi="Học phí", don_vi_tien="eur"),
            db=self.db, _=None,
        )
        payload.thpt_duhoc_huong_di_id = h1.id
        with self.assertRaises(HTTPException) as ctx:
            quoc_gia.update_thpt_duhoc_quoc_gia(qg.id, payload, db=self.db, _=None)
        self.assertIn("không thể chuyển", ctx.exception.detail)
        self.assertEqual(_ds_chi_phi(self.db).items[0].don_vi_tien, "EUR")

    def test_xoa_huong_di_xoa_theo_du_lieu_con(self):
        h = self._huong()
        qg = self._quoc_gia(h.id)
        nganh.create_thpt_duhoc_nganh(
            DmThptDuhocNganhWrite(thpt_duhoc_huong_di_id=h.id, thpt_duhoc_quoc_gia_id=qg.id, ten_nganh="A"),
            db=self.db, _=None,
        )
        kq = huong_di.delete_thpt_duhoc_huong_di_many(DmThptDuhocDeleteMany(ids=[h.id, 999]), db=self.db, _=None)
        self.assertEqual(kq.deleted, 1)
        self.assertEqual((_ds_quoc_gia(self.db).total, _ds_nganh(self.db).total), (0, 0))

    def test_xoa_nhieu_id_khong_ton_tai_tra_0(self):
        kq = kenh.delete_thpt_duhoc_kenh_ket_noi_many(DmThptDuhocDeleteMany(ids=[5]), db=self.db, _=None)
        self.assertEqual(kq.deleted, 0)


if __name__ == "__main__":
    unittest.main()
