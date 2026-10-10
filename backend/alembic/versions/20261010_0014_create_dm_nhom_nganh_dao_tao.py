"""create_dm_nhom_nganh_dao_tao

Revision ID: 20261010_0014
Revises: 20261010_0013
Create Date: 2026-10-10 13:41:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261010_0014"
down_revision: Union[str, Sequence[str], None] = "20261010_0013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dm_nhom_nganh_dao_tao",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("linh_vuc_id", sa.Integer(), nullable=False),
        sa.Column("ma_nhom_nganh", sa.String(length=20), nullable=False),
        sa.Column("ten_nhom_nganh", sa.String(length=255), nullable=False),
        sa.Column("ten_tieng_anh", sa.String(length=255), nullable=False),
        sa.Column("mo_ta", sa.Text(), nullable=True),
        sa.Column(
            "trang_thai",
            sa.SmallInteger(),
            server_default="1",
            nullable=False,
            comment="0: ngừng sử dụng, 1: hoạt động",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["linh_vuc_id"],
            ["dm_linh_vuc_dao_tao.id"],
            name="fk_dm_nhom_nganh_linh_vuc",
        ),
        sa.UniqueConstraint("ma_nhom_nganh", name="uq_dm_nhom_nganh_ma"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index("ix_dm_nhom_nganh_ten", "dm_nhom_nganh_dao_tao", ["ten_nhom_nganh"])
    op.create_index("ix_dm_nhom_nganh_ma", "dm_nhom_nganh_dao_tao", ["ma_nhom_nganh"])
    op.create_index("ix_dm_nhom_nganh_linh_vuc", "dm_nhom_nganh_dao_tao", ["linh_vuc_id"])


def downgrade() -> None:
    op.drop_index("ix_dm_nhom_nganh_linh_vuc", table_name="dm_nhom_nganh_dao_tao")
    op.drop_index("ix_dm_nhom_nganh_ma", table_name="dm_nhom_nganh_dao_tao")
    op.drop_index("ix_dm_nhom_nganh_ten", table_name="dm_nhom_nganh_dao_tao")
    op.drop_table("dm_nhom_nganh_dao_tao")
