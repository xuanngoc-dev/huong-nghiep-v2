"""create_dm_dan_toc

Revision ID: 20261009_0004
Revises: 20261009_0003
Create Date: 2026-10-09 19:50:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261009_0004"
down_revision: Union[str, Sequence[str], None] = "20261009_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dm_dan_toc",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ma_dan_toc", sa.String(length=20), nullable=False),
        sa.Column("ten_dan_toc", sa.String(length=150), nullable=False),
        sa.Column("ten_goi_khac", sa.String(length=255), nullable=True),
        sa.Column("dan_so", sa.Integer(), nullable=True),
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
        sa.UniqueConstraint("ma_dan_toc", name="uq_dm_dan_toc_ma_dan_toc"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index("ix_dm_dan_toc_ten_dan_toc", "dm_dan_toc", ["ten_dan_toc"])
    op.create_index("ix_dm_dan_toc_ma_dan_toc", "dm_dan_toc", ["ma_dan_toc"])


def downgrade() -> None:
    op.drop_index("ix_dm_dan_toc_ma_dan_toc", table_name="dm_dan_toc")
    op.drop_index("ix_dm_dan_toc_ten_dan_toc", table_name="dm_dan_toc")
    op.drop_table("dm_dan_toc")
