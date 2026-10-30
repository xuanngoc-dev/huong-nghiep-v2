from sqlalchemy import (
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DatsChinhSachXetTuyenThang(Base):
    """Chính sách xét tuyển thẳng của đề án."""

    __tablename__ = "dats_chinh_sach_xet_tuyen_thang"
    __table_args__ = (
        Index("idx_dats_chinh_sach_xet_tuyen_thang_de_an_id", "de_an_id"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Chính sách xét tuyển thẳng của đề án",
        },
    )

    id: Mapped[int] = mapped_column(
        BIGINT(),
        primary_key=True,
        autoincrement=True,
        comment="Khóa chính của chính sách",
    )
    de_an_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "dats_tuyen_sinh.id",
            name="fk_dats_chinh_sach_xet_tuyen_thang_de_an_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        nullable=False,
        comment="Đề án tuyển sinh áp dụng chính sách",
    )
    ma_chinh_sach: Mapped[str | None] = mapped_column(
        String(50),
        comment="Mã chính sách do trường quy định",
    )
    ten_chinh_sach: Mapped[str | None] = mapped_column(
        String(255),
        comment="Tên diện xét tuyển thẳng",
    )
    nhom_doi_tuong: Mapped[str | None] = mapped_column(
        String(100),
        comment="Nhóm đối tượng theo quy định",
    )
    can_cu_phap_ly: Mapped[str | None] = mapped_column(
        String(255),
        comment="Căn cứ điều, khoản, điểm",
    )
    mo_ta_doi_tuong: Mapped[str | None] = mapped_column(
        Text,
        comment="Điều kiện cụ thể để thuộc diện này",
    )
    mon_thi_linh_vuc: Mapped[str | None] = mapped_column(
        String(255),
        comment="Môn thi, đề tài hoặc lĩnh vực thành tích",
    )
    cap_thi: Mapped[str | None] = mapped_column(
        String(100),
        comment="Cấp độ cuộc thi/thành tích",
    )
    muc_giai: Mapped[str | None] = mapped_column(
        String(100),
        comment="Giải thưởng yêu cầu",
    )
    thoi_han_thanh_tich_nam: Mapped[int | None] = mapped_column(
        SmallInteger,
        comment="Số năm thành tích được tính đến thời điểm xét",
    )
    pham_vi_chuong_trinh: Mapped[str | None] = mapped_column(
        Text,
        comment="Ngành/chương trình được áp dụng",
    )
    dieu_kien_phu: Mapped[str | None] = mapped_column(
        Text,
        comment="Ngưỡng đầu vào hoặc điều kiện bổ sung của trường",
    )
    chi_tieu_tuyen_thang: Mapped[int | None] = mapped_column(
        Integer,
        comment="Số lượng tuyển theo diện này; để trống nếu không công bố riêng",
    )
    ho_so_minh_chung: Mapped[str | None] = mapped_column(
        Text,
        comment="Giấy tờ thí sinh phải nộp",
    )
    thu_tu_tieu_chi_xet: Mapped[str | None] = mapped_column(
        Text,
        comment="Thứ tự tiêu chí khi cần xếp hạng thí sinh",
    )
    tieu_chi_phu_khi_dong_diem: Mapped[str | None] = mapped_column(
        Text,
        comment="Tiêu chí xử lý khi các thí sinh bằng điểm/đồng hạng",
    )
    nguyen_tac_khi_vuot_chi_tieu: Mapped[str | None] = mapped_column(
        Text,
        comment="Cách xử lý khi số thí sinh đủ điều kiện vượt chỉ tiêu",
    )
    thoi_gian_nhan_ho_so: Mapped[str | None] = mapped_column(
        String(255),
        comment="Thời gian nhận hồ sơ",
    )
    trang_thai: Mapped[str | None] = mapped_column(
        String(20),
        comment="Trạng thái chính sách",
    )
    ghi_chu: Mapped[str | None] = mapped_column(
        Text,
        comment="Thông tin bổ sung",
    )
