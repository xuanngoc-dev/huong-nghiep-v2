"""Tạo danh mục xuất khẩu lao động sau THPT: nhóm nghề, thị trường, nghề cụ thể, chi phí, thủ tục, kênh kết nối.

thpt_xkld_thi_truong_id NULL nghĩa là dòng áp dụng chung cho cả nhóm nghề.

Revision ID: 20261201_0074
Revises: 20261130_0073
Create Date: 2026-12-01 10:00:00.000000
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.mysql import TINYINT

revision = "20261201_0074"
down_revision = "20261130_0073"
branch_labels = None
depends_on = None

_BANG = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}

YEU_CAU_GIOI_TINH = ("nam", "nu", "ca_hai")
LOAI_CHI_PHI_XKLD = ("phi_dich_vu_xuat_canh", "dao_tao_tieng_tay_nghe", "kham_suc_khoe_ho_so", "ky_quy_chong_tron")
LOAI_KENH_XKLD = ("co_quan_nha_nuoc", "doanh_nghiep_cap_phep", "trung_tam_lao_dong_ngoai_nuoc", "ho_tro_he_thong")


def _cot_nhom_nghe(ten_fk: str):
    return sa.Column(
        "thpt_xkld_nhom_nghe_id",
        sa.Integer(),
        sa.ForeignKey("dm_thpt_xkld_nhom_nghe.id", name=ten_fk, ondelete="CASCADE"),
        nullable=False,
    )


def _cot_thi_truong(ten_fk: str):
    return sa.Column(
        "thpt_xkld_thi_truong_id",
        sa.Integer(),
        sa.ForeignKey("dm_thpt_xkld_thi_truong.id", name=ten_fk, ondelete="CASCADE"),
        nullable=True,
    )


def _index_fk(bang: str, co_thi_truong: bool = True) -> None:
    op.create_index(f"ix_{bang}_thpt_xkld_nhom_nghe_id", bang, ["thpt_xkld_nhom_nghe_id"])
    if co_thi_truong:
        op.create_index(f"ix_{bang}_thpt_xkld_thi_truong_id", bang, ["thpt_xkld_thi_truong_id"])


def upgrade() -> None:
    op.create_table(
        "dm_thpt_xkld_nhom_nghe",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("ma_nhom", sa.String(50), nullable=False),
        sa.Column("ten_nhom", sa.String(255), nullable=False),
        sa.Column("mo_ta_cong_viec", sa.Text(), nullable=False),
        sa.Column("dieu_kien_suc_khoe_the_luc", sa.Text(), nullable=True),
        sa.Column("yeu_cau_ngoai_ngu", sa.String(255), nullable=True),
        sa.Column("thoi_gian_chuan_bi_text", sa.String(100), nullable=True),
        sa.Column("thoi_gian_chuan_bi_thang_min", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("thoi_gian_chuan_bi_thang_max", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("muc_thu_nhap_text", sa.String(255), nullable=True),
        sa.Column("thu_nhap_thang_min", sa.Numeric(5, 2), nullable=True),
        sa.Column("thu_nhap_thang_max", sa.Numeric(5, 2), nullable=True),
        sa.Column("trien_vong_sau_ve_nuoc", sa.Text(), nullable=True),
        sa.Column("kha_nang_gia_han_visa", sa.String(255), nullable=True),
        sa.Column("trang_thai", TINYINT(), nullable=False, server_default="1"),
        sa.Column("ngay_tao", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "ngay_cap_nhat",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
        **_BANG,
    )
    op.create_index("ix_dm_thpt_xkld_nhom_nghe_ma_nhom", "dm_thpt_xkld_nhom_nghe", ["ma_nhom"], unique=True)

    op.create_table(
        "dm_thpt_xkld_thi_truong",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        _cot_nhom_nghe("fk_dm_txtt_nhom_nghe_id"),
        sa.Column("ma_quoc_gia", sa.String(20), nullable=False),
        sa.Column("ten_quoc_gia", sa.String(100), nullable=False),
        sa.Column("loai_visa", sa.String(100), nullable=True),
        sa.Column("dac_diem_thi_truong", sa.Text(), nullable=True),
        sa.Column("thu_nhap_rieng_text", sa.String(255), nullable=True),
        sa.Column("thoi_han_hop_dong_nam", sa.Integer(), nullable=True, server_default="3"),
        sa.Column("thu_tu_hien_thi", sa.Integer(), nullable=False, server_default="0"),
        **_BANG,
    )
    _index_fk("dm_thpt_xkld_thi_truong", co_thi_truong=False)

    op.create_table(
        "dm_thpt_xkld_nghe_cu_the",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        _cot_nhom_nghe("fk_dm_txnct_nhom_nghe_id"),
        _cot_thi_truong("fk_dm_txnct_thi_truong_id"),
        sa.Column("ten_cong_viec", sa.String(255), nullable=False),
        sa.Column("mo_ta_ngan", sa.Text(), nullable=True),
        sa.Column(
            "yeu_cau_gioi_tinh",
            sa.Enum(*YEU_CAU_GIOI_TINH, name="yeu_cau_gioi_tinh"),
            nullable=True,
            server_default="ca_hai",
        ),
        **_BANG,
    )
    _index_fk("dm_thpt_xkld_nghe_cu_the")

    op.create_table(
        "dm_thpt_xkld_chi_phi",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        _cot_nhom_nghe("fk_dm_txcp_nhom_nghe_id"),
        _cot_thi_truong("fk_dm_txcp_thi_truong_id"),
        sa.Column("loai_chi_phi", sa.Enum(*LOAI_CHI_PHI_XKLD, name="loai_chi_phi_xkld"), nullable=False),
        sa.Column("ten_khoan_chi", sa.String(255), nullable=False),
        sa.Column("chi_phi_min", sa.Numeric(12, 2), nullable=True),
        sa.Column("chi_phi_max", sa.Numeric(12, 2), nullable=True),
        sa.Column("don_vi_tien", sa.String(20), nullable=False, server_default="VND"),
        sa.Column("chi_phi_quy_doi_vnd_text", sa.String(255), nullable=True),
        sa.Column("ghi_chu", sa.String(255), nullable=True),
        **_BANG,
    )
    _index_fk("dm_thpt_xkld_chi_phi")

    op.create_table(
        "dm_thpt_xkld_thu_tuc",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        _cot_nhom_nghe("fk_dm_txtht_nhom_nghe_id"),
        _cot_thi_truong("fk_dm_txtht_thi_truong_id"),
        sa.Column("buoc_so", TINYINT(), nullable=False),
        sa.Column("ten_buoc", sa.String(255), nullable=False),
        sa.Column("mo_ta_thu_tuc", sa.Text(), nullable=False),
        sa.Column("giay_to_can_co", sa.Text(), nullable=True),
        sa.Column("thoi_gian_du_kien", sa.String(100), nullable=True),
        **_BANG,
    )
    _index_fk("dm_thpt_xkld_thu_tuc")

    op.create_table(
        "dm_thpt_xkld_kenh_ket_noi",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        _cot_nhom_nghe("fk_dm_txkkn_nhom_nghe_id"),
        _cot_thi_truong("fk_dm_txkkn_thi_truong_id"),
        sa.Column("loai_kenh", sa.Enum(*LOAI_KENH_XKLD, name="loai_kenh_xkld"), nullable=False),
        sa.Column("ten_kenh", sa.String(255), nullable=False),
        sa.Column("thong_tin_lien_he", sa.String(255), nullable=True),
        sa.Column("mo_ta_ho_tro", sa.Text(), nullable=True),
        sa.Column("luu_y_tranh_rui_ro", sa.String(255), nullable=True),
        sa.Column("thu_tu_hien_thi", sa.Integer(), nullable=False, server_default="0"),
        **_BANG,
    )
    _index_fk("dm_thpt_xkld_kenh_ket_noi")


def downgrade() -> None:
    op.drop_table("dm_thpt_xkld_kenh_ket_noi")
    op.drop_table("dm_thpt_xkld_thu_tuc")
    op.drop_table("dm_thpt_xkld_chi_phi")
    op.drop_table("dm_thpt_xkld_nghe_cu_the")
    op.drop_table("dm_thpt_xkld_thi_truong")
    op.drop_table("dm_thpt_xkld_nhom_nghe")
