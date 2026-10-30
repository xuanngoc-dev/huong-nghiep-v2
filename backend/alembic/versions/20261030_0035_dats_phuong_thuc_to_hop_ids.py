"""Đổi dats_phuong_thuc.to_hop_id thành to_hop_ids.

Một phương thức có thể gắn nhiều tổ hợp. NULL nghĩa là áp dụng mọi tổ hợp.
Id cũ được chuyển thành mảng một phần tử.

Revision ID: 20261030_0035
Revises: 20261030_0034
Create Date: 2026-10-30 15:15:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261030_0035"
down_revision: Union[str, Sequence[str], None] = "20261030_0034"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_COMMENT = "Danh sách id tổ hợp môn áp dụng. NULL nếu phương thức áp dụng cho mọi tổ hợp."
_OLD_COMMENT = "Tổ hợp áp dụng; NULL nếu không dùng tổ hợp.; một tổ hợp theo Excel; nhiều tổ hợp dùng dats_phuong_thuc_to_hop."


def _drop_fk_if_exists(name: str) -> None:
    inspector = sa.inspect(op.get_bind())
    names = {item["name"] for item in inspector.get_foreign_keys("dats_phuong_thuc")}
    if name in names:
        op.drop_constraint(name, "dats_phuong_thuc", type_="foreignkey")


def _drop_index_if_exists(name: str) -> None:
    inspector = sa.inspect(op.get_bind())
    names = {item["name"] for item in inspector.get_indexes("dats_phuong_thuc")}
    if name in names:
        op.drop_index(name, table_name="dats_phuong_thuc")


def upgrade() -> None:
    op.add_column(
        "dats_phuong_thuc",
        sa.Column("to_hop_ids", sa.JSON(), nullable=True, comment=_COMMENT),
    )
    op.execute(
        sa.text(
            """
            UPDATE dats_phuong_thuc
            SET to_hop_ids = JSON_ARRAY(to_hop_id)
            WHERE to_hop_id IS NOT NULL
            """
        )
    )
    _drop_fk_if_exists("fk_dats_phuong_thuc_to_hop_id")
    _drop_index_if_exists("idx_dats_phuong_thuc_to_hop_id")
    op.drop_column("dats_phuong_thuc", "to_hop_id")


def downgrade() -> None:
    op.add_column(
        "dats_phuong_thuc",
        sa.Column("to_hop_id", sa.Integer(), nullable=True, comment=_OLD_COMMENT),
    )
    multiple = op.get_bind().execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM dats_phuong_thuc
            WHERE to_hop_ids IS NOT NULL AND JSON_LENGTH(to_hop_ids) > 1
            """
        )
    ).scalar()
    if multiple:
        raise RuntimeError("Không hạ được migration vì có phương thức gắn nhiều tổ hợp")
    op.execute(
        sa.text(
            """
            UPDATE dats_phuong_thuc
            SET to_hop_id = JSON_EXTRACT(to_hop_ids, '$[0]')
            WHERE to_hop_ids IS NOT NULL AND JSON_LENGTH(to_hop_ids) = 1
            """
        )
    )
    op.drop_column("dats_phuong_thuc", "to_hop_ids")
    op.create_index("idx_dats_phuong_thuc_to_hop_id", "dats_phuong_thuc", ["to_hop_id"])
    op.create_foreign_key(
        "fk_dats_phuong_thuc_to_hop_id",
        "dats_phuong_thuc",
        "dm_to_hop_mon_hoc",
        ["to_hop_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
