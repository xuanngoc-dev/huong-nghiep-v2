"""Tao bang tn_lich_su_tim_truong_phu_hop.

Luu moi luot tim truong phu hop cua tai khoan: du lieu dau vao, ket qua, loai luot
va thong tin mo khoa bao cao chuyen sau.

Revision ID: 20261112_0048
Revises: 20261112_0047
Create Date: 2026-11-12 18:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision: str = "20261112_0048"
down_revision: Union[str, Sequence[str], None] = "20261112_0047"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE = "tn_lich_su_tim_truong_phu_hop"


def _has_table(table: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(table)


def upgrade() -> None:
    if _has_table(_TABLE):
        return
    op.create_table(
        _TABLE,
        sa.Column("id", mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False, comment="Khóa chính"),
        sa.Column(
            "tai_khoan_id",
            mysql.BIGINT(unsigned=True),
            nullable=False,
            comment="ID tài khoản thực hiện tìm kiếm",
        ),
        sa.Column("ma_yeu_cau", sa.String(64), nullable=False, comment="Mã yêu cầu duy nhất, tránh xử lý trùng"),
        sa.Column("ma_nganh", sa.String(20), nullable=False, comment="Mã ngành đào tạo muốn tìm"),
        sa.Column("nam_tuyen_sinh", mysql.SMALLINT(unsigned=True), nullable=False, comment="Năm tuyển sinh"),
        sa.Column(
            "du_lieu_nang_luc",
            sa.JSON(),
            nullable=False,
            comment="Điểm thi thử THPT, học bạ, ĐGNL, chứng chỉ",
        ),
        sa.Column(
            "du_lieu_tai_chinh",
            sa.JSON(),
            nullable=False,
            comment="Khả năng tài chính, học phí và chi phí sinh hoạt",
        ),
        sa.Column(
            "tieu_chi_tim_kiem",
            sa.JSON(),
            nullable=False,
            comment="Khu vực, loại hình trường và ưu tiên khác",
        ),
        sa.Column(
            "so_truong_tim_thay",
            mysql.INTEGER(unsigned=True),
            server_default="0",
            nullable=False,
            comment="Tổng số trường tìm được",
        ),
        sa.Column(
            "so_truong_phu_hop_so_bo",
            mysql.INTEGER(unsigned=True),
            server_default="0",
            nullable=False,
            comment="Số trường đáp ứng tiêu chí sơ bộ",
        ),
        sa.Column(
            "du_lieu_ket_qua",
            sa.JSON(),
            nullable=True,
            comment="Danh sách các trường tìm thấy và kết quả đánh giá",
        ),
        sa.Column("phien_ban_thuat_toan", sa.String(50), nullable=True, comment="Phiên bản thuật toán phân tích"),
        sa.Column(
            "loai_luot",
            mysql.ENUM("mien_phi", "tra_phi", "khuyen_mai"),
            server_default="mien_phi",
            nullable=False,
            comment="Loại lượt: mien_phi, tra_phi, khuyen_mai",
        ),
        sa.Column(
            "da_tinh_luot",
            mysql.TINYINT(1),
            server_default="0",
            nullable=False,
            comment="1: Đã tính lượt; 0: Chưa tính",
        ),
        sa.Column(
            "da_mo_khoa_chuyen_sau",
            mysql.TINYINT(1),
            server_default="0",
            nullable=False,
            comment="1: Đã mở khóa báo cáo; 0: Chưa mở khóa",
        ),
        sa.Column(
            "gia_bao_cao_tai_thoi_diem",
            sa.Numeric(15, 0),
            nullable=True,
            comment="Giá báo cáo chuyên sâu tại thời điểm mua (VNĐ)",
        ),
        sa.Column(
            "giao_dich_thanh_toan_id",
            mysql.BIGINT(unsigned=True),
            nullable=True,
            comment="ID giao dịch thanh toán liên quan",
        ),
        sa.Column("ngay_mo_khoa", sa.DateTime(), nullable=True, comment="Thời điểm mở khóa phân tích chuyên sâu"),
        sa.Column(
            "trang_thai_xu_ly",
            mysql.ENUM("cho_xu_ly", "dang_xu_ly", "thanh_cong", "that_bai"),
            server_default="cho_xu_ly",
            nullable=False,
            comment="cho_xu_ly, dang_xu_ly, thanh_cong, that_bai",
        ),
        sa.Column("thong_bao_loi", sa.Text(), nullable=True, comment="Nội dung lỗi nếu tìm kiếm thất bại"),
        sa.Column("ngay_hoan_thanh", sa.DateTime(), nullable=True, comment="Thời điểm hoàn thành tìm kiếm"),
        sa.Column(
            "ngay_tao",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
            comment="Thời gian tạo",
        ),
        sa.Column(
            "ngay_cap_nhat",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
            nullable=False,
            comment="Thời gian cập nhật gần nhất",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ma_yeu_cau", name="uq_tn_lich_su_tim_truong_ma_yeu_cau"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index("idx_tn_lich_su_tim_truong_tai_khoan_ngay", _TABLE, ["tai_khoan_id", "ngay_tao"])
    op.create_index("idx_tn_lich_su_tim_truong_ma_nganh", _TABLE, ["ma_nganh", "nam_tuyen_sinh"])
    op.create_index("idx_tn_lich_su_tim_truong_trang_thai", _TABLE, ["trang_thai_xu_ly"])


def downgrade() -> None:
    if _has_table(_TABLE):
        op.drop_table(_TABLE)
