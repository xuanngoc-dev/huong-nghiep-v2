from unittest.mock import patch

import pytest

from app.services import thu_thap_tuyen_sinh_ai as ai
from app.services.dats_danh_muc_phuong_thuc import MA_PHUONG_THUC_BO_THEO_NAM
from app.schemas.dats_thu_thap import DanChungThuThap


_MA = "ma_phuong_thuc_cua_bo"
_PATH = f"/quy_tac_xet_tuyen/cong_thuc/0/{_MA}"
_CAU = "Hội đồng dùng chỉ số hồ sơ quy định tại mục 7 để lập danh sách theo thứ tự."
_LY_DO = "Theo thể lệ của diện này, chỉ số xếp thứ tự được tính từ kết quả đánh giá đã quy định."


def du_lieu(ma, cau=_CAU, vai_tro=None, ly_do=_LY_DO, phan_loai="suy_luan"):
    dong = {_MA: ma}
    muc = {"duong_dan": _PATH, "phan_loai_ma_bo": phan_loai, "ghi_chu": ly_do,
           "dan_chung": [{"nguon_id": 1, "vi_tri": "Thể lệ", "trich_dan": cau, "gia_tri": ma,
                         "vai_tro_can_cu": vai_tro}]}
    return dong, muc, {"du_lieu": {"quy_tac_xet_tuyen": {"cong_thuc": [dong]}}, "muc": [muc]}


def xu_ly(data, noi_dung=_CAU):
    tai_lieu = {1: ai._TaiLieu("https://truong.edu.vn", "", [("Thể lệ", noi_dung)], [])}
    with patch.object(ai, "_openai", side_effect=AssertionError("Kết luận đã do AI đưa ra")):
        ai._chuan_hoa_ma_phuong_thuc(data, 2026, {2026: set(MA_PHUONG_THUC_BO_THEO_NAM[2026])}, tai_lieu, {})
    return ai._chuan_hoa_dan_chung(data["muc"], tai_lieu, [])[0]


@pytest.mark.parametrize("ma", list(MA_PHUONG_THUC_BO_THEO_NAM[2026]))
def test_giu_ma_ai_va_nhan_xuat_xu_theo_tung_dien(ma):
    cong_bo = ma == "500"
    cau = f"Diện tại mục 7 đã đăng ký dưới số tham chiếu quốc gia {ma}." if cong_bo else _CAU
    dong, _, data = du_lieu(ma, cau=cau, phan_loai="cong_bo" if cong_bo else "suy_luan")
    muc = xu_ly(data, cau)
    assert dong[_MA] == ma
    dc = muc["dan_chung"][0]
    assert dc["phan_loai_ma_bo"] == ("cong_bo" if cong_bo else "suy_luan")
    if not cong_bo:
        assert _LY_DO in dc["ly_do_suy_luan_ma_bo"]


def test_thanh_phan_va_vai_tro_moi_cua_truong_duoc_giu_nguyen():
    vai = {"thanh_phan": "Chỉ số hồ sơ của hội đồng", "vai_tro": "xếp thứ tự khi đồng hạng", "trich_dan": _CAU}
    dong, _, data = du_lieu("401", vai_tro=[vai, {**vai, "trich_dan": "Câu không có trong nguồn"}])
    muc = xu_ly(data)
    assert dong[_MA] == "401"
    dc = muc["dan_chung"][0]
    assert dc["vai_tro_can_cu"] == [vai]
    assert DanChungThuThap(**dc, id="1").vai_tro_can_cu[0].vai_tro == vai["vai_tro"]


def test_ai_chua_ket_luan_giu_ly_do_va_ma_ung_vien():
    ly_do = "Có thể là 401 hoặc 402. Nguồn chưa cho biết đơn vị tổ chức."
    dong, _, data = du_lieu(None, ly_do=ly_do)
    muc = xu_ly(data)
    assert dong[_MA] is None
    assert muc["ghi_chu"] == ly_do


def test_nam_chua_nap_danh_muc_giu_ma_ai_doc_duoc_de_nguoi_duyet_doi_chieu():
    cau = "Cổng chung công bố mã 812 cho diện này của năm 2030."
    dong, muc, data = du_lieu("812", cau=cau, phan_loai="cong_bo")
    nguon = {1: ai._TaiLieu("https://truong.edu.vn", "", [("Thể lệ", cau)], [])}
    ai._chuan_hoa_ma_phuong_thuc(data, 2030, {}, nguon, {})
    assert dong[_MA] == "812"
    assert "Chưa có danh mục năm 2030" in muc["ghi_chu"]


@pytest.mark.parametrize("dc, ly_do", [
    ({"nguon_id": 2}, _LY_DO), ({"vi_tri": "Mục khác"}, _LY_DO), ({"trich_dan": "Không có trong nguồn"}, _LY_DO),
    ({"gia_tri": "PT401"}, _LY_DO), ({}, ""), ({"phan_loai_ma_bo": "tự động"}, _LY_DO),
])
def test_khong_nhan_dan_chung_sai_dia_chi_gia_tri_hoac_dinh_dang(dc, ly_do):
    dong, muc_ai, data = du_lieu("401", ly_do=ly_do)
    muc_ai["dan_chung"][0].update(dc)
    muc = xu_ly(data)
    assert dong[_MA] == "401"
    assert not muc["dan_chung"]
    assert "401" in muc["ghi_chu"]


def test_dan_chung_ai_khong_tu_doi_ma_suy_luan_thanh_ma_cong_bo():
    cau = "Phụ lục nêu tham chiếu 401. Hội đồng phải đối chiếu thêm cách sử dụng trong diện đang xét."
    dong, _, data = du_lieu("401", cau=cau)
    muc = xu_ly(data, cau)
    assert dong[_MA] == "401"
    assert muc["dan_chung"][0]["phan_loai_ma_bo"] == "suy_luan"


def test_giu_de_xuat_moi_khong_co_doan_trich_va_ly_giai_bang_tu_cua_ai():
    ly_do = "Theo AI, cách tính chỉ số chuẩn hóa của hội đồng tương ứng diện 402. Chưa dẫn được câu gốc."
    dong, item, data = du_lieu("402", ly_do=ly_do)
    item["dan_chung"] = []
    muc = xu_ly(data)
    assert dong[_MA] == "402"
    assert ly_do in muc["ghi_chu"] and "402" in muc["ghi_chu"]
    assert not muc["dan_chung"]
