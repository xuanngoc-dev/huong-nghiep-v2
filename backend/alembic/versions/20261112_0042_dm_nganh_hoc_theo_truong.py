"""Tao bang dm_nganh_hoc_theo_truong.

Luu cac nganh dao tao cua tung truong theo nam hoc.

Revision ID: 20261112_0042
Revises: 20261111_0041
Create Date: 2026-11-12 09:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261112_0042"
down_revision: Union[str, Sequence[str], None] = "20261111_0041"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE = "dm_nganh_hoc_theo_truong"


def _has_table(table: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(table)


def upgrade() -> None:
    if _has_table(_TABLE):
        return
    op.create_table(
        _TABLE,
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "ma_truong",
            sa.String(length=20),
            nullable=False,
            comment="Mã trường, tham chiếu dm_truong.ma_truong",
        ),
        sa.Column("nam_hoc", sa.Integer(), nullable=False, comment="Năm học/năm tuyển sinh"),
        sa.Column("ma_nganh", sa.String(length=20), nullable=False, comment="Mã ngành"),
        sa.Column("ma_xet_tuyen", sa.String(length=50), nullable=False, comment="Mã xét tuyển của trường"),
        sa.Column("ten_nganh", sa.String(length=255), nullable=False, comment="Tên ngành"),
        sa.Column("ten_chuong_trinh", sa.String(length=255), nullable=True, comment="Tên chương trình đào tạo"),
        sa.Column("ghi_chu", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["ma_truong"],
            ["dm_truong.ma_truong"],
            name="fk_dm_nganh_hoc_theo_truong_ma_truong",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "ma_truong",
            "nam_hoc",
            "ma_xet_tuyen",
            name="uq_dm_nganh_hoc_theo_truong_ma_xet_tuyen",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index("idx_dm_nganh_hoc_theo_truong_nam_hoc", _TABLE, ["nam_hoc"])
    op.create_index("idx_dm_nganh_hoc_theo_truong_ma_nganh", _TABLE, ["ma_nganh"])


def downgrade() -> None:
    if _has_table(_TABLE):
        op.drop_table(_TABLE)
