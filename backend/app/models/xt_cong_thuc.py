from decimal import Decimal

from sqlalchemy import Boolean, Enum, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT, TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

_BANG = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}

KIEU_TINH = ("TO_HOP_MON", "THANH_PHAN", "CHI_DIEU_KIEN", "THU_CONG")


class XtCongThuc(Base):
    """Công thức tính điểm xét tuyển của đề án.

    kieu_tinh: TO_HOP_MON tổng có hệ số các môn của tổ hợp; THANH_PHAN tổng các thành phần bài thi / chứng chỉ quy
    đổi; CHI_DIEU_KIEN chỉ xét điều kiện (xét tuyển thẳng); THU_CONG có điểm nhưng hệ thống chưa tự tính.
    """

    __tablename__ = "xt_cong_thuc"
    __table_args__ = (
        UniqueConstraint("de_an_id", "ma_cong_thuc", name="uk_xt_cong_thuc"),
        Index("idx_xt_cong_thuc_ma_phuong_thuc", "ma_phuong_thuc_cua_bo"),
        _BANG,
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    de_an_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("dats_tuyen_sinh.id", name="fk_xt_cong_thuc_de_an_id"), nullable=False
    )
    ma_cong_thuc: Mapped[str] = mapped_column(String(50), nullable=False)
    ten_cong_thuc: Mapped[str] = mapped_column(String(255), nullable=False)
    ma_phuong_thuc_cua_bo: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("dm_phuong_thuc_tuyen_sinh.ma_phuong_thuc", name="fk_xt_cong_thuc_ma_phuong_thuc"),
        nullable=False,
    )
    kieu_tinh: Mapped[str] = mapped_column(Enum(*KIEU_TINH, name="kieu_tinh"), nullable=False)
    nguon_diem_mon: Mapped[str | None] = mapped_column(Enum("THI_THPT", "HOC_BA", name="nguon_diem_mon"))
    thay_ngoai_ngu: Mapped[str] = mapped_column(
        Enum("KHONG", "DUOC_PHEP", "BAT_BUOC", name="thay_ngoai_ngu"),
        nullable=False,
        default="KHONG",
        server_default="KHONG",
    )
    bang_quy_doi_ngoai_ngu_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("xt_bang_quy_doi.id", name="fk_xt_cong_thuc_bang_quy_doi")
    )
    thang_diem: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False, default=30, server_default="30")
    he_so_nhan: Mapped[Decimal] = mapped_column(Numeric(12, 8), nullable=False, default=1, server_default="1")
    nguong_tb_mon: Mapped[Decimal | None] = mapped_column(Numeric(4, 2))
    nguong_thpt_to_hop: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    diem_san: Mapped[Decimal | None] = mapped_column(Numeric(7, 2))
    ap_dung_diem_cong: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="1")
    ap_dung_uu_tien: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="1")
    ty_le_diem_cong_toi_da: Mapped[Decimal] = mapped_column(
        Numeric(4, 3), nullable=False, default=Decimal("0.1"), server_default="0.1"
    )
    so_le_lam_tron: Mapped[int] = mapped_column(TINYINT(unsigned=True), nullable=False, default=2, server_default="2")
    mo_ta_cong_thuc: Mapped[str | None] = mapped_column(Text)
    trang_thai: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="1")
    ghi_chu: Mapped[str | None] = mapped_column(Text)


class XtCongThucHeSoMon(Base):
    """Hệ số môn của công thức TO_HOP_MON; môn không khai báo có hệ số 1, hệ số theo môn ưu tiên hơn theo nhóm."""

    __tablename__ = "xt_cong_thuc_he_so_mon"
    __table_args__ = (Index("idx_xt_cong_thuc_he_so_mon", "cong_thuc_id", "mon_hoc_id"), _BANG)

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    cong_thuc_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("xt_cong_thuc.id", name="fk_xt_cthsm_cong_thuc_id", ondelete="CASCADE"),
        nullable=False,
    )
    mon_hoc_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("dm_mon_hoc.id", name="fk_xt_cthsm_mon_hoc_id"))
    nhom_mon: Mapped[str | None] = mapped_column(String(50))
    he_so: Mapped[Decimal] = mapped_column(Numeric(6, 3), nullable=False)


class XtCongThucThanhPhan(Base):
    """Thành phần điểm của công thức THANH_PHAN; các dòng cùng vi_tri thay thế nhau, lấy giá trị cao nhất."""

    __tablename__ = "xt_cong_thuc_thanh_phan"
    __table_args__ = (Index("idx_xt_cong_thuc_thanh_phan", "cong_thuc_id", "vi_tri"), _BANG)

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    cong_thuc_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("xt_cong_thuc.id", name="fk_xt_cttp_cong_thuc_id", ondelete="CASCADE"),
        nullable=False,
    )
    vi_tri: Mapped[int] = mapped_column(TINYINT(unsigned=True), nullable=False)
    ten_thanh_phan: Mapped[str | None] = mapped_column(String(255))
    loai_nguon: Mapped[str] = mapped_column(Enum("BAI_THI", "CHUNG_CHI", name="loai_nguon"), nullable=False)
    bai_thi_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("dm_bai_thi_danh_gia.id", name="fk_xt_cttp_bai_thi_id")
    )
    bang_quy_doi_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("xt_bang_quy_doi.id", name="fk_xt_cttp_bang_quy_doi_id")
    )
    mon_hoc_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("dm_mon_hoc.id", name="fk_xt_cttp_mon_hoc_id"))
    he_so: Mapped[Decimal] = mapped_column(Numeric(6, 3), nullable=False, default=1, server_default="1")
    nam_thi_tu: Mapped[int | None] = mapped_column(SMALLINT(unsigned=True))
    nam_thi_den: Mapped[int | None] = mapped_column(SMALLINT(unsigned=True))
    yeu_cau_phan_tu_chon: Mapped[str | None] = mapped_column(String(50))
