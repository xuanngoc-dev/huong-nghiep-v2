"""Đảm bảo mọi bảng trong docs/tuyen_sinh_mysql_dm.sql đã tồn tại.

CREATE TABLE IF NOT EXISTS chỉ chạy khi bảng còn thiếu. Bảng đã có giữ
nguyên kiểu cột và collation hiện tại. Cũng cập nhật chú thích ma_truong
của đề án theo năm sang dm_truong.

Revision ID: 20261030_0030
Revises: 20261030_0029
Create Date: 2026-10-30 09:40:00.000000
"""

from pathlib import Path
import re
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261030_0030"
down_revision: Union[str, Sequence[str], None] = "20261030_0029"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_CREATE_TABLE = re.compile(r"^CREATE TABLE IF NOT EXISTS `([^`]+)`", re.IGNORECASE)
_MA_TRUONG_COMMENT = "Mã trường, tham chiếu dm_truong.ma_truong"
_MA_TRUONG_COMMENT_CU = "Mã trường, cùng quy ước với dm_truong_dai_hoc.ma_truong"


def _sql_statements(sql: str) -> list[str]:
    lines = [line for line in sql.splitlines() if not line.strip().startswith("--")]
    text = "\n".join(lines)
    statements: list[str] = []
    buffer: list[str] = []
    in_quote = False
    index = 0
    while index < len(text):
        char = text[index]
        if char == "'":
            if in_quote and index + 1 < len(text) and text[index + 1] == "'":
                buffer.append("''")
                index += 2
                continue
            in_quote = not in_quote
            buffer.append(char)
        elif char == ";" and not in_quote:
            statement = "".join(buffer).strip()
            if statement:
                statements.append(statement)
            buffer = []
        else:
            buffer.append(char)
        index += 1
    trailing = "".join(buffer).strip()
    if trailing:
        statements.append(trailing)
    return statements


def _create_missing_design_tables() -> None:
    sql_path = Path(__file__).resolve().parents[3] / "docs" / "tuyen_sinh_mysql_dm.sql"
    statements = _sql_statements(sql_path.read_text(encoding="utf-8"))
    existing = set(sa.inspect(op.get_bind()).get_table_names())
    for statement in statements:
        match = _CREATE_TABLE.match(statement)
        if match is None or match.group(1) in existing:
            continue
        op.get_bind().exec_driver_sql(statement)


def _alter_ma_truong_comment(comment: str) -> None:
    op.alter_column(
        "truong_hoc_tuyen_sinh_theo_nam",
        "ma_truong",
        existing_type=sa.String(length=20),
        existing_nullable=False,
        comment=comment,
    )


def upgrade() -> None:
    """Tạo bảng thiết kế còn thiếu và sửa chú thích mã trường."""
    _create_missing_design_tables()
    _alter_ma_truong_comment(_MA_TRUONG_COMMENT)


def downgrade() -> None:
    """Khôi phục chú thích cũ. Không xóa bảng thiết kế."""
    _alter_ma_truong_comment(_MA_TRUONG_COMMENT_CU)
