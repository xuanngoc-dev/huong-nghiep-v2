"""Tao cac bang luu ket qua danh gia xet tuyen (buoc 3.4 KE_HOACH_TRIEN_KHAI.md).

Theo docs/de-an-tuyen-sinh/01_schema.sql (xt_lan_danh_gia, xt_ket_qua_phuong_an, xt_ket_qua_chuong_trinh), dieu chinh:
- Chua co hs_ho_so (giai doan 4): xt_lan_danh_gia luu nguoi_dung_id / ma_thiet_bi de kiem tra quyen xem, ho_so_id
  de trong duoc va chua dat khoa ngoai; luu kem ban chup ho so da dung (JSON) va cac gia dinh khi dung ho so.
- Them phien_ban_thuat_toan, so dong ket qua, thoi gian tinh; xt_ket_qua_phuong_an them chi_tiet (cach tinh diem).
Ket qua phuong an xoa theo khi phuong an bi xoa (import lai quy tac): ket qua tinh theo quy tac cu khong con dung.

Revision ID: 20261118_0059
Revises: 20261117_0058
Create Date: 2026-11-18 09:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, SMALLINT

revision: str = "20261118_0059"
down_revision: Union[str, Sequence[str], None] = "20261117_0058"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_BANG = dict(mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci", mysql_engine="InnoDB")
_THU_TU = ["xt_lan_danh_gia", "xt_ket_qua_phuong_an", "xt_ket_qua_chuong_trinh"]


def _has_table(table: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(table)


def _tao(table: str, *columns, **kwargs) -> None:
    """Tạo bảng nếu chưa có. MySQL không rollback được DDL nên chạy lại sau khi lỗi giữa chừng vẫn được."""
    if not _has_table(table):
        op.create_table(table, *columns, **kwargs)


def upgrade() -> None:
    _tao(
        "xt_lan_danh_gia",
        sa.Column("id", BIGINT(unsigned=True), autoincrement=True, nullable=False, primary_key=True),
        sa.Column("nguoi_dung_id", sa.Integer(), comment="Thành viên chạy đánh giá; trống nếu là khách."),
        sa.Column("ma_thiet_bi", sa.String(64), comment="Khách vãng lai: mã thiết bị, dùng để kiểm tra quyền xem."),
        sa.Column("ho_so_id", BIGINT(unsigned=True), comment="Hồ sơ hs_ho_so (giai đoạn 4); trống khi dựng từ dữ liệu cũ."),
        sa.Column("nam_tuyen_sinh", SMALLINT(unsigned=True), nullable=False, comment="Năm của các đề án được dùng."),
        sa.Column("bo_tieu_chi_id", BIGINT(unsigned=True), nullable=False),
        sa.Column(
            "lich_su_tim_truong_id",
            BIGINT(unsigned=True),
            comment="tn_lich_su_tim_truong_phu_hop.id nếu chạy từ một lượt tìm trường.",
        ),
        sa.Column("phien_ban_thuat_toan", sa.String(20), nullable=False, server_default="xt-v1"),
        sa.Column("ho_so_xet_tuyen", sa.JSON(), comment="Bản chụp hồ sơ đã dùng để tính."),
        sa.Column("gia_dinh", sa.JSON(), comment="Các giả định khi dựng hồ sơ (điểm ước tính, ngân sách...)."),
        sa.Column("so_phuong_an", INTEGER(unsigned=True), nullable=False, server_default="0"),
        sa.Column("so_chuong_trinh", INTEGER(unsigned=True), nullable=False, server_default="0"),
        sa.Column("thoi_gian_tinh_ms", INTEGER(unsigned=True), comment="Thời gian chạy bộ tính, mili giây."),
        sa.Column("tao_luc", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Index("idx_xt_lan_danh_gia_nguoi_dung", "nguoi_dung_id", "tao_luc"),
        sa.Index("idx_xt_lan_danh_gia_thiet_bi", "ma_thiet_bi", "tao_luc"),
        sa.Index("idx_xt_lan_danh_gia_lich_su", "lich_su_tim_truong_id"),
        sa.ForeignKeyConstraint(
            ["nguoi_dung_id"], ["nguoi_dung.id"], name="fk_xt_ldg_nguoi_dung_id", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["bo_tieu_chi_id"], ["xt_bo_tieu_chi.id"], name="fk_xt_ldg_bo_tieu_chi_id"),
        sa.ForeignKeyConstraint(
            ["lich_su_tim_truong_id"],
            ["tn_lich_su_tim_truong_phu_hop.id"],
            name="fk_xt_ldg_lich_su_id",
            ondelete="SET NULL",
        ),
        comment="Mỗi lần chạy đánh giá xét tuyển cho một hồ sơ",
        **_BANG,
    )
    _tao(
        "xt_ket_qua_phuong_an",
        sa.Column("id", BIGINT(unsigned=True), autoincrement=True, nullable=False, primary_key=True),
        sa.Column("lan_danh_gia_id", BIGINT(unsigned=True), nullable=False),
        sa.Column("phuong_an_id", BIGINT(unsigned=True), nullable=False),
        sa.Column("de_an_chuong_trinh_id", BIGINT(unsigned=True), nullable=False),
        sa.Column("cong_thuc_id", BIGINT(unsigned=True), nullable=False),
        sa.Column("to_hop_id", sa.Integer()),
        sa.Column("kieu_tinh", sa.String(20), nullable=False),
        sa.Column("thang_diem", sa.Numeric(6, 2), nullable=False),
        sa.Column("diem_goc", sa.Numeric(9, 4), comment="Điểm theo công thức, chưa cộng."),
        sa.Column("tb_mon", sa.Numeric(6, 3), comment="Trung bình các môn học dùng xét."),
        sa.Column("tong_thpt_to_hop", sa.Numeric(6, 2), comment="Tổng điểm thi THPT theo tổ hợp, chưa gồm ưu tiên."),
        sa.Column("diem_cong", sa.Numeric(6, 2), nullable=False, server_default="0"),
        sa.Column("diem_uu_tien", sa.Numeric(6, 2), nullable=False, server_default="0"),
        sa.Column("diem_xet", sa.Numeric(7, 2), comment="Điểm xét tuyển cuối cùng."),
        sa.Column("dat_nguong", sa.Boolean(), comment="Đạt mọi ngưỡng điểm của công thức."),
        sa.Column("so_nhom_dieu_kien", SMALLINT(unsigned=True), nullable=False, server_default="0"),
        sa.Column("so_nhom_dat", SMALLINT(unsigned=True), nullable=False, server_default="0"),
        sa.Column("du_dieu_kien", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("ly_do_khong_dat", sa.String(1000)),
        sa.Column("diem_chuan_id", BIGINT(unsigned=True), comment="Dòng xt_diem_chuan dùng làm mốc."),
        sa.Column("diem_chuan_tham_chieu", sa.Numeric(7, 2)),
        sa.Column("thang_diem_chuan", sa.Numeric(6, 2)),
        sa.Column("nam_diem_chuan", SMALLINT(unsigned=True)),
        sa.Column("chenh_lech_30", sa.Numeric(6, 2), comment="(điểm xét - điểm chuẩn) cùng quy về thang 30."),
        sa.Column("chi_tiet", sa.String(500), comment="Cách tính điểm gốc, để giải thích cho học sinh."),
        sa.Index("idx_xt_kqpa_lan", "lan_danh_gia_id", "de_an_chuong_trinh_id"),
        sa.Index("idx_xt_kqpa_phuong_an", "phuong_an_id"),
        sa.ForeignKeyConstraint(
            ["lan_danh_gia_id"], ["xt_lan_danh_gia.id"], name="fk_xt_kqpa_lan_danh_gia_id", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["phuong_an_id"], ["xt_phuong_an.id"], name="fk_xt_kqpa_phuong_an_id", ondelete="CASCADE"),
        comment="Kết quả tính điểm và xét điều kiện của học sinh trên từng phương án",
        **_BANG,
    )
    _tao(
        "xt_ket_qua_chuong_trinh",
        sa.Column("id", BIGINT(unsigned=True), autoincrement=True, nullable=False, primary_key=True),
        sa.Column("lan_danh_gia_id", BIGINT(unsigned=True), nullable=False),
        sa.Column("de_an_chuong_trinh_id", BIGINT(unsigned=True), nullable=False),
        sa.Column("ma_truong", sa.String(20), nullable=False),
        sa.Column(
            "ket_qua_phuong_an_id",
            BIGINT(unsigned=True),
            nullable=False,
            comment="Phương án tốt nhất của học sinh cho chương trình này.",
        ),
        sa.Column("la_xet_thang", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("diem_xet", sa.Numeric(7, 2)),
        sa.Column("thang_diem", sa.Numeric(6, 2)),
        sa.Column("chenh_lech_30", sa.Numeric(6, 2)),
        sa.Column("diem_kha_nang", sa.Numeric(5, 2), comment="0-100; NULL nếu chưa có điểm chuẩn tham chiếu."),
        sa.Column("diem_nganh", sa.Numeric(5, 2), comment="0-100; NULL nếu chưa chọn ngành hoặc chưa gắn mã ngành."),
        sa.Column("diem_hoc_phi", sa.Numeric(5, 2), comment="0-100; NULL nếu thiếu ngân sách hoặc học phí."),
        sa.Column("diem_vi_tri", sa.Numeric(5, 2), comment="0-100; NULL nếu không nêu địa điểm mong muốn."),
        sa.Column("diem_phu_hop", sa.Numeric(5, 2), comment="Điểm tổng hợp 0-100; NULL nếu chưa có điểm khả năng."),
        sa.Column("xep_loai", sa.String(50)),
        sa.Column("thu_hang", INTEGER(unsigned=True), comment="Thứ hạng trong lần đánh giá (1 = phù hợp nhất)."),
        sa.UniqueConstraint("lan_danh_gia_id", "de_an_chuong_trinh_id", name="uk_xt_kqct"),
        sa.Index("idx_xt_kqct_xep_hang", "lan_danh_gia_id", "thu_hang"),
        sa.Index("idx_xt_kqct_truong", "lan_danh_gia_id", "ma_truong"),
        sa.ForeignKeyConstraint(
            ["lan_danh_gia_id"], ["xt_lan_danh_gia.id"], name="fk_xt_kqct_lan_danh_gia_id", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["ket_qua_phuong_an_id"],
            ["xt_ket_qua_phuong_an.id"],
            name="fk_xt_kqct_ket_qua_phuong_an_id",
            ondelete="CASCADE",
        ),
        comment="Mức độ phù hợp của từng chương trình với học sinh (theo phương án tốt nhất)",
        **_BANG,
    )


def downgrade() -> None:
    for table in reversed(_THU_TU):
        if _has_table(table):
            op.drop_table(table)
