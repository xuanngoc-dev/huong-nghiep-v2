from datetime import datetime

from sqlalchemy import JSON, DateTime, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TruongHocTuyenSinhTheoNam(Base):
    """Đề án tuyển sinh của một trường trong một năm.

    dieu_kien_chung và danh_sach_nganh giữ nguyên cấu trúc JSON nguồn.
    Mỗi ngành gồm mã ngành, mã xét tuyển, tên, chỉ tiêu, điều kiện,
    chương trình và danh sách phương thức. Mỗi phương thức gồm điểm sàn,
    điểm chuẩn, thang điểm, công thức, điểm ưu tiên, quy đổi điểm,
    điều kiện phụ và tổ hợp môn.
    """

    __tablename__ = "truong_hoc_tuyen_sinh_theo_nam"
    __table_args__ = (
        UniqueConstraint(
            "ma_truong",
            "nam_tuyen_sinh",
            name="uq_tuyen_sinh_nam_ma_truong_nam",
        ),
        Index("idx_tuyen_sinh_nam_nam", "nam_tuyen_sinh"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
        },
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    ma_truong: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Mã trường, cùng quy ước với dm_truong_dai_hoc.ma_truong",
    )
    ten_truong: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Tên trường trong đề án năm đó"
    )
    loai_hinh: Mapped[str | None] = mapped_column(
        String(50), comment="Loại hình trong đề án, ví dụ DaiHoc"
    )
    nam_tuyen_sinh: Mapped[int] = mapped_column(Integer, nullable=False, comment="Năm tuyển sinh")
    dieu_kien_chung: Mapped[list | None] = mapped_column(
        JSON,
        comment="Điều kiện chung của trường. Mỗi phần tử có loai, toan_tu, gia_tri",
    )
    danh_sach_nganh: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        comment=(
            "Danh sách ngành. Mỗi ngành có ma_nganh, ma_xet_tuyen, ten_nganh, "
            "ten_chuong_trinh, chi_tieu_nganh, dieu_kien_nganh và phuong_thuc_tuyen_sinh"
        ),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
