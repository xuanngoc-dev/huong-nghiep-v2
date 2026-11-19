from app.services.dats_dan_chung_chuong_trinh import bo_sung_dan_chung_chuong_trinh
from app.services.thu_thap_tuyen_sinh_ai import _TaiLieu


def _ban_nhap(ma="IT1", ten="Khoa học máy tính"):
    return {
        "dats_tuyen_sinh": {"dats_chuong_trinh_dao_tao": [{"ma_xet_tuyen": ma, "ten_chuong_trinh": ten}]},
        "quy_tac_xet_tuyen": {"chuong_trinh": [{"ma_xet_tuyen": ma, "ma_chuong_trinh": ma, "ten_chuong_trinh": ten}]},
    }


def test_ocr_gan_dan_chung_cung_dong_va_doi_chieu_ma_con_thieu():
    url_anh = "https://example.edu.vn/bang-tuyen-sinh.png"
    doc = _TaiLieu("https://example.edu.vn/tuyen-sinh", "Tuyển sinh đại học", [
        ("Nội dung", "Theo đó, Đại học tuyển sinh 14.668 chỉ tiêu cho 85 ngành/chương trình đào tạo với 05 phương thức xét tuyển."),
        ("Bảng ảnh 1", "STT | Tên chương trình | Mã xét tuyển\n1 | Khoa học máy tính | IT1\n2 | Kỹ thuật dữ liệu | IT2"),
    ], [], url_dan_chung={"Bảng ảnh 1": url_anh})

    muc, doi_chieu = bo_sung_dan_chung_chuong_trinh(_ban_nhap(), 3, doc)

    assert [item["duong_dan"] for item in muc] == [
        "/dats_tuyen_sinh/dats_chuong_trinh_dao_tao/0/ma_xet_tuyen",
        "/dats_tuyen_sinh/dats_chuong_trinh_dao_tao/0/ten_chuong_trinh",
        "/quy_tac_xet_tuyen/chuong_trinh/0/ma_xet_tuyen",
        "/quy_tac_xet_tuyen/chuong_trinh/0/ten_chuong_trinh",
        "/quy_tac_xet_tuyen/chuong_trinh/0/ma_chuong_trinh",
    ]
    assert all(item["dan_chung"][0]["trich_dan"] == "1 | Khoa học máy tính | IT1" for item in muc)
    assert [item["tong_cong_bo"] for item in doi_chieu] == [85, None, None]
    assert {ma for item in doi_chieu for ma in item["cac_ma"]} == {"IT1", "IT2"}


def test_khong_ghep_tien_to_ma_hoac_ten_khac_dong():
    doc = _TaiLieu("https://example.edu.vn/tuyen-sinh", "Tuyển sinh", [
        ("Nội dung", "1 | Khoa học máy tính | IT10\n2 | Khoa học máy tính nâng cao | IT1\n3 | IT1\nKhoa học máy tính\n4 IT1 Khoa học máy tính nâng cao"),
        ("Bảng", "Tên chương trình | Mã xét tuyển | Mã ngành\nKhoa học máy tính | IT10 | IT1"),
        ("Phụ lục đợt 2", "1 | Khoa học máy tính | IT1"),
    ], [])

    assert bo_sung_dan_chung_chuong_trinh(_ban_nhap(), 3, doc) == ([], [])


def test_chi_lay_tong_toan_truong_tu_noi_dung_goc_ro_rang():
    doc = _TaiLieu("https://example.edu.vn/tuyen-sinh", "Tuyển sinh", [
        ("Nội dung", "Năm 2026, trường tuyển sinh 95 chỉ tiêu.\n1 Khoa học máy tính IT1"),
        ("Bảng ảnh 1", "Tổng số 25 chương trình."),
    ], [], url_dan_chung={"Bảng ảnh 1": "https://example.edu.vn/bang.png"})

    muc, doi_chieu = bo_sung_dan_chung_chuong_trinh(_ban_nhap(), 3, doc)

    assert len(muc) == 5
    assert not doi_chieu


def test_ma_o_dung_cot_giu_duoc_khi_ten_chua_khop():
    doc = _TaiLieu("https://example.edu.vn/tuyen-sinh", "Tuyển sinh", [
        ("Bảng", "Tên chương trình | Mã xét tuyển\nKhoa học máy tính nâng cao | IT1"),
    ], [])

    muc, _ = bo_sung_dan_chung_chuong_trinh(_ban_nhap(), 3, doc)

    assert [item["duong_dan"].rsplit("/", 1)[-1] for item in muc] == ["ma_xet_tuyen", "ma_xet_tuyen", "ma_chuong_trinh"]
