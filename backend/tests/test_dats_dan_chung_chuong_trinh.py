from unittest.mock import patch

from app.services import thu_thap_tuyen_sinh_ai as ai


def test_dinh_dang_bang_truong_tu_dat_duoc_chuyen_cho_ai():
    parser = ai._TrangWeb()
    parser.feed("<article><h2>Hướng tiếp cận Omega</h2><table><tr><td rowspan='2'>Ngả</td>"
                "<td colspan='2'>Chặng</td></tr><tr><td>α</td><td>β</td></tr>"
                "<tr><td>M1</td><td>ở ngưỡng</td><td>ưu tiên</td></tr></table></article>")
    parser.close()
    (muc, bang), = [(m, b) for m, b in parser.doan if " · Bảng " in m]
    assert "Omega" in muc and "| M1 | ở ngưỡng | ưu tiên |" in bang
    assert "rowspan=2" in bang and "colspan=2" in bang


def test_bang_khong_tu_tao_chuong_trinh_va_dan_chung_khi_ai_de_trong():
    url = "https://example.edu.vn/cam-nang"
    title = "Trường Mẫu tuyển sinh năm 2026."
    doc = ai._TaiLieu(url, title, [("Bài", title), ("Bảng", "Tên chương trình | Mã xét tuyển\nOmega | M1")], [])
    nguon = {"id": 1, "url": url, "chinh_thuc": True, "phu_hop": True, "nam_ap_dung": 2026}
    data = {"du_lieu": {"thong_tin_import": {}, "dats_tuyen_sinh": {"nguon_du_lieu_url": url}, "quy_tac_xet_tuyen": {}},
            "muc": [], "doi_chieu_chuong_trinh": [], "ghi_chu": ["Bảng chỉ dùng cho đợt tương lai."],
            "nguon_xac_minh": [{"nguon_id": 1, "dung_truong_co_so": True, "nam_ap_dung": 2026,
                                "vi_tri": "Bài", "trich_dan": title}]}
    with patch.object(ai, "_doc_tai_lieu", return_value=doc), patch.object(ai, "_openai", return_value=(data, [])):
        result = ai.extract_draft({"ten_truong": "Trường Mẫu"}, 2026, [nguon])
    assert result["doi_chieu_chuong_trinh"] == [] and not result["muc"]
    assert not result["du_lieu"]["dats_tuyen_sinh"].get("dats_chuong_trinh_dao_tao")


def test_ai_doc_cong_thuc_chu_la_o_cuoi_nguon():
    path = "/quy_tac_xet_tuyen/cong_thuc/0/he_so_nhan"
    text = "Đại lượng Ω được xác lập bằng hai lần Z."
    doc = ai._TaiLieu("https://example.edu.vn/the-le", "", [("I", "x" * 110000), ("II", text)], [])
    du_lieu = {"quy_tac_xet_tuyen": {"cong_thuc": [{"ma_cong_thuc": "Ω", "he_so_nhan": 2}]}}
    def doc_lai(_prompt, payload, _tokens):
        assert payload["pham_vi_cong_thuc"][0]["ma_cong_thuc"] == "Ω"
        if any(("II", text) in n["noi_dung"] for n in payload["tai_lieu"]):
            return {"dan_chung": [{"duong_dan": path, "nguon_id": 1, "vi_tri": "II", "trich_dan": text}]}, []
        return {"dan_chung": []}, []
    with patch.object(ai, "_openai", side_effect=doc_lai) as model:
        muc = ai._bo_sung_dan_chung_cong_thuc(du_lieu, [], {1: doc}, [])
    assert model.call_count > 1
    assert muc[0]["dan_chung"][0]["gia_tri"] == 2
