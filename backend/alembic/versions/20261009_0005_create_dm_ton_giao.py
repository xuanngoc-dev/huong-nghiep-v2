"""create_dm_ton_giao

Revision ID: 20261009_0005
Revises: 20261009_0004
Create Date: 2026-10-09 19:58:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261009_0005"
down_revision: Union[str, Sequence[str], None] = "20261009_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dm_ton_giao",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ma_ton_giao", sa.String(length=20), nullable=False),
        sa.Column("ten_ton_giao", sa.String(length=150), nullable=False),
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
        sa.UniqueConstraint("ma_ton_giao", name="uq_dm_ton_giao_ma_ton_giao"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index("ix_dm_ton_giao_ten_ton_giao", "dm_ton_giao", ["ten_ton_giao"])
    op.create_index("ix_dm_ton_giao_ma_ton_giao", "dm_ton_giao", ["ma_ton_giao"])


def downgrade() -> None:
    op.drop_index("ix_dm_ton_giao_ma_ton_giao", table_name="dm_ton_giao")
    op.drop_index("ix_dm_ton_giao_ten_ton_giao", table_name="dm_ton_giao")
    op.drop_table("dm_ton_giao")
