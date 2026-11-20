"""Đối tượng hướng đến của phiên trò chuyện (chat_conversations.doi_tuong_huong_den).

Khớp frontend/src/constants/doiTuongHuongDen.js. Mỗi đối tượng có `ngu_canh` đưa vào lời nhắc hệ thống để trợ lý
trả lời theo hoàn cảnh của người hỏi. Mã lưu trong CSDL: chỉ thêm mã mới, không đổi/xóa mã đã dùng.
Nhóm THPT tách theo hướng đi (`code` trong HocSinhThpt/dinhHuong.js, có tiền tố `thpt-`).
"""

DOI_TUONG_HUONG_DEN = {
    "thpt-chua-dinh-huong": {
        "ten": "Học sinh THPT chưa định hướng",
        "ngu_canh": "Người hỏi là học sinh THPT chưa xác định sẽ làm gì sau khi tốt nghiệp. Không mặc định là sẽ thi"
        " đại học; giúp người hỏi khám phá sở thích, điểm mạnh, hoàn cảnh và giới thiệu các hướng đi (thi đại học/cao"
        " đẳng, du học, học nghề, đi làm, khởi nghiệp, xuất khẩu lao động) kèm ưu, nhược điểm; có thể gợi ý làm trắc"
        " nghiệm hướng nghiệp Holland trên hệ thống. Khi người hỏi đã nghiêng về một hướng thì tư vấn sâu theo hướng đó.",
    },
    "thpt-thi-dai-hoc": {
        "ten": "Học sinh THPT thi đại học & cao đẳng",
        "ngu_canh": "Người hỏi là học sinh THPT dự định thi/xét tuyển đại học, cao đẳng trong nước. Tập trung vào chọn ngành,"
        " chọn trường, tổ hợp, phương thức xét tuyển, điểm chuẩn và điều kiện tuyển sinh.",
    },
    "thpt-du-hoc": {
        "ten": "Học sinh THPT dự định du học",
        "ngu_canh": "Người hỏi là học sinh THPT dự định du học (đại học, du học nghề, chương trình chuyển tiếp/liên kết)."
        " Tập trung vào chọn quốc gia, ngành, lộ trình chuẩn bị, yêu cầu ngoại ngữ (IELTS, TOEFL, SAT...), hồ sơ, chi phí"
        " và học bổng ở mức tham khảo chung; chương trình liên kết quốc tế/chuyển tiếp của trường trong nước chỉ lấy theo"
        " DỮ LIỆU TUYỂN SINH.",
    },
    "thpt-di-lam": {
        "ten": "Học sinh THPT đi làm ngay sau tốt nghiệp",
        "ngu_canh": "Người hỏi là học sinh THPT muốn đi làm ngay sau khi tốt nghiệp. Tập trung vào nghề phù hợp, kỹ năng cần"
        " có, khóa học ngắn hạn, cách tìm việc và hướng học tiếp sau này; không mặc định khuyên thi đại học.",
    },
    "thpt-khoi-nghiep": {
        "ten": "Học sinh THPT khởi nghiệp",
        "ngu_canh": "Người hỏi là học sinh THPT quan tâm khởi nghiệp. Tập trung vào kiến thức, kỹ năng, ngành học hỗ trợ"
        " khởi nghiệp, cách bắt đầu với vốn nhỏ và rủi ro cần lưu ý.",
    },
    "thpt-xuat-khau-lao-dong": {
        "ten": "Học sinh THPT xuất khẩu lao động",
        "ngu_canh": "Người hỏi là học sinh THPT quan tâm xuất khẩu lao động. Tập trung vào thị trường, ngành nghề, yêu cầu"
        " (sức khỏe, ngoại ngữ, tay nghề), quy trình, chi phí ở mức tham khảo chung và cảnh báo lừa đảo; khuyên chọn doanh"
        " nghiệp được cấp phép.",
    },
    "hoc-nghe": {
        "ten": "Người học nghề",
        "ngu_canh": "Người hỏi muốn học nghề (trung cấp, cao đẳng nghề, khóa đào tạo nghề ngắn hạn). Tập trung vào chọn"
        " nghề, nơi đào tạo nghề, thời gian học, cơ hội việc làm và liên thông lên cao hơn.",
    },
    "hoc-sinh-thcs": {
        "ten": "Học sinh THCS",
        "ngu_canh": "Người hỏi là học sinh THCS. Tập trung vào lựa chọn sau lớp 9 (vào THPT, giáo dục thường xuyên, học"
        " nghề...), khám phá sở thích, năng lực; dùng lời lẽ đơn giản, gần gũi. Thông tin tuyển sinh đại học chỉ nêu khi"
        " được hỏi.",
    },
    "phu-huynh": {
        "ten": "Phụ huynh",
        "ngu_canh": "Người hỏi là phụ huynh đang tìm hiểu để hỗ trợ con chọn hướng đi. Xưng hô với phụ huynh (anh/chị),"
        " nói về con của họ; giải thích rõ các lựa chọn, chi phí, rủi ro và cách đồng hành cùng con.",
    },
    "sinh-vien": {
        "ten": "Sinh viên",
        "ngu_canh": "Người hỏi là sinh viên cao đẳng/đại học. Tập trung vào đối chiếu ngành đang học với năng lực, cơ hội"
        " việc làm, học lên cao, học văn bằng hai hoặc chuyển ngành.",
    },
    "thanh-nien-ngoai-truong": {
        "ten": "Thanh niên ngoài trường",
        "ngu_canh": "Người hỏi là thanh niên hiện không đi học, đang tìm hướng học tiếp hoặc đi làm. Tập trung vào học"
        " nghề ngắn hạn, hệ vừa học vừa làm, cơ hội việc làm và xuất khẩu lao động.",
    },
}

# Trước khi có cột này, trợ lý chỉ trả lời cho học sinh THPT thi đại học — phiên cũ và yêu cầu không gửi mã dùng mã này.
DOI_TUONG_MAC_DINH = "thpt-thi-dai-hoc"


def la_hoc_sinh_thpt(ma: str | None) -> bool:
    """Đối tượng thuộc nhóm học sinh THPT (mọi hướng đi): trợ lý dùng hồ sơ cá nhân kèm dữ liệu tuyển sinh."""
    return (ma or DOI_TUONG_MAC_DINH).startswith("thpt-")


def ghi_chu_doi_tuong(ma: str | None) -> str:
    """Đoạn ngữ cảnh đối tượng người hỏi đưa vào lời nhắc hệ thống; mã lạ thì dùng đối tượng mặc định."""
    doi_tuong = DOI_TUONG_HUONG_DEN.get(ma or "") or DOI_TUONG_HUONG_DEN[DOI_TUONG_MAC_DINH]
    return f"ĐỐI TƯỢNG NGƯỜI HỎI: {doi_tuong['ten']}. {doi_tuong['ngu_canh']}"
