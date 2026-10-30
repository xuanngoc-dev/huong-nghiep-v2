"""Đổi dats_phuong_thuc.to_hop_ids thành to_hop_mon_hoc.

Cột lưu mảng mã tổ hợp, ví dụ ["A01"]. Giá trị id số cũ được đổi sang mã.

Revision ID: 20261030_0036
Revises: 20261030_0035
Create Date: 2026-10-30 15:20:00.000000
"""

import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261030_0036"
down_revision: Union[str, Sequence[str], None] = "20261030_0035"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_COMMENT = 'Danh sách mã tổ hợp môn áp dụng, ví dụ ["A01"]. NULL nếu phương thức áp dụng cho mọi tổ hợp.'
_OLD_COMMENT = "Danh sách id tổ hợp môn áp dụng. NULL nếu phương thức áp dụng cho mọi tổ hợp."


def _column_names() -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {column["name"] for column in inspector.get_columns("dats_phuong_thuc")}


def _as_list(value) -> list | None:
    if value is None:
        return None
    if isinstance(value, list):
        return value
    if isinstance(value, (bytes, bytearray)):
        value = value.decode()
    if isinstance(value, str):
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else None
    return None


def _rewrite(column: str, mapping: dict, *, as_code: bool) -> None:
    bind = op.get_bind()
    rows = bind.execute(sa.text(f"SELECT id, {column} FROM dats_phuong_thuc WHERE {column} IS NOT NULL")).all()
    for row_id, raw in rows:
        values = _as_list(raw)
        if not values:
            continue
        converted = []
        changed = False
        for item in values:
            if as_code and isinstance(item, int):
                code = mapping.get(item)
                if code is None:
                    raise RuntimeError(f"Không tìm thấy mã tổ hợp cho id {item}")
                converted.append(code)
                changed = True
                continue
            if not as_code and isinstance(item, str) and not item.isdigit():
                combo_id = mapping.get(item.strip().upper())
                if combo_id is None:
                    raise RuntimeError(f"Không tìm thấy id tổ hợp cho mã {item}")
                converted.append(combo_id)
                changed = True
                continue
            converted.append(item)
        if changed:
            bind.execute(
                sa.text(f"UPDATE dats_phuong_thuc SET {column} = :value WHERE id = :row_id"),
                {"value": json.dumps(converted, ensure_ascii=False), "row_id": row_id},
            )


def upgrade() -> None:
    if "to_hop_ids" in _column_names():
        op.alter_column(
            "dats_phuong_thuc",
            "to_hop_ids",
            new_column_name="to_hop_mon_hoc",
            existing_type=sa.JSON(),
            existing_nullable=True,
            comment=_COMMENT,
        )
    op.alter_column(
        "dats_phuong_thuc",
        "to_hop_mon_hoc",
        existing_type=sa.JSON(),
        existing_nullable=True,
        comment=_COMMENT,
    )
    codes = {
        row[0]: str(row[1]).strip().upper()
        for row in op.get_bind().execute(sa.text("SELECT id, ma_to_hop FROM dm_to_hop_mon_hoc")).all()
        if row[1]
    }
    _rewrite("to_hop_mon_hoc", codes, as_code=True)


def downgrade() -> None:
    ids = {
        str(row[1]).strip().upper(): row[0]
        for row in op.get_bind().execute(sa.text("SELECT id, ma_to_hop FROM dm_to_hop_mon_hoc")).all()
        if row[1]
    }
    _rewrite("to_hop_mon_hoc", ids, as_code=False)
    if "to_hop_mon_hoc" in _column_names():
        op.alter_column(
            "dats_phuong_thuc",
            "to_hop_mon_hoc",
            new_column_name="to_hop_ids",
            existing_type=sa.JSON(),
            existing_nullable=True,
            comment=_OLD_COMMENT,
        )
