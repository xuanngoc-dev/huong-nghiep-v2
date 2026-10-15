"""chi_tiet_tra_loi_nullable_answer

Revision ID: 20261015_0026
Revises: 20261014_0025
Create Date: 2026-10-15 09:10:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261015_0026"
down_revision: Union[str, Sequence[str], None] = "20261014_0025"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "tn_chi_tiet_tra_loi",
        "cau_tra_loi_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.alter_column(
        "tn_chi_tiet_tra_loi",
        "diem_dat_duoc",
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade() -> None:
    op.execute("DELETE FROM tn_chi_tiet_tra_loi WHERE cau_tra_loi_id IS NULL OR diem_dat_duoc IS NULL")
    op.alter_column(
        "tn_chi_tiet_tra_loi",
        "cau_tra_loi_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.alter_column(
        "tn_chi_tiet_tra_loi",
        "diem_dat_duoc",
        existing_type=sa.Integer(),
        nullable=False,
    )
