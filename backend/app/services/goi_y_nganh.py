"""Gợi ý ngành chuẩn (dm_nganh_dao_tao) cho chương trình đào tạo trong đề án.

Thứ tự tin cậy:
1. Mã ngành chuẩn đã ghi ở dats_trinh_do_nganh của chương trình.
2. Mã xét tuyển bắt đầu bằng mã ngành 7 chữ số (ví dụ 7340116, 751060501, 73401011F).
3. Tên chương trình giống tên ngành, sau khi bỏ dấu và bỏ tiền tố loại chương trình (CT TT, CT CLC...).

Không có logic theo mã trường; mọi trường dùng chung một cách gợi ý.
"""

import re
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher

# Tiền tố loại chương trình hay đặt trước tên ngành, so khớp trên chuỗi đã bỏ dấu.
_TIEN_TO = re.compile(
    r"^(ct|chuong trinh)\s+(tt|clc|tc|th|dhnnqt|dhptqt|tien tien|chat luong cao|tieu chuan|"
    r"dinh huong nghe nghiep quoc te|dinh huong phat trien quoc te)\s+(i hons\s+)?"
)
_NGOAC = re.compile(r"\([^)]*\)")
_KHONG_CHU = re.compile(r"[^a-z0-9]+")
_MA_NGANH = re.compile(r"^(7\d{6})")

NGUONG_AP_DUNG = 0.85
SO_GOI_Y = 3


@dataclass
class Nganh:
    id: int
    ma_nganh: str
    ten_nganh: str


@dataclass
class GoiY:
    nganh_dao_tao_id: int
    ma_nganh: str
    ten_nganh: str
    diem: float
    ly_do: str


def chuan_hoa_ten(value: str | None) -> str:
    """Bỏ dấu, chữ thường, bỏ phần trong ngoặc, gộp ký tự đặc biệt thành một khoảng trắng."""
    if not value:
        return ""
    text = unicodedata.normalize("NFD", value.replace("đ", "d").replace("Đ", "D"))
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn").lower()
    text = _NGOAC.sub(" ", text).replace("&", " va ")
    return _KHONG_CHU.sub(" ", text).strip()


def ten_cot_loi(ten_chuong_trinh: str | None) -> str:
    """Tên chương trình sau khi bỏ tiền tố loại chương trình."""
    return _TIEN_TO.sub("", chuan_hoa_ten(ten_chuong_trinh)).strip()


def _do_giong(ten_ct: str, ten_nganh: str) -> float:
    if not ten_ct or not ten_nganh:
        return 0.0
    if ten_ct == ten_nganh:
        return 1.0
    # Tên ngành nằm trọn ở đầu tên chương trình ("cong nghe thong tin viet phap"). Chỉ tin khi tên ngành
    # đủ dài: "kinh te" ở đầu "kinh te doi ngoai" là ngành khác, để người duyệt chọn.
    if ten_ct.startswith(ten_nganh + " "):
        if len(ten_nganh.split()) >= 3:
            return round(min(0.97, 0.86 + 0.1 * len(ten_nganh) / len(ten_ct)), 3)
        return 0.8
    tu_ct, tu_nganh = set(ten_ct.split()), set(ten_nganh.split())
    trung_tu = len(tu_ct & tu_nganh) / len(tu_ct | tu_nganh)
    # Tỷ lệ ký tự chỉ được tính khi có chung từ, tránh "hoa hoc my pham" giống "khoa hoc may tinh".
    ty_le = SequenceMatcher(None, ten_ct, ten_nganh).ratio() if trung_tu >= 0.3 else 0.0
    return round(min(0.84, max(ty_le, trung_tu)), 3)


def goi_y_nganh(
    ten_chuong_trinh: str | None,
    ma_xet_tuyen: str | None,
    ds_nganh: list[Nganh],
    ma_nganh_chuan: str | None = None,
    so_goi_y: int = SO_GOI_Y,
) -> list[GoiY]:
    """Trả tối đa `so_goi_y` ngành, điểm từ 0 đến 1, cao nhất trước."""
    theo_ma = {n.ma_nganh: n for n in ds_nganh}
    ket_qua: dict[int, GoiY] = {}

    def them(nganh: Nganh, diem: float, ly_do: str) -> None:
        cu = ket_qua.get(nganh.id)
        if cu is None or diem > cu.diem:
            ket_qua[nganh.id] = GoiY(nganh.id, nganh.ma_nganh, nganh.ten_nganh, diem, ly_do)

    if ma_nganh_chuan and ma_nganh_chuan.strip() in theo_ma:
        them(theo_ma[ma_nganh_chuan.strip()], 1.0, "Mã ngành chuẩn ở trình độ ngành")
    khop_ma = _MA_NGANH.match((ma_xet_tuyen or "").strip())
    if khop_ma and khop_ma.group(1) in theo_ma:
        them(theo_ma[khop_ma.group(1)], 0.99, "Mã xét tuyển bắt đầu bằng mã ngành")

    cot_loi = ten_cot_loi(ten_chuong_trinh)
    if cot_loi:
        diem_ten = sorted(
            ((n, _do_giong(cot_loi, chuan_hoa_ten(n.ten_nganh))) for n in ds_nganh),
            key=lambda cap: cap[1],
            reverse=True,
        )
        for nganh, diem in diem_ten[:so_goi_y]:
            if diem >= 0.5:
                them(nganh, diem, "Tên giống tên ngành" if diem < 1 else "Trùng tên ngành")

    return sorted(ket_qua.values(), key=lambda g: g.diem, reverse=True)[:so_goi_y]
