"""Them cot kieu_tra_loi vao ht_cau_hinh_enduser.

Gia tri: diem_so hoac tinh_huong.

Revision ID: 20261113_0051
Revises: 20261113_0050
Create Date: 2026-11-13 14:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261113_0051"
down_revision: Union[str, Sequence[str], None] = "20261113_0050"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE = "ht_cau_hinh_enduser"
_COLUMN = "kieu_tra_loi"


def _columns() -> set[str]:
    return {col["name"] for col in sa.inspect(op.get_bind()).get_columns(_TABLE)}


def upgrade() -> None:
    if _COLUMN in _columns():
        return
    op.add_column(
        _TABLE,
        sa.Column(
            _COLUMN,
            sa.String(length=20),
            nullable=False,
            server_default="diem_so",
            comment="Kiểu trả lời: diem_so hoặc tinh_huong",
        ),
    )


def downgrade() -> None:
    if _COLUMN in _columns():
        op.drop_column(_TABLE, _COLUMN)
