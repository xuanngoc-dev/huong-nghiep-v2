"""create_dm_truong_dai_hoc

Revision ID: 20261014_0024
Revises: 20261012_0023
Create Date: 2026-10-14 15:54:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision: str = "20261014_0024"
down_revision: Union[str, Sequence[str], None] = "20261012_0023"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dm_truong_dai_hoc",
        sa.Column("id", mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False),
        sa.Column(
            "ma_truong",
            sa.String(length=20),
            nullable=False,
            comment="Mã trường (Bộ GD&ĐT)",
        ),
        sa.Column(
            "ten_truong",
            sa.String(length=255),
            nullable=False,
            comment="Tên đầy đủ tiếng Việt",
        ),
        sa.Column(
            "ten_viet_tat",
            sa.String(length=50),
            nullable=True,
            comment="Tên viết tắt (HUST, NEU...)",
        ),
        sa.Column(
            "ten_tieng_anh",
            sa.String(length=255),
            nullable=True,
            comment="Tên tiếng Anh",
        ),
        sa.Column(
            "khu_vuc",
            sa.String(length=50),
            nullable=True,
            comment="Tỉnh/Thành phố hoặc miền",
        ),
        sa.Column("dia_chi", sa.Text(), nullable=True, comment="Địa chỉ cơ sở chính"),
        sa.Column(
            "loai_hinh_dao_tao",
            sa.String(length=50),
            nullable=True,
            comment="Công lập, Tư thục, Quốc tế...",
        ),
        sa.Column(
            "nhom_nganh",
            sa.String(length=100),
            nullable=True,
            comment="Khối ngành chính",
        ),
        sa.Column("website", sa.String(length=255), nullable=True, comment="Link website"),
        sa.Column("email", sa.String(length=100), nullable=True, comment="Email liên hệ"),
        sa.Column("so_dien_thoai", sa.String(length=50), nullable=True, comment="Hotline"),
        sa.Column("logo", sa.String(length=255), nullable=True, comment="URL Logo trường"),
        sa.Column("anh_bia", sa.String(length=255), nullable=True, comment="URL ảnh bìa/campus"),
        sa.Column(
            "gioi_thieu",
            mysql.LONGTEXT(),
            nullable=True,
            comment="Mô tả chi tiết/Lịch sử",
        ),
        sa.Column(
            "hoc_phi_trung_binh",
            sa.String(length=100),
            nullable=True,
            comment="Mức học phí tham khảo",
        ),
        sa.Column("nam_thanh_lap", sa.Integer(), nullable=True, comment="Năm thành lập"),
        sa.Column(
            "trang_thai",
            mysql.TINYINT(),
            server_default="1",
            nullable=False,
            comment="1: Hoạt động, 0: Khóa",
        ),
        sa.Column(
            "ngay_tao",
            mysql.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "ngay_cap_nhat",
            mysql.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ma_truong", name="uq_dm_truong_dai_hoc_ma_truong"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index("idx_ma_truong", "dm_truong_dai_hoc", ["ma_truong"])
    op.create_index("idx_ten_truong", "dm_truong_dai_hoc", ["ten_truong"])
    op.create_index("idx_khu_vuc", "dm_truong_dai_hoc", ["khu_vuc"])


def downgrade() -> None:
    op.drop_index("idx_khu_vuc", table_name="dm_truong_dai_hoc")
    op.drop_index("idx_ten_truong", table_name="dm_truong_dai_hoc")
    op.drop_index("idx_ma_truong", table_name="dm_truong_dai_hoc")
    op.drop_table("dm_truong_dai_hoc")
