"""Gop dm_truong_dai_hoc vao dm_truong roi xoa bang cu.

Hoc phi trung binh duoc them vao dm_truong vi bang moi chua co cot tuong duong.
Cac cot con lai duoc map sang cot da co: khu vuc -> ten tinh thanh,
dia chi -> dia chi tru so, loai hinh dao tao -> loai hinh,
nhom nganh -> linh vuc dao tao chinh, logo/anh bia/gioi thieu/trang thai/ngay
sang cot tuong ung. Ma truong cua de an theo nam tro thanh khoa ngoai toi dm_truong.

Revision ID: 20261030_0029
Revises: 20261030_0028
Create Date: 2026-10-30 09:20:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision: str = "20261030_0029"
down_revision: Union[str, Sequence[str], None] = "20261030_0028"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(name: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(name)


def _has_column(table: str, column: str) -> bool:
    return any(item["name"] == column for item in sa.inspect(op.get_bind()).get_columns(table))


def _has_foreign_key(table: str, name: str) -> bool:
    return any(item.get("name") == name for item in sa.inspect(op.get_bind()).get_foreign_keys(table))


def upgrade() -> None:
    """Them hoc phi, chuyen du lieu neu bang cu con, roi gan khoa ngoai ma truong."""
    if not _has_column("dm_truong", "hoc_phi_trung_binh"):
        op.add_column(
            "dm_truong",
            sa.Column(
                "hoc_phi_trung_binh",
                sa.String(length=100),
                nullable=True,
                comment="Mức học phí tham khảo.",
            ),
        )
    if _has_table("dm_truong_dai_hoc"):
        _copy_legacy_schools()
        op.drop_table("dm_truong_dai_hoc")
    if not _has_foreign_key("truong_hoc_tuyen_sinh_theo_nam", "fk_tuyen_sinh_nam_ma_truong"):
        op.create_foreign_key(
            "fk_tuyen_sinh_nam_ma_truong",
            "truong_hoc_tuyen_sinh_theo_nam",
            "dm_truong",
            ["ma_truong"],
            ["ma_truong"],
            onupdate="CASCADE",
            ondelete="RESTRICT",
        )


def _copy_legacy_schools() -> None:
    op.execute(
        """
        INSERT INTO dm_truong (
            ma_truong,
            ten_truong,
            ten_viet_tat,
            ten_tieng_anh,
            loai_hinh,
            ten_tinh_thanh,
            dia_chi_tru_so,
            linh_vuc_dao_tao_chinh,
            website,
            email,
            so_dien_thoai,
            logo_url,
            anh_dai_dien_url,
            gioi_thieu_chi_tiet,
            hoc_phi_trung_binh,
            nam_thanh_lap,
            trang_thai_hoat_dong,
            tao_luc,
            cap_nhat_luc
        )
        SELECT
            ma_truong,
            ten_truong,
            NULLIF(TRIM(ten_viet_tat), ''),
            NULLIF(TRIM(ten_tieng_anh), ''),
            NULLIF(TRIM(loai_hinh_dao_tao), ''),
            NULLIF(TRIM(khu_vuc), ''),
            NULLIF(LEFT(dia_chi, 500), ''),
            CASE
                WHEN nhom_nganh IS NULL OR TRIM(nhom_nganh) = '' THEN NULL
                ELSE JSON_ARRAY(TRIM(nhom_nganh))
            END,
            NULLIF(TRIM(website), ''),
            NULLIF(TRIM(email), ''),
            NULLIF(LEFT(so_dien_thoai, 30), ''),
            NULLIF(TRIM(logo), ''),
            NULLIF(TRIM(anh_bia), ''),
            NULLIF(TRIM(gioi_thieu), ''),
            NULLIF(TRIM(hoc_phi_trung_binh), ''),
            nam_thanh_lap,
            CASE trang_thai
                WHEN 1 THEN 'Đang hoạt động'
                WHEN 0 THEN 'Ngừng hoạt động'
                ELSE NULL
            END,
            ngay_tao,
            ngay_cap_nhat
        FROM dm_truong_dai_hoc
        WHERE ma_truong NOT IN (SELECT ma_truong FROM dm_truong)
        """
    )


def downgrade() -> None:
    """Tao lai bang cu, copy du lieu da map va go khoa ngoai."""
    op.drop_constraint(
        "fk_tuyen_sinh_nam_ma_truong",
        "truong_hoc_tuyen_sinh_theo_nam",
        type_="foreignkey",
    )
    op.create_table(
        "dm_truong_dai_hoc",
        sa.Column("id", mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False),
        sa.Column("ma_truong", sa.String(20), nullable=False),
        sa.Column("ten_truong", sa.String(255), nullable=False),
        sa.Column("ten_viet_tat", sa.String(50)),
        sa.Column("ten_tieng_anh", sa.String(255)),
        sa.Column("khu_vuc", sa.String(50)),
        sa.Column("dia_chi", sa.Text()),
        sa.Column("loai_hinh_dao_tao", sa.String(50)),
        sa.Column("nhom_nganh", sa.String(100)),
        sa.Column("website", sa.String(255)),
        sa.Column("email", sa.String(100)),
        sa.Column("so_dien_thoai", sa.String(50)),
        sa.Column("logo", sa.String(255)),
        sa.Column("anh_bia", sa.String(255)),
        sa.Column("gioi_thieu", sa.Text()),
        sa.Column("hoc_phi_trung_binh", sa.String(100)),
        sa.Column("nam_thanh_lap", sa.Integer()),
        sa.Column("trang_thai", mysql.TINYINT(), nullable=False, server_default="1"),
        sa.Column("ngay_tao", mysql.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "ngay_cap_nhat",
            mysql.TIMESTAMP(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ma_truong", name="uq_dm_truong_dai_hoc_ma_truong"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.execute(
        """
        INSERT INTO dm_truong_dai_hoc (
            ma_truong,
            ten_truong,
            ten_viet_tat,
            ten_tieng_anh,
            khu_vuc,
            dia_chi,
            loai_hinh_dao_tao,
            nhom_nganh,
            website,
            email,
            so_dien_thoai,
            logo,
            anh_bia,
            gioi_thieu,
            hoc_phi_trung_binh,
            nam_thanh_lap,
            trang_thai,
            ngay_tao,
            ngay_cap_nhat
        )
        SELECT
            ma_truong,
            ten_truong,
            ten_viet_tat,
            ten_tieng_anh,
            ten_tinh_thanh,
            dia_chi_tru_so,
            loai_hinh,
            JSON_UNQUOTE(JSON_EXTRACT(linh_vuc_dao_tao_chinh, '$[0]')),
            website,
            email,
            so_dien_thoai,
            logo_url,
            anh_dai_dien_url,
            gioi_thieu_chi_tiet,
            hoc_phi_trung_binh,
            nam_thanh_lap,
            CASE WHEN trang_thai_hoat_dong = 'Ngừng hoạt động' THEN 0 ELSE 1 END,
            COALESCE(tao_luc, CURRENT_TIMESTAMP),
            COALESCE(cap_nhat_luc, CURRENT_TIMESTAMP)
        FROM dm_truong
        """
    )
    op.drop_column("dm_truong", "hoc_phi_trung_binh")
