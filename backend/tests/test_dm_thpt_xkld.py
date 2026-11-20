"""Danh mục xuất khẩu lao động THPT: nhóm nghề, thị trường, nghề cụ thể, chi phí, thủ tục, kênh kết nối."""

import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine, event
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session

import app.models as M
from app.api.v1.endpoints import (
    dm_thpt_xkld_chi_phi as chi_phi,
    dm_thpt_xkld_nhom_nghe as nhom_nghe,
    dm_thpt_xkld_kenh_ket_noi as kenh,
    dm_thpt_xkld_nghe_cu_the as nghe,
    dm_thpt_xkld_thi_truong as thi_truong,
    dm_thpt_xkld_thu_tuc as thu_tuc,
)
from app.db.base import Base
from app.schemas.dm_thpt_xkld import (
    DmThptXkldChiPhiWrite,
    DmThptXkldDeleteMany,
    DmThptXkldNhomNgheWrite,
    DmThptXkldNgheCuTheWrite,
    DmThptXkldThiTruongWrite,
    DmThptXkldThuTucWrite,
)


@compiles(TINYINT, "sqlite")
def _so_nguyen_sqlite(type_, compiler, **kw):
    return "INTEGER"


_BANG = [
    M.DmThptXkldNhomNghe, M.DmThptXkldThiTruong, M.DmThptXkldNgheCuThe, M.DmThptXkldChiPhi, M.DmThptXkldThuTuc,
    M.DmThptXkldKenhKetNoi,
]
_LOC_CON = {"q": None, "thpt_xkld_nhom_nghe_id": None, "thpt_xkld_thi_truong_id": None, "page": 1, "page_size": 10}


def _ds_nhom(db, **kw):
    return nhom_nghe.list_thpt_xkld_nhom_nghe(
        **{"q": None, "trang_thai": None, "page": 1, "page_size": 10, **kw}, db=db
    )


def _ds_thi_truong(db, **kw):
    return thi_truong.list_thpt_xkld_thi_truong(
        **{"q": None, "thpt_xkld_nhom_nghe_id": None, "page": 1, "page_size": 10, **kw}, db=db
    )


def _ds_nghe(db, **kw):
    return nghe.list_thpt_xkld_nghe_cu_the(**{**_LOC_CON, "yeu_cau_gioi_tinh": None, **kw}, db=db)


def _ds_chi_phi(db, **kw):
    return chi_phi.list_thpt_xkld_chi_phi(**{**_LOC_CON, "loai_chi_phi": None, **kw}, db=db)


def _ds_thu_tuc(db, **kw):
    return thu_tuc.list_thpt_xkld_thu_tuc(**{**_LOC_CON, **kw}, db=db)


def _ds_kenh(db, **kw):
    return kenh.list_thpt_xkld_kenh_ket_noi(**{**_LOC_CON, "loai_kenh": None, **kw}, db=db)


class TestDmThptXkld(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite://")
        event.listen(engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
        Base.metadata.create_all(engine, tables=[m.__table__ for m in _BANG])
        self.db = Session(engine)

    def tearDown(self):
        self.db.close()

    def _nhom(self, ma="co_khi", ten="Cơ khí"):
        return nhom_nghe.create_thpt_xkld_nhom_nghe(
            DmThptXkldNhomNgheWrite(ma_nhom=f" {ma} ", ten_nhom=ten, mo_ta_cong_viec="X"),
            db=self.db, _=None,
        )

    def _thi_truong(self, nhom_id, ma="jp", ten="Nhật Bản"):
        return thi_truong.create_thpt_xkld_thi_truong(
            DmThptXkldThiTruongWrite(thpt_xkld_nhom_nghe_id=nhom_id, ma_quoc_gia=ma, ten_quoc_gia=ten),
            db=self.db, _=None,
        )

    def test_danh_sach_rong_tra_dung_cau_truc(self):
        for ds in (_ds_nhom, _ds_thi_truong, _ds_nghe, _ds_chi_phi, _ds_thu_tuc, _ds_kenh):
            with self.subTest(ds=ds.__name__):
                page = ds(self.db)
                self.assertEqual((page.items, page.total, page.page, page.page_size), ([], 0, 1, 10))

    def test_id_khong_ton_tai_tra_400(self):
        for module, ham in ((nhom_nghe, "get_thpt_xkld_nhom_nghe"), (thi_truong, "get_thpt_xkld_thi_truong"),
                            (nghe, "get_thpt_xkld_nghe_cu_the"), (kenh, "get_thpt_xkld_kenh_ket_noi")):
            with self.subTest(ham=ham), self.assertRaises(HTTPException) as ctx:
                getattr(module, ham)(4242, db=self.db, _=None)
            self.assertEqual(ctx.exception.status_code, 400)
            self.assertIn("4242", ctx.exception.detail)

    def test_chuan_hoa_ma_va_tu_choi_trung(self):
        self.assertEqual(self._nhom().ma_nhom, "CO_KHI")
        with self.assertRaises(HTTPException) as ctx:
            nhom_nghe.create_thpt_xkld_nhom_nghe_bulk(
                [DmThptXkldNhomNgheWrite(ma_nhom="CO_KHI", ten_nhom="A", mo_ta_cong_viec="B")],
                db=self.db, _=None,
            )
        self.assertIn("CO_KHI", ctx.exception.detail)

    def test_khoang_nguoc_bi_tu_choi(self):
        with self.assertRaises(ValueError):
            DmThptXkldChiPhiWrite(thpt_xkld_nhom_nghe_id=1, loai_chi_phi="phi_dich_vu_xuat_canh", ten_khoan_chi="A",
                                   chi_phi_min=10, chi_phi_max=5)
        with self.assertRaises(ValueError):
            DmThptXkldNhomNgheWrite(ma_nhom="A", ten_nhom="A", mo_ta_cong_viec="A",
                                    thoi_gian_chuan_bi_thang_min=12, thoi_gian_chuan_bi_thang_max=3)

    def test_thu_nhap_nguoc_va_gioi_tinh(self):
        with self.assertRaises(ValueError):
            DmThptXkldNhomNgheWrite(ma_nhom="A", ten_nhom="A", mo_ta_cong_viec="A", thu_nhap_thang_min=40,
                                    thu_nhap_thang_max=30)
        h = self._nhom()
        for ten, gioi in (("Hàn", "nam"), ("May", None)):
            payload = {"yeu_cau_gioi_tinh": gioi} if gioi else {}
            nghe.create_thpt_xkld_nghe_cu_the(
                DmThptXkldNgheCuTheWrite(thpt_xkld_nhom_nghe_id=h.id, ten_cong_viec=ten, **payload),
                db=self.db, _=None,
            )
        self.assertEqual(_ds_nghe(self.db, yeu_cau_gioi_tinh="ca_hai").items[0].ten_cong_viec, "May")
        self.assertEqual(_ds_nghe(self.db, yeu_cau_gioi_tinh="nam").total, 1)

    def test_thi_truong_phai_thuoc_nhom_nghe(self):
        h1, h2 = self._nhom(), self._nhom("NONG_NGHIEP", "Nông nghiệp")
        tt = self._thi_truong(h1.id)
        self.assertEqual((tt.ma_quoc_gia, tt.ten_nhom), ("JP", "Cơ khí"))
        with self.assertRaises(HTTPException) as ctx:
            nghe.create_thpt_xkld_nghe_cu_the(
                DmThptXkldNgheCuTheWrite(thpt_xkld_nhom_nghe_id=h2.id, thpt_xkld_thi_truong_id=tt.id, ten_cong_viec="Hàn"),
                db=self.db, _=None,
            )
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("không thuộc nhóm nghề", ctx.exception.detail)
        with self.assertRaises(HTTPException) as ctx:
            thu_tuc.create_thpt_xkld_thu_tuc_bulk(
                [DmThptXkldThuTucWrite(thpt_xkld_nhom_nghe_id=h1.id, thpt_xkld_thi_truong_id=77, buoc_so=1,
                                        ten_buoc="A", mo_ta_thu_tuc="B")],
                db=self.db, _=None,
            )
        self.assertIn("77", ctx.exception.detail)

    def test_dong_chung_xep_truoc_va_ghep_ten(self):
        h = self._nhom()
        tt = self._thi_truong(h.id)
        for tt_id, ten in ((tt.id, "Hàn"), (None, "Tiện CNC")):
            nghe.create_thpt_xkld_nghe_cu_the(
                DmThptXkldNgheCuTheWrite(thpt_xkld_nhom_nghe_id=h.id, thpt_xkld_thi_truong_id=tt_id, ten_cong_viec=ten),
                db=self.db, _=None,
            )
        items = _ds_nghe(self.db).items
        self.assertEqual([(i.ten_cong_viec, i.ten_quoc_gia) for i in items],
                         [("Tiện CNC", None), ("Hàn", "Nhật Bản")])
        self.assertEqual(_ds_nghe(self.db, q="Nhật").total, 1)
        self.assertEqual(_ds_nghe(self.db, thpt_xkld_thi_truong_id=tt.id).total, 1)

    def test_khong_doi_nhom_nghe_khi_thi_truong_co_du_lieu_con(self):
        h1, h2 = self._nhom(), self._nhom("NONG_NGHIEP", "Nông nghiệp")
        tt = self._thi_truong(h1.id)
        payload = DmThptXkldThiTruongWrite(thpt_xkld_nhom_nghe_id=h2.id, ma_quoc_gia="JP", ten_quoc_gia="Nhật Bản")
        self.assertEqual(thi_truong.update_thpt_xkld_thi_truong(tt.id, payload, db=self.db, _=None).ten_nhom,
                         "Nông nghiệp")
        chi_phi.create_thpt_xkld_chi_phi(
            DmThptXkldChiPhiWrite(thpt_xkld_nhom_nghe_id=h2.id, thpt_xkld_thi_truong_id=tt.id,
                                   loai_chi_phi="dao_tao_tieng_tay_nghe", ten_khoan_chi="Học tiếng", don_vi_tien="jpy"),
            db=self.db, _=None,
        )
        payload.thpt_xkld_nhom_nghe_id = h1.id
        with self.assertRaises(HTTPException) as ctx:
            thi_truong.update_thpt_xkld_thi_truong(tt.id, payload, db=self.db, _=None)
        self.assertIn("không thể chuyển", ctx.exception.detail)
        self.assertEqual(_ds_chi_phi(self.db).items[0].don_vi_tien, "JPY")

    def test_xoa_nhom_nghe_xoa_theo_du_lieu_con(self):
        h = self._nhom()
        tt = self._thi_truong(h.id)
        nghe.create_thpt_xkld_nghe_cu_the(
            DmThptXkldNgheCuTheWrite(thpt_xkld_nhom_nghe_id=h.id, thpt_xkld_thi_truong_id=tt.id, ten_cong_viec="A"),
            db=self.db, _=None,
        )
        kq = nhom_nghe.delete_thpt_xkld_nhom_nghe_many(DmThptXkldDeleteMany(ids=[h.id, 999]), db=self.db, _=None)
        self.assertEqual(kq.deleted, 1)
        self.assertEqual((_ds_thi_truong(self.db).total, _ds_nghe(self.db).total), (0, 0))

    def test_xoa_nhieu_id_khong_ton_tai_tra_0(self):
        kq = kenh.delete_thpt_xkld_kenh_ket_noi_many(DmThptXkldDeleteMany(ids=[5]), db=self.db, _=None)
        self.assertEqual(kq.deleted, 0)


if __name__ == "__main__":
    unittest.main()
