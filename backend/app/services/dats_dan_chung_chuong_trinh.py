"""Khôi phục dẫn chứng mã và tên chương trình từ các dòng đã đọc được."""

import re
from collections import defaultdict
from unicodedata import normalize


_MA = re.compile(r"[\w][\w./-]{0,19}")
_TU = re.compile(r"[\w./-]+")
_SO_CONG_BO = re.compile(
    r"\b(?:tổng\s+(?:số|cộng)|tuyển\s+sinh)\b(?:[^.!?\n]|(?<=\d)\.(?=\d)){0,120}?"
    r"(?<![\w.,])([1-9]\d{0,3})\s+(?:mã\s+(?:(?:xét\s+)?tuyển|tuyển\s+sinh)|ngành|chương\s+trình|CTĐT)\b",
    re.IGNORECASE,
)
_PHAM_VI_HAN_CHE = re.compile(
    r"dự\s+(?:kiến|thảo)|đợt\s+(?:bổ\s+sung|[2-9]\d*)|phụ\s+lục|năm\s+trước", re.IGNORECASE,
)
_COT_MA = {"mã xét tuyển", "mã tuyển sinh", "mã ngành xét tuyển"}


def _van_ban(value: str) -> str:
    return " ".join(normalize("NFKC", value).replace("\u00ad", "").split())


def _chuong_trinh_theo_ma(du_lieu: dict) -> dict[str, list[tuple[str, dict]]]:
    ket_qua = defaultdict(list)
    for khoi, khoa in (("dats_tuyen_sinh", "dats_chuong_trinh_dao_tao"), ("quy_tac_xet_tuyen", "chuong_trinh")):
        nhanh = du_lieu.get(khoi)
        cac_ct = nhanh.get(khoa) if isinstance(nhanh, dict) else None
        if not isinstance(cac_ct, list):
            continue
        for i, ct in enumerate(cac_ct):
            ma = ct.get("ma_xet_tuyen") if isinstance(ct, dict) else None
            if isinstance(ma, str) and _MA.fullmatch(ma):
                ket_qua[_van_ban(ma).casefold()].append((f"/{khoi}/{khoa}/{i}", ct))
    return ket_qua


def _dau_muc(duong_dan: str, gia_tri: str, nguon_id: int, vi_tri: str, dong: str) -> dict:
    return {
        "duong_dan": duong_dan,
        "dan_chung": [{"nguon_id": nguon_id, "vi_tri": vi_tri, "trich_dan": dong, "gia_tri": gia_tri}],
    }


def _ten_co_trong_dong(ten: str, ma: str, dong: str, cac_o: list[str]) -> bool:
    if not isinstance(ten, str) or not ten.strip():
        return False
    ten = _van_ban(ten).casefold()
    if cac_o:
        return ten in cac_o
    # HTML/PDF không có dấu phân cột vẫn phải theo cấu trúc một hàng bảng bắt đầu bằng STT.
    ma, ten = re.escape(ma.casefold()), re.escape(ten)
    return bool(re.match(
        rf"^\d{{1,3}}[.)]?\s+(?:\d{{6,10}}\s+)?(?:{ten}\s+{ma}(?![\w./-])|{ma}\s+{ten}(?=\s*(?:$|\d)))",
        dong.casefold(),
    ))


def bo_sung_dan_chung_chuong_trinh(du_lieu: dict, nguon_id: int, doc) -> tuple[list[dict], list[dict]]:
    """Tìm dẫn chứng cho các giá trị đã có, giữ nguyên nhãn và đoạn trích của nguồn."""
    theo_ma = _chuong_trinh_theo_ma(du_lieu)
    muc = {}
    cac_dong_ma = []
    cac_tong = {}
    for vi_tri, noi_dung in doc.doan:
        if _PHAM_VI_HAN_CHE.search(vi_tri):
            continue
        cot_ma = None
        for van_ban in noi_dung.splitlines():
            dong = _van_ban(van_ban)
            if not dong or len(dong) > 2000:
                continue
            if vi_tri not in doc.url_dan_chung and (tong := _SO_CONG_BO.search(dong)) and doc.doi_chieu(vi_tri, tong[0]):
                cac_tong.setdefault(int(tong[1]), (vi_tri, tong[0]))
            o = [x.strip() for x in dong.strip("|").split("|")] if "|" in dong else []
            o_chuan = [x.casefold() for x in o]
            if cot := [i for i, x in enumerate(o_chuan) if x in _COT_MA]:
                cot_ma = (cot[0], len(o)) if len(cot) == 1 else None
                continue
            ma_tu_cot = o[cot_ma[0]] if cot_ma and len(o) == cot_ma[1] else ""
            if not _MA.fullmatch(ma_tu_cot) or not (ma_tu_cot.isupper() or any(c.isdigit() for c in ma_tu_cot)):
                ma_tu_cot = ""
            cac_ma = {ma_tu_cot} if ma_tu_cot else set()
            ung_vien = [ma_tu_cot] if cot_ma else o or _TU.findall(dong)
            cac_ct = [(ma, theo_ma[ma.casefold()]) for ma in dict.fromkeys(ung_vien) if ma.casefold() in theo_ma]
            if (not cac_ma and not cac_ct) or not doc.doi_chieu(vi_tri, dong):
                continue
            for ma, chung_muc in cac_ct:
                for duong_dan, ct in chung_muc:
                    ten_khop = _ten_co_trong_dong(ct.get("ten_chuong_trinh"), ma, dong, o_chuan)
                    if ma != ma_tu_cot and not ten_khop:
                        continue
                    cac_ma.add(ma)
                    cac_khoa = ["ma_xet_tuyen"]
                    if ten_khop:
                        cac_khoa.append("ten_chuong_trinh")
                    if ct.get("ma_chuong_trinh") == ct["ma_xet_tuyen"]:
                        cac_khoa.append("ma_chuong_trinh")
                    for khoa in cac_khoa:
                        path = f"{duong_dan}/{khoa}"
                        muc.setdefault(path, _dau_muc(path, ct[khoa], nguon_id, vi_tri, dong))
            if cac_ma:
                cac_dong_ma.append((vi_tri, dong, sorted(cac_ma)))

    # Chỉ mô tả bảng toàn trường khi văn bản chính nêu một tổng công bố rõ ràng.
    if len(cac_tong) != 1:
        return list(muc.values()), []
    (tong, (vi_tri, trich_dan)), = cac_tong.items()
    doi_chieu = [
        {"nguon_id": nguon_id, "vi_tri": vi_tri, "trich_dan": trich_dan, "cac_ma": [],
         "tong_cong_bo": tong, "pham_vi": "toan_truong"},
        *({"nguon_id": nguon_id, "vi_tri": nhan, "trich_dan": dong, "cac_ma": cac_ma,
           "tong_cong_bo": None, "pham_vi": "toan_truong"} for nhan, dong, cac_ma in cac_dong_ma),
    ]
    return list(muc.values()), doi_chieu
