from app.services import thu_thap_tuyen_sinh_ai as ai
from app.services.dats_ban_nhap_thu_thap import lap_muc_ban_nhap
from app.services.dats_doi_chieu_diem_chuan import gop_ra_soat_diem, nhan_ra_soat_diem


def test_phan_cuoi_bang_dai_van_co_dau_bang_de_ai_tu_doc(monkeypatch):
    dong_dau = "| Nhãn của trường | Chính thức | Quy đổi |"
    noi_dung = dong_dau + "\n" + "\n".join(f"| Mã {i} | 27,5 | 98 |" for i in range(500))
    docs = {1: ai._TaiLieu("x", "Thông báo", [("Phụ lục", noi_dung)], [])}
    monkeypatch.setattr(ai, "_KY_TU_MOI_NHOM", 5000)
    cac_nhom = ai._chia_nhom_tai_lieu([{"id": 1}], docs, {1: {}})
    assert len(cac_nhom) > 1
    assert dong_dau not in cac_nhom[-1][0]["noi_dung"][0][1]
    assert cac_nhom[-1][0]["dau_bang"]["Phụ lục"].startswith(dong_dau)
    a, b = ai._tach_nhom([{"noi_dung": [("Phụ lục", noi_dung)]}])
    assert a[0]["dau_bang"] == b[0]["dau_bang"]


def test_phan_nguon_bi_bo_qua_khac_voi_ai_da_doc_va_khong_co_diem():
    docs = {7: ai._TaiLieu("x", "Phụ lục", [("Mục G", "Bảng giao ngưỡng Zeta")], [])}
    da_doc = {"ra_soat_diem_chuan": [{"nguon_id": 7, "da_doc_het": True, "can_lam_ro": []}]}
    def da_ra_soat(cac_phan, loi=()):
        return nhan_ra_soat_diem(cac_phan, docs, loi, 0)["nguon"][0]["da_ra_soat"]
    assert da_ra_soat([([7], da_doc)])
    assert not da_ra_soat([([7], {})])
    assert not da_ra_soat([([7], da_doc), ([7], {"ra_soat_diem_chuan": []})])
    assert not da_ra_soat([([7], da_doc)], loi=[7])
    assert not da_ra_soat([([7], {"ra_soat_diem_chuan": [{"nguon_id": 7, "da_doc_het": True}]})])


def test_chi_ai_co_dan_chung_tu_nguon_bo_sung_moi_duoc_khep_muc_truoc():
    cu = {"nguon": [{"nguon_id": 1, "da_ra_soat": True}], "can_lam_ro": [
        {"nguon_id": 1, "pham_vi": p, "ly_do": "Cần đọc chú thích.", "vi_tri": "Mục G", "trich_dan": p}
        for p in ("Diện Hoa", "Diện Lá")
    ]}
    tai_lieu = {2: ai._TaiLieu("x", "Bổ sung", [("Đợt B", "Diện Hoa có ngưỡng 18.")], [])}
    def xu_ly(trich):
        moi = {"ra_soat_diem_chuan": [{"nguon_id": 2, "da_doc_het": True, "can_lam_ro": [],
                "da_giai_quyet": [{"stt": 1, "vi_tri": "Đợt B", "trich_dan": trich}]}]}
        bao_cao = nhan_ra_soat_diem([([2], moi)], tai_lieu, [], len(cu["can_lam_ro"]))
        return gop_ra_soat_diem(cu, bao_cao)
    assert [q["pham_vi"] for q in xu_ly("Diện Hoa có ngưỡng 18.")["can_lam_ro"]] == ["Diện Lá"]
    assert xu_ly("Câu tự tạo.")["can_lam_ro"] == cu["can_lam_ro"]
    assert len(cu["can_lam_ro"]) == 2


def test_ai_gan_nam_diem_hoi_cuu_tu_tieu_de_khac_biet():
    url, path = "https://truong.edu.vn/g", "/quy_tac_xet_tuyen/diem_chuan/0/diem_chuan"
    tai_lieu = {9: ai._TaiLieu(url, "Thông báo", [("Đợt Mây", "Khóa hai mươi sáu theo niên lịch. X1 / 21,5")], [])}
    nguon = [{"id": 9, "url": url, "nam_ap_dung": 2027, "chinh_thuc": True, "phu_hop": True, "lua_chon": "su_dung"}]
    dong = {"nam_tuyen_sinh": 2026, "diem_chuan": 21.5, "nguon_du_lieu_url": url}
    du_lieu = {"quy_tac_xet_tuyen": {"diem_chuan": [dong]}}
    def da_chon(nam, trich):
        dc = {"nguon_id": 9, "gia_tri": 21.5, "vi_tri": "Đợt Mây", "trich_dan": "X1 / 21,5",
              "can_cu_nam": {"nam_tuyen_sinh": nam, "vi_tri": "Đợt Mây", "trich_dan": trich}}
        items = ai._chuan_hoa_dan_chung([{"duong_dan": path, "dan_chung": [dc]}], tai_lieu, [])
        return next(m for m in lap_muc_ban_nhap(du_lieu, items, nguon, 2027) if m["duong_dan"] == path)["dan_chung_ids"]
    assert da_chon(2026, "Khóa hai mươi sáu theo niên lịch.") == ["1"]
    assert not da_chon(2025, "Khóa hai mươi sáu theo niên lịch.")
    assert not da_chon(2026, "Đoạn không có trong nguồn")
