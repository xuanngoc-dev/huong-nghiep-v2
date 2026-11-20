"""Đối chiếu bản nháp với danh mục mã và phạm vi chỉ tiêu đã công bố."""

import re
from collections import defaultdict


_DU_KIEN = re.compile(r"\bdự\s+kiến\b|\bdu-kien\b", re.IGNORECASE)
_DUONG_DAN_CHUONG_TRINH = "/dats_tuyen_sinh/dats_chuong_trinh_dao_tao"


def _ma_xet_tuyen(gia_tri) -> str:
    return gia_tri.strip().upper() if isinstance(gia_tri, str) else ""


def _pham_vi_chi_tieu(chuong_trinh: dict) -> tuple | None:
    ke_hoach = chuong_trinh.get("dats_ke_hoach_tuyen_sinh")
    if not isinstance(ke_hoach, list) or len(ke_hoach) != 1 or not isinstance(ke_hoach[0], dict):
        return None
    pham_vi = tuple(ke_hoach[0].get(k) for k in ("dot_tuyen_sinh", "pham_vi_tuyen_sinh", "don_vi_chi_tieu"))
    if not all(isinstance(x, str) and x.strip() for x in pham_vi):
        return None
    return (chuong_trinh.get("co_so_id"), *(x.strip().casefold() for x in pham_vi))


def _don_vi_tong(tong: int, trich_dan: str) -> str | None:
    don_vi = re.search(
        rf"(?<![\w.,]){tong}\s+(?P<ma>mã\s+(?:xét\s+)?tuyển)\b"
        rf"|(?<![\w.,]){tong}\s+(?:(?:ngành\s*(?:/|,|và)\s*)?(?:chương\s+trình|CTĐT))\b",
        trich_dan, re.IGNORECASE,
    )
    if don_vi is None:
        return None
    return "mã xét tuyển" if don_vi.group("ma") else "chương trình"


def _kiem_chuong_trinh(
    chuong_trinh: list[dict], doi_chieu: list[dict], ds_nguon: dict[int, dict],
) -> tuple[list[str], str | None, list[str]]:
    cac_ma_nhap = [ma for ct in chuong_trinh if (ma := _ma_xet_tuyen(ct.get("ma_xet_tuyen")))]
    ma_nhap = set(cac_ma_nhap)
    so_da_luu = {"mã xét tuyển": len(ma_nhap), "chương trình": len(cac_ma_nhap)}
    ma_theo_nguon = defaultdict(set)
    tong_theo_nguon = defaultdict(set)
    nguon_theo_tong = defaultdict(lambda: defaultdict(set))
    for dong in doi_chieu:
        nguon_id = dong["nguon_id"]
        if nguon_id not in ds_nguon or dong.get("pham_vi") != "toan_truong":
            continue
        ma_theo_nguon[nguon_id].update(ma for x in dong.get("cac_ma", []) if (ma := _ma_xet_tuyen(x)))
        tong = dong.get("tong_cong_bo")
        if type(tong) is int and tong > 0:
            don_vi = _don_vi_tong(tong, dong.get("trich_dan") or "")
            tong_theo_nguon[nguon_id].add((don_vi, tong))
            nguon_theo_tong[don_vi][tong].add(nguon_id)

    loi = []
    ghi_chu = []
    can_xac_nhan_tong = []
    da_doi_chieu_du = False
    for nguon_id, cac_ma in ma_theo_nguon.items():
        if thieu := sorted(cac_ma - ma_nhap):
            loi.append(f"{_DUONG_DAN_CHUONG_TRINH}: thiếu mã công bố ở nguồn #{nguon_id}: {', '.join(thieu)}.")
        if cac_ma and cac_ma == ma_nhap and any(
            so_da_luu.get(don_vi, len(ma_nhap)) == tong for don_vi, tong in tong_theo_nguon[nguon_id]
        ):
            da_doi_chieu_du = True

    for don_vi, theo_tong in nguon_theo_tong.items():
        if don_vi is None or len(theo_tong) > 1:
            if don_vi is None and da_doi_chieu_du and set(theo_tong) == {len(ma_nhap)}:
                continue
            ds_tong = ", ".join(str(tong) for tong in sorted(theo_tong))
            ly_do = f"Cần đối chiếu đơn vị và phạm vi của tổng công bố ({ds_tong}); bản nháp đã lưu {len(ma_nhap)} mã xét tuyển."
            can_xac_nhan_tong.append(ly_do)
            ghi_chu.append(ly_do)
            continue
        tong, ds_nguon_id = next(iter(theo_tong.items()))
        da_luu = so_da_luu[don_vi]
        if da_luu == tong:
            continue
        ten_nguon = ", ".join(f"#{nguon_id}" for nguon_id in sorted(ds_nguon_id))
        chenh = f"thiếu {tong - da_luu}" if da_luu < tong else f"thừa {da_luu - tong}"
        bao_cao = f"Bản nháp đã lưu {da_luu}/{tong} {don_vi} so với tổng công bố toàn trường (nguồn {ten_nguon}), {chenh}."
        if da_luu < tong:
            ma_con_thieu = set().union(*(ma_theo_nguon[nguon_id] for nguon_id in ds_nguon_id)) - ma_nhap
            if ma_con_thieu:
                bao_cao += f" Mã công bố còn thiếu: {', '.join(sorted(ma_con_thieu))}."
            if (chua_ro := tong - da_luu - len(ma_con_thieu)) > 0:
                bao_cao += f" Chưa xác minh được mã cụ thể của {chua_ro} mục còn thiếu."
        loi.append(f"{_DUONG_DAN_CHUONG_TRINH}: {bao_cao}")
        ghi_chu.append(bao_cao)

    if loi or (da_doi_chieu_du and not can_xac_nhan_tong):
        return loi, None, ghi_chu
    xac_nhan = " ".join(can_xac_nhan_tong) or "Chưa đối chiếu đủ danh sách mã với bảng công bố toàn trường."
    return loi, f"{xac_nhan} Hãy xác nhận phạm vi đã kiểm và ghi lý do.", ghi_chu


def _kiem_chi_tieu(de_an: dict, chuong_trinh: list[dict]) -> tuple[str | None, str | None]:
    tong = de_an.get("chi_tieu")
    cac_chi_tieu = [ct.get("chi_tieu_tuyen_sinh") for ct in chuong_trinh]
    if not chuong_trinh or (tong is None and not any(i is not None for i in cac_chi_tieu)):
        return None, None
    kieu = [ct.get("kieu_phan_bo_chi_tieu") for ct in chuong_trinh]
    pham_vi = [_pham_vi_chi_tieu(ct) for ct in chuong_trinh]
    chia_rieng = all(x == "theo_chuong_trinh" for x in kieu)
    cung_pham_vi = pham_vi[0] is not None and all(x == pham_vi[0] for x in pham_vi)
    if type(tong) is int and all(type(x) is int for x in cac_chi_tieu):
        cong = sum(cac_chi_tieu)
        if chia_rieng and cung_pham_vi:
            if cong != tong:
                return f"/dats_tuyen_sinh/chi_tieu: tổng chỉ tiêu chương trình cùng phạm vi là {cong}, đề án ghi {tong}.", None
            return None, None
        if len(chuong_trinh) == 1 and cong == tong and kieu[0] in (None, "theo_chuong_trinh"):
            return None, None
    return None, "Hãy xác nhận phạm vi, chỉ tiêu dùng chung hoặc nguyên nhân không đối chiếu được tổng chỉ tiêu, kèm căn cứ."


def _kiem_urls(de_an: dict, quy_tac: dict, ds_nguon: dict[int, dict]) -> list[str]:
    goc = de_an.get("nguon_du_lieu_url")
    de_an_quy_tac = quy_tac.get("de_an")
    url_quy_tac = de_an_quy_tac.get("nguon_du_lieu_url") if isinstance(de_an_quy_tac, dict) else None
    urls = {
        n["url"] for n in ds_nguon.values()
        if n.get("loai") not in {"phu_luc", "dieu_chinh"}
        and not _DU_KIEN.search(f"{n.get('tieu_de', '')} {n['url']}")
    }
    loi = []
    if not isinstance(goc, str) or goc not in urls:
        loi.append("/dats_tuyen_sinh/nguon_du_lieu_url: cần URL đề án trong nguồn chính thức đã chọn của năm tuyển sinh.")
    if not isinstance(url_quy_tac, str) or url_quy_tac != goc:
        loi.append("/quy_tac_xet_tuyen/de_an/nguon_du_lieu_url: URL phải khớp nguồn đề án của nhánh dats_tuyen_sinh.")
    return loi


def kiem_tra_doi_chieu(du_lieu: dict, nguon: list[dict], nam: int, doi_chieu: dict) -> tuple[list[str], dict[str, str]]:
    de_an = du_lieu.get("dats_tuyen_sinh")
    quy_tac = du_lieu.get("quy_tac_xet_tuyen")
    if not isinstance(de_an, dict) or not isinstance(quy_tac, dict):
        return [], {}
    ds_nguon = nguon_doi_chieu(nguon, nam)
    loi = _kiem_urls(de_an, quy_tac, ds_nguon)
    cac_chuong_trinh = de_an.get("dats_chuong_trinh_dao_tao")
    if not isinstance(cac_chuong_trinh, list) or not all(isinstance(ct, dict) for ct in cac_chuong_trinh):
        return loi, {}
    loi_ma, xac_nhan_ma, _ = _kiem_chuong_trinh(cac_chuong_trinh, doi_chieu.get("nguon", []), ds_nguon)
    loi.extend(loi_ma)
    loi_chi_tieu, xac_nhan_chi_tieu = _kiem_chi_tieu(de_an, cac_chuong_trinh)
    if loi_chi_tieu:
        loi.append(loi_chi_tieu)
    can_xac_nhan = {k: v for k, v in (("chuong_trinh", xac_nhan_ma), ("chi_tieu", xac_nhan_chi_tieu)) if v}
    return loi, can_xac_nhan


def ghi_chu_doi_chieu_chuong_trinh(du_lieu: dict, doi_chieu: dict, nguon: list[dict], nam: int) -> list[str]:
    de_an = du_lieu.get("dats_tuyen_sinh")
    cac_chuong_trinh = de_an.get("dats_chuong_trinh_dao_tao") if isinstance(de_an, dict) else None
    if not isinstance(cac_chuong_trinh, list) or not all(isinstance(ct, dict) for ct in cac_chuong_trinh):
        return []
    _, _, ghi_chu = _kiem_chuong_trinh(cac_chuong_trinh, doi_chieu.get("nguon", []), nguon_doi_chieu(nguon, nam))
    return ghi_chu


def nguon_doi_chieu(nguon: list[dict], nam: int) -> dict[int, dict]:
    return {
        n["id"]: n for n in nguon
        if n.get("lua_chon") == "su_dung" and n.get("chinh_thuc") and n.get("phu_hop")
        and n.get("nam_ap_dung") == nam and not n.get("chi_diem_lich_su")
    }
