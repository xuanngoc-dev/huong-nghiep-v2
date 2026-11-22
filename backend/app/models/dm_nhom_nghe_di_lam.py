from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

_BANG = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}

LOAI_HINH_DAU_VAO = ("di_lam_ngay", "hoc_nghe_ngan_han", "tu_hoc_ky_nang")
NHOM_MUC_TIEU = ("kiem_tien_ngay", "nghe_vung_chac", "thu_nhap_dot_pha")
CHU_KY_LUONG = ("gio", "ngay", "thang", "nam")
MUC_DO_AP_LUC = ("thap", "trung_binh", "cao")


class DmNhomNgheDiLam(Base):
    """Danh mục nhóm nghề cho học sinh đi làm ngay sau THPT (không học đại học)."""

    __tablename__ = "dm_nhom_nghe_di_lam"
    __table_args__ = _BANG

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ma_nhom: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    ten_nhom: Mapped[str] = mapped_column(String(255), nullable=False)
    mo_ta_dac_diem: Mapped[str] = mapped_column(Text, nullable=False)
    loai_hinh_dau_vao: Mapped[str | None] = mapped_column(Enum(*LOAI_HINH_DAU_VAO, name="loai_hinh_dau_vao"))
    thoi_gian_dao_tao_text: Mapped[str | None] = mapped_column(String(100))
    thoi_gian_dao_tao_thang_min: Mapped[int | None] = mapped_column(Integer)
    thoi_gian_dao_tao_thang_max: Mapped[int | None] = mapped_column(Integer)
    dieu_kien_dau_vao: Mapped[str | None] = mapped_column(Text)
    # Lương tính bằng triệu đồng/tháng.
    muc_luong_text: Mapped[str | None] = mapped_column(String(100))
    luong_khoi_diem_min: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    luong_khoi_diem_max: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    luong_kinh_nghiem_max: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    danh_gia_trien_vong: Mapped[str | None] = mapped_column(String(255))
    lo_trinh_phat_trien: Mapped[str | None] = mapped_column(Text)
    nhom_muc_tieu: Mapped[str | None] = mapped_column(Enum(*NHOM_MUC_TIEU, name="nhom_muc_tieu"))
    # Mã Holland ghép, ví dụ "RC", "ES".
    ma_holland: Mapped[str | None] = mapped_column(String(20))
    # Các mục giới thiệu nhóm nghề cho học sinh (hiển thị ở trang chi tiết nhóm nghề).
    nganh_nay_la_gi: Mapped[str | None] = mapped_column(Text)
    noi_lam_viec_o_dau: Mapped[str | None] = mapped_column(Text)
    cong_viec_hang_ngay_nhu_the_nao: Mapped[str | None] = mapped_column(Text)
    ap_luc_va_rui_ro: Mapped[str | None] = mapped_column(Text)
    xu_huong_tuong_lai: Mapped[str | None] = mapped_column(Text)
    ket_luan: Mapped[str | None] = mapped_column(Text)
    # URL hình ảnh mô tả nhóm nghề.
    hinh_anh_mo_ta: Mapped[str | None] = mapped_column(String(500))
    # 0: ngừng sử dụng, 1: hoạt động
    trang_thai: Mapped[int] = mapped_column(TINYINT, nullable=False, default=1, server_default="1")
    ngay_tao: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    ngay_cap_nhat: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )


class DmNgheCuTheDiLam(Base):
    """Nghề cụ thể thuộc một nhóm nghề đi làm."""

    __tablename__ = "dm_nghe_cu_the_di_lam"
    __table_args__ = _BANG

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nhom_nghe_di_lam_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dm_nhom_nghe_di_lam.id", name="fk_dm_ncdl_nhom_nghe_di_lam_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ten_nghe: Mapped[str] = mapped_column(String(255), nullable=False)
    mo_ta_ngan: Mapped[str | None] = mapped_column(Text)
    yeu_cau_them: Mapped[str | None] = mapped_column(String(500))
    # Bằng cấp / chứng chỉ bắt buộc để hành nghề (vd. "Bằng tốt nghiệp trường Công an nhân dân"); null: không yêu cầu.
    yeu_cau_bang_cap: Mapped[str | None] = mapped_column(String(255))
    # 1: phải qua đào tạo chính quy (trường công an, quân đội, y...), không đi làm ngay được; null: không bắt buộc.
    bat_buoc_dao_tao_chinh_quy: Mapped[int | None] = mapped_column(TINYINT)
    # URL hình ảnh mô tả nghề.
    hinh_anh_mo_ta: Mapped[str | None] = mapped_column(String(500))
    # Thông tin chi tiết nghề. Các mục dạng danh sách (vị trí, kỹ năng, chứng chỉ, từ khóa) ngăn cách bằng "; ".
    mo_ta_cong_viec: Mapped[str | None] = mapped_column(Text)
    trach_nhiem_chinh: Mapped[str | None] = mapped_column(Text)
    vi_tri_tuyen_dung_mau: Mapped[str | None] = mapped_column(Text)
    hinh_thuc_dao_tao: Mapped[str | None] = mapped_column(String(255))
    trinh_do_toi_thieu: Mapped[str | None] = mapped_column(String(100))
    chuyen_nganh_phu_hop: Mapped[str | None] = mapped_column(Text)
    ky_nang_chuyen_mon: Mapped[str | None] = mapped_column(Text)
    ky_nang_mem: Mapped[str | None] = mapped_column(Text)
    chung_chi_giay_phep: Mapped[str | None] = mapped_column(Text)
    # Lương tính theo đơn vị don_vi_tien_te (mặc định VND, số tiền đầy đủ) cho mỗi chu_ky_luong.
    luong_khoi_diem_min: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    luong_khoi_diem_max: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    luong_trung_binh_min: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    luong_trung_binh_max: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    luong_cao_min: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    luong_cao_max: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    don_vi_tien_te: Mapped[str] = mapped_column(String(10), nullable=False, default="VND", server_default="VND")
    chu_ky_luong: Mapped[str] = mapped_column(
        Enum(*CHU_KY_LUONG, name="chu_ky_luong"), nullable=False, default="thang", server_default="thang"
    )
    ghi_chu_luong: Mapped[str | None] = mapped_column(String(500))
    moi_truong_lam_viec: Mapped[str | None] = mapped_column(Text)
    dac_thu_thoi_gian: Mapped[str | None] = mapped_column(String(500))
    muc_do_ap_luc: Mapped[str | None] = mapped_column(Enum(*MUC_DO_AP_LUC, name="muc_do_ap_luc"))
    yeu_cau_suc_khoe: Mapped[str | None] = mapped_column(String(500))
    trien_vong_nghe_nghiep: Mapped[str | None] = mapped_column(Text)
    lo_trinh_phat_trien: Mapped[str | None] = mapped_column(Text)
    # Mã Holland ghép, ví dụ "RC".
    nhom_holland: Mapped[str | None] = mapped_column(String(20))
    tu_khoa_tim_kiem: Mapped[str | None] = mapped_column(String(500))


class DmTieuChiGoiY(Base):
    """Danh mục tiêu chí dùng để gợi ý nhóm nghề đi làm (sở thích, năng lực, hoàn cảnh, mục tiêu)."""

    __tablename__ = "dm_tieu_chi_goi_y"
    __table_args__ = _BANG

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ma_tieu_chi: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    ten_tieu_chi: Mapped[str] = mapped_column(String(255), nullable=False)
    nhom_tieu_chi: Mapped[str | None] = mapped_column(String(100))


class DmNhomNgheTieuChi(Base):
    """Mức độ phù hợp (1-5) giữa nhóm nghề đi làm và tiêu chí gợi ý."""

    __tablename__ = "dm_nhom_nghe_tieu_chi"
    __table_args__ = (
        CheckConstraint("diem_phu_hop BETWEEN 1 AND 5", name="chk_dm_nhom_nghe_tieu_chi_diem"),
        _BANG,
    )

    nhom_nghe_di_lam_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dm_nhom_nghe_di_lam.id", name="fk_dm_nntc_nhom_nghe_di_lam_id", ondelete="CASCADE"),
        primary_key=True,
    )
    tieu_chi_goi_y_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dm_tieu_chi_goi_y.id", name="fk_dm_nntc_tieu_chi_goi_y_id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    diem_phu_hop: Mapped[int | None] = mapped_column(TINYINT)
    ghi_chu: Mapped[str | None] = mapped_column(String(500))
