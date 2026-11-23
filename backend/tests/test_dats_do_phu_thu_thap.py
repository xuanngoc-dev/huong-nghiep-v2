from unittest.mock import Mock, patch

import httpx
import pytest

from app.services import dats_do_phu_thu_thap as phu


def ra_soat(muc, cu=None):
    return phu.muc_can_tim_bo_sung({"ma_truong": "M"}, 2026, muc, [{"id": 1, "url": "https://m.edu.vn"}],
                                  {"ghi_chu": ["Các diện có tên riêng"]}, cu or [], Mock())


def test_chi_ai_quyet_dinh_khoang_trong_va_pham_vi():
    dac_thu = "Hồ sơ trình diễn ban đêm tại cơ sở A cho mã BE01."
    muc = [{"duong_dan": "/quy_tac_xet_tuyen/chuong_trinh/0/ma_xet_tuyen", "gia_tri_ai": "BE01",
            "dan_chung": [{"nguon_id": 1, "vi_tri": "Quy định riêng", "trich_dan": "BE01 là mã xét tuyển."}]}]
    with patch.object(phu.ai, "_openai", return_value=({"muc_con_thieu": [dac_thu, dac_thu]}, [])) as model:
        assert ra_soat(muc, ["Tìm tên mã xét tuyển"]) == [dac_thu]
    payload = model.call_args.args[1]
    assert payload["ban_nhap"][0]["dan_chung"][0]["trich_dan"] == "BE01 là mã xét tuyển."
    assert payload["de_nghi_truoc"] == ["Tìm tên mã xét tuyển"]
    assert "/quy_tac_xet_tuyen/diem_chuan" in payload["hop_dong_cms"]
    with patch.object(phu.ai, "_openai", return_value=({"muc_con_thieu": []}, [])):
        assert ra_soat(muc) == []


@pytest.mark.parametrize("data", [{}, {"muc_con_thieu": "chưa đủ"}, {"muc_con_thieu": [{}]}])
def test_phan_hoi_hong_khong_bao_da_du(data):
    with patch.object(phu.ai, "_openai", return_value=(data, [])) as model, pytest.raises(
        phu.ai.AdmissionAIError, match="Chưa hoàn tất rà soát"
    ):
        ra_soat([])
    assert model.call_count == 2


def test_khong_gui_lai_yeu_cau_bi_tu_choi_quyen():
    request = httpx.Request("POST", "https://example.com/v1/responses")
    response = httpx.Response(401, request=request)
    exc = phu.ai.AdmissionAIError("API key bị từ chối")
    exc.__cause__ = httpx.HTTPStatusError("401", request=request, response=response)
    with patch.object(phu.ai, "_openai", side_effect=exc) as model, pytest.raises(phu.ai.AdmissionAIError):
        ra_soat([])
    assert model.call_count == 1


@pytest.mark.parametrize("phan_hoi_lo_hong", [{"muc_con_thieu": []}, {"nhan_xet": []}])
def test_lo_sai_dinh_dang_duoc_doc_lai_rieng_va_giu_tham_chieu_dong_trong(phan_hoi_lo_hong):
    path = "/quy_tac_xet_tuyen/chuong_trinh/7"
    muc = [
        {"duong_dan": path + "/ma_xet_tuyen", "gia_tri_ai": "A9", "dan_chung": [{"trich_dan": "a" * 65_000}]},
        {"duong_dan": path + "/ten_chuong_trinh", "gia_tri_ai": "A", "dan_chung": [{"trich_dan": "b" * 65_000}]},
        {"duong_dan": path + "/phuong_an", "gia_tri_ai": [],
         "ghi_chu": "Chưa tìm thấy dữ liệu cho mục này trong các tài liệu đã chọn."},
        {"duong_dan": path + "/chi_tieu", "gia_tri_ai": None},
    ]
    thu_tu = []

    def doc(chi_dan, payload, gioi_han):
        thu_tu.append(payload.get("phan"))
        if "phan" in payload:
            assert "muc_con_thieu" not in chi_dan
            if payload["phan"] == 2:
                assert payload["dinh_danh_dong"][path]["ma_xet_tuyen"] == "A9"
                trong = next(m for m in payload["ban_nhap"] if m.get("truong_trong"))
                assert trong == {"duong_dan": path, "truong_trong": True, "gia_tri": {"phuong_an": [], "chi_tieu": None}}
                if "yeu_cau_thu_lai" not in payload:
                    return phan_hoi_lo_hong, []
                return {"nhan_xet": ["Mã A9 thiếu phương án."]}, []
            return {"nhan_xet": ["A9 đúng phạm vi."]}, []
        assert "nhan_xet" not in chi_dan
        assert payload["doi_chieu_cua_cac_phan"] == ["A9 đúng phạm vi.", "Mã A9 thiếu phương án."]
        return {"muc_con_thieu": ["Đọc lại bảng phương án A9."]}, []

    with patch.object(phu.ai, "_openai", side_effect=doc):
        assert ra_soat(muc) == ["Đọc lại bảng phương án A9."]
    assert thu_tu == [1, 2, 2, None]


def test_ban_lon_tong_hop_bang_ai_ca_nhung_gi_phan_khac_da_giai_quyet():
    muc = [{"duong_dan": f"/gd/{i}", "gia_tri_ai": str(i), "dan_chung": [
        {"nguon_id": 1, "trich_dan": "a" * 60_000}
    ]} for i in range(3)]
    def doc(chi_dan, payload, gioi_han):
        if "phan" in payload:
            return {"nhan_xet": [payload["ban_nhap"][0]["gia_tri"]]}, []
        assert payload["doi_chieu_cua_cac_phan"] == ["0", "1", "2"]
        return {"muc_con_thieu": []}, []
    with patch.object(phu.ai, "_openai", side_effect=doc) as model:
        assert ra_soat(muc) == []
    assert model.call_count == 4
