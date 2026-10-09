"""create_dm_phuong_thuc_tuyen_sinh

Revision ID: 20261009_0008
Revises: 20261009_0007
Create Date: 2026-10-09 23:35:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261009_0008"
down_revision: Union[str, Sequence[str], None] = "20261009_0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dm_phuong_thuc_tuyen_sinh",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ten_phuong_thuc", sa.String(length=255), nullable=False),
        sa.Column("ma_phuong_thuc", sa.String(length=20), nullable=False),
        sa.Column("giai_thich", sa.Text(), nullable=True),
        sa.Column("truong_hop_cu_the", sa.Text(), nullable=True),
        sa.Column("luu_y", sa.Text(), nullable=True),
        sa.Column(
            "trang_thai",
            sa.SmallInteger(),
            server_default="1",
            nullable=False,
            comment="0: ngừng sử dụng, 1: hoạt động",
        ),
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
        sa.UniqueConstraint("ma_phuong_thuc", name="uq_dm_phuong_thuc_tuyen_sinh_ma"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index(
        "ix_dm_phuong_thuc_tuyen_sinh_ten",
        "dm_phuong_thuc_tuyen_sinh",
        ["ten_phuong_thuc"],
    )
    op.create_index(
        "ix_dm_phuong_thuc_tuyen_sinh_ma",
        "dm_phuong_thuc_tuyen_sinh",
        ["ma_phuong_thuc"],
    )


def downgrade() -> None:
    op.drop_index("ix_dm_phuong_thuc_tuyen_sinh_ma", table_name="dm_phuong_thuc_tuyen_sinh")
    op.drop_index("ix_dm_phuong_thuc_tuyen_sinh_ten", table_name="dm_phuong_thuc_tuyen_sinh")
    op.drop_table("dm_phuong_thuc_tuyen_sinh")
