"""Đổi các cột thời gian của thu thập đề án từ giờ UTC sang múi giờ hệ thống (UTC+7, như mọi bảng khác).

Trước đây API thu thập lưu giờ UTC; nay mọi thời điểm lưu theo `TIMEZONE` (mặc định Asia/Ho_Chi_Minh), nên cộng 7 giờ
cho dữ liệu cũ.

Revision ID: 20261206_0079
Revises: 20261205_0078
Create Date: 2026-12-06 10:00:00.000000
"""

from alembic import op

revision = "20261206_0079"
down_revision = "20261205_0078"
branch_labels = None
depends_on = None

COT_THOI_GIAN = {
    "dats_phien_thu_thap": ["tao_luc", "cap_nhat_luc", "bat_dau_tao_ban_nhap_luc", "duyet_luc"],
    "dats_ban_nhap_thu_thap": ["tao_luc"],
    "dats_nhat_ky_thu_thap": ["tao_luc"],
}


def _doi_gio(so_gio: int) -> None:
    for bang, cac_cot in COT_THOI_GIAN.items():
        gan = ", ".join(f"{cot} = DATE_ADD({cot}, INTERVAL {so_gio} HOUR)" for cot in cac_cot)
        op.execute(f"UPDATE {bang} SET {gan}")


def upgrade() -> None:
    _doi_gio(7)


def downgrade() -> None:
    _doi_gio(-7)
