"""Tao bang ht_ngan_hang_thanh_toan.

Luu tai khoan ngan hang nhan thanh toan cua he thong.

Revision ID: 20261111_0041
Revises: 20261106_0040
Create Date: 2026-11-11 16:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261111_0041"
down_revision: Union[str, Sequence[str], None] = "20261106_0040"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE = "ht_ngan_hang_thanh_toan"


def _has_table(table: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(table)


def upgrade() -> None:
    if _has_table(_TABLE):
        return
    op.create_table(
        _TABLE,
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ten_ngan_hang", sa.String(length=255), nullable=False, comment="Tên ngân hàng"),
        sa.Column("ten_ngan_hang_tieng_anh", sa.String(length=255), nullable=True, comment="Tên tiếng Anh"),
        sa.Column("ten_ngan_hang_viet_tat", sa.String(length=50), nullable=False, comment="Tên viết tắt"),
        sa.Column("so_tai_khoan", sa.String(length=50), nullable=False, comment="Số tài khoản"),
        sa.Column("chu_tai_khoan", sa.String(length=255), nullable=False, comment="Chủ tài khoản"),
        sa.Column("logo_ngan_hang", sa.String(length=500), nullable=True, comment="URL logo ngân hàng"),
        sa.Column("ghi_chu", sa.Text(), nullable=True),
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
        sa.UniqueConstraint(
            "ten_ngan_hang_viet_tat",
            "so_tai_khoan",
            name="uq_ht_ngan_hang_thanh_toan_tai_khoan",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index(
        "ix_ht_ngan_hang_thanh_toan_ten_ngan_hang",
        _TABLE,
        ["ten_ngan_hang"],
    )


def downgrade() -> None:
    if _has_table(_TABLE):
        op.drop_table(_TABLE)
