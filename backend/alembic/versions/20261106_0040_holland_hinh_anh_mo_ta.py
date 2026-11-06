"""Them hinh_anh_mo_ta cho dm_nhom_tinh_cach_holland.

Cot cho phep NULL, luu URL hinh anh mo ta.

Revision ID: 20261106_0040
Revises: 20261106_0039
Create Date: 2026-11-06 15:50:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261106_0040"
down_revision: Union[str, Sequence[str], None] = "20261106_0039"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    return any(item["name"] == column for item in sa.inspect(op.get_bind()).get_columns(table))


def upgrade() -> None:
    if _has_column("dm_nhom_tinh_cach_holland", "hinh_anh_mo_ta"):
        return
    op.add_column(
        "dm_nhom_tinh_cach_holland",
        sa.Column(
            "hinh_anh_mo_ta",
            sa.String(length=500),
            nullable=True,
            comment="URL hình ảnh mô tả",
        ),
    )


def downgrade() -> None:
    if _has_column("dm_nhom_tinh_cach_holland", "hinh_anh_mo_ta"):
        op.drop_column("dm_nhom_tinh_cach_holland", "hinh_anh_mo_ta")
