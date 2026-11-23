from app.schemas.dats_thu_thap import DoiChieuBanNhapPublic


def test_ban_cu_khong_co_bao_cao_kiem_ke():
    cu = DoiChieuBanNhapPublic.model_validate({"nguon": []})
    assert cu.cong_thuc is None
    assert cu.ma_tran is None


def test_bao_cao_tra_du_bieu_thuc_pham_vi_va_can_cu_cho_nguoi_duyet():
    can_cu = {"nguon_id": 3, "vi_tri": "Bảng 2, dòng 4", "trich_dan": "X ≤ 80: D = 0.8 × X.",
              "url_tai_lieu": "https://truong.example/bang-2.png"}
    cong_thuc = {
        "ten": "Điểm chứng chỉ", "pham_vi": "Đợt 1", "ma_xet_tuyen": ["CT1"],
        "bieu_thuc": "D = 0.8 × X", "dieu_kien": "X ≤ 80", "thang_diem": "100",
        "dan_chung": [can_cu], "duong_dan": [], "trang_thai": "chua_ghi", "ly_do": "Chưa xác định công thức đích.",
    }
    ma_tran = {
        "da_kiem_ke": False, "so_ma_nhan_dien": 1, "so_ma_da_ghi": 1,
        "so_lien_ket_nhan_dien": 2, "so_lien_ket_da_ghi": 1,
        "chua_ghi": [{"ma_xet_tuyen": "CT1", "noi_dung": "Thiếu diện chứng chỉ.", "dan_chung": [can_cu]}],
        "can_lam_ro": ["Chưa đọc được phần còn lại của bảng."],
    }
    bao_cao_cong_thuc = {"cong_thuc": [cong_thuc], "can_lam_ro": ["Thiếu thang quy đổi nhánh X > 80."]}
    ban = DoiChieuBanNhapPublic.model_validate({
        "trang_thai_ra_soat_ai": "da_chinh_sua", "ma_tran": ma_tran, "cong_thuc": bao_cao_cong_thuc,
    }).model_dump()
    assert ban["trang_thai_ra_soat_ai"] == "da_chinh_sua"
    assert ban["ma_tran"] == ma_tran
    assert ban["cong_thuc"] == bao_cao_cong_thuc
