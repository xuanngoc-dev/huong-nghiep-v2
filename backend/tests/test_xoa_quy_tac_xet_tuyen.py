import json
import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine, func, select
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT, TINYINT
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session

import app.models  # noqa: F401  # nạp toàn bộ model vào metadata
from app.api.v1.endpoints.dats_chuong_trinh_dao_tao import delete_chuong_trinh, delete_chuong_trinh_many, update_chuong_trinh
from app.api.v1.endpoints.dats_tuyen_sinh import delete_de_an
from app.db.base import Base
from app.models.dats_chuong_trinh_dao_tao import DatsChuongTrinhDaoTao
from app.models.dats_hoc_phi import DatsHocPhi
from app.models.dm_nganh_dao_tao import DmNganhDaoTao
from app.models.dm_truong import DmTruong
from app.models.xt_bang_quy_doi import XtBangQuyDoi, XtBangQuyDoiChiTiet
from app.models.xt_cong_thuc import XtCongThuc, XtCongThucHeSoMon, XtCongThucThanhPhan
from app.models.xt_dieu_kien import XtDiemCong, XtDieuKien, XtNhomDieuKien
from app.models.xt_lich_su_import import XtLichSuImport
from app.models.xt_phuong_an import XtPhuongAn
from app.schemas.dats_chuong_trinh_dao_tao import DatsChuongTrinhDaoTaoDeleteMany, DatsChuongTrinhDaoTaoWrite
from app.services.dats_import import _TABLES, _apply, prepare_import
from app.services.xt_quy_tac import delete_quy_tac_xet_tuyen
from tests.test_dats_import import NESTED, catalogs


@compiles(BIGINT, "sqlite")
@compiles(TINYINT, "sqlite")
@compiles(SMALLINT, "sqlite")
def _so_nguyen_sqlite(type_, compiler, **kw):
    # SQLite chỉ tự tăng khóa chính kiểu INTEGER.
    return "INTEGER"


_BANG_QUY_TAC = [
    XtBangQuyDoi,
    XtBangQuyDoiChiTiet,
    XtCongThuc,
    XtCongThucHeSoMon,
    XtCongThucThanhPhan,
    XtPhuongAn,
    XtNhomDieuKien,
    XtDieuKien,
    XtDiemCong,
    DatsHocPhi,
    XtLichSuImport,
]


class XoaQuyTacXetTuyenTests(unittest.TestCase):
    """Bước 2.2: xóa đề án dọn cả quy tắc xt_* và học phí; chương trình đang có quy tắc thì không xóa / chuyển được."""

    def setUp(self):
        engine = create_engine("sqlite://")
        bang = [DmTruong.__table__, DmNganhDaoTao.__table__, *(model.__table__ for _ten, model, _kind in _TABLES)]
        Base.metadata.create_all(engine, tables=bang + [model.__table__ for model in _BANG_QUY_TAC])
        self.db = Session(engine)
        self.db.add(DmTruong(ma_truong="BKA", ten_truong="Bách khoa"))
        self.db.flush()
        self.de_an = [self._nhap_de_an(2026), self._nhap_de_an(2027)]
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def _nhap_de_an(self, nam: int) -> int:
        rows = prepare_import(json.loads(NESTED.read_text()), ma_truong="BKA", nam_tuyen_sinh=nam, catalogs=catalogs())
        de_an_id, _counts = _apply(self.db, rows)
        ct = self.db.scalars(
            select(DatsChuongTrinhDaoTao).where(DatsChuongTrinhDaoTao.de_an_id == de_an_id).order_by(DatsChuongTrinhDaoTao.id)
        ).first()
        bang = XtBangQuyDoi(de_an_id=de_an_id, ma_bang="IELTS", ten_bang="IELTS", thang_diem_dich=10)
        self.db.add(bang)
        self.db.flush()
        cong_thuc = XtCongThuc(
            de_an_id=de_an_id,
            ma_cong_thuc="THPT",
            ten_cong_thuc="Điểm thi THPT",
            ma_phuong_thuc_cua_bo="100",
            kieu_tinh="TO_HOP_MON",
            bang_quy_doi_ngoai_ngu_id=bang.id,
        )
        nhom = XtNhomDieuKien(de_an_id=de_an_id, de_an_chuong_trinh_id=ct.id, ma_nhom="TN", ten_nhom="Tốt nghiệp")
        self.db.add_all([cong_thuc, nhom])
        self.db.flush()
        self.db.add_all(
            [
                XtBangQuyDoiChiTiet(bang_quy_doi_id=bang.id, diem_quy_doi=8),
                XtCongThucHeSoMon(cong_thuc_id=cong_thuc.id, nhom_mon="Ngoại ngữ", he_so=2),
                XtCongThucThanhPhan(cong_thuc_id=cong_thuc.id, vi_tri=1, loai_nguon="CHUNG_CHI", bang_quy_doi_id=bang.id),
                XtPhuongAn(de_an_id=de_an_id, de_an_chuong_trinh_id=ct.id, cong_thuc_id=cong_thuc.id),
                XtDieuKien(nhom_dieu_kien_id=nhom.id, ma_chi_so="DA_TOT_NGHIEP_THPT", toan_tu="=", gia_tri_so=1),
                XtDiemCong(
                    de_an_id=de_an_id,
                    loai_diem_cong="DIEM_THUONG",
                    nhom_cong="HSG",
                    ma_chi_so="THANH_TICH",
                    toan_tu="<=",
                    gia_tri_so=3,
                    diem_cong=1,
                ),
                DatsHocPhi(de_an_id=de_an_id, de_an_chuong_trinh_id=ct.id, hoc_phi_tu=30_000_000),
                XtLichSuImport(de_an_id=de_an_id, ten_file="mau.json"),
            ]
        )
        self.db.flush()
        return de_an_id

    def _so_dong(self, model, de_an_id: int) -> int:
        if model is XtBangQuyDoiChiTiet:
            dieu_kien = model.bang_quy_doi_id.in_(select(XtBangQuyDoi.id).where(XtBangQuyDoi.de_an_id == de_an_id))
        elif model in (XtCongThucHeSoMon, XtCongThucThanhPhan):
            dieu_kien = model.cong_thuc_id.in_(select(XtCongThuc.id).where(XtCongThuc.de_an_id == de_an_id))
        elif model is XtDieuKien:
            dieu_kien = model.nhom_dieu_kien_id.in_(select(XtNhomDieuKien.id).where(XtNhomDieuKien.de_an_id == de_an_id))
        else:
            dieu_kien = model.de_an_id == de_an_id
        return self.db.scalar(select(func.count()).select_from(model).where(dieu_kien))

    def _chuong_trinh(self, de_an_id: int) -> DatsChuongTrinhDaoTao:
        return self.db.scalars(
            select(DatsChuongTrinhDaoTao).where(DatsChuongTrinhDaoTao.de_an_id == de_an_id).order_by(DatsChuongTrinhDaoTao.id)
        ).first()

    def test_xoa_de_an_don_moi_bang_quy_tac_va_giu_de_an_khac(self):
        delete_de_an(self.de_an[0], self.db, None)
        for model in _BANG_QUY_TAC:
            with self.subTest(table=model.__tablename__):
                self.assertEqual(self._so_dong(model, self.de_an[0]), 0)
                self.assertEqual(self._so_dong(model, self.de_an[1]), 1)
        self.assertEqual(self.db.scalar(select(func.count()).select_from(DatsChuongTrinhDaoTao)), 4)

    def test_import_lai_giu_lich_su(self):
        da_xoa = delete_quy_tac_xet_tuyen(self.db, [self.de_an[0]], giu_lich_su=True)
        self.assertEqual(da_xoa["xt_phuong_an"], 1)
        self.assertNotIn("xt_lich_su_import", da_xoa)
        self.assertEqual(self._so_dong(XtLichSuImport, self.de_an[0]), 1)
        self.assertEqual(self._so_dong(XtCongThuc, self.de_an[0]), 0)

    def test_xoa_chuong_trinh_dang_co_quy_tac_bao_ro_ly_do(self):
        ct = self._chuong_trinh(self.de_an[0])
        for ham, args in (
            (delete_chuong_trinh, (ct.id,)),
            (delete_chuong_trinh_many, (DatsChuongTrinhDaoTaoDeleteMany(ids=[ct.id]),)),
        ):
            with self.subTest(ham=ham.__name__), self.assertRaises(HTTPException) as caught:
                ham(*args, self.db, None)
            self.assertEqual(caught.exception.status_code, 400)
            detail = caught.exception.detail
            self.assertIn(f"id = {ct.id}", detail)
            self.assertIn("1 phương án xét tuyển", detail)
            self.assertIn("1 dòng học phí", detail)
        self.assertIsNotNone(self.db.get(DatsChuongTrinhDaoTao, ct.id))

    def test_khong_chuyen_chuong_trinh_co_quy_tac_sang_de_an_khac(self):
        ct = self._chuong_trinh(self.de_an[0])
        payload = DatsChuongTrinhDaoTaoWrite(de_an_id=self.de_an[1], ten_chuong_trinh=ct.ten_chuong_trinh)
        with self.assertRaises(HTTPException) as caught:
            update_chuong_trinh(ct.id, payload, self.db, None)
        self.assertIn("chuyển sang đề án khác", caught.exception.detail)
        # Sửa trong cùng đề án vẫn được.
        payload = DatsChuongTrinhDaoTaoWrite(de_an_id=self.de_an[0], ten_chuong_trinh="Tên mới")
        self.assertEqual(update_chuong_trinh(ct.id, payload, self.db, None).ten_chuong_trinh, "Tên mới")


if __name__ == "__main__":
    unittest.main()
