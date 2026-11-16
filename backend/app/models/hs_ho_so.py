from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT, TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

_BANG = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


def _ho_so_id(table: str):
    return mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("hs_ho_so.id", name=f"fk_{table}_ho_so_id", ondelete="CASCADE"),
        nullable=False,
    )


class HsHoSo(Base):
    """Hồ sơ xét tuyển của học sinh. Thành viên theo nguoi_dung_id, khách theo ma_thiet_bi."""

    __tablename__ = "hs_ho_so"
    __table_args__ = (
        Index("idx_hs_ho_so_nguoi_dung_id", "nguoi_dung_id"),
        Index("idx_hs_ho_so_ma_thiet_bi", "ma_thiet_bi"),
        _BANG,
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    nguoi_dung_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("nguoi_dung.id", name="fk_hs_ho_so_nguoi_dung_id", ondelete="CASCADE")
    )
    ma_thiet_bi: Mapped[str | None] = mapped_column(String(64))
    ten_ho_so: Mapped[str | None] = mapped_column(String(150))
    # Hồ sơ dùng khi tìm trường phù hợp (một tài khoản có thể có nhiều hồ sơ giả định).
    la_ho_so_chinh: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="1")
    nam_tot_nghiep: Mapped[int | None] = mapped_column(SMALLINT(unsigned=True))
    da_tot_nghiep: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="1")
    chuong_trinh_thpt: Mapped[str] = mapped_column(
        Enum("GDPT_2018", "GDPT_2006", "NUOC_NGOAI", name="chuong_trinh_thpt"),
        nullable=False,
        default="GDPT_2018",
        server_default="GDPT_2018",
    )
    he_chuyen: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")
    mon_chuyen_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("dm_mon_hoc.id", name="fk_hs_ho_so_mon_chuyen_id")
    )
    ten_truong_thpt: Mapped[str | None] = mapped_column(String(255))
    tinh_thanh_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("dm_tinh_thanh.id", name="fk_hs_ho_so_tinh_thanh_id")
    )
    khu_vuc_uu_tien_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("dm_khu_vuc_uu_tien.id", name="fk_hs_ho_so_khu_vuc_uu_tien_id")
    )
    doi_tuong_uu_tien_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("dm_doi_tuong_uu_tien.id", name="fk_hs_ho_so_doi_tuong_uu_tien_id")
    )
    ngan_sach_hoc_phi_nam: Mapped[Decimal | None] = mapped_column(Numeric(15, 0))
    tao_luc: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    cap_nhat_luc: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class HsKetQuaNamHoc(Base):
    """Kết quả tổng kết từng năm THPT: điểm TB chung, học lực, rèn luyện (4 Tốt, 3 Khá, 2 Đạt, 1 Chưa đạt)."""

    __tablename__ = "hs_ket_qua_nam_hoc"
    __table_args__ = (UniqueConstraint("ho_so_id", "lop", name="uk_hs_ket_qua_nam_hoc"), _BANG)

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    ho_so_id: Mapped[int] = _ho_so_id("hs_ket_qua_nam_hoc")
    lop: Mapped[int] = mapped_column(TINYINT(unsigned=True), nullable=False)
    diem_tb_chung: Mapped[Decimal | None] = mapped_column(Numeric(4, 2))
    hoc_luc: Mapped[int | None] = mapped_column(TINYINT(unsigned=True))
    ren_luyen: Mapped[int | None] = mapped_column(TINYINT(unsigned=True))


class HsDiemMon(Base):
    """Điểm từng môn: thi tốt nghiệp THPT (lop = 0) và học bạ (lop 10/11/12, hoc_ky 0 = cả năm)."""

    __tablename__ = "hs_diem_mon"
    __table_args__ = (
        UniqueConstraint("ho_so_id", "nguon_diem", "mon_hoc_id", "lop", "hoc_ky", name="uk_hs_diem_mon"),
        Index("idx_hs_diem_mon_mon_hoc_id", "mon_hoc_id"),
        _BANG,
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    ho_so_id: Mapped[int] = _ho_so_id("hs_diem_mon")
    mon_hoc_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dm_mon_hoc.id", name="fk_hs_diem_mon_mon_hoc_id"), nullable=False
    )
    nguon_diem: Mapped[str] = mapped_column(Enum("THI_THPT", "HOC_BA", name="nguon_diem"), nullable=False)
    lop: Mapped[int] = mapped_column(TINYINT(unsigned=True), nullable=False, default=0, server_default="0")
    hoc_ky: Mapped[int] = mapped_column(TINYINT(unsigned=True), nullable=False, default=0, server_default="0")
    diem: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    nam: Mapped[int | None] = mapped_column(SMALLINT(unsigned=True))
    la_du_kien: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")


class HsDiemBaiThi(Base):
    """Kết quả bài thi đánh giá năng lực / tư duy, SAT, ACT."""

    __tablename__ = "hs_diem_bai_thi"
    __table_args__ = (
        Index("idx_hs_diem_bai_thi_ho_so_id", "ho_so_id", "bai_thi_id"),
        Index("idx_hs_diem_bai_thi_bai_thi_id", "bai_thi_id"),
        _BANG,
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    ho_so_id: Mapped[int] = _ho_so_id("hs_diem_bai_thi")
    bai_thi_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("dm_bai_thi_danh_gia.id", name="fk_hs_diem_bai_thi_bai_thi_id"), nullable=False
    )
    nam_thi: Mapped[int] = mapped_column(SMALLINT(unsigned=True), nullable=False)
    dot_thi: Mapped[str | None] = mapped_column(String(30))
    ngay_thi: Mapped[date | None] = mapped_column(Date)
    diem: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    phan_tu_chon: Mapped[str | None] = mapped_column(String(50))
    diem_thanh_phan: Mapped[dict | None] = mapped_column(JSON)


class HsChungChi(Base):
    """Chứng chỉ ngoại ngữ / quốc tế; ngay_het_han NULL = không thời hạn hoặc chưa biết."""

    __tablename__ = "hs_chung_chi"
    __table_args__ = (
        Index("idx_hs_chung_chi_ho_so_id", "ho_so_id", "chung_chi_id"),
        Index("idx_hs_chung_chi_chung_chi_id", "chung_chi_id"),
        _BANG,
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    ho_so_id: Mapped[int] = _ho_so_id("hs_chung_chi")
    chung_chi_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("dm_bang_cap_chung_chi.id", name="fk_hs_chung_chi_chung_chi_id"), nullable=False
    )
    diem: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    cap_do: Mapped[str | None] = mapped_column(String(30))
    ngay_cap: Mapped[date | None] = mapped_column(Date)
    ngay_het_han: Mapped[date | None] = mapped_column(Date)
    diem_thanh_phan: Mapped[dict | None] = mapped_column(JSON)


class HsThanhTich(Base):
    """Giải thưởng: muc_giai 1 Nhất/Vàng, 2 Nhì/Bạc, 3 Ba/Đồng, 4 Khuyến khích/Tư, 9 tham gia."""

    __tablename__ = "hs_thanh_tich"
    __table_args__ = (
        Index("idx_hs_thanh_tich_ho_so_id", "ho_so_id", "thanh_tich_id"),
        Index("idx_hs_thanh_tich_thanh_tich_id", "thanh_tich_id"),
        _BANG,
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    ho_so_id: Mapped[int] = _ho_so_id("hs_thanh_tich")
    thanh_tich_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dm_thanh_tich_hoc_tap_nghien_cuu.id", name="fk_hs_thanh_tich_thanh_tich_id"),
        nullable=False,
    )
    mon_hoc_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("dm_mon_hoc.id", name="fk_hs_thanh_tich_mon_hoc_id")
    )
    linh_vuc: Mapped[str | None] = mapped_column(String(150))
    muc_giai: Mapped[int] = mapped_column(TINYINT(unsigned=True), nullable=False)
    nam_dat_giai: Mapped[int | None] = mapped_column(SMALLINT(unsigned=True))
    lop: Mapped[int | None] = mapped_column(TINYINT(unsigned=True))


LOAI_MONG_MUON = ("NGANH", "NHOM_NGANH", "LINH_VUC", "TINH_THANH", "VUNG_MIEN", "LOAI_HINH_TRUONG")


class HsTieuChiMongMuon(Base):
    """Ngành, địa điểm, loại trường học sinh mong muốn (lọc và chấm điểm phù hợp)."""

    __tablename__ = "hs_tieu_chi_mong_muon"
    __table_args__ = (UniqueConstraint("ho_so_id", "loai", "gia_tri", name="uk_hs_tieu_chi_mong_muon"), _BANG)

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    ho_so_id: Mapped[int] = _ho_so_id("hs_tieu_chi_mong_muon")
    loai: Mapped[str] = mapped_column(Enum(*LOAI_MONG_MUON, name="loai_mong_muon"), nullable=False)
    gia_tri: Mapped[str] = mapped_column(String(100), nullable=False)
