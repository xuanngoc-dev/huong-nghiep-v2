from unittest.mock import Mock, patch

from app.services import thu_thap_tuyen_sinh_ai as ai
from app.services.dats_ma_tran_thu_thap import _chia_nhom_bang_day, lap_ma_tran_ai


def test_bang_ocr_day_giao_dung_mot_lan_tung_hang_kem_tieu_de_chu_thich_va_url():
    header = "Index | Programme | Seats"
    note = "*The seat count is provisional."
    rows = [f"{i} | X{i} Programme | {40 + i}" for i in range(1, 25)]
    caption = "Admissions table 2026"
    vt = "Catalogue annex"
    url = "https://example.edu.vn/catalogue.png"
    text = "\n".join([caption, header, *rows, note])
    doc = ai._TaiLieu("https://example.edu.vn", caption, [("Scope", caption), (vt, text)], [], url_dan_chung={vt: url})
    src = {"id": 1, "chinh_thuc": True, "nam_ap_dung": 2026}
    proofs = {1: ai._doan_xac_minh(doc)}
    groups = ai._chia_nhom_tai_lieu([src], {1: doc}, proofs)
    result = {"nguon_xac_minh": [{"nguon_id": 1, "dung_truong_co_so": True, "nam_ap_dung": 2026,
                                  "trich_dan": caption, "vi_tri": "Scope", "da_doc_het_bang": True}], "dong": [], "can_lam_ro": []}
    with patch.object(ai, "_openai", return_value=(result, [])) as model:
        lap_ma_tran_ai({}, 2026, groups, {1: doc}, proofs, Mock())
    parts = [call.args[1]["tai_lieu"][0] for call in model.call_args_list]
    assert len(parts) == 3
    assigned = []
    for part in parts:
        chunk = dict(part["noi_dung"])[vt]
        assigned.extend(line for line in chunk.splitlines() if line in rows)
        assert part["doan_xac_minh"] == groups[0][0]["doan_xac_minh"]
        assert dict(part["noi_dung"])["Scope"] == caption and part["url_dan_chung"][vt] == url
        assert all(s in part["dau_bang"][vt] for s in (caption, header, note))
    assert assigned == rows


def test_bang_html_bi_cat_chong_theo_ky_tu_giu_tieu_de_nhieu_dong_va_o_gop(monkeypatch):
    monkeypatch.setattr(ai, "_KY_TU_MOI_NHOM", 400)
    header = ["| Candidate | Scores |", "[Cấu trúc HTML hàng 1] ô 2: rowspan=1, colspan=2", "| Code | A | B |"]
    rows = [f"| X{i} programme | {i} | {i + 1} |" for i in range(32)]
    geom = "[Cấu trúc HTML hàng 10] ô 2: rowspan=5, colspan=1"
    doc = ai._TaiLieu("x", "Table", [("Table", "\n".join([*header, *rows[:8], geom, *rows[8:]]))], [])
    groups = ai._chia_nhom_tai_lieu([{"id": 1}], {1: doc}, {1: {}})
    assert len(groups) > 1
    parts = [group[0] for group in _chia_nhom_bang_day(groups, {1: doc})]
    assigned = [line for part in parts for line in dict(part["noi_dung"])["Table"].splitlines() if line in rows]
    assert assigned == rows and len(parts) == 4
    assert all("\n".join(header) in p["dau_bang"]["Table"] for p in parts)
    assert rows[7] in parts[1]["dau_bang"]["Table"] and geom in parts[1]["dau_bang"]["Table"]


def test_bai_viet_thong_thuong_va_bang_ngan_giu_nguyen_nhom_duoc_giao():
    doc = ai._TaiLieu("x", "News", [("Announcement", "A | B\nSeparate prose\nA story about applications."),
                                   ("Small table", "Name | Number\nQ | 1\nR | 2")], [])
    groups = ai._chia_nhom_tai_lieu([{"id": 1}], {1: doc}, {1: {}})
    assert _chia_nhom_bang_day(groups, {1: doc}) == groups


def test_nhieu_bang_ngan_cua_nhieu_nguon_van_tinh_tong_so_hang_cua_phan():
    text = "\n".join(["Index | Seats", *(f"{i} | {20 + i}" for i in range(6))])
    docs = {i: ai._TaiLieu(str(i), "Roster", [("Catalogue", text)], []) for i in (1, 2, 3)}
    groups = ai._chia_nhom_tai_lieu([{"id": i} for i in docs], docs, {i: {} for i in docs})
    assert len(groups) == 1
    assert [len(g) for g in _chia_nhom_bang_day(groups, docs)] == [1, 1, 1]
