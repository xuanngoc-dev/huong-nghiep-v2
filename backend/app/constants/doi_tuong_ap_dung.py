"""Đối tượng áp dụng của loại câu hỏi. Khớp frontend/src/constants/doiTuongApDung.js.

Mỗi giá trị ứng với một hướng đi của học sinh THPT (`code` trong HocSinhThpt/dinhHuong.js).
Dùng cho dm_loai_cau_hoi.doi_tuong_ap_dung (nhiều mã) và tn_phien_khao_sat.dinh_huong (một mã).
Chỉ thêm giá trị mới, không đổi/xóa số đã dùng vì dữ liệu đã lưu theo số.
Số 4 (du học) đã gộp vào 3 (du học nghề + du học chung một nhóm, migration 20261130_0073) — không dùng lại số 4.
"""

DOI_TUONG_AP_DUNG = {
    1: {"ma": "thi-dai-hoc", "ten": "Học sinh THPT thi đại học & cao đẳng"},
    2: {"ma": "di-lam", "ten": "Học sinh THPT đi làm ngay sau tốt nghiệp"},
    3: {"ma": "du-hoc", "ten": "Học sinh THPT du học (du học nghề, đại học, chuyển tiếp)"},
    5: {"ma": "khoi-nghiep", "ten": "Học sinh THPT khởi nghiệp"},
    6: {"ma": "xuat-khau-lao-dong", "ten": "Học sinh THPT xuất khẩu lao động"},
}

DOI_TUONG_THI_DAI_HOC = 1
DOI_TUONG_DI_LAM = 2
