"""create_truong_hoc_tuyen_sinh_theo_nam

Revision ID: 20261014_0025
Revises: 20261014_0024
Create Date: 2026-10-14 16:46:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision: str = "20261014_0025"
down_revision: Union[str, Sequence[str], None] = "20261014_0024"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "truong_hoc_tuyen_sinh_theo_nam",
        sa.Column("id", mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False),
        sa.Column(
            "ma_truong",
            sa.String(length=20),
            nullable=False,
            comment="Mã trường, cùng quy ước với dm_truong_dai_hoc.ma_truong",
        ),
        sa.Column(
            "ten_truong",
            sa.String(length=255),
            nullable=False,
            comment="Tên trường trong đề án năm đó",
        ),
        sa.Column(
            "loai_hinh",
            sa.String(length=50),
            nullable=True,
            comment="Loại hình trong đề án, ví dụ DaiHoc",
        ),
        sa.Column("nam_tuyen_sinh", sa.Integer(), nullable=False, comment="Năm tuyển sinh"),
        sa.Column(
            "dieu_kien_chung",
            sa.JSON(),
            nullable=True,
            comment="Điều kiện chung của trường. Mỗi phần tử có loai, toan_tu, gia_tri",
        ),
        sa.Column(
            "danh_sach_nganh",
            sa.JSON(),
            nullable=False,
            comment=(
                "Danh sách ngành. Mỗi ngành có ma_nganh, ma_xet_tuyen, ten_nganh, "
                "ten_chuong_trinh, chi_tieu_nganh, dieu_kien_nganh và phuong_thuc_tuyen_sinh"
            ),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "ma_truong",
            "nam_tuyen_sinh",
            name="uq_tuyen_sinh_nam_ma_truong_nam",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index(
        "idx_tuyen_sinh_nam_nam",
        "truong_hoc_tuyen_sinh_theo_nam",
        ["nam_tuyen_sinh"],
    )


def downgrade() -> None:
    op.drop_index("idx_tuyen_sinh_nam_nam", table_name="truong_hoc_tuyen_sinh_theo_nam")
    op.drop_table("truong_hoc_tuyen_sinh_theo_nam")
