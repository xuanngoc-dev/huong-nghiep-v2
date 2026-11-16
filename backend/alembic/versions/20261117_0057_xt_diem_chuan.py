"""Tao bang xt_diem_chuan (buoc 1.6 KE_HOACH_TRIEN_KHAI.md).

Diem trung tuyen cac nam theo ma truong + ma xet tuyen + nam, lam moc so sanh khi tim truong phu hop.

Revision ID: 20261117_0057
Revises: 20261116_0056
Create Date: 2026-11-17 09:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT

revision: str = "20261117_0057"
down_revision: Union[str, Sequence[str], None] = "20261116_0056"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE = "xt_diem_chuan"


def _has_table(table: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(table)


def upgrade() -> None:
    if _has_table(_TABLE):
        return
    op.create_table(
        _TABLE,
        sa.Column("id", BIGINT(unsigned=True), autoincrement=True, nullable=False),
        sa.Column("ma_truong", sa.String(length=20), nullable=False, comment="FK dm_truong.ma_truong."),
        sa.Column("nam_tuyen_sinh", SMALLINT(unsigned=True), nullable=False),
        sa.Column(
            "ma_xet_tuyen",
            sa.String(length=20),
            nullable=False,
            comment="Mã xét tuyển năm đó; dùng để nối với chương trình của đề án hiện hành.",
        ),
        sa.Column("ten_chuong_trinh", sa.String(length=255), nullable=True),
        sa.Column(
            "ma_phuong_thuc_cua_bo",
            sa.String(length=20),
            nullable=True,
            comment="NULL = điểm chuẩn chung mọi phương thức.",
        ),
        sa.Column("to_hop_id", sa.Integer(), nullable=True, comment="NULL = chung mọi tổ hợp."),
        sa.Column("diem_chuan", sa.Numeric(7, 2), nullable=False),
        sa.Column("thang_diem", sa.Numeric(6, 2), server_default="30.00", nullable=False),
        sa.Column("tieu_chi_phu", sa.String(length=255), nullable=True),
        sa.Column("nguon_du_lieu_url", sa.String(length=1000), nullable=True),
        sa.Column("ghi_chu", sa.Text(), nullable=True),
        sa.Column("tao_luc", sa.DateTime(), nullable=True, comment="Thời điểm tạo bản ghi."),
        sa.Column("cap_nhat_luc", sa.DateTime(), nullable=True, comment="Thời điểm cập nhật gần nhất."),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["ma_truong"], ["dm_truong.ma_truong"], name="fk_xt_diem_chuan_ma_truong", onupdate="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["ma_phuong_thuc_cua_bo"],
            ["dm_phuong_thuc_tuyen_sinh.ma_phuong_thuc"],
            name="fk_xt_diem_chuan_ma_phuong_thuc",
        ),
        sa.ForeignKeyConstraint(["to_hop_id"], ["dm_to_hop_mon_hoc.id"], name="fk_xt_diem_chuan_to_hop_id"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Điểm trúng tuyển các năm, làm mốc so sánh",
    )
    op.create_index("idx_xt_diem_chuan_tra_cuu", _TABLE, ["ma_truong", "ma_xet_tuyen", "nam_tuyen_sinh"])
    op.create_index("idx_xt_diem_chuan_to_hop_id", _TABLE, ["to_hop_id"])
    op.create_index("idx_xt_diem_chuan_ma_phuong_thuc", _TABLE, ["ma_phuong_thuc_cua_bo"])


def downgrade() -> None:
    if _has_table(_TABLE):
        op.drop_table(_TABLE)
