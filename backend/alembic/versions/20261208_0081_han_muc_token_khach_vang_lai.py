"""Hạn mức token AI miễn phí cho khách vãng lai.

- ht_cau_hinh_enduser.so_token_khach_vang_lai: số token khách được dùng khi chat (null = không giới hạn).
- chat_messages.tong_token: tổng token cả lượt (lập kế hoạch + trả lời) để cộng dồn token khách đã dùng.

Revision ID: 20261208_0081
Revises: 20261207_0080
Create Date: 2026-12-08 10:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "20261208_0081"
down_revision = "20261207_0080"
branch_labels = None
depends_on = None


def _co_cot(bang: str, cot: str) -> bool:
    return cot in {c["name"] for c in sa.inspect(op.get_bind()).get_columns(bang)}


def upgrade() -> None:
    if not _co_cot("ht_cau_hinh_enduser", "so_token_khach_vang_lai"):
        op.add_column(
            "ht_cau_hinh_enduser",
            sa.Column(
                "so_token_khach_vang_lai",
                sa.Integer(),
                nullable=True,
                comment="Số token AI miễn phí cho khách vãng lai; null = không giới hạn",
            ),
        )
    if not _co_cot("chat_messages", "tong_token"):
        op.add_column(
            "chat_messages",
            sa.Column("tong_token", sa.Integer(), nullable=True, comment="Tổng token cả lượt (lập kế hoạch + trả lời)"),
        )


def downgrade() -> None:
    if _co_cot("chat_messages", "tong_token"):
        op.drop_column("chat_messages", "tong_token")
    if _co_cot("ht_cau_hinh_enduser", "so_token_khach_vang_lai"):
        op.drop_column("ht_cau_hinh_enduser", "so_token_khach_vang_lai")
