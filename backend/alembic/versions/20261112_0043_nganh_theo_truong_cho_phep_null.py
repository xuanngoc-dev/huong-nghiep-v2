"""Cho phep de trong ma_nganh, ma_xet_tuyen, ten_nganh o dm_nganh_hoc_theo_truong.

Du lieu import co the thieu cac thong tin nay.

Revision ID: 20261112_0043
Revises: 20261112_0042
Create Date: 2026-11-12 10:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261112_0043"
down_revision: Union[str, Sequence[str], None] = "20261112_0042"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE = "dm_nganh_hoc_theo_truong"
_COLUMNS = (
    ("ma_nganh", sa.String(length=20), "Mã ngành"),
    ("ma_xet_tuyen", sa.String(length=50), "Mã xét tuyển của trường"),
    ("ten_nganh", sa.String(length=255), "Tên ngành"),
)


def _is_nullable(column: str) -> bool | None:
    for col in sa.inspect(op.get_bind()).get_columns(_TABLE):
        if col["name"] == column:
            return col["nullable"]
    return None


def upgrade() -> None:
    for name, type_, comment in _COLUMNS:
        if _is_nullable(name) is False:
            op.alter_column(_TABLE, name, existing_type=type_, nullable=True, existing_comment=comment)


def downgrade() -> None:
    # Không đặt lại NOT NULL vì có thể đã có bản ghi để trống.
    pass
