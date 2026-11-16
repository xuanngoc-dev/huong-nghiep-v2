import json
import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine, func, select
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session

from app.api.v1.endpoints.dats_tuyen_sinh import sao_chep_de_an_sang_nam
from app.models.dats_chuong_trinh_dao_tao import DatsChuongTrinhDaoTao
from app.models.dats_dieu_kien_du_tuyen import DatsDieuKienDuTuyen
from app.models.dats_phuong_thuc import DatsPhuongThuc
from app.models.dats_phuong_thuc_to_hop import DatsPhuongThucToHop
from app.models.dats_tru_so import DatsTruSo
from app.models.dats_tuyen_sinh import DatsTuyenSinh
from app.models.dm_truong import DmTruong
from app.schemas.dats_tuyen_sinh import DatsSaoChepRequest
from app.services.dats_import import _TABLES, _apply, prepare_import
from app.services.sao_chep_de_an import ten_de_an_nam_moi
from tests.test_dats_import import NESTED, catalogs


@compiles(BIGINT, "sqlite")
def _bigint_sqlite(type_, compiler, **kw):
    # SQLite chỉ tự tăng khóa chính kiểu INTEGER.
    return "INTEGER"


class SaoChepDeAnTests(unittest.TestCase):
    """Bước 1.5: đề án BKA 2026 (file mẫu rút gọn, nhập bằng bộ import) sao chép sang 2027."""

    def setUp(self):
        engine = create_engine("sqlite://")
        DmTruong.__table__.create(engine)
        for _table, model, _kind in _TABLES:
            model.__table__.create(engine)
        self.db = Session(engine)
        self.db.add(DmTruong(ma_truong="BKA", ten_truong="Bách khoa"))
        self.db.flush()
        rows = prepare_import(
            json.loads(NESTED.read_text()), ma_truong="BKA", nam_tuyen_sinh=2026, catalogs=catalogs()
        )
        self.goc_id, self.so_dong_goc = _apply(self.db, rows)
        goc = self.db.get(DatsTuyenSinh, self.goc_id)
        goc.ten_de_an = "Thông tin tuyển sinh năm 2026"
        # Cơ sở để kiểm tra khóa co_so_id của chương trình được nối sang cơ sở mới.
        co_so = DatsTruSo(de_an_id=self.goc_id, ten_co_so="Trụ sở chính")
        self.db.add(co_so)
        self.db.flush()
        for ct in self.db.scalars(select(DatsChuongTrinhDaoTao)):
            ct.co_so_id = co_so.id
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def _sao_chep(self, nam=2027, ten=None, de_an_id=None):
        return sao_chep_de_an_sang_nam(
            de_an_id or self.goc_id, DatsSaoChepRequest(nam_tuyen_sinh=nam, ten_de_an=ten), self.db, None
        )

    def _dem(self, model, de_an_id):
        cols = model.__table__.c
        if "de_an_id" in cols:
            return self.db.scalar(select(func.count()).select_from(model).where(cols.de_an_id == de_an_id))
        ct_ids = select(DatsChuongTrinhDaoTao.id).where(DatsChuongTrinhDaoTao.de_an_id == de_an_id)
        if "de_an_chuong_trinh_id" in cols:
            return self.db.scalar(
                select(func.count()).select_from(model).where(cols.de_an_chuong_trinh_id.in_(ct_ids))
            )
        pt_ids = select(DatsPhuongThuc.id).where(DatsPhuongThuc.de_an_chuong_trinh_id.in_(ct_ids))
        return self.db.scalar(select(func.count()).select_from(model).where(cols.de_an_phuong_thuc_id.in_(pt_ids)))

    def test_chep_du_moi_bang_con(self):
        ket_qua = self._sao_chep()
        moi_id = ket_qua.de_an.id
        self.assertNotEqual(moi_id, self.goc_id)
        for table, model, _kind in _TABLES:
            if table == "dats_tuyen_sinh":
                continue
            with self.subTest(table=table):
                goc = self._dem(model, self.goc_id)
                self.assertEqual(self._dem(model, moi_id), goc)
                self.assertEqual(ket_qua.counts.get(table, 0), goc)
        self.assertEqual(ket_qua.counts["dats_chuong_trinh_dao_tao"], 4)

    def test_de_an_moi_tro_ve_nam_truoc_va_doi_ten(self):
        de_an = self._sao_chep().de_an
        self.assertEqual((de_an.nam_tuyen_sinh, de_an.de_an_nam_truoc_id), (2027, self.goc_id))
        self.assertEqual(de_an.ten_de_an, "Thông tin tuyển sinh năm 2027")
        self.assertEqual(de_an.trang_thai_xet_tuyen, 0)
        self.assertIsNone(de_an.ngay_cong_bo)
        self.assertEqual(self._sao_chep(nam=2028, ten="Đề án tự đặt").de_an.ten_de_an, "Đề án tự đặt")

    def test_khoa_ngoai_noi_sang_ban_ghi_moi(self):
        moi_id = self._sao_chep().de_an.id
        co_so_moi = self.db.scalar(select(DatsTruSo.id).where(DatsTruSo.de_an_id == moi_id))
        chuong_trinh = list(self.db.scalars(select(DatsChuongTrinhDaoTao).where(DatsChuongTrinhDaoTao.de_an_id == moi_id)))
        self.assertTrue(all(ct.co_so_id == co_so_moi for ct in chuong_trinh))
        self.assertEqual(
            sorted(ct.ma_xet_tuyen_nam_truoc for ct in chuong_trinh), sorted(ct.ma_xet_tuyen for ct in chuong_trinh)
        )
        ct_ids = {ct.id for ct in chuong_trinh}
        phuong_thuc = list(self.db.scalars(select(DatsPhuongThuc).where(DatsPhuongThuc.de_an_chuong_trinh_id.in_(ct_ids))))
        self.assertEqual(len(phuong_thuc), 20)
        pt_ids = {pt.id for pt in phuong_thuc}
        to_hop = list(self.db.scalars(select(DatsPhuongThucToHop).where(DatsPhuongThucToHop.de_an_phuong_thuc_id.in_(pt_ids))))
        self.assertEqual(len(to_hop), 14)
        # Điều kiện của đề án mới chỉ trỏ tới đối tượng / chương trình của đề án mới.
        dieu_kien = list(self.db.scalars(select(DatsDieuKienDuTuyen).where(DatsDieuKienDuTuyen.de_an_id == moi_id)))
        doi_tuong_goc = set(
            self.db.scalars(select(DatsDieuKienDuTuyen.doi_tuong_du_tuyen_id).where(DatsDieuKienDuTuyen.de_an_id == self.goc_id))
        )
        for dk in dieu_kien:
            self.assertNotIn(dk.doi_tuong_du_tuyen_id, doi_tuong_goc - {None})
            if dk.de_an_chuong_trinh_id is not None:
                self.assertIn(dk.de_an_chuong_trinh_id, ct_ids)

    def test_de_an_goc_giu_nguyen(self):
        self._sao_chep()
        self.assertEqual(self._dem(DatsChuongTrinhDaoTao, self.goc_id), 4)
        goc = self.db.get(DatsTuyenSinh, self.goc_id)
        self.assertEqual((goc.nam_tuyen_sinh, goc.ten_de_an), (2026, "Thông tin tuyển sinh năm 2026"))

    def test_tu_choi_trung_nam_cung_nam_va_khong_ton_tai(self):
        self._sao_chep()
        for kwargs, thong_bao in (
            ({"nam": 2027}, "đã có đề án tuyển sinh năm 2027"),
            ({"nam": 2026}, "phải khác năm"),
            ({"de_an_id": 999}, "id = 999"),
        ):
            with self.subTest(**kwargs), self.assertRaises(HTTPException) as caught:
                self._sao_chep(**kwargs)
            self.assertEqual(caught.exception.status_code, 400)
            self.assertIn(thong_bao, caught.exception.detail)

    def test_doi_nam_trong_ten(self):
        self.assertEqual(ten_de_an_nam_moi("Đề án 2026 - BKA", 2026, 2027), "Đề án 2027 - BKA")
        self.assertEqual(ten_de_an_nam_moi("Đề án BKA", 2026, 2027), "Đề án BKA")
        self.assertIsNone(ten_de_an_nam_moi(None, 2026, 2027))


if __name__ == "__main__":
    unittest.main()
