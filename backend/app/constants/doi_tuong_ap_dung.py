"""Đối tượng áp dụng của loại câu hỏi. Khớp frontend/src/constants/doiTuongApDung.js.

Mỗi giá trị ứng với một hướng đi của học sinh THPT (`code` trong HocSinhThpt/dinhHuong.js).
Chỉ thêm giá trị mới, không đổi/xóa số đã dùng vì dữ liệu đã lưu theo số.
"""

DOI_TUONG_AP_DUNG = {
    1: {"ma": "thi-dai-hoc", "ten": "Học sinh THPT thi đại học & cao đẳng"},
    2: {"ma": "di-lam", "ten": "Học sinh THPT đi làm ngay sau tốt nghiệp"},
    3: {"ma": "du-hoc-nghe", "ten": "Học sinh THPT du học nghề"},
    4: {"ma": "du-hoc", "ten": "Học sinh THPT du học"},
    5: {"ma": "khoi-nghiep", "ten": "Học sinh THPT khởi nghiệp"},
    6: {"ma": "xuat-khau-lao-dong", "ten": "Học sinh THPT xuất khẩu lao động"},
}

DOI_TUONG_THI_DAI_HOC = 1
DOI_TUONG_DI_LAM = 2
