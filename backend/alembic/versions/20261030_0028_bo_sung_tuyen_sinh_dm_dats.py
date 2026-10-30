"""Bo sung bang va cot tuyen sinh tu docs/tuyen_sinh_mysql_dm.sql.

Cột NOT NULL được thêm vào bảng đã có dữ liệu được để NULL, gồm dm_doi_tuong_uu_tien.nam_ap_dung, dm_khu_vuc_uu_tien.nam_ap_dung, dm_mon_hoc.ma_mon và dm_mon_hoc.ten_mon.
Khóa ngoại tới bảng đã tồn tại dùng INT để khớp khóa chính hiện có, thay vì BIGINT UNSIGNED trong file thiết kế.
Bang da co giu nguyen kieu cot cu; chi them cot chua co.

Revision ID: 20261030_0028
Revises: 20261015_0027
Create Date: 2026-10-30 08:40:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision: str = "20261030_0028"
down_revision: Union[str, Sequence[str], None] = "20261015_0027"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Them cot con thieu, tao bang moi, roi tao chi muc va khoa ngoai."""
    op.add_column(
        "dm_nganh_dao_tao",
        sa.Column(
            "cap_danh_muc",
            sa.String(length=20),
            nullable=True,
            comment="Cấp của bản ghi trong hệ thống phân cấp.",
        ),
    )
    op.add_column(
        "dm_nganh_dao_tao",
        sa.Column(
            "nganh_cha_id",
            sa.Integer(),
            nullable=True,
            comment="ID lĩnh vực hoặc nhóm ngành cấp trên; tham chiếu dm_nganh_dao_tao.id. Để NULL nếu là cấp cao nhất.",
        ),
    )
    op.add_column(
        "dm_nganh_dao_tao",
        sa.Column(
            "trinh_do_ap_dung",
            sa.JSON(),
            nullable=True,
            comment="Các trình độ áp dụng theo danh mục hoặc dữ liệu đối chiếu.",
        ),
    )
    op.add_column(
        "dm_nganh_dao_tao",
        sa.Column(
            "ngay_hieu_luc_tu",
            sa.Date(),
            nullable=True,
            comment="Ngày bắt đầu hiệu lực của mã hoặc tên ngành.",
        ),
    )
    op.add_column(
        "dm_nganh_dao_tao",
        sa.Column(
            "ngay_hieu_luc_den",
            sa.Date(),
            nullable=True,
            comment="Ngày kết thúc hiệu lực, nếu có; để NULL nếu chưa xác định.",
        ),
    )
    op.add_column(
        "dm_nganh_dao_tao",
        sa.Column(
            "ghi_chu_theo_thong_tu",
            sa.Text(),
            nullable=True,
            comment="Ghi chú được nêu trong phụ lục danh mục ngành.",
        ),
    )
    op.add_column(
        "dm_nganh_dao_tao",
        sa.Column(
            "van_ban_id",
            mysql.BIGINT(unsigned=True),
            nullable=True,
            comment="ID văn bản nguồn; tham chiếu bảng văn bản pháp lý nếu có.",
        ),
    )
    op.add_column(
        "dm_nganh_dao_tao",
        sa.Column(
            "thu_tu_hien_thi",
            mysql.INTEGER(unsigned=True),
            nullable=True,
            comment="Thứ tự sắp xếp trong danh mục.",
        ),
    )
    op.add_column(
        "dm_nganh_dao_tao",
        sa.Column(
            "tao_luc",
            sa.DateTime(),
            nullable=True,
            comment="Thời điểm tạo bản ghi.",
        ),
    )
    op.add_column(
        "dm_nganh_dao_tao",
        sa.Column(
            "cap_nhat_luc",
            sa.DateTime(),
            nullable=True,
            comment="Thời điểm cập nhật gần nhất.",
        ),
    )
    op.add_column(
        "dm_ton_giao",
        sa.Column(
            "ten_goi_khac",
            sa.JSON(),
            nullable=True,
            comment="Tên gọi khác hoặc tên viết tắt.",
        ),
    )
    op.add_column(
        "dm_doi_tuong_uu_tien",
        sa.Column(
            "mo_ta_dieu_kien",
            sa.Text(),
            nullable=True,
            comment="Điều kiện để được hưởng ưu tiên.",
        ),
    )
    op.add_column(
        "dm_doi_tuong_uu_tien",
        sa.Column(
            "nhom_uu_tien",
            sa.String(length=10),
            nullable=True,
            comment="Nhóm ưu tiên.",
        ),
    )
    op.add_column(
        "dm_doi_tuong_uu_tien",
        sa.Column(
            "diem_uu_tien_co_ban",
            sa.Numeric(5, 2),
            nullable=True,
            comment="Mức điểm ưu tiên cơ bản theo thang điểm 30.",
        ),
    )
    op.add_column(
        "dm_doi_tuong_uu_tien",
        sa.Column(
            "nam_ap_dung",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Năm tuyển sinh áp dụng.",
        ),
    )
    op.add_column(
        "dm_doi_tuong_uu_tien",
        sa.Column(
            "van_ban_id",
            mysql.BIGINT(unsigned=True),
            nullable=True,
            comment="ID văn bản quy định, nếu có bảng văn bản.",
        ),
    )
    op.add_column(
        "dm_doi_tuong_uu_tien",
        sa.Column(
            "thu_tu_hien_thi",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Thứ tự hiển thị.",
        ),
    )
    op.add_column(
        "dm_khu_vuc_uu_tien",
        sa.Column(
            "mo_ta_dieu_kien",
            sa.Text(),
            nullable=True,
            comment="Mô tả địa bàn hoặc tiêu chí xác định khu vực.",
        ),
    )
    op.add_column(
        "dm_khu_vuc_uu_tien",
        sa.Column(
            "diem_uu_tien_co_ban",
            sa.Numeric(5, 2),
            nullable=True,
            comment="Mức điểm ưu tiên cơ bản theo thang điểm 30.",
        ),
    )
    op.add_column(
        "dm_khu_vuc_uu_tien",
        sa.Column(
            "nam_ap_dung",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Năm tuyển sinh áp dụng.",
        ),
    )
    op.add_column(
        "dm_khu_vuc_uu_tien",
        sa.Column(
            "van_ban_id",
            mysql.BIGINT(unsigned=True),
            nullable=True,
            comment="ID văn bản quy định, nếu có bảng văn bản.",
        ),
    )
    op.add_column(
        "dm_phuong_thuc_tuyen_sinh",
        sa.Column(
            "loai_phuong_thuc",
            sa.String(length=50),
            nullable=True,
            comment="Nhóm phương thức để phân loại.",
        ),
    )
    op.add_column(
        "dm_phuong_thuc_tuyen_sinh",
        sa.Column(
            "pham_vi_ap_dung",
            sa.String(length=30),
            nullable=True,
            comment="Phạm vi định nghĩa: danh mục chung hay phương thức riêng của trường.",
        ),
    )
    op.add_column(
        "dm_phuong_thuc_tuyen_sinh",
        sa.Column(
            "nam_ap_dung_tu",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Năm bắt đầu áp dụng bản ghi.",
        ),
    )
    op.add_column(
        "dm_phuong_thuc_tuyen_sinh",
        sa.Column(
            "nam_ap_dung_den",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Năm kết thúc áp dụng; để NULL nếu chưa xác định.",
        ),
    )
    op.add_column(
        "dm_phuong_thuc_tuyen_sinh",
        sa.Column(
            "thu_tu_hien_thi",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Thứ tự hiển thị trong giao diện.",
        ),
    )
    op.add_column(
        "dm_phuong_thuc_tuyen_sinh",
        sa.Column(
            "nguon_du_lieu_url",
            sa.String(length=1000),
            nullable=True,
            comment="Đường dẫn văn bản hoặc trang nguồn của thông tin.",
        ),
    )
    op.add_column(
        "dm_phuong_thuc_tuyen_sinh",
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Ghi chú quản trị hoặc nội dung cần kiểm tra.",
        ),
    )
    op.add_column(
        "dm_phuong_thuc_tuyen_sinh",
        sa.Column(
            "tao_luc",
            sa.DateTime(),
            nullable=True,
            comment="Thời điểm tạo bản ghi.",
        ),
    )
    op.add_column(
        "dm_phuong_thuc_tuyen_sinh",
        sa.Column(
            "cap_nhat_luc",
            sa.DateTime(),
            nullable=True,
            comment="Thời điểm cập nhật gần nhất.",
        ),
    )
    op.add_column(
        "dm_mon_hoc",
        sa.Column(
            "ma_mon",
            sa.String(length=20),
            nullable=True,
            comment="Mã định danh môn học.",
        ),
    )
    op.add_column(
        "dm_mon_hoc",
        sa.Column(
            "ten_mon",
            sa.String(length=100),
            nullable=True,
            comment="Tên môn học.",
        ),
    )
    op.add_column(
        "dm_mon_hoc",
        sa.Column(
            "ten_tieng_anh",
            sa.String(length=100),
            nullable=True,
            comment="Tên tiếng Anh, nếu có.",
        ),
    )
    op.add_column(
        "dm_mon_hoc",
        sa.Column(
            "ten_goi_khac",
            sa.JSON(),
            nullable=True,
            comment="Tên viết tắt hoặc tên gọi khác.",
        ),
    )
    op.add_column(
        "dm_mon_hoc",
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Ghi chú bổ sung.",
        ),
    )
    op.add_column(
        "dm_mon_hoc",
        sa.Column(
            "tao_luc",
            sa.DateTime(),
            nullable=True,
            comment="Thời điểm tạo bản ghi.",
        ),
    )
    op.add_column(
        "dm_mon_hoc",
        sa.Column(
            "cap_nhat_luc",
            sa.DateTime(),
            nullable=True,
            comment="Thời điểm cập nhật gần nhất.",
        ),
    )
    op.add_column(
        "dm_to_hop_mon_hoc",
        sa.Column(
            "mo_ta",
            sa.Text(),
            nullable=True,
            comment="Mô tả tổ hợp hoặc mục đích sử dụng.",
        ),
    )
    op.add_column(
        "dm_to_hop_mon_hoc",
        sa.Column(
            "nam_ap_dung_tu",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Năm bắt đầu áp dụng, nếu tổ hợp có thời hạn.",
        ),
    )
    op.add_column(
        "dm_to_hop_mon_hoc",
        sa.Column(
            "nam_ap_dung_den",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Năm kết thúc áp dụng; để NULL nếu chưa xác định.",
        ),
    )
    op.add_column(
        "dm_to_hop_mon_hoc",
        sa.Column(
            "tao_luc",
            sa.DateTime(),
            nullable=True,
            comment="Thời điểm tạo bản ghi.",
        ),
    )
    op.add_column(
        "dm_to_hop_mon_hoc",
        sa.Column(
            "cap_nhat_luc",
            sa.DateTime(),
            nullable=True,
            comment="Thời điểm cập nhật gần nhất.",
        ),
    )
    op.create_table(
        "dm_van_ban",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment="Khóa chính kỹ thuật của văn bản.",
        ),
        sa.Column(
            "so_ky_hieu",
            sa.String(length=100),
            nullable=True,
            comment="Số, ký hiệu văn bản được công bố.",
        ),
        sa.Column(
            "ten_van_ban",
            sa.String(length=500),
            nullable=True,
            comment="Tên đầy đủ hoặc trích yếu văn bản.",
        ),
        sa.Column(
            "loai_van_ban",
            sa.String(length=50),
            nullable=True,
            comment="Loại văn bản: thông tư, quyết định, quy chế,...",
        ),
        sa.Column(
            "co_quan_ban_hanh",
            sa.String(length=255),
            nullable=True,
            comment="Cơ quan ban hành văn bản.",
        ),
        sa.Column(
            "ngay_ban_hanh",
            sa.Date(),
            nullable=True,
            comment="Ngày ban hành văn bản nếu được công bố.",
        ),
        sa.Column(
            "ngay_hieu_luc",
            sa.Date(),
            nullable=True,
            comment="Ngày có hiệu lực nếu được công bố.",
        ),
        sa.Column(
            "nguon_du_lieu_url",
            sa.String(length=1000),
            nullable=True,
            comment="Đường dẫn văn bản gốc để xác minh.",
        ),
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Ghi chú hoặc phạm vi áp dụng.",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Văn bản quy phạm hoặc văn bản tham chiếu cho các danh mục (bổ sung thiết kế)",
    )
    op.create_table(
        "dm_truong",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment="Khóa chính, tự tăng, dùng liên kết với các bảng khác.",
        ),
        sa.Column(
            "ma_truong",
            sa.String(length=20),
            nullable=False,
            comment="Mã trường do cơ quan quản lý quy định.",
        ),
        sa.Column(
            "ten_truong",
            sa.String(length=255),
            nullable=False,
            comment="Tên tiếng Việt chính thức.",
        ),
        sa.Column(
            "ten_tieng_anh",
            sa.String(length=255),
            nullable=True,
            comment="Tên tiếng Anh chính thức.",
        ),
        sa.Column(
            "ten_viet_tat",
            sa.String(length=50),
            nullable=True,
            comment="Tên viết tắt thường dùng.",
        ),
        sa.Column(
            "ten_goi_khac",
            sa.JSON(),
            nullable=True,
            comment="Danh sách tên cũ hoặc tên thường gọi, hỗ trợ tìm kiếm.",
        ),
        sa.Column(
            "slug",
            sa.String(length=255),
            nullable=True,
            comment="Định danh dùng trong đường dẫn trang thông tin trường.",
        ),
        sa.Column(
            "loai_co_so",
            sa.String(length=50),
            nullable=True,
            comment="Phân loại cơ sở giáo dục: cao đẳng, trường đại học, đại học, học viện.",
        ),
        sa.Column(
            "loai_hinh",
            sa.String(length=50),
            nullable=True,
            comment="Loại hình sở hữu: công lập, tư thục hoặc có vốn đầu tư nước ngoài.",
        ),
        sa.Column(
            "co_quan_chu_quan",
            sa.String(length=255),
            nullable=True,
            comment="Cơ quan hoặc tổ chức chủ quản, nếu có.",
        ),
        sa.Column(
            "truong_cha_id",
            mysql.BIGINT(unsigned=True),
            nullable=True,
            comment="ID của đại học mà trường trực thuộc; tham chiếu dm_truong.id.",
        ),
        sa.Column(
            "ngay_thanh_lap",
            sa.Date(),
            nullable=True,
            comment="Ngày thành lập chính thức, nếu biết đầy đủ ngày, tháng, năm.",
        ),
        sa.Column(
            "nam_thanh_lap",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Năm thành lập; vẫn lưu được khi chưa biết ngày và tháng.",
        ),
        sa.Column(
            "gioi_thieu_ngan",
            sa.String(length=1000),
            nullable=True,
            comment="Mô tả ngắn để hiển thị trong danh sách trường.",
        ),
        sa.Column(
            "gioi_thieu_chi_tiet",
            sa.Text(),
            nullable=True,
            comment="Nội dung giới thiệu đầy đủ về lịch sử, hoạt động và định hướng phát triển.",
        ),
        sa.Column(
            "the_manh",
            sa.Text(),
            nullable=True,
            comment="Thế mạnh nổi bật về đào tạo, nghiên cứu hoặc hợp tác.",
        ),
        sa.Column(
            "bac_dao_tao",
            sa.JSON(),
            nullable=True,
            comment="Danh sách các bậc đào tạo trường cung cấp.",
        ),
        sa.Column(
            "linh_vuc_dao_tao_chinh",
            sa.JSON(),
            nullable=True,
            comment="Danh sách lĩnh vực đào tạo chính.",
        ),
        sa.Column(
            "linh_vuc_dao_tao_khac",
            sa.JSON(),
            nullable=True,
            comment="Các lĩnh vực đào tạo khác ngoài lĩnh vực chính.",
        ),
        sa.Column(
            "ma_tinh_thanh",
            sa.String(length=10),
            nullable=True,
            comment="Mã tỉnh/thành phố nơi đặt trụ sở chính.",
        ),
        sa.Column(
            "ten_tinh_thanh",
            sa.String(length=100),
            nullable=True,
            comment="Tên tỉnh/thành phố của trụ sở chính.",
        ),
        sa.Column(
            "ma_phuong_xa",
            sa.String(length=10),
            nullable=True,
            comment="Mã phường/xã của trụ sở chính.",
        ),
        sa.Column(
            "ten_phuong_xa",
            sa.String(length=100),
            nullable=True,
            comment="Tên phường/xã của trụ sở chính.",
        ),
        sa.Column(
            "dia_chi_tru_so",
            sa.String(length=500),
            nullable=True,
            comment="Địa chỉ đầy đủ của trụ sở chính.",
        ),
        sa.Column(
            "vung_mien",
            sa.String(length=20),
            nullable=True,
            comment="Vùng miền để tìm kiếm, lọc trường.",
        ),
        sa.Column(
            "vi_do",
            sa.Numeric(10, 7),
            nullable=True,
            comment="Vĩ độ trụ sở chính, phục vụ hiển thị trên bản đồ.",
        ),
        sa.Column(
            "kinh_do",
            sa.Numeric(10, 7),
            nullable=True,
            comment="Kinh độ trụ sở chính.",
        ),
        sa.Column(
            "so_dien_thoai",
            sa.String(length=30),
            nullable=True,
            comment="Số điện thoại liên hệ chung; lưu chuỗi để giữ số 0 đầu hoặc dấu +.",
        ),
        sa.Column(
            "email",
            sa.String(length=255),
            nullable=True,
            comment="Email liên hệ chung.",
        ),
        sa.Column(
            "website",
            sa.String(length=500),
            nullable=True,
            comment="Địa chỉ website chính thức.",
        ),
        sa.Column(
            "website_tuyen_sinh",
            sa.String(length=500),
            nullable=True,
            comment="Địa chỉ trang thông tin tuyển sinh chính thức.",
        ),
        sa.Column(
            "hotline_tuyen_sinh",
            sa.String(length=30),
            nullable=True,
            comment="Số điện thoại hỗ trợ tuyển sinh.",
        ),
        sa.Column(
            "email_tuyen_sinh",
            sa.String(length=255),
            nullable=True,
            comment="Email hỗ trợ tuyển sinh.",
        ),
        sa.Column(
            "logo_url",
            sa.String(length=1000),
            nullable=True,
            comment="Đường dẫn ảnh logo của trường.",
        ),
        sa.Column(
            "anh_dai_dien_url",
            sa.String(length=1000),
            nullable=True,
            comment="Đường dẫn ảnh đại diện hoặc ảnh khuôn viên.",
        ),
        sa.Column(
            "dien_tich_m2",
            sa.Numeric(15, 2),
            nullable=True,
            comment="Diện tích tính bằng m²; cần thống nhất phạm vi đo.",
        ),
        sa.Column(
            "trang_thai_hoat_dong",
            sa.String(length=30),
            nullable=True,
            comment="Trạng thái hoạt động của trường.",
        ),
        sa.Column(
            "nguon_du_lieu_url",
            sa.String(length=1000),
            nullable=True,
            comment="Đường dẫn nguồn chính dùng để xác minh thông tin.",
        ),
        sa.Column(
            "ngay_xac_minh",
            sa.DateTime(),
            nullable=True,
            comment="Thời điểm gần nhất thông tin được kiểm tra với nguồn.",
        ),
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Thông tin bổ sung hoặc nội dung cần xác minh.",
        ),
        sa.Column(
            "tao_luc",
            sa.DateTime(),
            nullable=True,
            comment="Thời điểm tạo bản ghi.",
        ),
        sa.Column(
            "cap_nhat_luc",
            sa.DateTime(),
            nullable=True,
            comment="Thời điểm cập nhật bản ghi gần nhất.",
        ),
        sa.UniqueConstraint("ma_truong", name="uk_dm_truong_ma_truong"),
        sa.CheckConstraint("vi_do IS NULL OR (vi_do BETWEEN -90 AND 90)", name="chk_dm_truong_vi_do"),
        sa.CheckConstraint("kinh_do IS NULL OR (kinh_do BETWEEN -180 AND 180)", name="chk_dm_truong_kinh_do"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Thông tin các trường học",
    )
    op.create_table(
        "dm_bang_cap_chung_chi",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment="Khóa chính, tự tăng.",
        ),
        sa.Column(
            "ma_chung_chi",
            sa.String(length=30),
            nullable=True,
            comment="Mã định danh chứng chỉ trong hệ thống.",
        ),
        sa.Column(
            "ten_chung_chi",
            sa.String(length=150),
            nullable=False,
            comment="Tên chứng chỉ.",
        ),
        sa.Column(
            "ma_ngon_ngu",
            sa.String(length=10),
            nullable=True,
            comment="Mã ngôn ngữ được đánh giá.",
        ),
        sa.Column(
            "ten_ngon_ngu",
            sa.String(length=100),
            nullable=True,
            comment="Tên ngôn ngữ được đánh giá.",
        ),
        sa.Column(
            "don_vi_cap",
            sa.String(length=255),
            nullable=True,
            comment="Tổ chức cấp hoặc đồng sở hữu chứng chỉ.",
        ),
        sa.Column(
            "loai_chung_chi",
            sa.String(length=50),
            nullable=True,
            comment="Nhóm hoặc loại chứng chỉ.",
        ),
        sa.Column(
            "thang_diem_min",
            sa.Numeric(6, 2),
            nullable=True,
            comment="Điểm thấp nhất của thang điểm chứng chỉ.",
        ),
        sa.Column(
            "thang_diem_max",
            sa.Numeric(6, 2),
            nullable=True,
            comment="Điểm cao nhất của thang điểm chứng chỉ.",
        ),
        sa.Column(
            "don_vi_diem",
            sa.String(length=30),
            nullable=True,
            comment="Đơn vị ghi điểm của chứng chỉ.",
        ),
        sa.Column(
            "ky_nang_duoc_danh_gia",
            sa.JSON(),
            nullable=True,
            comment="Danh sách kỹ năng được đánh giá.",
        ),
        sa.Column(
            "hinh_thuc_thi",
            sa.JSON(),
            nullable=True,
            comment="Danh sách hình thức thi có thể có.",
        ),
        sa.Column(
            "ghi_chu_hinh_thuc_thi",
            sa.Text(),
            nullable=True,
            comment="Mô tả hoặc lưu ý về các hình thức thi.",
        ),
        sa.Column(
            "thoi_han_hieu_luc_thang",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Thời hạn hiệu lực tính bằng tháng, nếu có quy định thống nhất.",
        ),
        sa.Column(
            "trang_thai",
            sa.String(length=20),
            nullable=True,
            comment="Trạng thái sử dụng trong danh mục.",
        ),
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Ghi chú chung về chứng chỉ hoặc cách xác minh.",
        ),
        sa.Column(
            "tao_luc",
            sa.DateTime(),
            nullable=True,
            comment="Thời điểm tạo bản ghi.",
        ),
        sa.Column(
            "cap_nhat_luc",
            sa.DateTime(),
            nullable=True,
            comment="Thời điểm cập nhật bản ghi gần nhất.",
        ),
        sa.UniqueConstraint("ma_chung_chi", name="uk_dm_bang_cap_chung_chi_ma_chung_chi"),
        sa.CheckConstraint("thang_diem_min IS NULL OR thang_diem_max IS NULL OR thang_diem_max >= thang_diem_min", name="chk_dm_bang_cap_chung_chi_thang_diem_min"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Danh mục bằng cấp và chứng chỉ",
    )
    op.create_table(
        "dm_bai_thi_danh_gia",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment="Khóa chính, tự tăng.",
        ),
        sa.Column(
            "ma_bai_thi",
            sa.String(length=30),
            nullable=True,
            comment="Mã định danh bài thi trong hệ thống.",
        ),
        sa.Column(
            "ten_bai_thi",
            sa.String(length=255),
            nullable=False,
            comment="Tên chính thức của bài thi hoặc kỳ thi.",
        ),
        sa.Column(
            "ten_viet_tat",
            sa.String(length=50),
            nullable=True,
            comment="Tên viết tắt thường dùng.",
        ),
        sa.Column(
            "don_vi_to_chuc",
            sa.String(length=255),
            nullable=True,
            comment="Đơn vị tổ chức hoặc quản lý bài thi.",
        ),
        sa.Column(
            "loai_danh_gia",
            sa.String(length=50),
            nullable=True,
            comment="Loại bài thi hoặc năng lực được đánh giá.",
        ),
        sa.Column(
            "mo_ta",
            sa.Text(),
            nullable=True,
            comment="Mô tả mục tiêu và phạm vi đánh giá của bài thi.",
        ),
        sa.Column(
            "doi_tuong_du_thi",
            sa.Text(),
            nullable=True,
            comment="Nhóm đối tượng có thể dự thi.",
        ),
        sa.Column(
            "hinh_thuc_thi",
            sa.JSON(),
            nullable=True,
            comment="Các hình thức tổ chức có thể áp dụng.",
        ),
        sa.Column(
            "thang_diem",
            sa.Numeric(8, 2),
            nullable=True,
            comment="Điểm tối đa của bài thi.",
        ),
        sa.Column(
            "diem_toi_thieu",
            sa.Numeric(8, 2),
            nullable=True,
            comment="Điểm thấp nhất có thể ghi nhận, nếu xác định được.",
        ),
        sa.Column(
            "don_vi_diem",
            sa.String(length=30),
            nullable=True,
            comment="Đơn vị hoặc cách biểu diễn điểm.",
        ),
        sa.Column(
            "cau_truc_bai_thi",
            sa.JSON(),
            nullable=True,
            comment="Các phần thi, số câu, thời lượng hoặc trọng số.",
        ),
        sa.Column(
            "thoi_luong_phut",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Tổng thời lượng làm bài tính bằng phút.",
        ),
        sa.Column(
            "cach_cong_bo_ket_qua",
            sa.Text(),
            nullable=True,
            comment="Mô tả cách đơn vị tổ chức công bố kết quả, nếu có.",
        ),
        sa.Column(
            "nam_ap_dung_tu",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Năm bắt đầu có thông tin trong danh mục.",
        ),
        sa.Column(
            "nam_ap_dung_den",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Năm kết thúc áp dụng; để NULL nếu chưa xác định.",
        ),
        sa.Column(
            "website_chinh_thuc",
            sa.String(length=1000),
            nullable=True,
            comment="Trang thông tin chính thức của bài thi hoặc đơn vị tổ chức.",
        ),
        sa.Column(
            "nguon_du_lieu_url",
            sa.String(length=1000),
            nullable=True,
            comment="Đường dẫn nguồn dùng để xác minh thông tin.",
        ),
        sa.Column(
            "trang_thai",
            sa.String(length=20),
            nullable=True,
            comment="Trạng thái của bài thi trong danh mục.",
        ),
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Ghi chú bổ sung.",
        ),
        sa.Column(
            "tao_luc",
            sa.DateTime(),
            nullable=True,
            comment="Thời điểm tạo bản ghi.",
        ),
        sa.Column(
            "cap_nhat_luc",
            sa.DateTime(),
            nullable=True,
            comment="Thời điểm cập nhật bản ghi gần nhất.",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Danh mục các bài thi đánh giá",
    )
    op.create_table(
        "dm_thanh_tich_hoc_tap",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment="Khóa chính, tự tăng.",
        ),
        sa.Column(
            "ma_loai_thanh_tich",
            sa.String(length=30),
            nullable=True,
            comment="Mã loại thành tích.",
        ),
        sa.Column(
            "ten_loai_thanh_tich",
            sa.String(length=255),
            nullable=False,
            comment="Tên loại thành tích.",
        ),
        sa.Column(
            "loai_cuoc_thi",
            sa.String(length=50),
            nullable=True,
            comment="Nhóm cuộc thi hoặc hoạt động.",
        ),
        sa.Column(
            "cap_cuoc_thi",
            sa.String(length=50),
            nullable=True,
            comment="Cấp tổ chức hoặc phạm vi cuộc thi.",
        ),
        sa.Column(
            "cac_muc_giai",
            sa.JSON(),
            nullable=True,
            comment="Danh sách giải thưởng có thể đạt trong loại thành tích này. Mỗi giải gồm mã, tên và thứ tự.",
        ),
        sa.Column(
            "mo_ta",
            sa.Text(),
            nullable=True,
            comment="Mô tả loại thành tích.",
        ),
        sa.Column(
            "trang_thai",
            sa.String(length=20),
            nullable=True,
            comment="Trạng thái sử dụng trong danh mục.",
        ),
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Ghi chú bổ sung.",
        ),
        sa.UniqueConstraint("ma_loai_thanh_tich", name="uk_dm_thanh_tich_hoc_tap_ma_loai_thanh_tich"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Danh mục thành tích học tập",
    )
    op.create_table(
        "dm_to_hop_mon_hoc_chi_tiet",
        sa.Column(
            "to_hop_id",
            sa.Integer(),
            primary_key=True,
            nullable=False,
            comment="Khóa ngoại đến tổ hợp môn học.",
        ),
        sa.Column(
            "mon_hoc_id",
            sa.Integer(),
            primary_key=True,
            nullable=False,
            comment="Khóa ngoại đến môn học trong tổ hợp.",
        ),
        sa.Column(
            "thu_tu_mon",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Thứ tự của môn trong tổ hợp, nếu có.",
        ),
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Lưu ý riêng về môn học trong tổ hợp.",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Bảng nối nhiều-nhiều giữa tổ hợp và môn học (bổ sung thiết kế)",
    )
    op.create_table(
        "dats_tuyen_sinh",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment="Khóa chính, tự tăng.",
        ),
        sa.Column(
            "truong_id",
            mysql.BIGINT(unsigned=True),
            nullable=False,
            comment="Đơn vị đào tạo; khóa ngoại đến dm_truong.id.",
        ),
        sa.Column(
            "nam_tuyen_sinh",
            mysql.SMALLINT(unsigned=True),
            nullable=False,
            comment="Năm tuyển sinh của đề án.",
        ),
        sa.Column(
            "chi_tieu",
            mysql.INTEGER(unsigned=True),
            nullable=True,
            comment="Tổng chỉ tiêu của đợt tuyển sinh",
        ),
        sa.Column(
            "ten_de_an",
            sa.String(length=255),
            nullable=True,
            comment="Tên đề án/thông tin tuyển sinh.",
        ),
        sa.Column(
            "hinh_thuc_dao_tao",
            sa.JSON(),
            nullable=True,
            comment="Danh sách hình thức đào tạo tuyển sinh.",
        ),
        sa.Column(
            "gioi_thieu",
            sa.Text(),
            nullable=True,
            comment="Nội dung tổng quan đề án.",
        ),
        sa.Column(
            "ngay_cong_bo",
            sa.Date(),
            nullable=True,
            comment="Ngày công bố đề án.",
        ),
        sa.Column(
            "nguon_du_lieu_url",
            sa.String(length=1000),
            nullable=True,
            comment="Đường dẫn đề án gốc.",
        ),
        sa.Column(
            "trang_thai",
            sa.String(length=20),
            nullable=True,
            comment="Trạng thái đề án.",
        ),
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Ghi chú/cập nhật.",
        ),
        sa.Column(
            "tao_luc",
            sa.DateTime(),
            nullable=True,
            comment="Thời điểm tạo bản ghi.",
        ),
        sa.Column(
            "cap_nhat_luc",
            sa.DateTime(),
            nullable=True,
            comment="Thời điểm cập nhật gần nhất.",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Thông tin chung của đề án theo trường và năm tuyển sinh",
    )
    op.create_table(
        "dats_tru_so",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment="Khóa chính.",
        ),
        sa.Column(
            "de_an_id",
            mysql.BIGINT(unsigned=True),
            nullable=False,
            comment="Đề án liên quan.",
        ),
        sa.Column(
            "vai_tro",
            sa.String(length=30),
            nullable=True,
            comment="Vai trò địa điểm: chính/phụ.",
        ),
        sa.Column(
            "ten_co_so",
            sa.String(length=255),
            nullable=True,
            comment="Tên trụ sở/cơ sở/phân hiệu.",
        ),
        sa.Column(
            "loai_co_so",
            sa.String(length=30),
            nullable=True,
            comment="Loại địa điểm.",
        ),
        sa.Column(
            "dia_chi",
            sa.String(length=500),
            nullable=True,
            comment="Địa chỉ đầy đủ.",
        ),
        sa.Column(
            "so_dien_thoai",
            sa.String(length=30),
            nullable=True,
            comment="Số liên hệ tại địa điểm.",
        ),
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Thông tin bổ sung.",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Trụ sở, cơ sở và phân hiệu của trường",
    )
    op.create_table(
        "dats_website",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment="Khóa chính.",
        ),
        sa.Column(
            "de_an_id",
            mysql.BIGINT(unsigned=True),
            nullable=False,
            comment="Đề án liên quan.",
        ),
        sa.Column(
            "loai_website",
            sa.String(length=30),
            nullable=True,
            comment="Phân loại website.",
        ),
        sa.Column(
            "ten_trang",
            sa.String(length=255),
            nullable=True,
            comment="Tên trang thông tin.",
        ),
        sa.Column(
            "url",
            sa.String(length=1000),
            nullable=True,
            comment="Địa chỉ trang.",
        ),
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Mô tả/lưu ý.",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Các trang thông tin điện tử liên quan đến đề án",
    )
    op.create_table(
        "dats_lien_he_tuyen_sinh",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment="Khóa chính.",
        ),
        sa.Column(
            "de_an_id",
            mysql.BIGINT(unsigned=True),
            nullable=False,
            comment="Đề án liên quan.",
        ),
        sa.Column(
            "ten_don_vi",
            sa.String(length=255),
            nullable=True,
            comment="Đơn vị phụ trách.",
        ),
        sa.Column(
            "ten_nguoi_lien_he",
            sa.String(length=255),
            nullable=True,
            comment="Người liên hệ nếu công bố.",
        ),
        sa.Column(
            "chuc_vu",
            sa.String(length=150),
            nullable=True,
            comment="Chức vụ người liên hệ.",
        ),
        sa.Column(
            "so_dien_thoai",
            sa.String(length=30),
            nullable=True,
            comment="Số điện thoại.",
        ),
        sa.Column(
            "email",
            sa.String(length=255),
            nullable=True,
            comment="Email liên hệ.",
        ),
        sa.Column(
            "thoi_gian_lien_he",
            sa.String(length=255),
            nullable=True,
            comment="Khung giờ hỗ trợ.",
        ),
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Thông tin liên hệ bổ sung.",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Đầu mối, số điện thoại và email tư vấn tuyển sinh",
    )
    op.create_table(
        "dats_chuong_trinh_dao_tao",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment="Khóa chính.",
        ),
        sa.Column(
            "de_an_id",
            mysql.BIGINT(unsigned=True),
            nullable=False,
            comment="Đề án áp dụng.",
        ),
        sa.Column(
            "nganh_dao_tao_id",
            sa.Integer(),
            nullable=True,
            comment="Ngành chuẩn; FK dm_nganh_dao_tao.id.",
        ),
        sa.Column(
            "ma_xet_tuyen",
            sa.String(length=20),
            nullable=True,
            comment="Mã xét tuyển do trường công bố.",
        ),
        sa.Column(
            "ten_chuong_trinh",
            sa.String(length=255),
            nullable=False,
            comment="Tên chương trình/ngành trong đề án.",
        ),
        sa.Column(
            "trinh_do_dao_tao",
            sa.String(length=30),
            nullable=True,
            comment="Trình độ đào tạo.",
        ),
        sa.Column(
            "hinh_thuc_dao_tao",
            sa.String(length=30),
            nullable=True,
            comment="Hình thức đào tạo.",
        ),
        sa.Column(
            "co_so_id",
            mysql.BIGINT(unsigned=True),
            nullable=True,
            comment="Cơ sở/phân hiệu phụ trách; có thể NULL.",
        ),
        sa.Column(
            "thoi_gian_dao_tao_nam",
            sa.Numeric(4, 1),
            nullable=True,
            comment="Thời lượng đào tạo theo năm.",
        ),
        sa.Column(
            "ngon_ngu_dao_tao",
            sa.String(length=100),
            nullable=True,
            comment="Ngôn ngữ giảng dạy.",
        ),
        sa.Column(
            "chi_tieu_tuyen_sinh",
            mysql.INTEGER(unsigned=True),
            nullable=True,
            comment="Tổng chỉ tiêu chương trình.",
        ),
        sa.Column(
            "kieu_phan_bo_chi_tieu",
            sa.String(length=30),
            nullable=True,
            comment="Phân bổ theo phương thức hay dùng chung.",
        ),
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Thông tin bổ sung.",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Danh sách chương trình và chỉ tiêu tổng theo chương trình",
    )
    op.create_table(
        "dats_ke_hoach_tuyen_sinh",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment="Khóa chính.",
        ),
        sa.Column(
            "de_an_chuong_trinh_id",
            mysql.BIGINT(unsigned=True),
            nullable=False,
            comment="Chương trình tuyển sinh.",
        ),
        sa.Column(
            "don_vi_chi_tieu",
            sa.String(length=30),
            nullable=True,
            comment="Đơn vị tính chỉ tiêu.",
        ),
        sa.Column(
            "pham_vi_tuyen_sinh",
            sa.String(length=255),
            nullable=True,
            comment="Phạm vi tuyển sinh.",
        ),
        sa.Column(
            "dot_tuyen_sinh",
            sa.String(length=100),
            nullable=True,
            comment="Đợt tuyển sinh.",
        ),
        sa.Column(
            "thoi_gian_nhan_ho_so",
            sa.String(length=255),
            nullable=True,
            comment="Thời gian nhận hồ sơ.",
        ),
        sa.Column(
            "dieu_kien_chung",
            sa.Text(),
            nullable=True,
            comment="Điều kiện chung trong kế hoạch.",
        ),
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Ghi chú kế hoạch.",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Kế hoạch và phạm vi tuyển sinh của chương trình",
    )
    op.create_table(
        "dats_phuong_thuc",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment="Khóa chính.",
        ),
        sa.Column(
            "de_an_chuong_trinh_id",
            mysql.BIGINT(unsigned=True),
            nullable=False,
            comment="Chương trình áp dụng.",
        ),
        sa.Column(
            "phuong_thuc_id",
            sa.Integer(),
            nullable=False,
            comment="Danh mục phương thức; FK dm_phuong_thuc_tuyen_sinh.id.",
        ),
        sa.Column(
            "ma_phuong_thuc_cua_truong",
            sa.String(length=20),
            nullable=True,
            comment="Mã riêng của trường.",
        ),
        sa.Column(
            "ten_phuong_thuc_cua_truong",
            sa.String(length=255),
            nullable=True,
            comment="Tên phương thức theo đề án.",
        ),
        sa.Column(
            "chi_tieu_phuong_thuc",
            mysql.INTEGER(unsigned=True),
            nullable=True,
            comment="Chỉ tiêu riêng; NULL nếu không chia chỉ tiêu.",
        ),
        sa.Column(
            "dieu_kien_can",
            sa.JSON(),
            nullable=True,
            comment="Điều kiện bắt buộc.",
        ),
        sa.Column(
            "dieu_kien_du",
            sa.JSON(),
            nullable=True,
            comment="Tiêu chí để đủ điều kiện trúng tuyển.",
        ),
        sa.Column(
            "diem_san",
            sa.Numeric(7, 2),
            nullable=True,
            comment="Ngưỡng nhận hồ sơ nếu công bố.",
        ),
        sa.Column(
            "diem_chuan",
            sa.Numeric(7, 2),
            nullable=True,
            comment="Ngưỡng trúng tuyển hồ sơ.",
        ),
        sa.Column(
            "thang_diem",
            sa.Numeric(7, 2),
            nullable=True,
            comment="Thang điểm xét tuyển.",
        ),
        sa.Column(
            "cong_thuc_tinh_diem",
            sa.Text(),
            nullable=True,
            comment="Công thức điểm xét tuyển.",
        ),
        sa.Column(
            "to_hop_id",
            sa.Integer(),
            nullable=True,
            comment="Tổ hợp áp dụng; NULL nếu không dùng tổ hợp.; một tổ hợp theo Excel; nhiều tổ hợp dùng dats_phuong_thuc_to_hop.",
        ),
        sa.Column(
            "thu_tu_uu_tien",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Thứ tự hiển thị.",
        ),
        sa.Column(
            "ghi_chu_chi_tieu",
            sa.Text(),
            nullable=True,
            comment="Cách phân bổ chỉ tiêu.",
        ),
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Lưu ý phương thức.",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Phương thức, điều kiện và chỉ tiêu theo phương thức",
    )
    op.create_table(
        "dats_phuong_thuc_to_hop",
        sa.Column(
            "de_an_phuong_thuc_id",
            mysql.BIGINT(unsigned=True),
            primary_key=True,
            nullable=False,
            comment="Khóa ngoại đến phương thức xét tuyển cụ thể trong đề án.",
        ),
        sa.Column(
            "to_hop_id",
            sa.Integer(),
            primary_key=True,
            nullable=False,
            comment="Khóa ngoại đến tổ hợp môn xét tuyển.",
        ),
        sa.Column(
            "thu_tu_hien_thi",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Thứ tự hiển thị tổ hợp của phương thức.",
        ),
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Lưu ý phạm vi hoặc điều kiện riêng của tổ hợp.",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Liên kết N-N giữa phương thức của đề án và tổ hợp môn (bổ sung thiết kế)",
    )
    op.create_table(
        "dats_nhan_su",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment="Khóa chính.",
        ),
        sa.Column(
            "de_an_id",
            mysql.BIGINT(unsigned=True),
            nullable=False,
            comment="Đề án liên quan.",
        ),
        sa.Column(
            "nhom_nhan_su",
            sa.String(length=30),
            nullable=True,
            comment="Nhóm giảng viên/cán bộ quản lý.",
        ),
        sa.Column(
            "ten_nhan_su",
            sa.String(length=255),
            nullable=True,
            comment="Tên cá nhân nếu công bố; có thể NULL.",
        ),
        sa.Column(
            "chuc_danh",
            sa.String(length=100),
            nullable=True,
            comment="Chức danh/vị trí.",
        ),
        sa.Column(
            "hoc_vi",
            sa.String(length=50),
            nullable=True,
            comment="Học vị.",
        ),
        sa.Column(
            "hoc_ham",
            sa.String(length=50),
            nullable=True,
            comment="Học hàm.",
        ),
        sa.Column(
            "linh_vuc_chuyen_mon",
            sa.String(length=255),
            nullable=True,
            comment="Lĩnh vực chuyên môn.",
        ),
        sa.Column(
            "so_luong",
            mysql.INTEGER(unsigned=True),
            nullable=True,
            comment="Số lượng nếu thống kê tổng hợp.",
        ),
        sa.Column(
            "nam_thong_ke",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Năm thống kê.",
        ),
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Ghi chú số liệu.",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Đội ngũ giảng viên và cán bộ quản lý được đề án công bố",
    )
    op.create_table(
        "dats_co_so_vat_chat",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment="Khóa chính.",
        ),
        sa.Column(
            "de_an_id",
            mysql.BIGINT(unsigned=True),
            nullable=False,
            comment="Đề án liên quan.",
        ),
        sa.Column(
            "co_so_id",
            mysql.BIGINT(unsigned=True),
            nullable=True,
            comment="Cơ sở sở hữu hạng mục; có thể NULL.",
        ),
        sa.Column(
            "loai_co_so_vat_chat",
            sa.String(length=50),
            nullable=True,
            comment="Loại hạng mục.",
        ),
        sa.Column(
            "ten_hang_muc",
            sa.String(length=255),
            nullable=True,
            comment="Tên cơ sở vật chất/thiết bị.",
        ),
        sa.Column(
            "so_luong",
            sa.Numeric(12, 2),
            nullable=True,
            comment="Số lượng hoặc diện tích.",
        ),
        sa.Column(
            "don_vi_tinh",
            sa.String(length=30),
            nullable=True,
            comment="Đơn vị đo.",
        ),
        sa.Column(
            "muc_dich_su_dung",
            sa.Text(),
            nullable=True,
            comment="Công năng đào tạo.",
        ),
        sa.Column(
            "nam_thong_ke",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Năm ghi nhận.",
        ),
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Ghi chú bổ sung.",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Cơ sở vật chất phục vụ đào tạo",
    )
    op.create_table(
        "dats_quy_mo_dao_tao",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment="Khóa chính.",
        ),
        sa.Column(
            "de_an_id",
            mysql.BIGINT(unsigned=True),
            nullable=False,
            comment="Đề án liên quan.",
        ),
        sa.Column(
            "de_an_chuong_trinh_id",
            mysql.BIGINT(unsigned=True),
            nullable=True,
            comment="Chương trình cụ thể; NULL nếu toàn trường.",
        ),
        sa.Column(
            "trinh_do_dao_tao",
            sa.String(length=30),
            nullable=True,
            comment="Trình độ đào tạo.",
        ),
        sa.Column(
            "hinh_thuc_dao_tao",
            sa.String(length=30),
            nullable=True,
            comment="Hình thức đào tạo.",
        ),
        sa.Column(
            "nam_thong_ke",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Năm thống kê.",
        ),
        sa.Column(
            "so_luong_nguoi_hoc",
            mysql.INTEGER(unsigned=True),
            nullable=True,
            comment="Quy mô người học.",
        ),
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Phạm vi/cách thống kê.",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Quy mô người học theo năm, trình độ và hình thức đào tạo",
    )
    op.create_table(
        "dats_ty_le_viec_lam",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment="Khóa chính.",
        ),
        sa.Column(
            "de_an_id",
            mysql.BIGINT(unsigned=True),
            nullable=False,
            comment="Đề án công bố số liệu.",
        ),
        sa.Column(
            "nganh_dao_tao_id",
            sa.Integer(),
            nullable=True,
            comment="Ngành thống kê; NULL nếu tổng hợp.",
        ),
        sa.Column(
            "trinh_do_dao_tao",
            sa.String(length=30),
            nullable=True,
            comment="Trình độ khóa tốt nghiệp.",
        ),
        sa.Column(
            "nam_tot_nghiep",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Năm tốt nghiệp.",
        ),
        sa.Column(
            "thoi_diem_khao_sat_thang",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Số tháng sau tốt nghiệp khi khảo sát.",
        ),
        sa.Column(
            "so_nguoi_tot_nghiep",
            mysql.INTEGER(unsigned=True),
            nullable=True,
            comment="Tổng số người tốt nghiệp trong mẫu/khóa.",
        ),
        sa.Column(
            "so_nguoi_co_viec_lam",
            mysql.INTEGER(unsigned=True),
            nullable=True,
            comment="Số người có việc làm theo khảo sát.",
        ),
        sa.Column(
            "ty_le_co_viec_lam",
            sa.Numeric(5, 2),
            nullable=True,
            comment="Tỷ lệ có việc làm theo %.",
        ),
        sa.Column(
            "phuong_phap_khao_sat",
            sa.Text(),
            nullable=True,
            comment="Cách thu thập kết quả.",
        ),
        sa.Column(
            "nguon_du_lieu_url",
            sa.String(length=1000),
            nullable=True,
            comment="URL nguồn công bố.",
        ),
        sa.CheckConstraint("ty_le_co_viec_lam IS NULL OR (ty_le_co_viec_lam BETWEEN 0 AND 100)", name="chk_dats_ty_le_viec_lam_ty_le_co_viec_lam"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Tỷ lệ việc làm của người học sau tốt nghiệp",
    )
    op.create_table(
        "dats_trinh_do_nganh",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment="Khóa chính.",
        ),
        sa.Column(
            "de_an_chuong_trinh_id",
            mysql.BIGINT(unsigned=True),
            nullable=False,
            comment="Chương trình thuộc đề án.",
        ),
        sa.Column(
            "trinh_do_dao_tao",
            sa.String(length=30),
            nullable=True,
            comment="Trình độ.",
        ),
        sa.Column(
            "hinh_thuc_dao_tao",
            sa.String(length=30),
            nullable=True,
            comment="Hình thức.",
        ),
        sa.Column(
            "thoi_gian_dao_tao_nam",
            sa.Numeric(4, 1),
            nullable=True,
            comment="Thời lượng chương trình.",
        ),
        sa.Column(
            "ma_nganh_chuan",
            sa.String(length=20),
            nullable=True,
            comment="Mã ngành chuẩn tại thời điểm đề án.",
        ),
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Thông tin bổ sung.",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Trình độ và hình thức đào tạo gắn với chương trình",
    )
    op.create_table(
        "dats_doi_tuong_du_tuyen",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment="Khóa chính.",
        ),
        sa.Column(
            "de_an_id",
            mysql.BIGINT(unsigned=True),
            nullable=False,
            comment="Đề án liên quan.",
        ),
        sa.Column(
            "ma_doi_tuong",
            sa.String(length=30),
            nullable=True,
            comment="Mã nhóm đối tượng.",
        ),
        sa.Column(
            "ten_doi_tuong",
            sa.String(length=255),
            nullable=False,
            comment="Tên đối tượng dự tuyển.",
        ),
        sa.Column(
            "mo_ta",
            sa.Text(),
            nullable=True,
            comment="Phạm vi đối tượng.",
        ),
        sa.Column(
            "nam_tot_nghiep_tu",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Năm tốt nghiệp tối thiểu nếu giới hạn.",
        ),
        sa.Column(
            "nam_tot_nghiep_den",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Năm tốt nghiệp tối đa; NULL nếu không giới hạn.",
        ),
        sa.Column(
            "pham_vi_ap_dung",
            sa.String(length=30),
            nullable=True,
            comment="Toàn đề án hoặc một chương trình.",
        ),
        sa.Column(
            "de_an_chuong_trinh_id",
            mysql.BIGINT(unsigned=True),
            nullable=True,
            comment="Chương trình áp dụng; có thể NULL.",
        ),
        sa.Column(
            "trang_thai",
            sa.String(length=20),
            nullable=True,
            comment="Trạng thái bản ghi.",
        ),
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Ghi chú/ngoại lệ.",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Nhóm thí sinh được phép dự tuyển",
    )
    op.create_table(
        "dats_dieu_kien_du_tuyen",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment="Khóa chính.",
        ),
        sa.Column(
            "de_an_id",
            mysql.BIGINT(unsigned=True),
            nullable=False,
            comment="Đề án áp dụng.",
        ),
        sa.Column(
            "doi_tuong_du_tuyen_id",
            mysql.BIGINT(unsigned=True),
            nullable=True,
            comment="Đối tượng chịu điều kiện; có thể NULL.",
        ),
        sa.Column(
            "de_an_chuong_trinh_id",
            mysql.BIGINT(unsigned=True),
            nullable=True,
            comment="Chương trình áp dụng; có thể NULL.",
        ),
        sa.Column(
            "de_an_phuong_thuc_id",
            mysql.BIGINT(unsigned=True),
            nullable=True,
            comment="Phương thức áp dụng; có thể NULL.",
        ),
        sa.Column(
            "ma_dieu_kien",
            sa.String(length=50),
            nullable=True,
            comment="Mã tiêu chí.",
        ),
        sa.Column(
            "ten_dieu_kien",
            sa.String(length=255),
            nullable=True,
            comment="Tên điều kiện.",
        ),
        sa.Column(
            "loai_dieu_kien",
            sa.String(length=30),
            nullable=True,
            comment="Nhóm điều kiện.",
        ),
        sa.Column(
            "noi_dung_dieu_kien",
            sa.Text(),
            nullable=True,
            comment="Nội dung đầy đủ.",
        ),
        sa.Column(
            "toan_tu_so_sanh",
            sa.String(length=10),
            nullable=True,
            comment="Toán tử điều kiện số.",
        ),
        sa.Column(
            "gia_tri_dieu_kien",
            sa.JSON(),
            nullable=True,
            comment="Giá trị có cấu trúc.",
        ),
        sa.Column(
            "bat_buoc",
            sa.Boolean(),
            nullable=True,
            comment="Điều kiện bắt buộc hay không.",
        ),
        sa.Column(
            "minh_chung_can_nop",
            sa.Text(),
            nullable=True,
            comment="Giấy tờ chứng minh.",
        ),
        sa.Column(
            "thu_tu_kiem_tra",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Thứ tự kiểm tra.",
        ),
        sa.Column(
            "nguon_du_lieu_url",
            sa.String(length=1000),
            nullable=True,
            comment="URL nguồn quy định.",
        ),
        sa.Column(
            "trang_thai",
            sa.String(length=20),
            nullable=True,
            comment="Trạng thái.",
        ),
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Ghi chú.",
        ),
        sa.CheckConstraint("bat_buoc IS NULL OR bat_buoc IN (0,1)", name="chk_dats_dieu_kien_du_tuyen_bat_buoc"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Điều kiện cần đáp ứng để dự tuyển",
    )
    op.create_table(
        "dats_tieu_chi_xet_tuyen",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment="Khóa chính.",
        ),
        sa.Column(
            "de_an_id",
            mysql.BIGINT(unsigned=True),
            nullable=False,
            comment="Đề án áp dụng.",
        ),
        sa.Column(
            "de_an_chuong_trinh_id",
            mysql.BIGINT(unsigned=True),
            nullable=True,
            comment="Chương trình; NULL nếu chung.",
        ),
        sa.Column(
            "de_an_phuong_thuc_id",
            mysql.BIGINT(unsigned=True),
            nullable=True,
            comment="Phương thức; NULL nếu chung.",
        ),
        sa.Column(
            "ma_tieu_chi",
            sa.String(length=50),
            nullable=True,
            comment="Mã tiêu chí.",
        ),
        sa.Column(
            "ten_tieu_chi",
            sa.String(length=255),
            nullable=True,
            comment="Tên tiêu chí.",
        ),
        sa.Column(
            "loai_tieu_chi",
            sa.String(length=30),
            nullable=True,
            comment="Chính/phụ/loại trừ.",
        ),
        sa.Column(
            "thu_tu_ap_dung",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Thứ tự xét tiêu chí.",
        ),
        sa.Column(
            "toan_tu_so_sanh",
            sa.String(length=10),
            nullable=True,
            comment="Toán tử nếu có ngưỡng số.",
        ),
        sa.Column(
            "gia_tri_tieu_chi",
            sa.JSON(),
            nullable=True,
            comment="Ngưỡng/giá trị tiêu chí.",
        ),
        sa.Column(
            "noi_dung_tieu_chi",
            sa.Text(),
            nullable=True,
            comment="Mô tả đầy đủ tiêu chí.",
        ),
        sa.Column(
            "nguon_du_lieu_url",
            sa.String(length=1000),
            nullable=True,
            comment="URL nguồn.",
        ),
        sa.Column(
            "trang_thai",
            sa.String(length=20),
            nullable=True,
            comment="Trạng thái.",
        ),
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Ghi chú.",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Tiêu chí chính, tiêu chí phụ và thứ tự xét",
    )
    op.create_table(
        "dats_diem_cong",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment="Khóa chính.",
        ),
        sa.Column(
            "de_an_id",
            mysql.BIGINT(unsigned=True),
            nullable=False,
            comment="Đề án áp dụng.",
        ),
        sa.Column(
            "de_an_chuong_trinh_id",
            mysql.BIGINT(unsigned=True),
            nullable=True,
            comment="Chương trình; NULL nếu chung.",
        ),
        sa.Column(
            "de_an_phuong_thuc_id",
            mysql.BIGINT(unsigned=True),
            nullable=True,
            comment="Phương thức; NULL nếu chung.",
        ),
        sa.Column(
            "loai_diem_cong",
            sa.String(length=30),
            nullable=True,
            comment="Điểm thưởng/xét thưởng/khuyến khích.",
        ),
        sa.Column(
            "ma_doi_tuong_cong",
            sa.String(length=50),
            nullable=True,
            comment="Mã thành tích/chứng chỉ được cộng.",
        ),
        sa.Column(
            "doi_tuong_duoc_cong",
            sa.Text(),
            nullable=True,
            comment="Mô tả đối tượng.",
        ),
        sa.Column(
            "dieu_kien_ap_dung",
            sa.Text(),
            nullable=True,
            comment="Điều kiện chi tiết.",
        ),
        sa.Column(
            "diem_cong",
            sa.Numeric(6, 3),
            nullable=True,
            comment="Mức điểm được cộng.",
        ),
        sa.Column(
            "thang_diem",
            sa.Numeric(6, 2),
            nullable=True,
            comment="Thang điểm áp dụng.",
        ),
        sa.Column(
            "muc_diem_cong_toi_da",
            sa.Numeric(6, 3),
            nullable=True,
            comment="Mức cộng tối đa.",
        ),
        sa.Column(
            "co_cong_don",
            sa.Boolean(),
            nullable=True,
            comment="Có cộng dồn quyền lợi không.",
        ),
        sa.Column(
            "quy_tac_ket_hop",
            sa.Text(),
            nullable=True,
            comment="Xử lý nhiều diện cùng lúc.",
        ),
        sa.Column(
            "nam_tuyen_sinh",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Năm áp dụng.",
        ),
        sa.Column(
            "nguon_du_lieu_url",
            sa.String(length=1000),
            nullable=True,
            comment="URL nguồn.",
        ),
        sa.Column(
            "trang_thai",
            sa.String(length=20),
            nullable=True,
            comment="Trạng thái quy tắc.",
        ),
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Ghi chú.",
        ),
        sa.CheckConstraint("co_cong_don IS NULL OR co_cong_don IN (0,1)", name="chk_dats_diem_cong_co_cong_don"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Điểm thưởng, điểm xét thưởng và điểm khuyến khích",
    )
    op.create_table(
        "dats_quy_tac_phan_bo",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment="Khóa chính.",
        ),
        sa.Column(
            "de_an_id",
            mysql.BIGINT(unsigned=True),
            nullable=False,
            comment="Đề án áp dụng.",
        ),
        sa.Column(
            "de_an_chuong_trinh_id",
            mysql.BIGINT(unsigned=True),
            nullable=True,
            comment="Chương trình; NULL nếu chung.",
        ),
        sa.Column(
            "de_an_phuong_thuc_id",
            mysql.BIGINT(unsigned=True),
            nullable=True,
            comment="Phương thức; NULL nếu chung.",
        ),
        sa.Column(
            "kieu_phan_bo",
            sa.String(length=30),
            nullable=True,
            comment="Cách phân bổ thí sinh.",
        ),
        sa.Column(
            "thu_tu_uu_tien",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Thứ tự ưu tiên.",
        ),
        sa.Column(
            "quy_tac_xu_ly_dong_diem",
            sa.Text(),
            nullable=True,
            comment="Xử lý bằng điểm tại ranh giới chỉ tiêu.",
        ),
        sa.Column(
            "quy_tac_chuyen_chi_tieu",
            sa.Text(),
            nullable=True,
            comment="Cách xử lý chỉ tiêu dư/điều chỉnh.",
        ),
        sa.Column(
            "noi_dung_quy_tac",
            sa.Text(),
            nullable=True,
            comment="Nội dung quy tắc phân bổ.",
        ),
        sa.Column(
            "nguon_du_lieu_url",
            sa.String(length=1000),
            nullable=True,
            comment="URL nguồn.",
        ),
        sa.Column(
            "trang_thai",
            sa.String(length=20),
            nullable=True,
            comment="Trạng thái.",
        ),
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Ghi chú.",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Quy tắc phân bổ thí sinh vào ngành/chương trình",
    )
    op.create_table(
        "dats_ho_so_du_tuyen",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment="Khóa chính.",
        ),
        sa.Column(
            "de_an_id",
            mysql.BIGINT(unsigned=True),
            nullable=False,
            comment="Đề án áp dụng.",
        ),
        sa.Column(
            "de_an_chuong_trinh_id",
            mysql.BIGINT(unsigned=True),
            nullable=True,
            comment="Chương trình; có thể NULL.",
        ),
        sa.Column(
            "de_an_phuong_thuc_id",
            mysql.BIGINT(unsigned=True),
            nullable=True,
            comment="Phương thức; có thể NULL.",
        ),
        sa.Column(
            "ten_giay_to",
            sa.String(length=255),
            nullable=True,
            comment="Tên giấy tờ/minh chứng.",
        ),
        sa.Column(
            "doi_tuong_phai_nop",
            sa.Text(),
            nullable=True,
            comment="Đối tượng cần nộp giấy tờ.",
        ),
        sa.Column(
            "bat_buoc",
            sa.Boolean(),
            nullable=True,
            comment="Có bắt buộc nộp không.",
        ),
        sa.Column(
            "hinh_thuc_nop",
            sa.String(length=30),
            nullable=True,
            comment="Cách nộp hồ sơ.",
        ),
        sa.Column(
            "thoi_han_nop",
            sa.String(length=255),
            nullable=True,
            comment="Hạn nộp hồ sơ.",
        ),
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Yêu cầu/lưu ý.",
        ),
        sa.CheckConstraint("bat_buoc IS NULL OR bat_buoc IN (0,1)", name="chk_dats_ho_so_du_tuyen_bat_buoc"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Giấy tờ và minh chứng thí sinh cần nộp",
    )
    op.create_table(
        "dats_quy_doi_nguong_dau_vao",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment="Khóa chính.",
        ),
        sa.Column(
            "de_an_id",
            mysql.BIGINT(unsigned=True),
            nullable=False,
            comment="Đề án áp dụng.",
        ),
        sa.Column(
            "de_an_chuong_trinh_id",
            mysql.BIGINT(unsigned=True),
            nullable=True,
            comment="Chương trình áp dụng.",
        ),
        sa.Column(
            "nam_tuyen_sinh",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Năm tuyển sinh.",
        ),
        sa.Column(
            "phuong_thuc_nguon_id",
            sa.Integer(),
            nullable=True,
            comment="Phương thức nguồn.",
        ),
        sa.Column(
            "to_hop_nguon_id",
            sa.Integer(),
            nullable=True,
            comment="Tổ hợp nguồn; NULL nếu không dùng.",
        ),
        sa.Column(
            "phuong_thuc_dich_id",
            sa.Integer(),
            nullable=True,
            comment="Phương thức đích.",
        ),
        sa.Column(
            "to_hop_dich_id",
            sa.Integer(),
            nullable=True,
            comment="Tổ hợp đích; NULL nếu không dùng.",
        ),
        sa.Column(
            "diem_moc_nguon",
            sa.Numeric(7, 3),
            nullable=True,
            comment="Mốc ngưỡng đầu vào nguồn.",
        ),
        sa.Column(
            "diem_moc_dich",
            sa.Numeric(7, 3),
            nullable=True,
            comment="Ngưỡng tương đương đích.",
        ),
        sa.Column(
            "do_lech_diem",
            sa.Numeric(7, 3),
            nullable=True,
            comment="Điểm đích trừ điểm nguồn.",
        ),
        sa.Column(
            "thang_diem_nguon",
            sa.Numeric(7, 2),
            nullable=True,
            comment="Thang điểm nguồn tối đa.",
        ),
        sa.Column(
            "thang_diem_dich",
            sa.Numeric(7, 2),
            nullable=True,
            comment="Thang điểm đích tối đa.",
        ),
        sa.Column(
            "cong_thuc_noi_suy",
            sa.Text(),
            nullable=True,
            comment="Công thức giữa các mốc.",
        ),
        sa.Column(
            "dieu_kien_ap_dung",
            sa.Text(),
            nullable=True,
            comment="Điều kiện/phạm vi áp dụng.",
        ),
        sa.Column(
            "nguon_du_lieu_url",
            sa.String(length=1000),
            nullable=True,
            comment="URL bảng quy đổi gốc.",
        ),
        sa.Column(
            "trang_thai",
            sa.String(length=20),
            nullable=True,
            comment="Trạng thái quy tắc.",
        ),
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Ghi chú.",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Quy đổi ngưỡng đầu vào giữa phương thức/tổ hợp",
    )
    op.create_table(
        "dats_quy_doi_diem_trung_tuyen",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment="Khóa chính.",
        ),
        sa.Column(
            "de_an_id",
            mysql.BIGINT(unsigned=True),
            nullable=False,
            comment="Đề án áp dụng.",
        ),
        sa.Column(
            "de_an_chuong_trinh_id",
            mysql.BIGINT(unsigned=True),
            nullable=True,
            comment="Chương trình áp dụng.",
        ),
        sa.Column(
            "nam_tuyen_sinh",
            mysql.SMALLINT(unsigned=True),
            nullable=True,
            comment="Năm tuyển sinh.",
        ),
        sa.Column(
            "phuong_thuc_nguon_id",
            sa.Integer(),
            nullable=True,
            comment="Phương thức nguồn.",
        ),
        sa.Column(
            "to_hop_nguon_id",
            sa.Integer(),
            nullable=True,
            comment="Tổ hợp nguồn; NULL nếu không dùng.",
        ),
        sa.Column(
            "phuong_thuc_dich_id",
            sa.Integer(),
            nullable=True,
            comment="Phương thức đích.",
        ),
        sa.Column(
            "to_hop_dich_id",
            sa.Integer(),
            nullable=True,
            comment="Tổ hợp đích; NULL nếu không dùng.",
        ),
        sa.Column(
            "diem_moc_nguon",
            sa.Numeric(7, 3),
            nullable=True,
            comment="Mốc điểm trúng tuyển nguồn.",
        ),
        sa.Column(
            "diem_moc_dich",
            sa.Numeric(7, 3),
            nullable=True,
            comment="Mốc điểm tương đương đích.",
        ),
        sa.Column(
            "do_lech_diem",
            sa.Numeric(7, 3),
            nullable=True,
            comment="Điểm đích trừ điểm nguồn.",
        ),
        sa.Column(
            "thang_diem_nguon",
            sa.Numeric(7, 2),
            nullable=True,
            comment="Thang điểm nguồn tối đa.",
        ),
        sa.Column(
            "thang_diem_dich",
            sa.Numeric(7, 2),
            nullable=True,
            comment="Thang điểm đích tối đa.",
        ),
        sa.Column(
            "cong_thuc_noi_suy",
            sa.Text(),
            nullable=True,
            comment="Công thức nội suy giữa các mốc.",
        ),
        sa.Column(
            "dieu_kien_ap_dung",
            sa.Text(),
            nullable=True,
            comment="Điều kiện/phạm vi áp dụng.",
        ),
        sa.Column(
            "nguon_du_lieu_url",
            sa.String(length=1000),
            nullable=True,
            comment="URL bảng quy đổi gốc.",
        ),
        sa.Column(
            "trang_thai",
            sa.String(length=20),
            nullable=True,
            comment="Trạng thái quy tắc.",
        ),
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Ghi chú.",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Quy đổi điểm trúng tuyển giữa phương thức/tổ hợp",
    )
    op.create_table(
        "dats_chinh_sach_xet_tuyen_thang",
        sa.Column(
            "id",
            mysql.BIGINT(),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment="Khóa chính của chính sách",
        ),
        sa.Column(
            "de_an_id",
            mysql.BIGINT(unsigned=True),
            nullable=False,
            comment="Đề án tuyển sinh áp dụng chính sách",
        ),
        sa.Column(
            "ma_chinh_sach",
            sa.String(length=50),
            nullable=True,
            comment="Mã chính sách do trường quy định",
        ),
        sa.Column(
            "ten_chinh_sach",
            sa.String(length=255),
            nullable=True,
            comment="Tên diện xét tuyển thẳng",
        ),
        sa.Column(
            "nhom_doi_tuong",
            sa.String(length=100),
            nullable=True,
            comment="Nhóm đối tượng theo quy định",
        ),
        sa.Column(
            "can_cu_phap_ly",
            sa.String(length=255),
            nullable=True,
            comment="Căn cứ điều, khoản, điểm",
        ),
        sa.Column(
            "mo_ta_doi_tuong",
            sa.Text(),
            nullable=True,
            comment="Điều kiện cụ thể để thuộc diện này",
        ),
        sa.Column(
            "mon_thi_linh_vuc",
            sa.String(length=255),
            nullable=True,
            comment="Môn thi, đề tài hoặc lĩnh vực thành tích",
        ),
        sa.Column(
            "cap_thi",
            sa.String(length=100),
            nullable=True,
            comment="Cấp độ cuộc thi/thành tích",
        ),
        sa.Column(
            "muc_giai",
            sa.String(length=100),
            nullable=True,
            comment="Giải thưởng yêu cầu",
        ),
        sa.Column(
            "thoi_han_thanh_tich_nam",
            sa.SmallInteger(),
            nullable=True,
            comment="Số năm thành tích được tính đến thời điểm xét",
        ),
        sa.Column(
            "pham_vi_chuong_trinh",
            sa.Text(),
            nullable=True,
            comment="Ngành/chương trình được áp dụng",
        ),
        sa.Column(
            "dieu_kien_phu",
            sa.Text(),
            nullable=True,
            comment="Ngưỡng đầu vào hoặc điều kiện bổ sung của trường",
        ),
        sa.Column(
            "chi_tieu_tuyen_thang",
            sa.Integer(),
            nullable=True,
            comment="Số lượng tuyển theo diện này; để trống nếu không công bố riêng",
        ),
        sa.Column(
            "ho_so_minh_chung",
            sa.Text(),
            nullable=True,
            comment="Giấy tờ thí sinh phải nộp",
        ),
        sa.Column(
            "thu_tu_tieu_chi_xet",
            sa.Text(),
            nullable=True,
            comment="Thứ tự tiêu chí khi cần xếp hạng thí sinh",
        ),
        sa.Column(
            "tieu_chi_phu_khi_dong_diem",
            sa.Text(),
            nullable=True,
            comment="Tiêu chí xử lý khi các thí sinh bằng điểm/đồng hạng",
        ),
        sa.Column(
            "nguyen_tac_khi_vuot_chi_tieu",
            sa.Text(),
            nullable=True,
            comment="Cách xử lý khi số thí sinh đủ điều kiện vượt chỉ tiêu",
        ),
        sa.Column(
            "thoi_gian_nhan_ho_so",
            sa.String(length=255),
            nullable=True,
            comment="Thời gian nhận hồ sơ",
        ),
        sa.Column(
            "trang_thai",
            sa.String(length=20),
            nullable=True,
            comment="Trạng thái chính sách",
        ),
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Thông tin bổ sung",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Chính sách xét tuyển thẳng của đề án",
    )
    op.create_table(
        "dats_chinh_sach_uu_tien_xet_tuyen",
        sa.Column(
            "id",
            mysql.BIGINT(),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment="Khóa chính của chính sách",
        ),
        sa.Column(
            "de_an_id",
            mysql.BIGINT(unsigned=True),
            nullable=False,
            comment="Đề án tuyển sinh áp dụng chính sách",
        ),
        sa.Column(
            "ma_chinh_sach",
            sa.String(length=50),
            nullable=True,
            comment="Mã chính sách do trường quy định",
        ),
        sa.Column(
            "ten_chinh_sach",
            sa.String(length=255),
            nullable=True,
            comment="Tên diện ưu tiên xét tuyển",
        ),
        sa.Column(
            "nhom_doi_tuong",
            sa.String(length=100),
            nullable=True,
            comment="Nhóm đối tượng được ưu tiên",
        ),
        sa.Column(
            "can_cu_phap_ly",
            sa.String(length=255),
            nullable=True,
            comment="Căn cứ điều, khoản, điểm",
        ),
        sa.Column(
            "mo_ta_doi_tuong",
            sa.Text(),
            nullable=True,
            comment="Điều kiện cụ thể để được ưu tiên",
        ),
        sa.Column(
            "mon_thi_linh_vuc",
            sa.String(length=255),
            nullable=True,
            comment="Môn thi, đề tài hoặc lĩnh vực thành tích",
        ),
        sa.Column(
            "muc_giai",
            sa.String(length=100),
            nullable=True,
            comment="Giải thưởng yêu cầu",
        ),
        sa.Column(
            "thoi_han_thanh_tich_nam",
            sa.SmallInteger(),
            nullable=True,
            comment="Số năm thành tích được tính",
        ),
        sa.Column(
            "pham_vi_chuong_trinh",
            sa.Text(),
            nullable=True,
            comment="Ngành/chương trình được áp dụng",
        ),
        sa.Column(
            "hinh_thuc_uu_tien",
            sa.String(length=50),
            nullable=True,
            comment="Cách trường áp dụng ưu tiên",
        ),
        sa.Column(
            "loai_diem_cong",
            sa.String(length=50),
            nullable=True,
            comment="Loại điểm cộng nếu áp dụng",
        ),
        sa.Column(
            "muc_diem_cong",
            sa.Numeric(5, 2),
            nullable=True,
            comment="Mức điểm cộng theo quy định của đề án",
        ),
        sa.Column(
            "dieu_kien_nguong_dau_vao",
            sa.Text(),
            nullable=True,
            comment="Ngưỡng cần đạt trước khi được ưu tiên, nếu có",
        ),
        sa.Column(
            "chi_tieu_uu_tien",
            sa.Integer(),
            nullable=True,
            comment="Số lượng dự kiến dành cho diện này, nếu có",
        ),
        sa.Column(
            "thu_tu_tieu_chi_xet",
            sa.Text(),
            nullable=True,
            comment="Thứ tự tiêu chí xếp hạng khi áp dụng ưu tiên",
        ),
        sa.Column(
            "tieu_chi_phu_khi_dong_diem",
            sa.Text(),
            nullable=True,
            comment="Tiêu chí xử lý khi các thí sinh bằng điểm",
        ),
        sa.Column(
            "ho_so_minh_chung",
            sa.Text(),
            nullable=True,
            comment="Giấy tờ thí sinh phải nộp",
        ),
        sa.Column(
            "thoi_gian_nhan_ho_so",
            sa.String(length=255),
            nullable=True,
            comment="Thời gian nhận hồ sơ",
        ),
        sa.Column(
            "trang_thai",
            sa.String(length=20),
            nullable=True,
            comment="Trạng thái chính sách",
        ),
        sa.Column(
            "ghi_chu",
            sa.Text(),
            nullable=True,
            comment="Thông tin bổ sung",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
        comment="Chính sách ưu tiên xét tuyển của đề án",
    )
    op.create_index("idx_dm_van_ban_so_ky_hieu", "dm_van_ban", ["so_ky_hieu"])
    op.create_index("idx_dm_truong_slug", "dm_truong", ["slug"])
    op.create_index("idx_dm_truong_loai_co_so_vung_mien", "dm_truong", ["loai_co_so", "vung_mien"])
    op.create_index("idx_dm_truong_truong_cha_id", "dm_truong", ["truong_cha_id"])
    op.create_index("idx_dm_nganh_dao_tao_ngay_hieu_luc_tu", "dm_nganh_dao_tao", ["ngay_hieu_luc_tu"])
    op.create_index("idx_dm_nganh_dao_tao_nganh_cha_id", "dm_nganh_dao_tao", ["nganh_cha_id"])
    op.create_index("idx_dm_nganh_dao_tao_van_ban_id", "dm_nganh_dao_tao", ["van_ban_id"])
    op.create_index("idx_dm_bai_thi_danh_gia_ma_bai_thi", "dm_bai_thi_danh_gia", ["ma_bai_thi"])
    op.create_index("idx_dm_doi_tuong_uu_tien_ma_doi_tuong_nam_ap_dung", "dm_doi_tuong_uu_tien", ["ma_doi_tuong", "nam_ap_dung"])
    op.create_index("idx_dm_doi_tuong_uu_tien_van_ban_id", "dm_doi_tuong_uu_tien", ["van_ban_id"])
    op.create_index("idx_dm_khu_vuc_uu_tien_ma_khu_vuc_nam_ap_dung", "dm_khu_vuc_uu_tien", ["ma_khu_vuc", "nam_ap_dung"])
    op.create_index("idx_dm_khu_vuc_uu_tien_van_ban_id", "dm_khu_vuc_uu_tien", ["van_ban_id"])
    op.create_index("idx_dm_phuong_thuc_tuyen_sinh_nam_ap_dung_tu", "dm_phuong_thuc_tuyen_sinh", ["nam_ap_dung_tu"])
    op.create_index("uk_dm_mon_hoc_ma_mon", "dm_mon_hoc", ["ma_mon"], unique=True)
    op.create_index("idx_dm_to_hop_mon_hoc_chi_tiet_to_hop_id", "dm_to_hop_mon_hoc_chi_tiet", ["to_hop_id"])
    op.create_index("idx_dm_to_hop_mon_hoc_chi_tiet_mon_hoc_id", "dm_to_hop_mon_hoc_chi_tiet", ["mon_hoc_id"])
    op.create_index("idx_dats_tuyen_sinh_truong_id_nam_tuyen_sinh", "dats_tuyen_sinh", ["truong_id", "nam_tuyen_sinh"])
    op.create_index("idx_dats_tru_so_de_an_id", "dats_tru_so", ["de_an_id"])
    op.create_index("idx_dats_website_de_an_id", "dats_website", ["de_an_id"])
    op.create_index("idx_dats_lien_he_tuyen_sinh_de_an_id", "dats_lien_he_tuyen_sinh", ["de_an_id"])
    op.create_index("idx_dats_chuong_trinh_dao_tao_de_an_id_ma_xet_tuyen", "dats_chuong_trinh_dao_tao", ["de_an_id", "ma_xet_tuyen"])
    op.create_index("idx_dats_chuong_trinh_dao_tao_nganh_dao_tao_id", "dats_chuong_trinh_dao_tao", ["nganh_dao_tao_id"])
    op.create_index("idx_dats_chuong_trinh_dao_tao_co_so_id", "dats_chuong_trinh_dao_tao", ["co_so_id"])
    op.create_index("idx_dats_ke_hoach_tuyen_sinh_de_an_chuong_trinh_id", "dats_ke_hoach_tuyen_sinh", ["de_an_chuong_trinh_id"])
    op.create_index("idx_dats_phuong_thuc_de_an_chuong_trinh_id_phuong_thuc_id", "dats_phuong_thuc", ["de_an_chuong_trinh_id", "phuong_thuc_id"])
    op.create_index("idx_dats_phuong_thuc_phuong_thuc_id", "dats_phuong_thuc", ["phuong_thuc_id"])
    op.create_index("idx_dats_phuong_thuc_to_hop_id", "dats_phuong_thuc", ["to_hop_id"])
    op.create_index("idx_dats_phuong_thuc_to_hop_de_an_phuong_thuc_id", "dats_phuong_thuc_to_hop", ["de_an_phuong_thuc_id"])
    op.create_index("idx_dats_phuong_thuc_to_hop_to_hop_id", "dats_phuong_thuc_to_hop", ["to_hop_id"])
    op.create_index("idx_dats_nhan_su_de_an_id", "dats_nhan_su", ["de_an_id"])
    op.create_index("idx_dats_co_so_vat_chat_de_an_id", "dats_co_so_vat_chat", ["de_an_id"])
    op.create_index("idx_dats_co_so_vat_chat_co_so_id", "dats_co_so_vat_chat", ["co_so_id"])
    op.create_index("idx_dats_quy_mo_dao_tao_de_an_id", "dats_quy_mo_dao_tao", ["de_an_id"])
    op.create_index("idx_dats_quy_mo_dao_tao_de_an_chuong_trinh_id", "dats_quy_mo_dao_tao", ["de_an_chuong_trinh_id"])
    op.create_index("idx_dats_ty_le_viec_lam_de_an_id", "dats_ty_le_viec_lam", ["de_an_id"])
    op.create_index("idx_dats_ty_le_viec_lam_nganh_dao_tao_id", "dats_ty_le_viec_lam", ["nganh_dao_tao_id"])
    op.create_index("idx_dats_trinh_do_nganh_de_an_chuong_trinh_id", "dats_trinh_do_nganh", ["de_an_chuong_trinh_id"])
    op.create_index("idx_dats_doi_tuong_du_tuyen_de_an_id", "dats_doi_tuong_du_tuyen", ["de_an_id"])
    op.create_index("idx_dats_doi_tuong_du_tuyen_de_an_chuong_trinh_id", "dats_doi_tuong_du_tuyen", ["de_an_chuong_trinh_id"])
    op.create_index("idx_dats_dieu_kien_du_tuyen_de_an_id", "dats_dieu_kien_du_tuyen", ["de_an_id"])
    op.create_index("idx_dats_dieu_kien_du_tuyen_de_an_chuong_trinh_id", "dats_dieu_kien_du_tuyen", ["de_an_chuong_trinh_id"])
    op.create_index("idx_dats_dieu_kien_du_tuyen_de_an_phuong_thuc_id", "dats_dieu_kien_du_tuyen", ["de_an_phuong_thuc_id"])
    op.create_index("idx_dats_dieu_kien_du_tuyen_doi_tuong_du_tuyen_id", "dats_dieu_kien_du_tuyen", ["doi_tuong_du_tuyen_id"])
    op.create_index("idx_dats_tieu_chi_xet_tuyen_de_an_id", "dats_tieu_chi_xet_tuyen", ["de_an_id"])
    op.create_index("idx_dats_tieu_chi_xet_tuyen_de_an_chuong_trinh_id", "dats_tieu_chi_xet_tuyen", ["de_an_chuong_trinh_id"])
    op.create_index("idx_dats_tieu_chi_xet_tuyen_de_an_phuong_thuc_id", "dats_tieu_chi_xet_tuyen", ["de_an_phuong_thuc_id"])
    op.create_index("idx_dats_diem_cong_de_an_id", "dats_diem_cong", ["de_an_id"])
    op.create_index("idx_dats_diem_cong_de_an_chuong_trinh_id", "dats_diem_cong", ["de_an_chuong_trinh_id"])
    op.create_index("idx_dats_diem_cong_de_an_phuong_thuc_id", "dats_diem_cong", ["de_an_phuong_thuc_id"])
    op.create_index("idx_dats_quy_tac_phan_bo_de_an_id", "dats_quy_tac_phan_bo", ["de_an_id"])
    op.create_index("idx_dats_quy_tac_phan_bo_de_an_chuong_trinh_id", "dats_quy_tac_phan_bo", ["de_an_chuong_trinh_id"])
    op.create_index("idx_dats_quy_tac_phan_bo_de_an_phuong_thuc_id", "dats_quy_tac_phan_bo", ["de_an_phuong_thuc_id"])
    op.create_index("idx_dats_ho_so_du_tuyen_de_an_id", "dats_ho_so_du_tuyen", ["de_an_id"])
    op.create_index("idx_dats_ho_so_du_tuyen_de_an_chuong_trinh_id", "dats_ho_so_du_tuyen", ["de_an_chuong_trinh_id"])
    op.create_index("idx_dats_ho_so_du_tuyen_de_an_phuong_thuc_id", "dats_ho_so_du_tuyen", ["de_an_phuong_thuc_id"])
    op.create_index("idx_dats_quy_doi_nguong_dau_vao_de_an_id_nam_tuyen_sinh", "dats_quy_doi_nguong_dau_vao", ["de_an_id", "nam_tuyen_sinh"])
    op.create_index("idx_dats_quy_doi_nguong_dau_vao_de_an_chuong_trinh_id", "dats_quy_doi_nguong_dau_vao", ["de_an_chuong_trinh_id"])
    op.create_index("idx_dats_quy_doi_nguong_dau_vao_phuong_thuc_nguon_id", "dats_quy_doi_nguong_dau_vao", ["phuong_thuc_nguon_id"])
    op.create_index("idx_dats_quy_doi_nguong_dau_vao_phuong_thuc_dich_id", "dats_quy_doi_nguong_dau_vao", ["phuong_thuc_dich_id"])
    op.create_index("idx_dats_quy_doi_nguong_dau_vao_to_hop_nguon_id", "dats_quy_doi_nguong_dau_vao", ["to_hop_nguon_id"])
    op.create_index("idx_dats_quy_doi_nguong_dau_vao_to_hop_dich_id", "dats_quy_doi_nguong_dau_vao", ["to_hop_dich_id"])
    op.create_index("idx_dats_quy_doi_diem_trung_tuyen_de_an_id_nam_tuyen_sinh", "dats_quy_doi_diem_trung_tuyen", ["de_an_id", "nam_tuyen_sinh"])
    op.create_index("idx_dats_quy_doi_diem_trung_tuyen_de_an_chuong_trinh_id", "dats_quy_doi_diem_trung_tuyen", ["de_an_chuong_trinh_id"])
    op.create_index("idx_dats_quy_doi_diem_trung_tuyen_phuong_thuc_nguon_id", "dats_quy_doi_diem_trung_tuyen", ["phuong_thuc_nguon_id"])
    op.create_index("idx_dats_quy_doi_diem_trung_tuyen_phuong_thuc_dich_id", "dats_quy_doi_diem_trung_tuyen", ["phuong_thuc_dich_id"])
    op.create_index("idx_dats_quy_doi_diem_trung_tuyen_to_hop_nguon_id", "dats_quy_doi_diem_trung_tuyen", ["to_hop_nguon_id"])
    op.create_index("idx_dats_quy_doi_diem_trung_tuyen_to_hop_dich_id", "dats_quy_doi_diem_trung_tuyen", ["to_hop_dich_id"])
    op.create_index("idx_dats_chinh_sach_xet_tuyen_thang_de_an_id", "dats_chinh_sach_xet_tuyen_thang", ["de_an_id"])
    op.create_index("idx_dats_chinh_sach_uu_tien_xet_tuyen_de_an_id", "dats_chinh_sach_uu_tien_xet_tuyen", ["de_an_id"])
    op.create_foreign_key(
        "fk_dm_truong_truong_cha_id",
        "dm_truong",
        "dm_truong",
        ["truong_cha_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dm_nganh_dao_tao_nganh_cha_id",
        "dm_nganh_dao_tao",
        "dm_nganh_dao_tao",
        ["nganh_cha_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dm_nganh_dao_tao_van_ban_id",
        "dm_nganh_dao_tao",
        "dm_van_ban",
        ["van_ban_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dm_doi_tuong_uu_tien_van_ban_id",
        "dm_doi_tuong_uu_tien",
        "dm_van_ban",
        ["van_ban_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dm_khu_vuc_uu_tien_van_ban_id",
        "dm_khu_vuc_uu_tien",
        "dm_van_ban",
        ["van_ban_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dm_to_hop_mon_hoc_chi_tiet_to_hop_id",
        "dm_to_hop_mon_hoc_chi_tiet",
        "dm_to_hop_mon_hoc",
        ["to_hop_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dm_to_hop_mon_hoc_chi_tiet_mon_hoc_id",
        "dm_to_hop_mon_hoc_chi_tiet",
        "dm_mon_hoc",
        ["mon_hoc_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_tuyen_sinh_truong_id",
        "dats_tuyen_sinh",
        "dm_truong",
        ["truong_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_tru_so_de_an_id",
        "dats_tru_so",
        "dats_tuyen_sinh",
        ["de_an_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_website_de_an_id",
        "dats_website",
        "dats_tuyen_sinh",
        ["de_an_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_lien_he_tuyen_sinh_de_an_id",
        "dats_lien_he_tuyen_sinh",
        "dats_tuyen_sinh",
        ["de_an_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_chuong_trinh_dao_tao_de_an_id",
        "dats_chuong_trinh_dao_tao",
        "dats_tuyen_sinh",
        ["de_an_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_chuong_trinh_dao_tao_nganh_dao_tao_id",
        "dats_chuong_trinh_dao_tao",
        "dm_nganh_dao_tao",
        ["nganh_dao_tao_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_chuong_trinh_dao_tao_co_so_id",
        "dats_chuong_trinh_dao_tao",
        "dats_tru_so",
        ["co_so_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_ke_hoach_tuyen_sinh_de_an_chuong_trinh_id",
        "dats_ke_hoach_tuyen_sinh",
        "dats_chuong_trinh_dao_tao",
        ["de_an_chuong_trinh_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_phuong_thuc_de_an_chuong_trinh_id",
        "dats_phuong_thuc",
        "dats_chuong_trinh_dao_tao",
        ["de_an_chuong_trinh_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_phuong_thuc_phuong_thuc_id",
        "dats_phuong_thuc",
        "dm_phuong_thuc_tuyen_sinh",
        ["phuong_thuc_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_phuong_thuc_to_hop_id",
        "dats_phuong_thuc",
        "dm_to_hop_mon_hoc",
        ["to_hop_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_phuong_thuc_to_hop_de_an_phuong_thuc_id",
        "dats_phuong_thuc_to_hop",
        "dats_phuong_thuc",
        ["de_an_phuong_thuc_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_phuong_thuc_to_hop_to_hop_id",
        "dats_phuong_thuc_to_hop",
        "dm_to_hop_mon_hoc",
        ["to_hop_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_nhan_su_de_an_id",
        "dats_nhan_su",
        "dats_tuyen_sinh",
        ["de_an_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_co_so_vat_chat_de_an_id",
        "dats_co_so_vat_chat",
        "dats_tuyen_sinh",
        ["de_an_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_co_so_vat_chat_co_so_id",
        "dats_co_so_vat_chat",
        "dats_tru_so",
        ["co_so_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_quy_mo_dao_tao_de_an_id",
        "dats_quy_mo_dao_tao",
        "dats_tuyen_sinh",
        ["de_an_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_quy_mo_dao_tao_de_an_chuong_trinh_id",
        "dats_quy_mo_dao_tao",
        "dats_chuong_trinh_dao_tao",
        ["de_an_chuong_trinh_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_ty_le_viec_lam_de_an_id",
        "dats_ty_le_viec_lam",
        "dats_tuyen_sinh",
        ["de_an_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_ty_le_viec_lam_nganh_dao_tao_id",
        "dats_ty_le_viec_lam",
        "dm_nganh_dao_tao",
        ["nganh_dao_tao_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_trinh_do_nganh_de_an_chuong_trinh_id",
        "dats_trinh_do_nganh",
        "dats_chuong_trinh_dao_tao",
        ["de_an_chuong_trinh_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_doi_tuong_du_tuyen_de_an_id",
        "dats_doi_tuong_du_tuyen",
        "dats_tuyen_sinh",
        ["de_an_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_doi_tuong_du_tuyen_de_an_chuong_trinh_id",
        "dats_doi_tuong_du_tuyen",
        "dats_chuong_trinh_dao_tao",
        ["de_an_chuong_trinh_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_dieu_kien_du_tuyen_de_an_id",
        "dats_dieu_kien_du_tuyen",
        "dats_tuyen_sinh",
        ["de_an_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_dieu_kien_du_tuyen_de_an_chuong_trinh_id",
        "dats_dieu_kien_du_tuyen",
        "dats_chuong_trinh_dao_tao",
        ["de_an_chuong_trinh_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_dieu_kien_du_tuyen_de_an_phuong_thuc_id",
        "dats_dieu_kien_du_tuyen",
        "dats_phuong_thuc",
        ["de_an_phuong_thuc_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_dieu_kien_du_tuyen_doi_tuong_du_tuyen_id",
        "dats_dieu_kien_du_tuyen",
        "dats_doi_tuong_du_tuyen",
        ["doi_tuong_du_tuyen_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_tieu_chi_xet_tuyen_de_an_id",
        "dats_tieu_chi_xet_tuyen",
        "dats_tuyen_sinh",
        ["de_an_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_tieu_chi_xet_tuyen_de_an_chuong_trinh_id",
        "dats_tieu_chi_xet_tuyen",
        "dats_chuong_trinh_dao_tao",
        ["de_an_chuong_trinh_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_tieu_chi_xet_tuyen_de_an_phuong_thuc_id",
        "dats_tieu_chi_xet_tuyen",
        "dats_phuong_thuc",
        ["de_an_phuong_thuc_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_diem_cong_de_an_id",
        "dats_diem_cong",
        "dats_tuyen_sinh",
        ["de_an_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_diem_cong_de_an_chuong_trinh_id",
        "dats_diem_cong",
        "dats_chuong_trinh_dao_tao",
        ["de_an_chuong_trinh_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_diem_cong_de_an_phuong_thuc_id",
        "dats_diem_cong",
        "dats_phuong_thuc",
        ["de_an_phuong_thuc_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_quy_tac_phan_bo_de_an_id",
        "dats_quy_tac_phan_bo",
        "dats_tuyen_sinh",
        ["de_an_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_quy_tac_phan_bo_de_an_chuong_trinh_id",
        "dats_quy_tac_phan_bo",
        "dats_chuong_trinh_dao_tao",
        ["de_an_chuong_trinh_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_quy_tac_phan_bo_de_an_phuong_thuc_id",
        "dats_quy_tac_phan_bo",
        "dats_phuong_thuc",
        ["de_an_phuong_thuc_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_ho_so_du_tuyen_de_an_id",
        "dats_ho_so_du_tuyen",
        "dats_tuyen_sinh",
        ["de_an_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_ho_so_du_tuyen_de_an_chuong_trinh_id",
        "dats_ho_so_du_tuyen",
        "dats_chuong_trinh_dao_tao",
        ["de_an_chuong_trinh_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_ho_so_du_tuyen_de_an_phuong_thuc_id",
        "dats_ho_so_du_tuyen",
        "dats_phuong_thuc",
        ["de_an_phuong_thuc_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_quy_doi_nguong_dau_vao_de_an_id",
        "dats_quy_doi_nguong_dau_vao",
        "dats_tuyen_sinh",
        ["de_an_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_quy_doi_nguong_dau_vao_de_an_chuong_trinh_id",
        "dats_quy_doi_nguong_dau_vao",
        "dats_chuong_trinh_dao_tao",
        ["de_an_chuong_trinh_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_quy_doi_nguong_dau_vao_phuong_thuc_nguon_id",
        "dats_quy_doi_nguong_dau_vao",
        "dm_phuong_thuc_tuyen_sinh",
        ["phuong_thuc_nguon_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_quy_doi_nguong_dau_vao_phuong_thuc_dich_id",
        "dats_quy_doi_nguong_dau_vao",
        "dm_phuong_thuc_tuyen_sinh",
        ["phuong_thuc_dich_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_quy_doi_nguong_dau_vao_to_hop_nguon_id",
        "dats_quy_doi_nguong_dau_vao",
        "dm_to_hop_mon_hoc",
        ["to_hop_nguon_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_quy_doi_nguong_dau_vao_to_hop_dich_id",
        "dats_quy_doi_nguong_dau_vao",
        "dm_to_hop_mon_hoc",
        ["to_hop_dich_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_quy_doi_diem_trung_tuyen_de_an_id",
        "dats_quy_doi_diem_trung_tuyen",
        "dats_tuyen_sinh",
        ["de_an_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_quy_doi_diem_trung_tuyen_de_an_chuong_trinh_id",
        "dats_quy_doi_diem_trung_tuyen",
        "dats_chuong_trinh_dao_tao",
        ["de_an_chuong_trinh_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_quy_doi_diem_trung_tuyen_phuong_thuc_nguon_id",
        "dats_quy_doi_diem_trung_tuyen",
        "dm_phuong_thuc_tuyen_sinh",
        ["phuong_thuc_nguon_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_quy_doi_diem_trung_tuyen_phuong_thuc_dich_id",
        "dats_quy_doi_diem_trung_tuyen",
        "dm_phuong_thuc_tuyen_sinh",
        ["phuong_thuc_dich_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_quy_doi_diem_trung_tuyen_to_hop_nguon_id",
        "dats_quy_doi_diem_trung_tuyen",
        "dm_to_hop_mon_hoc",
        ["to_hop_nguon_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_quy_doi_diem_trung_tuyen_to_hop_dich_id",
        "dats_quy_doi_diem_trung_tuyen",
        "dm_to_hop_mon_hoc",
        ["to_hop_dich_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_chinh_sach_xet_tuyen_thang_de_an_id",
        "dats_chinh_sach_xet_tuyen_thang",
        "dats_tuyen_sinh",
        ["de_an_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dats_chinh_sach_uu_tien_xet_tuyen_de_an_id",
        "dats_chinh_sach_uu_tien_xet_tuyen",
        "dats_tuyen_sinh",
        ["de_an_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    """Go khoa ngoai, bang moi, chi muc va cot da bo sung."""
    op.drop_constraint("fk_dm_khu_vuc_uu_tien_van_ban_id", "dm_khu_vuc_uu_tien", type_="foreignkey")
    op.drop_constraint("fk_dm_doi_tuong_uu_tien_van_ban_id", "dm_doi_tuong_uu_tien", type_="foreignkey")
    op.drop_constraint("fk_dm_nganh_dao_tao_van_ban_id", "dm_nganh_dao_tao", type_="foreignkey")
    op.drop_constraint("fk_dm_nganh_dao_tao_nganh_cha_id", "dm_nganh_dao_tao", type_="foreignkey")
    op.drop_table("dats_chinh_sach_uu_tien_xet_tuyen")
    op.drop_table("dats_chinh_sach_xet_tuyen_thang")
    op.drop_table("dats_quy_doi_diem_trung_tuyen")
    op.drop_table("dats_quy_doi_nguong_dau_vao")
    op.drop_table("dats_ho_so_du_tuyen")
    op.drop_table("dats_quy_tac_phan_bo")
    op.drop_table("dats_diem_cong")
    op.drop_table("dats_tieu_chi_xet_tuyen")
    op.drop_table("dats_dieu_kien_du_tuyen")
    op.drop_table("dats_doi_tuong_du_tuyen")
    op.drop_table("dats_trinh_do_nganh")
    op.drop_table("dats_ty_le_viec_lam")
    op.drop_table("dats_quy_mo_dao_tao")
    op.drop_table("dats_co_so_vat_chat")
    op.drop_table("dats_nhan_su")
    op.drop_table("dats_phuong_thuc_to_hop")
    op.drop_table("dats_phuong_thuc")
    op.drop_table("dats_ke_hoach_tuyen_sinh")
    op.drop_table("dats_chuong_trinh_dao_tao")
    op.drop_table("dats_lien_he_tuyen_sinh")
    op.drop_table("dats_website")
    op.drop_table("dats_tru_so")
    op.drop_table("dats_tuyen_sinh")
    op.drop_table("dm_to_hop_mon_hoc_chi_tiet")
    op.drop_table("dm_thanh_tich_hoc_tap")
    op.drop_table("dm_bai_thi_danh_gia")
    op.drop_table("dm_bang_cap_chung_chi")
    op.drop_table("dm_truong")
    op.drop_table("dm_van_ban")
    op.drop_index("uk_dm_mon_hoc_ma_mon", table_name="dm_mon_hoc")
    op.drop_index("idx_dm_phuong_thuc_tuyen_sinh_nam_ap_dung_tu", table_name="dm_phuong_thuc_tuyen_sinh")
    op.drop_index("idx_dm_khu_vuc_uu_tien_van_ban_id", table_name="dm_khu_vuc_uu_tien")
    op.drop_index("idx_dm_khu_vuc_uu_tien_ma_khu_vuc_nam_ap_dung", table_name="dm_khu_vuc_uu_tien")
    op.drop_index("idx_dm_doi_tuong_uu_tien_van_ban_id", table_name="dm_doi_tuong_uu_tien")
    op.drop_index("idx_dm_doi_tuong_uu_tien_ma_doi_tuong_nam_ap_dung", table_name="dm_doi_tuong_uu_tien")
    op.drop_index("idx_dm_nganh_dao_tao_van_ban_id", table_name="dm_nganh_dao_tao")
    op.drop_index("idx_dm_nganh_dao_tao_nganh_cha_id", table_name="dm_nganh_dao_tao")
    op.drop_index("idx_dm_nganh_dao_tao_ngay_hieu_luc_tu", table_name="dm_nganh_dao_tao")
    op.drop_column("dm_nganh_dao_tao", "cap_nhat_luc")
    op.drop_column("dm_nganh_dao_tao", "tao_luc")
    op.drop_column("dm_nganh_dao_tao", "thu_tu_hien_thi")
    op.drop_column("dm_nganh_dao_tao", "van_ban_id")
    op.drop_column("dm_nganh_dao_tao", "ghi_chu_theo_thong_tu")
    op.drop_column("dm_nganh_dao_tao", "ngay_hieu_luc_den")
    op.drop_column("dm_nganh_dao_tao", "ngay_hieu_luc_tu")
    op.drop_column("dm_nganh_dao_tao", "trinh_do_ap_dung")
    op.drop_column("dm_nganh_dao_tao", "nganh_cha_id")
    op.drop_column("dm_nganh_dao_tao", "cap_danh_muc")
    op.drop_column("dm_ton_giao", "ten_goi_khac")
    op.drop_column("dm_doi_tuong_uu_tien", "thu_tu_hien_thi")
    op.drop_column("dm_doi_tuong_uu_tien", "van_ban_id")
    op.drop_column("dm_doi_tuong_uu_tien", "nam_ap_dung")
    op.drop_column("dm_doi_tuong_uu_tien", "diem_uu_tien_co_ban")
    op.drop_column("dm_doi_tuong_uu_tien", "nhom_uu_tien")
    op.drop_column("dm_doi_tuong_uu_tien", "mo_ta_dieu_kien")
    op.drop_column("dm_khu_vuc_uu_tien", "van_ban_id")
    op.drop_column("dm_khu_vuc_uu_tien", "nam_ap_dung")
    op.drop_column("dm_khu_vuc_uu_tien", "diem_uu_tien_co_ban")
    op.drop_column("dm_khu_vuc_uu_tien", "mo_ta_dieu_kien")
    op.drop_column("dm_phuong_thuc_tuyen_sinh", "cap_nhat_luc")
    op.drop_column("dm_phuong_thuc_tuyen_sinh", "tao_luc")
    op.drop_column("dm_phuong_thuc_tuyen_sinh", "ghi_chu")
    op.drop_column("dm_phuong_thuc_tuyen_sinh", "nguon_du_lieu_url")
    op.drop_column("dm_phuong_thuc_tuyen_sinh", "thu_tu_hien_thi")
    op.drop_column("dm_phuong_thuc_tuyen_sinh", "nam_ap_dung_den")
    op.drop_column("dm_phuong_thuc_tuyen_sinh", "nam_ap_dung_tu")
    op.drop_column("dm_phuong_thuc_tuyen_sinh", "pham_vi_ap_dung")
    op.drop_column("dm_phuong_thuc_tuyen_sinh", "loai_phuong_thuc")
    op.drop_column("dm_mon_hoc", "cap_nhat_luc")
    op.drop_column("dm_mon_hoc", "tao_luc")
    op.drop_column("dm_mon_hoc", "ghi_chu")
    op.drop_column("dm_mon_hoc", "ten_goi_khac")
    op.drop_column("dm_mon_hoc", "ten_tieng_anh")
    op.drop_column("dm_mon_hoc", "ten_mon")
    op.drop_column("dm_mon_hoc", "ma_mon")
    op.drop_column("dm_to_hop_mon_hoc", "cap_nhat_luc")
    op.drop_column("dm_to_hop_mon_hoc", "tao_luc")
    op.drop_column("dm_to_hop_mon_hoc", "nam_ap_dung_den")
    op.drop_column("dm_to_hop_mon_hoc", "nam_ap_dung_tu")
    op.drop_column("dm_to_hop_mon_hoc", "mo_ta")
