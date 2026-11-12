"""Tao bang ht_cau_hinh_tra_cuu.

Luu han muc tra cuu, tu van AI, phan tich truong moi ngay va cau hinh thanh toan.
Them san mot dong cau hinh mac dinh de he thong doc ngay.

Revision ID: 20261112_0045
Revises: 20261112_0044
Create Date: 2026-11-12 15:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261112_0045"
down_revision: Union[str, Sequence[str], None] = "20261112_0044"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE = "ht_cau_hinh_tra_cuu"


def _has_table(table: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(table)


def upgrade() -> None:
    if _has_table(_TABLE):
        return
    table = op.create_table(
        _TABLE,
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "so_luot_tra_cuu_mien_phi_ngay",
            sa.Integer(),
            server_default="5",
            nullable=False,
            comment="Số lượt tra cứu miễn phí mỗi ngày",
        ),
        sa.Column(
            "so_luot_tu_van_ai_ngay",
            sa.Integer(),
            server_default="10",
            nullable=False,
            comment="Số lượt tư vấn AI mỗi ngày",
        ),
        sa.Column(
            "so_luot_phan_tich_truong_ngay",
            sa.Integer(),
            server_default="3",
            nullable=False,
            comment="Số lượt phân tích trường mỗi ngày",
        ),
        sa.Column(
            "bat_tinh_nang_holland",
            sa.Boolean(),
            server_default="1",
            nullable=False,
            comment="Bật tính năng trắc nghiệm Holland",
        ),
        sa.Column("bat_thanh_toan", sa.Boolean(), server_default="0", nullable=False, comment="Bật thanh toán"),
        sa.Column(
            "gia_bao_cao_chuyen_sau",
            sa.Numeric(15, 0),
            server_default="0",
            nullable=False,
            comment="Giá báo cáo chuyên sâu (VNĐ)",
        ),
        sa.Column(
            "trang_thai",
            sa.SmallInteger(),
            server_default="1",
            nullable=False,
            comment="0: ngừng sử dụng, 1: đang áp dụng",
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.bulk_insert(
        table,
        [
            {
                "so_luot_tra_cuu_mien_phi_ngay": 5,
                "so_luot_tu_van_ai_ngay": 10,
                "so_luot_phan_tich_truong_ngay": 3,
                "bat_tinh_nang_holland": True,
                "bat_thanh_toan": False,
                "gia_bao_cao_chuyen_sau": 0,
                "trang_thai": 1,
            }
        ],
    )


def downgrade() -> None:
    if _has_table(_TABLE):
        op.drop_table(_TABLE)
