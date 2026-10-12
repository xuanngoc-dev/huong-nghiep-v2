"""add khu vuc and doi tuong uu tien to ho so

Revision ID: 20261012_0023
Revises: 20261012_0022
Create Date: 2026-10-12 19:25:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261012_0023"
down_revision: Union[str, Sequence[str], None] = "20261012_0022"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("nguoi_dung_thong_tin", sa.Column("khu_vuc_uu_tien_id", sa.Integer(), nullable=True))
    op.add_column("nguoi_dung_thong_tin", sa.Column("doi_tuong_uu_tien_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_nguoi_dung_thong_tin_khu_vuc",
        "nguoi_dung_thong_tin",
        "dm_khu_vuc_uu_tien",
        ["khu_vuc_uu_tien_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_nguoi_dung_thong_tin_doi_tuong",
        "nguoi_dung_thong_tin",
        "dm_doi_tuong_uu_tien",
        ["doi_tuong_uu_tien_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_nguoi_dung_thong_tin_khu_vuc",
        "nguoi_dung_thong_tin",
        ["khu_vuc_uu_tien_id"],
    )
    op.create_index(
        "ix_nguoi_dung_thong_tin_doi_tuong",
        "nguoi_dung_thong_tin",
        ["doi_tuong_uu_tien_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_nguoi_dung_thong_tin_doi_tuong", table_name="nguoi_dung_thong_tin")
    op.drop_index("ix_nguoi_dung_thong_tin_khu_vuc", table_name="nguoi_dung_thong_tin")
    op.drop_constraint("fk_nguoi_dung_thong_tin_doi_tuong", "nguoi_dung_thong_tin", type_="foreignkey")
    op.drop_constraint("fk_nguoi_dung_thong_tin_khu_vuc", "nguoi_dung_thong_tin", type_="foreignkey")
    op.drop_column("nguoi_dung_thong_tin", "doi_tuong_uu_tien_id")
    op.drop_column("nguoi_dung_thong_tin", "khu_vuc_uu_tien_id")
