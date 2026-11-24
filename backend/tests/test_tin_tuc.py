"""Tin tức: nhóm tin và bài viết (quản trị)."""

import unittest

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine, event
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session

import app.models as M
from app.api.v1.endpoints import tin_tuc_bai_viet as bai, tin_tuc_cong_khai as cong_khai, tin_tuc_nhom_tin as nhom
from app.db.base import Base
from app.schemas.tin_tuc import (
    TinTucBaiVietDeleteMany,
    TinTucBaiVietHienThi,
    TinTucBaiVietWrite,
    TinTucNhomTinDeleteMany,
    TinTucNhomTinWrite,
    tao_slug,
)


@compiles(TINYINT, "sqlite")
def _so_nguyen_sqlite(type_, compiler, **kw):
    return "INTEGER"


def _ds_nhom(db, **kw):
    return nhom.list_nhom_tin(**{"q": None, "trang_thai": None, "page": 1, "page_size": 20, **kw}, db=db)


def _ds_bai(db, **kw):
    params = {"q": None, "nhom_tin_tuc_id": None, "trang_thai": None, "is_noi_bat": None, "page": 1, "page_size": 20}
    return bai.list_bai_viet(**{**params, **kw}, db=db)


class TestTinTuc(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite://")
        event.listen(engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
        Base.metadata.create_all(engine, tables=[M.TinTucNhomTin.__table__, M.TinTucBaiViet.__table__])
        self.db = Session(engine)

    def tearDown(self):
        self.db.close()

    def _tao_nhom(self, ma="huong_nghiep", ten="Hướng nghiệp", **kw):
        return nhom.create_nhom_tin(TinTucNhomTinWrite(ma_nhom=ma, ten_nhom=ten, **kw), db=self.db)

    def _tao_bai(self, nhom_id, tieu_de="Chọn ngành thế nào?", **kw):
        return bai.create_bai_viet(TinTucBaiVietWrite(nhom_tin_tuc_id=nhom_id, tieu_de=tieu_de, **kw), db=self.db)

    def test_tao_slug_tieng_viet(self):
        self.assertEqual(tao_slug("Đề án tuyển sinh 2026: Những điều cần biết!"), "de-an-tuyen-sinh-2026-nhung-dieu-can-biet")
        self.assertEqual(tao_slug("  ---  "), "")

    def test_danh_sach_rong_tra_dung_cau_truc(self):
        for page in (_ds_nhom(self.db), _ds_bai(self.db)):
            self.assertEqual((page.items, page.total, page.page, page.page_size), ([], 0, 1, 20))

    def test_id_khong_ton_tai_tra_400(self):
        for ham in (nhom.get_nhom_tin, bai.get_bai_viet, nhom.delete_nhom_tin, bai.delete_bai_viet):
            with self.subTest(ham=ham.__name__), self.assertRaises(HTTPException) as ctx:
                ham(99, db=self.db)
            self.assertEqual(ctx.exception.status_code, 400)
            self.assertIn("99", ctx.exception.detail)
        # Bài viết gắn nhóm tin không tồn tại.
        with self.assertRaises(HTTPException) as ctx:
            self._tao_bai(42)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("nhóm tin có id = 42", ctx.exception.detail)
        self.assertEqual(nhom.delete_nhom_tin_many(TinTucNhomTinDeleteMany(ids=[7]), db=self.db).deleted, 0)

    def test_nhom_tin_chuan_hoa_slug_va_tu_choi_trung(self):
        n = self._tao_nhom(ma=" tuyen_sinh ", ten="Tin tuyển sinh", mo_ta="  ")
        self.assertEqual((n.ma_nhom, n.slug, n.mo_ta, n.so_bai_viet), ("TUYEN_SINH", "tin-tuyen-sinh", None, 0))
        with self.assertRaises(HTTPException) as ctx:
            self._tao_nhom(ma="TUYEN_SINH", ten="Khác")
        self.assertIn("Mã nhóm", ctx.exception.detail)
        with self.assertRaises(HTTPException) as ctx:
            self._tao_nhom(ma="KHAC", ten="Khác", slug="Tin Tuyển Sinh")
        self.assertIn("Slug", ctx.exception.detail)
        # Sửa chính nó (giữ nguyên mã, slug) không bị coi là trùng.
        sua = nhom.update_nhom_tin(
            n.id, TinTucNhomTinWrite(ma_nhom="TUYEN_SINH", ten_nhom="Tuyển sinh", slug="tin-tuyen-sinh", thu_tu=2),
            db=self.db,
        )
        self.assertEqual((sua.ten_nhom, sua.thu_tu), ("Tuyển sinh", 2))

    def test_bai_viet_crud_va_loc(self):
        n1, n2 = self._tao_nhom(), self._tao_nhom(ma="KY_NANG", ten="Kỹ năng")
        b1 = self._tao_bai(n1.id, noi_dung="<p>Nội dung</p>", tac_gia="Ban biên tập", is_noi_bat=1)
        self._tao_bai(n2.id, tieu_de="Quản lý thời gian", trang_thai=0)
        self.assertEqual((b1.slug, b1.ten_nhom, b1.luot_xem), ("chon-nganh-the-nao", "Hướng nghiệp", 0))

        # Danh sách không kèm nội dung; lọc theo nhóm, trạng thái, nổi bật, từ khóa.
        ds = _ds_bai(self.db)
        self.assertEqual(ds.total, 2)
        self.assertNotIn("noi_dung", ds.items[0].model_dump())
        self.assertEqual([b.tieu_de for b in _ds_bai(self.db, nhom_tin_tuc_id=n2.id).items], ["Quản lý thời gian"])
        self.assertEqual([b.id for b in _ds_bai(self.db, trang_thai=1).items], [b1.id])
        self.assertEqual([b.id for b in _ds_bai(self.db, is_noi_bat=1).items], [b1.id])
        self.assertEqual([b.id for b in _ds_bai(self.db, q="biên tập").items], [b1.id])
        self.assertEqual(bai.get_bai_viet(b1.id, db=self.db).noi_dung, "<p>Nội dung</p>")

        with self.assertRaises(HTTPException) as ctx:
            self._tao_bai(n1.id, tieu_de="Chọn ngành thế nào")
        self.assertIn("Slug", ctx.exception.detail)

        an = bai.update_hien_thi_bai_viet(b1.id, TinTucBaiVietHienThi(trang_thai=0), db=self.db)
        self.assertEqual((an.trang_thai, an.is_noi_bat), (0, 1))
        with self.assertRaises(ValidationError):
            TinTucBaiVietHienThi()

        sua = bai.update_bai_viet(
            b1.id, TinTucBaiVietWrite(nhom_tin_tuc_id=n2.id, tieu_de="Chọn ngành", slug="chon-nganh"), db=self.db
        )
        self.assertEqual((sua.ten_nhom, sua.slug, sua.noi_dung), ("Kỹ năng", "chon-nganh", None))

    def test_khong_xoa_nhom_con_bai_viet(self):
        n = self._tao_nhom()
        b = self._tao_bai(n.id)
        self.assertEqual(_ds_nhom(self.db).items[0].so_bai_viet, 1)
        for xoa in (lambda: nhom.delete_nhom_tin(n.id, db=self.db),
                    lambda: nhom.delete_nhom_tin_many(TinTucNhomTinDeleteMany(ids=[n.id]), db=self.db)):
            with self.assertRaises(HTTPException) as ctx:
                xoa()
            self.assertIn("Hướng nghiệp (1 bài)", ctx.exception.detail)
        self.assertEqual(bai.delete_bai_viet_many(TinTucBaiVietDeleteMany(ids=[b.id, 999]), db=self.db).deleted, 1)
        nhom.delete_nhom_tin(n.id, db=self.db)
        self.assertEqual(_ds_nhom(self.db).total, 0)

    def test_cong_khai_chi_hien_bai_xuat_ban_thuoc_nhom_hien_thi(self):
        n1 = self._tao_nhom()
        n2 = self._tao_nhom(ma="AN", ten="Nhóm ẩn", trang_thai=0)
        b1 = self._tao_bai(n1.id, tieu_de="Bài một", is_noi_bat=1, noi_dung="<p>Một</p>")
        b2 = self._tao_bai(n1.id, tieu_de="Bài hai")
        self._tao_bai(n1.id, tieu_de="Bài nháp", trang_thai=0)
        self._tao_bai(n2.id, tieu_de="Bài trong nhóm ẩn")

        def ds(**kw):
            return cong_khai.list_bai_viet_cong_khai(
                **{"q": None, "nhom": None, "is_noi_bat": None, "page": 1, "page_size": 9, **kw}, db=self.db
            )

        self.assertEqual(sorted(b.tieu_de for b in ds().items), ["Bài hai", "Bài một"])
        self.assertEqual([b.id for b in ds(is_noi_bat=1).items], [b1.id])
        self.assertEqual([b.slug_nhom for b in ds(nhom="huong-nghiep").items], ["huong-nghiep", "huong-nghiep"])
        self.assertEqual(ds(nhom="nhom-an").total, 0)
        self.assertEqual([b.id for b in ds(q="hai").items], [b2.id])

        nhom_hien = cong_khai.list_nhom_tin_cong_khai(db=self.db)
        self.assertEqual([(n.slug, n.so_bai_viet) for n in nhom_hien], [("huong-nghiep", 2)])

        ct = cong_khai.get_bai_viet_cong_khai("bai-mot", db=self.db)
        self.assertEqual((ct.noi_dung, ct.luot_xem, ct.ten_nhom), ("<p>Một</p>", 1, "Hướng nghiệp"))
        self.assertEqual([b.id for b in ct.bai_lien_quan], [b2.id])
        self.assertEqual(cong_khai.get_bai_viet_cong_khai("bai-mot", db=self.db).luot_xem, 2)
        for slug in ("bai-nhap", "bai-trong-nhom-an", "khong-co"):
            with self.subTest(slug=slug), self.assertRaises(HTTPException) as ctx:
                cong_khai.get_bai_viet_cong_khai(slug, db=self.db)
            self.assertEqual(ctx.exception.status_code, 400)
            self.assertIn(slug, ctx.exception.detail)

    def test_cong_khai_rong_tra_dung_cau_truc(self):
        self.assertEqual(cong_khai.list_nhom_tin_cong_khai(db=self.db), [])
        page = cong_khai.list_bai_viet_cong_khai(q=None, nhom=None, is_noi_bat=None, page=1, page_size=9, db=self.db)
        self.assertEqual((page.items, page.total, page.page, page.page_size), ([], 0, 1, 9))


if __name__ == "__main__":
    unittest.main()
