from copy import deepcopy
from unittest.mock import Mock

import httpx
import pytest

from app.services import dats_kiem_ke_cong_thuc as kk
from app.services import thu_thap_tuyen_sinh_ai as ai


TRUONG = {"ma_truong": "X", "ten_truong": "Trường X"}
CHUNG = "Chương trình CT-1, diện hồ sơ. Trên thang 100, nếu x ≤ 40 thì y = x²/20; nếu x > 40 thì y = 80."
VI_TRI = "Phụ lục · Ảnh bảng 2"
ANH = "https://truong.edu.vn/anh/phu-luc.png"


def nguon(ma=1, **thay_doi):
    return {"id": ma, "url": f"https://truong.edu.vn/2026/{ma}", "nam_ap_dung": 2026, "chinh_thuc": True,
            "phu_hop": True, "lua_chon": "su_dung", **thay_doi}


def tai_lieu(ma=1, noi_dung=CHUNG):
    return ai._TaiLieu(nguon(ma)["url"], "Quy chế tuyển sinh", [(VI_TRI, noi_dung)], [], url_dan_chung={VI_TRI: ANH})


def cong_thuc(**thay_doi):
    return {"ten": "Điểm hồ sơ", "pham_vi": "Diện hồ sơ", "ma_xet_tuyen": ["CT-1", "CT-1"],
            "bieu_thuc": "y = x²/20", "dieu_kien": "nếu x ≤ 40", "thang_diem": "thang 100",
            "dan_chung": [{"vi_tri": VI_TRI, "trich_dan": CHUNG, "url_tai_lieu": "https://tu-tao.vn"}], **thay_doi}


def bao_cao(ma=1, *dong, **thay_doi):
    return {"nguon_id": ma, "cong_thuc": list(dong), "can_lam_ro": [], "da_doc_het": True, **thay_doi}


def chay(doc=None, ds=None, cache=None):
    return kk.kiem_ke_cong_thuc_ai(TRUONG, 2026, ds if ds is not None else [nguon()],
                                   doc if doc is not None else {1: tai_lieu()}, Mock(), bo_nho=cache)


def test_bieu_thuc_tung_nhanh_va_url_anh_duoc_giu_nguyen_khi_doc_lai(monkeypatch):
    tren = cong_thuc(bieu_thuc="y = 80", dieu_kien="nếu x > 40")
    goi = Mock(return_value=({"phan": [bao_cao(1, cong_thuc(), tren)]}, []))
    monkeypatch.setattr(ai, "_openai", goi)
    cache = {}
    kq = chay(cache=cache)
    assert kq["can_lam_ro"] == []
    assert [(r["bieu_thuc"], r["dieu_kien"]) for r in kq["cong_thuc"]] == [("y = x²/20", "nếu x ≤ 40"), ("y = 80", "nếu x > 40")]
    assert kq["cong_thuc"][0]["dan_chung"][0]["url_tai_lieu"] == ANH
    assert kq["cong_thuc"][0]["ma_xet_tuyen"] == ["CT-1"]
    assert chay(cache=cache) == kq
    assert goi.call_count == 1
    assert kk.gop_kiem_ke_cong_thuc(kq, kq) == kq
    khac = chay({1: tai_lieu(noi_dung=CHUNG + " Bản đính chính.")}, cache=cache)
    assert khac["cong_thuc"] == kq["cong_thuc"]
    assert goi.call_count == 2


@pytest.mark.parametrize("sua", [
    {"bieu_thuc": "y = x2/20"}, {"dieu_kien": "nếu x < 40"}, {"thang_diem": "30"}, {"ma_xet_tuyen": ["CT-11"]},
    {"bieu_thuc": "y = x²/2"}, {"dieu_kien": "nếu x ≤ 4"}, {"thang_diem": "thang 10"},
    {"dan_chung": [{"nguon_id": 9, "vi_tri": VI_TRI, "trich_dan": CHUNG}]},
    {"dan_chung": [{"vi_tri": VI_TRI, "trich_dan": "Chương trình CT-1 ghi trên thang 100 theo quy chế."}]},
])
def test_de_xuat_khong_khop_nguyen_van_giu_du_lieu_da_kiem_va_bao_thieu(monkeypatch, sua):
    goi = Mock(return_value=({"phan": [bao_cao(1, cong_thuc(), cong_thuc(**sua))]}, []))
    monkeypatch.setattr(ai, "_openai", goi)
    cache = {}
    kq = chay(cache=cache)
    assert len(kq["cong_thuc"]) == 1
    assert kq["phan_nguon"][0]["da_kiem_ke"] is False
    assert "Nguồn #1" in kq["can_lam_ro"][0] and "Điểm hồ sơ" in kq["can_lam_ro"][0]
    assert not cache and goi.call_count == 2


def test_khoi_phuc_vi_tri_duy_nhat_va_tach_hai_trich_dan_khong_lien_ke(monkeypatch):
    tieu_de = "TT | A00 | Điểm thi TSA"
    hang = "Khoảng 6 | 20 - 22,5 | 44.93 - 54.90"
    doc = tai_lieu(noi_dung=f"{tieu_de}\nKhoảng 1 | 28 - 30 | 83.57 - 100\n{hang}")
    dc = {"vi_tri": f"{VI_TRI}, Khoảng 6 — {ANH}", "trich_dan": f"{tieu_de}\n{hang}"}
    ban = cong_thuc(ma_xet_tuyen=[], bieu_thuc=hang, dieu_kien=None, thang_diem=None, dan_chung=[dc])
    goi = Mock(return_value=({"phan": [bao_cao(1, ban)]}, []))
    monkeypatch.setattr(ai, "_openai", goi)
    kq = chay({1: doc})
    assert not kq["can_lam_ro"]
    assert [(d["vi_tri"], d["trich_dan"], d["url_tai_lieu"]) for d in kq["cong_thuc"][0]["dan_chung"]] == [
        (VI_TRI, tieu_de, ANH), (VI_TRI, hang, ANH)]
    assert goi.call_args.args[1]["tai_lieu"][0]["noi_dung"][0] == {
        "ma_doan": 1, "vi_tri": VI_TRI, "van_ban": doc.doan[0][1]}


def test_chi_phuc_hoi_dan_chung_khi_phan_nguon_va_vi_tri_xac_dinh_duoc():
    doan = [("Phụ lục A", "Công thức điểm: x = 2"), ("Phụ lục B", "Công thức điểm: x = 2 hoặc x = 5")]
    doc = ai._TaiLieu(nguon()["url"], "Tài liệu nguồn", doan, [])
    phan = {"noi_dung": doan}
    assert kk.xac_dinh_vi_tri_trich_dan(phan, doc, "Vị trí do AI diễn giải", "x = 2") is None
    assert kk.xac_dinh_vi_tri_trich_dan(phan, doc, "", "x = 2", 2) == "Phụ lục B"
    assert kk.xac_dinh_vi_tri_trich_dan(phan, doc, "Phụ lục A", "x = 5", 2) is None
    assert kk.xac_dinh_vi_tri_trich_dan(phan, doc, "Phụ lục A", "x = 5") is None
    assert kk.xac_dinh_vi_tri_trich_dan({"noi_dung": [doan[0]]}, doc, "", "x = 5") is None
    for ma_doan in (True, 0, 3):
        assert kk.xac_dinh_vi_tri_trich_dan(phan, doc, "", "x = 2", ma_doan) is None


@pytest.mark.parametrize("bo_trong_khi_doc_lai", [False, True])
def test_giu_bieu_thuc_va_truong_phu_da_kiem_khi_dieu_kien_chua_khop(monkeypatch, bo_trong_khi_doc_lai):
    sai_dieu_kien = cong_thuc(dieu_kien="nếu x ≤ 4")
    lan_dau = ({"phan": [bao_cao(1, sai_dieu_kien)]}, [])
    lan_sau = ({"phan": [bao_cao(1)]}, []) if bo_trong_khi_doc_lai else lan_dau
    goi = Mock(side_effect=[lan_dau, lan_sau])
    monkeypatch.setattr(ai, "_openai", goi)
    cache = {}
    kq = chay(cache=cache)
    ban, = kq["cong_thuc"]
    assert (ban["bieu_thuc"], ban["dieu_kien"], ban["thang_diem"]) == ("y = x²/20", None, "thang 100")
    assert ban["truong_chua_xac_minh"] == ["dieu_kien"]
    assert ban["dan_chung"][0]["url_tai_lieu"] == ANH
    assert not kq["phan_nguon"][0]["da_kiem_ke"] and not cache
    assert any("Điểm hồ sơ — chưa xác minh được điều kiện áp dụng" in q for q in kq["can_lam_ro"])
    goi.side_effect = [lan_dau, ({"phan": [bao_cao(1, cong_thuc())]}, [])]
    da_sua = chay(cache=cache)
    assert cache and da_sua["phan_nguon"][0]["da_kiem_ke"]
    assert not da_sua["can_lam_ro"] and len(da_sua["cong_thuc"]) == 1
    assert da_sua["cong_thuc"][0]["dieu_kien"] == "nếu x ≤ 40"
    assert kk.gop_kiem_ke_cong_thuc(kq, da_sua) == da_sua


@pytest.mark.parametrize(("doan", "nguon", "ket_qua"), [
    ("x = 2", "x = 20", False), ("x = 2", "x = 2.5", False), ("x = 2", "x = 2,5", False),
    ("2 + x", "12 + x", False), ("2 + x", "1,2 + x", False), ("2 + x", "1.2 + x", False),
    ("2 + x", "−2 + x", False), ("x²", "x2", False),
    ("x = 2", "x = 2, nếu đủ điều kiện.", True), ("x = 2", "x = 2.", True),
    ("x = 2", "x = 20; x = 2", True), ("2,5 + x", "Điểm: 2,5 + x", True),
])
def test_so_o_ranh_gioi_cua_bieu_thuc(doan, nguon, ket_qua):
    assert kk.co_bieu_thuc_nguyen_van(doan, nguon) is ket_qua


def test_khong_nhan_dan_chung_tu_cat_bot_mau_so(monkeypatch):
    trich = "nếu x ≤ 40 thì y = x²/2"
    dong = cong_thuc(bieu_thuc="y = x²/2", ma_xet_tuyen=[], thang_diem=None,
                     dan_chung=[{"vi_tri": VI_TRI, "trich_dan": trich}])
    goi = Mock(return_value=({"phan": [bao_cao(1, dong)]}, []))
    monkeypatch.setattr(ai, "_openai", goi)
    kq = chay()
    assert kq["cong_thuc"] == [] and kq["can_lam_ro"]


def test_doc_lai_bo_sot_bieu_thuc_bi_tu_choi_van_bao_thieu_nguyen_van(monkeypatch):
    sai = cong_thuc(ten="Tổng điểm", bieu_thuc="y = x²/2")
    goi = Mock(side_effect=[({"phan": [bao_cao(1, cong_thuc(), sai)]}, []), ({"phan": [bao_cao(1, cong_thuc())]}, [])])
    monkeypatch.setattr(ai, "_openai", goi)
    cache = {}
    kq = chay(cache=cache)
    assert [r["ten"] for r in kq["cong_thuc"]] == ["Điểm hồ sơ"]
    assert not kq["phan_nguon"][0]["da_kiem_ke"] and not cache
    assert any("Chưa tìm lại được dẫn chứng cho Tổng điểm" in q for q in kq["can_lam_ro"])


def test_bo_lich_su_va_nguon_chua_xac_minh(monkeypatch):
    ds = [nguon(), nguon(2, chi_diem_lich_su=True), nguon(3, phu_hop=False), nguon(4, chinh_thuc=False),
          nguon(5, lua_chon="loai"), nguon(6, nam_ap_dung=2025), nguon(7)]
    goi = Mock(return_value=({"phan": [bao_cao(1)]}, []))
    monkeypatch.setattr(ai, "_openai", goi)
    kq = chay({n["id"]: tai_lieu(n["id"]) for n in ds[:-1]}, ds)
    assert [r["id"] for r in goi.call_args.args[1]["tai_lieu"]] == [1]
    assert kq == {"cong_thuc": [], "phan_nguon": [{"nguon_id": 1, "da_kiem_ke": True, "can_lam_ro": []}], "can_lam_ro": []}


def test_chia_lo_qua_dung_luong_va_chi_thu_lai_phan_chua_xong(monkeypatch):
    goi = Mock(side_effect=[
        ai._LoiDungLuongModel("response truncated"),
        ({"phan": [bao_cao(1, cong_thuc())]}, []),
        ({"phan": []}, []),
    ])
    monkeypatch.setattr(ai, "_openai", goi)
    cache = {}
    cu = chay({1: tai_lieu(), 2: tai_lieu(2)}, [nguon(), nguon(2)], cache)
    assert [r["da_kiem_ke"] for r in cu["phan_nguon"]] == [True, False]
    assert goi.call_count == 3
    goi.side_effect = None
    goi.return_value = {"phan": [bao_cao(2, cong_thuc())]}, []
    moi = chay({1: tai_lieu(), 2: tai_lieu(2)}, [nguon(), nguon(2)], cache)
    assert [n["id"] for n in goi.call_args.args[1]["tai_lieu"]] == [2]
    tong = kk.gop_kiem_ke_cong_thuc(cu, moi)
    assert len(tong["cong_thuc"]) == 1
    assert [r["nguon_id"] for r in tong["cong_thuc"][0]["dan_chung"]] == [1, 2]
    assert not tong["can_lam_ro"] and all(r["da_kiem_ke"] for r in tong["phan_nguon"])


def test_dieu_kien_khac_va_trang_khong_co_noi_dung(monkeypatch):
    goi = Mock(return_value=({"phan": [bao_cao(1, cong_thuc())]}, []))
    monkeypatch.setattr(ai, "_openai", goi)
    kq = chay()
    doi = deepcopy(kq)
    doi["cong_thuc"][0]["dieu_kien"] = "nếu x > 40"
    assert len(kk.gop_kiem_ke_cong_thuc(kq, doi)["cong_thuc"]) == 2
    doc = ai._TaiLieu(nguon()["url"], "Bảng chưa đọc được", [], [])
    trong = chay({1: doc})
    assert trong["phan_nguon"][0]["da_kiem_ke"] is False and trong["can_lam_ro"]
    assert goi.call_count == 1


def test_bieu_thuc_giu_so_mu_chi_so_duoi_tu_html_den_ban_kiem_ke(monkeypatch):
    raw = """<h2>Điểm quy đổi</h2><p>y = x² + x<sup><span>2</span></sup> + x<sub>n+1</sub></p>
             <table><tr><td>x₁</td><td>x<sup>3</sup> + ½</td></tr></table>"""
    url = httpx.URL(nguon()["url"])
    monkeypatch.setattr(ai, "_tai_tai_lieu", lambda *_args, **_kwargs: (url, raw.encode(), "text/html"))
    doc = ai._doc_tai_lieu(str(url), chi_html=True)
    bt = "y = x² + x^(2) + x_(n+1)"
    assert doc.doi_chieu("Mục: Điểm quy đổi", bt)
    assert any("| x₁ | x^(3) + ½ |" in s for _, s in doc.doan)
    ban = cong_thuc(ma_xet_tuyen=[], bieu_thuc=bt, thang_diem=None, dieu_kien=None,
                    dan_chung=[{"vi_tri": "Mục: Điểm quy đổi", "trich_dan": bt}])
    monkeypatch.setattr(ai, "_openai", Mock(return_value=({"phan": [bao_cao(1, ban)]}, [])))
    assert chay({1: doc})["cong_thuc"][0]["bieu_thuc"] == bt


def test_anh_trong_bieu_thuc_chua_co_ocr_bao_phan_can_doc(monkeypatch):
    url = httpx.URL(nguon()["url"])
    raw = '<p>Điểm = <img src="/noi-suy.png"> + ưu tiên</p>'
    monkeypatch.setattr(ai, "_tai_tai_lieu", lambda *_args, **_kwargs: (url, raw.encode(), "text/html"))
    doc = ai._doc_tai_lieu(str(url), chi_html=True)
    vt, text = doc.doan[0]
    assert "[Ảnh HTML: /noi-suy.png]" in text and not doc.url_dan_chung
    ban = cong_thuc(bieu_thuc=text, ma_xet_tuyen=[], dieu_kien=None, thang_diem=None,
                    dan_chung=[{"vi_tri": vt, "trich_dan": text}])
    monkeypatch.setattr(ai, "_openai", Mock(return_value=({"phan": [bao_cao(1, ban)]}, [])))
    kq = chay({1: doc})
    assert kq["cong_thuc"] == [] and "phần nằm trong ảnh" in kq["can_lam_ro"][0]


def test_o_ocr_chua_doc_duoc_khong_tro_thanh_bieu_thuc_da_xac_minh(monkeypatch):
    text = "y = x / [không rõ]"
    ban = cong_thuc(bieu_thuc=text, ma_xet_tuyen=[], dieu_kien=None, thang_diem=None,
                    dan_chung=[{"vi_tri": VI_TRI, "trich_dan": text}])
    monkeypatch.setattr(ai, "_openai", Mock(return_value=({"phan": [bao_cao(1, ban)]}, [])))
    kq = chay({1: tai_lieu(noi_dung=text)})
    assert kq["cong_thuc"] == [] and "phần nằm trong ảnh" in kq["can_lam_ro"][0]


@pytest.mark.parametrize("raw", ['<p>Điểm = <img src="/quy-doi.png"> + ưu tiên</p>', '<img src="/quy-doi.png">'])
def test_anh_noi_tuyen_hoac_trang_chi_co_anh_chua_ocr_thi_ds_rong_van_can_kiem_tra(monkeypatch, raw):
    url = httpx.URL(nguon()["url"])
    monkeypatch.setattr(ai, "_tai_tai_lieu", lambda *_args, **_kwargs: (url, raw.encode(), "text/html"))
    doc, cache = ai._doc_tai_lieu(str(url), chi_html=True), {}
    goi = Mock(return_value=({"phan": [bao_cao(1)]}, []))
    monkeypatch.setattr(ai, "_openai", goi)
    kq = chay({1: doc}, cache=cache)
    anh = "https://truong.edu.vn/quy-doi.png"
    assert kq["cong_thuc"] == [] and any(anh in q for q in kq["can_lam_ro"]) and not cache
    doc.doan.append(("Bảng ảnh 1", "Công thức đã đọc"))
    doc.url_dan_chung["Bảng ảnh 1"] = anh
    assert not chay({1: doc}, cache=cache)["can_lam_ro"]
    assert goi.call_count == 2


def test_anh_minh_hoa_co_ngu_canh_khong_bao_thieu_cong_thuc(monkeypatch):
    doc = tai_lieu(noi_dung="Ảnh tác giả [Ảnh HTML: /tac-gia.jpg] chụp tại hội trường.")
    doc.url_dan_chung.clear()
    mh = [{"url": "https://truong.edu.vn/tac-gia.jpg", "ly_do": "Chú thích xác nhận ảnh tác giả."}]
    goi = Mock(return_value=({"phan": [bao_cao(1, anh_minh_hoa=mh)]}, []))
    monkeypatch.setattr(ai, "_openai", goi)
    assert not chay({1: doc})["can_lam_ro"]
