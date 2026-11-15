"""Tao bang ht_lich_su_giao_dich_ngan_hang.

Luu bien dong so du (tien vao/ra) cac tai khoan ngan hang nhan qua webhook (SePay),
kem ket qua doi soat voi ht_lich_su_nap_tien.

Revision ID: 20261115_0055
Revises: 20261115_0054
Create Date: 2026-11-15 18:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261115_0055"
down_revision: Union[str, Sequence[str], None] = "20261115_0054"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE = "ht_lich_su_giao_dich_ngan_hang"


def _has_table(table: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(table)


def upgrade() -> None:
    if _has_table(_TABLE):
        return
    op.create_table(
        _TABLE,
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ma_giao_dich_cong", sa.String(length=64), nullable=False, comment="id giao dịch phía cổng (SePay)"),
        sa.Column("ngan_hang", sa.String(length=100), nullable=True, comment="Tên ngân hàng (gateway)"),
        sa.Column("thoi_gian_giao_dich", sa.DateTime(), nullable=True, comment="Thời gian giao dịch"),
        sa.Column("so_tai_khoan", sa.String(length=50), nullable=True, comment="Số tài khoản"),
        sa.Column("tai_khoan_phu", sa.String(length=50), nullable=True, comment="Tài khoản phụ"),
        sa.Column("ma_thanh_toan", sa.String(length=100), nullable=True, comment="Mã thanh toán (code)"),
        sa.Column("noi_dung", sa.Text(), nullable=True, comment="Nội dung chuyển khoản"),
        sa.Column("loai_giao_dich", sa.String(length=10), nullable=False, comment="in: tiền vào, out: tiền ra"),
        sa.Column("mo_ta", sa.Text(), nullable=True, comment="Mô tả (description)"),
        sa.Column("so_tien", sa.Numeric(18, 0), nullable=False, comment="Số tiền giao dịch"),
        sa.Column("so_du_luy_ke", sa.Numeric(18, 0), nullable=True, comment="Số dư lũy kế"),
        sa.Column("ma_tham_chieu", sa.String(length=100), nullable=True, comment="Mã tham chiếu ngân hàng"),
        sa.Column("ngan_hang_thanh_toan_id", sa.Integer(), nullable=True, comment="Tài khoản nhận tiền khớp"),
        sa.Column("lich_su_nap_tien_id", sa.Integer(), nullable=True, comment="Giao dịch nạp tiền được đối soát"),
        sa.Column(
            "trang_thai_doi_soat",
            sa.SmallInteger(),
            server_default="0",
            nullable=False,
            comment="0: chưa khớp, 1: đã khớp và cộng số dư, 2: tiền ra, 3: khớp nhưng thiếu tiền",
        ),
        sa.Column("ghi_chu_doi_soat", sa.String(length=500), nullable=True, comment="Ghi chú đối soát"),
        sa.Column("du_lieu_goc", sa.JSON(), nullable=True, comment="Payload webhook gốc"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ma_giao_dich_cong", name="uq_ht_lich_su_giao_dich_ngan_hang_ma_cong"),
        sa.ForeignKeyConstraint(
            ["ngan_hang_thanh_toan_id"],
            ["ht_ngan_hang_thanh_toan.id"],
            name="fk_ht_gd_ngan_hang_ngan_hang",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["lich_su_nap_tien_id"],
            ["ht_lich_su_nap_tien.id"],
            name="fk_ht_gd_ngan_hang_nap_tien",
            ondelete="SET NULL",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    for column in (
        "thoi_gian_giao_dich",
        "so_tai_khoan",
        "ma_thanh_toan",
        "loai_giao_dich",
        "ma_tham_chieu",
        "lich_su_nap_tien_id",
        "trang_thai_doi_soat",
        "created_at",
    ):
        op.create_index(f"ix_{_TABLE}_{column}", _TABLE, [column])


def downgrade() -> None:
    if _has_table(_TABLE):
        op.drop_table(_TABLE)
