"""Bỏ trạng thái lưu trữ (`luu_tru`) của phiên trò chuyện: phiên đang lưu trữ chuyển thành đã kết thúc (`da_dong`).

Revision ID: 20261205_0078
Revises: 20261204_0077
Create Date: 2026-12-05 10:00:00.000000
"""

from alembic import op

revision = "20261205_0078"
down_revision = "20261204_0077"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE chat_conversations SET trang_thai = 'da_dong' WHERE trang_thai = 'luu_tru'")
    op.execute(
        "ALTER TABLE chat_conversations MODIFY trang_thai "
        "ENUM('dang_hoat_dong', 'da_dong') NOT NULL DEFAULT 'dang_hoat_dong'"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE chat_conversations MODIFY trang_thai "
        "ENUM('dang_hoat_dong', 'da_dong', 'luu_tru') NOT NULL DEFAULT 'dang_hoat_dong'"
    )
