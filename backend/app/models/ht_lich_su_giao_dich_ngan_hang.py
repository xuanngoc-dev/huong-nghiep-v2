from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, Numeric, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class HtLichSuGiaoDichNganHang(Base):
    """Biến động số dư (tiền vào/ra) ở các tài khoản ngân hàng, nhận qua webhook (SePay).

    Giao dịch tiền vào có mã giao dịch nạp tiền trong nội dung được đối soát tự động với ht_lich_su_nap_tien.
    """

    __tablename__ = "ht_lich_su_giao_dich_ngan_hang"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
        "mysql_engine": "InnoDB",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # id giao dịch phía cổng (SePay `id`), duy nhất để webhook gửi lại không bị lưu trùng.
    ma_giao_dich_cong: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    # Tên ngân hàng phía cổng (`gateway`), ví dụ Vietcombank.
    ngan_hang: Mapped[str | None] = mapped_column(String(100))
    thoi_gian_giao_dich: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    so_tai_khoan: Mapped[str | None] = mapped_column(String(50), index=True)
    tai_khoan_phu: Mapped[str | None] = mapped_column(String(50))
    # Mã thanh toán cổng nhận diện được trong nội dung (`code`).
    ma_thanh_toan: Mapped[str | None] = mapped_column(String(100), index=True)
    noi_dung: Mapped[str | None] = mapped_column(Text)
    # in: tiền vào, out: tiền ra
    loai_giao_dich: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    mo_ta: Mapped[str | None] = mapped_column(Text)
    so_tien: Mapped[Decimal] = mapped_column(Numeric(18, 0), nullable=False)
    so_du_luy_ke: Mapped[Decimal | None] = mapped_column(Numeric(18, 0))
    ma_tham_chieu: Mapped[str | None] = mapped_column(String(100), index=True)
    # Tài khoản nhận tiền của hệ thống khớp với `accountNumber`.
    ngan_hang_thanh_toan_id: Mapped[int | None] = mapped_column(
        ForeignKey("ht_ngan_hang_thanh_toan.id", ondelete="SET NULL"),
    )
    # Giao dịch nạp tiền được đối soát với khoản tiền này.
    lich_su_nap_tien_id: Mapped[int | None] = mapped_column(
        ForeignKey("ht_lich_su_nap_tien.id", ondelete="SET NULL"),
        index=True,
    )
    # 0: chưa khớp giao dịch nạp, 1: đã khớp và cộng số dư, 2: tiền ra (không đối soát), 3: khớp nhưng thiếu tiền
    trang_thai_doi_soat: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default="0", index=True
    )
    ghi_chu_doi_soat: Mapped[str | None] = mapped_column(String(500))
    # Payload webhook gốc để tra soát.
    du_lieu_goc: Mapped[Any | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
