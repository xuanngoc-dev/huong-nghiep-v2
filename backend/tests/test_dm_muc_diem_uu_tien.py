"""Bước 5.1: API mức điểm ưu tiên theo năm."""

import unittest

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import BIGINT, ENUM, SMALLINT
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session

from app.api.v1.endpoints.dm_muc_diem_uu_tien import (
    create_muc_diem_uu_tien,
    delete_muc_diem_uu_tien_many,
    get_muc_diem_uu_tien,
    list_muc_diem_uu_tien,
    update_muc_diem_uu_tien,
)
from app.models.dm_doi_tuong_uu_tien import DmDoiTuongUuTien
from app.models.dm_khu_vuc_uu_tien import DmKhuVucUuTien
from app.models.dm_muc_diem_uu_tien import DmMucDiemUuTien
from app.schemas.dm_muc_diem_uu_tien import DmMucDiemUuTienDeleteMany, DmMucDiemUuTienWrite


@compiles(BIGINT, "sqlite")
@compiles(SMALLINT, "sqlite")
def _so_nguyen_sqlite(type_, compiler, **kw):
    return "INTEGER"


@compiles(ENUM, "sqlite")
def _enum_sqlite(type_, compiler, **kw):
    return "VARCHAR(50)"


def _muc(**kw) -> DmMucDiemUuTienWrite:
    data = {"loai": "DOI_TUONG", "ma": "04", "nam_ap_dung_tu": 2026, "diem_cong": 1}
    data.update(kw)
    return DmMucDiemUuTienWrite(**data)


class MucDiemUuTienTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite://")
        for model in (DmKhuVucUuTien, DmDoiTuongUuTien, DmMucDiemUuTien):
            model.__table__.create(engine)
        self.db = Session(engine)
        self.db.add(DmKhuVucUuTien(ma_khu_vuc="KV1", ten_khu_vuc="Khu vực 1", diem_cong=0.75))
        self.db.add(DmDoiTuongUuTien(ma_doi_tuong="04", ten_doi_tuong="Đối tượng 04", diem_cong=2))
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def _list(self, **kw):
        args = {"q": None, "loai": None, "nam": None, "page": 1, "page_size": 10, "db": self.db}
        args.update(kw)
        return list_muc_diem_uu_tien(**args)

    def test_danh_sach_rong(self):
        page = self._list()
        self.assertEqual((page.items, page.total, page.page, page.page_size), ([], 0, 1, 10))

    def test_them_sua_xoa_va_loc_theo_nam(self):
        cu = create_muc_diem_uu_tien(_muc(nam_ap_dung_tu=2020, nam_ap_dung_den=2025, diem_cong=2), self.db, None)
        moi = create_muc_diem_uu_tien(_muc(ma=" 04 ", can_cu="Thông tư 06/2026/TT-BGDĐT"), self.db, None)
        self.assertEqual((moi.ma, moi.ten, moi.diem_cong), ("04", "Đối tượng 04", 1.0))
        self.assertEqual([i.id for i in self._list(nam=2026).items], [moi.id])
        self.assertEqual([i.id for i in self._list(nam=2024).items], [cu.id])
        sua = update_muc_diem_uu_tien(moi.id, _muc(diem_cong=1.5), self.db, None)
        self.assertEqual(sua.diem_cong, 1.5)
        self.assertEqual(get_muc_diem_uu_tien(moi.id, self.db, None).diem_cong, 1.5)
        self.assertEqual(delete_muc_diem_uu_tien_many(DmMucDiemUuTienDeleteMany(ids=[cu.id, 999]), self.db, None).deleted, 1)

    def test_tu_choi_ma_la_va_khoang_nam_chong(self):
        with self.assertRaises(HTTPException) as ctx:
            create_muc_diem_uu_tien(_muc(loai="KHU_VUC", ma="KV9"), self.db, None)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("KV9", ctx.exception.detail)
        create_muc_diem_uu_tien(_muc(nam_ap_dung_tu=2024, nam_ap_dung_den=2026), self.db, None)
        with self.assertRaises(HTTPException) as ctx:
            create_muc_diem_uu_tien(_muc(nam_ap_dung_tu=2026), self.db, None)
        self.assertIn("trùng khoảng năm", ctx.exception.detail)
        # Khoảng nối tiếp thì được.
        create_muc_diem_uu_tien(_muc(nam_ap_dung_tu=2027), self.db, None)
        with self.assertRaises(ValidationError):
            _muc(nam_ap_dung_tu=2026, nam_ap_dung_den=2025)

    def test_id_khong_ton_tai_tra_400(self):
        with self.assertRaises(HTTPException) as ctx:
            get_muc_diem_uu_tien(123, self.db, None)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("123", ctx.exception.detail)


if __name__ == "__main__":
    unittest.main()
