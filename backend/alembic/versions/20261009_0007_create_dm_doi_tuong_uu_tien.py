"""create_dm_doi_tuong_uu_tien

Revision ID: 20261009_0007
Revises: 20261009_0006
Create Date: 2026-10-09 23:15:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261009_0007"
down_revision: Union[str, Sequence[str], None] = "20261009_0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dm_doi_tuong_uu_tien",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ten_doi_tuong", sa.String(length=150), nullable=False),
        sa.Column("ma_doi_tuong", sa.String(length=20), nullable=False),
        sa.Column("diem_cong", sa.Numeric(precision=5, scale=2), server_default="0", nullable=False),
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
        sa.UniqueConstraint("ma_doi_tuong", name="uq_dm_doi_tuong_uu_tien_ma_doi_tuong"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index("ix_dm_doi_tuong_uu_tien_ten_doi_tuong", "dm_doi_tuong_uu_tien", ["ten_doi_tuong"])
    op.create_index("ix_dm_doi_tuong_uu_tien_ma_doi_tuong", "dm_doi_tuong_uu_tien", ["ma_doi_tuong"])


def downgrade() -> None:
    op.drop_index("ix_dm_doi_tuong_uu_tien_ma_doi_tuong", table_name="dm_doi_tuong_uu_tien")
    op.drop_index("ix_dm_doi_tuong_uu_tien_ten_doi_tuong", table_name="dm_doi_tuong_uu_tien")
    op.drop_table("dm_doi_tuong_uu_tien")
