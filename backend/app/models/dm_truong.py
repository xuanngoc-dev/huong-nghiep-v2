from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DmTruong(Base):
    """Thông tin các trường học."""

    __tablename__ = "dm_truong"
    __table_args__ = (
        UniqueConstraint("ma_truong", name="uk_dm_truong_ma_truong"),
        Index("idx_dm_truong_slug", "slug"),
        Index("idx_dm_truong_loai_co_so_vung_mien", "loai_co_so", "vung_mien"),
        Index("idx_dm_truong_truong_cha_id", "truong_cha_id"),
        CheckConstraint("vi_do IS NULL OR (vi_do BETWEEN -90 AND 90)", name="chk_dm_truong_vi_do"),
        CheckConstraint("kinh_do IS NULL OR (kinh_do BETWEEN -180 AND 180)", name="chk_dm_truong_kinh_do"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Thông tin các trường học",
        },
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
        comment="Khóa chính, tự tăng, dùng liên kết với các bảng khác.",
    )
    ma_truong: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Mã trường do cơ quan quản lý quy định.",
    )
    ten_truong: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Tên tiếng Việt chính thức.",
    )
    ten_tieng_anh: Mapped[str | None] = mapped_column(
        String(255),
        comment="Tên tiếng Anh chính thức.",
    )
    ten_viet_tat: Mapped[str | None] = mapped_column(
        String(50),
        comment="Tên viết tắt thường dùng.",
    )
    ten_goi_khac: Mapped[dict | list | None] = mapped_column(
        JSON,
        comment="Danh sách tên cũ hoặc tên thường gọi, hỗ trợ tìm kiếm.",
    )
    slug: Mapped[str | None] = mapped_column(
        String(255),
        comment="Định danh dùng trong đường dẫn trang thông tin trường.",
    )
    loai_co_so: Mapped[str | None] = mapped_column(
        String(50),
        comment="Phân loại cơ sở giáo dục: cao đẳng, trường đại học, đại học, học viện.",
    )
    loai_hinh: Mapped[str | None] = mapped_column(
        String(50),
        comment="Loại hình sở hữu: công lập, tư thục hoặc có vốn đầu tư nước ngoài.",
    )
    co_quan_chu_quan: Mapped[str | None] = mapped_column(
        String(255),
        comment="Cơ quan hoặc tổ chức chủ quản, nếu có.",
    )
    truong_cha_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "dm_truong.id",
            name="fk_dm_truong_truong_cha_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        comment="ID của đại học mà trường trực thuộc; tham chiếu dm_truong.id.",
    )
    ngay_thanh_lap: Mapped[date | None] = mapped_column(
        Date,
        comment="Ngày thành lập chính thức, nếu biết đầy đủ ngày, tháng, năm.",
    )
    nam_thanh_lap: Mapped[int | None] = mapped_column(
        SMALLINT(unsigned=True),
        comment="Năm thành lập; vẫn lưu được khi chưa biết ngày và tháng.",
    )
    gioi_thieu_ngan: Mapped[str | None] = mapped_column(
        String(1000),
        comment="Mô tả ngắn để hiển thị trong danh sách trường.",
    )
    gioi_thieu_chi_tiet: Mapped[str | None] = mapped_column(
        Text,
        comment="Nội dung giới thiệu đầy đủ về lịch sử, hoạt động và định hướng phát triển.",
    )
    the_manh: Mapped[str | None] = mapped_column(
        Text,
        comment="Thế mạnh nổi bật về đào tạo, nghiên cứu hoặc hợp tác.",
    )
    bac_dao_tao: Mapped[dict | list | None] = mapped_column(
        JSON,
        comment="Danh sách các bậc đào tạo trường cung cấp.",
    )
    linh_vuc_dao_tao_chinh: Mapped[dict | list | None] = mapped_column(
        JSON,
        comment="Danh sách lĩnh vực đào tạo chính.",
    )
    linh_vuc_dao_tao_khac: Mapped[dict | list | None] = mapped_column(
        JSON,
        comment="Các lĩnh vực đào tạo khác ngoài lĩnh vực chính.",
    )
    ma_tinh_thanh: Mapped[str | None] = mapped_column(
        String(10),
        comment="Mã tỉnh/thành phố nơi đặt trụ sở chính.",
    )
    ten_tinh_thanh: Mapped[str | None] = mapped_column(
        String(100),
        comment="Tên tỉnh/thành phố của trụ sở chính.",
    )
    ma_phuong_xa: Mapped[str | None] = mapped_column(
        String(10),
        comment="Mã phường/xã của trụ sở chính.",
    )
    ten_phuong_xa: Mapped[str | None] = mapped_column(
        String(100),
        comment="Tên phường/xã của trụ sở chính.",
    )
    dia_chi_tru_so: Mapped[str | None] = mapped_column(
        String(500),
        comment="Địa chỉ đầy đủ của trụ sở chính.",
    )
    vung_mien: Mapped[str | None] = mapped_column(
        String(20),
        comment="Vùng miền để tìm kiếm, lọc trường.",
    )
    vi_do: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 7),
        comment="Vĩ độ trụ sở chính, phục vụ hiển thị trên bản đồ.",
    )
    kinh_do: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 7),
        comment="Kinh độ trụ sở chính.",
    )
    so_dien_thoai: Mapped[str | None] = mapped_column(
        String(30),
        comment="Số điện thoại liên hệ chung; lưu chuỗi để giữ số 0 đầu hoặc dấu +.",
    )
    email: Mapped[str | None] = mapped_column(
        String(255),
        comment="Email liên hệ chung.",
    )
    website: Mapped[str | None] = mapped_column(
        String(500),
        comment="Địa chỉ website chính thức.",
    )
    website_tuyen_sinh: Mapped[str | None] = mapped_column(
        String(500),
        comment="Địa chỉ trang thông tin tuyển sinh chính thức.",
    )
    hotline_tuyen_sinh: Mapped[str | None] = mapped_column(
        String(30),
        comment="Số điện thoại hỗ trợ tuyển sinh.",
    )
    email_tuyen_sinh: Mapped[str | None] = mapped_column(
        String(255),
        comment="Email hỗ trợ tuyển sinh.",
    )
    logo_url: Mapped[str | None] = mapped_column(
        String(1000),
        comment="Đường dẫn ảnh logo của trường.",
    )
    anh_dai_dien_url: Mapped[str | None] = mapped_column(
        String(1000),
        comment="Đường dẫn ảnh đại diện hoặc ảnh khuôn viên.",
    )
    dien_tich_m2: Mapped[Decimal | None] = mapped_column(
        Numeric(15, 2),
        comment="Diện tích tính bằng m²; cần thống nhất phạm vi đo.",
    )
    hoc_phi_trung_binh: Mapped[str | None] = mapped_column(
        String(100),
        comment="Mức học phí tham khảo.",
    )
    trang_thai_hoat_dong: Mapped[str | None] = mapped_column(
        String(30),
        comment="Trạng thái hoạt động của trường.",
    )
    nguon_du_lieu_url: Mapped[str | None] = mapped_column(
        String(1000),
        comment="Đường dẫn nguồn chính dùng để xác minh thông tin.",
    )
    ngay_xac_minh: Mapped[datetime | None] = mapped_column(
        DateTime,
        comment="Thời điểm gần nhất thông tin được kiểm tra với nguồn.",
    )
    ghi_chu: Mapped[str | None] = mapped_column(
        Text,
        comment="Thông tin bổ sung hoặc nội dung cần xác minh.",
    )
    tao_luc: Mapped[datetime | None] = mapped_column(
        DateTime,
        comment="Thời điểm tạo bản ghi.",
    )
    cap_nhat_luc: Mapped[datetime | None] = mapped_column(
        DateTime,
        comment="Thời điểm cập nhật bản ghi gần nhất.",
    )
