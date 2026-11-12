from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import JSON, DateTime, Index, Numeric, String, Text, UniqueConstraint, func, text
from sqlalchemy.dialects.mysql import BIGINT, ENUM, INTEGER, SMALLINT, TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

LOAI_LUOT = ("mien_phi", "tra_phi", "khuyen_mai")
TRANG_THAI_XU_LY = ("cho_xu_ly", "dang_xu_ly", "thanh_cong", "that_bai")


class TnLichSuTimTruongPhuHop(Base):
    """Một lượt tìm trường phù hợp của tài khoản: dữ liệu đầu vào, kết quả, lượt và mở khóa báo cáo."""

    __tablename__ = "tn_lich_su_tim_truong_phu_hop"
    __table_args__ = (
        UniqueConstraint("ma_yeu_cau", name="uq_tn_lich_su_tim_truong_ma_yeu_cau"),
        # Đếm lượt đã dùng trong ngày của một tài khoản.
        Index("idx_tn_lich_su_tim_truong_tai_khoan_ngay", "tai_khoan_id", "ngay_tao"),
        Index("idx_tn_lich_su_tim_truong_thiet_bi_ngay", "ma_thiet_bi", "ngay_tao"),
        Index("idx_tn_lich_su_tim_truong_ma_nganh", "ma_nganh", "nam_tuyen_sinh"),
        Index("idx_tn_lich_su_tim_truong_trang_thai", "trang_thai_xu_ly"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
        },
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    # Không đặt khóa ngoại: nguoi_dung.id là INT nên không khớp kiểu BIGINT UNSIGNED. Trống nếu là khách.
    tai_khoan_id: Mapped[int | None] = mapped_column(BIGINT(unsigned=True))
    # Khách vãng lai: mã thiết bị do trình duyệt sinh để đếm lượt, và thông tin liên hệ khách tự nhập.
    ma_thiet_bi: Mapped[str | None] = mapped_column(String(64))
    thong_tin_khach: Mapped[Any | None] = mapped_column(JSON)
    # Mã yêu cầu do client sinh, gửi lại cùng mã thì không xử lý và trừ lượt lần nữa.
    ma_yeu_cau: Mapped[str] = mapped_column(String(64), nullable=False)
    ma_nganh: Mapped[str] = mapped_column(String(20), nullable=False)
    nam_tuyen_sinh: Mapped[int] = mapped_column(SMALLINT(unsigned=True), nullable=False)
    # Điểm thi thử THPT, học bạ, ĐGNL, chứng chỉ.
    du_lieu_nang_luc: Mapped[Any] = mapped_column(JSON, nullable=False)
    # Khả năng tài chính, học phí và chi phí sinh hoạt.
    du_lieu_tai_chinh: Mapped[Any] = mapped_column(JSON, nullable=False)
    # Khu vực, loại hình trường và ưu tiên khác.
    tieu_chi_tim_kiem: Mapped[Any] = mapped_column(JSON, nullable=False)
    so_truong_tim_thay: Mapped[int] = mapped_column(
        INTEGER(unsigned=True), nullable=False, default=0, server_default="0"
    )
    so_truong_phu_hop_so_bo: Mapped[int] = mapped_column(
        INTEGER(unsigned=True), nullable=False, default=0, server_default="0"
    )
    # Danh sách các trường tìm thấy và kết quả đánh giá.
    du_lieu_ket_qua: Mapped[Any | None] = mapped_column(JSON)
    phien_ban_thuat_toan: Mapped[str | None] = mapped_column(String(50))
    loai_luot: Mapped[str] = mapped_column(
        ENUM(*LOAI_LUOT), nullable=False, default="mien_phi", server_default="mien_phi"
    )
    da_tinh_luot: Mapped[bool] = mapped_column(TINYINT(1), nullable=False, default=0, server_default="0")
    da_mo_khoa_chuyen_sau: Mapped[bool] = mapped_column(
        TINYINT(1), nullable=False, default=0, server_default="0"
    )
    # Giá báo cáo chuyên sâu tại thời điểm mua (VNĐ).
    gia_bao_cao_tai_thoi_diem: Mapped[Decimal | None] = mapped_column(Numeric(15, 0))
    giao_dich_thanh_toan_id: Mapped[int | None] = mapped_column(BIGINT(unsigned=True))
    ngay_mo_khoa: Mapped[datetime | None] = mapped_column(DateTime)
    trang_thai_xu_ly: Mapped[str] = mapped_column(
        ENUM(*TRANG_THAI_XU_LY), nullable=False, default="cho_xu_ly", server_default="cho_xu_ly"
    )
    thong_bao_loi: Mapped[str | None] = mapped_column(Text)
    ngay_hoan_thanh: Mapped[datetime | None] = mapped_column(DateTime)
    ngay_tao: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    ngay_cap_nhat: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        onupdate=func.now(),
    )
