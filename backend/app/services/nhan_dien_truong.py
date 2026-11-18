"""Nhận diện trường được nhắc tới trong câu hỏi chat để báo "chưa có dữ liệu" với trường chưa có dữ liệu tuyển sinh.

Kiểm tra cứng, không phụ thuộc AI lập kế hoạch. Một trường được nhận ra qua:
- tên đầy đủ hoặc phần tên riêng (bỏ "Trường/Đại học/Học viện…") từ 3 từ trở lên, vd. "Kinh tế Quốc dân";
- phần tên riêng ngắn hơn đi sau "trường / đại học / ĐH / học viện / cao đẳng", vd. "trường Thương mại",
  "ĐH Kiến trúc" (bỏ địa danh cuối tên: "Kiến trúc Hà Nội" → "Kiến trúc");
- tên viết tắt gõ VIẾT HOA: mã trường, tên viết tắt trong danh mục / data/ten_viet_tat_truong.json, hoặc
  chữ cái đầu kèm ĐH / HV / CĐ theo loại trường (vd. ĐHTM, HVTC).
Tiền tố đi đúng loại trường: "ĐH Thương mại" không khớp "Cao đẳng Thương mại"; "trường X" chỉ hiểu là đại học /
học viện. Phần tên riêng trùng tên ngành (vd. "Công nghệ thông tin", "Kiến trúc") chỉ khớp sau "đại học / học viện",
không khớp sau "trường" hay đứng một mình, để "ngành công nghệ thông tin" không bị hiểu là một trường.
Nhiều cụm cùng khớp thì chỉ xét cụm dài nhất (vd. "Đại học Công nghiệp Hà Nội" chứ không phải "Đại học Công nghiệp").
"""

import json
import re
import unicodedata
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

_FILE_VIET_TAT = Path(__file__).resolve().parents[2] / "data" / "ten_viet_tat_truong.json"
_TIEN_TO_LOAI = ("truong", "dai hoc", "hoc vien", "cao dang", "phan hieu")
# Tiền tố đi kèm phần tên riêng theo loại trường: (tiền tố, chữ viết tắt đầu, có dùng "trường" trơn không).
# "trường X" chỉ hiểu là đại học / học viện; cao đẳng phải ghi rõ "cao đẳng". Tên riêng trùng tên ngành
# không dùng "trường" trơn.
_LOAI_TRUONG = {
    "dai hoc": (("dai hoc", "truong dai hoc"), "DH", True),
    "hoc vien": (("hoc vien",), "HV", True),
    "cao dang": (("cao dang", "truong cao dang"), "CD", False),
}
_KHONG_RO_LOAI = ((), "", True)
_DIA_DANH_CUOI = re.compile(
    r"\s+(?:co so\s+.*|(?:tp|thanh pho|tinh)?\s*(?:ha noi|ho chi minh|da nang|hue|can tho|hai phong|thai nguyen|"
    r"nam dinh|vinh long|quang ngai|nha trang|quy nhon|vinh|mien bac|mien nam|mien trung))$"
)
_MA_TO_HOP = re.compile(r"^[A-Z]\d{2}$")


def chuan_hoa(text: str) -> str:
    value = unicodedata.normalize("NFD", str(text or "").lower().replace("đ", "d"))
    value = "".join(c for c in value if unicodedata.category(c) != "Mn")
    value = re.sub(r"tp[.\s]*hcm|tphcm|tp\.?\s*ho chi minh", "ho chi minh", value)
    value = re.sub(r"\bdh\b", "dai hoc", value)
    value = re.sub(r"\bhv\b", "hoc vien", value)
    return " ".join(re.findall(r"[a-z0-9]+", value))


def _co(text: str, cum: str) -> bool:
    return bool(cum) and f" {cum} " in f" {text} "


def _bo_tien_to(key: str) -> str:
    """Phần tên riêng: bỏ "trường", "đại học", "học viện"… ở đầu."""
    changed = True
    while changed:
        changed = False
        for tien_to in _TIEN_TO_LOAI:
            if key.startswith(tien_to + " "):
                key, changed = key[len(tien_to) + 1:], True
    return key


def _viet_tat_dau(core: str) -> str:
    return "".join(w[0] for w in core.split() if w and w[0].isalpha()).upper()


@lru_cache(maxsize=1)
def _viet_tat_bo_sung(signature: tuple) -> dict[str, list[str]]:
    try:
        data = json.loads(_FILE_VIET_TAT.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {str(k): [str(v) for v in vs] for k, vs in data.items() if not k.startswith("_") and isinstance(vs, list)}


def viet_tat_bo_sung() -> dict[str, list[str]]:
    try:
        stat = _FILE_VIET_TAT.stat()
    except OSError:
        return {}
    return _viet_tat_bo_sung((stat.st_mtime_ns, stat.st_size))


@dataclass
class _ChiMuc:
    cum: dict[str, set[int]] = field(default_factory=dict)  # cụm (đã chuẩn hóa) → các trường
    tu: dict[str, set[int]] = field(default_factory=dict)  # tên viết tắt (viết hoa, Đ→D) → các trường
    tu_dung: dict[str, set[int]] = field(default_factory=dict)  # tên viết tắt đúng chữ hoa/thường (vd. HaUI)

    def them_cum(self, cum: str, i: int) -> None:
        if cum:
            self.cum.setdefault(cum, set()).add(i)

    def them_tu(self, tu: str, i: int) -> None:
        tu = tu.replace("Đ", "D").replace("đ", "d").strip()
        if len(tu) >= 3 and " " not in tu and not _MA_TO_HOP.match(tu):
            self.tu.setdefault(tu.upper(), set()).add(i)
            self.tu_dung.setdefault(tu, set()).add(i)


def _loai(key: str) -> tuple:
    key = key[len("truong "):] if key.startswith("truong ") else key
    return next((v for k, v in _LOAI_TRUONG.items() if key.startswith(k + " ")), _KHONG_RO_LOAI)


def _them_ten_rieng(chi_muc: "_ChiMuc", core: str, loai: tuple, trung_nganh: bool, i: int) -> None:
    tien_to, chu_dau, truong_tron = loai
    for t in (*tien_to, *(("truong",) if truong_tron and not trung_nganh else ())):
        chi_muc.them_cum(f"{t} {core}", i)
    if chu_dau and len(core.split()) >= 2:
        chi_muc.them_tu(chu_dau + _viet_tat_dau(core), i)


def _chi_muc(truong: list[dict], ten_nganh: set[str]) -> _ChiMuc:
    chi_muc = _ChiMuc()
    for i, row in enumerate(truong):
        key = chuan_hoa(row.get("ten_truong"))
        loai = _loai(key)
        core = _bo_tien_to(key)
        # "Bách khoa - Đại học Quốc gia TP.HCM" → "Bách khoa"; "Kiến trúc Hà Nội" → "Kiến trúc".
        cores = {core, core.split(" dai hoc ")[0]}
        cores |= {_DIA_DANH_CUOI.sub("", c) for c in list(cores)}
        cores.discard("")
        # Chỉ coi là trùng tên ngành khi giống hệt ("Kiến trúc"), không phải nằm trong tên ngành dài hơn
        # ("Thương mại" trong "Thương mại điện tử") để vẫn nhận "trường Thương mại".
        trung_nganh = {c for c in cores if c in ten_nganh}
        if len(key.split()) >= 3:
            chi_muc.them_cum(key, i)
        for c in cores:
            if len(c.split()) >= 3 and c not in trung_nganh:
                chi_muc.them_cum(c, i)
            _them_ten_rieng(chi_muc, c, loai, c in trung_nganh, i)
        ma = str(row.get("ma_truong") or "")
        if ma.isalpha():
            chi_muc.them_tu(ma, i)
        for ten in row.get("ten_khac") or []:
            if " " in ten.strip():
                ten_key = chuan_hoa(ten)
                ten_core = _bo_tien_to(ten_key)
                if len(ten_key.split()) >= 3:
                    chi_muc.them_cum(ten_key, i)
                _them_ten_rieng(chi_muc, ten_core, loai, ten_core in ten_nganh, i)
            else:
                chi_muc.them_tu(ten, i)
    return chi_muc


def truong_chua_co_du_lieu(cau_hoi: str, danh_muc: list[dict], co_du_lieu: list[dict], ten_nganh: set[str]) -> list[str]:
    """Tên các trường nhắc tới trong câu hỏi mà chưa có dữ liệu tuyển sinh.

    danh_muc / co_du_lieu: [{"ma_truong", "ten_truong", "ten_khac": [...]}] — toàn bộ trường / trường đang có dữ liệu.
    ten_nganh: tên ngành đã chuẩn hóa (chuan_hoa) để không nhầm tên ngành với tên trường.
    Cụm khớp thuộc nhiều trường (vd. "ĐH Kinh tế") mà có trường đã có dữ liệu thì không báo.
    """
    ma_co = {str(r.get("ma_truong")) for r in co_du_lieu}
    ten_co = {chuan_hoa(r.get("ten_truong")) for r in co_du_lieu}
    # Trường có dữ liệu cũng vào chỉ mục để cụm dài nhất thuộc về chúng thay vì một trường tên ngắn hơn.
    truong = [*danh_muc, *co_du_lieu]
    da_co = [str(r.get("ma_truong")) in ma_co or chuan_hoa(r.get("ten_truong")) in ten_co for r in truong]
    chi_muc = _chi_muc(truong, ten_nganh)

    cau = chuan_hoa(cau_hoi)
    khop = [c for c in chi_muc.cum if _co(cau, c)]
    nhom = [chi_muc.cum[c] for c in khop if not any(o != c and _co(o, c) for o in khop)]
    # Tên viết tắt: gõ VIẾT HOA (NEU, ĐHTM) hoặc đúng chữ hoa/thường như danh mục (HaUI); chữ thường không khớp
    # để không nhầm với từ tiếng Việt (vd. "hau").
    for t in {t.replace("Đ", "D").replace("đ", "d") for t in re.findall(r"[0-9A-Za-zĐđ]+", cau_hoi)}:
        if t.upper() == t and any(ch.isalpha() for ch in t) and t in chi_muc.tu:
            nhom.append(chi_muc.tu[t])
        elif t in chi_muc.tu_dung:
            nhom.append(chi_muc.tu_dung[t])

    ket_qua = []
    for ids in nhom:
        if any(da_co[i] for i in ids):
            continue
        for i in sorted(ids):
            ten = truong[i].get("ten_truong")
            if ten and ten not in ket_qua:
                ket_qua.append(ten)
    return ket_qua
