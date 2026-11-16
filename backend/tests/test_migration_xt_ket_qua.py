import importlib.util
import unittest
from pathlib import Path

import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, SMALLINT
from sqlalchemy.ext.compiler import compiles

import app.models  # noqa: F401  # nạp toàn bộ model vào metadata
from app.db.base import Base


@compiles(BIGINT, "sqlite")
@compiles(INTEGER, "sqlite")
@compiles(SMALLINT, "sqlite")
def _so_nguyen_sqlite(type_, compiler, **kw):
    # SQLite chỉ tự tăng khóa chính kiểu INTEGER; kiểu số nguyên MySQL khác cũng quy về INTEGER.
    return "INTEGER"


_FILE = Path(__file__).resolve().parents[1] / "alembic" / "versions" / "20261118_0059_xt_ket_qua_danh_gia.py"
_spec = importlib.util.spec_from_file_location("migration_0059", _FILE)
migration = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(migration)


class MigrationXtKetQuaTests(unittest.TestCase):
    def setUp(self):
        self.engine = sa.create_engine("sqlite://")

    def _chay(self, ham):
        with self.engine.begin() as conn:
            with Operations.context(MigrationContext.configure(conn)):
                ham()

    def test_nang_cap_hai_lan_cot_khop_model_va_ha_cap(self):
        self._chay(migration.upgrade)
        self._chay(migration.upgrade)
        inspector = sa.inspect(self.engine)
        for table in migration._THU_TU:
            with self.subTest(table=table):
                trong_db = {c["name"] for c in inspector.get_columns(table)}
                self.assertEqual(set(Base.metadata.tables[table].columns.keys()), trong_db)
        self._chay(migration.downgrade)
        self.assertFalse(set(migration._THU_TU) & set(sa.inspect(self.engine).get_table_names()))

    def test_ddl_mysql_hop_le_voi_5_7(self):
        """Không dùng DEFAULT dạng biểu thức (now()) mà MySQL 5.7 không nhận."""
        import io

        buf = io.StringIO()
        ctx = MigrationContext.configure(dialect_name="mysql", opts={"as_sql": True, "output_buffer": buf})
        goc = migration._has_table
        migration._has_table = lambda _table: False
        try:
            with Operations.context(ctx):
                migration.upgrade()
        finally:
            migration._has_table = goc
        ddl = buf.getvalue()
        self.assertEqual(ddl.count("CREATE TABLE"), 3)
        self.assertNotIn("DEFAULT (", ddl)
        self.assertIn("DEFAULT CURRENT_TIMESTAMP", ddl)


if __name__ == "__main__":
    unittest.main()
