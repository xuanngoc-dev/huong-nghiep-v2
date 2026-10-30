"""Mở rộng nhom_doi_tuong của chính sách đề án để chứa mô tả đầy đủ.

Revision ID: 20261030_0033
Revises: 20261030_0032
Create Date: 2026-10-30 12:10:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261030_0033"
down_revision: Union[str, Sequence[str], None] = "20261030_0032"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "dats_chinh_sach_xet_tuyen_thang",
        "nhom_doi_tuong",
        existing_type=sa.String(100),
        type_=sa.String(255),
        existing_nullable=True,
        existing_comment="Nhóm đối tượng theo quy định",
    )
    op.alter_column(
        "dats_chinh_sach_uu_tien_xet_tuyen",
        "nhom_doi_tuong",
        existing_type=sa.String(100),
        type_=sa.String(255),
        existing_nullable=True,
        existing_comment="Nhóm đối tượng được ưu tiên",
    )


def downgrade() -> None:
    op.alter_column(
        "dats_chinh_sach_uu_tien_xet_tuyen",
        "nhom_doi_tuong",
        existing_type=sa.String(255),
        type_=sa.String(100),
        existing_nullable=True,
        existing_comment="Nhóm đối tượng được ưu tiên",
    )
    op.alter_column(
        "dats_chinh_sach_xet_tuyen_thang",
        "nhom_doi_tuong",
        existing_type=sa.String(255),
        type_=sa.String(100),
        existing_nullable=True,
        existing_comment="Nhóm đối tượng theo quy định",
    )
