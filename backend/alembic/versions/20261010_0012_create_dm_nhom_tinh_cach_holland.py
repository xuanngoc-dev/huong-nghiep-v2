"""create_dm_nhom_tinh_cach_holland

Revision ID: 20261010_0012
Revises: 20261010_0011
Create Date: 2026-10-10 13:06:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261010_0012"
down_revision: Union[str, Sequence[str], None] = "20261010_0011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dm_nhom_tinh_cach_holland",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ma_nhom", sa.String(length=20), nullable=False),
        sa.Column("ten_nhom", sa.String(length=150), nullable=False),
        sa.Column("ten_tieng_anh", sa.String(length=150), nullable=False),
        sa.Column("mo_ta", sa.Text(), nullable=True),
        sa.Column("vi_du_nghe_nghiep", sa.Text(), nullable=True),
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
        sa.UniqueConstraint("ma_nhom", name="uq_dm_nhom_holland_ma_nhom"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index("ix_dm_nhom_holland_ten", "dm_nhom_tinh_cach_holland", ["ten_nhom"])
    op.create_index("ix_dm_nhom_holland_ma", "dm_nhom_tinh_cach_holland", ["ma_nhom"])


def downgrade() -> None:
    op.drop_index("ix_dm_nhom_holland_ma", table_name="dm_nhom_tinh_cach_holland")
    op.drop_index("ix_dm_nhom_holland_ten", table_name="dm_nhom_tinh_cach_holland")
    op.drop_table("dm_nhom_tinh_cach_holland")
