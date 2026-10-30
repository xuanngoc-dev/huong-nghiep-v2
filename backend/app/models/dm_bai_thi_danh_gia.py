from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    DateTime,
    Index,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DmBaiThiDanhGia(Base):
    """Danh mục các bài thi đánh giá."""

    __tablename__ = "dm_bai_thi_danh_gia"
    __table_args__ = (
        Index("idx_dm_bai_thi_danh_gia_ma_bai_thi", "ma_bai_thi"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Danh mục các bài thi đánh giá",
        },
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
        comment="Khóa chính, tự tăng.",
    )
    ma_bai_thi: Mapped[str | None] = mapped_column(
        String(30),
        comment="Mã định danh bài thi trong hệ thống.",
    )
    ten_bai_thi: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Tên chính thức của bài thi hoặc kỳ thi.",
    )
    ten_viet_tat: Mapped[str | None] = mapped_column(
        String(50),
        comment="Tên viết tắt thường dùng.",
    )
    don_vi_to_chuc: Mapped[str | None] = mapped_column(
        String(255),
        comment="Đơn vị tổ chức hoặc quản lý bài thi.",
    )
    loai_danh_gia: Mapped[str | None] = mapped_column(
        String(50),
        comment="Loại bài thi hoặc năng lực được đánh giá.",
    )
    mo_ta: Mapped[str | None] = mapped_column(
        Text,
        comment="Mô tả mục tiêu và phạm vi đánh giá của bài thi.",
    )
    doi_tuong_du_thi: Mapped[str | None] = mapped_column(
        Text,
        comment="Nhóm đối tượng có thể dự thi.",
    )
    hinh_thuc_thi: Mapped[dict | list | None] = mapped_column(
        JSON,
        comment="Các hình thức tổ chức có thể áp dụng.",
    )
    thang_diem: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 2),
        comment="Điểm tối đa của bài thi.",
    )
    diem_toi_thieu: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 2),
        comment="Điểm thấp nhất có thể ghi nhận, nếu xác định được.",
    )
    don_vi_diem: Mapped[str | None] = mapped_column(
        String(30),
        comment="Đơn vị hoặc cách biểu diễn điểm.",
    )
    cau_truc_bai_thi: Mapped[dict | list | None] = mapped_column(
        JSON,
        comment="Các phần thi, số câu, thời lượng hoặc trọng số.",
    )
    thoi_luong_phut: Mapped[int | None] = mapped_column(
        SMALLINT(unsigned=True),
        comment="Tổng thời lượng làm bài tính bằng phút.",
    )
    cach_cong_bo_ket_qua: Mapped[str | None] = mapped_column(
        Text,
        comment="Mô tả cách đơn vị tổ chức công bố kết quả, nếu có.",
    )
    nam_ap_dung_tu: Mapped[int | None] = mapped_column(
        SMALLINT(unsigned=True),
        comment="Năm bắt đầu có thông tin trong danh mục.",
    )
    nam_ap_dung_den: Mapped[int | None] = mapped_column(
        SMALLINT(unsigned=True),
        comment="Năm kết thúc áp dụng; để NULL nếu chưa xác định.",
    )
    website_chinh_thuc: Mapped[str | None] = mapped_column(
        String(1000),
        comment="Trang thông tin chính thức của bài thi hoặc đơn vị tổ chức.",
    )
    nguon_du_lieu_url: Mapped[str | None] = mapped_column(
        String(1000),
        comment="Đường dẫn nguồn dùng để xác minh thông tin.",
    )
    trang_thai: Mapped[str | None] = mapped_column(
        String(20),
        comment="Trạng thái của bài thi trong danh mục.",
    )
    ghi_chu: Mapped[str | None] = mapped_column(
        Text,
        comment="Ghi chú bổ sung.",
    )
    tao_luc: Mapped[datetime | None] = mapped_column(
        DateTime,
        comment="Thời điểm tạo bản ghi.",
    )
    cap_nhat_luc: Mapped[datetime | None] = mapped_column(
        DateTime,
        comment="Thời điểm cập nhật bản ghi gần nhất.",
    )
