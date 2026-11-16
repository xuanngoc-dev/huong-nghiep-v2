import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session

from app.api.v1.endpoints.dats_tuyen_sinh import create_de_an, create_de_an_bulk, update_de_an
from app.models.dats_tuyen_sinh import DatsTuyenSinh
from app.models.dm_truong import DmTruong
from app.schemas.dats_tuyen_sinh import DatsTuyenSinhWrite
from app.services.dats_import import DatsImportError, import_document


@compiles(BIGINT, "sqlite")
def _bigint_sqlite(type_, compiler, **kw):
    # SQLite chỉ tự tăng khóa chính kiểu INTEGER.
    return "INTEGER"


def _de_an(ma_truong: str, nam: int) -> DatsTuyenSinhWrite:
    return DatsTuyenSinhWrite(ma_truong=ma_truong, nam_tuyen_sinh=nam, ten_de_an=f"Đề án {ma_truong} {nam}")


class DeAnTrungNamTests(unittest.TestCase):
    """Mỗi trường chỉ có một đề án mỗi năm (bước 1.3): trùng thì trả 400 kèm thông báo."""

    def setUp(self):
        engine = create_engine("sqlite://")
        DmTruong.__table__.create(engine)
        DatsTuyenSinh.__table__.create(engine)
        self.db = Session(engine)
        self.db.add_all(
            [DmTruong(ma_truong="BKA", ten_truong="Bách khoa"), DmTruong(ma_truong="NTH", ten_truong="Ngoại thương")]
        )
        self.db.commit()
        self.bka_2026 = create_de_an(_de_an("BKA", 2026), self.db, None)

    def tearDown(self):
        self.db.close()

    def _loi_400(self, ham, *args) -> str:
        with self.assertRaises(HTTPException) as caught:
            ham(*args, self.db, None)
        self.assertEqual(caught.exception.status_code, 400)
        return caught.exception.detail

    def test_tao_trung_truong_nam_bi_tu_choi(self):
        detail = self._loi_400(create_de_an, _de_an("BKA", 2026))
        self.assertIn("trường BKA năm 2026", detail)
        self.assertIn(f"id = {self.bka_2026.id}", detail)

    def test_cung_truong_khac_nam_van_tao_duoc(self):
        moi = create_de_an(_de_an("BKA", 2027), self.db, None)
        self.assertEqual(moi.nam_tuyen_sinh, 2027)

    def test_them_nhieu_trung_trong_danh_sach_hoac_voi_csdl(self):
        detail = self._loi_400(create_de_an_bulk, [_de_an("NTH", 2026), _de_an("NTH", 2026)])
        self.assertIn("NTH/2026", detail)
        detail = self._loi_400(create_de_an_bulk, [_de_an("NTH", 2026), _de_an("BKA", 2026)])
        self.assertIn("trường BKA năm 2026", detail)
        self.assertEqual(create_de_an_bulk([_de_an("NTH", 2026), _de_an("NTH", 2025)], self.db, None).created, 2)

    def test_sua_giu_nguyen_nam_duoc_doi_sang_nam_da_co_bi_chan(self):
        ban_2027 = create_de_an(_de_an("BKA", 2027), self.db, None)
        sua = update_de_an(ban_2027.id, _de_an("BKA", 2027), self.db, None)
        self.assertEqual(sua.ten_de_an, "Đề án BKA 2027")
        detail = self._loi_400(update_de_an, ban_2027.id, _de_an("BKA", 2026))
        self.assertIn("trường BKA năm 2026", detail)

    def test_import_json_luon_tu_choi_khi_da_co_de_an(self):
        # File không ghi xu_ly_khi_da_ton_tai vẫn bị từ chối, trước khi đọc tới danh mục.
        with self.assertRaises(DatsImportError) as caught:
            import_document(self.db, "BKA", 2026, {"dats_tuyen_sinh": {"ten_de_an": "Nhập lại"}})
        self.assertIn("năm 2026", str(caught.exception))
        self.assertIn(f"id = {self.bka_2026.id}", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
