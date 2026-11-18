from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class HtLichSuNapTien(Base):
    """Lịch sử nạp tiền: mỗi lần người dùng bấm Đăng ký một gói cước sinh một giao dịch.

    Lưu bản chụp thông tin gói và tài khoản nhận tiền tại thời điểm đăng ký, để lịch sử không đổi
    khi admin sửa/xóa gói cước hoặc ngân hàng sau này.
    """

    __tablename__ = "ht_lich_su_nap_tien"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
        "mysql_engine": "InnoDB",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # Mã giao dịch nội bộ, duy nhất; dùng làm nội dung chuyển khoản để đối soát.
    ma_giao_dich: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    # Giữ lịch sử khi tài khoản bị xóa.
    nguoi_dung_id: Mapped[int | None] = mapped_column(
        ForeignKey("nguoi_dung.id", ondelete="SET NULL"),
        index=True,
    )

    # Gói cước đăng ký và bản chụp thông tin gói lúc đăng ký.
    goi_cuoc_dang_ky_id: Mapped[int | None] = mapped_column(
        ForeignKey("ht_cau_hinh_goi_cuoc.id", ondelete="SET NULL"),
        index=True,
    )
    ma_goi_cuoc: Mapped[str] = mapped_column(String(50), nullable=False)
    ten_goi_cuoc: Mapped[str] = mapped_column(String(255), nullable=False)
    # edu_coin, tra_cuu, khao_sat, hoi_dap, token
    loai_ap_dung: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Số Edu coin/lượt được cộng khi giao dịch thành công (đã tính khuyến mãi).
    so_luot_nhan_duoc: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    # Số tiền phải nạp (VNĐ, đã tính khuyến mãi) và số tiền thực nhận theo sao kê.
    so_tien_nap: Mapped[Decimal] = mapped_column(Numeric(15, 0), nullable=False)
    so_tien_thuc_nhan: Mapped[Decimal | None] = mapped_column(Numeric(15, 0))

    # Tài khoản nhận tiền người dùng chọn và bản chụp thông tin chuyển khoản.
    ngan_hang_thanh_toan_id: Mapped[int | None] = mapped_column(
        ForeignKey("ht_ngan_hang_thanh_toan.id", ondelete="SET NULL"),
    )
    ten_ngan_hang_viet_tat: Mapped[str | None] = mapped_column(String(50))
    so_tai_khoan_nhan: Mapped[str | None] = mapped_column(String(50))
    chu_tai_khoan_nhan: Mapped[str | None] = mapped_column(String(255))
    noi_dung_chuyen_khoan: Mapped[str | None] = mapped_column(String(255))
    # Mã tham chiếu của ngân hàng (trên sao kê/biên lai), nhập khi đối soát.
    ma_tham_chieu_ngan_hang: Mapped[str | None] = mapped_column(String(100), index=True)

    # 0: chờ thanh toán, 1: thành công (đã cộng Edu coin/lượt), 2: đã hủy, 3: thất bại
    trang_thai: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default="0", index=True
    )
    thoi_gian_thanh_toan: Mapped[datetime | None] = mapped_column(DateTime)
    thoi_gian_xac_nhan: Mapped[datetime | None] = mapped_column(DateTime)
    # Admin xác nhận/từ chối giao dịch.
    nguoi_xac_nhan_id: Mapped[int | None] = mapped_column(
        ForeignKey("nguoi_dung.id", ondelete="SET NULL"),
    )
    ghi_chu: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
