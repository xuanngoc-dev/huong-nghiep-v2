"""Dữ liệu mẫu danh mục hướng đi sau THCS: hướng đi, ưu/nhược điểm, tiêu chí, điểm phù hợp, lời khuyên lưu ý.

Liên kết tra theo mã (ma_huong, ma_tieu_chi), không gán id cứng. Hướng đi hoặc tiêu chí đã có mã trong bảng thì bỏ qua
(hướng đi đã có thì bỏ qua cả dữ liệu con của nó). Chi phí tính theo VNĐ/tháng; số liệu là tham khảo.

Revision ID: 20261204_0077
Revises: 20261203_0076
Create Date: 2026-12-04 10:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "20261204_0077"
down_revision = "20261203_0076"
branch_labels = None
depends_on = None

# (ma_huong, ten_huong, mo_ta_tong_quan, doi_tuong_phu_hop, chi_phi_du_kien_text, chi_phi_min, chi_phi_max,
#  muc_do_ap_luc_hoc_tap, muc_do_tu_giac_can_thiet, tinh_linh_hoat_sau_lop_12, ma_holland, thu_tu_hien_thi)
HUONG_DI = [
    (
        "THPT_CONG_LAP", "THPT công lập",
        "Thi tuyển vào lớp 10 trường THPT công lập, học chương trình giáo dục phổ thông 3 năm, thi tốt nghiệp THPT "
        "và xét tuyển đại học, cao đẳng. Là lựa chọn phổ biến nhất, học phí thấp nhưng cạnh tranh đầu vào cao ở "
        "các thành phố lớn.",
        "Học sinh có học lực khá trở lên, đủ điểm thi vào lớp 10 tại trường gần nhà; muốn giữ ngưỡng cửa đại học "
        "rộng mở nhưng chưa xác định rõ ngành nghề.",
        "0,5 - 2 triệu VNĐ/tháng (học phí, học thêm, sách vở)", 500000, 2000000,
        "cao", "cao",
        "Rất linh hoạt: thi đại học, cao đẳng, du học, học nghề hoặc đi làm đều được; bằng THPT là điều kiện "
        "của hầu hết các lựa chọn sau này.",
        "ISC", 1,
    ),
    (
        "THPT_CHUYEN", "THPT chuyên",
        "Thi tuyển vào lớp chuyên (Toán, Lý, Hóa, Văn, Anh...) của trường chuyên tỉnh hoặc trường chuyên thuộc "
        "đại học. Chương trình nâng cao, hướng tới thi học sinh giỏi và các trường đại học top đầu.",
        "Học sinh giỏi, có năng khiếu nổi bật ở một môn, chịu được cường độ học cao và thích cạnh tranh học thuật.",
        "1 - 4 triệu VNĐ/tháng (học phí thấp, chi phí học thêm, ôn đội tuyển)", 1000000, 4000000,
        "cao", "rat_cao",
        "Rộng mở nhất: được ưu tiên xét tuyển thẳng, học bổng du học, các chương trình tài năng; vẫn có thể "
        "chuyển sang hướng khác nếu không phù hợp.",
        "IAE", 2,
    ),
    (
        "THPT_TU_THUC", "THPT tư thục, dân lập",
        "Học chương trình THPT tại trường ngoài công lập; điểm đầu vào thấp hơn hoặc xét học bạ, lớp ít học sinh, "
        "nhiều trường có thêm chương trình tiếng Anh, kỹ năng sống.",
        "Học sinh không đỗ hoặc không muốn cạnh tranh vào công lập, gia đình có điều kiện tài chính, muốn môi "
        "trường quan tâm sát sao hơn.",
        "3 - 10 triệu VNĐ/tháng (tùy trường)", 3000000, 10000000,
        "trung_binh", "cao",
        "Giống THPT công lập: nhận bằng tốt nghiệp THPT, thi hoặc xét tuyển đại học, cao đẳng, du học.",
        "SEC", 3,
    ),
    (
        "THPT_QUOC_TE", "Chương trình song bằng, quốc tế",
        "Học tại trường quốc tế hoặc chương trình song bằng (Cambridge, IB, Mỹ, Úc...) kết hợp chương trình Việt "
        "Nam; giảng dạy chủ yếu bằng tiếng Anh, hướng tới du học.",
        "Học sinh có nền tảng tiếng Anh tốt, gia đình có định hướng du học và khả năng tài chính cao.",
        "15 - 60 triệu VNĐ/tháng", 15000000, 60000000,
        "trung_binh", "rat_cao",
        "Thuận lợi du học hoặc vào chương trình quốc tế trong nước; cần lưu ý điều kiện công nhận bằng nếu "
        "muốn thi đại học trong nước.",
        "AES", 4,
    ),
    (
        "GDNN_GDTX", "Trung tâm GDNN - GDTX",
        "Học chương trình giáo dục thường xuyên cấp THPT (văn hóa) tại Trung tâm Giáo dục nghề nghiệp - Giáo dục "
        "thường xuyên, thường kết hợp học một nghề ngắn hạn. Không thi tuyển, học buổi ngắn hơn THPT.",
        "Học sinh học lực trung bình, không thi vào lớp 10 công lập, cần thời gian linh hoạt để vừa học vừa "
        "phụ giúp gia đình hoặc học nghề.",
        "0,3 - 1,5 triệu VNĐ/tháng", 300000, 1500000,
        "thap", "cao",
        "Nhận bằng tốt nghiệp THPT (hệ GDTX), vẫn được xét tuyển đại học, cao đẳng; có thêm chứng chỉ nghề nếu "
        "học kết hợp.",
        "RCS", 5,
    ),
    (
        "TRUNG_CAP_9_PLUS", "Trung cấp nghề (mô hình 9+)",
        "Vào thẳng trường trung cấp, cao đẳng sau lớp 9: học nghề (cơ khí, điện, ô tô, CNTT, du lịch, chăm sóc "
        "sắc đẹp...) song song với văn hóa THPT. Học phí được miễn hoặc hỗ trợ theo chính sách.",
        "Học sinh thích thực hành, muốn có nghề và đi làm sớm; học lực trung bình hoặc khá nhưng không mặn mà "
        "với con đường thi cử học thuật.",
        "0 - 1,5 triệu VNĐ/tháng (nhiều trường miễn học phí cho học sinh tốt nghiệp THCS)", 0, 1500000,
        "trung_binh", "cao",
        "Ra trường có bằng trung cấp, có thể liên thông lên cao đẳng, đại học; học đủ văn hóa thì được thi tốt "
        "nghiệp THPT để mở rộng lựa chọn.",
        "RCE", 6,
    ),
    (
        "HOC_NGHE_NGAN_HAN", "Học nghề ngắn hạn, đi làm sớm",
        "Học các khóa nghề sơ cấp 3 - 12 tháng (may, sửa xe, điện dân dụng, làm bánh, cắt tóc...) hoặc học việc "
        "tại cơ sở, sau đó đi làm ngay.",
        "Học sinh có hoàn cảnh khó khăn cần đi làm sớm, đã xác định rõ nghề muốn theo, hoặc không muốn tiếp tục "
        "học văn hóa.",
        "1 - 3 triệu VNĐ/tháng trong thời gian học", 1000000, 3000000,
        "thap", "trung_binh",
        "Kém linh hoạt nhất: muốn học tiếp lên cao cần học bổ túc văn hóa; bù lại có thu nhập và kinh nghiệm "
        "sớm.",
        "RCE", 7,
    ),
]

# (ma_tieu_chi, ten_tieu_chi, mo_ta_tieu_chi, nhom_tieu_chi, thu_tu_hien_thi)
TIEU_CHI = [
    ("HOC_LUC", "Học lực lớp 9", "Kết quả học tập và khả năng đạt điểm cao trong kỳ thi vào lớp 10", "Năng lực", 1),
    ("NANG_KHIEU_MON", "Năng khiếu một môn học", "Có thế mạnh nổi bật, từng đạt giải học sinh giỏi một môn",
     "Năng lực", 2),
    ("NGOAI_NGU", "Nền tảng ngoại ngữ", "Khả năng tiếng Anh hiện tại để theo chương trình dạy bằng tiếng Anh",
     "Năng lực", 3),
    ("THICH_THUC_HANH", "Thích thực hành, làm bằng tay", "Thích làm ra sản phẩm cụ thể hơn là học lý thuyết",
     "Sở thích", 4),
    ("MUC_TIEU_DAI_HOC", "Mục tiêu học đại học", "Gia đình và học sinh muốn hướng tới bằng đại học", "Định hướng", 5),
    ("DI_LAM_SOM", "Nhu cầu đi làm sớm", "Cần có thu nhập hoặc muốn tự lập sớm", "Định hướng", 6),
    ("TAI_CHINH", "Khả năng tài chính gia đình", "Mức chi phí học tập gia đình có thể chi trả hằng tháng",
     "Hoàn cảnh", 7),
    ("TU_GIAC", "Tính tự giác, chịu áp lực", "Tự học, giữ kỷ luật và chịu được áp lực thi cử", "Tính cách", 8),
]

# Điểm phù hợp 1-5 theo thứ tự cột TIEU_CHI.
_DIEM = {
    "THPT_CONG_LAP": (4, 3, 3, 2, 5, 2, 4, 4),
    "THPT_CHUYEN": (5, 5, 4, 2, 5, 1, 3, 5),
    "THPT_TU_THUC": (3, 2, 3, 2, 4, 2, 2, 3),
    "THPT_QUOC_TE": (4, 3, 5, 2, 5, 1, 1, 4),
    "GDNN_GDTX": (2, 1, 2, 3, 3, 4, 5, 3),
    "TRUNG_CAP_9_PLUS": (2, 2, 2, 5, 2, 5, 5, 3),
    "HOC_NGHE_NGAN_HAN": (1, 1, 1, 5, 1, 5, 4, 2),
}

# Nhận định tư vấn cho những cặp đáng nói; cặp còn lại để trống.
_NHAN_DINH = {
    ("THPT_CONG_LAP", "HOC_LUC"): "Cần điểm thi vào 10 đủ chuẩn trường mong muốn, nên chọn nguyện vọng vừa sức",
    ("THPT_CONG_LAP", "TAI_CHINH"): "Chi phí thấp, phù hợp đa số gia đình",
    ("THPT_CHUYEN", "NANG_KHIEU_MON"): "Điều kiện gần như bắt buộc để đỗ và theo kịp lớp chuyên",
    ("THPT_CHUYEN", "TU_GIAC"): "Áp lực rất cao, cần tự học tốt và tinh thần vững",
    ("THPT_TU_THUC", "TAI_CHINH"): "Cần cân đối học phí suốt 3 năm trước khi chọn",
    ("THPT_QUOC_TE", "NGOAI_NGU"): "Học chủ yếu bằng tiếng Anh, nền tảng yếu sẽ rất vất vả",
    ("THPT_QUOC_TE", "TAI_CHINH"): "Chi phí cao nhất, chỉ phù hợp gia đình có điều kiện",
    ("GDNN_GDTX", "TAI_CHINH"): "Chi phí thấp, thời gian học linh hoạt",
    ("TRUNG_CAP_9_PLUS", "THICH_THUC_HANH"): "Rất phù hợp: thời lượng thực hành chiếm phần lớn chương trình",
    ("TRUNG_CAP_9_PLUS", "DI_LAM_SOM"): "Có nghề và bằng trung cấp sau khoảng 2 - 3 năm",
    ("HOC_NGHE_NGAN_HAN", "MUC_TIEU_DAI_HOC"): "Không phù hợp nếu vẫn muốn học đại học",
    ("HOC_NGHE_NGAN_HAN", "DI_LAM_SOM"): "Có thu nhập nhanh nhất, sau vài tháng học",
}

# (ma_huong, loai, tieu_de, noi_dung_chi_tiet, thu_tu_hien_thi)
UU_NHUOC_DIEM = [
    ("THPT_CONG_LAP", "uu_diem", "Học phí thấp",
     "Được nhà nước hỗ trợ học phí, chi phí chủ yếu là học thêm và sách vở.", 1),
    ("THPT_CONG_LAP", "uu_diem", "Mở rộng mọi lựa chọn sau lớp 12",
     "Bằng THPT là điều kiện để thi đại học, cao đẳng, du học hay học nghề trình độ cao.", 2),
    ("THPT_CONG_LAP", "uu_diem", "Môi trường bạn bè đa dạng",
     "Học cùng bạn bè gần nhà, phát triển kỹ năng giao tiếp và hoạt động ngoại khóa.", 3),
    ("THPT_CONG_LAP", "nhuoc_diem", "Cạnh tranh đầu vào cao",
     "Ở các thành phố lớn, tỷ lệ chọi vào lớp 10 công lập cao, áp lực ôn thi từ lớp 9.", 1),
    ("THPT_CONG_LAP", "nhuoc_diem", "Sĩ số lớp đông",
     "Giáo viên khó kèm sát từng học sinh, học sinh yếu dễ bị hổng kiến thức.", 2),

    ("THPT_CHUYEN", "uu_diem", "Môi trường học thuật hàng đầu",
     "Giáo viên giỏi, bạn bè cùng chí hướng, nhiều cơ hội thi học sinh giỏi quốc gia, quốc tế.", 1),
    ("THPT_CHUYEN", "uu_diem", "Lợi thế xét tuyển, học bổng",
     "Được ưu tiên xét tuyển ở nhiều trường đại học top đầu và các chương trình học bổng du học.", 2),
    ("THPT_CHUYEN", "nhuoc_diem", "Áp lực rất lớn",
     "Lượng kiến thức nặng, cạnh tranh liên tục; học sinh dễ căng thẳng, mất cân bằng.", 1),
    ("THPT_CHUYEN", "nhuoc_diem", "Học lệch",
     "Tập trung quá nhiều vào môn chuyên có thể làm yếu các môn khác và kỹ năng mềm.", 2),

    ("THPT_TU_THUC", "uu_diem", "Lớp ít học sinh, quan tâm sát",
     "Giáo viên theo dõi từng học sinh, liên lạc thường xuyên với phụ huynh.", 1),
    ("THPT_TU_THUC", "uu_diem", "Đầu vào nhẹ nhàng",
     "Xét học bạ hoặc điểm chuẩn thấp, giảm áp lực thi vào lớp 10.", 2),
    ("THPT_TU_THUC", "nhuoc_diem", "Chi phí cao",
     "Học phí cao hơn nhiều so với công lập, kèm các khoản bán trú, xe đưa đón.", 1),
    ("THPT_TU_THUC", "nhuoc_diem", "Chất lượng không đồng đều",
     "Cần tìm hiểu kỹ uy tín, kết quả tốt nghiệp của trường trước khi chọn.", 2),

    ("THPT_QUOC_TE", "uu_diem", "Sẵn sàng du học",
     "Ngoại ngữ, phương pháp học và chứng chỉ quốc tế giúp chuyển tiếp du học dễ dàng.", 1),
    ("THPT_QUOC_TE", "uu_diem", "Phát triển toàn diện",
     "Chú trọng tư duy phản biện, dự án, hoạt động ngoại khóa và kỹ năng mềm.", 2),
    ("THPT_QUOC_TE", "nhuoc_diem", "Chi phí rất cao",
     "Học phí và các khoản phụ thu lớn, kéo dài nhiều năm.", 1),
    ("THPT_QUOC_TE", "nhuoc_diem", "Khó quay lại hệ thống trong nước",
     "Kiến thức khác chương trình Việt Nam, bất lợi nếu đổi ý muốn thi đại học trong nước.", 2),

    ("GDNN_GDTX", "uu_diem", "Không thi tuyển, thời gian linh hoạt",
     "Học ít buổi hơn, có thể vừa học vừa làm hoặc học thêm một nghề.", 1),
    ("GDNN_GDTX", "uu_diem", "Vẫn có bằng THPT",
     "Tốt nghiệp được dùng để xét tuyển đại học, cao đẳng như bằng THPT chính quy.", 2),
    ("GDNN_GDTX", "nhuoc_diem", "Môi trường thiếu động lực",
     "Ít hoạt động phong trào, học sinh dễ chểnh mảng nếu không tự giác.", 1),
    ("GDNN_GDTX", "nhuoc_diem", "Định kiến xã hội",
     "Một số người vẫn đánh giá thấp hệ GDTX dù bằng cấp có giá trị pháp lý.", 2),

    ("TRUNG_CAP_9_PLUS", "uu_diem", "Có nghề sớm",
     "Ra trường ở tuổi 18 - 19 đã có tay nghề và bằng trung cấp để đi làm.", 1),
    ("TRUNG_CAP_9_PLUS", "uu_diem", "Miễn, giảm học phí",
     "Học sinh tốt nghiệp THCS vào trung cấp được miễn học phí theo quy định.", 2),
    ("TRUNG_CAP_9_PLUS", "uu_diem", "Liên thông lên cao",
     "Có thể liên thông lên cao đẳng, đại học khi có nhu cầu.", 3),
    ("TRUNG_CAP_9_PLUS", "nhuoc_diem", "Chọn nghề sớm",
     "Ở tuổi 15 nhiều em chưa hiểu rõ sở thích, dễ chọn sai nghề.", 1),
    ("TRUNG_CAP_9_PLUS", "nhuoc_diem", "Học văn hóa song song vất vả",
     "Muốn có bằng THPT phải học thêm văn hóa, lịch học dày.", 2),

    ("HOC_NGHE_NGAN_HAN", "uu_diem", "Có thu nhập nhanh",
     "Chỉ sau vài tháng học đã có thể đi làm, phụ giúp gia đình.", 1),
    ("HOC_NGHE_NGAN_HAN", "uu_diem", "Chi phí thấp, thời gian ngắn",
     "Không mất nhiều năm học, phù hợp gia đình khó khăn.", 2),
    ("HOC_NGHE_NGAN_HAN", "nhuoc_diem", "Hạn chế thăng tiến",
     "Thiếu bằng cấp, khó lên vị trí quản lý hoặc chuyển nghề sau này.", 1),
    ("HOC_NGHE_NGAN_HAN", "nhuoc_diem", "Đi làm khi còn nhỏ tuổi",
     "Dưới 18 tuổi bị giới hạn công việc, giờ làm; dễ gặp môi trường làm việc không an toàn.", 2),
]

# (ma_huong, doi_tuong_nhan, noi_dung_luu_y, thu_tu_hien_thi)
LOI_KHUYEN = [
    ("THPT_CONG_LAP", "hoc_sinh",
     "Ôn thi vào lớp 10 theo kế hoạch từ đầu năm lớp 9, tập trung các môn thi bắt buộc của địa phương.", 1),
    ("THPT_CONG_LAP", "phu_huynh",
     "Tìm hiểu điểm chuẩn các năm trước để đặt nguyện vọng vừa sức, luôn có một nguyện vọng an toàn.", 2),
    ("THPT_CHUYEN", "hoc_sinh",
     "Chỉ thi chuyên khi thực sự yêu thích môn đó; chuẩn bị tinh thần cho cường độ học cao.", 1),
    ("THPT_CHUYEN", "phu_huynh",
     "Không ép con thi chuyên vì thành tích; theo dõi sức khỏe tinh thần của con trong suốt 3 năm.", 2),
    ("THPT_TU_THUC", "phu_huynh",
     "Đến thăm trường, hỏi rõ tổng chi phí 3 năm và tỷ lệ tốt nghiệp, đỗ đại học trước khi đăng ký.", 1),
    ("THPT_TU_THUC", "ca_hai",
     "Chọn trường có giấy phép và được Sở Giáo dục và Đào tạo công nhận để bằng tốt nghiệp hợp lệ.", 2),
    ("THPT_QUOC_TE", "phu_huynh",
     "Lập kế hoạch tài chính dài hạn cho cả giai đoạn THPT và du học sau đó.", 1),
    ("THPT_QUOC_TE", "hoc_sinh",
     "Củng cố tiếng Anh học thuật trước khi vào học để không bị đuối trong năm đầu.", 2),
    ("GDNN_GDTX", "hoc_sinh",
     "Tận dụng thời gian rảnh để học thêm một nghề hoặc kỹ năng, đừng để thời gian trôi lãng phí.", 1),
    ("GDNN_GDTX", "phu_huynh",
     "Động viên con, không coi đây là lựa chọn thất bại; theo dõi chuyên cần vì môi trường ít kỷ luật hơn.", 2),
    ("TRUNG_CAP_9_PLUS", "hoc_sinh",
     "Trải nghiệm thử hoặc tham quan xưởng thực hành trước khi chọn nghề; ưu tiên nghề đang thiếu lao động.", 1),
    ("TRUNG_CAP_9_PLUS", "ca_hai",
     "Hỏi rõ trường có dạy văn hóa THPT kèm theo không và điều kiện liên thông lên cao đẳng, đại học.", 2),
    ("HOC_NGHE_NGAN_HAN", "phu_huynh",
     "Chọn cơ sở đào tạo có giấy phép; con dưới 18 tuổi chỉ làm công việc, giờ làm theo đúng luật lao động.", 1),
    ("HOC_NGHE_NGAN_HAN", "hoc_sinh",
     "Có thể học bổ túc văn hóa buổi tối để sau này còn cơ hội học lên khi cần.", 2),
]


def _bang(ten: str, *cot: str) -> sa.TableClause:
    return sa.table(ten, *(sa.column(c) for c in cot))


def _map_ma_id(conn, bang: str, cot_ma: str, ma: list[str]) -> dict[str, int]:
    stmt = sa.text(f"SELECT {cot_ma}, id FROM {bang} WHERE {cot_ma} IN :ids").bindparams(
        sa.bindparam("ids", expanding=True)
    )
    return {row[0]: row[1] for row in conn.execute(stmt, {"ids": ma})}


def upgrade() -> None:
    conn = op.get_bind()

    tc_co_san = set(conn.execute(sa.text("SELECT ma_tieu_chi FROM dm_thcs_tieu_chi")).scalars())
    tc_moi = [dong for dong in TIEU_CHI if dong[0] not in tc_co_san]
    if tc_moi:
        cot = ("ma_tieu_chi", "ten_tieu_chi", "mo_ta_tieu_chi", "nhom_tieu_chi", "thu_tu_hien_thi")
        op.bulk_insert(_bang("dm_thcs_tieu_chi", *cot), [dict(zip(cot, dong, strict=True)) for dong in tc_moi])

    hd_co_san = set(conn.execute(sa.text("SELECT ma_huong FROM dm_thcs_huong_di")).scalars())
    hd_moi = [dong for dong in HUONG_DI if dong[0] not in hd_co_san]
    if not hd_moi:
        return
    cot = (
        "ma_huong", "ten_huong", "mo_ta_tong_quan", "doi_tuong_phu_hop", "chi_phi_du_kien_text",
        "chi_phi_thang_min", "chi_phi_thang_max", "muc_do_ap_luc_hoc_tap", "muc_do_tu_giac_can_thiet",
        "tinh_linh_hoat_sau_lop_12", "ma_holland", "thu_tu_hien_thi",
    )
    op.bulk_insert(_bang("dm_thcs_huong_di", *cot), [dict(zip(cot, dong, strict=True)) for dong in hd_moi])

    id_huong = _map_ma_id(conn, "dm_thcs_huong_di", "ma_huong", [dong[0] for dong in hd_moi])
    id_tieu_chi = _map_ma_id(conn, "dm_thcs_tieu_chi", "ma_tieu_chi", [dong[0] for dong in TIEU_CHI])

    op.bulk_insert(
        _bang("dm_thcs_uu_nhuoc_diem", "thcs_huong_di_id", "loai", "tieu_de", "noi_dung_chi_tiet", "thu_tu_hien_thi"),
        [
            {"thcs_huong_di_id": id_huong[ma], "loai": loai, "tieu_de": tieu_de, "noi_dung_chi_tiet": noi_dung,
             "thu_tu_hien_thi": thu_tu}
            for ma, loai, tieu_de, noi_dung, thu_tu in UU_NHUOC_DIEM
            if ma in id_huong
        ],
    )
    op.bulk_insert(
        _bang("dm_thcs_huong_di_tieu_chi", "thcs_huong_di_id", "thcs_tieu_chi_id", "diem_phu_hop", "nhan_dinh_tu_van"),
        [
            {"thcs_huong_di_id": id_huong[ma_huong], "thcs_tieu_chi_id": id_tieu_chi[tc[0]], "diem_phu_hop": diem,
             "nhan_dinh_tu_van": _NHAN_DINH.get((ma_huong, tc[0]))}
            for ma_huong, ds_diem in _DIEM.items()
            if ma_huong in id_huong
            for tc, diem in zip(TIEU_CHI, ds_diem, strict=True)
        ],
    )
    op.bulk_insert(
        _bang("dm_thcs_loi_khuyen_luu_y", "thcs_huong_di_id", "doi_tuong_nhan", "noi_dung_luu_y", "thu_tu_hien_thi"),
        [
            {"thcs_huong_di_id": id_huong[ma], "doi_tuong_nhan": doi_tuong, "noi_dung_luu_y": noi_dung,
             "thu_tu_hien_thi": thu_tu}
            for ma, doi_tuong, noi_dung, thu_tu in LOI_KHUYEN
            if ma in id_huong
        ],
    )


def downgrade() -> None:
    # Ưu/nhược điểm, điểm phù hợp, lời khuyên bị xóa theo nhờ khóa ngoại ON DELETE CASCADE.
    conn = op.get_bind()
    for bang, cot, ma in (
        ("dm_thcs_huong_di", "ma_huong", [dong[0] for dong in HUONG_DI]),
        ("dm_thcs_tieu_chi", "ma_tieu_chi", [dong[0] for dong in TIEU_CHI]),
    ):
        conn.execute(
            sa.text(f"DELETE FROM {bang} WHERE {cot} IN :ids").bindparams(sa.bindparam("ids", expanding=True)),
            {"ids": ma},
        )
