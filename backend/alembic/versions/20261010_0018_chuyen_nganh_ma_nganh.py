"""store major code on dm_chuyen_nganh

Revision ID: 20261010_0018
Revises: 20261010_0017
Create Date: 2026-10-10 14:36:00.000000

dm_chuyen_nganh.nganh_id -> ma_nganh, liên kết dm_nganh_dao_tao.ma_nganh
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261010_0018"
down_revision: Union[str, Sequence[str], None] = "20261010_0017"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _require_filled(table: str, column: str) -> None:
    missing = op.get_bind().execute(sa.text(f"SELECT COUNT(*) FROM {table} WHERE {column} IS NULL")).scalar()
    if missing:
        raise RuntimeError(f"Không đổi được {table}.{column}: còn {missing} dòng chưa có mã ngành")


def upgrade() -> None:
    op.add_column("dm_chuyen_nganh", sa.Column("ma_nganh", sa.String(length=20), nullable=True))
    op.execute(
        """
        UPDATE dm_chuyen_nganh AS chuyen
        JOIN dm_nganh_dao_tao AS nganh ON chuyen.nganh_id = nganh.id
        SET chuyen.ma_nganh = nganh.ma_nganh
        """
    )
    _require_filled("dm_chuyen_nganh", "ma_nganh")
    op.alter_column(
        "dm_chuyen_nganh",
        "ma_nganh",
        existing_type=sa.String(length=20),
        nullable=False,
    )
    op.drop_constraint("fk_dm_chuyen_nganh_nganh", "dm_chuyen_nganh", type_="foreignkey")
    op.drop_index("ix_dm_chuyen_nganh_nganh", table_name="dm_chuyen_nganh")
    op.drop_column("dm_chuyen_nganh", "nganh_id")
    op.create_index("ix_dm_chuyen_nganh_ma_nganh", "dm_chuyen_nganh", ["ma_nganh"])
    op.create_foreign_key(
        "fk_dm_chuyen_nganh_nganh",
        "dm_chuyen_nganh",
        "dm_nganh_dao_tao",
        ["ma_nganh"],
        ["ma_nganh"],
        onupdate="CASCADE",
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint("fk_dm_chuyen_nganh_nganh", "dm_chuyen_nganh", type_="foreignkey")
    op.drop_index("ix_dm_chuyen_nganh_ma_nganh", table_name="dm_chuyen_nganh")
    op.add_column("dm_chuyen_nganh", sa.Column("nganh_id", sa.Integer(), nullable=True))
    op.execute(
        """
        UPDATE dm_chuyen_nganh AS chuyen
        JOIN dm_nganh_dao_tao AS nganh ON chuyen.ma_nganh = nganh.ma_nganh
        SET chuyen.nganh_id = nganh.id
        """
    )
    _require_filled("dm_chuyen_nganh", "nganh_id")
    op.alter_column(
        "dm_chuyen_nganh",
        "nganh_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.drop_column("dm_chuyen_nganh", "ma_nganh")
    op.create_index("ix_dm_chuyen_nganh_nganh", "dm_chuyen_nganh", ["nganh_id"])
    op.create_foreign_key(
        "fk_dm_chuyen_nganh_nganh",
        "dm_chuyen_nganh",
        "dm_nganh_dao_tao",
        ["nganh_id"],
        ["id"],
    )
