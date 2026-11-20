"""Đối chiếu dữ liệu bản nháp với dẫn chứng và ghi các thay đổi theo đường dẫn JSON."""

import re
from copy import deepcopy

from app.schemas.dats_thu_thap import SuaMucBanNhap
from app.services.dats_hop_dong_thu_thap import hoan_thien_cau_truc_cms

_BO_QUA = {"id", "tao_luc", "cap_nhat_luc", "de_an_id", "de_an_nam_truoc_id", "ghi_chu"}
_HE_THONG = {
    "/dats_tuyen_sinh/trang_thai",
    "/dats_tuyen_sinh/trang_thai_xet_tuyen",
    "/dats_tuyen_sinh/ma_truong",
    "/dats_tuyen_sinh/nam_tuyen_sinh",
    "/quy_tac_xet_tuyen/ma_truong",
    "/quy_tac_xet_tuyen/nam_tuyen_sinh",
    "/quy_tac_xet_tuyen/phien_ban",
}


def _ma_hoa(khoa: str) -> str:
    return khoa.replace("~", "~0").replace("/", "~1")


def _cac_doan(duong_dan: str) -> list[str]:
    if not duong_dan.startswith("/") or re.search(r"~(?![01])", duong_dan):
        raise ValueError(f"Đường dẫn JSON không hợp lệ: {duong_dan}.")
    return [p.replace("~1", "/").replace("~0", "~") for p in duong_dan[1:].split("/")]


def _chi_so(doan: str) -> int:
    if not re.fullmatch(r"0|[1-9][0-9]{0,8}", doan):
        raise KeyError(doan)
    return int(doan)


def _lay(goc, cac_doan: list[str]):
    for doan in cac_doan:
        goc = goc[_chi_so(doan) if isinstance(goc, list) else doan]
    return goc


def _muc_du_lieu(du_lieu: dict, mang_co_dan_chung: set[str]) -> dict:
    def duyet(gia_tri, duong_dan):
        if duong_dan in _HE_THONG:
            return
        if isinstance(gia_tri, dict) and gia_tri:
            for khoa, con in gia_tri.items():
                if khoa not in _BO_QUA:
                    yield from duyet(con, f"{duong_dan}/{_ma_hoa(khoa)}")
        elif isinstance(gia_tri, list) and gia_tri and (
            duong_dan not in mang_co_dan_chung or any(isinstance(i, (list, dict)) for i in gia_tri)
        ):
            for i, con in enumerate(gia_tri):
                yield from duyet(con, f"{duong_dan}/{i}")
        else:
            yield duong_dan, gia_tri

    return dict(duyet({k: v for k, v in du_lieu.items() if k != "thong_tin_import"}, ""))


def _giong_nhau(a, b) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_giong_nhau(x, y) for x, y in zip(a, b, strict=True))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_giong_nhau(a[k], b[k]) for k in a)
    return a == b


def _chua_xac_minh(gia_tri) -> bool:
    return gia_tri is None or gia_tri == [] or gia_tri == {}


def _nguon_hop_le(du_lieu: dict, duong_dan: str, nguon: dict, nam: int) -> bool:
    if not nguon.get("chinh_thuc") or not nguon.get("phu_hop") or nguon.get("lua_chon") != "su_dung":
        return False
    tach = _cac_doan(duong_dan)
    if tach[:2] == ["quy_tac_xet_tuyen", "diem_chuan"] and len(tach) >= 4:
        dong = _lay(du_lieu, tach[:3])
        if not isinstance(dong, dict):
            return False
        nam_diem = dong.get("nam_tuyen_sinh", nam)
        # Năm hiện tại cũng phải có URL công bố đúng bản ghi điểm chuẩn.
        return nguon.get("nam_ap_dung") == nam_diem and nguon["url"] == dong.get("nguon_du_lieu_url")
    return not nguon.get("chi_diem_lich_su") and nguon.get("nam_ap_dung") == nam


def _muc_moi(duong_dan: str, gia_tri, *, tu_ai: bool = False) -> dict:
    return {
        "duong_dan": duong_dan,
        "gia_tri_ai": gia_tri if tu_ai else None,
        "dan_chung": [],
        "dan_chung_ids": [],
        "ghi_chu": "",
        "da_kiem_tra": False,
        "mau_thuan": False,
    }


def _co_mau_thuan(dan_chung: list[dict]) -> bool:
    return any(not _giong_nhau(dc["gia_tri"], dan_chung[0]["gia_tri"]) for dc in dan_chung[1:])


def lap_muc_ban_nhap(du_lieu: dict, muc_ai: list[dict], nguon: list[dict], nam: int) -> list[dict]:
    """Gắn dẫn chứng vào các mục thực sự có trong dữ liệu nháp."""
    theo_duong_dan = {}
    for item in muc_ai:
        theo_duong_dan.setdefault(item["duong_dan"], []).append(item)

    ket_qua = []
    ds_nguon = {n["id"]: n for n in nguon}
    for duong_dan, gia_tri in _muc_du_lieu(du_lieu, set(theo_duong_dan)).items():
        muc = _muc_moi(duong_dan, gia_tri, tu_ai=True)
        de_xuat = theo_duong_dan.get(duong_dan, [])
        for item in de_xuat:
            for dc in item["dan_chung"]:
                if dc["nguon_id"] not in ds_nguon or len(muc["dan_chung"]) >= 50:
                    continue
                muc["dan_chung"].append({**dc, "id": str(len(muc["dan_chung"]) + 1)})
        muc["mau_thuan"] = any(item.get("mau_thuan") for item in de_xuat) or _co_mau_thuan(muc["dan_chung"])
        muc["ghi_chu"] = next((i["ghi_chu"] for i in de_xuat if i.get("ghi_chu")), "")
        if _chua_xac_minh(gia_tri) and not muc["ghi_chu"]:
            muc["ghi_chu"] = "Chưa tìm thấy dữ liệu cho mục này trong các tài liệu đã chọn."
        for dc in muc["dan_chung"]:
            if _giong_nhau(dc["gia_tri"], gia_tri) and _nguon_hop_le(
                du_lieu, duong_dan, ds_nguon[dc["nguon_id"]], nam
            ):
                muc["dan_chung_ids"].append(dc["id"])
        ket_qua.append(muc)
    return ket_qua


def sua_muc_ban_nhap(du_lieu: dict, muc: list[dict], thay_doi: list[SuaMucBanNhap], nguon: list[dict]):
    """Áp dụng thay đổi và giữ bản gốc, giá trị trước/sau cùng dẫn chứng đã chọn."""
    ket_qua = deepcopy(du_lieu)
    da_co = {i["duong_dan"]: deepcopy(i) for i in muc}
    mang_co_dan_chung = da_co.keys() | {i.duong_dan for i in thay_doi if i.dan_chung_moi}
    ds_nguon = {n["id"]: n for n in nguon}
    nhat_ky = []
    for sua in thay_doi:
        path = sua.duong_dan
        cac_doan = _cac_doan(path)
        if len(cac_doan) < 2 or cac_doan[0] == "thong_tin_import" or path in _HE_THONG:
            raise ValueError(f"Không thể sửa trường do hệ thống quản lý: {path}.")
        try:
            cha = _lay(ket_qua, cac_doan[:-1])
            if not isinstance(cha, (dict, list)):
                raise TypeError("Trường cha phải là object hoặc mảng.")
            khoa = _chi_so(cac_doan[-1]) if isinstance(cha, list) else cac_doan[-1]
            gia_tri_cu = cha.get(khoa) if isinstance(cha, dict) else cha[khoa]
        except (IndexError, KeyError, TypeError) as exc:
            raise ValueError(f"Không tìm thấy vị trí dữ liệu: {path}.") from exc

        truoc = da_co.get(path)
        moi = deepcopy(truoc) if truoc else _muc_moi(path, None)
        gia_tri = sua.gia_tri if "gia_tri" in sua.model_fields_set else gia_tri_cu
        them_muc = isinstance(cha, dict) and khoa not in cha and "gia_tri" in sua.model_fields_set
        doi_gia_tri = them_muc or not _giong_nhau(gia_tri, gia_tri_cu)
        if doi_gia_tri:
            cha[khoa] = gia_tri
            # Khi thay một mảng/nhóm, các chỉ số hoặc trường con có thể đã đổi nghĩa.
            da_co = {p: i for p, i in da_co.items() if not p.startswith(path + "/")}

        ids = list(dict.fromkeys(sua.dan_chung_ids))
        if set(ids) - {d["id"] for d in moi["dan_chung"]}:
            raise ValueError(f"Dẫn chứng được chọn không thuộc mục {path}.")
        if len(moi["dan_chung"]) + len(sua.dan_chung_moi) > 50:
            raise ValueError(f"Mục {path} có quá 50 dẫn chứng.")
        for dc in sua.dan_chung_moi:
            if dc.nguon_id not in ds_nguon:
                raise ValueError(f"Nguồn {dc.nguon_id} không thuộc phiên bản đang xét duyệt.")
            dc_id = str(len(moi["dan_chung"]) + 1)
            moi["dan_chung"].append({**dc.model_dump(), "id": dc_id})
            ids.append(dc_id)
        if (doi_gia_tri or sua.dan_chung_moi or (truoc and ids != truoc["dan_chung_ids"])) and not sua.ghi_chu:
            raise ValueError(f"Cần ghi lý do chỉnh sửa hoặc chọn dẫn chứng tại {path}.")
        moi.update(
            dan_chung_ids=ids,
            ghi_chu=sua.ghi_chu,
            da_kiem_tra=sua.da_kiem_tra,
            mau_thuan=moi["mau_thuan"] or _co_mau_thuan(moi["dan_chung"]),
        )
        if moi != truoc or doi_gia_tri:
            da_co[path] = moi
            nhat_ky.append({"duong_dan": path, "truoc": deepcopy(gia_tri_cu), "sau": deepcopy(gia_tri), "ghi_chu": sua.ghi_chu,
                           "dan_chung_ids": ids, "da_kiem_tra": sua.da_kiem_tra})

    ket_qua = hoan_thien_cau_truc_cms(ket_qua)
    cac_muc = []
    for p, v in _muc_du_lieu(ket_qua, mang_co_dan_chung).items():
        item = da_co.get(p)
        if item is None:
            item = _muc_moi(p, v)
            if _chua_xac_minh(v):
                item["ghi_chu"] = "Chưa tìm thấy dữ liệu cho mục này trong các tài liệu đã chọn."
        cac_muc.append(item)
    return ket_qua, cac_muc, nhat_ky


def loi_dan_chung(du_lieu: dict, muc: list[dict], nguon: list[dict], nam: int) -> list[str]:
    theo_duong_dan = {item["duong_dan"]: item for item in muc}
    ds_nguon = {n["id"]: n for n in nguon}
    loi = []
    for p, gia_tri in _muc_du_lieu(du_lieu, set(theo_duong_dan)).items():
        item = theo_duong_dan.get(p) or _muc_moi(p, gia_tri)
        da_chon = [dc for dc in item["dan_chung"] if dc["id"] in item["dan_chung_ids"]]
        if _chua_xac_minh(gia_tri):
            if not item["ghi_chu"].strip():
                loi.append(f"{p}: cần ghi chú lý do giữ giá trị trống.")
        elif gia_tri == "":
            loi.append(f"{p}: dùng null và ghi chú nếu chưa xác minh được giá trị.")
        elif not da_chon or not all(
            _giong_nhau(dc["gia_tri"], gia_tri) and dc["nguon_id"] in ds_nguon
            and _nguon_hop_le(du_lieu, p, ds_nguon[dc["nguon_id"]], nam) for dc in da_chon
        ):
            loi.append(f"{p}: cần dẫn chứng chính thức phù hợp với giá trị, trường và năm áp dụng.")
        if item["mau_thuan"] and (not item["da_kiem_tra"] or not item["ghi_chu"].strip()):
            loi.append(f"{p}: cần đối chiếu mâu thuẫn, xác nhận và ghi lý do.")
    return loi
