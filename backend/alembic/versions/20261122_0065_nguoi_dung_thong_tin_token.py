"""Them so_luong_token_kha_dung, so_luong_token_da_dung vao nguoi_dung_thong_tin.

- so_luong_token_kha_dung: token AI con dung duoc, cong khi nap goi cuoc loai_ap_dung = token.
- so_luong_token_da_dung: tong token da dung.
Ca hai BIGINT (goi token toi 1 ty token, cong don vuot gioi han INT), mac dinh 0. ht_cau_hinh_goi_cuoc.loai_ap_dung la VARCHAR nen them loai "token" khong can doi cot.

Revision ID: 20261122_0065
Revises: 20261121_0064
Create Date: 2026-11-22 09:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261122_0065"
down_revision: Union[str, Sequence[str], None] = "20261121_0064"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE = "nguoi_dung_thong_tin"
_COLUMNS = {
    "so_luong_token_kha_dung": "Số token AI còn dùng được (cộng khi nạp gói token)",
    "so_luong_token_da_dung": "Tổng số token AI đã dùng",
}


def _columns() -> set[str]:
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(_TABLE)}


def upgrade() -> None:
    existing = _columns()
    for name, comment in _COLUMNS.items():
        if name not in existing:
            op.add_column(
                _TABLE,
                sa.Column(name, sa.BigInteger(), nullable=False, server_default="0", comment=comment),
            )


def downgrade() -> None:
    existing = _columns()
    for name in reversed(list(_COLUMNS)):
        if name in existing:
            op.drop_column(_TABLE, name)
