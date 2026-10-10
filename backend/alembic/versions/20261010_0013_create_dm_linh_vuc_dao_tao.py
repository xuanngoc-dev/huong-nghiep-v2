"""create_dm_linh_vuc_dao_tao

Revision ID: 20261010_0013
Revises: 20261010_0012
Create Date: 2026-10-10 13:40:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261010_0013"
down_revision: Union[str, Sequence[str], None] = "20261010_0012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dm_linh_vuc_dao_tao",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ma_linh_vuc", sa.String(length=20), nullable=False),
        sa.Column("ten_linh_vuc", sa.String(length=255), nullable=False),
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
        sa.UniqueConstraint("ma_linh_vuc", name="uq_dm_linh_vuc_ma"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index("ix_dm_linh_vuc_ten", "dm_linh_vuc_dao_tao", ["ten_linh_vuc"])
    op.create_index("ix_dm_linh_vuc_ma", "dm_linh_vuc_dao_tao", ["ma_linh_vuc"])


def downgrade() -> None:
    op.drop_index("ix_dm_linh_vuc_ma", table_name="dm_linh_vuc_dao_tao")
    op.drop_index("ix_dm_linh_vuc_ten", table_name="dm_linh_vuc_dao_tao")
    op.drop_table("dm_linh_vuc_dao_tao")
