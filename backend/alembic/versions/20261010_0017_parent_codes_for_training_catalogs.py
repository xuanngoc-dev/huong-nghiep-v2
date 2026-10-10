"""store parent codes instead of ids

Revision ID: 20261010_0017
Revises: 20261010_0016
Create Date: 2026-10-10 13:56:00.000000

dm_nhom_nganh_dao_tao.linh_vuc_id -> ma_linh_vuc
dm_nganh_dao_tao.nhom_nganh_id -> ma_nhom_nganh
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261010_0017"
down_revision: Union[str, Sequence[str], None] = "20261010_0016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _require_filled(table: str, column: str) -> None:
    missing = op.get_bind().execute(sa.text(f"SELECT COUNT(*) FROM {table} WHERE {column} IS NULL")).scalar()
    if missing:
        raise RuntimeError(f"Không đổi được {table}.{column}: còn {missing} dòng chưa có mã cha")


def upgrade() -> None:
    op.add_column(
        "dm_nganh_dao_tao",
        sa.Column("ma_nhom_nganh", sa.String(length=20), nullable=True),
    )
    op.execute(
        """
        UPDATE dm_nganh_dao_tao AS nganh
        JOIN dm_nhom_nganh_dao_tao AS nhom ON nganh.nhom_nganh_id = nhom.id
        SET nganh.ma_nhom_nganh = nhom.ma_nhom_nganh
        """
    )
    _require_filled("dm_nganh_dao_tao", "ma_nhom_nganh")
    op.alter_column(
        "dm_nganh_dao_tao",
        "ma_nhom_nganh",
        existing_type=sa.String(length=20),
        nullable=False,
    )
    op.drop_constraint("fk_dm_nganh_nhom_nganh", "dm_nganh_dao_tao", type_="foreignkey")
    op.drop_index("ix_dm_nganh_nhom", table_name="dm_nganh_dao_tao")
    op.drop_column("dm_nganh_dao_tao", "nhom_nganh_id")
    op.create_index("ix_dm_nganh_ma_nhom", "dm_nganh_dao_tao", ["ma_nhom_nganh"])
    op.create_foreign_key(
        "fk_dm_nganh_nhom_nganh",
        "dm_nganh_dao_tao",
        "dm_nhom_nganh_dao_tao",
        ["ma_nhom_nganh"],
        ["ma_nhom_nganh"],
        onupdate="CASCADE",
        ondelete="RESTRICT",
    )

    op.add_column(
        "dm_nhom_nganh_dao_tao",
        sa.Column("ma_linh_vuc", sa.String(length=20), nullable=True),
    )
    op.execute(
        """
        UPDATE dm_nhom_nganh_dao_tao AS nhom
        JOIN dm_linh_vuc_dao_tao AS linh_vuc ON nhom.linh_vuc_id = linh_vuc.id
        SET nhom.ma_linh_vuc = linh_vuc.ma_linh_vuc
        """
    )
    _require_filled("dm_nhom_nganh_dao_tao", "ma_linh_vuc")
    op.alter_column(
        "dm_nhom_nganh_dao_tao",
        "ma_linh_vuc",
        existing_type=sa.String(length=20),
        nullable=False,
    )
    op.drop_constraint("fk_dm_nhom_nganh_linh_vuc", "dm_nhom_nganh_dao_tao", type_="foreignkey")
    op.drop_index("ix_dm_nhom_nganh_linh_vuc", table_name="dm_nhom_nganh_dao_tao")
    op.drop_column("dm_nhom_nganh_dao_tao", "linh_vuc_id")
    op.create_index("ix_dm_nhom_nganh_ma_linh_vuc", "dm_nhom_nganh_dao_tao", ["ma_linh_vuc"])
    op.create_foreign_key(
        "fk_dm_nhom_nganh_linh_vuc",
        "dm_nhom_nganh_dao_tao",
        "dm_linh_vuc_dao_tao",
        ["ma_linh_vuc"],
        ["ma_linh_vuc"],
        onupdate="CASCADE",
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint("fk_dm_nhom_nganh_linh_vuc", "dm_nhom_nganh_dao_tao", type_="foreignkey")
    op.drop_index("ix_dm_nhom_nganh_ma_linh_vuc", table_name="dm_nhom_nganh_dao_tao")
    op.add_column("dm_nhom_nganh_dao_tao", sa.Column("linh_vuc_id", sa.Integer(), nullable=True))
    op.execute(
        """
        UPDATE dm_nhom_nganh_dao_tao AS nhom
        JOIN dm_linh_vuc_dao_tao AS linh_vuc ON nhom.ma_linh_vuc = linh_vuc.ma_linh_vuc
        SET nhom.linh_vuc_id = linh_vuc.id
        """
    )
    _require_filled("dm_nhom_nganh_dao_tao", "linh_vuc_id")
    op.alter_column(
        "dm_nhom_nganh_dao_tao",
        "linh_vuc_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.drop_column("dm_nhom_nganh_dao_tao", "ma_linh_vuc")
    op.create_index("ix_dm_nhom_nganh_linh_vuc", "dm_nhom_nganh_dao_tao", ["linh_vuc_id"])
    op.create_foreign_key(
        "fk_dm_nhom_nganh_linh_vuc",
        "dm_nhom_nganh_dao_tao",
        "dm_linh_vuc_dao_tao",
        ["linh_vuc_id"],
        ["id"],
    )

    op.drop_constraint("fk_dm_nganh_nhom_nganh", "dm_nganh_dao_tao", type_="foreignkey")
    op.drop_index("ix_dm_nganh_ma_nhom", table_name="dm_nganh_dao_tao")
    op.add_column("dm_nganh_dao_tao", sa.Column("nhom_nganh_id", sa.Integer(), nullable=True))
    op.execute(
        """
        UPDATE dm_nganh_dao_tao AS nganh
        JOIN dm_nhom_nganh_dao_tao AS nhom ON nganh.ma_nhom_nganh = nhom.ma_nhom_nganh
        SET nganh.nhom_nganh_id = nhom.id
        """
    )
    _require_filled("dm_nganh_dao_tao", "nhom_nganh_id")
    op.alter_column(
        "dm_nganh_dao_tao",
        "nhom_nganh_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.drop_column("dm_nganh_dao_tao", "ma_nhom_nganh")
    op.create_index("ix_dm_nganh_nhom", "dm_nganh_dao_tao", ["nhom_nganh_id"])
    op.create_foreign_key(
        "fk_dm_nganh_nhom_nganh",
        "dm_nganh_dao_tao",
        "dm_nhom_nganh_dao_tao",
        ["nhom_nganh_id"],
        ["id"],
    )
