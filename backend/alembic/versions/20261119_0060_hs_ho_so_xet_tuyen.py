"""Tao cac bang ho so xet tuyen hs_* (buoc 4.2 KE_HOACH_TRIEN_KHAI.md).

Theo docs/de-an-tuyen-sinh/01_schema.sql (phan B), dieu chinh:
- Khong tao hs_chi_so: bo tinh Python tu tinh chi so tu cac bang hs_*.
- hs_ho_so them la_ho_so_chinh (mot tai khoan co the co nhieu ho so gia dinh; tim truong dung ho so chinh);
  cap_nhat_luc do code cap nhat (khong dung ON UPDATE CURRENT_TIMESTAMP).
- Them khoa ngoai xt_lan_danh_gia.ho_so_id -> hs_ho_so (ON DELETE SET NULL).

Revision ID: 20261119_0060
Revises: 20261118_0059
Create Date: 2026-11-19 09:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT, TINYINT

revision: str = "20261119_0060"
down_revision: Union[str, Sequence[str], None] = "20261118_0059"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_BANG = dict(mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci", mysql_engine="InnoDB")
_THU_TU = [
    "hs_ho_so",
    "hs_ket_qua_nam_hoc",
    "hs_diem_mon",
    "hs_diem_bai_thi",
    "hs_chung_chi",
    "hs_thanh_tich",
    "hs_tieu_chi_mong_muon",
]
_FK_LAN_DANH_GIA = "fk_xt_ldg_ho_so_id"


def _has_table(table: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(table)


def _tao(table: str, *columns, **kwargs) -> None:
    """Tạo bảng nếu chưa có. MySQL không rollback được DDL nên chạy lại sau khi lỗi giữa chừng vẫn được."""
    if not _has_table(table):
        op.create_table(table, *columns, **kwargs)


def _id() -> sa.Column:
    return sa.Column("id", BIGINT(unsigned=True), autoincrement=True, nullable=False, primary_key=True)


def _ho_so_id() -> sa.Column:
    return sa.Column("ho_so_id", BIGINT(unsigned=True), nullable=False)


def _fk_ho_so(table: str) -> sa.ForeignKeyConstraint:
    return sa.ForeignKeyConstraint(["ho_so_id"], ["hs_ho_so.id"], name=f"fk_{table}_ho_so_id", ondelete="CASCADE")


def upgrade() -> None:
    _tao(
        "hs_ho_so",
        _id(),
        sa.Column("nguoi_dung_id", sa.Integer(), comment="Tài khoản sở hữu; NULL nếu khách vãng lai."),
        sa.Column("ma_thiet_bi", sa.String(64), comment="Mã thiết bị của khách vãng lai."),
        sa.Column("ten_ho_so", sa.String(150), comment="Tên gợi nhớ (một tài khoản có thể có nhiều hồ sơ giả định)."),
        sa.Column(
            "la_ho_so_chinh",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
            comment="Hồ sơ dùng khi tìm trường phù hợp.",
        ),
        sa.Column("nam_tot_nghiep", SMALLINT(unsigned=True), comment="Năm tốt nghiệp THPT (thực tế hoặc dự kiến)."),
        sa.Column("da_tot_nghiep", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "chuong_trinh_thpt",
            sa.Enum("GDPT_2018", "GDPT_2006", "NUOC_NGOAI", name="chuong_trinh_thpt"),
            nullable=False,
            server_default="GDPT_2018",
        ),
        sa.Column("he_chuyen", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("mon_chuyen_id", sa.Integer(), comment="Môn chuyên; FK dm_mon_hoc.id."),
        sa.Column("ten_truong_thpt", sa.String(255)),
        sa.Column("tinh_thanh_id", sa.Integer(), comment="Tỉnh/thành nơi học THPT."),
        sa.Column("khu_vuc_uu_tien_id", sa.Integer()),
        sa.Column("doi_tuong_uu_tien_id", sa.Integer(), comment="Đối tượng ưu tiên (mức cao nhất)."),
        sa.Column("ngan_sach_hoc_phi_nam", sa.Numeric(15, 0), comment="Học phí tối đa gia đình chi trả được mỗi năm (VNĐ)."),
        sa.Column("tao_luc", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("cap_nhat_luc", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Index("idx_hs_ho_so_nguoi_dung_id", "nguoi_dung_id"),
        sa.Index("idx_hs_ho_so_ma_thiet_bi", "ma_thiet_bi"),
        sa.ForeignKeyConstraint(["nguoi_dung_id"], ["nguoi_dung.id"], name="fk_hs_ho_so_nguoi_dung_id", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["mon_chuyen_id"], ["dm_mon_hoc.id"], name="fk_hs_ho_so_mon_chuyen_id"),
        sa.ForeignKeyConstraint(["tinh_thanh_id"], ["dm_tinh_thanh.id"], name="fk_hs_ho_so_tinh_thanh_id"),
        sa.ForeignKeyConstraint(["khu_vuc_uu_tien_id"], ["dm_khu_vuc_uu_tien.id"], name="fk_hs_ho_so_khu_vuc_uu_tien_id"),
        sa.ForeignKeyConstraint(
            ["doi_tuong_uu_tien_id"], ["dm_doi_tuong_uu_tien.id"], name="fk_hs_ho_so_doi_tuong_uu_tien_id"
        ),
        comment="Hồ sơ xét tuyển của học sinh",
        **_BANG,
    )
    _tao(
        "hs_ket_qua_nam_hoc",
        _id(),
        _ho_so_id(),
        sa.Column("lop", TINYINT(unsigned=True), nullable=False, comment="10, 11 hoặc 12."),
        sa.Column("diem_tb_chung", sa.Numeric(4, 2), comment="Điểm trung bình chung cả năm, thang 10."),
        sa.Column("hoc_luc", TINYINT(unsigned=True), comment="4 Tốt/Giỏi, 3 Khá, 2 Đạt/Trung bình, 1 Chưa đạt/Yếu."),
        sa.Column("ren_luyen", TINYINT(unsigned=True), comment="4 Tốt, 3 Khá, 2 Đạt/Trung bình, 1 Chưa đạt/Yếu."),
        sa.UniqueConstraint("ho_so_id", "lop", name="uk_hs_ket_qua_nam_hoc"),
        _fk_ho_so("hs_ket_qua_nam_hoc"),
        comment="Kết quả tổng kết từng năm THPT của học sinh",
        **_BANG,
    )
    _tao(
        "hs_diem_mon",
        _id(),
        _ho_so_id(),
        sa.Column("mon_hoc_id", sa.Integer(), nullable=False, comment="Ngoại ngữ ghi đúng môn: ANH, PHAP, TRUNG..."),
        sa.Column("nguon_diem", sa.Enum("THI_THPT", "HOC_BA", name="nguon_diem"), nullable=False),
        sa.Column("lop", TINYINT(unsigned=True), nullable=False, server_default="0", comment="HOC_BA: 10/11/12; THI_THPT: 0."),
        sa.Column("hoc_ky", TINYINT(unsigned=True), nullable=False, server_default="0", comment="0 = cả năm, 1, 2."),
        sa.Column("diem", sa.Numeric(5, 2), nullable=False, comment="Điểm thang 10."),
        sa.Column("nam", SMALLINT(unsigned=True), comment="Năm thi / năm học."),
        sa.Column("la_du_kien", sa.Boolean(), nullable=False, server_default=sa.false(), comment="Điểm thi thử / ước lượng."),
        sa.UniqueConstraint("ho_so_id", "nguon_diem", "mon_hoc_id", "lop", "hoc_ky", name="uk_hs_diem_mon"),
        sa.Index("idx_hs_diem_mon_mon_hoc_id", "mon_hoc_id"),
        _fk_ho_so("hs_diem_mon"),
        sa.ForeignKeyConstraint(["mon_hoc_id"], ["dm_mon_hoc.id"], name="fk_hs_diem_mon_mon_hoc_id"),
        comment="Điểm từng môn: thi tốt nghiệp THPT và học bạ",
        **_BANG,
    )
    _tao(
        "hs_diem_bai_thi",
        _id(),
        _ho_so_id(),
        sa.Column("bai_thi_id", BIGINT(unsigned=True), nullable=False, comment="HSA, V-ACT, TSA, SAT, ACT..."),
        sa.Column("nam_thi", SMALLINT(unsigned=True), nullable=False),
        sa.Column("dot_thi", sa.String(30)),
        sa.Column("ngay_thi", sa.Date()),
        sa.Column("diem", sa.Numeric(8, 2), nullable=False, comment="Tổng điểm theo thang gốc của bài thi."),
        sa.Column("phan_tu_chon", sa.String(50), comment="Ví dụ HSA phần 3: KHOA_HOC / TIENG_ANH."),
        sa.Column("diem_thanh_phan", sa.JSON(), comment="Điểm từng phần thi (để hiển thị)."),
        sa.Index("idx_hs_diem_bai_thi_ho_so_id", "ho_so_id", "bai_thi_id"),
        sa.Index("idx_hs_diem_bai_thi_bai_thi_id", "bai_thi_id"),
        _fk_ho_so("hs_diem_bai_thi"),
        sa.ForeignKeyConstraint(["bai_thi_id"], ["dm_bai_thi_danh_gia.id"], name="fk_hs_diem_bai_thi_bai_thi_id"),
        comment="Kết quả các bài thi ĐGNL/ĐGTD/SAT/ACT của học sinh",
        **_BANG,
    )
    _tao(
        "hs_chung_chi",
        _id(),
        _ho_so_id(),
        sa.Column("chung_chi_id", BIGINT(unsigned=True), nullable=False, comment="IELTS, TOEFL, JLPT, HSK, DELF, VSTEP..."),
        sa.Column("diem", sa.Numeric(8, 2), comment="Điểm theo thang của chứng chỉ; NULL nếu chỉ có cấp độ."),
        sa.Column("cap_do", sa.String(30), comment="N3, HSK4, B2..."),
        sa.Column("ngay_cap", sa.Date()),
        sa.Column("ngay_het_han", sa.Date(), comment="NULL: không thời hạn / chưa biết."),
        sa.Column("diem_thanh_phan", sa.JSON(), comment="Điểm kỹ năng (để hiển thị)."),
        sa.Index("idx_hs_chung_chi_ho_so_id", "ho_so_id", "chung_chi_id"),
        sa.Index("idx_hs_chung_chi_chung_chi_id", "chung_chi_id"),
        _fk_ho_so("hs_chung_chi"),
        sa.ForeignKeyConstraint(["chung_chi_id"], ["dm_bang_cap_chung_chi.id"], name="fk_hs_chung_chi_chung_chi_id"),
        comment="Chứng chỉ ngoại ngữ / quốc tế của học sinh",
        **_BANG,
    )
    _tao(
        "hs_thanh_tich",
        _id(),
        _ho_so_id(),
        sa.Column("thanh_tich_id", sa.Integer(), nullable=False, comment="HSG-QG, HSG-TINH, NCKH-QG..."),
        sa.Column("mon_hoc_id", sa.Integer(), comment="Môn đạt giải."),
        sa.Column("linh_vuc", sa.String(150), comment="Lĩnh vực đề tài (KHKT) nếu không gắn với môn học."),
        sa.Column("muc_giai", TINYINT(unsigned=True), nullable=False, comment="1 Nhất, 2 Nhì, 3 Ba, 4 Khuyến khích, 9 tham gia."),
        sa.Column("nam_dat_giai", SMALLINT(unsigned=True)),
        sa.Column("lop", TINYINT(unsigned=True), comment="Lớp khi đạt giải."),
        sa.Index("idx_hs_thanh_tich_ho_so_id", "ho_so_id", "thanh_tich_id"),
        sa.Index("idx_hs_thanh_tich_thanh_tich_id", "thanh_tich_id"),
        _fk_ho_so("hs_thanh_tich"),
        sa.ForeignKeyConstraint(
            ["thanh_tich_id"], ["dm_thanh_tich_hoc_tap_nghien_cuu.id"], name="fk_hs_thanh_tich_thanh_tich_id"
        ),
        sa.ForeignKeyConstraint(["mon_hoc_id"], ["dm_mon_hoc.id"], name="fk_hs_thanh_tich_mon_hoc_id"),
        comment="Giải thưởng, thành tích của học sinh",
        **_BANG,
    )
    _tao(
        "hs_tieu_chi_mong_muon",
        _id(),
        _ho_so_id(),
        sa.Column(
            "loai",
            sa.Enum("NGANH", "NHOM_NGANH", "LINH_VUC", "TINH_THANH", "VUNG_MIEN", "LOAI_HINH_TRUONG", name="loai_mong_muon"),
            nullable=False,
        ),
        sa.Column("gia_tri", sa.String(100), nullable=False, comment="Mã ngành / nhóm ngành / lĩnh vực / mã tỉnh / vùng / loại hình."),
        sa.UniqueConstraint("ho_so_id", "loai", "gia_tri", name="uk_hs_tieu_chi_mong_muon"),
        _fk_ho_so("hs_tieu_chi_mong_muon"),
        comment="Ngành, địa điểm, loại trường học sinh mong muốn",
        **_BANG,
    )
    if op.get_context().as_sql:
        # Chế độ sinh SQL offline không đọc được cấu trúc bảng; luôn thêm khóa ngoại.
        op.create_foreign_key(
            _FK_LAN_DANH_GIA, "xt_lan_danh_gia", "hs_ho_so", ["ho_so_id"], ["id"], ondelete="SET NULL"
        )
        return
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    # SQLite (test) không thêm được khóa ngoại vào bảng đã có.
    if bind.dialect.name != "sqlite" and inspector.has_table("xt_lan_danh_gia") and _FK_LAN_DANH_GIA not in {
        fk["name"] for fk in inspector.get_foreign_keys("xt_lan_danh_gia")
    }:
        op.create_foreign_key(
            _FK_LAN_DANH_GIA, "xt_lan_danh_gia", "hs_ho_so", ["ho_so_id"], ["id"], ondelete="SET NULL"
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if bind.dialect.name != "sqlite" and inspector.has_table("xt_lan_danh_gia") and _FK_LAN_DANH_GIA in {
        fk["name"] for fk in inspector.get_foreign_keys("xt_lan_danh_gia")
    }:
        op.drop_constraint(_FK_LAN_DANH_GIA, "xt_lan_danh_gia", type_="foreignkey")
    for table in reversed(_THU_TU):
        if _has_table(table):
            op.drop_table(table)
