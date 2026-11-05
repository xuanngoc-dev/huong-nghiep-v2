"""Them hinh_anh_mo_ta cho nhom nganh va nganh dao tao.

Cot cho phep NULL, luu URL hinh anh mo ta. dm_nganh_dao_tao da co cot nay
tu revision 20261015_0027; migration chi them khi cot chua ton tai.

Revision ID: 20261105_0037
Revises: 20261030_0036
Create Date: 2026-11-05 09:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261105_0037"
down_revision: Union[str, Sequence[str], None] = "20261030_0036"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    return any(item["name"] == column for item in sa.inspect(op.get_bind()).get_columns(table))


def _add_hinh_anh(table: str) -> None:
    if _has_column(table, "hinh_anh_mo_ta"):
        return
    op.add_column(
        table,
        sa.Column(
            "hinh_anh_mo_ta",
            sa.String(length=500),
            nullable=True,
            comment="URL hình ảnh mô tả",
        ),
    )


def upgrade() -> None:
    _add_hinh_anh("dm_nhom_nganh_dao_tao")
    _add_hinh_anh("dm_nganh_dao_tao")


def downgrade() -> None:
    if _has_column("dm_nhom_nganh_dao_tao", "hinh_anh_mo_ta"):
        op.drop_column("dm_nhom_nganh_dao_tao", "hinh_anh_mo_ta")
