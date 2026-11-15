"""Tao bang ht_lich_su_nap_tien.

Luu lich su nap tien/dang ky goi cuoc cua nguoi dung: ban chup goi, so tien,
tai khoan nhan tien, noi dung chuyen khoan va trang thai doi soat.

Revision ID: 20261115_0054
Revises: 20261115_0053
Create Date: 2026-11-15 17:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261115_0054"
down_revision: Union[str, Sequence[str], None] = "20261115_0053"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE = "ht_lich_su_nap_tien"


def _has_table(table: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(table)


def upgrade() -> None:
    if _has_table(_TABLE):
        return
    op.create_table(
        _TABLE,
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ma_giao_dich", sa.String(length=50), nullable=False, comment="Mã giao dịch nội bộ, duy nhất"),
        sa.Column("nguoi_dung_id", sa.Integer(), nullable=True, comment="Người nạp"),
        sa.Column("goi_cuoc_dang_ky_id", sa.Integer(), nullable=True, comment="Gói cước đăng ký"),
        sa.Column("ma_goi_cuoc", sa.String(length=50), nullable=False, comment="Mã gói lúc đăng ký"),
        sa.Column("ten_goi_cuoc", sa.String(length=255), nullable=False, comment="Tên gói lúc đăng ký"),
        sa.Column(
            "loai_ap_dung",
            sa.String(length=50),
            nullable=False,
            comment="edu_coin, tra_cuu, khao_sat, hoi_dap",
        ),
        sa.Column(
            "so_luot_nhan_duoc",
            sa.Integer(),
            server_default="0",
            nullable=False,
            comment="Số Edu coin/lượt được cộng khi thành công",
        ),
        sa.Column("so_tien_nap", sa.Numeric(15, 0), nullable=False, comment="Số tiền phải nạp (VNĐ)"),
        sa.Column("so_tien_thuc_nhan", sa.Numeric(15, 0), nullable=True, comment="Số tiền thực nhận (VNĐ)"),
        sa.Column("ngan_hang_thanh_toan_id", sa.Integer(), nullable=True, comment="Tài khoản nhận tiền"),
        sa.Column("ten_ngan_hang_viet_tat", sa.String(length=50), nullable=True, comment="Ngân hàng nhận"),
        sa.Column("so_tai_khoan_nhan", sa.String(length=50), nullable=True, comment="Số tài khoản nhận"),
        sa.Column("chu_tai_khoan_nhan", sa.String(length=255), nullable=True, comment="Chủ tài khoản nhận"),
        sa.Column("noi_dung_chuyen_khoan", sa.String(length=255), nullable=True, comment="Nội dung chuyển khoản"),
        sa.Column(
            "ma_tham_chieu_ngan_hang",
            sa.String(length=100),
            nullable=True,
            comment="Mã tham chiếu trên sao kê ngân hàng",
        ),
        sa.Column(
            "trang_thai",
            sa.SmallInteger(),
            server_default="0",
            nullable=False,
            comment="0: chờ thanh toán, 1: thành công, 2: đã hủy, 3: thất bại",
        ),
        sa.Column("thoi_gian_thanh_toan", sa.DateTime(), nullable=True, comment="Thời điểm người dùng chuyển khoản"),
        sa.Column("thoi_gian_xac_nhan", sa.DateTime(), nullable=True, comment="Thời điểm admin xác nhận"),
        sa.Column("nguoi_xac_nhan_id", sa.Integer(), nullable=True, comment="Admin xác nhận"),
        sa.Column("ghi_chu", sa.Text(), nullable=True, comment="Ghi chú"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ma_giao_dich", name="uq_ht_lich_su_nap_tien_ma_giao_dich"),
        sa.ForeignKeyConstraint(
            ["nguoi_dung_id"], ["nguoi_dung.id"], name="fk_ht_lich_su_nap_tien_nguoi_dung", ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["goi_cuoc_dang_ky_id"],
            ["ht_cau_hinh_goi_cuoc.id"],
            name="fk_ht_lich_su_nap_tien_goi_cuoc",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["ngan_hang_thanh_toan_id"],
            ["ht_ngan_hang_thanh_toan.id"],
            name="fk_ht_lich_su_nap_tien_ngan_hang",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["nguoi_xac_nhan_id"],
            ["nguoi_dung.id"],
            name="fk_ht_lich_su_nap_tien_nguoi_xac_nhan",
            ondelete="SET NULL",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    for column in (
        "nguoi_dung_id",
        "goi_cuoc_dang_ky_id",
        "loai_ap_dung",
        "ma_tham_chieu_ngan_hang",
        "trang_thai",
        "created_at",
    ):
        op.create_index(f"ix_{_TABLE}_{column}", _TABLE, [column])


def downgrade() -> None:
    if _has_table(_TABLE):
        op.drop_table(_TABLE)
