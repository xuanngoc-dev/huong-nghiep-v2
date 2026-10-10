"""create_tn_cau_tra_loi

Revision ID: 20261010_0020
Revises: 20261010_0019
Create Date: 2026-10-10 23:29:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261010_0020"
down_revision: Union[str, Sequence[str], None] = "20261010_0019"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tn_cau_tra_loi",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cau_hoi_id", sa.Integer(), nullable=False),
        sa.Column("noi_dung_cau_tra_loi", sa.Text(), nullable=False),
        sa.Column("diem", sa.Integer(), nullable=False),
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
            ["cau_hoi_id"],
            ["tn_cau_hoi_trac_nghiem.id"],
            name="fk_tn_cau_tra_loi_cau_hoi",
            ondelete="CASCADE",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index("ix_tn_cau_tra_loi_cau_hoi", "tn_cau_tra_loi", ["cau_hoi_id"])


def downgrade() -> None:
    op.drop_index("ix_tn_cau_tra_loi_cau_hoi", table_name="tn_cau_tra_loi")
    op.drop_table("tn_cau_tra_loi")
