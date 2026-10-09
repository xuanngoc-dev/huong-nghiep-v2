"""create_dm_tinh_thanh

Revision ID: 20261009_0003
Revises: 20261009_0002
Create Date: 2026-10-09 19:06:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261009_0003"
down_revision: Union[str, Sequence[str], None] = "20261009_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dm_tinh_thanh",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ten_tinh", sa.String(length=150), nullable=False),
        sa.Column("ma_tinh", sa.String(length=20), nullable=False),
        sa.Column("khu_vuc", sa.String(length=100), nullable=True),
        sa.Column("dien_tich", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("nam_thanh_lap", sa.SmallInteger(), nullable=True),
        sa.Column(
            "trang_thai",
            sa.SmallInteger(),
            server_default="1",
            nullable=False,
            comment="0: ngừng sử dụng, 1: hoạt động",
        ),
        sa.Column("ghi_chu", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ma_tinh", name="uq_dm_tinh_thanh_ma_tinh"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index("ix_dm_tinh_thanh_ten_tinh", "dm_tinh_thanh", ["ten_tinh"])
    op.create_index("ix_dm_tinh_thanh_ma_tinh", "dm_tinh_thanh", ["ma_tinh"])


def downgrade() -> None:
    op.drop_index("ix_dm_tinh_thanh_ma_tinh", table_name="dm_tinh_thanh")
    op.drop_index("ix_dm_tinh_thanh_ten_tinh", table_name="dm_tinh_thanh")
    op.drop_table("dm_tinh_thanh")
