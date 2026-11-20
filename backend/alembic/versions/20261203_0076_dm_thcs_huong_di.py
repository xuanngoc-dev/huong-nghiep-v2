"""Tạo danh mục hướng đi sau THCS: hướng đi, ưu/nhược điểm, tiêu chí, mức phù hợp theo tiêu chí, lời khuyên lưu ý.

Revision ID: 20261203_0076
Revises: 20261202_0075
Create Date: 2026-12-03 10:00:00.000000
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.mysql import TINYINT

revision = "20261203_0076"
down_revision = "20261202_0075"
branch_labels = None
depends_on = None

_BANG = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}

MUC_DO_AP_LUC_HOC_TAP = ("thap", "trung_binh", "cao")
MUC_DO_TU_GIAC = ("trung_binh", "cao", "rat_cao")
LOAI_UU_NHUOC_DIEM = ("uu_diem", "nhuoc_diem")
DOI_TUONG_NHAN_LUU_Y = ("hoc_sinh", "phu_huynh", "ca_hai")


def _cot_huong_di(ten_fk: str, **kwargs):
    return sa.Column(
        "thcs_huong_di_id",
        sa.Integer(),
        sa.ForeignKey("dm_thcs_huong_di.id", name=ten_fk, ondelete="CASCADE"),
        nullable=False,
        **kwargs,
    )


def upgrade() -> None:
    op.create_table(
        "dm_thcs_huong_di",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("ma_huong", sa.String(50), nullable=False),
        sa.Column("ten_huong", sa.String(255), nullable=False),
        sa.Column("mo_ta_tong_quan", sa.Text(), nullable=False),
        sa.Column("doi_tuong_phu_hop", sa.Text(), nullable=True),
        sa.Column("chi_phi_du_kien_text", sa.String(255), nullable=True),
        sa.Column("chi_phi_thang_min", sa.Numeric(10, 2), nullable=True),
        sa.Column("chi_phi_thang_max", sa.Numeric(10, 2), nullable=True),
        sa.Column(
            "muc_do_ap_luc_hoc_tap",
            sa.Enum(*MUC_DO_AP_LUC_HOC_TAP, name="muc_do_ap_luc_hoc_tap"),
            nullable=True,
            server_default="trung_binh",
        ),
        sa.Column(
            "muc_do_tu_giac_can_thiet",
            sa.Enum(*MUC_DO_TU_GIAC, name="muc_do_tu_giac_can_thiet"),
            nullable=True,
            server_default="cao",
        ),
        sa.Column("tinh_linh_hoat_sau_lop_12", sa.Text(), nullable=True),
        sa.Column("ma_holland", sa.String(20), nullable=True),
        sa.Column("thu_tu_hien_thi", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("trang_thai", TINYINT(1), nullable=False, server_default="1"),
        sa.Column("ngay_tao", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "ngay_cap_nhat",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
        **_BANG,
    )
    op.create_index("ix_dm_thcs_huong_di_ma_huong", "dm_thcs_huong_di", ["ma_huong"], unique=True)

    op.create_table(
        "dm_thcs_uu_nhuoc_diem",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        _cot_huong_di("fk_dm_tund_huong_di_id"),
        sa.Column("loai", sa.Enum(*LOAI_UU_NHUOC_DIEM, name="loai_uu_nhuoc_diem"), nullable=False),
        sa.Column("tieu_de", sa.String(255), nullable=False),
        sa.Column("noi_dung_chi_tiet", sa.Text(), nullable=False),
        sa.Column("thu_tu_hien_thi", sa.Integer(), nullable=False, server_default="0"),
        **_BANG,
    )
    op.create_index("ix_dm_thcs_uu_nhuoc_diem_thcs_huong_di_id", "dm_thcs_uu_nhuoc_diem", ["thcs_huong_di_id"])

    op.create_table(
        "dm_thcs_tieu_chi",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("ma_tieu_chi", sa.String(50), nullable=False),
        sa.Column("ten_tieu_chi", sa.String(255), nullable=False),
        sa.Column("mo_ta_tieu_chi", sa.String(255), nullable=True),
        sa.Column("nhom_tieu_chi", sa.String(100), nullable=True),
        sa.Column("thu_tu_hien_thi", sa.Integer(), nullable=False, server_default="0"),
        **_BANG,
    )
    op.create_index("ix_dm_thcs_tieu_chi_ma_tieu_chi", "dm_thcs_tieu_chi", ["ma_tieu_chi"], unique=True)

    op.create_table(
        "dm_thcs_huong_di_tieu_chi",
        _cot_huong_di("fk_dm_thdtc_huong_di_id", primary_key=True),
        sa.Column(
            "thcs_tieu_chi_id",
            sa.Integer(),
            sa.ForeignKey("dm_thcs_tieu_chi.id", name="fk_dm_thdtc_tieu_chi_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("diem_phu_hop", TINYINT(), nullable=False, server_default="3"),
        sa.Column("nhan_dinh_tu_van", sa.String(255), nullable=True),
        sa.CheckConstraint("diem_phu_hop BETWEEN 1 AND 5", name="chk_dm_thcs_huong_di_tieu_chi_diem"),
        **_BANG,
    )
    op.create_index(
        "ix_dm_thcs_huong_di_tieu_chi_thcs_tieu_chi_id", "dm_thcs_huong_di_tieu_chi", ["thcs_tieu_chi_id"]
    )

    op.create_table(
        "dm_thcs_loi_khuyen_luu_y",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        _cot_huong_di("fk_dm_tlkly_huong_di_id"),
        sa.Column(
            "doi_tuong_nhan",
            sa.Enum(*DOI_TUONG_NHAN_LUU_Y, name="doi_tuong_nhan_luu_y"),
            nullable=True,
            server_default="ca_hai",
        ),
        sa.Column("noi_dung_luu_y", sa.Text(), nullable=False),
        sa.Column("thu_tu_hien_thi", sa.Integer(), nullable=False, server_default="0"),
        **_BANG,
    )
    op.create_index(
        "ix_dm_thcs_loi_khuyen_luu_y_thcs_huong_di_id", "dm_thcs_loi_khuyen_luu_y", ["thcs_huong_di_id"]
    )


def downgrade() -> None:
    op.drop_table("dm_thcs_loi_khuyen_luu_y")
    op.drop_table("dm_thcs_huong_di_tieu_chi")
    op.drop_table("dm_thcs_tieu_chi")
    op.drop_table("dm_thcs_uu_nhuoc_diem")
    op.drop_table("dm_thcs_huong_di")
