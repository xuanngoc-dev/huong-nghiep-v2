from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DmBangCapChungChi(Base):
    """Danh mục bằng cấp và chứng chỉ."""

    __tablename__ = "dm_bang_cap_chung_chi"
    __table_args__ = (
        UniqueConstraint("ma_chung_chi", name="uk_dm_bang_cap_chung_chi_ma_chung_chi"),
        CheckConstraint("thang_diem_min IS NULL OR thang_diem_max IS NULL OR thang_diem_max >= thang_diem_min", name="chk_dm_bang_cap_chung_chi_thang_diem_min"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Danh mục bằng cấp và chứng chỉ",
        },
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
        comment="Khóa chính, tự tăng.",
    )
    ma_chung_chi: Mapped[str | None] = mapped_column(
        String(30),
        comment="Mã định danh chứng chỉ trong hệ thống.",
    )
    ten_chung_chi: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        comment="Tên chứng chỉ.",
    )
    ma_ngon_ngu: Mapped[str | None] = mapped_column(
        String(10),
        comment="Mã ngôn ngữ được đánh giá.",
    )
    ten_ngon_ngu: Mapped[str | None] = mapped_column(
        String(100),
        comment="Tên ngôn ngữ được đánh giá.",
    )
    don_vi_cap: Mapped[str | None] = mapped_column(
        String(255),
        comment="Tổ chức cấp hoặc đồng sở hữu chứng chỉ.",
    )
    loai_chung_chi: Mapped[str | None] = mapped_column(
        String(50),
        comment="Nhóm hoặc loại chứng chỉ.",
    )
    thang_diem_min: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2),
        comment="Điểm thấp nhất của thang điểm chứng chỉ.",
    )
    thang_diem_max: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2),
        comment="Điểm cao nhất của thang điểm chứng chỉ.",
    )
    don_vi_diem: Mapped[str | None] = mapped_column(
        String(30),
        comment="Đơn vị ghi điểm của chứng chỉ.",
    )
    ky_nang_duoc_danh_gia: Mapped[dict | list | None] = mapped_column(
        JSON,
        comment="Danh sách kỹ năng được đánh giá.",
    )
    hinh_thuc_thi: Mapped[dict | list | None] = mapped_column(
        JSON,
        comment="Danh sách hình thức thi có thể có.",
    )
    ghi_chu_hinh_thuc_thi: Mapped[str | None] = mapped_column(
        Text,
        comment="Mô tả hoặc lưu ý về các hình thức thi.",
    )
    thoi_han_hieu_luc_thang: Mapped[int | None] = mapped_column(
        SMALLINT(unsigned=True),
        comment="Thời hạn hiệu lực tính bằng tháng, nếu có quy định thống nhất.",
    )
    trang_thai: Mapped[str | None] = mapped_column(
        String(20),
        comment="Trạng thái sử dụng trong danh mục.",
    )
    ghi_chu: Mapped[str | None] = mapped_column(
        Text,
        comment="Ghi chú chung về chứng chỉ hoặc cách xác minh.",
    )
    tao_luc: Mapped[datetime | None] = mapped_column(
        DateTime,
        comment="Thời điểm tạo bản ghi.",
    )
    cap_nhat_luc: Mapped[datetime | None] = mapped_column(
        DateTime,
        comment="Thời điểm cập nhật bản ghi gần nhất.",
    )
