"""Kiểm tra và nhập bản đề án đã được xét duyệt trên CMS."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from unicodedata import normalize

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dats_tuyen_sinh import DatsTuyenSinh
from app.schemas.xet_tuyen_chuan import ChuongTrinhChuan, DeAnXetTuyenChuan
from app.services.dats_import import (
    KHOA_QUY_TAC,
    PHIEN_BAN_QUY_TAC,
    DatsImportError,
    _DATS_FK,
    _MA_THAY_ID,
    _MODELS,
    _kind,
    doi_ten_bang_viet_tat,
    flatten_nested_document,
    import_day_du,
)
from app.services.xet_tuyen_ghi import THU_NGHIEM, KetQuaNhap
from app.services.xet_tuyen_import import XetTuyenImportError, doc_cau_truc

_CAC_KHOI = {"thong_tin_import", "dats_tuyen_sinh", KHOA_QUY_TAC}
_KIEU_DATS = {
    "int": (int,),
    "decimal": (int, float),
    "text": (str,),
    "date": (str,),
    "bool": (bool,),
    "json": (dict, list),
}
_MA_CONG_THUC = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")
_TEN_TAT_DATS = {
    "dats_phuong_thuc": {"to_hop_ids", "to_hop_id"},
    "dats_phuong_thuc_to_hop": {"ma_to_hop"},
    "dats_dieu_kien_du_tuyen": {"ma_doi_tuong_du_tuyen"},
}
_BAT_BUOC = {
    "dats_tru_so": ("ten_co_so",),
    "dats_chuong_trinh_dao_tao": ("ma_xet_tuyen", "ten_chuong_trinh"),
    "dats_phuong_thuc": ("ma_phuong_thuc_cua_bo",),
}


def _cau_truc_dats(bang: str, dong: dict, vi_tri: str, ma_truong: str, nam: int, loi: list[str]) -> None:
    cot = _MODELS[bang].__table__.columns
    ten_tat = _TEN_TAT_DATS.get(bang, set()) | {ma for id_cot, (ma, _) in _MA_THAY_ID.items() if id_cot in cot}
    for khoa in _BAT_BUOC.get(bang, ()):
        gia_tri = dong.get(khoa)
        if not isinstance(gia_tri, str) or not gia_tri.strip():
            loi.append(f"{vi_tri}/{khoa}: cần nhập dữ liệu")
    for khoa, gia_tri in dong.items():
        duong_dan = f"{vi_tri}/{khoa}"
        if khoa in _MODELS:
            if khoa == "dats_tuyen_sinh" or not any(
                ten_cha == bang and khoa_ngoai in _MODELS[khoa].__table__.columns
                for khoa_ngoai, ten_cha in _DATS_FK.items()
            ):
                loi.append(f"{duong_dan}: bảng không thuộc phạm vi {bang}")
            elif not isinstance(gia_tri, list):
                loi.append(f"{duong_dan}: phải là mảng")
            else:
                for so, con in enumerate(gia_tri):
                    if not isinstance(con, dict):
                        loi.append(f"{duong_dan}/{so}: phải là object")
                    else:
                        _cau_truc_dats(khoa, con, f"{duong_dan}/{so}", ma_truong, nam, loi)
            continue
        if khoa not in cot and khoa not in ten_tat:
            loi.append(f"{duong_dan}: trường dữ liệu không có trong mẫu import")
            continue
        if gia_tri is None:
            continue
        kieu = _kind(cot[khoa]) if khoa in cot else "text"
        if khoa == "to_hop_ids":
            kieu = "json"
        if khoa == "to_hop_id" and bang == "dats_phuong_thuc":
            kieu = "int"
        if kieu in _KIEU_DATS and type(gia_tri) not in _KIEU_DATS[kieu]:
            loi.append(f"{duong_dan}: sai kiểu dữ liệu")
        if khoa == "ma_truong" and gia_tri != ma_truong:
            loi.append(f"{duong_dan}: phải là {ma_truong}")
        if khoa == "nam_tuyen_sinh" and gia_tri != nam:
            loi.append(f"{duong_dan}: phải là {nam}")


def _ten_doi_chieu(ten: str) -> str:
    return " ".join(normalize("NFC", ten).split())


def _trung_doi_chieu(
    quy_tac: DeAnXetTuyenChuan, phang: dict, loi: list[str],
) -> dict[tuple[str, str], int]:
    cac_ct = phang.get("dats_chuong_trinh_dao_tao", [])
    dem_dats = Counter(ct["ma_xet_tuyen"] for ct in cac_ct)
    dem_quy_tac = Counter(ct.ma_xet_tuyen for ct in quy_tac.chuong_trinh)
    if thieu := dem_quy_tac - dem_dats:
        loi.append(f"Thiếu chương trình trong đề án để gắn quy tắc: {', '.join(sorted(thieu))}.")

    co_so = phang.get("dats_tru_so", [])
    co_so_theo_id = {r["id"]: _ten_doi_chieu(r["ten_co_so"]) for r in co_so}
    ten_theo_ma = {r.ma_co_so: _ten_doi_chieu(r.ten_co_so) for r in quy_tac.co_so}
    theo_ten = {co_so_theo_id[r["id"]]: r for r in co_so}
    tru_so_chinh = {co_so_theo_id[r["id"]] for r in co_so if r.get("vai_tro") == "chinh"}
    for r in quy_tac.co_so:
        ten = ten_theo_ma[r.ma_co_so]
        tru_so_chinh.discard(ten)
        if r.la_tru_so_chinh:
            tru_so_chinh.add(ten)
    if len(theo_ten) != len(co_so) or len(set(ten_theo_ma.values())) != len(quy_tac.co_so):
        loi.append("Tên cơ sở phải duy nhất trong mỗi khối dữ liệu")
    if not set(ten_theo_ma.values()) <= theo_ten.keys():
        loi.append("quy_tac_xet_tuyen/co_so: tên cơ sở phải khớp dats_tuyen_sinh/dats_tru_so")
    for cs in quy_tac.co_so:
        if (tinh := theo_ten.get(ten_theo_ma[cs.ma_co_so], {}).get("ma_tinh")) and cs.ma_tinh and tinh != cs.ma_tinh:
            loi.append(f"quy_tac_xet_tuyen/co_so/{cs.ma_co_so}: mã tỉnh khác cơ sở trong đề án")

    co_so_mac_dinh = next(iter(tru_so_chinh)) if len(tru_so_chinh) == 1 else None

    def co_so_quy_tac(ct: ChuongTrinhChuan) -> str | None:
        return ten_theo_ma.get(ct.ma_co_so) if ct.ma_co_so is not None else co_so_mac_dinh

    quy_tac_theo_ma: dict[str, list[ChuongTrinhChuan]] = defaultdict(list)
    for ct in quy_tac.chuong_trinh:
        quy_tac_theo_ma[ct.ma_xet_tuyen].append(ct)
    ct_quy_tac_theo_id: dict[int, ChuongTrinhChuan] = {}
    da_khop: set[str] = set()
    for ct in cac_ct:
        ma = ct["ma_xet_tuyen"]
        vi_tri = f"dats_chuong_trinh_dao_tao/{ma}"
        gioi_han = ct.get("chi_tieu_tuyen_sinh")
        ten_ct = _ten_doi_chieu(ct["ten_chuong_trinh"])
        ten_co_so = co_so_theo_id.get(ct.get("co_so_id"))
        ket_qua = quy_tac_theo_ma[ma]
        if not ket_qua:
            continue
        if dem_dats[ma] == dem_quy_tac[ma] == 1:
            doi_chieu = ket_qua[0]
        else:
            theo_ten_ct = [q for q in ket_qua if _ten_doi_chieu(q.ten_chuong_trinh) == ten_ct]
            if len(theo_ten_ct) > 1 and ten_co_so is not None:
                theo_ten_ct = [q for q in theo_ten_ct if co_so_quy_tac(q) == ten_co_so]
            if not theo_ten_ct:
                continue
            if len(theo_ten_ct) != 1 or theo_ten_ct[0].ma_chuong_trinh in da_khop:
                loi.append(f"{vi_tri}: cần tên và cơ sở để định danh mã xét tuyển có nhiều dòng")
                continue
            doi_chieu = theo_ten_ct[0]
        ct_quy_tac_theo_id[ct["id"]] = doi_chieu
        da_khop.add(doi_chieu.ma_chuong_trinh)
        if ten_ct != _ten_doi_chieu(doi_chieu.ten_chuong_trinh):
            loi.append(f"{vi_tri}/ten_chuong_trinh: tên chương trình khác giữa đề án và quy tắc")
        if gioi_han is not None and doi_chieu.chi_tieu is not None and gioi_han != doi_chieu.chi_tieu:
            loi.append(f"{vi_tri}: chỉ tiêu khác giữa đề án và quy tắc")
        if ct.get("ma_nganh") and doi_chieu.ma_nganh and ct["ma_nganh"] != doi_chieu.ma_nganh:
            loi.append(f"{vi_tri}: mã ngành khác giữa đề án và quy tắc")
        ten_co_so_quy_tac = co_so_quy_tac(doi_chieu)
        if ten_co_so and ten_co_so_quy_tac and ten_co_so_quy_tac != ten_co_so:
            loi.append(f"{vi_tri}: mã cơ sở của quy tắc không khớp cơ sở trong đề án")

    for ct in quy_tac.chuong_trinh:
        if ct.ma_chuong_trinh not in da_khop:
            loi.append(f"quy_tac_xet_tuyen/chuong_trinh/{ct.ma_chuong_trinh}: chưa xác định được dòng chương trình trong đề án")
    return _kiem_phuong_thuc(phang, quy_tac, ct_quy_tac_theo_id, loi)


def _to_hop_phuong_thuc(pt: dict, chi_tiet: list, ma_rieng: dict[str, str], vi_tri: str, loi: list[str]) -> set[str]:
    cac_mang = {}
    for khoa, gia_tri in (
        ("to_hop_mon_hoc", pt.get("to_hop_mon_hoc")),
        ("to_hop_ids", pt.get("to_hop_ids")),
        ("dats_phuong_thuc_to_hop", chi_tiet or None),
    ):
        if gia_tri is None:
            continue
        if not isinstance(gia_tri, list) or any(not isinstance(ma, str) or not ma.strip() for ma in gia_tri):
            loi.append(f"{vi_tri}/{khoa}: phải là mảng mã tổ hợp. Hãy dùng mã thay cho ID danh mục.")
            continue
        cac_mang[khoa] = {ma_rieng.get(ma, ma) for ma in gia_tri}
        if len(cac_mang[khoa]) != len(gia_tri):
            loi.append(f"{vi_tri}/{khoa}: có mã tổ hợp bị lặp")
    if pt.get("to_hop_id") is not None:
        loi.append(f"{vi_tri}/to_hop_id: hãy dùng mã tổ hợp trong to_hop_mon_hoc thay cho ID danh mục")
    chinh = cac_mang.get("to_hop_mon_hoc")
    bi_danh = cac_mang.get("to_hop_ids")
    if chinh is not None and bi_danh is not None and chinh != bi_danh:
        loi.append(f"{vi_tri}: to_hop_mon_hoc và to_hop_ids khai hai danh sách mã khác nhau")
    ma_chi_tiet = cac_mang.get("dats_phuong_thuc_to_hop", set())
    da_khai = chinh if chinh is not None else bi_danh
    if da_khai is not None and not ma_chi_tiet.issubset(da_khai):
        loi.append(f"{vi_tri}: mã trong bảng tổ hợp chi tiết khác danh sách của phương thức")
    return da_khai if da_khai is not None else ma_chi_tiet


def _kiem_phuong_thuc(
    phang: dict, quy_tac: DeAnXetTuyenChuan, ct_quy_tac_theo_id: dict[int, ChuongTrinhChuan], loi: list[str]
) -> dict[tuple[str, str], int]:
    cong_thuc = {c.ma_cong_thuc: c for c in quy_tac.cong_thuc}
    to_hop_theo_pt = defaultdict(list)
    for so, row in enumerate(phang.get("dats_phuong_thuc_to_hop", [])):
        if row.get("to_hop_id") is not None:
            loi.append(f"dats_phuong_thuc_to_hop/{so}/to_hop_id: hãy dùng ma_to_hop thay cho ID danh mục")
        else:
            to_hop_theo_pt[row.get("de_an_phuong_thuc_id")].append(row.get("ma_to_hop"))
    ma_rieng = {f"{quy_tac.ma_truong}-{t.ma_to_hop}": t.ma_to_hop for t in quy_tac.to_hop_rieng}
    phuong_thuc_theo_ct = defaultdict(list)
    for so, pt in enumerate(phang.get("dats_phuong_thuc", [])):
        vi_tri = f"dats_phuong_thuc/{so}"
        ct_id = pt.get("de_an_chuong_trinh_id")
        to_hop = _to_hop_phuong_thuc(pt, to_hop_theo_pt[pt["id"]], ma_rieng, vi_tri, loi)
        ma_ct = (pt.get("cong_thuc_tinh_diem") or "").strip()
        ma_ct = ma_ct if ma_ct in cong_thuc or _MA_CONG_THUC.fullmatch(ma_ct) else None
        phuong_thuc_theo_ct[ct_id].append((vi_tri, pt, ma_ct, to_hop))

    ket_qua = {}
    for ct_id, chuong_trinh in ct_quy_tac_theo_id.items():
        cac_pt = phuong_thuc_theo_ct[ct_id]
        pa_theo_bo = Counter(
            cong_thuc[pa.ma_cong_thuc].ma_phuong_thuc_cua_bo
            for pa in chuong_trinh.phuong_an if pa.ma_cong_thuc in cong_thuc
        )
        da_noi = defaultdict(set)
        to_hop_theo_phuong_an = defaultdict(set)
        for so, pa in enumerate(chuong_trinh.phuong_an):
            ct = cong_thuc.get(pa.ma_cong_thuc)
            vi_tri = f"quy_tac_xet_tuyen/chuong_trinh/{chuong_trinh.ma_chuong_trinh}/phuong_an/{so}"
            if ct is None:
                loi.append(f"{vi_tri}: công thức {pa.ma_cong_thuc} không tồn tại")
                continue
            cung_ma = [
                (pt, ma) for _, pt, ma, _ in cac_pt
                if pt.get("ma_phuong_thuc_cua_bo") == ct.ma_phuong_thuc_cua_bo
            ]
            if pa.ma_phuong_thuc_cua_truong is not None:
                ung_vien = [pt for pt, _ in cung_ma if pt.get("ma_phuong_thuc_cua_truong") == pa.ma_phuong_thuc_cua_truong]
            else:
                ung_vien = [pt for pt, ma in cung_ma if ma == pa.ma_cong_thuc]
                if not ung_vien and len(cung_ma) == pa_theo_bo[ct.ma_phuong_thuc_cua_bo] == 1 and cung_ma[0][1] is None:
                    ung_vien = [cung_ma[0][0]]
            if len(ung_vien) != 1:
                loi.append(
                    f"{vi_tri}: cần đúng một phương thức đề án cho công thức {pa.ma_cong_thuc}. "
                    "Hãy đối chiếu mã Bộ, mã phương thức của trường và mã công thức."
                )
                continue
            id_pt = ung_vien[0]["id"]
            khoa = (chuong_trinh.ma_chuong_trinh, pa.ma_cong_thuc)
            if khoa in ket_qua:
                loi.append(f"{vi_tri}: công thức {pa.ma_cong_thuc} đã được khai cho chương trình này")
                continue
            ket_qua[khoa] = id_pt
            da_noi[id_pt].add(pa.ma_cong_thuc)
            if ct.kieu_tinh == "TO_HOP_MON":
                ma_to_hop = {ma_rieng.get(ma, ma) for ma in pa.to_hop}
                if len(ma_to_hop) != len(pa.to_hop):
                    loi.append(f"{vi_tri}/to_hop: có mã tổ hợp bị lặp sau khi chuẩn hóa")
                to_hop_theo_phuong_an[id_pt].update(ma_to_hop)

        for vi_tri, pt, ma_ct, to_hop in cac_pt:
            id_pt = pt["id"]
            if id_pt in da_noi and ma_ct is not None and ma_ct not in da_noi[id_pt]:
                loi.append(f"{vi_tri}: công thức {ma_ct} không khớp phương án của phương thức này")
            if to_hop and not to_hop_theo_phuong_an[id_pt].issubset(to_hop):
                loi.append(f"{vi_tri}: mã tổ hợp không khớp phạm vi của các công thức đã đối chiếu")
    return ket_qua


def validate_admission_payload(payload: dict, ma_truong: str, nam_tuyen_sinh: int) -> dict[tuple[str, str], int]:
    """Kiểm tra đúng cấu trúc xuất và đối chiếu các nhánh trước khi nhập."""
    if not isinstance(payload, dict) or set(payload) != _CAC_KHOI or any(
        not isinstance(khoi, dict) for khoi in payload.values()
    ):
        raise DatsImportError("JSON cần đúng ba object thong_tin_import, dats_tuyen_sinh và quy_tac_xet_tuyen")
    try:
        json.dumps(payload, allow_nan=False)
    except (TypeError, ValueError):
        raise DatsImportError("Dữ liệu phải là JSON hợp lệ và chỉ chứa số hữu hạn") from None
    thong_tin = payload["thong_tin_import"]
    if set(thong_tin) - {"ma_truong", "nam_tuyen_sinh", "xu_ly_khi_da_ton_tai"}:
        raise DatsImportError("thong_tin_import có trường ngoài mẫu import")
    if (
        thong_tin.get("ma_truong") != ma_truong
        or type(thong_tin.get("nam_tuyen_sinh")) is not int
        or thong_tin["nam_tuyen_sinh"] != nam_tuyen_sinh
    ):
        raise DatsImportError("thong_tin_import phải khớp mã trường và năm của phiên")
    if thong_tin.get("xu_ly_khi_da_ton_tai", "tu_choi") != "tu_choi":
        raise DatsImportError("thong_tin_import/xu_ly_khi_da_ton_tai phải là tu_choi")

    de_an = doi_ten_bang_viet_tat(payload["dats_tuyen_sinh"])
    loi: list[str] = []
    _cau_truc_dats("dats_tuyen_sinh", de_an, "dats_tuyen_sinh", ma_truong, nam_tuyen_sinh, loi)
    if loi:
        raise DatsImportError(loi[0], loi)

    quy_tac = {
        "phien_ban": PHIEN_BAN_QUY_TAC,
        "ma_truong": ma_truong,
        "nam_tuyen_sinh": nam_tuyen_sinh,
        "de_an": {"ten_de_an": de_an.get("ten_de_an") or f"Đề án tuyển sinh {nam_tuyen_sinh} {ma_truong}"},
        **payload[KHOA_QUY_TAC],
    }
    if quy_tac["ma_truong"] != ma_truong or quy_tac["nam_tuyen_sinh"] != nam_tuyen_sinh:
        raise DatsImportError(f"{KHOA_QUY_TAC}: mã trường và năm phải khớp phiên")
    cong_thuc = quy_tac.get("cong_thuc")
    if isinstance(cong_thuc, list):
        for so, dong in enumerate(cong_thuc):
            if isinstance(dong, dict):
                ma = dong.get("ma_phuong_thuc_cua_bo")
                if not isinstance(ma, str) or not ma.strip():
                    loi.append(f"{KHOA_QUY_TAC}/cong_thuc/{so}/ma_phuong_thuc_cua_bo: cần nhập dữ liệu")
    if loi:
        raise DatsImportError(loi[0], loi)
    try:
        doc = doc_cau_truc(quy_tac, strict=True)
    except XetTuyenImportError as exc:
        loi = [f"{KHOA_QUY_TAC}/{dong}" for dong in exc.loi]
        raise DatsImportError(loi[0], loi) from None

    phang = flatten_nested_document({**payload, "dats_tuyen_sinh": de_an})
    phuong_thuc = _trung_doi_chieu(doc, phang, loi)
    diem_chuan_da_gap = set()
    ma_to_hop_rieng = {f"{ma_truong}-{th.ma_to_hop}": th.ma_to_hop for th in doc.to_hop_rieng}
    for so, dong in enumerate(doc.diem_chuan):
        vi_tri = f"{KHOA_QUY_TAC}/diem_chuan/{so}"
        ma_to_hop = ma_to_hop_rieng.get(dong.ma_to_hop, dong.ma_to_hop)
        khoa = (dong.nam_tuyen_sinh, dong.ma_xet_tuyen, dong.ma_phuong_thuc_cua_bo, ma_to_hop)
        if khoa in diem_chuan_da_gap:
            loi.append(f"{vi_tri}: điểm chuẩn lặp trường dữ liệu năm, mã xét tuyển, phương thức và tổ hợp")
        diem_chuan_da_gap.add(khoa)
        if not dong.ma_xet_tuyen.strip():
            loi.append(f"{vi_tri}: mã xét tuyển không hợp lệ")
        if not 0 <= dong.nam_tuyen_sinh <= 65535:  # xt_diem_chuan.nam_tuyen_sinh là SMALLINT UNSIGNED.
            loi.append(f"{vi_tri}: năm điểm chuẩn không hợp lệ")
    if loi:
        raise DatsImportError(loi[0], loi)
    return phuong_thuc


def import_approved_admission(
    db: Session, payload: dict, ma_truong: str, nam_tuyen_sinh: int, nguoi_duyet_id: int
) -> tuple[int, dict[str, int], KetQuaNhap]:
    """Ghi đề án và quy tắc ở trạng thái thử nghiệm. Transaction do nơi gọi quản lý."""
    phuong_thuc_theo_phuong_an = validate_admission_payload(payload, ma_truong, nam_tuyen_sinh)
    de_an = payload["dats_tuyen_sinh"]
    if (id_nam_truoc := de_an.get("de_an_nam_truoc_id")) is not None and db.scalar(
        select(DatsTuyenSinh.id).where(
            DatsTuyenSinh.id == id_nam_truoc,
            DatsTuyenSinh.ma_truong == ma_truong,
            DatsTuyenSinh.nam_tuyen_sinh < nam_tuyen_sinh,
        )
    ) is None:
        raise DatsImportError("dats_tuyen_sinh/de_an_nam_truoc_id: cần đề án năm trước của cùng trường")
    document = {
        **payload,
        "dats_tuyen_sinh": {**de_an, "trang_thai": "nhap", "trang_thai_xet_tuyen": THU_NGHIEM},
    }
    de_an_id, counts, quy_tac = import_day_du(
        db,
        ma_truong,
        nam_tuyen_sinh,
        document,
        nguoi_import_id=nguoi_duyet_id,
        chuan_hoa_quy_tac=False,
        noi_dung_da_duyet=True,
        giu_diem_chuan_ngoai_file=True,
        phuong_thuc_theo_phuong_an=phuong_thuc_theo_phuong_an,
    )
    assert quy_tac is not None  # validate_admission_payload đã yêu cầu khối quy tắc.
    return de_an_id, counts, quy_tac
