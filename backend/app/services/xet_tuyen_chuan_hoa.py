"""Chuẩn hóa linh hoạt file quy tắc xét tuyển trước khi kiểm tra theo cấu trúc chuẩn.

File do người hoặc công cụ khác soạn hay dùng mã gần đúng (`IELTS` thay cho `DIEM_CHUNG_CHI` + khoa `IELTS`,
`DIEM_THI_TOAN_2026`, `VACT` thay cho `V-ACT`, `HSGQG_NHAT`, `nguon_diem_mon: HOC_BA_THPT_VA_CHUNG_CHI`...).
`chuan_hoa(du_lieu, dm)`:

- đổi về mã chuẩn khi đổi được chắc chắn (theo bí danh cố định hoặc khớp duy nhất với danh mục), ghi cảnh báo;
- phần hệ thống chưa tính được (điều kiện / điểm cộng dùng chỉ số lạ, thành phần thiếu bảng quy đổi...) thì bỏ khỏi
  phần tính toán hoặc chuyển công thức thành THU_CONG, ghi cảnh báo và trả về để đưa vào `quy_dinh_chua_mo_hinh_hoa`;
- không đoán khi có nhiều khả năng; lỗi còn lại (thiếu trường bắt buộc, kiểu sai...) vẫn để bước kiểm tra báo.

Không sửa `du_lieu` gốc.
"""

import copy
import re
from typing import TYPE_CHECKING, get_args

from app.schemas.xet_tuyen_chuan import MaChiSo

if TYPE_CHECKING:
    from app.services.xet_tuyen_import import DanhMucXetTuyen

CHI_SO_CHUAN = set(get_args(MaChiSo))
# Mã chỉ số hay gặp → mã chuẩn không cần khoa.
_BI_DANH_CHI_SO = {
    "TOT_NGHIEP_HOP_LE": "DA_TOT_NGHIEP_THPT",
    "TOT_NGHIEP_THPT": "DA_TOT_NGHIEP_THPT",
    "DA_TOT_NGHIEP": "DA_TOT_NGHIEP_THPT",
    "TOT_NGHIEP": "DA_TOT_NGHIEP_THPT",
}
# Tên chứng chỉ hay gặp → mã danh mục chứng chỉ (chỉ dùng khi mã đích có trong danh mục).
_BI_DANH_CHUNG_CHI = {
    "TOEFL_IBT": "TOEFL_IBT_120",
    "TOEFL_ITP": "TOEFL_ITP_L1",
    "IELTS_ACADEMIC": "IELTS",
}
# Chỉ số có khoa → loại danh mục của khoa (giống _KHOA_CHI_SO của bước kiểm tra).
_DANH_MUC_KHOA = {
    "MON_CHUYEN": "mon",
    "DIEM_THI_THPT": "mon",
    "DIEM_HOC_BA_TB": "mon",
    "DIEM_BAI_THI": "bai_thi",
    "DIEM_CHUNG_CHI": "chung_chi",
    "CO_CHUNG_CHI": "chung_chi",
    "THANH_TICH": "thanh_tich",
}
# Hậu tố mức giải trong mã thành tích (HSGQG_NHAT...) → muc_giai của bộ tính (1 nhất ... 4 khuyến khích).
_MUC_GIAI = {"NHAT": 1, "NHI": 2, "BA": 3, "KK": 4, "KHUYEN_KHICH": 4, "KHUYENKHICH": 4}
_HAU_TO_GIAI = re.compile(r"^(.+?)[_-]?(" + "|".join(sorted(_MUC_GIAI, key=len, reverse=True)) + r")$")
_HAU_TO_NAM = re.compile(r"_(19|20)\d{2}$")
_NGUON_DIEM_MON = ("THI_THPT", "HOC_BA")
_LOAI_NGUON = ("BAI_THI", "CHUNG_CHI")
_KIEU_TINH = ("TO_HOP_MON", "THANH_PHAN", "CHI_DIEU_KIEN", "THU_CONG")


def _gon(ma: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", ma.upper())


def tim_ma(ma, tap, bi_danh: dict | None = None) -> str | None:
    """Mã trong danh mục `tap` ứng với `ma`: trùng khớp, theo bí danh, hoặc khớp duy nhất khi bỏ dấu `-`, `_`."""
    if not isinstance(ma, str) or not ma.strip():
        return None
    ma = ma.strip().upper()
    ma = (bi_danh or {}).get(ma, ma)
    if ma in tap:
        return ma
    khop = [x for x in tap if _gon(x) == _gon(ma)]
    return khop[0] if len(khop) == 1 else None


def _tim_khoa(loai: str, khoa: str, dm: "DanhMucXetTuyen") -> str | None:
    return tim_ma(khoa, getattr(dm, loai), _BI_DANH_CHUNG_CHI if loai == "chung_chi" else None)


def doi_dieu_kien(d: dict, dm: "DanhMucXetTuyen") -> dict | None:
    """Đổi một điều kiện / dòng điểm cộng (ma_chi_so, khoa, toan_tu, gia_tri) về dạng chuẩn; không chắc thì None.

    Không cần đổi gì thì trả nguyên bản ghi.
    """
    moi = _doi_dieu_kien(d, dm)
    if moi is None:
        return None
    khoa_cu = d.get("khoa") or ""
    if (moi["ma_chi_so"], moi["khoa"], moi.get("toan_tu"), moi.get("gia_tri")) == (
        d.get("ma_chi_so"),
        khoa_cu,
        d.get("toan_tu"),
        d.get("gia_tri"),
    ):
        return d
    return moi


def _doi_dieu_kien(d: dict, dm: "DanhMucXetTuyen") -> dict | None:
    ma = d.get("ma_chi_so")
    if not isinstance(ma, str) or not ma.strip():
        return None
    ma = ma.strip().upper()
    khoa = "" if d.get("khoa") is None else str(d["khoa"]).strip()

    if ma in CHI_SO_CHUAN:
        loai = _DANH_MUC_KHOA.get(ma)
        if not loai or not khoa:
            return {**d, "ma_chi_so": ma, "khoa": khoa}
        if moi := _tim_khoa(loai, khoa, dm):
            return {**d, "ma_chi_so": ma, "khoa": moi}
        # Thành tích kèm mức giải trong mã (HSGQG_NHAT = 1): đổi thành khoa HSG-QG, muc_giai = 1.
        tach = _HAU_TO_GIAI.match(khoa.upper()) if ma == "THANH_TICH" else None
        if tach and (goc := _tim_khoa("thanh_tich", tach.group(1), dm)) and d.get("toan_tu") in ("=", ">="):
            if d.get("gia_tri") in (1, 1.0, True):
                return {**d, "ma_chi_so": ma, "khoa": goc, "toan_tu": "=", "gia_tri": _MUC_GIAI[tach.group(2)]}
        return None

    goc = _HAU_TO_NAM.sub("", ma)
    if goc in _BI_DANH_CHI_SO:
        return {**d, "ma_chi_so": _BI_DANH_CHI_SO[goc], "khoa": ""}
    # Tên chứng chỉ đứng ở chỗ mã chỉ số (IELTS >= 7.0): điểm chứng chỉ đó; khoa cũ (IELTS_7) chỉ là nhãn mức.
    if chung_chi := _tim_khoa("chung_chi", goc, dm):
        return {**d, "ma_chi_so": "DIEM_CHUNG_CHI", "khoa": chung_chi}
    for tien_to, chi_so in (
        ("DIEM_THI_THPT_", "DIEM_THI_THPT"),
        ("DIEM_THI_", "DIEM_THI_THPT"),
        ("DIEM_HOC_BA_TB_", "DIEM_HOC_BA_TB"),
        ("DIEM_HOC_BA_", "DIEM_HOC_BA_TB"),
    ):
        if goc.startswith(tien_to) and (mon := _tim_khoa("mon", goc[len(tien_to) :], dm)):
            return {**d, "ma_chi_so": chi_so, "khoa": mon}
    if bai_thi := _tim_khoa("bai_thi", goc, dm):
        return {**d, "ma_chi_so": "DIEM_BAI_THI", "khoa": bai_thi}
    return None


class _KetQua:
    def __init__(self) -> None:
        self.canh_bao: list[str] = []
        self.chua_mo_hinh_hoa: list[dict] = []

    def bo(self, loai: str, ma, mo_ta: str, vi_tri: str, ly_do: str) -> None:
        self.canh_bao.append(f"{vi_tri}: {ly_do}, đã bỏ qua và ghi vào quy định chưa mô hình hóa")
        # Cùng một quy định lặp ở nhiều chương trình chỉ ghi một lần.
        muc = {"loai": loai, "ma": ma, "mo_ta": mo_ta}
        if muc not in self.chua_mo_hinh_hoa:
            self.chua_mo_hinh_hoa.append(muc)

    def doi(self, vi_tri: str, cu: dict, moi: dict) -> None:
        if moi is cu:
            return
        truoc = (cu.get("ma_chi_so"), cu.get("khoa") or "", cu.get("toan_tu"), cu.get("gia_tri"))
        sau = (moi["ma_chi_so"], moi["khoa"], moi.get("toan_tu"), moi.get("gia_tri"))
        if truoc != sau:
            self.canh_bao.append(
                f'{vi_tri}: đổi "{cu.get("ma_chi_so")}"'
                + (f' / khoa "{cu.get("khoa")}"' if cu.get("khoa") else "")
                + f" thành {moi['ma_chi_so']}"
                + (f' / khoa "{moi["khoa"]}"' if moi["khoa"] else "")
                + (f" {moi.get('toan_tu')} {moi.get('gia_tri')}" if truoc[2:] != sau[2:] else "")
            )


def _mo_ta_dieu_kien(d: dict) -> str:
    phan = " ".join(str(x) for x in (d.get("ma_chi_so"), d.get("khoa"), d.get("toan_tu"), d.get("gia_tri")) if x)
    return f"{phan} ({d['mo_ta']})" if d.get("mo_ta") else phan


def _chuan_hoa_nhom(ds_nhom, vi_tri: str, dm, kq: _KetQua):
    if not isinstance(ds_nhom, list):
        return ds_nhom
    giu = []
    for i, nhom in enumerate(ds_nhom):
        if not isinstance(nhom, dict) or not isinstance(nhom.get("mot_trong"), list):
            giu.append(nhom)
            continue
        vt_nhom = f"{vi_tri}/{i}"
        dieu_kien = []
        for j, d in enumerate(nhom["mot_trong"]):
            if not isinstance(d, dict):
                dieu_kien.append(d)
                continue
            vt = f"{vt_nhom}/mot_trong/{j}"
            moi = doi_dieu_kien(d, dm)
            if moi is None:
                kq.bo(
                    "DIEU_KIEN_CHUA_MO_HINH_HOA",
                    nhom.get("ma_nhom"),
                    f"{nhom.get('ten_nhom') or nhom.get('ma_nhom')}: {_mo_ta_dieu_kien(d)}",
                    vt,
                    f'chỉ số "{d.get("ma_chi_so")}"'
                    + (f' / khoa "{d.get("khoa")}"' if d.get("khoa") else "")
                    + " chưa có trong hệ thống",
                )
                continue
            kq.doi(vt, d, moi)
            dieu_kien.append(moi)
        if not dieu_kien and nhom["mot_trong"]:
            kq.canh_bao.append(
                f"{vt_nhom}: nhóm {nhom.get('ma_nhom')} không còn điều kiện nào kiểm tra được, đã bỏ nhóm"
            )
            continue
        giu.append({**nhom, "mot_trong": dieu_kien})
    return giu


def _chuan_hoa_thanh_phan(tp: dict, dm) -> dict | None:
    """Thành phần tính được thì trả bản chuẩn; không tính được (nguồn lạ, thiếu bảng quy đổi...) thì None."""
    loai = tp.get("loai_nguon")
    if loai == "BAI_THI":
        ma = tim_ma(tp.get("ma_bai_thi"), dm.bai_thi)
        return {**tp, "ma_bai_thi": ma} if ma else None
    if loai == "CHUNG_CHI":
        if tp.get("ma_bang_quy_doi"):
            return tp
        # Chứng chỉ chưa có bảng quy đổi nhưng là bài thi trong danh mục (SAT, ACT): tính thẳng theo điểm bài thi.
        ma = tim_ma(tp.get("ma_bai_thi"), dm.bai_thi)
        return {**tp, "loai_nguon": "BAI_THI", "ma_bai_thi": ma} if ma else None
    return None


def _chuan_hoa_cong_thuc(c: dict, vt: str, dm, kq: _KetQua) -> dict:
    ma = c.get("ma_cong_thuc")
    ten = c.get("ten_cong_thuc") or ma
    kieu = c.get("kieu_tinh")
    if kieu is not None and kieu not in _KIEU_TINH:
        kq.canh_bao.append(f'{vt}: kieu_tinh "{kieu}" chưa hỗ trợ, chuyển thành THU_CONG (hệ thống chưa tự tính điểm)')
        c = {**c, "kieu_tinh": "THU_CONG", "thanh_phan": [], "he_so_mon": []}
        kieu = "THU_CONG"

    nguon = c.get("nguon_diem_mon")
    if kieu == "TO_HOP_MON" and isinstance(nguon, str) and nguon not in _NGUON_DIEM_MON:
        moi = "HOC_BA" if "HOC_BA" in nguon.upper() else "THI_THPT" if re.search("THI|THPT", nguon.upper()) else None
        if moi:
            kq.canh_bao.append(
                f'{vt}/nguon_diem_mon: "{nguon}" được hiểu là {moi}, phần còn lại chưa được tính tự động'
            )
            kq.chua_mo_hinh_hoa.append(
                {"loai": "NGUON_DIEM_CHUA_MO_HINH_HOA", "ma": ma, "mo_ta": f"{ten}: nguồn điểm {nguon}"}
            )
            c = {**c, "nguon_diem_mon": moi}

    if c.get("thay_ngoai_ngu") not in (None, "KHONG") and not c.get("ma_bang_quy_doi_ngoai_ngu"):
        kq.canh_bao.append(f"{vt}: thay_ngoai_ngu cần ma_bang_quy_doi_ngoai_ngu nhưng chưa khai, chuyển thành KHONG")
        c = {**c, "thay_ngoai_ngu": "KHONG"}

    thanh_phan = c.get("thanh_phan")
    if isinstance(thanh_phan, list) and thanh_phan:
        moi = []
        khong_tinh = []
        for j, tp in enumerate(thanh_phan):
            chuan = _chuan_hoa_thanh_phan(tp, dm) if isinstance(tp, dict) else tp
            if chuan is None:
                khong_tinh.append(
                    f"{tp.get('ten_thanh_phan') or tp.get('vi_tri')} ({tp.get('loai_nguon')} {tp.get('ma_bai_thi') or ''})".strip()
                )
            else:
                if isinstance(tp, dict) and chuan != tp:
                    kq.canh_bao.append(
                        f'{vt}/thanh_phan/{j}: đổi {tp.get("loai_nguon")} "{tp.get("ma_bai_thi")}" thành '
                        f'{chuan["loai_nguon"]} "{chuan["ma_bai_thi"]}"'
                    )
                moi.append(chuan)
        if khong_tinh and kieu == "THANH_PHAN":
            kq.canh_bao.append(
                f"{vt}: thành phần {', '.join(khong_tinh)} chưa tính được (nguồn lạ, mã bài thi không có trong danh mục "
                "hoặc thiếu bảng quy đổi), chuyển công thức thành THU_CONG (hệ thống chưa tự tính điểm)"
            )
            c = {**c, "kieu_tinh": "THU_CONG", "thanh_phan": []}
        else:
            c = {**c, "thanh_phan": moi}
    return c


def chuan_hoa(du_lieu, dm: "DanhMucXetTuyen") -> tuple[object, list[str], list[dict]]:
    """Trả (dữ liệu đã chuẩn hóa, cảnh báo, quy định chưa mô hình hóa). Dữ liệu không phải object thì trả nguyên."""
    if not isinstance(du_lieu, dict):
        return du_lieu, [], []
    doc = copy.deepcopy(du_lieu)
    kq = _KetQua()

    if isinstance(doc.get("cong_thuc"), list):
        for i, c in enumerate(doc["cong_thuc"]):
            if isinstance(c, dict):
                c = _chuan_hoa_cong_thuc(c, f"cong_thuc/{i}", dm, kq)
                if "dieu_kien" in c:
                    c["dieu_kien"] = _chuan_hoa_nhom(c["dieu_kien"], f"cong_thuc/{i}/dieu_kien", dm, kq)
                doc["cong_thuc"][i] = c

    if "dieu_kien_chung" in doc:
        doc["dieu_kien_chung"] = _chuan_hoa_nhom(doc["dieu_kien_chung"], "dieu_kien_chung", dm, kq)

    if isinstance(doc.get("diem_cong"), list):
        giu = []
        for i, d in enumerate(doc["diem_cong"]):
            if not isinstance(d, dict):
                giu.append(d)
                continue
            moi = doi_dieu_kien(d, dm)
            if moi is None:
                kq.bo(
                    "DIEM_CONG_CHUA_MO_HINH_HOA",
                    d.get("nhom_cong"),
                    f"{d.get('nhom_cong')}: {_mo_ta_dieu_kien(d)}, cộng {d.get('diem_cong')}",
                    f"diem_cong/{i}",
                    f'chỉ số "{d.get("ma_chi_so")}"'
                    + (f' / khoa "{d.get("khoa")}"' if d.get("khoa") else "")
                    + " chưa có trong hệ thống",
                )
                continue
            kq.doi(f"diem_cong/{i}", d, moi)
            giu.append(moi)
        doc["diem_cong"] = giu

    if isinstance(doc.get("chuong_trinh"), list):
        for i, ct in enumerate(doc["chuong_trinh"]):
            if not isinstance(ct, dict):
                continue
            hp = ct.get("hoc_phi")
            if isinstance(hp, dict) and hp.get("hoc_phi_tu") is None:
                if hp.get("hoc_phi_den") is not None:
                    ct["hoc_phi"] = {**hp, "hoc_phi_tu": hp["hoc_phi_den"]}
                    kq.canh_bao.append(f"chuong_trinh/{i}/hoc_phi: thiếu hoc_phi_tu, dùng hoc_phi_den")
                else:
                    ct["hoc_phi"] = None
                    kq.canh_bao.append(f"chuong_trinh/{i}/hoc_phi: chưa có mức học phí, bỏ khối học phí")
            if "dieu_kien_rieng" in ct:
                ct["dieu_kien_rieng"] = _chuan_hoa_nhom(
                    ct["dieu_kien_rieng"], f"chuong_trinh/{i}/dieu_kien_rieng", dm, kq
                )
    return doc, kq.canh_bao, kq.chua_mo_hinh_hoa
