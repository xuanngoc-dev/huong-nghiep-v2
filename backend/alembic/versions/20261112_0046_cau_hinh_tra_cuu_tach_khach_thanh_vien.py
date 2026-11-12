"""Tach so luot tra cuu thanh luot cua khach vang lai va cua thanh vien.

Doi ten so_luot_tra_cuu_mien_phi_ngay thanh so_luot_tra_cuu_thanh_vien_ngay (giu gia tri cu),
them so_luot_tra_cuu_khach_ngay mac dinh 1.

Revision ID: 20261112_0046
Revises: 20261112_0045
Create Date: 2026-11-12 16:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261112_0046"
down_revision: Union[str, Sequence[str], None] = "20261112_0045"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE = "ht_cau_hinh_tra_cuu"
_CU = "so_luot_tra_cuu_mien_phi_ngay"
_THANH_VIEN = "so_luot_tra_cuu_thanh_vien_ngay"
_KHACH = "so_luot_tra_cuu_khach_ngay"


def _columns() -> set[str]:
    return {col["name"] for col in sa.inspect(op.get_bind()).get_columns(_TABLE)}


def upgrade() -> None:
    cols = _columns()
    if _CU in cols and _THANH_VIEN not in cols:
        op.alter_column(
            _TABLE,
            _CU,
            new_column_name=_THANH_VIEN,
            existing_type=sa.Integer(),
            existing_nullable=False,
            existing_server_default="5",
            comment="Số lượt tra cứu mỗi ngày của thành viên",
        )
    if _KHACH not in cols:
        op.add_column(
            _TABLE,
            sa.Column(
                _KHACH,
                sa.Integer(),
                server_default="1",
                nullable=False,
                comment="Số lượt tra cứu mỗi ngày của khách vãng lai",
            ),
        )
        op.execute(f"ALTER TABLE {_TABLE} MODIFY COLUMN {_KHACH} INT NOT NULL DEFAULT 1 "
                   f"COMMENT 'Số lượt tra cứu mỗi ngày của khách vãng lai' AFTER id")


def downgrade() -> None:
    cols = _columns()
    if _KHACH in cols:
        op.drop_column(_TABLE, _KHACH)
    if _THANH_VIEN in cols and _CU not in cols:
        op.alter_column(
            _TABLE,
            _THANH_VIEN,
            new_column_name=_CU,
            existing_type=sa.Integer(),
            existing_nullable=False,
            existing_server_default="5",
            comment="Số lượt tra cứu miễn phí mỗi ngày",
        )
