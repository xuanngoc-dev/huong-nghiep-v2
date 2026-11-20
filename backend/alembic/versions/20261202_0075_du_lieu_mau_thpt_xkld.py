"""Dữ liệu mẫu danh mục xuất khẩu lao động sau THPT: nhóm nghề, thị trường, nghề cụ thể, chi phí, thủ tục, kênh kết nối.

Liên kết tra theo mã (ma_nhom, ma_quoc_gia), không gán id cứng; nhóm nghề đã có mã trong bảng thì bỏ qua cả nhóm.
Thu nhập nhóm nghề tính theo triệu VNĐ/tháng. Số liệu chi phí, thu nhập là tham khảo.

Revision ID: 20261202_0075
Revises: 20261201_0074
Create Date: 2026-12-02 10:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "20261202_0075"
down_revision = "20261201_0074"
branch_labels = None
depends_on = None

# (ma_nhom, ten_nhom, mo_ta_cong_viec, dieu_kien_suc_khoe_the_luc, yeu_cau_ngoai_ngu, thoi_gian_chuan_bi_text,
#  thang_min, thang_max, muc_thu_nhap_text, thu_nhap_min, thu_nhap_max, trien_vong_sau_ve_nuoc, kha_nang_gia_han_visa)
NHOM_NGHE = [
    (
        "CO_KHI", "Cơ khí - Hàn - Xây dựng",
        "Làm việc tại nhà máy, công trường: hàn, tiện, phay, lắp ráp kết cấu thép, cốp pha, cốt thép. "
        "Công việc nặng, làm theo ca, thường có tăng ca.",
        "Nam 18 - 35 tuổi, cao từ 1m60, nặng từ 50kg; không mắc bệnh truyền nhiễm (lao, viêm gan B thể hoạt động, "
        "HIV); thị lực tốt, không mù màu; chịu được nóng, ồn, đứng lâu.",
        "Tiếng Nhật N5-N4 hoặc tiếng Hàn đạt bài thi EPS-TOPIK",
        "4 - 8 tháng (học tiếng, thi tay nghề, làm hồ sơ)", 4, 8,
        "28 - 40 triệu VNĐ/tháng (chưa tính tăng ca)", 28, 40,
        "Về nước làm tổ trưởng, kỹ thuật viên tại doanh nghiệp FDI Nhật, Hàn; mở xưởng cơ khí; làm phiên dịch, "
        "giáo viên tiếng cho lao động đi sau.",
        "Nhật: chuyển sang kỹ năng đặc định; Hàn: gia hạn thêm nếu chủ sử dụng đồng ý",
    ),
    (
        "CHE_BIEN_THUC_PHAM", "Chế biến thực phẩm",
        "Sơ chế, chế biến, đóng gói thực phẩm (cơm hộp, bánh, thủy sản, thịt) trong nhà máy; làm trong môi trường "
        "lạnh, đứng theo dây chuyền.",
        "Nam, nữ 18 - 35 tuổi; không mắc bệnh truyền nhiễm, bệnh ngoài da; chịu được lạnh và đứng lâu.",
        "Tiếng Nhật N5 trở lên hoặc tiếng Trung giao tiếp cơ bản (Đài Loan)",
        "3 - 6 tháng", 3, 6,
        "22 - 32 triệu VNĐ/tháng", 22, 32,
        "Làm quản lý chất lượng, tổ trưởng tại nhà máy chế biến xuất khẩu; kinh doanh thực phẩm theo tiêu chuẩn "
        "vệ sinh đã học được.",
        "Nhật: chuyển kỹ năng đặc định ngành thực phẩm; Đài Loan: gia hạn hợp đồng theo quy định",
    ),
    (
        "NONG_NGHIEP", "Nông nghiệp",
        "Trồng trọt (rau, nấm, cây ăn quả trong nhà kính), chăn nuôi bò sữa, lợn, gà tại trang trại; làm ngoài trời, "
        "theo mùa vụ.",
        "Nam, nữ 18 - 40 tuổi; sức khỏe tốt, không dị ứng phấn hoa, lông động vật; chịu được nắng, lạnh.",
        "Tiếng Nhật N5 hoặc tiếng Hàn đạt bài thi EPS-TOPIK",
        "4 - 8 tháng", 4, 8,
        "25 - 35 triệu VNĐ/tháng (thường được hỗ trợ chỗ ở)", 25, 35,
        "Áp dụng kỹ thuật canh tác công nghệ cao, mô hình trang trại khi về quê; làm kỹ thuật viên cho doanh nghiệp "
        "nông nghiệp.",
        "Nhật: chuyển kỹ năng đặc định ngành nông nghiệp; Hàn: gia hạn theo chương trình EPS",
    ),
    (
        "DIEU_DUONG_HO_LY", "Điều dưỡng - Hộ lý",
        "Chăm sóc người cao tuổi, người bệnh tại viện dưỡng lão, bệnh viện: hỗ trợ ăn uống, vệ sinh, di chuyển, "
        "theo dõi sức khỏe; làm theo ca, kể cả ca đêm.",
        "Nam, nữ 18 - 35 tuổi; cột sống khỏe để nâng đỡ người bệnh; kiên nhẫn, chịu được áp lực tâm lý.",
        "Tiếng Nhật N4 trở lên hoặc tiếng Đức B1-B2",
        "8 - 14 tháng", 8, 14,
        "30 - 45 triệu VNĐ/tháng", 30, 45,
        "Làm tại bệnh viện, viện dưỡng lão, dịch vụ chăm sóc tại nhà trong nước - lĩnh vực đang thiếu nhân lực "
        "có kỹ năng; có thể học tiếp ngành điều dưỡng.",
        "Nhật: đỗ chứng chỉ Kaigo Fukushishi được lưu trú dài hạn; Đức: ở lại làm việc khi được công nhận bằng",
    ),
]

# (ma_nhom, ma_quoc_gia, ten_quoc_gia, loai_visa, dac_diem_thi_truong, thu_nhap_rieng_text, thoi_han_hop_dong_nam,
#  thu_tu_hien_thi)
THI_TRUONG = [
    ("CO_KHI", "JP", "Nhật Bản", "Thực tập sinh kỹ năng",
     "Nhiều đơn hàng nhất; môi trường kỷ luật, an toàn lao động nghiêm ngặt; lương theo mức tối thiểu vùng.",
     "180.000 - 230.000 JPY/tháng", 3, 1),
    ("CO_KHI", "KR", "Hàn Quốc", "E-9 (chương trình EPS)",
     "Tuyển qua chương trình EPS do Nhà nước tổ chức, chi phí thấp; phải thi tiếng Hàn EPS-TOPIK và tay nghề.",
     "2.100.000 - 2.600.000 KRW/tháng", 3, 2),
    ("CO_KHI", "TW", "Đài Loan", "Lao động phổ thông",
     "Thủ tục nhanh, yêu cầu ngoại ngữ thấp; lương cơ bản theo quy định Đài Loan, nhiều tăng ca.",
     "28.000 - 33.000 TWD/tháng", 3, 3),
    ("CHE_BIEN_THUC_PHAM", "JP", "Nhật Bản", "Thực tập sinh kỹ năng",
     "Đơn hàng ổn định quanh năm, nhiều đơn tuyển nữ; làm trong nhà xưởng sạch, nhiệt độ thấp.",
     "170.000 - 210.000 JPY/tháng", 3, 1),
    ("CHE_BIEN_THUC_PHAM", "TW", "Đài Loan", "Lao động phổ thông",
     "Nhà máy thực phẩm, thủy sản; chi phí đi thấp hơn Nhật Bản.",
     "28.000 - 32.000 TWD/tháng", 3, 2),
    ("NONG_NGHIEP", "JP", "Nhật Bản", "Thực tập sinh kỹ năng",
     "Trang trại ở vùng nông thôn, thường được hỗ trợ nhà ở; công việc theo mùa vụ.",
     "170.000 - 200.000 JPY/tháng", 3, 1),
    ("NONG_NGHIEP", "KR", "Hàn Quốc", "E-9 (chương trình EPS)",
     "Ngành nông nghiệp, chăn nuôi trong chương trình EPS; thời gian làm việc dài vào mùa vụ.",
     "2.000.000 - 2.400.000 KRW/tháng", 3, 2),
    ("DIEU_DUONG_HO_LY", "JP", "Nhật Bản", "Kỹ năng đặc định (điều dưỡng - Kaigo)",
     "Nhu cầu rất lớn do dân số già; cần thi kỹ năng Kaigo và tiếng Nhật chuyên ngành điều dưỡng.",
     "200.000 - 250.000 JPY/tháng", 5, 1),
    ("DIEU_DUONG_HO_LY", "DE", "Đức", "Lao động điều dưỡng",
     "Thiếu điều dưỡng trầm trọng; cần tiếng Đức B1-B2 và được công nhận văn bằng.",
     "2.300 - 3.000 EUR/tháng", 3, 2),
]

# (ma_nhom, ma_quoc_gia | None, ten_cong_viec, mo_ta_ngan, yeu_cau_gioi_tinh)
NGHE_CU_THE = [
    ("CO_KHI", "JP", "Hàn bán tự động", "Hàn kết cấu thép, khung xe, chi tiết máy bằng máy hàn CO2/MIG.", "nam"),
    ("CO_KHI", "JP", "Tiện - phay CNC", "Vận hành, căn chỉnh máy tiện, phay CNC theo bản vẽ kỹ thuật.", "nam"),
    ("CO_KHI", "KR", "Công nhân sản xuất chế tạo",
     "Làm tại doanh nghiệp vừa và nhỏ ngành kim loại, nhựa, linh kiện ô tô.", "ca_hai"),
    ("CO_KHI", "TW", "Lắp ráp linh kiện cơ khí", "Lắp ráp, kiểm tra chi tiết cơ khí trên dây chuyền.", "ca_hai"),
    ("CO_KHI", None, "Cốp pha - cốt thép xây dựng", "Gia công, lắp dựng cốp pha, cốt thép tại công trường.", "nam"),
    ("CHE_BIEN_THUC_PHAM", "JP", "Chế biến cơm hộp",
     "Nấu, chia suất, đóng hộp cơm và món ăn sẵn cho cửa hàng tiện lợi.", "nu"),
    ("CHE_BIEN_THUC_PHAM", "JP", "Chế biến thủy sản", "Sơ chế, phi lê, cấp đông cá và hải sản.", "ca_hai"),
    ("CHE_BIEN_THUC_PHAM", "TW", "Đóng gói thực phẩm",
     "Vận hành máy đóng gói, kiểm tra nhãn mác trên dây chuyền.", "ca_hai"),
    ("CHE_BIEN_THUC_PHAM", None, "Làm bánh công nghiệp", "Nhào bột, tạo hình, nướng và đóng gói bánh.", "ca_hai"),
    ("NONG_NGHIEP", "JP", "Trồng rau nhà kính",
     "Gieo trồng, chăm sóc, thu hoạch rau, cà chua trong nhà kính.", "ca_hai"),
    ("NONG_NGHIEP", "JP", "Chăn nuôi bò sữa", "Cho ăn, vắt sữa, vệ sinh chuồng trại.", "nam"),
    ("NONG_NGHIEP", "KR", "Trồng nấm, cây ăn quả", "Chăm sóc, thu hái nấm và cây ăn quả.", "ca_hai"),
    ("DIEU_DUONG_HO_LY", "JP", "Hộ lý viện dưỡng lão",
     "Chăm sóc sinh hoạt hằng ngày cho người cao tuổi: ăn uống, tắm rửa, di chuyển.", "ca_hai"),
    ("DIEU_DUONG_HO_LY", "DE", "Trợ lý điều dưỡng",
     "Hỗ trợ điều dưỡng chăm sóc bệnh nhân tại bệnh viện, viện dưỡng lão.", "ca_hai"),
]

_TIEN_DICH_VU_NHAT = "Không vượt mức trần theo quy định (tối đa 3 tháng lương/hợp đồng 3 năm)"
_TIEN_DICH_VU_DAI_LOAN = "Không vượt mức trần theo quy định (tối đa 1 tháng lương/năm làm việc)"
_EPS = "Nộp cho Trung tâm Lao động ngoài nước, đã gồm vé máy bay"
_KY_QUY_EPS = "Hoàn trả cả gốc và lãi khi về nước đúng hạn hợp đồng"

# (ma_nhom, ma_quoc_gia | None, loai_chi_phi, ten_khoan_chi, chi_phi_min, chi_phi_max, don_vi_tien,
#  chi_phi_quy_doi_vnd_text, ghi_chu)
CHI_PHI = [
    ("CO_KHI", "JP", "phi_dich_vu_xuat_canh", "Tiền dịch vụ trả doanh nghiệp", 0, 3_600, "USD",
     "0 - 92 triệu VNĐ", _TIEN_DICH_VU_NHAT),
    ("CO_KHI", "JP", "dao_tao_tieng_tay_nghe", "Học tiếng Nhật và giáo dục định hướng", 10_000_000, 20_000_000,
     "VND", "10 - 20 triệu VNĐ", None),
    ("CO_KHI", "KR", "phi_dich_vu_xuat_canh", "Chi phí đi làm việc theo chương trình EPS", 600, 700, "USD",
     "15 - 18 triệu VNĐ", _EPS),
    ("CO_KHI", "KR", "ky_quy_chong_tron", "Ký quỹ tại ngân hàng", 100_000_000, 100_000_000, "VND",
     "100 triệu VNĐ", _KY_QUY_EPS),
    ("CO_KHI", "TW", "phi_dich_vu_xuat_canh", "Tiền dịch vụ trả doanh nghiệp", 0, 3_000, "USD",
     "0 - 77 triệu VNĐ", _TIEN_DICH_VU_DAI_LOAN),
    ("CO_KHI", None, "dao_tao_tieng_tay_nghe", "Học và thi tay nghề hàn, cơ khí", 3_000_000, 8_000_000, "VND",
     "3 - 8 triệu VNĐ", None),
    ("CO_KHI", None, "kham_suc_khoe_ho_so", "Khám sức khỏe, hộ chiếu, lý lịch tư pháp", 2_000_000, 4_000_000,
     "VND", "2 - 4 triệu VNĐ", None),
    ("CHE_BIEN_THUC_PHAM", "JP", "phi_dich_vu_xuat_canh", "Tiền dịch vụ trả doanh nghiệp", 0, 3_600, "USD",
     "0 - 92 triệu VNĐ", _TIEN_DICH_VU_NHAT),
    ("CHE_BIEN_THUC_PHAM", "JP", "dao_tao_tieng_tay_nghe", "Học tiếng Nhật và giáo dục định hướng", 10_000_000,
     18_000_000, "VND", "10 - 18 triệu VNĐ", None),
    ("CHE_BIEN_THUC_PHAM", "TW", "phi_dich_vu_xuat_canh", "Tiền dịch vụ trả doanh nghiệp", 0, 3_000, "USD",
     "0 - 77 triệu VNĐ", _TIEN_DICH_VU_DAI_LOAN),
    ("CHE_BIEN_THUC_PHAM", None, "kham_suc_khoe_ho_so", "Khám sức khỏe, hộ chiếu, lý lịch tư pháp", 2_000_000,
     4_000_000, "VND", "2 - 4 triệu VNĐ", None),
    ("NONG_NGHIEP", "JP", "phi_dich_vu_xuat_canh", "Tiền dịch vụ trả doanh nghiệp", 0, 3_600, "USD",
     "0 - 92 triệu VNĐ", _TIEN_DICH_VU_NHAT),
    ("NONG_NGHIEP", "KR", "phi_dich_vu_xuat_canh", "Chi phí đi làm việc theo chương trình EPS", 600, 700, "USD",
     "15 - 18 triệu VNĐ", _EPS),
    ("NONG_NGHIEP", "KR", "ky_quy_chong_tron", "Ký quỹ tại ngân hàng", 100_000_000, 100_000_000, "VND",
     "100 triệu VNĐ", _KY_QUY_EPS),
    ("NONG_NGHIEP", None, "kham_suc_khoe_ho_so", "Khám sức khỏe, hộ chiếu, lý lịch tư pháp", 2_000_000, 4_000_000,
     "VND", "2 - 4 triệu VNĐ", None),
    ("DIEU_DUONG_HO_LY", "JP", "phi_dich_vu_xuat_canh", "Tiền dịch vụ trả doanh nghiệp", 0, 3_600, "USD",
     "0 - 92 triệu VNĐ", "Theo hợp đồng dịch vụ, không vượt mức trần theo quy định"),
    ("DIEU_DUONG_HO_LY", "JP", "dao_tao_tieng_tay_nghe", "Học tiếng Nhật N4 và luyện thi kỹ năng Kaigo",
     25_000_000, 45_000_000, "VND", "25 - 45 triệu VNĐ", None),
    ("DIEU_DUONG_HO_LY", "DE", "dao_tao_tieng_tay_nghe", "Học tiếng Đức A1 - B2", 40_000_000, 80_000_000, "VND",
     "40 - 80 triệu VNĐ", None),
    ("DIEU_DUONG_HO_LY", "DE", "kham_suc_khoe_ho_so", "Dịch thuật, công chứng, công nhận văn bằng", 15_000_000,
     25_000_000, "VND", "15 - 25 triệu VNĐ", None),
]

_CHON_DOANH_NGHIEP = (
    1, "Chọn doanh nghiệp được cấp phép",
    "Tra cứu giấy phép doanh nghiệp trên trang Cục Quản lý lao động ngoài nước; ký hợp đồng dịch vụ ghi rõ "
    "các khoản phí.",
    "CCCD, bằng tốt nghiệp THPT", "1 - 2 tuần",
)

# (ma_nhom, ma_quoc_gia | None, buoc_so, ten_buoc, mo_ta_thu_tuc, giay_to_can_co, thoi_gian_du_kien)
THU_TUC = [
    ("CO_KHI", "JP", *_CHON_DOANH_NGHIEP),
    ("CO_KHI", "JP", 2, "Khám sức khỏe, thi tuyển",
     "Khám tại cơ sở y tế đủ điều kiện; thi tay nghề, thể lực và phỏng vấn với xí nghiệp Nhật.",
     "Giấy khám sức khỏe, sơ yếu lý lịch", "1 - 2 tháng"),
    ("CO_KHI", "JP", 3, "Đào tạo tiếng và định hướng",
     "Học tiếng Nhật, văn hóa, pháp luật, kỹ năng làm việc; được cấp chứng chỉ bồi dưỡng kiến thức cần thiết.",
     None, "4 - 6 tháng"),
    ("CO_KHI", "JP", 4, "Xin tư cách lưu trú (COE) và visa",
     "Nghiệp đoàn nộp hồ sơ xin COE; có COE thì xin visa tại Đại sứ quán Nhật Bản.",
     "Hộ chiếu, hợp đồng lao động, COE", "3 - 4 tháng"),
    ("CO_KHI", "JP", 5, "Xuất cảnh",
     "Hoàn tất hợp đồng, tham gia Quỹ hỗ trợ việc làm ngoài nước, nhận vé máy bay.",
     "Visa, hợp đồng, biên lai các khoản đã nộp", "1 tuần"),
    ("CO_KHI", "KR", 1, "Đăng ký dự thi EPS-TOPIK",
     "Theo dõi thông báo của Trung tâm Lao động ngoài nước, đăng ký thi tiếng Hàn đúng ngành và đợt tuyển.",
     "CCCD, hộ chiếu, ảnh", "Theo đợt thi"),
    ("CO_KHI", "KR", 2, "Thi tay nghề và chờ chủ sử dụng chọn",
     "Thi kỹ năng nghề, đánh giá năng lực; hồ sơ được đưa lên hệ thống để chủ sử dụng Hàn Quốc lựa chọn.",
     "Giấy khám sức khỏe, hồ sơ dự tuyển", "1 - 6 tháng"),
    ("CO_KHI", "KR", 3, "Ký hợp đồng, ký quỹ và nhận visa E-9",
     "Ký hợp đồng lao động, ký quỹ tại ngân hàng, học định hướng trước khi xuất cảnh.",
     "Hợp đồng lao động, giấy xác nhận ký quỹ", "1 - 2 tháng"),
    ("CHE_BIEN_THUC_PHAM", None, *_CHON_DOANH_NGHIEP),
    ("CHE_BIEN_THUC_PHAM", None, 2, "Thi tuyển, khám sức khỏe",
     "Thi tuyển theo đơn hàng (thao tác tay, thể lực), khám sức khỏe tại cơ sở y tế đủ điều kiện.",
     "Giấy khám sức khỏe, sơ yếu lý lịch", "2 - 4 tuần"),
    ("CHE_BIEN_THUC_PHAM", None, 3, "Đào tạo, làm visa và xuất cảnh",
     "Học ngoại ngữ, định hướng; doanh nghiệp làm thủ tục visa và tổ chức xuất cảnh.",
     "Hộ chiếu, hợp đồng lao động", "3 - 5 tháng"),
    ("NONG_NGHIEP", None, *_CHON_DOANH_NGHIEP),
    ("NONG_NGHIEP", None, 2, "Thi tuyển, khám sức khỏe",
     "Phỏng vấn với chủ trang trại, kiểm tra thể lực; khám sức khỏe theo yêu cầu đơn hàng.",
     "Giấy khám sức khỏe, sơ yếu lý lịch", "2 - 4 tuần"),
    ("NONG_NGHIEP", None, 3, "Đào tạo, làm visa và xuất cảnh",
     "Học ngoại ngữ, kỹ năng nông nghiệp cơ bản, định hướng; làm thủ tục visa và xuất cảnh.",
     "Hộ chiếu, hợp đồng lao động", "4 - 6 tháng"),
    ("DIEU_DUONG_HO_LY", "JP", 1, "Học tiếng Nhật N4",
     "Học tiếng Nhật đạt N4 (hoặc JFT-Basic) và tiếng Nhật chuyên ngành điều dưỡng.",
     "CCCD, bằng tốt nghiệp THPT", "6 - 10 tháng"),
    ("DIEU_DUONG_HO_LY", "JP", 2, "Thi kỹ năng Kaigo",
     "Thi kỳ thi đánh giá kỹ năng điều dưỡng và kỳ thi tiếng Nhật điều dưỡng.",
     "Hộ chiếu, chứng chỉ tiếng Nhật", "1 - 2 tháng"),
    ("DIEU_DUONG_HO_LY", "JP", 3, "Ký hợp đồng và xin visa kỹ năng đặc định",
     "Phỏng vấn với cơ sở điều dưỡng, ký hợp đồng, xin tư cách lưu trú và visa.",
     "Chứng chỉ kỹ năng, chứng chỉ tiếng, hợp đồng lao động", "2 - 4 tháng"),
    ("DIEU_DUONG_HO_LY", "DE", 1, "Học tiếng Đức B1 - B2",
     "Học tiếng Đức và thi chứng chỉ Goethe hoặc telc.", "CCCD, bằng tốt nghiệp", "8 - 12 tháng"),
    ("DIEU_DUONG_HO_LY", "DE", 2, "Công nhận văn bằng, ký hợp đồng",
     "Nộp hồ sơ công nhận văn bằng điều dưỡng, phỏng vấn và ký hợp đồng với cơ sở y tế Đức.",
     "Văn bằng dịch thuật công chứng, chứng chỉ tiếng Đức", "2 - 4 tháng"),
    ("DIEU_DUONG_HO_LY", "DE", 3, "Xin visa và xuất cảnh",
     "Đặt lịch nộp visa lao động tại Đại sứ quán Đức, nhận visa và xuất cảnh.",
     "Hợp đồng lao động, hộ chiếu, bảo hiểm", "1 - 3 tháng"),
]

_TRUNG_TAM_EPS = (
    "trung_tam_lao_dong_ngoai_nuoc", "Trung tâm Lao động ngoài nước (chương trình EPS)", "colab.gov.vn",
    "Tổ chức thi tiếng Hàn, tuyển chọn và đưa lao động đi Hàn Quốc theo chương trình EPS.",
    "Chương trình do Nhà nước thực hiện, không qua môi giới", 3,
)

# (ma_nhom, ma_quoc_gia | None, loai_kenh, ten_kenh, thong_tin_lien_he, mo_ta_ho_tro, luu_y_tranh_rui_ro,
#  thu_tu_hien_thi)
KENH_KET_NOI = [
    kenh
    for ma_nhom, *_ in NHOM_NGHE
    for kenh in (
        (ma_nhom, None, "co_quan_nha_nuoc", "Cục Quản lý lao động ngoài nước", "dolab.gov.vn",
         "Tra cứu doanh nghiệp được cấp phép, đơn hàng đã đăng ký; tiếp nhận phản ánh, khiếu nại.",
         "Chỉ ký hợp đồng với doanh nghiệp có tên trong danh sách cấp phép", 1),
        (ma_nhom, None, "doanh_nghiep_cap_phep", "Doanh nghiệp dịch vụ được cấp phép", "Tra cứu tại dolab.gov.vn",
         "Tuyển chọn, đào tạo, làm thủ tục và quản lý người lao động trong thời gian làm việc ở nước ngoài.",
         "Không nộp tiền cho cá nhân, môi giới; yêu cầu biên lai cho mọi khoản thu", 2),
        (ma_nhom, None, "ho_tro_he_thong", "Tư vấn định hướng trên hệ thống", None,
         "Gợi ý nhóm nghề, thị trường phù hợp với sức khỏe, sở thích và khả năng tài chính.", None, 4),
    )
] + [
    ("CO_KHI", "KR", *_TRUNG_TAM_EPS),
    ("NONG_NGHIEP", "KR", *_TRUNG_TAM_EPS),
    ("DIEU_DUONG_HO_LY", "DE", "trung_tam_lao_dong_ngoai_nuoc",
     "Trung tâm Lao động ngoài nước (chương trình điều dưỡng Đức)", "colab.gov.vn",
     "Tuyển chọn, đào tạo tiếng Đức và đưa điều dưỡng sang Đức theo chương trình hợp tác.",
     "Kiểm tra thông báo tuyển chọn trên trang chính thức", 3),
]


def _bang(ten: str, *cot: str) -> sa.TableClause:
    return sa.table(ten, *(sa.column(c) for c in cot))


def _dong(cot, du_lieu):
    return [dict(zip(cot, dong, strict=True)) for dong in du_lieu]


def _map_id(conn, sql: str, ids: list) -> dict:
    """Chạy truy vấn trả về (khóa..., id) với tham số IN :ids, trả về map khóa → id."""
    stmt = sa.text(sql).bindparams(sa.bindparam("ids", expanding=True))
    return {tuple(row[:-1]) if len(row) > 2 else row[0]: row[-1] for row in conn.execute(stmt, {"ids": ids})}


def upgrade() -> None:
    conn = op.get_bind()
    co_san = set(conn.execute(sa.text("SELECT ma_nhom FROM dm_thpt_xkld_nhom_nghe")).scalars())
    nhom_moi = [dong for dong in NHOM_NGHE if dong[0] not in co_san]
    if not nhom_moi:
        return
    ma_moi = [dong[0] for dong in nhom_moi]

    op.bulk_insert(
        _bang(
            "dm_thpt_xkld_nhom_nghe", "ma_nhom", "ten_nhom", "mo_ta_cong_viec", "dieu_kien_suc_khoe_the_luc",
            "yeu_cau_ngoai_ngu", "thoi_gian_chuan_bi_text", "thoi_gian_chuan_bi_thang_min",
            "thoi_gian_chuan_bi_thang_max", "muc_thu_nhap_text", "thu_nhap_thang_min", "thu_nhap_thang_max",
            "trien_vong_sau_ve_nuoc", "kha_nang_gia_han_visa",
        ),
        _dong(
            (
                "ma_nhom", "ten_nhom", "mo_ta_cong_viec", "dieu_kien_suc_khoe_the_luc", "yeu_cau_ngoai_ngu",
                "thoi_gian_chuan_bi_text", "thoi_gian_chuan_bi_thang_min", "thoi_gian_chuan_bi_thang_max",
                "muc_thu_nhap_text", "thu_nhap_thang_min", "thu_nhap_thang_max", "trien_vong_sau_ve_nuoc",
                "kha_nang_gia_han_visa",
            ),
            nhom_moi,
        ),
    )
    id_nhom = _map_id(conn, "SELECT ma_nhom, id FROM dm_thpt_xkld_nhom_nghe WHERE ma_nhom IN :ids", ma_moi)

    op.bulk_insert(
        _bang(
            "dm_thpt_xkld_thi_truong", "thpt_xkld_nhom_nghe_id", "ma_quoc_gia", "ten_quoc_gia", "loai_visa",
            "dac_diem_thi_truong", "thu_nhap_rieng_text", "thoi_han_hop_dong_nam", "thu_tu_hien_thi",
        ),
        [
            {
                "thpt_xkld_nhom_nghe_id": id_nhom[ma_nhom], "ma_quoc_gia": ma_qg, "ten_quoc_gia": ten_qg,
                "loai_visa": visa, "dac_diem_thi_truong": dac_diem, "thu_nhap_rieng_text": thu_nhap,
                "thoi_han_hop_dong_nam": hop_dong, "thu_tu_hien_thi": thu_tu,
            }
            for ma_nhom, ma_qg, ten_qg, visa, dac_diem, thu_nhap, hop_dong, thu_tu in THI_TRUONG
            if ma_nhom in id_nhom
        ],
    )
    id_tt = _map_id(
        conn,
        "SELECT thpt_xkld_nhom_nghe_id, ma_quoc_gia, id FROM dm_thpt_xkld_thi_truong "
        "WHERE thpt_xkld_nhom_nghe_id IN :ids",
        list(id_nhom.values()),
    )

    def _lien_ket(cot, du_lieu):
        """Đổi (ma_nhom, ma_quoc_gia) đầu mỗi dòng thành id nhóm nghề, id thị trường."""
        dong_moi = []
        for ma_nhom, ma_qg, *con_lai in du_lieu:
            if ma_nhom not in id_nhom:
                continue
            nhom_id = id_nhom[ma_nhom]
            dong_moi.append((nhom_id, id_tt[(nhom_id, ma_qg)] if ma_qg else None, *con_lai))
        return _dong(("thpt_xkld_nhom_nghe_id", "thpt_xkld_thi_truong_id", *cot), dong_moi)

    for ten, cot, du_lieu in (
        ("dm_thpt_xkld_nghe_cu_the", ("ten_cong_viec", "mo_ta_ngan", "yeu_cau_gioi_tinh"), NGHE_CU_THE),
        (
            "dm_thpt_xkld_chi_phi",
            ("loai_chi_phi", "ten_khoan_chi", "chi_phi_min", "chi_phi_max", "don_vi_tien",
             "chi_phi_quy_doi_vnd_text", "ghi_chu"),
            CHI_PHI,
        ),
        (
            "dm_thpt_xkld_thu_tuc",
            ("buoc_so", "ten_buoc", "mo_ta_thu_tuc", "giay_to_can_co", "thoi_gian_du_kien"),
            THU_TUC,
        ),
        (
            "dm_thpt_xkld_kenh_ket_noi",
            ("loai_kenh", "ten_kenh", "thong_tin_lien_he", "mo_ta_ho_tro", "luu_y_tranh_rui_ro", "thu_tu_hien_thi"),
            KENH_KET_NOI,
        ),
    ):
        op.bulk_insert(_bang(ten, "thpt_xkld_nhom_nghe_id", "thpt_xkld_thi_truong_id", *cot), _lien_ket(cot, du_lieu))


def downgrade() -> None:
    # Bảng con và thị trường bị xóa theo nhờ khóa ngoại ON DELETE CASCADE.
    op.get_bind().execute(
        sa.text("DELETE FROM dm_thpt_xkld_nhom_nghe WHERE ma_nhom IN :ids").bindparams(
            sa.bindparam("ids", expanding=True)
        ),
        {"ids": [dong[0] for dong in NHOM_NGHE]},
    )
