"""create_nguoi_dung_table

Revision ID: 20261009_0001
Revises:
Create Date: 2026-10-09 15:54:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261009_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "nguoi_dung",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ho_ten", sa.String(length=150), nullable=False),
        sa.Column("so_dien_thoai", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("mat_khau", sa.String(length=255), nullable=False),
        sa.Column(
            "vai_tro",
            sa.SmallInteger(),
            server_default="0",
            nullable=False,
            comment="0: người dùng, 1: admin",
        ),
        sa.Column(
            "trang_thai",
            sa.SmallInteger(),
            server_default="1",
            nullable=False,
            comment="0: khóa, 1: hoạt động",
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
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("so_dien_thoai"),
    )
    op.create_index("ix_nguoi_dung_email", "nguoi_dung", ["email"])
    op.create_index("ix_nguoi_dung_so_dien_thoai", "nguoi_dung", ["so_dien_thoai"])


def downgrade() -> None:
    op.drop_index("ix_nguoi_dung_so_dien_thoai", table_name="nguoi_dung")
    op.drop_index("ix_nguoi_dung_email", table_name="nguoi_dung")
    op.drop_table("nguoi_dung")
