from datetime import datetime
from decimal import Decimal

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Index, Integer, Numeric, String, UniqueConstraint, text
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, SMALLINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

_BANG = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class XtLanDanhGia(Base):
    """Mỗi lần chạy bộ tính xét tuyển cho một hồ sơ. Chủ sở hữu: nguoi_dung_id (thành viên) hoặc ma_thiet_bi (khách)."""

    __tablename__ = "xt_lan_danh_gia"
    __table_args__ = (
        Index("idx_xt_lan_danh_gia_nguoi_dung", "nguoi_dung_id", "tao_luc"),
        Index("idx_xt_lan_danh_gia_thiet_bi", "ma_thiet_bi", "tao_luc"),
        Index("idx_xt_lan_danh_gia_lich_su", "lich_su_tim_truong_id"),
        _BANG,
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    nguoi_dung_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("nguoi_dung.id", name="fk_xt_ldg_nguoi_dung_id", ondelete="CASCADE")
    )
    ma_thiet_bi: Mapped[str | None] = mapped_column(String(64))
    # Hồ sơ hs_ho_so (giai đoạn 4); trống khi dựng từ dữ liệu cũ.
    ho_so_id: Mapped[int | None] = mapped_column(BIGINT(unsigned=True))
    nam_tuyen_sinh: Mapped[int] = mapped_column(SMALLINT(unsigned=True), nullable=False)
    bo_tieu_chi_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("xt_bo_tieu_chi.id", name="fk_xt_ldg_bo_tieu_chi_id"), nullable=False
    )
    lich_su_tim_truong_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("tn_lich_su_tim_truong_phu_hop.id", name="fk_xt_ldg_lich_su_id", ondelete="SET NULL"),
    )
    phien_ban_thuat_toan: Mapped[str] = mapped_column(String(20), nullable=False, default="xt-v1", server_default="xt-v1")
    ho_so_xet_tuyen: Mapped[dict | None] = mapped_column(JSON)
    gia_dinh: Mapped[list | None] = mapped_column(JSON)
    so_phuong_an: Mapped[int] = mapped_column(INTEGER(unsigned=True), nullable=False, default=0, server_default="0")
    so_chuong_trinh: Mapped[int] = mapped_column(INTEGER(unsigned=True), nullable=False, default=0, server_default="0")
    thoi_gian_tinh_ms: Mapped[int | None] = mapped_column(INTEGER(unsigned=True))
    tao_luc: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class XtKetQuaPhuongAn(Base):
    """Kết quả tính điểm và xét điều kiện của học sinh trên từng phương án."""

    __tablename__ = "xt_ket_qua_phuong_an"
    __table_args__ = (
        Index("idx_xt_kqpa_lan", "lan_danh_gia_id", "de_an_chuong_trinh_id"),
        Index("idx_xt_kqpa_phuong_an", "phuong_an_id"),
        _BANG,
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    lan_danh_gia_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("xt_lan_danh_gia.id", name="fk_xt_kqpa_lan_danh_gia_id", ondelete="CASCADE"),
        nullable=False,
    )
    # Xóa theo khi import lại quy tắc: kết quả tính theo quy tắc cũ không còn đúng.
    phuong_an_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("xt_phuong_an.id", name="fk_xt_kqpa_phuong_an_id", ondelete="CASCADE"),
        nullable=False,
    )
    de_an_chuong_trinh_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), nullable=False)
    cong_thuc_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), nullable=False)
    to_hop_id: Mapped[int | None] = mapped_column(Integer)
    kieu_tinh: Mapped[str] = mapped_column(String(20), nullable=False)
    thang_diem: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    diem_goc: Mapped[Decimal | None] = mapped_column(Numeric(9, 4))
    tb_mon: Mapped[Decimal | None] = mapped_column(Numeric(6, 3))
    tong_thpt_to_hop: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    diem_cong: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False, default=0, server_default="0")
    diem_uu_tien: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False, default=0, server_default="0")
    diem_xet: Mapped[Decimal | None] = mapped_column(Numeric(7, 2))
    dat_nguong: Mapped[bool | None] = mapped_column(Boolean)
    so_nhom_dieu_kien: Mapped[int] = mapped_column(SMALLINT(unsigned=True), nullable=False, default=0, server_default="0")
    so_nhom_dat: Mapped[int] = mapped_column(SMALLINT(unsigned=True), nullable=False, default=0, server_default="0")
    du_dieu_kien: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")
    ly_do_khong_dat: Mapped[str | None] = mapped_column(String(1000))
    diem_chuan_id: Mapped[int | None] = mapped_column(BIGINT(unsigned=True))
    diem_chuan_tham_chieu: Mapped[Decimal | None] = mapped_column(Numeric(7, 2))
    thang_diem_chuan: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    nam_diem_chuan: Mapped[int | None] = mapped_column(SMALLINT(unsigned=True))
    chenh_lech_30: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    chi_tiet: Mapped[str | None] = mapped_column(String(500))


class XtKetQuaChuongTrinh(Base):
    """Mức độ phù hợp của từng chương trình với học sinh (mỗi chương trình một dòng, theo phương án tốt nhất)."""

    __tablename__ = "xt_ket_qua_chuong_trinh"
    __table_args__ = (
        UniqueConstraint("lan_danh_gia_id", "de_an_chuong_trinh_id", name="uk_xt_kqct"),
        Index("idx_xt_kqct_xep_hang", "lan_danh_gia_id", "thu_hang"),
        Index("idx_xt_kqct_truong", "lan_danh_gia_id", "ma_truong"),
        _BANG,
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    lan_danh_gia_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("xt_lan_danh_gia.id", name="fk_xt_kqct_lan_danh_gia_id", ondelete="CASCADE"),
        nullable=False,
    )
    de_an_chuong_trinh_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), nullable=False)
    ma_truong: Mapped[str] = mapped_column(String(20), nullable=False)
    ket_qua_phuong_an_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("xt_ket_qua_phuong_an.id", name="fk_xt_kqct_ket_qua_phuong_an_id", ondelete="CASCADE"),
        nullable=False,
    )
    la_xet_thang: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")
    diem_xet: Mapped[Decimal | None] = mapped_column(Numeric(7, 2))
    thang_diem: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    chenh_lech_30: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    diem_kha_nang: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    diem_nganh: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    diem_hoc_phi: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    diem_vi_tri: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    diem_phu_hop: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    xep_loai: Mapped[str | None] = mapped_column(String(50))
    thu_hang: Mapped[int | None] = mapped_column(INTEGER(unsigned=True))
