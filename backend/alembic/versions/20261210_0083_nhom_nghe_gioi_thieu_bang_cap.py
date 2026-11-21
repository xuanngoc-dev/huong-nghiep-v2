"""Nhóm nghề đi làm: thêm mục giới thiệu; nghề cụ thể: thêm yêu cầu bằng cấp, bắt buộc đào tạo chính quy.

- dm_nhom_nghe_di_lam: nganh_nay_la_gi, noi_lam_viec_o_dau, cong_viec_hang_ngay_nhu_the_nao, ap_luc_va_rui_ro,
  xu_huong_tuong_lai, ket_luan (TEXT, null).
- dm_nghe_cu_the_di_lam: yeu_cau_bang_cap (VARCHAR 255, null = không yêu cầu), bat_buoc_dao_tao_chinh_quy
  (TINYINT, 1 = bắt buộc, null = không).
- Dữ liệu mẫu: điền mục giới thiệu cho 8 nhóm cũ (chỉ ô đang trống), thêm 10 nhóm mới (kể cả nhóm cần bằng cấp /
  đào tạo chính quy như công an, quân đội, y tế), thêm nghề cụ thể và điểm tiêu chí gợi ý cho nhóm mới. Không ghi
  đè dữ liệu quản trị đã sửa; chạy lại được. Lương tính bằng triệu đồng/tháng, mang tính tham khảo.

Revision ID: 20261210_0083
Revises: 20261209_0082
Create Date: 2026-12-10 10:00:00.000000
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.mysql import TINYINT

revision = "20261210_0083"
down_revision = "20261209_0082"
branch_labels = None
depends_on = None

COT_GIOI_THIEU = (
    "nganh_nay_la_gi",
    "noi_lam_viec_o_dau",
    "cong_viec_hang_ngay_nhu_the_nao",
    "ap_luc_va_rui_ro",
    "xu_huong_tuong_lai",
    "ket_luan",
)

# Nhóm nghề mới. Lương: khởi điểm min/max, có kinh nghiệm tối đa (triệu đồng/tháng).
NHOM_MOI = [
    dict(
        ma_nhom="XAY_DUNG_HOAN_THIEN", ten_nhom="Xây dựng, hoàn thiện công trình",
        mo_ta_dac_diem="Thi công và hoàn thiện nhà ở, công trình: xây trát, ốp lát, sơn bả, cốp pha, cốt thép, điện"
        " nước; học việc theo thợ cả hoặc học sơ cấp nghề.",
        loai_hinh_dau_vao="hoc_nghe_ngan_han", thoi_gian_dao_tao_text="Học việc 3-6 tháng hoặc sơ cấp nghề",
        thoi_gian_dao_tao_thang_min=3, thoi_gian_dao_tao_thang_max=6,
        dieu_kien_dau_vao="Đủ 18 tuổi, sức khỏe tốt, không sợ độ cao, chịu được nắng nóng.",
        muc_luong_text="8 - 12 triệu/tháng", luong_khoi_diem_min=8, luong_khoi_diem_max=12, luong_kinh_nghiem_max=25,
        danh_gia_trien_vong="Nhu cầu ổn định nhờ xây dựng hạ tầng, nhà ở; thợ lành nghề luôn thiếu",
        lo_trinh_phat_trien="Phụ hồ → Thợ chính → Thợ cả / Tổ trưởng → Nhận khoán công trình nhỏ.",
        nhom_muc_tieu="nghe_vung_chac", ma_holland="RC",
    ),
    dict(
        ma_nhom="KHO_VAN_LOGISTICS", ten_nhom="Kho vận, logistics",
        mo_ta_dac_diem="Nhận, sắp xếp, kiểm đếm, đóng gói và xuất hàng tại kho của sàn thương mại điện tử, siêu thị,"
        " công ty vận chuyển; vận hành xe nâng, máy quét mã vạch.",
        loai_hinh_dau_vao="di_lam_ngay", thoi_gian_dao_tao_text="Đào tạo tại chỗ 1-2 tuần; xe nâng học 1-2 tháng",
        thoi_gian_dao_tao_thang_min=0, thoi_gian_dao_tao_thang_max=2,
        dieu_kien_dau_vao="Tốt nghiệp THCS/THPT, đủ 18 tuổi, cẩn thận, chịu được làm ca.",
        muc_luong_text="7 - 10 triệu/tháng", luong_khoi_diem_min=7, luong_khoi_diem_max=10, luong_kinh_nghiem_max=18,
        danh_gia_trien_vong="Tăng mạnh theo thương mại điện tử và giao hàng nhanh",
        lo_trinh_phat_trien="Nhân viên kho → Tổ trưởng ca → Thủ kho → Giám sát kho, điều phối vận tải.",
        nhom_muc_tieu="kiem_tien_ngay", ma_holland="RC",
    ),
    dict(
        ma_nhom="NONG_NGHIEP_CONG_NGHE", ten_nhom="Nông nghiệp, chăn nuôi công nghệ cao",
        mo_ta_dac_diem="Trồng rau nhà màng, thủy canh, chăn nuôi trang trại, nuôi trồng thủy sản; dùng hệ thống tưới"
        " tự động, cảm biến, phần mềm quản lý trang trại.",
        loai_hinh_dau_vao="hoc_nghe_ngan_han", thoi_gian_dao_tao_text="Sơ cấp nghề 3-6 tháng hoặc học tại trang trại",
        thoi_gian_dao_tao_thang_min=0, thoi_gian_dao_tao_thang_max=6,
        dieu_kien_dau_vao="Tốt nghiệp THCS/THPT, yêu thiên nhiên, chịu được làm ngoài trời.",
        muc_luong_text="7 - 11 triệu/tháng", luong_khoi_diem_min=7, luong_khoi_diem_max=11, luong_kinh_nghiem_max=30,
        danh_gia_trien_vong="Được khuyến khích phát triển; có thể tự làm chủ mô hình trang trại",
        lo_trinh_phat_trien="Công nhân trang trại → Kỹ thuật viên → Quản lý khu sản xuất → Tự làm chủ mô hình.",
        nhom_muc_tieu="nghe_vung_chac", ma_holland="RI",
    ),
    dict(
        ma_nhom="DU_LICH_SU_KIEN", ten_nhom="Du lịch, lữ hành, tổ chức sự kiện",
        mo_ta_dac_diem="Hướng dẫn, điều hành tour, đặt dịch vụ, tổ chức sự kiện, dẫn chương trình; công việc theo"
        " mùa du lịch và lịch sự kiện.",
        loai_hinh_dau_vao="hoc_nghe_ngan_han", thoi_gian_dao_tao_text="Khóa ngắn hạn 1-6 tháng",
        thoi_gian_dao_tao_thang_min=1, thoi_gian_dao_tao_thang_max=6,
        dieu_kien_dau_vao="Tốt nghiệp THPT, giao tiếp tốt; ngoại ngữ là lợi thế lớn.",
        muc_luong_text="6 - 10 triệu/tháng + tiền tip, công tác phí", luong_khoi_diem_min=6, luong_khoi_diem_max=10,
        luong_kinh_nghiem_max=25,
        danh_gia_trien_vong="Tăng trưởng tốt theo du lịch, thu nhập thay đổi theo mùa",
        lo_trinh_phat_trien="Cộng tác viên sự kiện → Điều hành tour → Trưởng nhóm → Mở công ty lữ hành, sự kiện nhỏ.",
        nhom_muc_tieu="nghe_vung_chac", ma_holland="ES",
    ),
    dict(
        ma_nhom="Y_TE_CHAM_SOC", ten_nhom="Y tế, chăm sóc sức khỏe",
        mo_ta_dac_diem="Chăm sóc người bệnh, người cao tuổi, phụ việc tại bệnh viện, phòng khám, nhà thuốc. Nhiều"
        " nghề trong nhóm (điều dưỡng, y sĩ, bác sĩ, dược sĩ) bắt buộc học chính quy và có giấy phép hành nghề.",
        loai_hinh_dau_vao="hoc_nghe_ngan_han",
        thoi_gian_dao_tao_text="Hộ lý 1-3 tháng; điều dưỡng 3 năm; bác sĩ 6 năm",
        thoi_gian_dao_tao_thang_min=1, thoi_gian_dao_tao_thang_max=72,
        dieu_kien_dau_vao="Tốt nghiệp THPT, sức khỏe tốt, kiên nhẫn; nghề cần bằng cấp xét tuyển theo tổ hợp có"
        " Toán, Hóa, Sinh.",
        muc_luong_text="6 - 9 triệu/tháng (hộ lý, chăm sóc)", luong_khoi_diem_min=6, luong_khoi_diem_max=9,
        luong_kinh_nghiem_max=40,
        danh_gia_trien_vong="Nhu cầu rất lớn do dân số già đi và nhu cầu chăm sóc sức khỏe tăng",
        lo_trinh_phat_trien="Hộ lý, chăm sóc → học tiếp điều dưỡng → Điều dưỡng trưởng; hoặc thi vào trường y để"
        " làm y sĩ, bác sĩ.",
        nhom_muc_tieu="nghe_vung_chac", ma_holland="SI",
    ),
    dict(
        ma_nhom="AN_NINH_LUC_LUONG_VU_TRANG", ten_nhom="Công an, quân đội, bảo vệ",
        mo_ta_dac_diem="Bảo vệ an ninh, trật tự tại tòa nhà, sự kiện (đi làm được ngay); công an, quân đội chuyên"
        " nghiệp, phòng cháy chữa cháy phải thi tuyển và học chính quy tại trường của ngành.",
        loai_hinh_dau_vao="hoc_nghe_ngan_han",
        thoi_gian_dao_tao_text="Bảo vệ 1-2 tuần; công an, quân đội 2-4 năm chính quy",
        thoi_gian_dao_tao_thang_min=0, thoi_gian_dao_tao_thang_max=48,
        dieu_kien_dau_vao="Đủ 18 tuổi, sức khỏe và chiều cao theo quy định; công an, quân đội cần lý lịch rõ ràng,"
        " sơ tuyển tại địa phương rồi thi tuyển.",
        muc_luong_text="7 - 10 triệu/tháng (bảo vệ)", luong_khoi_diem_min=7, luong_khoi_diem_max=10,
        luong_kinh_nghiem_max=30,
        danh_gia_trien_vong="Bảo vệ luôn cần người; công an, quân đội ổn định, có chế độ đãi ngộ",
        lo_trinh_phat_trien="Bảo vệ → Đội trưởng → Quản lý an ninh; hoặc nhập ngũ, thi vào trường công an, quân đội"
        " để theo ngành lâu dài.",
        nhom_muc_tieu="nghe_vung_chac", ma_holland="RS",
    ),
    dict(
        ma_nhom="CHAM_SOC_GIA_DINH", ten_nhom="Giúp việc, chăm sóc trẻ và người cao tuổi",
        mo_ta_dac_diem="Dọn dẹp, nấu ăn, trông trẻ, chăm sóc người cao tuổi tại gia đình hoặc qua công ty dịch vụ;"
        " có thể làm theo giờ hoặc ở lại nhà chủ.",
        loai_hinh_dau_vao="di_lam_ngay", thoi_gian_dao_tao_text="Đào tạo 1-4 tuần qua công ty dịch vụ",
        thoi_gian_dao_tao_thang_min=0, thoi_gian_dao_tao_thang_max=1,
        dieu_kien_dau_vao="Đủ 18 tuổi, trung thực, kiên nhẫn, sức khỏe tốt.",
        muc_luong_text="6 - 10 triệu/tháng (thường bao ăn ở)", luong_khoi_diem_min=6, luong_khoi_diem_max=10,
        luong_kinh_nghiem_max=15,
        danh_gia_trien_vong="Nhu cầu tăng ở thành phố lớn và đơn hàng điều dưỡng, hộ lý ở nước ngoài",
        lo_trinh_phat_trien="Giúp việc theo giờ → Nhân viên chăm sóc chuyên nghiệp → Học điều dưỡng hoặc đi làm"
        " hộ lý ở nước ngoài.",
        nhom_muc_tieu="kiem_tien_ngay", ma_holland="S",
    ),
    dict(
        ma_nhom="VAN_PHONG_HANH_CHINH", ten_nhom="Văn phòng, hành chính, thu ngân",
        mo_ta_dac_diem="Lễ tân, nhập liệu, thu ngân, trợ lý hành chính tại công ty, cửa hàng; kế toán cần bằng"
        " trung cấp chuyên ngành trở lên.",
        loai_hinh_dau_vao="hoc_nghe_ngan_han",
        thoi_gian_dao_tao_text="Tin học văn phòng 1-3 tháng; kế toán trung cấp 1,5-2 năm",
        thoi_gian_dao_tao_thang_min=1, thoi_gian_dao_tao_thang_max=24,
        dieu_kien_dau_vao="Tốt nghiệp THPT, thành thạo tin học văn phòng, cẩn thận, chữ viết rõ ràng.",
        muc_luong_text="6 - 8 triệu/tháng", luong_khoi_diem_min=6, luong_khoi_diem_max=8, luong_kinh_nghiem_max=15,
        danh_gia_trien_vong="Ổn định nhưng cạnh tranh; việc nhập liệu đang dần được tự động hóa",
        lo_trinh_phat_trien="Nhập liệu, thu ngân → Trợ lý → Chuyên viên hành chính (học thêm văn bằng).",
        nhom_muc_tieu="nghe_vung_chac", ma_holland="CS",
    ),
    dict(
        ma_nhom="GIAO_DUC_TRO_GIANG", ten_nhom="Giáo dục: trợ giảng, mầm non",
        mo_ta_dac_diem="Trợ giảng ở trung tâm ngoại ngữ, kỹ năng, bảo mẫu nhóm trẻ, gia sư; giáo viên mầm non, tiểu"
        " học phải học sư phạm chính quy.",
        loai_hinh_dau_vao="hoc_nghe_ngan_han",
        thoi_gian_dao_tao_text="Bảo mẫu 1-3 tháng; giáo viên mầm non cao đẳng 3 năm",
        thoi_gian_dao_tao_thang_min=1, thoi_gian_dao_tao_thang_max=36,
        dieu_kien_dau_vao="Tốt nghiệp THPT, yêu trẻ, giọng nói chuẩn; ngoại ngữ tốt nếu làm trợ giảng.",
        muc_luong_text="5 - 8 triệu/tháng", luong_khoi_diem_min=5, luong_khoi_diem_max=8, luong_kinh_nghiem_max=15,
        danh_gia_trien_vong="Ổn định; giáo viên mầm non vẫn thiếu ở nhiều nơi",
        lo_trinh_phat_trien="Trợ giảng, bảo mẫu → Học sư phạm → Giáo viên → Quản lý nhóm lớp, trung tâm.",
        nhom_muc_tieu="nghe_vung_chac", ma_holland="SA",
    ),
    dict(
        ma_nhom="HANG_KHONG_HANG_HAI", ten_nhom="Hàng không, hàng hải",
        mo_ta_dac_diem="Phục vụ mặt đất ở sân bay, tiếp viên hàng không, thuyền viên tàu biển; phần lớn phải qua"
        " đào tạo bắt buộc và có chứng chỉ chuyên môn của ngành.",
        loai_hinh_dau_vao="hoc_nghe_ngan_han",
        thoi_gian_dao_tao_text="Mặt đất 1-3 tháng; tiếp viên 3-4 tháng; thuyền viên 6-24 tháng",
        thoi_gian_dao_tao_thang_min=1, thoi_gian_dao_tao_thang_max=24,
        dieu_kien_dau_vao="Tốt nghiệp THPT, tiếng Anh tốt, sức khỏe và chiều cao đạt tiêu chuẩn ngành.",
        muc_luong_text="8 - 15 triệu/tháng", luong_khoi_diem_min=8, luong_khoi_diem_max=15, luong_kinh_nghiem_max=45,
        danh_gia_trien_vong="Phục hồi tốt theo du lịch và thương mại quốc tế; thu nhập cao nhưng tuyển chọn khắt khe",
        lo_trinh_phat_trien="Nhân viên mặt đất → Trưởng ca; tiếp viên → Tiếp viên trưởng; thủy thủ → Sĩ quan"
        " (học thêm).",
        nhom_muc_tieu="thu_nhap_dot_pha", ma_holland="ESR",
    ),
]

# Mục giới thiệu cho từng nhóm (thứ tự theo COT_GIOI_THIEU).
GIOI_THIEU = {
    "CONG_NHAN_SAN_XUAT": (
        "Là những người trực tiếp làm ra sản phẩm trong nhà máy: lắp ráp, may, vận hành máy, kiểm tra và đóng gói"
        " theo dây chuyền.",
        "Nhà máy, xưởng sản xuất trong các khu công nghiệp ở Bắc Ninh, Bắc Giang, Bình Dương, Đồng Nai, Hải Phòng…",
        "Làm theo ca 8-12 tiếng, mỗi người phụ trách một công đoạn, thao tác lặp lại theo hướng dẫn; được đào tạo"
        " ngay khi vào làm.",
        "Công việc lặp lại dễ nhàm chán, tăng ca nhiều mùa cao điểm, phải đứng lâu; một số vị trí có tiếng ồn,"
        " hóa chất cần tuân thủ bảo hộ lao động.",
        "Nhu cầu vẫn lớn nhờ các nhà máy FDI, nhưng tự động hóa đang tăng: công nhân biết vận hành, bảo trì máy sẽ có"
        " lợi thế.",
        "Phù hợp nếu bạn cần thu nhập ổn định ngay, chịu được làm ca. Nên học thêm kỹ năng vận hành máy hoặc quản lý"
        " để không dừng ở vị trí công nhân.",
    ),
    "BAN_HANG_DICH_VU": (
        "Tư vấn sản phẩm, bán hàng và chăm sóc khách hàng trực tiếp hoặc qua điện thoại, mạng xã hội.",
        "Cửa hàng, siêu thị, trung tâm thương mại, showroom, tổng đài chăm sóc khách hàng, văn phòng kinh doanh.",
        "Đón khách, tìm hiểu nhu cầu, giới thiệu sản phẩm, chốt đơn, giải đáp thắc mắc và theo dõi khách sau khi mua.",
        "Áp lực doanh số hằng tháng, gặp khách khó tính; thu nhập lên xuống theo hoa hồng; phải đứng lâu hoặc làm"
        " cuối tuần, lễ Tết.",
        "Bán hàng đa kênh (cửa hàng + online) phát triển; người giỏi tư vấn, chăm sóc khách hàng vẫn rất được cần.",
        "Hợp với người thích giao tiếp và muốn thu nhập theo năng lực. Kỹ năng bán hàng dùng được ở hầu hết ngành"
        " nghề sau này.",
    ),
    "GIAO_HANG_VAN_TAI": (
        "Vận chuyển hàng hóa và hành khách bằng xe máy, ô tô, xe tải; giao hàng cho sàn thương mại điện tử và"
        " nhà hàng.",
        "Ngoài đường phố, bến xe, kho hàng; làm việc qua ứng dụng (Grab, Be, Shopee, GHN…) hoặc cho công ty vận tải.",
        "Nhận đơn, lấy hàng, tìm đường, giao và thu tiền; tài xế đường dài chạy theo chuyến, nghỉ dọc đường.",
        "Nắng mưa, kẹt xe, rủi ro tai nạn giao thông; thu nhập phụ thuộc số đơn; chi phí xăng, khấu hao xe tự chịu.",
        "Thương mại điện tử tăng nên nhu cầu giao hàng vẫn cao; xe điện và giao hàng tự động có thể thay đổi nghề"
        " trong dài hạn.",
        "Kiếm tiền nhanh và linh hoạt giờ giấc. Muốn bền vững nên học lấy bằng lái hạng cao để lái xe tải, xe khách.",
    ),
    "DIEN_CO_KHI": (
        "Lắp đặt, bảo dưỡng, sửa chữa hệ thống điện, điện lạnh, máy móc, ô tô, xe máy, thiết bị điện tử.",
        "Công trình, nhà máy, gara, cửa hàng sửa chữa, công ty dịch vụ kỹ thuật; nhiều người tự mở tiệm.",
        "Kiểm tra, tìm lỗi, thay thế linh kiện, lắp đặt thiết bị mới và hướng dẫn khách sử dụng an toàn.",
        "Nguy cơ điện giật, làm việc trên cao, môi trường dầu mỡ; phải chịu trách nhiệm khi sửa chữa sai.",
        "Thợ kỹ thuật giỏi luôn thiếu; xe điện, điện mặt trời, nhà thông minh mở thêm nhiều việc mới.",
        "Nghề vững, càng làm càng giỏi và có thể tự làm chủ. Nên có chứng chỉ an toàn điện và học trung cấp nghề"
        " để lên bậc thợ.",
    ),
    "BEP_NHA_HANG": (
        "Chế biến món ăn, pha chế đồ uống và phục vụ khách tại nhà hàng, khách sạn, quán cà phê.",
        "Nhà hàng, khách sạn, khu nghỉ dưỡng, quán cà phê, bếp ăn công nghiệp, du thuyền.",
        "Sơ chế nguyên liệu, nấu theo thực đơn, giữ vệ sinh bếp; pha chế, phục vụ bàn, đón tiếp khách lưu trú.",
        "Làm việc khi người khác nghỉ (tối, cuối tuần, lễ Tết), nóng bức, đứng lâu; giờ cao điểm rất áp lực.",
        "Du lịch, ăn uống phát triển; đầu bếp, barista giỏi có thể làm ở nước ngoài hoặc mở quán riêng.",
        "Hợp với người thích nấu nướng, khéo tay, chịu khó. Nên học khóa nghề có chứng chỉ để có mức lương tốt hơn.",
    ),
    "LAM_DEP": (
        "Cắt tóc, làm móng, chăm sóc da, trang điểm, phun xăm thẩm mỹ cho khách.",
        "Salon tóc, tiệm nail, spa, thẩm mỹ viện, studio trang điểm; nhiều người tự mở tiệm tại nhà.",
        "Tư vấn kiểu dáng, thực hiện dịch vụ, vệ sinh dụng cụ, chăm sóc khách quen và giới thiệu dịch vụ mới.",
        "Đứng hoặc ngồi lâu, tiếp xúc hóa chất (thuốc nhuộm, sơn móng); khách không hài lòng ảnh hưởng uy tín.",
        "Nhu cầu làm đẹp tăng đều; thợ có tay nghề và biết xây dựng khách hàng trên mạng xã hội rất có lợi thế.",
        "Hợp với người khéo tay, có gu thẩm mỹ. Học nghề ngắn và có thể mở tiệm với vốn nhỏ.",
    ),
    "KY_NANG_SO": (
        "Làm việc với máy tính: thiết kế đồ họa, lập trình, chạy quảng cáo, biên tập video, kiểm thử phần mềm.",
        "Công ty công nghệ, agency quảng cáo, phòng marketing của doanh nghiệp; nhiều việc làm từ xa hoặc freelance.",
        "Nhận yêu cầu, làm sản phẩm trên phần mềm, sửa theo góp ý, theo dõi số liệu và học công cụ mới.",
        "Ngồi máy tính nhiều giờ, deadline gấp; công nghệ thay đổi nhanh, không tự học sẽ bị tụt lại.",
        "Nhu cầu nhân lực số cao và tăng; AI đổi cách làm nhưng người biết dùng AI để làm nhanh hơn sẽ có lợi thế.",
        "Không cần bằng đại học nếu có sản phẩm thực tế (portfolio). Hợp với người tự học tốt, kiên trì.",
    ),
    "KINH_DOANH_ONLINE": (
        "Tự bán hàng, livestream, làm nội dung trên mạng xã hội và sàn thương mại điện tử để kiếm tiền.",
        "Tại nhà, studio nhỏ, kho hàng; bán qua Shopee, Lazada, TikTok Shop, Facebook.",
        "Tìm nguồn hàng, chụp ảnh, viết mô tả, livestream, trả lời khách, đóng gói, theo dõi đơn và chạy quảng cáo.",
        "Thu nhập không ổn định, cạnh tranh gay gắt, có thể lỗ vốn; phải tự chịu trách nhiệm về thuế, chất lượng"
        " hàng.",
        "Thương mại điện tử Việt Nam tăng trưởng nhanh; người làm nội dung có chất lượng vẫn có nhiều cơ hội.",
        "Hợp với người năng động, thích tự làm chủ. Nên bắt đầu nhỏ, học cách làm nội dung và quản lý tiền vốn.",
    ),
    "XAY_DUNG_HOAN_THIEN": (
        "Những người trực tiếp xây dựng và hoàn thiện nhà cửa, công trình: xây, trát, ốp lát, sơn, lắp đặt điện"
        " nước, nhôm kính.",
        "Công trường nhà ở, chung cư, nhà xưởng, công trình giao thông; làm cho nhà thầu hoặc theo đội thợ.",
        "Đọc bản vẽ đơn giản, chuẩn bị vật liệu, thi công theo hạng mục, đảm bảo đúng kỹ thuật và an toàn.",
        "Làm ngoài trời, trên cao, công việc nặng; nguy cơ tai nạn lao động nếu không dùng đồ bảo hộ; việc theo"
        " công trình nên có lúc gián đoạn.",
        "Đầu tư hạ tầng và nhà ở tiếp tục lớn; thợ hoàn thiện chất lượng cao (ốp lát, sơn, nhôm kính) rất được giá.",
        "Hợp với người khỏe, khéo tay, thích nhìn thấy sản phẩm mình làm ra. Lên thợ cả có thể nhận khoán, thu nhập"
        " tốt.",
    ),
    "KHO_VAN_LOGISTICS": (
        "Quản lý dòng hàng hóa trong kho: nhận, sắp xếp, đóng gói, xuất hàng và điều phối giao nhận.",
        "Kho của sàn thương mại điện tử, siêu thị, công ty chuyển phát, cảng, khu công nghiệp.",
        "Quét mã nhận hàng, xếp lên kệ, soạn đơn theo phiếu, đóng gói, kiểm đếm cuối ca, lái xe nâng di chuyển hàng.",
        "Làm ca đêm, bê vác nặng, áp lực đơn mùa sale (11/11, 12/12, Tết); sai sót kiểm đếm phải bồi thường.",
        "Logistics và thương mại điện tử tăng nhanh; kho tự động cần thêm người biết vận hành phần mềm, thiết bị.",
        "Vào làm nhanh, không cần kinh nghiệm. Học thêm lái xe nâng, phần mềm quản lý kho để lên thủ kho, giám sát.",
    ),
    "NONG_NGHIEP_CONG_NGHE": (
        "Sản xuất nông nghiệp bằng kỹ thuật mới: nhà màng, thủy canh, tưới tự động, chăn nuôi khép kín, nuôi thủy sản"
        " công nghệ cao.",
        "Trang trại, hợp tác xã, khu nông nghiệp công nghệ cao (Lâm Đồng, Sơn La, Đồng bằng sông Cửu Long…), doanh"
        " nghiệp chế biến.",
        "Gieo trồng, chăm sóc, theo dõi cảm biến nhiệt độ, độ ẩm, cho ăn, phòng bệnh, thu hoạch và sơ chế.",
        "Phụ thuộc thời tiết, dịch bệnh, giá cả đầu ra; làm việc ngoài trời, xa thành phố.",
        "Nông nghiệp sạch, xuất khẩu được khuyến khích; người trẻ biết công nghệ và bán hàng online có nhiều cơ hội.",
        "Hợp với người yêu thiên nhiên, muốn làm ở quê hoặc tự làm chủ. Nên học thêm kỹ thuật và cách bán nông sản.",
    ),
    "DU_LICH_SU_KIEN": (
        "Tổ chức và phục vụ chuyến đi, sự kiện: hướng dẫn khách, điều hành tour, đặt dịch vụ, dẫn chương trình.",
        "Công ty lữ hành, khu du lịch, khách sạn, công ty tổ chức sự kiện, trung tâm hội nghị.",
        "Lên lịch trình, đón khách, thuyết minh điểm đến, xử lý phát sinh; chuẩn bị sân khấu, âm thanh cho sự kiện.",
        "Đi xa nhiều, làm cả cuối tuần, lễ Tết; mùa thấp điểm ít việc; phải xử lý tình huống bất ngờ.",
        "Du lịch quốc tế và nội địa tăng; người biết ngoại ngữ, kể chuyện hay và dùng mạng xã hội rất được cần.",
        "Hợp với người hoạt bát, thích đi đây đó. Hướng dẫn viên cần thẻ hành nghề; học ngoại ngữ sẽ tăng thu nhập"
        " rõ rệt.",
    ),
    "Y_TE_CHAM_SOC": (
        "Chăm sóc sức khỏe con người: từ hỗ trợ sinh hoạt người bệnh (hộ lý) đến khám chữa bệnh, cấp phát thuốc"
        " (bác sĩ, dược sĩ).",
        "Bệnh viện, phòng khám, trung tâm dưỡng lão, nhà thuốc, phòng xét nghiệm; chăm sóc tại nhà người bệnh.",
        "Hộ lý giúp người bệnh ăn uống, vệ sinh, di chuyển; điều dưỡng theo dõi, tiêm truyền; bác sĩ khám, chẩn đoán,"
        " điều trị.",
        "Trực đêm, tiếp xúc nguồn bệnh, áp lực tính mạng con người. Bác sĩ, điều dưỡng, dược sĩ phải học chính quy"
        " nhiều năm và có giấy phép hành nghề, không thể đi làm ngay sau THPT.",
        "Dân số già đi, nhu cầu chăm sóc tăng mạnh trong nước và ở Nhật, Đức (điều dưỡng, hộ lý).",
        "Có thể bắt đầu ngay bằng hộ lý, chăm sóc người cao tuổi. Muốn làm điều dưỡng, y sĩ, bác sĩ thì cần xác định"
        " học chính quy tại trường y từ sớm.",
    ),
    "AN_NINH_LUC_LUONG_VU_TRANG": (
        "Bảo vệ an ninh, trật tự và an toàn: từ bảo vệ tòa nhà, sự kiện đến lực lượng công an, quân đội, phòng"
        " cháy chữa cháy.",
        "Tòa nhà, nhà máy, ngân hàng, sự kiện (bảo vệ); đơn vị công an, quân đội, đội cứu hỏa trên cả nước.",
        "Bảo vệ tuần tra, kiểm soát ra vào, xử lý sự cố; chiến sĩ huấn luyện, làm nhiệm vụ theo phân công.",
        "Trực đêm, nguy hiểm khi xử lý tình huống; kỷ luật nghiêm. Công an, quân đội chuyên nghiệp phải qua sơ tuyển"
        " sức khỏe, lý lịch và học chính quy tại trường của ngành.",
        "Bảo vệ chuyên nghiệp ngày càng được chuẩn hóa; công an, quân đội tuyển sinh hằng năm, ổn định lâu dài.",
        "Bảo vệ đi làm được ngay. Muốn vào công an, quân đội nên chuẩn bị sức khỏe, học lực và tìm hiểu kỳ thi vào"
        " trường công an, quân đội từ lớp 11, 12.",
    ),
    "CHAM_SOC_GIA_DINH": (
        "Hỗ trợ việc nhà và chăm sóc người thân cho các gia đình: dọn dẹp, nấu ăn, trông trẻ, chăm sóc người cao"
        " tuổi.",
        "Nhà riêng, căn hộ ở thành phố lớn; làm trực tiếp với gia đình hoặc qua công ty cung cấp dịch vụ.",
        "Dọn nhà, giặt giũ, đi chợ nấu ăn, đưa đón và trông trẻ, nhắc người già uống thuốc, hỗ trợ vệ sinh cá nhân.",
        "Ít thời gian riêng nếu ở lại nhà chủ; phụ thuộc tính cách gia đình; nên có hợp đồng rõ ràng để được bảo vệ"
        " quyền lợi.",
        "Nhu cầu tăng ở đô thị và qua chương trình hộ lý, điều dưỡng sang Nhật, Đức.",
        "Đi làm ngay, ít cần vốn. Học thêm kỹ năng chăm sóc người cao tuổi giúp tăng thu nhập và mở đường làm ở"
        " nước ngoài.",
    ),
    "VAN_PHONG_HANH_CHINH": (
        "Hỗ trợ vận hành văn phòng, cửa hàng: đón khách, nhập liệu, thu ngân, giấy tờ hành chính, sổ sách.",
        "Văn phòng công ty, cửa hàng, siêu thị, phòng khám, trường học, cơ quan.",
        "Tiếp khách, nghe điện thoại, nhập dữ liệu vào phần mềm, tính tiền, lưu trữ hồ sơ, soạn văn bản đơn giản.",
        "Công việc lặp lại, thu nhập khởi điểm không cao; sai sót tiền, số liệu phải chịu trách nhiệm.",
        "Phần mềm và AI thay dần việc nhập liệu thuần túy; người biết thêm kế toán, Excel nâng cao sẽ có lợi thế.",
        "Hợp với người cẩn thận, ngăn nắp, thích làm việc trong nhà. Nên học tin học văn phòng và lấy bằng kế toán"
        " nếu muốn đi xa hơn.",
    ),
    "GIAO_DUC_TRO_GIANG": (
        "Hỗ trợ việc dạy và chăm sóc trẻ: trợ giảng, bảo mẫu, gia sư; giáo viên mầm non, tiểu học trực tiếp dạy học.",
        "Trung tâm ngoại ngữ, kỹ năng, nhóm trẻ, trường mầm non, tiểu học, dạy kèm tại nhà.",
        "Chuẩn bị đồ dùng, hỗ trợ giáo viên trên lớp, kèm học sinh yếu, chăm sóc ăn ngủ của trẻ, trao đổi với phụ"
        " huynh.",
        "Cần kiên nhẫn, chịu trách nhiệm an toàn của trẻ; thu nhập khởi điểm thấp. Giáo viên mầm non, tiểu học bắt"
        " buộc có bằng sư phạm chính quy.",
        "Nhu cầu giáo viên mầm non vẫn thiếu; trung tâm ngoại ngữ, kỹ năng mở rộng.",
        "Hợp với người yêu trẻ, thích truyền đạt. Có thể bắt đầu bằng trợ giảng, bảo mẫu rồi học sư phạm để thành"
        " giáo viên.",
    ),
    "HANG_KHONG_HANG_HAI": (
        "Phục vụ vận tải hàng không và đường biển: nhân viên mặt đất, tiếp viên, an ninh sân bay, thuyền viên, sĩ"
        " quan tàu biển, phi công.",
        "Sân bay, hãng hàng không, cảng biển, tàu hàng, tàu du lịch trong nước và quốc tế.",
        "Làm thủ tục, xếp dỡ hàng, phục vụ khách trên chuyến bay; trên tàu biển: vận hành, bảo dưỡng tàu theo ca"
        " trực.",
        "Lịch làm việc theo ca, theo chuyến, xa nhà lâu (thuyền viên nhiều tháng); tuyển chọn khắt khe về sức khỏe,"
        " ngoại hình, tiếng Anh. Phi công, sĩ quan hàng hải phải học chính quy.",
        "Hàng không và vận tải biển phục hồi, thiếu thuyền viên, sĩ quan có chứng chỉ quốc tế.",
        "Thu nhập cao nhưng đòi hỏi tiếng Anh, sức khỏe và đào tạo bắt buộc. Nên chuẩn bị tiếng Anh từ sớm.",
    ),
}

# Nghề cụ thể: (tên nghề, mô tả ngắn, yêu cầu thêm, yêu cầu bằng cấp, bắt buộc đào tạo chính quy).
# Nghề đã có từ migration 0069 (NGHE_CU) chỉ được điền yeu_cau_bang_cap / bat_buoc_dao_tao_chinh_quy nếu đang trống.
NGHE = {
    "CONG_NHAN_SAN_XUAT": [
        ("Công nhân lắp ráp điện tử", None, None, None, None),
        ("Công nhân may công nghiệp", None, None, None, None),
        ("Công nhân vận hành máy", None, None, None, None),
        ("Công nhân kiểm tra chất lượng (QC)", "Kiểm tra sản phẩm theo tiêu chuẩn, phát hiện và báo lỗi trên dây"
         " chuyền.", "Cẩn thận, thị lực tốt", None, None),
        ("Công nhân đóng gói", "Đóng gói, dán nhãn, xếp thành phẩm lên pallet.", None, None, None),
        ("Thợ hàn", "Hàn kết cấu kim loại trong nhà máy cơ khí, đóng tàu, xây dựng.", "Chịu nóng, tuân thủ an toàn",
         "Chứng chỉ thợ hàn (bậc 3G/6G cho vị trí lương cao)", None),
    ],
    "BAN_HANG_DICH_VU": [
        ("Nhân viên bán hàng cửa hàng", None, None, None, None),
        ("Nhân viên tổng đài", None, None, None, None),
        ("Nhân viên kinh doanh thị trường", None, None, None, None),
        ("Nhân viên telesales", "Gọi điện giới thiệu sản phẩm, chăm sóc khách hàng tiềm năng.", "Giọng nói dễ nghe",
         None, None),
        ("Nhân viên chăm sóc khách hàng online", "Trả lời tin nhắn, xử lý đơn và khiếu nại qua mạng xã hội, sàn"
         " thương mại điện tử.", "Đánh máy nhanh", None, None),
        ("Nhân viên tư vấn bảo hiểm", "Tư vấn, bán các gói bảo hiểm nhân thọ, sức khỏe.", "Đủ 18 tuổi",
         "Chứng chỉ đại lý bảo hiểm", None),
    ],
    "GIAO_HANG_VAN_TAI": [
        ("Nhân viên giao hàng", None, None, "Giấy phép lái xe hạng A1 trở lên", None),
        ("Tài xế xe công nghệ", None, None, "Giấy phép lái xe phù hợp (A1 với xe máy, B với ô tô)", None),
        ("Lái xe tải", None, None, "Giấy phép lái xe hạng C trở lên", None),
        ("Lái xe khách", "Chở khách tuyến cố định, xe hợp đồng, xe đưa đón công nhân.", "Có kinh nghiệm lái xe",
         "Giấy phép lái xe hạng D trở lên (đủ tuổi, kinh nghiệm theo quy định)", None),
        ("Lái xe container", "Vận chuyển container giữa cảng, kho và khu công nghiệp.", "Chịu được đi đường dài",
         "Giấy phép lái xe hạng CE", None),
        ("Phụ xe, áp tải hàng", "Hỗ trợ tài xế bốc xếp, áp tải, giao nhận chứng từ.", "Sức khỏe tốt", None, None),
    ],
    "DIEN_CO_KHI": [
        ("Thợ điện dân dụng", None, None, "Chứng chỉ an toàn điện", None),
        ("Thợ sửa chữa điện lạnh", None, None, None, None),
        ("Thợ sửa chữa ô tô, xe máy", None, None, None, None),
        ("Thợ điện công nghiệp", "Lắp đặt, bảo trì tủ điện, động cơ, hệ thống điều khiển trong nhà máy.",
         "Đọc được sơ đồ điện", "Chứng chỉ an toàn điện; sơ cấp hoặc trung cấp nghề điện", None),
        ("Thợ vận hành máy CNC", "Lập trình đơn giản và vận hành máy tiện, phay CNC gia công chi tiết.",
         "Đọc bản vẽ kỹ thuật", None, None),
        ("Thợ sửa chữa điện thoại, máy tính", "Chẩn đoán lỗi, thay linh kiện, cài đặt phần mềm.", "Khéo tay, tỉ mỉ",
         None, None),
        ("Thợ lắp đặt điện mặt trời", "Lắp đặt, bảo trì tấm pin năng lượng mặt trời trên mái nhà, nhà xưởng.",
         "Không sợ độ cao", "Chứng chỉ an toàn điện, an toàn làm việc trên cao", None),
    ],
    "BEP_NHA_HANG": [
        ("Đầu bếp", None, None, None, None),
        ("Nhân viên pha chế (bartender/barista)", None, None, None, None),
        ("Nhân viên phục vụ, lễ tân khách sạn", None, None, None, None),
        ("Phụ bếp", "Sơ chế nguyên liệu, hỗ trợ đầu bếp, giữ vệ sinh khu bếp.", None,
         "Giấy xác nhận kiến thức an toàn thực phẩm (thường do chủ cơ sở lo)", None),
        ("Thợ làm bánh", "Làm bánh mì, bánh ngọt, bánh kem tại tiệm bánh, khách sạn.", "Khéo tay, có gu trang trí",
         None, None),
        ("Nhân viên buồng phòng khách sạn", "Dọn dẹp, chuẩn bị phòng cho khách lưu trú.", "Cẩn thận, trung thực",
         None, None),
    ],
    "LAM_DEP": [
        ("Thợ cắt tóc", None, None, None, None),
        ("Thợ làm nail", None, None, None, None),
        ("Kỹ thuật viên spa", None, None, None, None),
        ("Chuyên viên trang điểm", "Trang điểm cô dâu, sự kiện, chụp ảnh.", "Có gu thẩm mỹ", None, None),
        ("Kỹ thuật viên nối mi", "Nối, uốn mi cho khách tại tiệm, spa.", "Tỉ mỉ, thị lực tốt", None, None),
        ("Thợ phun xăm thẩm mỹ", "Phun mày, môi, mí theo yêu cầu của khách.", "Tay nghề vững, giữ vệ sinh vô trùng",
         "Chứng chỉ nghề phun xăm thẩm mỹ", None),
    ],
    "KY_NANG_SO": [
        ("Thiết kế đồ họa", None, None, None, None),
        ("Lập trình viên web", None, None, None, None),
        ("Nhân viên quảng cáo trực tuyến", None, None, None, None),
        ("Biên tập video", "Dựng, cắt ghép video cho mạng xã hội, quảng cáo, kênh YouTube.",
         "Thành thạo CapCut/Premiere", None, None),
        ("Kiểm thử phần mềm (tester)", "Kiểm tra ứng dụng, website, ghi nhận lỗi để lập trình viên sửa.",
         "Tỉ mỉ, tư duy logic", None, None),
        ("Nhân viên SEO, viết nội dung", "Viết bài, tối ưu nội dung để website lên top tìm kiếm.", "Viết tốt",
         None, None),
    ],
    "KINH_DOANH_ONLINE": [
        ("Chủ shop trên sàn thương mại điện tử", None, None, None, None),
        ("Người livestream bán hàng", None, None, None, None),
        ("Người sáng tạo nội dung", None, None, None, None),
        ("Cộng tác viên tiếp thị liên kết (affiliate)", "Giới thiệu sản phẩm qua đường link, nhận hoa hồng trên đơn"
         " hàng.", "Có kênh mạng xã hội", None, None),
        ("Nhân viên vận hành gian hàng", "Đăng sản phẩm, cập nhật giá, chạy khuyến mãi cho shop trên sàn.",
         "Thành thạo Excel cơ bản", None, None),
        ("Nhiếp ảnh sản phẩm", "Chụp, chỉnh ảnh sản phẩm cho shop online, thương hiệu nhỏ.", "Có máy ảnh hoặc điện"
         " thoại chụp tốt", None, None),
    ],
    "XAY_DUNG_HOAN_THIEN": [
        ("Thợ xây, trát", "Xây tường, trát vữa, làm móng cho nhà ở, công trình.", "Sức khỏe tốt", None, None),
        ("Thợ ốp lát gạch", "Ốp lát gạch nền, tường, cầu thang theo thiết kế.", "Khéo tay, cẩn thận", None, None),
        ("Thợ sơn bả", "Bả matit, sơn tường, sơn chống thấm, sơn trang trí.", None, None, None),
        ("Thợ cốp pha, cốt thép", "Lắp dựng cốp pha, gia công và buộc cốt thép cho dầm, sàn, cột.",
         "Không sợ độ cao", None, None),
        ("Thợ điện nước công trình", "Đi đường ống nước, lắp đặt điện cho nhà ở, công trình.", None,
         "Chứng chỉ an toàn điện", None),
        ("Thợ lắp đặt nhôm kính", "Gia công, lắp cửa nhôm, vách kính, lan can.", "Không sợ độ cao", None, None),
        ("Vận hành máy xúc, máy ủi", "Điều khiển máy thi công đào, san lấp mặt bằng.", "Đủ 18 tuổi",
         "Chứng chỉ vận hành máy thi công (máy xúc, máy ủi)", None),
    ],
    "KHO_VAN_LOGISTICS": [
        ("Nhân viên kho", "Nhận hàng, xếp lên kệ, kiểm đếm tồn kho.", "Chịu được làm ca", None, None),
        ("Nhân viên soạn hàng, đóng gói", "Lấy hàng theo đơn, đóng gói, dán nhãn vận chuyển.", "Nhanh nhẹn",
         None, None),
        ("Lái xe nâng", "Điều khiển xe nâng bốc xếp, di chuyển pallet hàng.", None,
         "Chứng chỉ vận hành xe nâng", None),
        ("Thủ kho", "Quản lý nhập xuất, sổ sách, báo cáo tồn kho.", "Có kinh nghiệm làm kho, dùng Excel", None, None),
        ("Nhân viên điều phối giao nhận", "Sắp xếp tuyến, phân đơn cho tài xế, theo dõi tình trạng giao hàng.",
         "Dùng máy tính tốt", None, None),
        ("Nhân viên khai báo hải quan", "Chuẩn bị chứng từ, khai báo hàng xuất nhập khẩu.", "Tiếng Anh đọc hiểu",
         "Chứng chỉ nghiệp vụ khai hải quan", None),
    ],
    "NONG_NGHIEP_CONG_NGHE": [
        ("Công nhân trồng rau nhà màng, thủy canh", "Gieo trồng, chăm sóc, thu hoạch rau trong nhà màng.", None,
         None, None),
        ("Công nhân chăn nuôi trang trại", "Cho ăn, vệ sinh chuồng, theo dõi sức khỏe vật nuôi.", "Sức khỏe tốt",
         None, None),
        ("Kỹ thuật viên nuôi trồng thủy sản", "Quản lý ao nuôi tôm, cá: nước, thức ăn, phòng bệnh.", None,
         None, None),
        ("Nhân viên vận hành hệ thống tưới tự động", "Cài đặt, theo dõi cảm biến và lịch tưới trên phần mềm.",
         "Biết dùng điện thoại, máy tính", None, None),
        ("Kỹ thuật viên thú y", "Tiêm phòng, chẩn đoán và điều trị bệnh cho vật nuôi.", None,
         "Bằng trung cấp thú y trở lên và chứng chỉ hành nghề thú y", 1),
        ("Người bán nông sản online", "Đưa nông sản của gia đình, hợp tác xã lên sàn, mạng xã hội.",
         "Biết chụp ảnh, làm video", None, None),
    ],
    "DU_LICH_SU_KIEN": [
        ("Hướng dẫn viên du lịch nội địa", "Dẫn đoàn, thuyết minh điểm đến, chăm sóc khách trong tour.",
         "Giọng nói tốt, hiểu biết lịch sử, văn hóa", "Thẻ hướng dẫn viên du lịch nội địa", None),
        ("Nhân viên điều hành tour", "Đặt xe, khách sạn, nhà hàng, xử lý phát sinh trong tour.", None, None, None),
        ("Nhân viên đặt phòng, đặt vé", "Tư vấn và đặt vé máy bay, phòng khách sạn cho khách.", "Tiếng Anh cơ bản",
         None, None),
        ("Nhân viên tổ chức sự kiện", "Chuẩn bị, setup sân khấu, điều phối chương trình sự kiện.",
         "Chịu được làm khuya", None, None),
        ("MC sự kiện, hoạt náo viên", "Dẫn chương trình, khuấy động không khí sự kiện, team building.",
         "Tự tin, giọng tốt", None, None),
        ("Nhân viên cứu hộ bể bơi, bãi biển", "Giám sát an toàn, cứu đuối, sơ cứu cho khách.", "Bơi giỏi",
         "Chứng chỉ cứu hộ, sơ cấp cứu", None),
    ],
    "Y_TE_CHAM_SOC": [
        ("Hộ lý bệnh viện", "Hỗ trợ người bệnh ăn uống, vệ sinh, di chuyển; vệ sinh buồng bệnh.", "Kiên nhẫn",
         None, None),
        ("Nhân viên chăm sóc người cao tuổi", "Chăm sóc sinh hoạt hằng ngày tại viện dưỡng lão hoặc tại nhà.",
         "Kiên nhẫn, sức khỏe tốt", None, None),
        ("Nhân viên bán thuốc (phụ quầy)", "Hỗ trợ bán thuốc, sắp xếp quầy dưới sự phụ trách của dược sĩ.",
         "Cẩn thận", None, None),
        ("Điều dưỡng", "Theo dõi người bệnh, tiêm truyền, thực hiện y lệnh của bác sĩ.", None,
         "Bằng cao đẳng điều dưỡng trở lên và giấy phép hành nghề", 1),
        ("Y sĩ", "Khám, chữa bệnh thông thường ở trạm y tế, phòng khám.", None,
         "Bằng y sĩ và giấy phép hành nghề", 1),
        ("Kỹ thuật viên xét nghiệm", "Lấy mẫu, thực hiện xét nghiệm máu, nước tiểu… tại phòng xét nghiệm.", None,
         "Bằng cao đẳng kỹ thuật xét nghiệm y học trở lên", 1),
        ("Dược sĩ", "Tư vấn, cấp phát thuốc, quản lý nhà thuốc.", None,
         "Bằng dược (cao đẳng trở lên) và chứng chỉ hành nghề dược", 1),
        ("Bác sĩ", "Khám, chẩn đoán và điều trị bệnh.", "Học lực tốt khối Toán, Hóa, Sinh",
         "Bằng bác sĩ (đại học y 6 năm), thực hành và giấy phép hành nghề", 1),
    ],
    "AN_NINH_LUC_LUONG_VU_TRANG": [
        ("Nhân viên bảo vệ", "Tuần tra, kiểm soát ra vào tại tòa nhà, nhà máy, ngân hàng.", "Đủ 18 tuổi, sức khỏe"
         " tốt", "Chứng chỉ nghiệp vụ bảo vệ (công ty dịch vụ bảo vệ đào tạo)", None),
        ("Nhân viên an ninh sự kiện", "Giữ trật tự, kiểm soát vé, bảo vệ khách mời tại sự kiện.", "Cao, khỏe",
         "Chứng chỉ nghiệp vụ bảo vệ", None),
        ("Chiến sĩ nghĩa vụ quân sự, công an", "Thực hiện nghĩa vụ 2 năm (quân đội) hoặc 2 năm (công an) theo luật.",
         "Đạt tiêu chuẩn sức khỏe khi khám tuyển", None, None),
        ("Sĩ quan công an nhân dân", "Bảo vệ an ninh, trật tự, điều tra, cảnh sát giao thông…",
         "Sơ tuyển lý lịch, sức khỏe tại công an địa phương",
         "Bằng tốt nghiệp trường công an nhân dân (học viện, đại học, trung cấp CAND)", 1),
        ("Sĩ quan, quân nhân chuyên nghiệp quân đội", "Chỉ huy, huấn luyện, làm công tác kỹ thuật trong quân đội.",
         "Sơ tuyển sức khỏe, lý lịch tại ban chỉ huy quân sự",
         "Bằng tốt nghiệp trường quân đội (học viện, trường sĩ quan, cao đẳng, trung cấp kỹ thuật)", 1),
        ("Cảnh sát phòng cháy, chữa cháy và cứu nạn", "Chữa cháy, cứu nạn, cứu hộ, kiểm tra an toàn phòng cháy.",
         "Sức khỏe rất tốt", "Bằng tốt nghiệp trường đào tạo phòng cháy chữa cháy của Bộ Công an", 1),
    ],
    "CHAM_SOC_GIA_DINH": [
        ("Giúp việc gia đình", "Dọn dẹp, giặt giũ, nấu ăn, ở lại nhà chủ.", "Trung thực, chăm chỉ", None, None),
        ("Giúp việc theo giờ", "Dọn dẹp, nấu ăn theo ca, làm nhiều nhà trong ngày.", "Có xe máy", None, None),
        ("Bảo mẫu, trông trẻ tại nhà", "Chăm sóc ăn ngủ, vui chơi, đưa đón trẻ.", "Yêu trẻ, kiên nhẫn", None, None),
        ("Chăm sóc người cao tuổi tại nhà", "Hỗ trợ sinh hoạt, nhắc uống thuốc, đi khám cùng người già.",
         "Kiên nhẫn, sức khỏe tốt", None, None),
        ("Nhân viên vệ sinh công nghiệp", "Vệ sinh tòa nhà, văn phòng, trung tâm thương mại theo ca.", None,
         None, None),
        ("Đầu bếp gia đình", "Nấu ăn hằng ngày cho gia đình theo khẩu vị, chế độ dinh dưỡng.", "Nấu ăn ngon",
         None, None),
    ],
    "VAN_PHONG_HANH_CHINH": [
        ("Lễ tân văn phòng", "Đón khách, nghe điện thoại, nhận thư, đặt phòng họp.", "Giao tiếp tốt, ngoại hình gọn"
         " gàng", None, None),
        ("Nhân viên nhập liệu", "Nhập dữ liệu vào phần mềm, kiểm tra và đối chiếu số liệu.", "Đánh máy nhanh",
         None, None),
        ("Thu ngân siêu thị, cửa hàng", "Tính tiền, thanh toán thẻ, đối chiếu tiền cuối ca.", "Cẩn thận, trung thực",
         None, None),
        ("Trợ lý hành chính", "Soạn văn bản, sắp xếp lịch, chuẩn bị tài liệu, mua văn phòng phẩm.",
         "Thành thạo Word, Excel", None, None),
        ("Nhân viên văn thư, lưu trữ", "Quản lý công văn đến, đi, lưu trữ hồ sơ.", "Ngăn nắp", None, None),
        ("Nhân viên kế toán", "Ghi chép chứng từ, lập báo cáo, kê khai thuế cho doanh nghiệp nhỏ.",
         "Thành thạo Excel, phần mềm kế toán", "Bằng trung cấp kế toán trở lên", None),
    ],
    "GIAO_DUC_TRO_GIANG": [
        ("Trợ giảng tiếng Anh", "Hỗ trợ giáo viên trên lớp, chấm bài, kèm học sinh.", "Tiếng Anh tốt", None, None),
        ("Bảo mẫu nhóm trẻ", "Chăm sóc ăn ngủ, vệ sinh cho trẻ ở nhóm trẻ, trường mầm non.", "Yêu trẻ",
         "Chứng chỉ bồi dưỡng chăm sóc trẻ (thường được yêu cầu)", None),
        ("Gia sư", "Dạy kèm học sinh tại nhà hoặc online.", "Học lực tốt môn dạy", None, None),
        ("Huấn luyện viên thể thao, kỹ năng cho trẻ", "Dạy bơi, võ, kỹ năng sống cho trẻ ở trung tâm.",
         "Giỏi môn mình dạy", "Chứng chỉ chuyên môn của môn thể thao, kỹ năng", None),
        ("Giáo viên mầm non", "Tổ chức hoạt động học, chơi, chăm sóc trẻ 3-6 tuổi.", None,
         "Bằng cao đẳng sư phạm mầm non trở lên", 1),
        ("Giáo viên tiểu học", "Dạy các môn ở bậc tiểu học, chủ nhiệm lớp.", None,
         "Bằng cử nhân sư phạm (đại học) trở lên", 1),
    ],
    "HANG_KHONG_HANG_HAI": [
        ("Nhân viên phục vụ mặt đất sân bay", "Làm thủ tục check-in, hướng dẫn hành khách, xử lý hành lý.",
         "Tiếng Anh giao tiếp", None, None),
        ("Nhân viên khai thác hàng hóa sân bay", "Tiếp nhận, kiểm tra, xếp dỡ hàng hóa hàng không.", "Sức khỏe tốt",
         None, None),
        ("Nhân viên an ninh hàng không", "Soi chiếu hành lý, kiểm tra an ninh hành khách.", "Đạt tiêu chuẩn sức khỏe",
         "Chứng chỉ nghiệp vụ an ninh hàng không", None),
        ("Tiếp viên hàng không", "Phục vụ, đảm bảo an toàn cho hành khách trên chuyến bay.",
         "Chiều cao, ngoại hình, tiếng Anh tốt", "Chứng chỉ chuyên môn tiếp viên do hãng hàng không đào tạo", None),
        ("Thủy thủ, thuyền viên tàu biển", "Trực ca, bảo dưỡng, làm hàng trên tàu.", "Chịu được xa nhà dài ngày",
         "Chứng chỉ chuyên môn thuyền viên và sổ thuyền viên", None),
        ("Sĩ quan hàng hải", "Điều khiển, quản lý vận hành tàu biển.", "Tiếng Anh tốt",
         "Bằng cao đẳng/đại học hàng hải và giấy chứng nhận khả năng chuyên môn", 1),
        ("Phi công", "Điều khiển máy bay thương mại.", "Sức khỏe hạng 1, tiếng Anh tốt",
         "Bằng phi công thương mại do cơ sở đào tạo được cấp phép", 1),
    ],
}

# Nghề đã có từ migration 0069: downgrade không xóa các nghề này.
NGHE_CU = {
    "Công nhân lắp ráp điện tử", "Công nhân may công nghiệp", "Công nhân vận hành máy",
    "Nhân viên bán hàng cửa hàng", "Nhân viên tổng đài", "Nhân viên kinh doanh thị trường",
    "Nhân viên giao hàng", "Tài xế xe công nghệ", "Lái xe tải",
    "Thợ điện dân dụng", "Thợ sửa chữa điện lạnh", "Thợ sửa chữa ô tô, xe máy",
    "Đầu bếp", "Nhân viên pha chế (bartender/barista)", "Nhân viên phục vụ, lễ tân khách sạn",
    "Thợ cắt tóc", "Thợ làm nail", "Kỹ thuật viên spa",
    "Thiết kế đồ họa", "Lập trình viên web", "Nhân viên quảng cáo trực tuyến",
    "Chủ shop trên sàn thương mại điện tử", "Người livestream bán hàng", "Người sáng tạo nội dung",
}

# Điểm phù hợp tiêu chí gợi ý (1-5) cho nhóm mới: (mã tiêu chí, điểm, ghi chú).
TIEU_CHI = {
    "XAY_DUNG_HOAN_THIEN": [
        ("THICH_VAN_DONG", 5, None), ("SUC_KHOE_TOT", 5, "Làm ngoài trời, trên cao"), ("KHEO_TAY", 4, None),
        ("CAN_THU_NHAP_NGAY", 4, None), ("IT_VON", 5, None), ("MUON_TU_LAM_CHU", 3, "Lên thợ cả có thể nhận khoán"),
    ],
    "KHO_VAN_LOGISTICS": [
        ("THICH_VAN_DONG", 4, None), ("SUC_KHOE_TOT", 4, "Làm ca, bê vác"), ("CAN_THU_NHAP_NGAY", 5, None),
        ("IT_VON", 5, None), ("MUON_ON_DINH", 4, None),
    ],
    "NONG_NGHIEP_CONG_NGHE": [
        ("THICH_VAN_DONG", 4, None), ("SUC_KHOE_TOT", 4, None), ("TU_HOC_TOT", 3, None), ("MUON_ON_DINH", 3, None),
        ("MUON_TU_LAM_CHU", 5, "Có thể làm chủ trang trại"),
    ],
    "DU_LICH_SU_KIEN": [
        ("THICH_GIAO_TIEP", 5, None), ("THICH_SANG_TAO", 3, None), ("SUC_KHOE_TOT", 4, "Đi lại nhiều"),
        ("TU_HOC_TOT", 4, "Ngoại ngữ, kiến thức điểm đến"), ("CAN_THU_NHAP_NGAY", 3, None),
    ],
    "Y_TE_CHAM_SOC": [
        ("THICH_GIAO_TIEP", 4, None), ("SUC_KHOE_TOT", 4, "Trực đêm"), ("KHEO_TAY", 4, None),
        ("TU_HOC_TOT", 4, "Nghề cần bằng cấp phải học nhiều năm"), ("MUON_ON_DINH", 5, None),
    ],
    "AN_NINH_LUC_LUONG_VU_TRANG": [
        ("THICH_VAN_DONG", 5, None), ("SUC_KHOE_TOT", 5, "Có tiêu chuẩn sức khỏe, chiều cao"),
        ("CAN_THU_NHAP_NGAY", 3, "Bảo vệ đi làm được ngay"), ("MUON_ON_DINH", 5, "Công an, quân đội"),
    ],
    "CHAM_SOC_GIA_DINH": [
        ("THICH_GIAO_TIEP", 3, None), ("SUC_KHOE_TOT", 4, None), ("KHEO_TAY", 3, None),
        ("CAN_THU_NHAP_NGAY", 5, None), ("IT_VON", 5, None),
    ],
    "VAN_PHONG_HANH_CHINH": [
        ("THICH_GIAO_TIEP", 3, None), ("THICH_CONG_NGHE", 3, "Tin học văn phòng"), ("TU_HOC_TOT", 3, None),
        ("IT_VON", 4, None), ("MUON_ON_DINH", 4, None),
    ],
    "GIAO_DUC_TRO_GIANG": [
        ("THICH_GIAO_TIEP", 5, None), ("THICH_SANG_TAO", 3, None), ("TU_HOC_TOT", 4, None), ("MUON_ON_DINH", 4, None),
    ],
    "HANG_KHONG_HANG_HAI": [
        ("THICH_GIAO_TIEP", 4, None), ("SUC_KHOE_TOT", 5, "Tiêu chuẩn sức khỏe của ngành"),
        ("TU_HOC_TOT", 4, "Tiếng Anh"), ("MUON_ON_DINH", 3, None),
    ],
}

_NHOM = sa.table(
    "dm_nhom_nghe_di_lam",
    sa.column("id", sa.Integer),
    sa.column("ma_nhom", sa.String),
    sa.column("trang_thai", sa.Integer),
    *[sa.column(ten) for ten in NHOM_MOI[0] if ten != "ma_nhom"],
    *[sa.column(ten, sa.Text) for ten in COT_GIOI_THIEU],
)
_NGHE = sa.table(
    "dm_nghe_cu_the_di_lam",
    sa.column("id", sa.Integer),
    sa.column("nhom_nghe_di_lam_id", sa.Integer),
    sa.column("ten_nghe", sa.String),
    sa.column("mo_ta_ngan", sa.Text),
    sa.column("yeu_cau_them", sa.String),
    sa.column("yeu_cau_bang_cap", sa.String),
    sa.column("bat_buoc_dao_tao_chinh_quy", sa.Integer),
)
_TIEU_CHI = sa.table("dm_tieu_chi_goi_y", sa.column("id", sa.Integer), sa.column("ma_tieu_chi", sa.String))
_NHOM_TIEU_CHI = sa.table(
    "dm_nhom_nghe_tieu_chi",
    sa.column("nhom_nghe_di_lam_id", sa.Integer),
    sa.column("tieu_chi_goi_y_id", sa.Integer),
    sa.column("diem_phu_hop", sa.Integer),
    sa.column("ghi_chu", sa.String),
)


def _co_cot(bang: str, cot: str) -> bool:
    return cot in {c["name"] for c in sa.inspect(op.get_bind()).get_columns(bang)}


def _id_nhom(conn) -> dict[str, int]:
    return {ma: id_ for id_, ma in conn.execute(sa.select(_NHOM.c.id, _NHOM.c.ma_nhom))}


def upgrade() -> None:
    for cot in COT_GIOI_THIEU:
        if not _co_cot("dm_nhom_nghe_di_lam", cot):
            op.add_column("dm_nhom_nghe_di_lam", sa.Column(cot, sa.Text(), nullable=True))
    if not _co_cot("dm_nghe_cu_the_di_lam", "yeu_cau_bang_cap"):
        op.add_column(
            "dm_nghe_cu_the_di_lam",
            sa.Column("yeu_cau_bang_cap", sa.String(255), nullable=True,
                      comment="Bằng cấp / chứng chỉ bắt buộc để hành nghề; null = không yêu cầu"),
        )
    if not _co_cot("dm_nghe_cu_the_di_lam", "bat_buoc_dao_tao_chinh_quy"):
        op.add_column(
            "dm_nghe_cu_the_di_lam",
            sa.Column("bat_buoc_dao_tao_chinh_quy", TINYINT(), nullable=True,
                      comment="1 = bắt buộc đào tạo chính quy; null = không"),
        )

    conn = op.get_bind()

    # Nhóm mới (bỏ qua nếu mã nhóm đã có).
    co_san = _id_nhom(conn)
    for nhom in NHOM_MOI:
        if nhom["ma_nhom"] not in co_san:
            conn.execute(_NHOM.insert().values(**nhom, trang_thai=1))
    id_nhom = _id_nhom(conn)

    # Mục giới thiệu: chỉ điền ô đang trống, không ghi đè nội dung quản trị đã sửa.
    for ma_nhom, gia_tri in GIOI_THIEU.items():
        if ma_nhom not in id_nhom:
            continue
        for cot, noi_dung in zip(COT_GIOI_THIEU, gia_tri, strict=True):
            conn.execute(
                _NHOM.update()
                .where(_NHOM.c.id == id_nhom[ma_nhom], _NHOM.c[cot].is_(None))
                .values({cot: noi_dung})
            )

    # Nghề cụ thể: thêm nếu chưa có (theo nhóm + tên), nghề đã có chỉ điền yêu cầu bằng cấp / chính quy còn trống.
    for ma_nhom, ds_nghe in NGHE.items():
        nhom_id = id_nhom.get(ma_nhom)
        if nhom_id is None:
            continue
        for ten, mo_ta, yeu_cau_them, bang_cap, chinh_quy in ds_nghe:
            nghe_id = conn.scalar(
                sa.select(_NGHE.c.id).where(_NGHE.c.nhom_nghe_di_lam_id == nhom_id, _NGHE.c.ten_nghe == ten)
            )
            if nghe_id is None:
                conn.execute(_NGHE.insert().values(
                    nhom_nghe_di_lam_id=nhom_id, ten_nghe=ten, mo_ta_ngan=mo_ta, yeu_cau_them=yeu_cau_them,
                    yeu_cau_bang_cap=bang_cap, bat_buoc_dao_tao_chinh_quy=chinh_quy,
                ))
                continue
            if bang_cap:
                conn.execute(_NGHE.update().where(_NGHE.c.id == nghe_id, _NGHE.c.yeu_cau_bang_cap.is_(None))
                             .values(yeu_cau_bang_cap=bang_cap))
            if chinh_quy:
                conn.execute(_NGHE.update().where(_NGHE.c.id == nghe_id, _NGHE.c.bat_buoc_dao_tao_chinh_quy.is_(None))
                             .values(bat_buoc_dao_tao_chinh_quy=chinh_quy))

    # Điểm tiêu chí gợi ý cho nhóm mới (bỏ qua tiêu chí không tồn tại hoặc cặp đã có).
    id_tieu_chi = {ma: id_ for id_, ma in conn.execute(sa.select(_TIEU_CHI.c.id, _TIEU_CHI.c.ma_tieu_chi))}
    for ma_nhom, ds in TIEU_CHI.items():
        nhom_id = id_nhom.get(ma_nhom)
        if nhom_id is None:
            continue
        for ma_tieu_chi, diem, ghi_chu in ds:
            tieu_chi_id = id_tieu_chi.get(ma_tieu_chi)
            if tieu_chi_id is None:
                continue
            da_co = conn.scalar(sa.select(sa.func.count()).select_from(_NHOM_TIEU_CHI).where(
                _NHOM_TIEU_CHI.c.nhom_nghe_di_lam_id == nhom_id, _NHOM_TIEU_CHI.c.tieu_chi_goi_y_id == tieu_chi_id,
            ))
            if not da_co:
                conn.execute(_NHOM_TIEU_CHI.insert().values(
                    nhom_nghe_di_lam_id=nhom_id, tieu_chi_goi_y_id=tieu_chi_id, diem_phu_hop=diem, ghi_chu=ghi_chu,
                ))


def downgrade() -> None:
    conn = op.get_bind()
    id_nhom = _id_nhom(conn)
    ids_moi = [id_nhom[n["ma_nhom"]] for n in NHOM_MOI if n["ma_nhom"] in id_nhom]
    if ids_moi:
        conn.execute(_NHOM_TIEU_CHI.delete().where(_NHOM_TIEU_CHI.c.nhom_nghe_di_lam_id.in_(ids_moi)))
        conn.execute(_NGHE.delete().where(_NGHE.c.nhom_nghe_di_lam_id.in_(ids_moi)))
        conn.execute(_NHOM.delete().where(_NHOM.c.id.in_(ids_moi)))
    # Nghề thêm vào các nhóm cũ.
    for ma_nhom, ds_nghe in NGHE.items():
        nhom_id = id_nhom.get(ma_nhom)
        ten_moi = [ten for ten, *_ in ds_nghe if ten not in NGHE_CU]
        if nhom_id is not None and ten_moi:
            conn.execute(_NGHE.delete().where(_NGHE.c.nhom_nghe_di_lam_id == nhom_id, _NGHE.c.ten_nghe.in_(ten_moi)))

    for cot in ("bat_buoc_dao_tao_chinh_quy", "yeu_cau_bang_cap"):
        if _co_cot("dm_nghe_cu_the_di_lam", cot):
            op.drop_column("dm_nghe_cu_the_di_lam", cot)
    for cot in reversed(COT_GIOI_THIEU):
        if _co_cot("dm_nhom_nghe_di_lam", cot):
            op.drop_column("dm_nhom_nghe_di_lam", cot)
