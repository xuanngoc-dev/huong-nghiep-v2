"""Tạo danh mục nhóm nghề đi làm, nghề cụ thể, tiêu chí gợi ý và bảng liên kết nhóm nghề - tiêu chí, kèm dữ liệu mẫu.

Lương tính bằng triệu đồng/tháng.

Revision ID: 20261126_0069
Revises: 20261125_0068
Create Date: 2026-11-26 10:00:00.000000
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.mysql import TINYINT

revision = "20261126_0069"
down_revision = "20261125_0068"
branch_labels = None
depends_on = None

_BANG = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}

LOAI_HINH_DAU_VAO = ("di_lam_ngay", "hoc_nghe_ngan_han", "tu_hoc_ky_nang")
NHOM_MUC_TIEU = ("kiem_tien_ngay", "nghe_vung_chac", "thu_nhap_dot_pha")

# (id, ma_nhom, ten_nhom, mo_ta_dac_diem, loai_hinh_dau_vao, thoi_gian_text, thang_min, thang_max, dieu_kien_dau_vao,
#  muc_luong_text, luong_min, luong_max, luong_kinh_nghiem_max, danh_gia_trien_vong, lo_trinh_phat_trien,
#  nhom_muc_tieu, ma_holland)
NHOM_NGHE = [
    (
        1, "CONG_NHAN_SAN_XUAT", "Công nhân sản xuất, lắp ráp",
        "Làm việc tại nhà máy, khu công nghiệp theo dây chuyền; công việc lặp lại, có ca kíp, được đào tạo tại chỗ.",
        "di_lam_ngay", "Đào tạo tại chỗ 1-2 tuần", 0, 1,
        "Tốt nghiệp THCS/THPT, đủ 18 tuổi, sức khỏe tốt.",
        "7 - 9 triệu/tháng", 7, 9, 15,
        "Nhu cầu tuyển dụng lớn, ổn định tại các khu công nghiệp",
        "Công nhân → Tổ trưởng → Trưởng chuyền → Quản lý xưởng (cần học thêm kỹ năng quản lý).",
        "kiem_tien_ngay", "RC",
    ),
    (
        2, "BAN_HANG_DICH_VU", "Bán hàng, chăm sóc khách hàng",
        "Tư vấn, bán hàng tại cửa hàng, siêu thị, tổng đài; thu nhập gồm lương cứng và hoa hồng theo doanh số.",
        "di_lam_ngay", "Đào tạo tại chỗ 1-4 tuần", 0, 1,
        "Tốt nghiệp THPT, giao tiếp tốt, ngoại hình ưa nhìn là lợi thế.",
        "6 - 8 triệu/tháng + hoa hồng", 6, 8, 20,
        "Luôn có nhu cầu, thu nhập phụ thuộc năng lực bán hàng",
        "Nhân viên → Trưởng ca → Cửa hàng trưởng → Quản lý khu vực.",
        "kiem_tien_ngay", "ES",
    ),
    (
        3, "GIAO_HANG_VAN_TAI", "Giao hàng, vận tải",
        "Giao hàng cho sàn thương mại điện tử, lái xe công nghệ, lái xe tải; thời gian linh hoạt, làm việc ngoài trời.",
        "di_lam_ngay", "0 - 3 tháng (học bằng lái nếu cần)", 0, 3,
        "Đủ 18 tuổi, có bằng lái xe phù hợp, có phương tiện cá nhân.",
        "8 - 12 triệu/tháng", 8, 12, 18,
        "Nhu cầu tăng theo thương mại điện tử, cạnh tranh cao",
        "Giao hàng → Lái xe tải hạng C → Điều phối kho vận → Tự mở dịch vụ vận chuyển.",
        "kiem_tien_ngay", "RE",
    ),
    (
        4, "DIEN_CO_KHI", "Điện, điện lạnh, cơ khí sửa chữa",
        "Lắp đặt, sửa chữa điện dân dụng, điện lạnh, ô tô, xe máy; nghề kỹ thuật cần tay nghề và chứng chỉ.",
        "hoc_nghe_ngan_han", "3 - 12 tháng tại trường nghề", 3, 12,
        "Tốt nghiệp THCS/THPT, khéo tay, không sợ độ cao/điện.",
        "7 - 10 triệu/tháng", 7, 10, 25,
        "Nghề bền vững, thiếu thợ giỏi, dễ tự mở tiệm",
        "Học việc → Thợ chính → Trưởng nhóm kỹ thuật → Tự mở tiệm/xưởng dịch vụ.",
        "nghe_vung_chac", "RI",
    ),
    (
        5, "BEP_NHA_HANG", "Nấu ăn, pha chế, nhà hàng - khách sạn",
        "Làm việc tại bếp nhà hàng, quán cà phê, khách sạn, resort; cường độ cao vào giờ cao điểm và dịp lễ.",
        "hoc_nghe_ngan_han", "3 - 6 tháng", 3, 6,
        "Tốt nghiệp THCS/THPT, có giấy khám sức khỏe, yêu thích ẩm thực.",
        "6 - 9 triệu/tháng", 6, 9, 30,
        "Phát triển theo du lịch, đầu bếp giỏi thu nhập cao",
        "Phụ bếp → Đầu bếp → Bếp phó → Bếp trưởng → Mở quán riêng.",
        "nghe_vung_chac", "RAS",
    ),
    (
        6, "LAM_DEP", "Làm đẹp: tóc, nail, spa",
        "Cắt tóc, làm móng, chăm sóc da tại salon, spa; nghề thủ công cần thẩm mỹ và giao tiếp với khách.",
        "hoc_nghe_ngan_han", "2 - 6 tháng", 2, 6,
        "Không yêu cầu bằng cấp, khéo tay, có gu thẩm mỹ.",
        "6 - 10 triệu/tháng", 6, 10, 30,
        "Nhu cầu tăng, dễ khởi nghiệp với vốn nhỏ",
        "Học viên → Thợ phụ → Thợ chính → Mở salon/spa riêng → Đào tạo học viên.",
        "nghe_vung_chac", "AS",
    ),
    (
        7, "KY_NANG_SO", "Kỹ năng số: thiết kế, lập trình, marketing online",
        "Thiết kế đồ họa, dựng video, lập trình web, chạy quảng cáo; làm tại công ty hoặc tự do (freelance).",
        "tu_hoc_ky_nang", "6 - 12 tháng tự học/khóa ngắn hạn", 6, 12,
        "Có máy tính, đọc hiểu tiếng Anh cơ bản, kiên trì tự học.",
        "7 - 12 triệu/tháng", 7, 12, 40,
        "Triển vọng rất tốt, thu nhập tăng nhanh theo năng lực",
        "Thực tập → Nhân viên junior → Senior → Trưởng nhóm / Freelancer quốc tế.",
        "thu_nhap_dot_pha", "AIE",
    ),
    (
        8, "KINH_DOANH_ONLINE", "Kinh doanh online, sáng tạo nội dung",
        "Bán hàng trên sàn thương mại điện tử, mạng xã hội, livestream, làm nội dung; tự chủ thời gian, thu nhập không cố định.",
        "tu_hoc_ky_nang", "1 - 6 tháng", 1, 6,
        "Có điện thoại/máy tính, chịu khó học hỏi, vốn ban đầu nhỏ.",
        "5 - 10 triệu/tháng (không cố định)", 5, 10, 50,
        "Cơ hội lớn nhưng rủi ro cao, cạnh tranh gay gắt",
        "Cộng tác viên → Chủ shop nhỏ → Xây dựng thương hiệu riêng → Mở rộng kênh phân phối.",
        "thu_nhap_dot_pha", "EA",
    ),
]

# (nhom_nghe_di_lam_id, ten_nghe, mo_ta_ngan, yeu_cau_them)
NGHE_CU_THE = [
    (1, "Công nhân lắp ráp điện tử", "Lắp ráp linh kiện điện thoại, máy tính theo dây chuyền.", "Thị lực tốt, cẩn thận"),
    (1, "Công nhân may công nghiệp", "May các công đoạn sản phẩm dệt may xuất khẩu.", None),
    (1, "Công nhân vận hành máy", "Vận hành, giám sát máy móc sản xuất.", "Chịu được làm ca đêm"),
    (2, "Nhân viên bán hàng cửa hàng", "Tư vấn, bán hàng tại cửa hàng thời trang, điện máy, siêu thị.", None),
    (2, "Nhân viên tổng đài", "Giải đáp, chăm sóc khách hàng qua điện thoại.", "Giọng nói rõ ràng"),
    (2, "Nhân viên kinh doanh thị trường", "Tìm kiếm, phát triển đại lý và khách hàng.", "Có xe máy"),
    (3, "Nhân viên giao hàng", "Giao hàng cho các sàn thương mại điện tử, đơn vị vận chuyển.", "Có xe máy, bằng A1"),
    (3, "Tài xế xe công nghệ", "Chở khách, giao đồ ăn qua ứng dụng.", "Có bằng lái phù hợp"),
    (3, "Lái xe tải", "Vận chuyển hàng hóa đường dài, nội thành.", "Bằng lái hạng C trở lên"),
    (4, "Thợ điện dân dụng", "Lắp đặt, sửa chữa hệ thống điện nhà ở, công trình.", "Chứng chỉ an toàn điện"),
    (4, "Thợ sửa chữa điện lạnh", "Lắp đặt, bảo dưỡng điều hòa, tủ lạnh, máy giặt.", None),
    (4, "Thợ sửa chữa ô tô, xe máy", "Bảo dưỡng, sửa chữa động cơ và hệ thống điện xe.", None),
    (5, "Đầu bếp", "Chế biến món ăn tại nhà hàng, khách sạn.", "Chứng chỉ nghề nấu ăn là lợi thế"),
    (5, "Nhân viên pha chế (bartender/barista)", "Pha chế đồ uống tại quán cà phê, quầy bar.", None),
    (5, "Nhân viên phục vụ, lễ tân khách sạn", "Đón tiếp, phục vụ khách lưu trú, ăn uống.", "Tiếng Anh giao tiếp là lợi thế"),
    (6, "Thợ cắt tóc", "Cắt, uốn, nhuộm tóc nam nữ.", None),
    (6, "Thợ làm nail", "Chăm sóc, sơn, vẽ móng.", "Khéo tay, tỉ mỉ"),
    (6, "Kỹ thuật viên spa", "Chăm sóc da, massage thư giãn.", "Chứng chỉ kỹ thuật viên spa"),
    (7, "Thiết kế đồ họa", "Thiết kế ấn phẩm, banner, nhận diện thương hiệu.", "Thành thạo Photoshop/Illustrator"),
    (7, "Lập trình viên web", "Xây dựng, bảo trì website và ứng dụng web.", "Có sản phẩm cá nhân để ứng tuyển"),
    (7, "Nhân viên quảng cáo trực tuyến", "Chạy quảng cáo Facebook, Google, TikTok.", None),
    (8, "Chủ shop trên sàn thương mại điện tử", "Kinh doanh trên Shopee, Lazada, TikTok Shop.", "Vốn nhập hàng ban đầu"),
    (8, "Người livestream bán hàng", "Livestream giới thiệu, bán sản phẩm.", "Tự tin trước ống kính"),
    (8, "Người sáng tạo nội dung", "Làm video, bài viết trên mạng xã hội để kiếm tiền từ quảng cáo, hợp tác.", None),
]

# (id, ma_tieu_chi, ten_tieu_chi, nhom_tieu_chi)
TIEU_CHI = [
    (1, "THICH_VAN_DONG", "Thích làm việc chân tay, vận động", "Sở thích"),
    (2, "THICH_GIAO_TIEP", "Thích giao tiếp, gặp gỡ người mới", "Sở thích"),
    (3, "THICH_SANG_TAO", "Thích sáng tạo, có gu thẩm mỹ", "Sở thích"),
    (4, "THICH_CONG_NGHE", "Thích máy tính, công nghệ", "Sở thích"),
    (5, "SUC_KHOE_TOT", "Sức khỏe tốt, chịu được cường độ cao", "Năng lực"),
    (6, "KHEO_TAY", "Khéo tay, tỉ mỉ", "Năng lực"),
    (7, "TU_HOC_TOT", "Có khả năng tự học", "Năng lực"),
    (8, "CAN_THU_NHAP_NGAY", "Cần có thu nhập ngay", "Hoàn cảnh"),
    (9, "IT_VON", "Không có hoặc ít vốn ban đầu", "Hoàn cảnh"),
    (10, "MUON_ON_DINH", "Muốn công việc ổn định lâu dài", "Mục tiêu"),
    (11, "MUON_TU_LAM_CHU", "Muốn tự kinh doanh, làm chủ", "Mục tiêu"),
]

# (nhom_nghe_di_lam_id, tieu_chi_goi_y_id, diem_phu_hop, ghi_chu)
NHOM_NGHE_TIEU_CHI = [
    (1, 1, 4, None), (1, 5, 5, "Làm ca, đứng nhiều giờ"), (1, 8, 5, "Có lương ngay tháng đầu"),
    (1, 9, 5, None), (1, 10, 4, None),
    (2, 2, 5, "Giao tiếp là kỹ năng cốt lõi"), (2, 8, 5, None), (2, 9, 5, None), (2, 11, 3, None),
    (3, 1, 4, None), (3, 5, 5, "Làm việc ngoài trời"), (3, 8, 5, None), (3, 9, 3, "Cần có phương tiện"),
    (3, 11, 3, None),
    (4, 1, 4, None), (4, 6, 5, None), (4, 10, 5, "Nghề kỹ thuật luôn có việc"), (4, 11, 4, "Dễ mở tiệm sửa chữa"),
    (5, 1, 3, None), (5, 3, 4, None), (5, 5, 4, None), (5, 6, 4, None), (5, 10, 4, None), (5, 11, 4, None),
    (6, 2, 4, None), (6, 3, 5, None), (6, 6, 5, "Yêu cầu tỉ mỉ cao"), (6, 11, 5, "Vốn mở tiệm nhỏ"),
    (7, 3, 4, None), (7, 4, 5, None), (7, 7, 5, "Phải liên tục cập nhật kiến thức"), (7, 9, 4, None),
    (7, 11, 3, None),
    (8, 2, 4, None), (8, 3, 4, None), (8, 4, 4, None), (8, 7, 4, None), (8, 11, 5, None),
]


def upgrade() -> None:
    nhom_nghe = op.create_table(
        "dm_nhom_nghe_di_lam",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("ma_nhom", sa.String(50), nullable=False),
        sa.Column("ten_nhom", sa.String(255), nullable=False),
        sa.Column("mo_ta_dac_diem", sa.Text(), nullable=False),
        sa.Column("loai_hinh_dau_vao", sa.Enum(*LOAI_HINH_DAU_VAO, name="loai_hinh_dau_vao"), nullable=True),
        sa.Column("thoi_gian_dao_tao_text", sa.String(100), nullable=True),
        sa.Column("thoi_gian_dao_tao_thang_min", sa.Integer(), nullable=True),
        sa.Column("thoi_gian_dao_tao_thang_max", sa.Integer(), nullable=True),
        sa.Column("dieu_kien_dau_vao", sa.Text(), nullable=True),
        sa.Column("muc_luong_text", sa.String(100), nullable=True),
        sa.Column("luong_khoi_diem_min", sa.Numeric(5, 2), nullable=True),
        sa.Column("luong_khoi_diem_max", sa.Numeric(5, 2), nullable=True),
        sa.Column("luong_kinh_nghiem_max", sa.Numeric(5, 2), nullable=True),
        sa.Column("danh_gia_trien_vong", sa.String(255), nullable=True),
        sa.Column("lo_trinh_phat_trien", sa.Text(), nullable=True),
        sa.Column("nhom_muc_tieu", sa.Enum(*NHOM_MUC_TIEU, name="nhom_muc_tieu"), nullable=True),
        sa.Column("ma_holland", sa.String(20), nullable=True),
        sa.Column("trang_thai", TINYINT(), nullable=False, server_default="1"),
        sa.Column("ngay_tao", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "ngay_cap_nhat",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
        **_BANG,
    )
    op.create_index("ix_dm_nhom_nghe_di_lam_ma_nhom", "dm_nhom_nghe_di_lam", ["ma_nhom"], unique=True)

    nghe_cu_the = op.create_table(
        "dm_nghe_cu_the_di_lam",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "nhom_nghe_di_lam_id",
            sa.Integer(),
            sa.ForeignKey("dm_nhom_nghe_di_lam.id", name="fk_dm_ncdl_nhom_nghe_di_lam_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("ten_nghe", sa.String(255), nullable=False),
        sa.Column("mo_ta_ngan", sa.Text(), nullable=True),
        sa.Column("yeu_cau_them", sa.String(500), nullable=True),
        **_BANG,
    )
    op.create_index(
        "ix_dm_nghe_cu_the_di_lam_nhom_nghe_di_lam_id", "dm_nghe_cu_the_di_lam", ["nhom_nghe_di_lam_id"]
    )

    tieu_chi = op.create_table(
        "dm_tieu_chi_goi_y",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("ma_tieu_chi", sa.String(50), nullable=False),
        sa.Column("ten_tieu_chi", sa.String(255), nullable=False),
        sa.Column("nhom_tieu_chi", sa.String(100), nullable=True),
        **_BANG,
    )
    op.create_index("ix_dm_tieu_chi_goi_y_ma_tieu_chi", "dm_tieu_chi_goi_y", ["ma_tieu_chi"], unique=True)

    lien_ket = op.create_table(
        "dm_nhom_nghe_tieu_chi",
        sa.Column(
            "nhom_nghe_di_lam_id",
            sa.Integer(),
            sa.ForeignKey("dm_nhom_nghe_di_lam.id", name="fk_dm_nntc_nhom_nghe_di_lam_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "tieu_chi_goi_y_id",
            sa.Integer(),
            sa.ForeignKey("dm_tieu_chi_goi_y.id", name="fk_dm_nntc_tieu_chi_goi_y_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("diem_phu_hop", TINYINT(), nullable=True),
        sa.Column("ghi_chu", sa.String(500), nullable=True),
        sa.CheckConstraint("diem_phu_hop BETWEEN 1 AND 5", name="chk_dm_nhom_nghe_tieu_chi_diem"),
        **_BANG,
    )
    op.create_index(
        "ix_dm_nhom_nghe_tieu_chi_tieu_chi_goi_y_id", "dm_nhom_nghe_tieu_chi", ["tieu_chi_goi_y_id"]
    )

    # Dữ liệu mẫu — bảng mới nên gán id tường minh để liên kết.
    op.bulk_insert(
        nhom_nghe,
        [
            dict(
                zip(
                    (
                        "id", "ma_nhom", "ten_nhom", "mo_ta_dac_diem", "loai_hinh_dau_vao",
                        "thoi_gian_dao_tao_text", "thoi_gian_dao_tao_thang_min", "thoi_gian_dao_tao_thang_max",
                        "dieu_kien_dau_vao", "muc_luong_text", "luong_khoi_diem_min", "luong_khoi_diem_max",
                        "luong_kinh_nghiem_max", "danh_gia_trien_vong", "lo_trinh_phat_trien", "nhom_muc_tieu",
                        "ma_holland",
                    ),
                    dong,
                    strict=True,
                )
            )
            for dong in NHOM_NGHE
        ],
    )
    op.bulk_insert(
        nghe_cu_the,
        [
            dict(zip(("nhom_nghe_di_lam_id", "ten_nghe", "mo_ta_ngan", "yeu_cau_them"), dong, strict=True))
            for dong in NGHE_CU_THE
        ],
    )
    op.bulk_insert(
        tieu_chi,
        [dict(zip(("id", "ma_tieu_chi", "ten_tieu_chi", "nhom_tieu_chi"), dong, strict=True)) for dong in TIEU_CHI],
    )
    op.bulk_insert(
        lien_ket,
        [
            dict(zip(("nhom_nghe_di_lam_id", "tieu_chi_goi_y_id", "diem_phu_hop", "ghi_chu"), dong, strict=True))
            for dong in NHOM_NGHE_TIEU_CHI
        ],
    )


def downgrade() -> None:
    op.drop_table("dm_nhom_nghe_tieu_chi")
    op.drop_table("dm_tieu_chi_goi_y")
    op.drop_table("dm_nghe_cu_the_di_lam")
    op.drop_table("dm_nhom_nghe_di_lam")
