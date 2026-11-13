"""Tao bang ht_cau_hinh_enduser.

Luu cau hinh phia nguoi dung cuoi, noi dung cau hinh dang JSON.

Revision ID: 20261113_0050
Revises: 20261112_0049
Create Date: 2026-11-13 12:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261113_0050"
down_revision: Union[str, Sequence[str], None] = "20261112_0049"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE = "ht_cau_hinh_enduser"


def _has_table(table: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(table)


def upgrade() -> None:
    if _has_table(_TABLE):
        return
    op.create_table(
        _TABLE,
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ten_cau_hinh", sa.String(length=255), nullable=False, comment="Tên cấu hình"),
        sa.Column("noi_dung_cau_hinh", sa.JSON(), nullable=True, comment="Nội dung cấu hình (JSON)"),
        sa.Column("mo_ta", sa.Text(), nullable=True, comment="Mô tả"),
        sa.Column(
            "trang_thai",
            sa.SmallInteger(),
            server_default="1",
            nullable=False,
            comment="0: ngừng sử dụng, 1: hoạt động",
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index(
        "ix_ht_cau_hinh_enduser_ten_cau_hinh",
        _TABLE,
        ["ten_cau_hinh"],
    )


def downgrade() -> None:
    if _has_table(_TABLE):
        op.drop_table(_TABLE)
