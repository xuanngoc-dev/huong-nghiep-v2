from types import SimpleNamespace
from unittest.mock import patch

import pytest

from app.api.v1.endpoints import dats_thu_thap as api
from app.schemas.dats_thu_thap import SuaMucBanNhap
from app.services import thu_thap_tuyen_sinh_ai as ai
from app.services.dats_ban_nhap_thu_thap import canh_bao_dan_chung, lap_muc_ban_nhap, sua_muc_ban_nhap


PATH = "/dats_tuyen_sinh/chi_tieu"
NGUON = {"id": 1, "url": "https://truong.edu.vn/cu", "lua_chon": "su_dung", "nam_ap_dung": 2026,
         "chinh_thuc": True, "phu_hop": True}
SUA = {**NGUON, "id": 2, "url": "https://truong.edu.vn/sua", "ngay_hieu_luc": "2026-06-01",
       "thay_the_url": NGUON["url"], "pham_vi_dieu_chinh": "Chỉ tiêu toàn trường"}


def trich_xuat(nguon, chi_tieu):
    return {"du_lieu": {"thong_tin_import": {}, "dats_tuyen_sinh": {"chi_tieu": chi_tieu}, "quy_tac_xet_tuyen": {}},
            "muc": [{"duong_dan": PATH, "dan_chung": [
                {"nguon_id": nguon["id"], "vi_tri": "Đề án", "trich_dan": f"Toàn trường có {chi_tieu} chỉ tiêu.",
                 "gia_tri": chi_tieu}]}], "nguon_ids": [nguon["id"]], "ghi_chu": []}


def tra_loi(gia_tri, ids):
    return {"ket_luan": [{"duong_dan": PATH, "gia_tri": gia_tri, "dan_chung_ids": ids,
                          "ly_do": "Đối chiếu phạm vi và hiệu lực của hai đề án."}]}, []


@pytest.mark.parametrize("gia_tri, ids, chap_nhan", [(95, [2], True), (None, [1, 2], True),
                                                     (99, [2], False), (95, [1], False), (95, [True], False),
                                                     (None, [1], False)])
def test_quyet_dinh_phai_chon_gia_tri_cua_dung_dan_chung(gia_tri, ids, chap_nhan):
    data, muc, _ = ai._gop_ket_qua([trich_xuat(NGUON, 80), trich_xuat(SUA, 95)], [])
    with patch.object(ai, "_openai", return_value=tra_loi(gia_tri, ids)) as model:
        ai.doi_chieu_mau_thuan_ai({}, 2026, data, muc, [NGUON, SUA])
        assert model.call_count == 1
        assert model.call_args.args[1]["nguon"][1]["pham_vi_dieu_chinh"] == SUA["pham_vi_dieu_chinh"]
        assert data["dats_tuyen_sinh"]["chi_tieu"] == (gia_tri if chap_nhan else 80)
        assert bool(muc[0].get("phan_tich_mau_thuan_ai")) == chap_nhan
        assert muc[0]["mau_thuan"] and len(muc[0]["dan_chung"]) == 2
        if chap_nhan:
            ai.doi_chieu_mau_thuan_ai({}, 2026, data, muc, [NGUON, SUA])
            assert model.call_count == 1


def test_bo_sung_xet_lai_nguon_cu_va_moi_nguoi_duyet_co_the_xac_nhan():
    cu, moi = trich_xuat(NGUON, 80), trich_xuat(SUA, 95)
    ban = SimpleNamespace(du_lieu=cu["du_lieu"], nguon_ids=[1], loi_nguon={})
    with (patch.object(ai, "search_missing_sources", return_value=([SUA], [])),
          patch.object(api, "_chon_nguon_tu_dong", return_value=[NGUON, SUA]),
          patch.object(ai, "_openai", return_value=tra_loi(95, [2]))):
        kq, _, _ = api._tim_bo_sung_ban_nhap({}, 2026, [NGUON], ban, cu, ["Chỉ tiêu"],
                                               lambda *_: moi, lambda *_: None, lambda *_: None, set())
    data = kq["du_lieu"]
    muc = lap_muc_ban_nhap(data, kq["muc"], [NGUON, SUA], 2026)
    truong = next(m for m in muc if m["duong_dan"] == PATH)
    assert truong["gia_tri_ai"] == 95
    assert truong["dan_chung_ids"] == ["2"]
    assert [dc["ai_chon_khi_mau_thuan"] for dc in truong["dan_chung"]] == [False, True]
    assert any(PATH in loi for loi in canh_bao_dan_chung(data, muc))
    da_sua, da_kiem, _ = sua_muc_ban_nhap(data, muc, [
        SuaMucBanNhap(duong_dan=PATH, dan_chung_ids=["2"], da_kiem_tra=True, ghi_chu="Đã xem văn bản điều chỉnh.")],
        [NGUON, SUA])
    assert not any(PATH in loi for loi in canh_bao_dan_chung(da_sua, da_kiem))


def test_bo_qua_khi_hai_nguon_neu_cung_gia_tri():
    data, muc, _ = ai._gop_ket_qua([trich_xuat(NGUON, 80), trich_xuat(SUA, 80)], [])
    with patch.object(ai, "_openai", side_effect=AssertionError("Nguồn thống nhất")):
        ai.doi_chieu_mau_thuan_ai({}, 2026, data, muc, [NGUON, SUA])
    assert data["dats_tuyen_sinh"]["chi_tieu"] == 80


def test_model_chua_phan_dinh_duoc_o_luot_moi_giu_de_xuat_va_ly_do_cu():
    cu, moi = trich_xuat(NGUON, 80), trich_xuat(SUA, 95)
    data, muc, _ = ai._gop_ket_qua([cu, moi], [])
    with patch.object(ai, "_openai", return_value=tra_loi(95, [2])):
        ai.doi_chieu_mau_thuan_ai({}, 2026, data, muc, [NGUON, SUA])
    bo_sung = {**NGUON, "id": 3, "url": "https://truong.edu.vn/chi-tieu"}
    tong, muc_tong, _ = ai._gop_ket_qua([
        {"du_lieu": data, "muc": muc, "ghi_chu": []}, trich_xuat(bo_sung, 120)], [])
    with patch.object(ai, "_openai", side_effect=ai.AdmissionAIError("Hết thời gian.")):
        ai.doi_chieu_mau_thuan_ai({}, 2026, tong, muc_tong, [NGUON, SUA, bo_sung])
    assert tong["dats_tuyen_sinh"]["chi_tieu"] == 95
    assert len(muc_tong[0]["dan_chung"]) == 3
    assert "Hết thời gian." in muc_tong[0]["ghi_chu"] and "hiệu lực" in muc_tong[0]["ghi_chu"]
