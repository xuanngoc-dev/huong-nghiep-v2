"""Bo rang buoc duy nhat (ma_truong, nam_hoc, ma_xet_tuyen) o dm_nganh_hoc_theo_truong.

Mot ma xet tuyen co the gom nhieu nganh/chuong trinh, nen chi giu index thuong.

Revision ID: 20261112_0044
Revises: 20261112_0043
Create Date: 2026-11-12 11:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261112_0044"
down_revision: Union[str, Sequence[str], None] = "20261112_0043"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE = "dm_nganh_hoc_theo_truong"
_UNIQUE = "uq_dm_nganh_hoc_theo_truong_ma_xet_tuyen"
_INDEX = "idx_dm_nganh_hoc_theo_truong_ma_xet_tuyen"


def _index_names() -> set[str]:
    inspector = sa.inspect(op.get_bind())
    names = {idx["name"] for idx in inspector.get_indexes(_TABLE)}
    names |= {uq["name"] for uq in inspector.get_unique_constraints(_TABLE)}
    return names


def upgrade() -> None:
    names = _index_names()
    # Tạo index thường trước: khóa ngoại ma_truong đang dựa vào index duy nhất.
    if _INDEX not in names:
        op.create_index(_INDEX, _TABLE, ["ma_truong", "nam_hoc", "ma_xet_tuyen"])
    if _UNIQUE in names:
        op.drop_constraint(_UNIQUE, _TABLE, type_="unique")


def downgrade() -> None:
    names = _index_names()
    if _UNIQUE not in names:
        op.create_unique_constraint(_UNIQUE, _TABLE, ["ma_truong", "nam_hoc", "ma_xet_tuyen"])
    if _INDEX in names:
        op.drop_index(_INDEX, table_name=_TABLE)
