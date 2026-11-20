"""Tạo danh mục du học sau THPT: hướng đi, quốc gia, ngành, chi phí, thủ tục, kênh kết nối, kèm dữ liệu mẫu.

thpt_duhoc_quoc_gia_id NULL nghĩa là dòng áp dụng chung cho cả hướng đi. Số liệu chi phí, lương là tham khảo.

Revision ID: 20261129_0072
Revises: 20261128_0071
Create Date: 2026-11-29 10:00:00.000000
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.mysql import TINYINT

revision = "20261129_0072"
down_revision = "20261128_0071"
branch_labels = None
depends_on = None

_BANG = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}

LOAI_HINH_DU_HOC = ("du_hoc_nghe", "du_hoc_hoc_thuat", "chuyen_tiep")
LOAI_CHI_PHI = ("truoc_khi_bay", "tai_nuoc_so_tai", "chung_minh_tai_chinh", "khoan_bu_dap")
LOAI_KENH = ("chinh_thong", "trung_tam_tu_van", "cong_dong", "ho_tro_he_thong")

# (id, ma_huong, ten_huong, loai_hinh, mo_ta_dac_diem, yeu_cau_ngoai_ngu, thoi_gian_chuan_bi_text, thang_min,
#  thang_max, chi_phi_du_kien_text, co_hoi_lam_them, lo_trinh_visa_dinh_cu)
HUONG_DI = [
    (
        1, "DU_HOC_NGHE", "Du học nghề", "du_hoc_nghe",
        "Học nghề kết hợp thực hành tại doanh nghiệp (Đức) hoặc trường chuyên môn (Nhật Bản); ra trường có tay nghề, "
        "dễ xin việc ở lại. Phù hợp học sinh muốn đi làm sớm, học lực trung bình khá trở lên.",
        "Tiếng Đức B1-B2 hoặc tiếng Nhật N4-N2 tùy nước",
        "8 - 18 tháng (chủ yếu học ngoại ngữ)", 8, 18,
        "150 - 350 triệu VNĐ trước khi bay (chưa gồm chứng minh tài chính)",
        "Đức: được trả lương học nghề hằng tháng. Nhật: làm thêm tối đa 28 giờ/tuần khi có giấy phép.",
        "Tốt nghiệp → visa lao động tay nghề → sau 3-5 năm làm việc có thể xin thường trú tùy nước.",
    ),
    (
        2, "DU_HOC_DAI_HOC", "Du học đại học (học thuật)", "du_hoc_hoc_thuat",
        "Học chương trình cử nhân tại đại học nước ngoài ngay sau THPT; yêu cầu học lực và ngoại ngữ tốt, "
        "chi phí cao, có cơ hội học bổng.",
        "IELTS 6.0-6.5 (Úc) hoặc TOPIK 3-4 (Hàn Quốc)",
        "6 - 12 tháng", 6, 12,
        "400 triệu - 1,5 tỷ VNĐ/năm tùy nước và trường",
        "Úc: làm thêm 48 giờ/2 tuần trong kỳ học. Hàn Quốc: làm thêm 20-25 giờ/tuần sau 6 tháng nhập học.",
        "Tốt nghiệp → visa sau đại học tìm việc 1-4 năm → visa tay nghề → thường trú.",
    ),
    (
        3, "CHUYEN_TIEP", "Du học chuyển tiếp", "chuyen_tiep",
        "Học dự bị đại học (Foundation) hoặc 1-2 năm đầu tại Việt Nam/nước thứ ba rồi chuyển tiếp lên năm 2-3 "
        "đại học nước ngoài; giảm chi phí và rủi ro so với đi thẳng.",
        "IELTS 5.5-6.0 cho chương trình dự bị/chuyển tiếp",
        "3 - 6 tháng", 3, 6,
        "250 - 800 triệu VNĐ/năm (giai đoạn học ở Việt Nam rẻ hơn nhiều)",
        "Theo quy định nước sở tại sau khi chuyển tiếp (thường 20 giờ/tuần).",
        "Bằng cử nhân nước ngoài → visa làm việc sau tốt nghiệp (Anh: Graduate Route 18 tháng - 2 năm).",
    ),
]

# (id, thpt_duhoc_huong_di_id, ma_quoc_gia, ten_quoc_gia, dac_diem_noi_bat, yeu_cau_ngoai_ngu_rieng,
#  co_hoi_viec_lam_visa, thu_tu_hien_thi)
QUOC_GIA = [
    (
        1, 1, "DE", "Đức",
        "Chương trình Ausbildung: 3 năm học nghề kép, miễn học phí, được doanh nghiệp trả lương hằng tháng.",
        "Tiếng Đức B1 (tối thiểu), ngành điều dưỡng thường yêu cầu B2",
        "Đức thiếu lao động ngành điều dưỡng, kỹ thuật, nhà hàng; tốt nghiệp được ở lại làm việc, "
        "có thể xin thường trú sau khoảng 2-4 năm.",
        1,
    ),
    (
        2, 1, "JP", "Nhật Bản",
        "Học 1-2 năm trường Nhật ngữ rồi lên trường chuyên môn (senmon) 2 năm; được làm thêm hợp pháp.",
        "JLPT N5-N4 khi nhập học trường tiếng, N2 để vào senmon",
        "Tốt nghiệp senmon xin visa kỹ sư/kỹ năng đặc định; nhu cầu lớn ngành điều dưỡng, nhà hàng, cơ khí.",
        2,
    ),
    (
        3, 2, "AU", "Úc",
        "Giáo dục chất lượng cao, môi trường đa văn hóa, chính sách visa sau tốt nghiệp rõ ràng.",
        "IELTS 6.0-6.5, không kỹ năng nào dưới 5.5-6.0",
        "Visa 485 sau tốt nghiệp 2-4 năm; các ngành thuộc danh sách tay nghề có lộ trình thường trú.",
        1,
    ),
    (
        4, 2, "KR", "Hàn Quốc",
        "Chi phí hợp lý, nhiều học bổng từ trường và chính phủ (GKS), văn hóa gần gũi.",
        "TOPIK 3 trở lên (hoặc học khóa tiếng D-4 trước)",
        "Visa D-10 tìm việc sau tốt nghiệp, chuyển sang E-7 khi có việc làm chuyên môn.",
        2,
    ),
    (
        5, 3, "GB", "Anh",
        "Chương trình dự bị 1 năm (Foundation) rồi lên cử nhân 3 năm; tổng thời gian ngắn hơn nhiều nước.",
        "IELTS UKVI 5.5 (Foundation), 6.0-6.5 (cử nhân)",
        "Graduate Route cho phép ở lại làm việc sau tốt nghiệp, sau đó chuyển visa Skilled Worker.",
        1,
    ),
    (
        6, 3, "SG", "Singapore",
        "Gần Việt Nam, chi phí thấp hơn Anh/Úc; nhiều chương trình liên kết chuyển tiếp sang Anh, Úc.",
        "IELTS 5.5-6.0",
        "Sau tốt nghiệp có thể xin Employment Pass hoặc S Pass nếu có việc đáp ứng mức lương tối thiểu.",
        2,
    ),
]

# (thpt_duhoc_huong_di_id, thpt_duhoc_quoc_gia_id, ten_nganh, nhu_cau_nhan_luc, muc_luong_tham_khao, ghi_chu)
NGANH = [
    (1, 1, "Điều dưỡng", "Rất cao", "Học nghề 1.100 - 1.300 EUR/tháng; sau tốt nghiệp 2.800 - 3.500 EUR/tháng",
     "Yêu cầu tiếng Đức B2 để được công nhận"),
    (1, 1, "Nhà hàng - khách sạn", "Cao", "Học nghề 900 - 1.100 EUR/tháng; sau tốt nghiệp 2.200 - 2.800 EUR/tháng",
     None),
    (1, 1, "Cơ điện tử", "Cao", "Học nghề 1.000 - 1.200 EUR/tháng; sau tốt nghiệp 3.000 - 3.800 EUR/tháng",
     "Cần nền tảng Toán, Lý"),
    (1, 2, "Điều dưỡng - chăm sóc người cao tuổi", "Rất cao", "200.000 - 250.000 JPY/tháng",
     "Có thể thi chứng chỉ Kaigo Fukushishi"),
    (1, 2, "Ô tô - cơ khí", "Cao", "220.000 - 280.000 JPY/tháng", None),
    (1, None, "Công nghệ thông tin ứng dụng", "Cao", "Tùy quốc gia", "Có ở cả Đức (Fachinformatiker) và Nhật"),
    (2, 3, "Công nghệ thông tin", "Cao", "70.000 - 90.000 AUD/năm", "Thuộc danh sách ngành tay nghề"),
    (2, 3, "Kế toán", "Trung bình", "60.000 - 75.000 AUD/năm", None),
    (2, 4, "Kỹ thuật bán dẫn", "Rất cao", "3.000.000 - 4.000.000 KRW/tháng", "Nhiều học bổng doanh nghiệp"),
    (2, 4, "Truyền thông - nội dung số", "Trung bình", "2.500.000 - 3.200.000 KRW/tháng", None),
    (3, 5, "Quản trị kinh doanh", "Trung bình", "25.000 - 32.000 GBP/năm", None),
    (3, 6, "Khoa học máy tính", "Cao", "4.000 - 5.500 SGD/tháng", None),
    (3, None, "Logistics và quản lý chuỗi cung ứng", "Cao", "Tùy quốc gia", "Nhiều chương trình 2+2 tại Việt Nam"),
]

# (thpt_duhoc_huong_di_id, thpt_duhoc_quoc_gia_id, loai_chi_phi, ten_khoan_chi, chi_phi_min, chi_phi_max,
#  don_vi_tien, chi_phi_quy_doi_vnd_text, ghi_chu)
CHI_PHI = [
    (1, 1, "truoc_khi_bay", "Học tiếng Đức A1 - B1", 40_000_000, 80_000_000, "VND", "40 - 80 triệu VNĐ", None),
    (1, 1, "truoc_khi_bay", "Thi chứng chỉ, dịch thuật, visa", 15_000_000, 25_000_000, "VND",
     "15 - 25 triệu VNĐ", None),
    (1, 1, "chung_minh_tai_chinh", "Tài khoản phong tỏa (nếu lương học nghề chưa đủ)", 0, 11_904, "EUR",
     "0 - 330 triệu VNĐ", "Miễn nếu lương học nghề đạt mức tối thiểu"),
    (1, 1, "tai_nuoc_so_tai", "Sinh hoạt phí", 800, 1_000, "EUR", "22 - 28 triệu VNĐ/tháng", "Theo tháng"),
    (1, 1, "khoan_bu_dap", "Lương học nghề", 1_000, 1_300, "EUR", "28 - 36 triệu VNĐ/tháng", "Theo tháng"),
    (1, 2, "truoc_khi_bay", "Học phí trường Nhật ngữ năm đầu", 700_000, 900_000, "JPY", "120 - 155 triệu VNĐ",
     None),
    (1, 2, "chung_minh_tai_chinh", "Sổ tiết kiệm người bảo lãnh", 500_000_000, 700_000_000, "VND",
     "500 - 700 triệu VNĐ", "Gửi trước tối thiểu 3-6 tháng"),
    (1, 2, "khoan_bu_dap", "Thu nhập làm thêm", 100_000, 140_000, "JPY", "17 - 24 triệu VNĐ/tháng",
     "Tối đa 28 giờ/tuần"),
    (2, 3, "tai_nuoc_so_tai", "Học phí cử nhân", 30_000, 45_000, "AUD", "500 - 750 triệu VNĐ/năm", "Theo năm"),
    (2, 3, "chung_minh_tai_chinh", "Chi phí sinh hoạt cần chứng minh", 29_710, 29_710, "AUD",
     "khoảng 500 triệu VNĐ/năm", "Mức tối thiểu theo quy định visa 500"),
    (2, 4, "tai_nuoc_so_tai", "Học phí cử nhân", 5_000_000, 9_000_000, "KRW", "90 - 160 triệu VNĐ/năm",
     "Theo năm"),
    (2, 4, "chung_minh_tai_chinh", "Sổ tiết kiệm", 20_000, 20_000, "USD", "khoảng 510 triệu VNĐ", None),
    (2, None, "truoc_khi_bay", "Luyện thi IELTS/TOPIK", 15_000_000, 40_000_000, "VND", "15 - 40 triệu VNĐ", None),
    (3, 5, "tai_nuoc_so_tai", "Học phí Foundation", 18_000, 25_000, "GBP", "600 - 830 triệu VNĐ", None),
    (3, 5, "chung_minh_tai_chinh", "Sinh hoạt phí 9 tháng (ngoài London)", 10_224, 10_224, "GBP",
     "khoảng 340 triệu VNĐ", None),
    (3, 6, "tai_nuoc_so_tai", "Học phí dự bị/năm đầu", 15_000, 25_000, "SGD", "290 - 480 triệu VNĐ", None),
    (3, None, "truoc_khi_bay", "Học phí 2 năm đầu tại Việt Nam (chương trình 2+2)", 150_000_000, 300_000_000,
     "VND", "150 - 300 triệu VNĐ/năm", None),
]

# (thpt_duhoc_huong_di_id, thpt_duhoc_quoc_gia_id, buoc_so, ten_buoc, mo_ta_thu_tuc, giay_to_can_co,
#  thoi_gian_du_kien)
THU_TUC = [
    (1, 1, 1, "Học tiếng Đức", "Học từ A1 đến B1/B2 và thi chứng chỉ Goethe hoặc telc.",
     "CCCD, bằng/học bạ THPT", "6 - 12 tháng"),
    (1, 1, 2, "Tìm doanh nghiệp nhận học nghề", "Gửi hồ sơ, phỏng vấn online với doanh nghiệp Đức để ký hợp đồng.",
     "CV tiếng Đức, thư động lực, chứng chỉ tiếng", "1 - 3 tháng"),
    (1, 1, 3, "Công nhận bằng cấp và nộp visa", "Xin xác nhận của cơ quan lao động Đức, đặt lịch nộp visa học nghề.",
     "Hợp đồng học nghề, hộ chiếu, bảo hiểm, chứng minh tài chính", "2 - 4 tháng"),
    (1, 1, 4, "Nhập cảnh và đăng ký cư trú", "Đăng ký địa chỉ, mở tài khoản, nhận thẻ cư trú tại Đức.",
     "Visa, hợp đồng thuê nhà", "1 tháng"),
    (1, 2, 1, "Học tiếng Nhật", "Học đạt trình độ N5-N4 và thi JLPT/NAT-TEST.", "CCCD, học bạ THPT", "6 - 8 tháng"),
    (1, 2, 2, "Nộp hồ sơ trường Nhật ngữ", "Trường nộp hồ sơ xin Tư cách lưu trú (COE) lên Cục Xuất nhập cảnh Nhật.",
     "Bằng THPT, chứng chỉ tiếng, giấy tờ người bảo lãnh tài chính", "3 - 4 tháng"),
    (1, 2, 3, "Xin visa du học", "Nhận COE, đóng học phí và nộp visa tại Đại sứ quán/Tổng lãnh sự quán Nhật.",
     "COE, hộ chiếu, biên lai học phí", "1 tháng"),
    (2, None, 1, "Chọn trường và ngành", "Đối chiếu học lực, ngân sách, chứng chỉ ngoại ngữ để chọn 3-5 trường.",
     None, "1 - 2 tháng"),
    (2, None, 2, "Thi chứng chỉ ngoại ngữ", "Luyện và thi IELTS/TOEFL hoặc TOPIK đạt yêu cầu.",
     "CCCD/hộ chiếu", "3 - 6 tháng"),
    (2, 3, 3, "Nhận thư mời và CoE", "Chấp nhận offer, đóng học phí kỳ đầu và mua bảo hiểm OSHC để nhận CoE.",
     "Học bạ, bằng THPT, IELTS, hộ chiếu", "1 - 2 tháng"),
    (2, 3, 4, "Nộp visa 500", "Nộp visa online kèm GTE/Genuine Student, chứng minh tài chính, khám sức khỏe.",
     "CoE, chứng minh tài chính, giấy khám sức khỏe", "1 - 2 tháng"),
    (2, 4, 3, "Nộp visa D-2", "Nhận giấy nhập học và nộp visa tại Đại sứ quán Hàn Quốc.",
     "Giấy nhập học, sổ tiết kiệm, bằng THPT hợp pháp hóa", "3 - 6 tuần"),
    (3, None, 1, "Chọn chương trình chuyển tiếp", "So sánh chương trình Foundation và 2+2/3+1, kiểm tra trường đối tác.",
     None, "1 tháng"),
    (3, 5, 2, "Nộp hồ sơ qua UCAS hoặc trường", "Nộp hồ sơ Foundation, nhận thư mời và CAS.",
     "Học bạ, IELTS UKVI, hộ chiếu", "1 - 2 tháng"),
    (3, 5, 3, "Xin visa Student", "Nộp visa online, chứng minh tài chính 28 ngày, lấy sinh trắc học.",
     "CAS, sao kê ngân hàng, hộ chiếu, xét nghiệm lao", "3 - 4 tuần"),
]

# (thpt_duhoc_huong_di_id, thpt_duhoc_quoc_gia_id, loai_kenh, ten_kenh, thong_tin_lien_he, mo_ta_ho_tro,
#  luu_y_khi_ket_noi, thu_tu_hien_thi)
KENH_KET_NOI = [
    (1, 1, "chinh_thong", "Đại sứ quán Đức tại Hà Nội", "vietnam.diplo.de",
     "Thông tin visa học nghề, đặt lịch nộp hồ sơ.", "Chỉ đặt lịch qua kênh chính thức, không mất phí", 1),
    (1, 1, "chinh_thong", "Viện Goethe Hà Nội", "goethe.de/vietnam",
     "Học và thi chứng chỉ tiếng Đức.", None, 2),
    (1, 2, "chinh_thong", "Study in Japan (JASSO)", "studyinjapan.go.jp",
     "Thông tin trường, học bổng, thủ tục du học Nhật.", None, 1),
    (1, None, "chinh_thong", "Cục Quản lý lao động ngoài nước", "dolab.gov.vn",
     "Tra cứu doanh nghiệp được cấp phép đưa người đi làm việc ở nước ngoài.",
     "Kiểm tra giấy phép trước khi đóng tiền", 3),
    (1, None, "cong_dong", "Nhóm cộng đồng du học nghề Đức, Nhật", "Facebook, Zalo",
     "Chia sẻ kinh nghiệm học tiếng, phỏng vấn, cuộc sống thực tế.",
     "Thông tin chỉ tham khảo, cảnh giác lời mời đóng tiền", 4),
    (2, 3, "chinh_thong", "Study Australia", "studyaustralia.gov.au",
     "Cổng thông tin chính thức của Chính phủ Úc về du học.", None, 1),
    (2, 4, "chinh_thong", "Study in Korea (NIIED)", "studyinkorea.go.kr",
     "Danh sách trường, học bổng GKS.", None, 2),
    (2, None, "trung_tam_tu_van", "Trung tâm tư vấn du học được cấp phép", "Tra cứu trên website Sở GD&ĐT",
     "Tư vấn chọn trường, hồ sơ, visa.", "Chỉ chọn đơn vị có giấy chứng nhận đăng ký kinh doanh dịch vụ tư vấn du học", 3),
    (3, 5, "chinh_thong", "British Council Việt Nam", "britishcouncil.vn",
     "Thi IELTS, thông tin du học Anh.", None, 1),
    (3, None, "ho_tro_he_thong", "Tư vấn viên hệ thống định hướng nghề", "Mục Hỗ trợ trên hệ thống",
     "Hỗ trợ so sánh lộ trình chuyển tiếp phù hợp với kết quả trắc nghiệm.", None, 2),
]


def _dong(cot, du_lieu):
    return [dict(zip(cot, dong, strict=True)) for dong in du_lieu]


def _cot_huong_di(ten_fk: str):
    return sa.Column(
        "thpt_duhoc_huong_di_id",
        sa.Integer(),
        sa.ForeignKey("dm_thpt_duhoc_huong_di.id", name=ten_fk, ondelete="CASCADE"),
        nullable=False,
    )


def _cot_quoc_gia(ten_fk: str):
    return sa.Column(
        "thpt_duhoc_quoc_gia_id",
        sa.Integer(),
        sa.ForeignKey("dm_thpt_duhoc_quoc_gia.id", name=ten_fk, ondelete="CASCADE"),
        nullable=True,
    )


def _index_fk(bang: str, co_quoc_gia: bool = True) -> None:
    op.create_index(f"ix_{bang}_thpt_duhoc_huong_di_id", bang, ["thpt_duhoc_huong_di_id"])
    if co_quoc_gia:
        op.create_index(f"ix_{bang}_thpt_duhoc_quoc_gia_id", bang, ["thpt_duhoc_quoc_gia_id"])


def upgrade() -> None:
    huong_di = op.create_table(
        "dm_thpt_duhoc_huong_di",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("ma_huong", sa.String(50), nullable=False),
        sa.Column("ten_huong", sa.String(255), nullable=False),
        sa.Column("loai_hinh", sa.Enum(*LOAI_HINH_DU_HOC, name="loai_hinh_du_hoc"), nullable=False),
        sa.Column("mo_ta_dac_diem", sa.Text(), nullable=False),
        sa.Column("yeu_cau_ngoai_ngu", sa.String(255), nullable=True),
        sa.Column("thoi_gian_chuan_bi_text", sa.String(100), nullable=True),
        sa.Column("thoi_gian_chuan_bi_thang_min", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("thoi_gian_chuan_bi_thang_max", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("chi_phi_du_kien_text", sa.String(255), nullable=True),
        sa.Column("co_hoi_lam_them", sa.Text(), nullable=True),
        sa.Column("lo_trinh_visa_dinh_cu", sa.Text(), nullable=True),
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
    op.create_index("ix_dm_thpt_duhoc_huong_di_ma_huong", "dm_thpt_duhoc_huong_di", ["ma_huong"], unique=True)

    quoc_gia = op.create_table(
        "dm_thpt_duhoc_quoc_gia",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        _cot_huong_di("fk_dm_tdqg_huong_di_id"),
        sa.Column("ma_quoc_gia", sa.String(20), nullable=False),
        sa.Column("ten_quoc_gia", sa.String(100), nullable=False),
        sa.Column("dac_diem_noi_bat", sa.Text(), nullable=True),
        sa.Column("yeu_cau_ngoai_ngu_rieng", sa.String(255), nullable=True),
        sa.Column("co_hoi_viec_lam_visa", sa.Text(), nullable=True),
        sa.Column("thu_tu_hien_thi", sa.Integer(), nullable=False, server_default="0"),
        **_BANG,
    )
    _index_fk("dm_thpt_duhoc_quoc_gia", co_quoc_gia=False)

    nganh = op.create_table(
        "dm_thpt_duhoc_nganh",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        _cot_huong_di("fk_dm_tdn_huong_di_id"),
        _cot_quoc_gia("fk_dm_tdn_quoc_gia_id"),
        sa.Column("ten_nganh", sa.String(255), nullable=False),
        sa.Column("nhu_cau_nhan_luc", sa.String(255), nullable=True),
        sa.Column("muc_luong_tham_khao", sa.String(255), nullable=True),
        sa.Column("ghi_chu", sa.Text(), nullable=True),
        **_BANG,
    )
    _index_fk("dm_thpt_duhoc_nganh")

    chi_phi = op.create_table(
        "dm_thpt_duhoc_chi_phi",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        _cot_huong_di("fk_dm_tdcp_huong_di_id"),
        _cot_quoc_gia("fk_dm_tdcp_quoc_gia_id"),
        sa.Column("loai_chi_phi", sa.Enum(*LOAI_CHI_PHI, name="loai_chi_phi"), nullable=False),
        sa.Column("ten_khoan_chi", sa.String(255), nullable=False),
        sa.Column("chi_phi_min", sa.Numeric(12, 2), nullable=True),
        sa.Column("chi_phi_max", sa.Numeric(12, 2), nullable=True),
        sa.Column("don_vi_tien", sa.String(20), nullable=False, server_default="VND"),
        sa.Column("chi_phi_quy_doi_vnd_text", sa.String(255), nullable=True),
        sa.Column("ghi_chu", sa.String(255), nullable=True),
        **_BANG,
    )
    _index_fk("dm_thpt_duhoc_chi_phi")

    thu_tuc = op.create_table(
        "dm_thpt_duhoc_thu_tuc",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        _cot_huong_di("fk_dm_tdtt_huong_di_id"),
        _cot_quoc_gia("fk_dm_tdtt_quoc_gia_id"),
        sa.Column("buoc_so", TINYINT(), nullable=False),
        sa.Column("ten_buoc", sa.String(255), nullable=False),
        sa.Column("mo_ta_thu_tuc", sa.Text(), nullable=False),
        sa.Column("giay_to_can_co", sa.Text(), nullable=True),
        sa.Column("thoi_gian_du_kien", sa.String(100), nullable=True),
        **_BANG,
    )
    _index_fk("dm_thpt_duhoc_thu_tuc")

    kenh = op.create_table(
        "dm_thpt_duhoc_kenh_ket_noi",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        _cot_huong_di("fk_dm_tdkkn_huong_di_id"),
        _cot_quoc_gia("fk_dm_tdkkn_quoc_gia_id"),
        sa.Column("loai_kenh", sa.Enum(*LOAI_KENH, name="loai_kenh"), nullable=False),
        sa.Column("ten_kenh", sa.String(255), nullable=False),
        sa.Column("thong_tin_lien_he", sa.String(255), nullable=True),
        sa.Column("mo_ta_ho_tro", sa.Text(), nullable=True),
        sa.Column("luu_y_khi_ket_noi", sa.String(255), nullable=True),
        sa.Column("thu_tu_hien_thi", sa.Integer(), nullable=False, server_default="0"),
        **_BANG,
    )
    _index_fk("dm_thpt_duhoc_kenh_ket_noi")

    # Dữ liệu mẫu — bảng mới nên gán id tường minh cho bảng cha để liên kết.
    op.bulk_insert(
        huong_di,
        _dong(
            (
                "id", "ma_huong", "ten_huong", "loai_hinh", "mo_ta_dac_diem", "yeu_cau_ngoai_ngu",
                "thoi_gian_chuan_bi_text", "thoi_gian_chuan_bi_thang_min", "thoi_gian_chuan_bi_thang_max",
                "chi_phi_du_kien_text", "co_hoi_lam_them", "lo_trinh_visa_dinh_cu",
            ),
            HUONG_DI,
        ),
    )
    op.bulk_insert(
        quoc_gia,
        _dong(
            (
                "id", "thpt_duhoc_huong_di_id", "ma_quoc_gia", "ten_quoc_gia", "dac_diem_noi_bat",
                "yeu_cau_ngoai_ngu_rieng", "co_hoi_viec_lam_visa", "thu_tu_hien_thi",
            ),
            QUOC_GIA,
        ),
    )
    op.bulk_insert(
        nganh,
        _dong(
            (
                "thpt_duhoc_huong_di_id", "thpt_duhoc_quoc_gia_id", "ten_nganh", "nhu_cau_nhan_luc",
                "muc_luong_tham_khao", "ghi_chu",
            ),
            NGANH,
        ),
    )
    op.bulk_insert(
        chi_phi,
        _dong(
            (
                "thpt_duhoc_huong_di_id", "thpt_duhoc_quoc_gia_id", "loai_chi_phi", "ten_khoan_chi", "chi_phi_min",
                "chi_phi_max", "don_vi_tien", "chi_phi_quy_doi_vnd_text", "ghi_chu",
            ),
            CHI_PHI,
        ),
    )
    op.bulk_insert(
        thu_tuc,
        _dong(
            (
                "thpt_duhoc_huong_di_id", "thpt_duhoc_quoc_gia_id", "buoc_so", "ten_buoc", "mo_ta_thu_tuc",
                "giay_to_can_co", "thoi_gian_du_kien",
            ),
            THU_TUC,
        ),
    )
    op.bulk_insert(
        kenh,
        _dong(
            (
                "thpt_duhoc_huong_di_id", "thpt_duhoc_quoc_gia_id", "loai_kenh", "ten_kenh", "thong_tin_lien_he",
                "mo_ta_ho_tro", "luu_y_khi_ket_noi", "thu_tu_hien_thi",
            ),
            KENH_KET_NOI,
        ),
    )


def downgrade() -> None:
    op.drop_table("dm_thpt_duhoc_kenh_ket_noi")
    op.drop_table("dm_thpt_duhoc_thu_tuc")
    op.drop_table("dm_thpt_duhoc_chi_phi")
    op.drop_table("dm_thpt_duhoc_nganh")
    op.drop_table("dm_thpt_duhoc_quoc_gia")
    op.drop_table("dm_thpt_duhoc_huong_di")
