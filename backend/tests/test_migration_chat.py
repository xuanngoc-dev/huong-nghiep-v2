"""Migration 20261121_0064 tạo bảng chat_conversations / chat_messages: chạy lại được và downgrade sạch."""

import importlib.util
import unittest
from pathlib import Path

import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

from app.models.nguoi_dung import NguoiDung

_FILE = Path(__file__).resolve().parents[1] / "alembic/versions/20261121_0064_chat_conversations_messages.py"


def _migration():
    spec = importlib.util.spec_from_file_location("migration_chat", _FILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MigrationChatTests(unittest.TestCase):
    def test_upgrade_hai_lan_roi_downgrade(self):
        mod = _migration()
        engine = sa.create_engine("sqlite://")
        with engine.begin() as conn:
            NguoiDung.__table__.create(conn)
            with Operations.context(MigrationContext.configure(conn)):
                mod.upgrade()
                mod.upgrade()
                insp = sa.inspect(conn)
                self.assertTrue({"chat_conversations", "chat_messages"} <= set(insp.get_table_names()))
                self.assertEqual(
                    {fk["referred_table"] for fk in insp.get_foreign_keys("chat_messages")},
                    {"chat_conversations", "nguoi_dung"},
                )
                mod.downgrade()
                self.assertFalse({"chat_conversations", "chat_messages"} & set(sa.inspect(conn).get_table_names()))


if __name__ == "__main__":
    unittest.main()
