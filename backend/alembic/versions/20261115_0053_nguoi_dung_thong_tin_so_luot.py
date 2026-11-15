"""Them so luot tra cuu, hoi dap, khao sat vao nguoi_dung_thong_tin.

Luot mua them cua nguoi dung (cong khi nap goi cuoc, tru khi su dung).

Revision ID: 20261115_0053
Revises: 20261115_0052
Create Date: 2026-11-15 16:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261115_0053"
down_revision: Union[str, Sequence[str], None] = "20261115_0052"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE = "nguoi_dung_thong_tin"
_COLUMNS = (
    ("luot_tra_cuu", "Số lượt tra cứu còn lại"),
    ("luot_hoi_dap", "Số lượt hỏi đáp còn lại"),
    ("luot_khao_sat", "Số lượt khảo sát còn lại"),
)


def _columns() -> set[str]:
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(_TABLE)}


def upgrade() -> None:
    existing = _columns()
    for name, comment in _COLUMNS:
        if name in existing:
            continue
        op.add_column(
            _TABLE,
            sa.Column(name, sa.Integer(), server_default="0", nullable=False, comment=comment),
        )


def downgrade() -> None:
    existing = _columns()
    for name, _comment in reversed(_COLUMNS):
        if name in existing:
            op.drop_column(_TABLE, name)
