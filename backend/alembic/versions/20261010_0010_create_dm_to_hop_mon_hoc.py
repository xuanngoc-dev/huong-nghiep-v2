"""create_dm_to_hop_mon_hoc

Revision ID: 20261010_0010
Revises: 20261010_0009
Create Date: 2026-10-10 00:36:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261010_0010"
down_revision: Union[str, Sequence[str], None] = "20261010_0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dm_to_hop_mon_hoc",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ten_to_hop", sa.String(length=150), nullable=False),
        sa.Column("ma_to_hop", sa.String(length=20), nullable=False),
        sa.Column(
            "ds_mon_hoc",
            sa.JSON(),
            nullable=False,
            comment="Danh sách mã môn học (ma_mon_hoc) lấy từ dm_mon_hoc",
        ),
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
        sa.UniqueConstraint("ma_to_hop", name="uq_dm_to_hop_mon_hoc_ma_to_hop"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index("ix_dm_to_hop_mon_hoc_ten", "dm_to_hop_mon_hoc", ["ten_to_hop"])
    op.create_index("ix_dm_to_hop_mon_hoc_ma", "dm_to_hop_mon_hoc", ["ma_to_hop"])


def downgrade() -> None:
    op.drop_index("ix_dm_to_hop_mon_hoc_ma", table_name="dm_to_hop_mon_hoc")
    op.drop_index("ix_dm_to_hop_mon_hoc_ten", table_name="dm_to_hop_mon_hoc")
    op.drop_table("dm_to_hop_mon_hoc")
