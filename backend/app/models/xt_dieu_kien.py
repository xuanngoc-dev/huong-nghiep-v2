from decimal import Decimal

from sqlalchemy import Boolean, Enum, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

_BANG = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}

TOAN_TU = (">=", ">", "=", "<=", "<", "!=")


class XtNhomDieuKien(Base):
    """Nhóm điều kiện dự tuyển; các nhóm áp dụng cho một phương án phải cùng đạt (AND)."""

    __tablename__ = "xt_nhom_dieu_kien"
    __table_args__ = (Index("idx_xt_nhom_dieu_kien_de_an", "de_an_id", "cong_thuc_id", "de_an_chuong_trinh_id"), _BANG)

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    de_an_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("dats_tuyen_sinh.id", name="fk_xt_ndk_de_an_id"), nullable=False
    )
    # NULL = mọi công thức của đề án.
    cong_thuc_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("xt_cong_thuc.id", name="fk_xt_ndk_cong_thuc_id", ondelete="CASCADE")
    )
    # NULL = mọi chương trình.
    de_an_chuong_trinh_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("dats_chuong_trinh_dao_tao.id", name="fk_xt_ndk_chuong_trinh_id")
    )
    ma_nhom: Mapped[str] = mapped_column(String(50), nullable=False)
    ten_nhom: Mapped[str] = mapped_column(String(255), nullable=False)
    mo_ta: Mapped[str | None] = mapped_column(Text)
    # True: không đạt thì loại; False: chỉ cảnh báo.
    bat_buoc: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="1")


class XtDieuKien(Base):
    """Điều kiện đơn; trong một nhóm chỉ cần một điều kiện đạt (OR). Học sinh không có chỉ số = không đạt."""

    __tablename__ = "xt_dieu_kien"
    __table_args__ = (
        Index("idx_xt_dieu_kien_nhom", "nhom_dieu_kien_id"),
        Index("idx_xt_dieu_kien_chi_so", "ma_chi_so", "khoa"),
        _BANG,
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    nhom_dieu_kien_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("xt_nhom_dieu_kien.id", name="fk_xt_dk_nhom_dieu_kien_id", ondelete="CASCADE"),
        nullable=False,
    )
    ma_chi_so: Mapped[str] = mapped_column(
        String(50), ForeignKey("dm_chi_so_xet_tuyen.ma_chi_so", name="fk_xt_dk_ma_chi_so"), nullable=False
    )
    khoa: Mapped[str] = mapped_column(String(50), nullable=False, default="", server_default="")
    toan_tu: Mapped[str] = mapped_column(Enum(*TOAN_TU, name="toan_tu"), nullable=False)
    gia_tri_so: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    mo_ta: Mapped[str | None] = mapped_column(String(500))


class XtDiemCong(Base):
    """Quy tắc điểm cộng có cấu trúc; cùng nhom_cong lấy mức cao nhất, khác nhóm cộng dồn."""

    __tablename__ = "xt_diem_cong"
    __table_args__ = (Index("idx_xt_diem_cong_de_an", "de_an_id", "cong_thuc_id"), _BANG)

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    de_an_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("dats_tuyen_sinh.id", name="fk_xt_diem_cong_de_an_id"), nullable=False
    )
    # NULL = mọi công thức của đề án có ap_dung_diem_cong.
    cong_thuc_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("xt_cong_thuc.id", name="fk_xt_diem_cong_cong_thuc_id", ondelete="CASCADE")
    )
    loai_diem_cong: Mapped[str] = mapped_column(
        Enum("DIEM_THUONG", "DIEM_XET_THUONG", "DIEM_KHUYEN_KHICH", name="loai_diem_cong"), nullable=False
    )
    nhom_cong: Mapped[str] = mapped_column(String(50), nullable=False)
    ma_chi_so: Mapped[str] = mapped_column(
        String(50), ForeignKey("dm_chi_so_xet_tuyen.ma_chi_so", name="fk_xt_diem_cong_ma_chi_so"), nullable=False
    )
    khoa: Mapped[str] = mapped_column(String(50), nullable=False, default="", server_default="")
    toan_tu: Mapped[str] = mapped_column(Enum(*TOAN_TU, name="toan_tu"), nullable=False)
    gia_tri_so: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    # Mức cộng tính trên thang 30; tự quy đổi theo thang điểm của công thức.
    diem_cong: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    mo_ta: Mapped[str | None] = mapped_column(String(500))
