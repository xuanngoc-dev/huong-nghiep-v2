import importlib.util
import unittest
from pathlib import Path

import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session

import app.models as M
from app.services.xet_tuyen.danh_gia import muc_diem_uu_tien


@compiles(BIGINT, "sqlite")
@compiles(SMALLINT, "sqlite")
def _so_nguyen_sqlite(type_, compiler, **kw):
    return "INTEGER"


def _nap(ten: str, file: str):
    duong_dan = Path(__file__).resolve().parents[1] / "alembic" / "versions" / file
    spec = importlib.util.spec_from_file_location(ten, duong_dan)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bang = _nap("migration_0061", "20261120_0061_dm_muc_diem_uu_tien.py")
du_lieu = _nap("migration_0062", "20261120_0062_diem_uu_tien_tt06_2026.py")


class MigrationDiemUuTienTests(unittest.TestCase):
    def setUp(self):
        self.engine = sa.create_engine("sqlite://")
        for model in (M.DmKhuVucUuTien, M.DmDoiTuongUuTien):
            model.__table__.create(self.engine)
        with Session(self.engine) as db:
            db.add_all(
                M.DmDoiTuongUuTien(ma_doi_tuong=f"0{i}", ten_doi_tuong=f"ĐT 0{i}", diem_cong=2 if i <= 4 else 1)
                for i in range(1, 8)
            )
            db.commit()

    def _chay(self, ham):
        with self.engine.begin() as conn:
            with Operations.context(MigrationContext.configure(conn)):
                ham()

    def test_tt06_tu_2026_va_giu_nam_cu(self):
        self._chay(bang.upgrade)
        self._chay(bang.upgrade)  # chạy lại không lỗi
        self._chay(du_lieu.upgrade)
        self._chay(du_lieu.upgrade)  # chạy lại không thêm dòng
        with Session(self.engine) as db:
            self.assertEqual(db.scalar(sa.select(sa.func.count()).select_from(M.DmMucDiemUuTien)), 2)
            dt_2025, dt_2026 = muc_diem_uu_tien(db, 2025)[1], muc_diem_uu_tien(db, 2026)[1]
        self.assertEqual([dt_2025[f"0{i}"] for i in range(1, 8)], [2, 2, 2, 2, 1, 1, 1])
        self.assertEqual([dt_2026[f"0{i}"] for i in range(1, 8)], [2, 2, 2, 1, 1, 1, 0])
        self._chay(du_lieu.downgrade)
        with Session(self.engine) as db:
            self.assertEqual(db.scalar(sa.select(sa.func.count()).select_from(M.DmMucDiemUuTien)), 0)
        self._chay(bang.downgrade)
        self.assertNotIn("dm_muc_diem_uu_tien", sa.inspect(self.engine).get_table_names())


if __name__ == "__main__":
    unittest.main()
