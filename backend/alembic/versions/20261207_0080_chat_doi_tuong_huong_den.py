"""Thêm cột doi_tuong_huong_den (đối tượng hướng đến) vào chat_conversations.

Phiên cũ nhận mặc định 'thpt-thi-dai-hoc' (trước đây trợ lý chỉ trả lời cho học sinh THPT thi đại học).

Revision ID: 20261207_0080
Revises: 20261206_0079
Create Date: 2026-12-07 10:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "20261207_0080"
down_revision = "20261206_0079"
branch_labels = None
depends_on = None


def _co_cot(bang: str, cot: str) -> bool:
    return cot in {c["name"] for c in sa.inspect(op.get_bind()).get_columns(bang)}


def upgrade() -> None:
    if _co_cot("chat_conversations", "doi_tuong_huong_den"):
        return
    op.add_column(
        "chat_conversations",
        sa.Column(
            "doi_tuong_huong_den",
            sa.String(50),
            nullable=False,
            server_default="thpt-thi-dai-hoc",
            comment="Đối tượng hướng đến (học sinh THPT thi ĐH, phụ huynh, học sinh THCS...)",
        ),
    )


def downgrade() -> None:
    if _co_cot("chat_conversations", "doi_tuong_huong_den"):
        op.drop_column("chat_conversations", "doi_tuong_huong_den")
