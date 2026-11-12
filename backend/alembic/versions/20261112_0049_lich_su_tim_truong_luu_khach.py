"""Cho phep luu luot tim truong cua khach vang lai.

tai_khoan_id duoc de trong (khach), them ma_thiet_bi de dem luot cua khach theo ngay
va thong_tin_khach (ho ten, email, so dien thoai khach tu nhap).

Revision ID: 20261112_0049
Revises: 20261112_0048
Create Date: 2026-11-12 19:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision: str = "20261112_0049"
down_revision: Union[str, Sequence[str], None] = "20261112_0048"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE = "tn_lich_su_tim_truong_phu_hop"
_INDEX = "idx_tn_lich_su_tim_truong_thiet_bi_ngay"


def _columns() -> set[str]:
    return {col["name"] for col in sa.inspect(op.get_bind()).get_columns(_TABLE)}


def _indexes() -> set[str]:
    return {idx["name"] for idx in sa.inspect(op.get_bind()).get_indexes(_TABLE)}


def upgrade() -> None:
    op.alter_column(
        _TABLE,
        "tai_khoan_id",
        existing_type=mysql.BIGINT(unsigned=True),
        nullable=True,
        existing_comment="ID tài khoản thực hiện tìm kiếm",
        comment="ID tài khoản thực hiện tìm kiếm, để trống nếu là khách vãng lai",
    )
    cols = _columns()
    if "ma_thiet_bi" not in cols:
        op.add_column(
            _TABLE,
            sa.Column(
                "ma_thiet_bi",
                sa.String(64),
                nullable=True,
                comment="Mã thiết bị của khách vãng lai, dùng để đếm lượt theo ngày",
            ),
        )
        op.execute(
            f"ALTER TABLE {_TABLE} MODIFY COLUMN ma_thiet_bi VARCHAR(64) NULL "
            "COMMENT 'Mã thiết bị của khách vãng lai, dùng để đếm lượt theo ngày' AFTER tai_khoan_id"
        )
    if "thong_tin_khach" not in cols:
        op.add_column(
            _TABLE,
            sa.Column(
                "thong_tin_khach",
                sa.JSON(),
                nullable=True,
                comment="Họ tên, email, số điện thoại khách vãng lai tự nhập",
            ),
        )
        op.execute(
            f"ALTER TABLE {_TABLE} MODIFY COLUMN thong_tin_khach JSON NULL "
            "COMMENT 'Họ tên, email, số điện thoại khách vãng lai tự nhập' AFTER ma_thiet_bi"
        )
    if _INDEX not in _indexes():
        op.create_index(_INDEX, _TABLE, ["ma_thiet_bi", "ngay_tao"])


def downgrade() -> None:
    if _INDEX in _indexes():
        op.drop_index(_INDEX, table_name=_TABLE)
    cols = _columns()
    if "thong_tin_khach" in cols:
        op.drop_column(_TABLE, "thong_tin_khach")
    if "ma_thiet_bi" in cols:
        op.drop_column(_TABLE, "ma_thiet_bi")
    # Xóa lượt của khách trước khi bắt buộc lại tai_khoan_id.
    op.execute(f"DELETE FROM {_TABLE} WHERE tai_khoan_id IS NULL")
    op.alter_column(
        _TABLE,
        "tai_khoan_id",
        existing_type=mysql.BIGINT(unsigned=True),
        nullable=False,
        comment="ID tài khoản thực hiện tìm kiếm",
    )
