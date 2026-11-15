"""Tao bang ht_cau_hinh_goi_cuoc.

Luu cac goi cuoc (gia goc, gia khuyen mai, so luot nhan duoc) theo loai ap dung.

Revision ID: 20261115_0052
Revises: 20261113_0051
Create Date: 2026-11-15 12:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261115_0052"
down_revision: Union[str, Sequence[str], None] = "20261113_0051"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE = "ht_cau_hinh_goi_cuoc"


def _has_table(table: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(table)


def upgrade() -> None:
    if _has_table(_TABLE):
        return
    op.create_table(
        _TABLE,
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ma_goi_cuoc", sa.String(length=50), nullable=False, comment="Mã gói cước"),
        sa.Column("ten_goi_cuoc", sa.String(length=255), nullable=False, comment="Tên gói cước"),
        sa.Column(
            "loai_ap_dung",
            sa.String(length=50),
            nullable=False,
            comment="tra_cuu: tra cứu, khao_sat: khảo sát, hoi_dap: hỏi đáp",
        ),
        sa.Column("gia_goc", sa.Numeric(15, 0), server_default="0", nullable=False, comment="Giá gốc (VNĐ)"),
        sa.Column("gia_khuyen_mai", sa.Numeric(15, 0), nullable=True, comment="Giá khuyến mãi (VNĐ)"),
        sa.Column(
            "so_luot_nhan_duoc_goc",
            sa.Integer(),
            server_default="0",
            nullable=False,
            comment="Số lượt nhận được theo giá gốc",
        ),
        sa.Column(
            "so_luot_nhan_duoc_khuyen_mai",
            sa.Integer(),
            nullable=True,
            comment="Số lượt nhận được khi khuyến mãi",
        ),
        sa.Column(
            "trang_thai",
            sa.SmallInteger(),
            server_default="1",
            nullable=False,
            comment="0: ngừng sử dụng, 1: hoạt động",
        ),
        sa.Column("ghi_chu", sa.Text(), nullable=True, comment="Ghi chú"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ma_goi_cuoc", name="uq_ht_cau_hinh_goi_cuoc_ma_goi_cuoc"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index("ix_ht_cau_hinh_goi_cuoc_ten_goi_cuoc", _TABLE, ["ten_goi_cuoc"])
    op.create_index("ix_ht_cau_hinh_goi_cuoc_loai_ap_dung", _TABLE, ["loai_ap_dung"])


def downgrade() -> None:
    if _has_table(_TABLE):
        op.drop_table(_TABLE)
