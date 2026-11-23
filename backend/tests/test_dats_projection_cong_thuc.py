from copy import deepcopy
from unittest.mock import patch

import pytest

from app.services import dats_projection_cong_thuc as project
from app.services.dats_ban_nhap_thu_thap import lap_muc_ban_nhap
from app.services.dats_lien_ket_chuong_trinh import _ap_dung_gop


CT = "/quy_tac_xet_tuyen/cong_thuc/0"
BANG = "/dats_tuyen_sinh/dats_quy_doi_diem_trung_tuyen"
URL = "https://test.edu.vn/de-an"


def fact(expr, scope="Diện xét chứng chỉ", **extra):
    trich = extra.pop("trich", expr)
    return {"ten": "Quy tắc xét", "pham_vi": scope, "ma_xet_tuyen": [], "bieu_thuc": expr,
            "dieu_kien": None, "thang_diem": None, "dan_chung": [
                {"nguon_id": 10, "vi_tri": "Mục 2", "trich_dan": trich, "url_tai_lieu": URL},
            ], **extra}


def nhap(formulas=None):
    return {"du_lieu": {"dats_tuyen_sinh": {}, "quy_tac_xet_tuyen": {
        "cong_thuc": formulas if formulas is not None else [{"ma_cong_thuc": "F", "ten_cong_thuc": "Xét chứng chỉ"}],
    }}, "muc": []}


def chay(data, facts, *de_xuat):
    tra_loi = {"ket_qua": [{**p, "ly_do": p.get("ly_do", "Cùng diện trong phụ lục."), "stt": i}
                           for i, p in enumerate(de_xuat)]}
    with patch.object(project.ai, "_openai", return_value=(tra_loi, [])):
        return project.chieu_cong_thuc_vao_ban_nhap({"ma_truong": "ABC"}, 2026, data,
                                                    {"cong_thuc": facts, "can_lam_ro": []})


def test_giu_hai_nhanh_cung_cong_thuc_va_dan_chung_dung_gia_tri_sau_khi_luu_cms():
    data = nhap()
    f1 = fact("(7 × X − 6100) / 60", dieu_kien="X ≤ 1650", trich="X ≤ 1650, điểm là (7 × X − 6100) / 60")
    f2 = fact("100 − (1800 − X) / 30", dieu_kien="X > 1650", trich="X > 1650, tính 100 − (1800 − X) / 30")
    d = {"dich": [CT]}
    report = chay(data, [f1, f2], d, d)
    desc = data["du_lieu"]["quy_tac_xet_tuyen"]["cong_thuc"][0]["mo_ta_cong_thuc"]
    assert all(f["bieu_thuc"] in desc and f["dieu_kien"] in desc for f in [f1, f2])
    assert [r["trang_thai"] for r in report["cong_thuc"]] == ["da_ghi_mo_ta"] * 2
    nguon = [{"id": 10, "chinh_thuc": True, "phu_hop": True, "lua_chon": "su_dung", "nam_ap_dung": 2026}]
    items = lap_muc_ban_nhap(data["du_lieu"], data["muc"], nguon, 2026)
    item = next(x for x in items if x["duong_dan"] == CT + "/mo_ta_cong_thuc")
    assert not item["mau_thuan"] and len(item["dan_chung_ids"]) == 2
    truoc = deepcopy(data)
    chay(data, [f1, f2], d, d)
    assert data == truoc


def test_tao_cong_thuc_thu_cong_dung_thang_diem_khong_suy_doan_ma_bo_va_khong_nhan_doi():
    data = nhap([])
    f = fact("HSNL = tư duy + thành tích + thưởng", ten="Điểm HSNL",
             thang_diem="Thang 100", trich="Thang 100. HSNL = tư duy + thành tích + thưởng")
    de_xuat = {"cong_thuc_moi": {"ma_cong_thuc": "HSNL", "thang_diem": 100}}
    out = chay(data, [f], de_xuat)
    ct = data["du_lieu"]["quy_tac_xet_tuyen"]["cong_thuc"]
    assert len(ct) == 1 and ct[0]["thang_diem"] == 100
    assert ct[0]["ma_phuong_thuc_cua_bo"] is None and ct[0]["kieu_tinh"] == "THU_CONG"
    assert out["cong_thuc"][0]["trang_thai"] == "da_ghi_mo_ta"
    cu = deepcopy(data)
    assert chay(data, [f], de_xuat) == out and data == cu


def test_he_so_co_trong_dan_chung_vao_chinh_dong_co_don_vi_va_luu_ca_bieu_thuc():
    data = nhap([{"ma_cong_thuc": "F", "kieu_tinh": "TO_HOP_MON", "he_so_mon": [{"ma_mon": "TOAN"}]}])
    f = fact("Toán nhân hệ số 2")
    out = chay(data, [f], {"dich": [CT], "tham_so": {CT: {"he_so_mon/0/he_so": 2}}})
    assert out["cong_thuc"][0]["trang_thai"] == "da_cau_truc"
    assert data["du_lieu"]["quy_tac_xet_tuyen"]["cong_thuc"][0]["he_so_mon"][0]["he_so"] == 2
    assert CT + "/he_so_mon/0/he_so" in out["cong_thuc"][0]["duong_dan"]


def test_thieu_dieu_kien_chi_luu_mo_ta_khong_ghi_he_so_tinh_diem():
    data = nhap([{"ma_cong_thuc": "F", "kieu_tinh": "TO_HOP_MON", "he_so_mon": [{"ma_mon": "TOAN"}]}])
    f = fact("Toán nhân hệ số 2", truong_chua_xac_minh=["dieu_kien"])
    out = chay(data, [f], {"dich": [CT], "tham_so": {CT: {"he_so_mon/0/he_so": 2}}})
    row = data["du_lieu"]["quy_tac_xet_tuyen"]["cong_thuc"][0]
    assert row["he_so_mon"] == [{"ma_mon": "TOAN"}] and f["bieu_thuc"] in row["mo_ta_cong_thuc"]
    assert out["cong_thuc"][0]["trang_thai"] == "da_ghi_mo_ta"
    assert "điều kiện áp dụng" in out["cong_thuc"][0]["ly_do"] and out["can_lam_ro"]


def test_chua_xac_minh_thang_diem_khong_tao_moc_quy_doi_so():
    data = nhap()
    f = fact("A00 27,82 tương ứng TSA 68,17", truong_chua_xac_minh=["thang_diem"])
    moc = {"bang": BANG, "ten_nguon": "A00", "ten_dich": "TSA", "diem_moc_nguon": 27.82, "diem_moc_dich": 68.17}
    out = chay(data, [f], {"moc_moi": [moc]})
    assert data["du_lieu"]["dats_tuyen_sinh"] == {}
    assert out["cong_thuc"][0]["trang_thai"] == "chua_ghi" and "thang điểm" in out["can_lam_ro"][0]


def test_hai_dau_mut_quy_doi_vao_bang_cap_truong_giu_chieu_va_dan_chung():
    data = nhap()
    f = fact("A00 [26,23; 27,82) tương ứng TSA [61,33; 68,17)", scope="Bảng phân vị chung",
             dieu_kien="Khoảng 4, đóng trái mở phải")
    dich = {"bang": BANG, "ten_nguon": "A00", "ten_dich": "TSA", "ma_to_hop_nguon": "A00"}
    moc = [{**dich, "diem_moc_nguon": 26.23, "diem_moc_dich": 61.33},
           {**dich, "diem_moc_nguon": 27.82, "diem_moc_dich": 68.17}]
    out = chay(data, [f], {"moc_moi": moc})
    ds = data["du_lieu"]["dats_tuyen_sinh"]["dats_quy_doi_diem_trung_tuyen"]
    assert len(ds) == 2 and [(r["diem_moc_nguon"], r["diem_moc_dich"]) for r in ds] == [(26.23, 61.33), (27.82, 68.17)]
    assert all(r["nguon_du_lieu_url"] == URL and "A00 → TSA" in r["dieu_kien_ap_dung"] for r in ds)
    assert out["cong_thuc"][0]["trang_thai"] == "da_cau_truc"
    assert all(dc["url_tai_lieu"] == URL for item in data["muc"] for dc in item["dan_chung"])
    truoc = deepcopy(data)
    chay(data, [f], {"moc_moi": moc})
    assert data == truoc


@pytest.mark.parametrize("sua", [
    {"diem_moc_dich": 80.4}, {"bang": "/quy_tac_xet_tuyen/diem_chuan"}, {"ten_dich": "V-SAT"},
])
def test_khong_luu_mot_phan_bang_neu_co_moc_nguoi_mau_tu_doan(sua):
    data = nhap()
    f = fact("A00 [26,23; 27,82) tương ứng TSA [61,33; 68,17)")
    d = {"bang": BANG, "ten_nguon": "A00", "ten_dich": "TSA", "diem_moc_nguon": 26.23, "diem_moc_dich": 61.33}
    out = chay(data, [f], {"moc_moi": [d, {**d, **sua}]})
    assert data["du_lieu"]["dats_tuyen_sinh"] == {}
    assert out["cong_thuc"][0]["trang_thai"] == "chua_ghi" and out["can_lam_ro"]


def test_pham_vi_rieng_khong_ghi_de_cong_thuc_dang_dung_chung_cho_ma_khac():
    data = nhap()
    data["du_lieu"]["quy_tac_xet_tuyen"]["chuong_trinh"] = [
        {"ma_xet_tuyen": ma, "phuong_an": [{"ma_cong_thuc": "F"}]} for ma in ("A1", "A2")
    ]
    truoc = deepcopy(data)
    out = chay(data, [fact("M = 2T", ma_xet_tuyen=["A1"])], {"dich": [CT]})
    assert data == truoc and out["cong_thuc"][0]["trang_thai"] == "chua_ghi"


@pytest.mark.parametrize(("target", "param", "expr"), [
    ("bang_quy_doi", "muc/0/diem_quy_doi", "IELTS 6.0 quy đổi thành 8 điểm cho KT1"),
    ("diem_cong", "diem_cong", "Cộng 1 điểm cho KT1"),
])
def test_khong_ghi_quy_doi_va_diem_cong_rieng_cua_nganh_vao_bang_dung_chung(target, param, expr):
    data = nhap([{"ma_cong_thuc": "F1", "ma_bang_quy_doi_ngoai_ngu": "NN"},
                {"ma_cong_thuc": "F2", "thanh_phan": [{"ma_bang_quy_doi": "NN"}]}])
    qt = data["du_lieu"]["quy_tac_xet_tuyen"]
    qt.update(chuong_trinh=[
        {"ma_xet_tuyen": "KT1", "phuong_an": [{"ma_cong_thuc": "F1"}]},
        {"ma_xet_tuyen": "KT2", "phuong_an": [{"ma_cong_thuc": "F2"}]},
    ], bang_quy_doi=[{"ma_bang": "NN", "muc": [{"ma_chung_chi": "IELTS"}]}],
        diem_cong=[{"ma_cong_thuc": None}])
    before = deepcopy(data)
    path = "/quy_tac_xet_tuyen/" + target + "/0"
    f = fact(expr, scope="Riêng ngành KT1", ma_xet_tuyen=["KT1"])
    out = chay(data, [f], {"dich": [path], "tham_so": {path: {param: 8 if target == "bang_quy_doi" else 1}}})
    assert data == before and out["cong_thuc"][0]["trang_thai"] == "chua_ghi"
    assert f["pham_vi"] in out["can_lam_ro"][0]


def test_khong_ghi_de_mau_thuan_va_bao_dung_pham_vi_khi_model_khong_tra_tung_quy_tac():
    data = nhap()
    data["muc"] = [{"duong_dan": CT + "/mo_ta_cong_thuc", "dan_chung": [], "mau_thuan": True}]
    cu = deepcopy(data)
    f = fact("Điểm = X / 2")
    out = chay(data, [f], {"dich": [CT]})
    assert out["can_lam_ro"] and data == cu
    out = chay(data, [f])
    assert f["pham_vi"] in out["can_lam_ro"][0] and out["cong_thuc"][0]["dan_chung"] == f["dan_chung"]


@pytest.mark.parametrize("goc", ["X = điểm thi + 20", "X = điểm thi + 2,50", "X = điểm thi + 2.5"])
def test_khong_ghi_bieu_thuc_mat_chu_so_cuoi(goc):
    data = nhap()
    cu = deepcopy(data)
    out = chay(data, [fact("X = điểm thi + 2", trich=goc)], {"dich": [CT]})
    assert data == cu and out["cong_thuc"][0]["trang_thai"] == "chua_ghi"


def test_chi_ghi_mot_dau_mut_chua_du_cho_ca_khoang():
    data = nhap()
    f = fact("A00 [26,23; 27,82) tương ứng TSA [61,33; 68,17)")
    d = {"bang": BANG, "ten_nguon": "A00", "ten_dich": "TSA", "diem_moc_nguon": 26.23, "diem_moc_dich": 61.33}
    out = chay(data, [f], {"moc_moi": [d]})
    assert out["cong_thuc"][0]["trang_thai"] == "da_ghi_mo_ta"
    assert f["bieu_thuc"] in out["can_lam_ro"][0]
    assert f["bieu_thuc"] in data["du_lieu"]["dats_tuyen_sinh"]["dats_quy_doi_diem_trung_tuyen"][0]["ghi_chu"]


@pytest.mark.parametrize("thay_dan_chung,so_dong", [({}, 1), ({"nguon_id": 999}, 0),
                                                  ({"gia_tri": 93.5}, 0), ({"trich_dan": "28.75 | 86.5"}, 0)])
def test_doi_chieu_gia_tri_o_moc_da_co_voi_chinh_hang_nguon(thay_dan_chung, so_dong):
    data = nhap()
    expr = "Band 2 | 28.75 - 29.53 | 86.5 - 96.67"
    f = fact(expr, thang_diem="A (30) | B (100)", ma_xet_tuyen=["K"], trich="A (30) | B (100)\n" + expr)
    row = {"diem_moc_nguon": 28.75, "diem_moc_dich": 86.5, "thang_diem_nguon": 30, "thang_diem_dich": 100}
    data["du_lieu"]["dats_tuyen_sinh"]["dats_chuong_trinh_dao_tao"] = [
        {"ma_xet_tuyen": "K", "dats_quy_doi_diem_trung_tuyen": [row]}]
    path = "/dats_tuyen_sinh/dats_chuong_trinh_dao_tao/0/dats_quy_doi_diem_trung_tuyen/0"
    for k in ("diem_moc_nguon", "diem_moc_dich"):
        dc = {**f["dan_chung"][0], "trich_dan": expr, "gia_tri": row[k]}
        if k == "diem_moc_dich":
            dc.update(thay_dan_chung)
        data["muc"].append({"duong_dan": f"{path}/{k}", "dan_chung": [dc]})
    bc = chay(data, [f], {"dich": [path]})
    report = project.doi_chieu_sau_khi_noi_cong_thuc(data, bc)["cong_thuc"][0]
    assert report["trang_thai"] == "da_ghi_mo_ta"
    assert (path + "/diem_moc_nguon" in report["duong_dan"]) == bool(so_dong)
    assert (path + "/diem_moc_dich" in report["duong_dan"]) == bool(so_dong)
    assert ("1 dòng quy đổi" in report["ly_do"]) == bool(so_dong)


def test_tu_doi_chieu_vi_tri_moc_sau_khi_gop_va_giu_tung_dau_mut():
    data = nhap()
    d = data["du_lieu"]["dats_tuyen_sinh"]
    d["dats_chuong_trinh_dao_tao"] = [
        {"ma_xet_tuyen": ma, "ten_chuong_trinh": ma} for ma in ("U0", "U0", "U1")
    ]
    ct = "/dats_tuyen_sinh/dats_chuong_trinh_dao_tao"
    path = ct + "/2/dats_quy_doi_diem_trung_tuyen"
    f = fact("A00 [26,23; 27,82) tương ứng TSA [61,33; 68,17)", scope="U1", ma_xet_tuyen=["U1"])
    row = {"bang": path, "ten_nguon": "A00", "ten_dich": "TSA"}
    out = chay(data, [f], {"moc_moi": [{**row, "diem_moc_nguon": 26.23, "diem_moc_dich": 61.33},
                                      {**row, "diem_moc_nguon": 27.82, "diem_moc_dich": 68.17}]})
    _ap_dung_gop(data["du_lieu"], data["muc"], [(ct + "/0", ct + "/1", "Cùng chương trình U0.")], [])
    assert len(d["dats_chuong_trinh_dao_tao"]) == 2
    project.doi_chieu_sau_khi_noi_cong_thuc(data, out)
    assert not out["can_lam_ro"] and out["cong_thuc"][0]["trang_thai"] == "da_cau_truc"
    assert all(p.startswith(ct + "/1/") for p in out["cong_thuc"][0]["duong_dan"])
    assert len(out["cong_thuc"][0]["duong_dan"]) == 6 and "_vi_tri_cong_thuc_truoc_gop" not in data


@pytest.mark.parametrize("chinh,so_loi", [(True, 1), (False, 0)])
def test_hau_kiem_chi_bao_ma_chua_noi_voi_cong_thuc_xet_chinh(chinh, so_loi):
    data = nhap()
    data["du_lieu"]["quy_tac_xet_tuyen"]["chuong_trinh"] = [
        {"ma_xet_tuyen": "KT1", "phuong_an": [{"ma_cong_thuc": "F"}]}, {"ma_xet_tuyen": "KT2"},
    ]
    f = fact("Điểm = X", scope="KT1 và KT2", ma_xet_tuyen=["KT1", "KT2"])
    out = chay(data, [f], {"dich": [CT], "la_cong_thuc_xet": chinh})
    project.doi_chieu_sau_khi_noi_cong_thuc(data, out)
    assert out["cong_thuc"][0]["duong_dan"] and len(out["can_lam_ro"]) == so_loi
    if so_loi:
        assert "KT2" in out["can_lam_ro"][0] and "KT1" not in out["can_lam_ro"][0]
