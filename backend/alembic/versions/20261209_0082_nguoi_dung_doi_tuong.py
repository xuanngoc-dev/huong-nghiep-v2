"""Đối tượng người dùng tự chọn khi đăng ký.

- nguoi_dung.doi_tuong: mã đối tượng hướng đến (app/constants/doi_tuong_huong_den.py, cùng mã với
  chat_conversations.doi_tuong_huong_den), trợ lý chat dùng cố định cho tài khoản. Null với tài khoản cũ.

Revision ID: 20261209_0082
Revises: 20261208_0081
Create Date: 2026-12-09 10:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "20261209_0082"
down_revision = "20261208_0081"
branch_labels = None
depends_on = None


def _co_cot(bang: str, cot: str) -> bool:
    return cot in {c["name"] for c in sa.inspect(op.get_bind()).get_columns(bang)}


def upgrade() -> None:
    if not _co_cot("nguoi_dung", "doi_tuong"):
        op.add_column(
            "nguoi_dung",
            sa.Column(
                "doi_tuong",
                sa.String(50),
                nullable=True,
                comment="Đối tượng hướng đến chọn khi đăng ký (mã như chat_conversations.doi_tuong_huong_den)",
            ),
        )


def downgrade() -> None:
    if _co_cot("nguoi_dung", "doi_tuong"):
        op.drop_column("nguoi_dung", "doi_tuong")
