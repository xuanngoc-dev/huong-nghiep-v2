"""create_tn_cau_hoi_trac_nghiem

Revision ID: 20261010_0019
Revises: 20261010_0018
Create Date: 2026-10-10 23:28:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261010_0019"
down_revision: Union[str, Sequence[str], None] = "20261010_0018"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tn_cau_hoi_trac_nghiem",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ma_holand", sa.String(length=20), nullable=False),
        sa.Column("loai_cau_hoi_id", sa.Integer(), nullable=False),
        sa.Column("noi_dung_cau_hoi", sa.Text(), nullable=False),
        sa.Column("ghi_chu", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["ma_holand"],
            ["dm_nhom_tinh_cach_holland.ma_nhom"],
            name="fk_tn_cau_hoi_holland",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["loai_cau_hoi_id"],
            ["dm_loai_cau_hoi.id"],
            name="fk_tn_cau_hoi_loai",
            ondelete="RESTRICT",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index("ix_tn_cau_hoi_holland", "tn_cau_hoi_trac_nghiem", ["ma_holand"])
    op.create_index("ix_tn_cau_hoi_loai", "tn_cau_hoi_trac_nghiem", ["loai_cau_hoi_id"])


def downgrade() -> None:
    op.drop_index("ix_tn_cau_hoi_loai", table_name="tn_cau_hoi_trac_nghiem")
    op.drop_index("ix_tn_cau_hoi_holland", table_name="tn_cau_hoi_trac_nghiem")
    op.drop_table("tn_cau_hoi_trac_nghiem")
