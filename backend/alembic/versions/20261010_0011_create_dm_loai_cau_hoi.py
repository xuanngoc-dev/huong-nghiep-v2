"""create_dm_loai_cau_hoi

Revision ID: 20261010_0011
Revises: 20261010_0010
Create Date: 2026-10-10 13:05:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261010_0011"
down_revision: Union[str, Sequence[str], None] = "20261010_0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dm_loai_cau_hoi",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ten_loai_cau_hoi", sa.String(length=150), nullable=False),
        sa.Column("ghi_chu", sa.Text(), nullable=True),
        sa.Column("thu_tu_uu_tien", sa.Integer(), nullable=False),
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
        sa.UniqueConstraint("thu_tu_uu_tien", name="uq_dm_loai_cau_hoi_thu_tu"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index("ix_dm_loai_cau_hoi_ten", "dm_loai_cau_hoi", ["ten_loai_cau_hoi"])
    op.create_index("ix_dm_loai_cau_hoi_thu_tu", "dm_loai_cau_hoi", ["thu_tu_uu_tien"])


def downgrade() -> None:
    op.drop_index("ix_dm_loai_cau_hoi_thu_tu", table_name="dm_loai_cau_hoi")
    op.drop_index("ix_dm_loai_cau_hoi_ten", table_name="dm_loai_cau_hoi")
    op.drop_table("dm_loai_cau_hoi")
