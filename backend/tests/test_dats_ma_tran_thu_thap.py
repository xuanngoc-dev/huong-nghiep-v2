from copy import deepcopy
from unittest.mock import Mock, patch

import pytest

from app.services import thu_thap_tuyen_sinh_ai as ai
from app.services.dats_ma_tran_thu_thap import bao_cao_ma_tran, chieu_danh_muc, gop_ma_tran, lap_ma_tran_ai


URL = "https://example.edu.vn/2026/tuyen-sinh"
TIEU_DE = "Thông tin tuyển sinh 2026 của Đại học M"
TRICH = "IT1 | Khoa học Máy tính | 300 | A00, A01, K01"
NGUON = {"id": 1, "nam_ap_dung": 2026, "url": URL, "chinh_thuc": True, "phu_hop": True}
DC = {"nguon_id": 1, "vi_tri": "Bảng ngành", "trich_dan": TRICH}
DONG = {"ma_xet_tuyen": "IT1", "ten_chuong_trinh": "Khoa học Máy tính", "pham_vi": None, "chi_tieu": 300,
        "dien": "Điểm thi tốt nghiệp THPT", "to_hop": ["A00", "A01", "K01"], "dan_chung": [DC]}
XAC_MINH = {"nguon_id": 1, "dung_truong_co_so": True, "nam_ap_dung": 2026, "vi_tri": "Đầu trang",
            "trich_dan": TIEU_DE, "da_doc_het_bang": True}


def nghien_cuu(rows, *, xac_minh=XAC_MINH, cau_hoi=(), doc=None, noi_dung=None):
    doc = doc or ai._TaiLieu(URL, TIEU_DE, [("Đầu trang", TIEU_DE), ("Bảng ngành", TRICH)], [])
    doan = {1: ai._doan_xac_minh(doc)}
    nhom = ai._chia_nhom_tai_lieu([NGUON], {1: doc}, doan)
    if noi_dung is not None:
        nhom[0][0]["noi_dung"] = noi_dung
    with patch.object(ai, "_openai", return_value=({"nguon_xac_minh": [xac_minh], "dong": rows, "can_lam_ro": list(cau_hoi)}, [])):
        return lap_ma_tran_ai({"ma_truong": "M"}, 2026, nhom, {1: doc}, doan, Mock())


def test_luu_chi_tieu_vao_hai_nhanh_truy_duoc_dong_goc_va_bao_thieu_lien_ket():
    bang, ids = nghien_cuu([DONG])
    assert ids == {1}
    ket_qua = {"ma_tran_goc": bang, "du_lieu": {"dats_tuyen_sinh": {}, "quy_tac_xet_tuyen": {}}, "muc": []}
    chieu_danh_muc(ket_qua)
    chieu_danh_muc(ket_qua)
    assert ket_qua["du_lieu"]["dats_tuyen_sinh"]["dats_chuong_trinh_dao_tao"][0]["chi_tieu_tuyen_sinh"] == 300
    assert ket_qua["du_lieu"]["quy_tac_xet_tuyen"]["chuong_trinh"][0]["chi_tieu"] == 300
    assert len(ket_qua["muc"]) == 6
    assert ket_qua["muc"][0]["dan_chung"][0]["url_tai_lieu"] == URL
    bc = bao_cao_ma_tran(ket_qua)
    assert (bc["so_ma_da_ghi"], bc["so_lien_ket_da_ghi"]) == (1, 0)
    assert "K01" in bc["chua_ghi"][0]["noi_dung"]
    assert any("danh mục" in note for note in bc["can_lam_ro"])
    ket_qua["doi_chieu_chuong_trinh"] = [{"nguon_id": 1, "pham_vi": "toan_truong", "cac_ma": ["IT1", "K2"],
                                          "tong_cong_bo": 2, "don_vi_tong": "mã xét tuyển"}]
    assert any("K2" in note for note in bao_cao_ma_tran(ket_qua)["can_lam_ro"])


@pytest.mark.parametrize("thay_doi", [{"dan_chung": 7}, {"dan_chung": [{**DC, "trich_dan": "nội dung lạ"}]},
                                       {"ma_xet_tuyen": "IT"}, {"chi_tieu": 301}])
def test_khong_chuyen_dong_khong_khop_nguon(thay_doi):
    bang, ids = nghien_cuu([{**DONG, **thay_doi}])
    assert not bang["dong"] and bang["loi_theo_nguon"]
    assert ids == {1}


def test_khoi_phuc_nhan_vi_tri_bang_nganh_khi_khop_duy_nhat_trong_phan_duoc_giao():
    url_bang = URL + "/danh-muc.png"
    doc = ai._TaiLieu(URL, TIEU_DE, [("Đầu trang", TIEU_DE), ("Bảng ngành", TRICH)], [],
                      url_dan_chung={"Bảng ngành": url_bang})
    dc = {**DC, "vi_tri": f"Bảng ngành ({url_bang})"}
    bang, _ = nghien_cuu([{**DONG, "dan_chung": [dc]}], doc=doc)
    assert bang["dong"] == [{**DONG, "dan_chung": [{**DC, "url_tai_lieu": url_bang}]}]
    assert not bang["loi_theo_nguon"]


TIEU_DE_BANG = "STT | Mã xét tuyển | Tên mã xét tuyển | Chỉ tiêu"
DONG_BF1 = "13 | BF1 | Kỹ thuật Sinh học | 160"
DONG_ME2 = "3 | ME2 | Kỹ thuật Cơ khí | 560"


@pytest.mark.parametrize(("trich", "chi_tieu", "noi_dung", "hop_le"), [
    (TIEU_DE_BANG + "\n" + DONG_BF1, 160, None, True),
    (TIEU_DE_BANG + "\n" + DONG_BF1.replace("160", "161"), 160, None, False),
    (TIEU_DE_BANG + "\n" + DONG_BF1, 160, [("Bảng ngành", DONG_BF1), ("Bảng khác", TIEU_DE_BANG)], False),
    (DONG_BF1 + "\n" + DONG_ME2, 560, None, False),
])
def test_dan_tieu_de_va_dong_ma_khong_lien_ke(trich, chi_tieu, noi_dung, hop_le):
    url_bang = URL + "/bang-danh-muc.jpg"
    doc = ai._TaiLieu(URL, TIEU_DE, [("Đầu trang", TIEU_DE),
                      ("Bảng ngành", "\n".join([TIEU_DE_BANG, DONG_ME2, DONG_BF1]))], [],
                      url_dan_chung={"Bảng ngành": url_bang})
    row = {**DONG, "ma_xet_tuyen": "BF1", "ten_chuong_trinh": "Kỹ thuật Sinh học", "chi_tieu": chi_tieu,
           "dien": None, "to_hop": None, "dan_chung": [{**DC, "trich_dan": trich}]}
    bang, _ = nghien_cuu([row], doc=doc, noi_dung=noi_dung)
    if hop_le:
        assert bang["dong"][0]["dan_chung"] == [
            {**DC, "trich_dan": dong, "url_tai_lieu": url_bang} for dong in [TIEU_DE_BANG, DONG_BF1]]
        assert not bang["loi_theo_nguon"]
    else:
        assert not bang["dong"] and bang["loi_theo_nguon"]


@pytest.mark.parametrize("dc,noi_dung", [
    ({**DC, "vi_tri": "Bảng ngành + URL"}, [("Bảng ngành", TRICH), ("Phụ lục", TRICH)]),
    (DC, [("Bảng ngành", "Mã xét tuyển | Tên chương trình | Chỉ tiêu")]),
    ({**DC, "vi_tri": "Bảng ngành + URL", "trich_dan": TRICH.replace("K01", "K02")}, [("Bảng ngành", TRICH)]),
    ({**DC, "vi_tri": "Bảng ngành + URL", "nguon_id": 2}, [("Bảng ngành", TRICH)]),
])
def test_khong_dinh_vi_bang_nganh_khi_trung_sai_phan_sai_chu_hoac_sai_nguon(dc, noi_dung):
    doc = ai._TaiLieu(URL, TIEU_DE, [("Đầu trang", TIEU_DE), ("Bảng ngành", TRICH), ("Phụ lục", TRICH)], [])
    bang, _ = nghien_cuu([{**DONG, "dan_chung": [dc]}], doc=doc, noi_dung=noi_dung)
    assert not bang["dong"] and bang["loi_theo_nguon"]


def test_tai_lieu_khong_co_bang_nganh_van_duoc_xac_minh_de_doc_cong_thuc():
    bang, ids = nghien_cuu([])
    assert not bang["dong"] and bang["da_doc"] == [1] and ids == {1}
    bang, ids = nghien_cuu([DONG], xac_minh={**XAC_MINH, "nam_ap_dung": 2025})
    assert not bang["dong"] and not ids


def test_doc_lai_giai_quyet_loi_va_cau_hoi_nhung_khong_mat_dong():
    cu, _ = nghien_cuu([DONG], xac_minh={**XAC_MINH, "da_doc_het_bang": False}, cau_hoi=["Kiểm tra bảng ngành"])
    moi, _ = nghien_cuu([DONG])
    hop = gop_ma_tran(cu, moi)
    assert hop["da_doc"] == [1] and not hop["loi_theo_nguon"] and not hop["can_lam_ro"]
    assert hop["dong"] == moi["dong"]


def test_chi_tieu_mau_thuan_khong_ghi_de_gia_tri_dang_duyet():
    bang, _ = nghien_cuu([DONG])
    da = {"ma_xet_tuyen": "IT1", "ten_chuong_trinh": "Khoa học Máy tính", "chi_tieu_tuyen_sinh": 250}
    ket_qua = {"ma_tran_goc": bang, "du_lieu": {"dats_tuyen_sinh": {"dats_chuong_trinh_dao_tao": [deepcopy(da)]},
                                               "quy_tac_xet_tuyen": {}}, "muc": []}
    chieu_danh_muc(ket_qua)
    assert ket_qua["du_lieu"]["dats_tuyen_sinh"]["dats_chuong_trinh_dao_tao"] == [da]
    assert "300" in bao_cao_ma_tran(ket_qua)["chua_ghi"][0]["noi_dung"]
