"""Các khóa phải có trong bản JSON CMS theo bố cục mẫu XDA."""

from copy import deepcopy
from dataclasses import dataclass
from urllib.parse import urlsplit

from app.services.dats_import import PHIEN_BAN_QUY_TAC, _DATS_FK, _MA_THAY_ID, _MODELS, _SKIP_COLUMNS, _kind


@dataclass(frozen=True)
class _Khoi:
    gia_tri: tuple[str, ...] = ()
    co_the_null: tuple[str, ...] = ()
    danh_sach: tuple[str, ...] = ()
    danh_sach_neu_co: tuple[str, ...] = ()
    danh_sach_bat_buoc: tuple[str, ...] = ()
    doi_tuong: tuple[str, ...] = ()


_DATS = ("dats_tuyen_sinh",)
_CHUONG_TRINH = (*_DATS, "dats_chuong_trinh_dao_tao")
_PHUONG_THUC = (*_CHUONG_TRINH, "dats_phuong_thuc")
_QUY_TAC = ("quy_tac_xet_tuyen",)
_QT_CT = (*_QUY_TAC, "chuong_trinh")
_QT_CT_CONG_THUC = (*_QUY_TAC, "cong_thuc")
_CHINH_SACH_CHUNG = (
    "ma_chinh_sach", "ten_chinh_sach", "nhom_doi_tuong", "can_cu_phap_ly", "mo_ta_doi_tuong", "mon_thi_linh_vuc",
    "muc_giai", "thoi_han_thanh_tich_nam", "pham_vi_chuong_trinh", "ho_so_minh_chung", "thu_tu_tieu_chi_xet",
    "tieu_chi_phu_khi_dong_diem", "thoi_gian_nhan_ho_so", "trang_thai", "ghi_chu",
)
_CAC_KHOI = {
    (): _Khoi(doi_tuong=("thong_tin_import", *_DATS, *_QUY_TAC)),
    ("thong_tin_import",): _Khoi(gia_tri=("ma_truong", "nam_tuyen_sinh", "xu_ly_khi_da_ton_tai")),
    _DATS: _Khoi(
        gia_tri=("trang_thai", "trang_thai_xet_tuyen"),
        co_the_null=("ten_de_an", "nguon_du_lieu_url", "chi_tieu", "gioi_thieu", "ngay_cong_bo", "ghi_chu", "de_an_nam_truoc_id"),
        danh_sach=(
            "hinh_thuc_dao_tao", "dats_tru_so", "dats_website", "dats_lien_he_tuyen_sinh", "dats_nhan_su",
            "dats_co_so_vat_chat", "dats_quy_mo_dao_tao", "dats_ty_le_viec_lam", "dats_doi_tuong_du_tuyen",
            "dats_chinh_sach_xet_tuyen_thang", "dats_chinh_sach_uu_tien_xet_tuyen",
        ),
        danh_sach_bat_buoc=("dats_chuong_trinh_dao_tao",),
        danh_sach_neu_co=("dats_quy_doi_nguong_dau_vao", "dats_quy_doi_diem_trung_tuyen"),
    ),
    _CHUONG_TRINH: _Khoi(
        gia_tri=("ma_xet_tuyen", "ten_chuong_trinh"),
        co_the_null=(
            "ma_nganh", "ma_xet_tuyen_nam_truoc", "trinh_do_dao_tao", "hinh_thuc_dao_tao", "co_so_id",
            "thoi_gian_dao_tao_nam", "ngon_ngu_dao_tao", "chi_tieu_tuyen_sinh", "kieu_phan_bo_chi_tieu", "ghi_chu",
        ),
        danh_sach=(
            "dats_ke_hoach_tuyen_sinh", "dats_trinh_do_nganh", "dats_quy_mo_dao_tao", "dats_quy_doi_nguong_dau_vao",
            "dats_quy_doi_diem_trung_tuyen", "dats_phuong_thuc",
        ),
    ),
    _PHUONG_THUC: _Khoi(
        gia_tri=("ma_phuong_thuc_cua_bo",),
        co_the_null=(
            "ma_phuong_thuc_cua_truong", "ten_phuong_thuc_cua_truong", "chi_tieu_phuong_thuc", "dieu_kien_can",
            "dieu_kien_du", "diem_san", "diem_chuan", "thang_diem", "cong_thuc_tinh_diem", "to_hop_mon_hoc",
            "thu_tu_uu_tien", "ghi_chu_chi_tieu", "ghi_chu",
        ),
        danh_sach=(
            "dats_phuong_thuc_to_hop", "dats_dieu_kien_du_tuyen", "dats_tieu_chi_xet_tuyen", "dats_diem_cong",
            "dats_quy_tac_phan_bo", "dats_ho_so_du_tuyen",
        ),
    ),
    (*_DATS, "dats_tru_so"): _Khoi(
        gia_tri=("ten_co_so",),
        co_the_null=("vai_tro", "loai_co_so", "dia_chi", "ma_tinh", "so_dien_thoai", "ghi_chu"),
    ),
    (*_DATS, "dats_website"): _Khoi(
        gia_tri=("url",), co_the_null=("loai_website", "ten_trang", "ghi_chu"),
    ),
    (*_DATS, "dats_lien_he_tuyen_sinh"): _Khoi(co_the_null=(
        "ten_don_vi", "ten_nguoi_lien_he", "chuc_vu", "so_dien_thoai", "email", "thoi_gian_lien_he", "ghi_chu",
    )),
    (*_DATS, "dats_doi_tuong_du_tuyen"): _Khoi(
        gia_tri=("ma_doi_tuong", "ten_doi_tuong"),
        co_the_null=(
            "mo_ta", "nam_tot_nghiep_tu", "nam_tot_nghiep_den", "pham_vi_ap_dung", "de_an_chuong_trinh_id",
            "trang_thai", "ghi_chu",
        ),
    ),
    (*_DATS, "dats_chinh_sach_xet_tuyen_thang"): _Khoi(co_the_null=(
        *_CHINH_SACH_CHUNG, "cap_thi", "dieu_kien_phu", "chi_tieu_tuyen_thang", "nguyen_tac_khi_vuot_chi_tieu",
    )),
    (*_DATS, "dats_chinh_sach_uu_tien_xet_tuyen"): _Khoi(co_the_null=(
        *_CHINH_SACH_CHUNG, "hinh_thuc_uu_tien", "loai_diem_cong", "muc_diem_cong", "dieu_kien_nguong_dau_vao",
        "chi_tieu_uu_tien",
    )),
    (*_CHUONG_TRINH, "dats_ke_hoach_tuyen_sinh"): _Khoi(co_the_null=(
        "don_vi_chi_tieu", "pham_vi_tuyen_sinh", "dot_tuyen_sinh", "thoi_gian_nhan_ho_so", "dieu_kien_chung", "ghi_chu",
    )),
    (*_CHUONG_TRINH, "dats_trinh_do_nganh"): _Khoi(co_the_null=(
        "trinh_do_dao_tao", "hinh_thuc_dao_tao", "thoi_gian_dao_tao_nam", "ma_nganh_chuan", "ghi_chu",
    )),
    (*_PHUONG_THUC, "dats_phuong_thuc_to_hop"): _Khoi(
        gia_tri=("ma_to_hop",), co_the_null=("thu_tu_hien_thi", "ghi_chu"),
    ),
    (*_PHUONG_THUC, "dats_tieu_chi_xet_tuyen"): _Khoi(
        gia_tri=("ma_tieu_chi", "ten_tieu_chi"),
        co_the_null=(
            "loai_tieu_chi", "thu_tu_ap_dung", "toan_tu_so_sanh", "gia_tri_tieu_chi", "noi_dung_tieu_chi",
            "nguon_du_lieu_url", "trang_thai", "ghi_chu",
        ),
    ),
    _QUY_TAC: _Khoi(
        gia_tri=("phien_ban",),
        doi_tuong=("de_an",),
        danh_sach=("co_so", "to_hop_rieng", "bang_quy_doi", "dieu_kien_chung", "diem_cong", "diem_chuan"),
        danh_sach_bat_buoc=("cong_thuc", "chuong_trinh"),
    ),
    (*_QUY_TAC, "de_an"): _Khoi(
        gia_tri=("ten_de_an",),
        co_the_null=("nguon_du_lieu_url", "so_quyet_dinh", "ngay_cong_bo", "ghi_chu"),
    ),
    (*_QUY_TAC, "co_so"): _Khoi(
        gia_tri=("ma_co_so", "ten_co_so"), co_the_null=("ma_tinh", "dia_chi", "la_tru_so_chinh"),
    ),
    (*_QUY_TAC, "to_hop_rieng"): _Khoi(
        gia_tri=("ma_to_hop", "ten_to_hop"), danh_sach_bat_buoc=("vi_tri",),
    ),
    (*_QUY_TAC, "bang_quy_doi"): _Khoi(
        gia_tri=("ma_bang", "ten_bang", "thang_diem_dich"),
        co_the_null=("ghi_chu",), danh_sach_bat_buoc=("muc",),
    ),
    (*_QUY_TAC, "bang_quy_doi", "muc"): _Khoi(
        gia_tri=("diem_quy_doi",),
        co_the_null=(
            "ma_chung_chi", "ma_bai_thi", "ma_mon_thay_the", "cap_do", "diem_tu", "diem_den", "he_so_noi_suy",
            "dat_nguong",
        ),
    ),
    _QT_CT_CONG_THUC: _Khoi(
        gia_tri=("ma_cong_thuc", "ten_cong_thuc", "ma_phuong_thuc_cua_bo", "kieu_tinh", "thang_diem"),
        co_the_null=(
            "nguon_diem_mon", "thay_ngoai_ngu", "ma_bang_quy_doi_ngoai_ngu", "he_so_nhan", "nguong_tb_mon",
            "nguong_thpt_to_hop", "diem_san", "ap_dung_diem_cong", "ap_dung_uu_tien", "ty_le_diem_cong_toi_da",
            "so_le_lam_tron", "mo_ta_cong_thuc", "dang_dung", "ghi_chu",
        ),
        danh_sach=("he_so_mon", "thanh_phan", "dieu_kien"),
    ),
    (*_QT_CT_CONG_THUC, "he_so_mon"): _Khoi(gia_tri=("he_so",), co_the_null=("ma_mon", "nhom_mon")),
    (*_QT_CT_CONG_THUC, "thanh_phan"): _Khoi(
        gia_tri=("vi_tri", "loai_nguon"),
        co_the_null=(
            "ten_thanh_phan", "ma_bai_thi", "ma_bang_quy_doi", "ma_mon", "he_so", "nam_thi_tu", "nam_thi_den",
            "yeu_cau_phan_tu_chon",
        ),
    ),
    (*_QUY_TAC, "diem_cong"): _Khoi(
        gia_tri=("loai_diem_cong", "nhom_cong", "ma_chi_so", "toan_tu", "gia_tri", "diem_cong"),
        co_the_null=("ma_cong_thuc", "khoa", "mo_ta"),
    ),
    _QT_CT: _Khoi(
        gia_tri=("ma_chuong_trinh", "ma_xet_tuyen", "ten_chuong_trinh"),
        co_the_null=("ma_nganh", "ma_co_so", "loai_chuong_trinh", "chi_tieu", "hoc_phi"),
        danh_sach=("dieu_kien_rieng",),
        danh_sach_bat_buoc=("phuong_an",),
    ),
    (*_QT_CT, "hoc_phi"): _Khoi(gia_tri=("hoc_phi_tu",), co_the_null=("nam_hoc", "hoc_phi_den", "ghi_chu")),
    (*_QT_CT, "phuong_an"): _Khoi(gia_tri=("ma_cong_thuc",), danh_sach=("to_hop",)),
    (*_QUY_TAC, "diem_chuan"): _Khoi(
        gia_tri=("nam_tuyen_sinh", "ma_xet_tuyen", "diem_chuan", "thang_diem"),
        co_the_null=("nguon_du_lieu_url", "ten_chuong_trinh", "ma_phuong_thuc_cua_bo", "ma_to_hop", "tieu_chi_phu"),
    ),
}

_NHOM_DIEU_KIEN = _Khoi(
    gia_tri=("ma_nhom", "ten_nhom"), co_the_null=("mo_ta", "bat_buoc", "ma_cong_thuc"),
    danh_sach_bat_buoc=("mot_trong",),
)
_DIEU_KIEN = _Khoi(gia_tri=("ma_chi_so", "toan_tu", "gia_tri"), co_the_null=("khoa", "mo_ta"))
for _duong_dan in ((*_QUY_TAC, "dieu_kien_chung"), (*_QT_CT, "dieu_kien_rieng"), (*_QT_CT_CONG_THUC, "dieu_kien")):
    _CAC_KHOI[_duong_dan] = _NHOM_DIEU_KIEN
    _CAC_KHOI[(*_duong_dan, "mot_trong")] = _DIEU_KIEN


def _doi_tuong(gia_tri, bang=(), vi_tri=""):
    if isinstance(gia_tri, dict):
        yield gia_tri, bang, vi_tri
        for khoa, con in gia_tri.items():
            yield from _doi_tuong(con, (*bang, khoa), f"{vi_tri}/{khoa}")
    elif isinstance(gia_tri, list):
        for so, con in enumerate(gia_tri):
            yield from _doi_tuong(con, bang, f"{vi_tri}/{so}")


def _co_khoa_tuong_duong(doi_tuong: dict, bang: tuple, khoa: str) -> bool:
    return bang == _PHUONG_THUC and khoa == "to_hop_mon_hoc" and "to_hop_ids" in doi_tuong


def hoan_thien_cau_truc_cms(payload: dict) -> dict:
    """Bổ sung vỏ cấu trúc và chuẩn hóa chuỗi trống ở trường được phép null."""
    du_lieu = deepcopy(payload)
    for doi_tuong, bang, _ in _doi_tuong(du_lieu):
        if bang and (khoi := _CAC_KHOI.get(bang)):
            for khoa in khoi.co_the_null:
                if not _co_khoa_tuong_duong(doi_tuong, bang, khoa):
                    gia_tri = doi_tuong.get(khoa)
                    if gia_tri is None or (isinstance(gia_tri, str) and not gia_tri.strip()):
                        doi_tuong[khoa] = None
            for khoa in (*khoi.danh_sach, *khoi.danh_sach_bat_buoc):
                doi_tuong.setdefault(khoa, [])
            for khoa in khoi.doi_tuong:
                doi_tuong.setdefault(khoa, {})
        if bang == _QUY_TAC:
            doi_tuong.setdefault("phien_ban", PHIEN_BAN_QUY_TAC)
    return du_lieu


def _url_http(gia_tri) -> bool:
    if not isinstance(gia_tri, str) or any(ky_tu.isspace() for ky_tu in gia_tri):
        return False
    try:
        url = urlsplit(gia_tri)
        return url.scheme in {"http", "https"} and bool(url.hostname) and url.username is None
    except ValueError:
        return False


def _kiem_tra_khoa(doi_tuong: dict, bang: tuple, vi_tri: str, khoi: _Khoi) -> list[str]:
    loi = []
    for khoa in khoi.gia_tri:
        gia_tri = doi_tuong.get(khoa)
        if gia_tri is None or (isinstance(gia_tri, str) and not gia_tri.strip()):
            loi.append(f"{vi_tri}/{khoa}: cần có giá trị.")
        elif khoa in {"nguon_du_lieu_url", "url"} and not _url_http(gia_tri):
            loi.append(f"{vi_tri}/{khoa}: cần URL nguồn HTTP(S) hợp lệ.")
    for khoa in khoi.co_the_null:
        if khoa == "nguon_du_lieu_url" and doi_tuong.get(khoa) is not None and not _url_http(doi_tuong[khoa]):
            loi.append(f"{vi_tri}/{khoa}: cần URL nguồn HTTP(S) hợp lệ hoặc null.")
        if khoa not in doi_tuong and not _co_khoa_tuong_duong(doi_tuong, bang, khoa):
            loi.append(f"{vi_tri}/{khoa}: thiếu khóa, dùng null khi chưa có dữ liệu.")
    for khoa in (*khoi.danh_sach, *khoi.danh_sach_bat_buoc, *(k for k in khoi.danh_sach_neu_co if k in doi_tuong)):
        gia_tri = doi_tuong.get(khoa)
        if not isinstance(gia_tri, list):
            loi.append(f"{vi_tri}/{khoa}: cần khai báo danh sách.")
        elif not gia_tri and khoa in khoi.danh_sach_bat_buoc:
            loi.append(f"{vi_tri}/{khoa}: cần ít nhất một bản ghi.")
    for khoa in khoi.doi_tuong:
        if not isinstance(doi_tuong.get(khoa), dict):
            loi.append(f"{vi_tri}/{khoa}: cần khai báo đối tượng.")
    return loi


def kiem_tra_cau_truc_cms(payload: dict) -> list[str]:
    """Kiểm tra chính dữ liệu đã lưu, không thêm khóa hoặc áp dụng mặc định khi duyệt."""
    if not isinstance(payload, dict) or set(payload) != set(_CAC_KHOI[()].doi_tuong):
        return ["JSON cần đúng ba đối tượng thong_tin_import, dats_tuyen_sinh và quy_tac_xet_tuyen."]
    loi = []
    id_theo_mang: dict[str, set[int]] = {}
    for doi_tuong, bang, vi_tri in _doi_tuong(payload):
        if khoi := _CAC_KHOI.get(bang):
            loi.extend(_kiem_tra_khoa(doi_tuong, bang, vi_tri, khoi))
        if len(bang) > 1 and bang[:1] == _DATS and bang[-1].startswith("dats_") and "id" in doi_tuong:
            id_cuc_bo = doi_tuong["id"]
            duong_dan_mang = vi_tri.rsplit("/", 1)[0]
            da_co = id_theo_mang.setdefault(duong_dan_mang, set())
            if type(id_cuc_bo) is not int or id_cuc_bo <= 0:
                loi.append(f"{vi_tri}/id: ID cục bộ phải là số nguyên dương.")
            elif id_cuc_bo in da_co:
                loi.append(f"{vi_tri}/id: ID cục bộ {id_cuc_bo} trùng trong bảng {bang[-1]}.")
            else:
                da_co.add(id_cuc_bo)
    return loi


def hop_dong_cau_truc_cms() -> dict:
    """Liệt kê khóa bắt buộc và dạng rỗng cho prompt, theo đúng hợp đồng kiểm duyệt."""
    hop_dong = {
        "/" + "/".join(bang): {
            nhom: list(getattr(khoi, nhom))
            for nhom in ("gia_tri", "co_the_null", "danh_sach", "danh_sach_neu_co", "danh_sach_bat_buoc", "doi_tuong")
            if getattr(khoi, nhom)
        }
        for bang, khoi in _CAC_KHOI.items()
    }
    # Nhiều bảng tùy chọn rỗng trong mẫu XDA. Cho AI biết tên và kiểu cột mà trình nhập thực sự nhận.
    for bang, khoi in _CAC_KHOI.items():
        for con in (*khoi.danh_sach, *khoi.danh_sach_neu_co):
            if con not in _MODELS or (*bang, con) in _CAC_KHOI:
                continue
            truong = {}
            for cot in _MODELS[con].__table__.columns:
                ten = cot.name
                if ten in _SKIP_COLUMNS or ten == "trang_thai":
                    continue
                if ten in _MA_THAY_ID:
                    truong[_MA_THAY_ID[ten][0]] = "text"
                elif ten == "doi_tuong_du_tuyen_id":
                    truong["ma_doi_tuong_du_tuyen"] = "text"
                elif ten not in _DATS_FK or ten == "co_so_id":
                    truong[ten] = _kind(cot)
            hop_dong["/" + "/".join((*bang, con))] = {"truong_tuy_chon_va_kieu": truong}
    return hop_dong


def mau_rut_gon_cms(mau: dict) -> dict:
    """Lấy bố cục từ XDA và bỏ các giá trị ví dụ trước khi gửi cho AI."""
    def gop(gia_tri):
        if isinstance(gia_tri, dict):
            return {khoa: gop(con) for khoa, con in gia_tri.items()}
        if isinstance(gia_tri, list):
            dai_dien = {}
            for con in gia_tri:
                if isinstance(con, dict):
                    for khoa, muc in con.items():
                        if khoa not in dai_dien or (muc and not dai_dien[khoa]):
                            dai_dien[khoa] = muc
            return [gop(dai_dien)] if dai_dien else []
        return None

    return gop(mau)
