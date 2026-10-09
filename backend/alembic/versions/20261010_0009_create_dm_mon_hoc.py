"""create_dm_mon_hoc

Revision ID: 20261010_0009
Revises: 20261009_0008
Create Date: 2026-10-10 00:35:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261010_0009"
down_revision: Union[str, Sequence[str], None] = "20261009_0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dm_mon_hoc",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ten_mon_hoc", sa.String(length=150), nullable=False),
        sa.Column("ma_mon_hoc", sa.String(length=20), nullable=False),
        sa.Column("ten_viet_tat", sa.String(length=50), nullable=True),
        sa.Column(
            "nhom_mon",
            sa.String(length=50),
            nullable=True,
            comment="Nhóm môn: tự nhiên, xã hội, ngoại ngữ, ...",
        ),
        sa.Column(
            "trang_thai",
            sa.SmallInteger(),
            server_default="1",
            nullable=False,
            comment="0: ngừng sử dụng, 1: hoạt động",
        ),
        sa.Column("mo_ta", sa.Text(), nullable=True),
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
        sa.UniqueConstraint("ma_mon_hoc", name="uq_dm_mon_hoc_ma_mon_hoc"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index("ix_dm_mon_hoc_ten", "dm_mon_hoc", ["ten_mon_hoc"])
    op.create_index("ix_dm_mon_hoc_ma", "dm_mon_hoc", ["ma_mon_hoc"])


def downgrade() -> None:
    op.drop_index("ix_dm_mon_hoc_ma", table_name="dm_mon_hoc")
    op.drop_index("ix_dm_mon_hoc_ten", table_name="dm_mon_hoc")
    op.drop_table("dm_mon_hoc")
