import importlib.util
import json
import unittest
from pathlib import Path

import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT, TINYINT
from sqlalchemy.ext.compiler import compiles

import app.models  # noqa: F401  # nạp toàn bộ model vào metadata
from app.db.base import Base


@compiles(BIGINT, "sqlite")
@compiles(TINYINT, "sqlite")
@compiles(SMALLINT, "sqlite")
def _so_nguyen_sqlite(type_, compiler, **kw):
    # SQLite chỉ tự tăng khóa chính kiểu INTEGER; kiểu số nguyên MySQL khác cũng quy về INTEGER.
    return "INTEGER"


_FILE = Path(__file__).resolve().parents[1] / "alembic" / "versions" / "20261117_0058_xt_quy_tac_xet_tuyen.py"
_spec = importlib.util.spec_from_file_location("migration_0058", _FILE)
migration = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(migration)

# Bảng có sẵn mà các bảng mới trỏ tới.
_BANG_NEN = [
    "nguoi_dung",
    "dm_truong",
    "dm_mon_hoc",
    "dm_to_hop_mon_hoc",
    "dm_to_hop_mon_hoc_chi_tiet",
    "dm_phuong_thuc_tuyen_sinh",
    "dm_bai_thi_danh_gia",
    "dm_bang_cap_chung_chi",
    "dats_tuyen_sinh",
    "dats_tru_so",
    "dats_chuong_trinh_dao_tao",
    "dats_phuong_thuc",
]


class MigrationXtQuyTacTests(unittest.TestCase):
    def setUp(self):
        self.engine = sa.create_engine("sqlite://")
        Base.metadata.create_all(self.engine, tables=[Base.metadata.tables[t] for t in _BANG_NEN])
        with self.engine.begin() as conn:
            for ma, nhom in (("TOAN", "Tự nhiên"), ("VAN", "Xã hội"), ("LY", "Tự nhiên"), ("HOA", "Tự nhiên"),
                             ("SINH", "Tự nhiên"), ("TIN", "Tự nhiên"), ("ANH", "Ngoại ngữ")):
                conn.execute(
                    sa.text("INSERT INTO dm_mon_hoc (ma_mon_hoc, ten_mon_hoc, nhom_mon, trang_thai) "
                            "VALUES (:ma, :ma, :nhom, 1)"),
                    {"ma": ma, "nhom": nhom},
                )
            for ma, ds in (("A00", ["TOAN", "LY", "HOA"]), ("K01", ["TOAN", "VAN", "LY", "HOA", "SINH", "TIN"]),
                           ("K00", []), ("X01", ["TOAN", "CN", "GDDP"])):
                conn.execute(
                    sa.text("INSERT INTO dm_to_hop_mon_hoc (ma_to_hop, ten_to_hop, ds_mon_hoc, trang_thai) "
                            "VALUES (:ma, :ma, :ds, 1)"),
                    {"ma": ma, "ds": json.dumps(ds)},
                )

    def _chay(self, ham):
        with self.engine.begin() as conn:
            with Operations.context(MigrationContext.configure(conn)):
                ham()

    def _dem(self, sql):
        with self.engine.connect() as conn:
            return conn.execute(sa.text(sql)).scalar()

    def test_nang_cap_hai_lan_va_ha_cap(self):
        self._chay(migration.upgrade)
        self._chay(migration.upgrade)  # chạy lại không lỗi, không nhân đôi dữ liệu nền
        bang = set(sa.inspect(self.engine).get_table_names())
        self.assertTrue(set(migration._THU_TU) <= bang)
        self.assertEqual(self._dem("SELECT COUNT(*) FROM dm_chi_so_xet_tuyen"), len(migration.CHI_SO))
        self.assertEqual(self._dem("SELECT COUNT(*) FROM xt_bo_tieu_chi WHERE mac_dinh = 1"), 1)
        self.assertEqual(self._dem("SELECT SUM(trong_so) FROM xt_tieu_chi_phu_hop"), 100)
        self.assertEqual(self._dem("SELECT COUNT(*) FROM xt_muc_phu_hop"), len(migration.MUC_PHU_HOP))
        # A00: 3 môn; K01: Toán, Văn + một trong 4 môn ở vị trí 3; K00 và X01 không dựng được.
        self.assertEqual(self._dem("SELECT COUNT(*) FROM dm_to_hop_mon_hoc_chi_tiet"), 3 + 6)
        self.assertEqual(
            self._dem(
                "SELECT COUNT(*) FROM dm_to_hop_mon_hoc_chi_tiet c JOIN dm_to_hop_mon_hoc t ON t.id = c.to_hop_id "
                "WHERE t.ma_to_hop = 'K01' AND c.thu_tu_mon = 3"
            ),
            4,
        )
        self._chay(migration.downgrade)
        self.assertFalse(set(migration._THU_TU) & set(sa.inspect(self.engine).get_table_names()))
        # Chi tiết tổ hợp là dữ liệu danh mục, giữ lại khi hạ cấp.
        self.assertEqual(self._dem("SELECT COUNT(*) FROM dm_to_hop_mon_hoc_chi_tiet"), 9)

    def test_cot_model_khop_migration(self):
        self._chay(migration.upgrade)
        inspector = sa.inspect(self.engine)
        for table in migration._THU_TU:
            with self.subTest(table=table):
                trong_db = {c["name"] for c in inspector.get_columns(table)}
                self.assertEqual(set(Base.metadata.tables[table].columns.keys()), trong_db)


class ViTriToHopTests(unittest.TestCase):
    ID_MON = {"TOAN": 1, "VAN": 2, "LY": 3, "HOA": 4, "SINH": 5, "TIN": 6}

    def test_to_hop_ba_mon_theo_thu_tu(self):
        self.assertEqual(
            migration.vi_tri_to_hop("A00", '["TOAN", "LY", "HOA"]', self.ID_MON), [(1, 1, None), (3, 2, None), (4, 3, None)]
        )

    def test_khong_du_ba_vi_tri_thi_bo_qua(self):
        self.assertEqual(migration.vi_tri_to_hop("X01", ["TOAN", "CN", "GDDP"], self.ID_MON), [])
        self.assertEqual(migration.vi_tri_to_hop("K00", [], self.ID_MON), [])
        self.assertEqual(migration.vi_tri_to_hop("M00", ["VAN", "TOAN", "LY", "HOA"], self.ID_MON), [])


if __name__ == "__main__":
    unittest.main()
