"""Kiểm tra dữ liệu hiện có trước khi tích hợp đề án tuyển sinh theo năm (bước 0.2 trong
docs/de-an-tuyen-sinh/KE_HOACH_TRIEN_KHAI.md).

CHỈ ĐỌC: mọi truy vấn chạy trong một transaction READ ONLY và được rollback ở cuối, không ghi gì vào CSDL.

Chạy từ thư mục backend:

    python -m app.scripts.kiem_tra_truoc_tich_hop_de_an                  # in báo cáo ra màn hình
    python -m app.scripts.kiem_tra_truoc_tich_hop_de_an duong/dan.md     # ghi báo cáo ra file

Mã thoát: 0 khi không có mục CHẶN, 1 khi có mục CHẶN (phải xử lý trước bước tương ứng).
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.dats_chuong_trinh_dao_tao import DatsChuongTrinhDaoTao
from app.models.dats_tru_so import DatsTruSo
from app.models.dats_tuyen_sinh import DatsTuyenSinh
from app.models.dm_bai_thi_danh_gia import DmBaiThiDanhGia
from app.models.dm_bang_cap_chung_chi import DmBangCapChungChi
from app.models.dm_doi_tuong_uu_tien import DmDoiTuongUuTien
from app.models.dm_khu_vuc_uu_tien import DmKhuVucUuTien
from app.models.dm_mon_hoc import DmMonHoc
from app.models.dm_nganh_dao_tao import DmNganhDaoTao
from app.models.dm_tinh_thanh import DmTinhThanh
from app.models.dm_to_hop_mon_hoc import DmToHopMonHoc
from app.models.dm_to_hop_mon_hoc_chi_tiet import DmToHopMonHocChiTiet
from app.models.dm_truong import DmTruong

THU_MUC_DE_AN = Path(__file__).resolve().parents[3] / "docs" / "de-an-tuyen-sinh" / "chuan_du_lieu"
FILE_MAU = ("mau_NTH_2026.json", "mau_BKA_2026.json")

# Theo THIET_KE.md mục 7.5 (Thông tư 06/2026, Điều 7 khoản 2a): UT1 gồm 01–03 cộng 2,0; UT2 gồm 04–06 cộng 1,0.
DIEM_UU_TIEN_THONG_TU = {"01": 2.0, "02": 2.0, "03": 2.0, "04": 1.0, "05": 1.0, "06": 1.0}

# Mức độ của một mục trong báo cáo.
CHAN = "CHẶN"  # phải xử lý trước bước ghi kèm, nếu không migration / import sẽ lỗi
BO_SUNG = "CẦN BỔ SUNG"  # không chặn code nhưng chặn kết quả có nghĩa
CANH_BAO = "CẢNH BÁO"
THONG_TIN = "THÔNG TIN"

SO_DONG_TOI_DA = 30  # số dòng chi tiết in ra mỗi mục


@dataclass
class Muc:
    ma: str
    tieu_de: str
    muc_do: str
    buoc: str  # bước trong kế hoạch bị ảnh hưởng
    tom_tat: str
    cot: list[str] = field(default_factory=list)
    dong: list[list] = field(default_factory=list)
    ghi_chu: str = ""


# ---------------------------------------------------------------------------
# Thu thập (chỉ SELECT)
# ---------------------------------------------------------------------------


def _dong(db: Session, stmt) -> list[dict]:
    return [dict(row._mapping) for row in db.execute(stmt)]


def thu_thap(db: Session) -> dict:
    """Đọc các bảng cần kiểm tra thành list[dict] để phần phân tích không phụ thuộc CSDL."""
    return {
        "de_an": _dong(
            db, select(DatsTuyenSinh.id, DatsTuyenSinh.ma_truong, DatsTuyenSinh.nam_tuyen_sinh)
        ),
        "chuong_trinh": _dong(
            db,
            select(
                DatsChuongTrinhDaoTao.id,
                DatsChuongTrinhDaoTao.de_an_id,
                DatsChuongTrinhDaoTao.ma_xet_tuyen,
                DatsChuongTrinhDaoTao.nganh_dao_tao_id,
                DatsChuongTrinhDaoTao.co_so_id,
            ),
        ),
        "tru_so": _dong(db, select(DatsTruSo.id, DatsTruSo.de_an_id, DatsTruSo.ten_co_so, DatsTruSo.dia_chi)),
        "truong": _dong(
            db,
            select(DmTruong.ma_truong, DmTruong.ma_tinh_thanh, DmTruong.ten_tinh_thanh, DmTruong.vung_mien),
        ),
        "tinh_thanh": _dong(db, select(DmTinhThanh.id, DmTinhThanh.ma_tinh, DmTinhThanh.ten_tinh)),
        "to_hop": _dong(
            db,
            select(
                DmToHopMonHoc.id,
                DmToHopMonHoc.ma_to_hop,
                DmToHopMonHoc.ds_mon_hoc,
                DmToHopMonHoc.trang_thai,
                DmToHopMonHoc.nam_ap_dung_tu,
                DmToHopMonHoc.nam_ap_dung_den,
            ),
        ),
        "to_hop_chi_tiet": _dong(db, select(DmToHopMonHocChiTiet.to_hop_id)),
        "mon_hoc": _dong(
            db, select(DmMonHoc.ma_mon_hoc, DmMonHoc.ma_mon, DmMonHoc.ten_mon_hoc, DmMonHoc.nhom_mon)
        ),
        "doi_tuong": _dong(
            db,
            select(
                DmDoiTuongUuTien.ma_doi_tuong,
                DmDoiTuongUuTien.ten_doi_tuong,
                DmDoiTuongUuTien.diem_cong,
                DmDoiTuongUuTien.nam_ap_dung,
                DmDoiTuongUuTien.trang_thai,
            ),
        ),
        "khu_vuc": _dong(
            db,
            select(
                DmKhuVucUuTien.ma_khu_vuc,
                DmKhuVucUuTien.diem_cong,
                DmKhuVucUuTien.nam_ap_dung,
                DmKhuVucUuTien.trang_thai,
            ),
        ),
        "bai_thi": [r["ma_bai_thi"] for r in _dong(db, select(DmBaiThiDanhGia.ma_bai_thi))],
        "chung_chi": [r["ma_chung_chi"] for r in _dong(db, select(DmBangCapChungChi.ma_chung_chi))],
        "nganh": [r["ma_nganh"] for r in _dong(db, select(DmNganhDaoTao.ma_nganh))],
    }


def doc_file_mau(thu_muc: Path = THU_MUC_DE_AN) -> dict[str, dict]:
    """Đọc các file đề án mẫu (chuẩn JSON) để kiểm tra mã chúng tham chiếu đã có trong CSDL chưa."""
    ket_qua = {}
    for ten in FILE_MAU:
        duong_dan = thu_muc / ten
        if duong_dan.is_file():
            ket_qua[ten] = json.loads(duong_dan.read_text(encoding="utf-8"))
    return ket_qua


# ---------------------------------------------------------------------------
# Phân tích (hàm thuần)
# ---------------------------------------------------------------------------


def _so(value) -> float | None:
    if value is None:
        return None
    return float(value) if isinstance(value, (int, float, Decimal)) else None


def _ds_mon(value) -> list[str]:
    """ds_mon_hoc có thể là list JSON hoặc chuỗi JSON / chuỗi phân tách bằng dấu phẩy."""
    if value is None:
        return []
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError:
            value = [x for x in value.replace(";", ",").split(",")]
    if not isinstance(value, list):
        return []
    return [str(x).strip() for x in value if str(x).strip()]


def _de_an_trung(du_lieu: dict) -> Muc:
    so_ct = Counter(ct["de_an_id"] for ct in du_lieu["chuong_trinh"])
    nhom = defaultdict(list)
    for da in du_lieu["de_an"]:
        nhom[(da["ma_truong"], da["nam_tuyen_sinh"])].append(da["id"])
    trung = sorted((k, ids) for k, ids in nhom.items() if len(ids) > 1)
    return Muc(
        ma="de_an_trung",
        tieu_de="Đề án trùng trường + năm",
        muc_do=CHAN if trung else THONG_TIN,
        buoc="1.1, 1.2",
        tom_tat=(
            f"{len(trung)} cặp trường + năm có nhiều hơn một đề án. Phải gộp trước khi đặt khóa duy nhất."
            if trung
            else "Không có đề án trùng."
        ),
        cot=["Mã trường", "Năm", "Id đề án (số chương trình)"],
        dong=[
            [ma, nam, ", ".join(f"{i} ({so_ct.get(i, 0)})" for i in sorted(ids))] for (ma, nam), ids in trung
        ],
    )


def _de_an_theo_nam(du_lieu: dict) -> Muc:
    so_ct = Counter(ct["de_an_id"] for ct in du_lieu["chuong_trinh"])
    theo_nam = defaultdict(lambda: [0, 0, 0])  # số đề án, số trường, số đề án không có chương trình
    truong_theo_nam = defaultdict(set)
    for da in du_lieu["de_an"]:
        nam = da["nam_tuyen_sinh"]
        theo_nam[nam][0] += 1
        truong_theo_nam[nam].add(da["ma_truong"])
        if not so_ct.get(da["id"]):
            theo_nam[nam][2] += 1
    for nam, ds in truong_theo_nam.items():
        theo_nam[nam][1] = len(ds)
    return Muc(
        ma="de_an_theo_nam",
        tieu_de="Số đề án theo năm",
        muc_do=THONG_TIN,
        buoc="1.x",
        tom_tat=f"{len(du_lieu['de_an'])} đề án, {len(theo_nam)} năm tuyển sinh.",
        cot=["Năm", "Số đề án", "Số trường", "Đề án chưa có chương trình"],
        dong=[[nam, *v] for nam, v in sorted(theo_nam.items())],
    )


def _chuong_trinh_thieu(du_lieu: dict) -> Muc:
    de_an = {da["id"]: da for da in du_lieu["de_an"]}
    thong_ke = defaultdict(lambda: [0, 0, 0, 0])  # tổng, thiếu ngành, thiếu cơ sở, thiếu mã xét tuyển
    for ct in du_lieu["chuong_trinh"]:
        da = de_an.get(ct["de_an_id"]) or {"ma_truong": "?", "nam_tuyen_sinh": "?"}
        tk = thong_ke[(da["ma_truong"], da["nam_tuyen_sinh"])]
        tk[0] += 1
        tk[1] += ct["nganh_dao_tao_id"] is None
        tk[2] += ct["co_so_id"] is None
        tk[3] += not (ct["ma_xet_tuyen"] or "").strip()
    tong = [sum(v[i] for v in thong_ke.values()) for i in range(4)]
    co_van_de = sorted(
        ([ma, nam, *v] for (ma, nam), v in thong_ke.items() if v[1] or v[2] or v[3]),
        key=lambda r: (-r[3], str(r[0])),
    )
    return Muc(
        ma="chuong_trinh_thieu",
        tieu_de="Chương trình đào tạo thiếu mã ngành / cơ sở / mã xét tuyển",
        muc_do=BO_SUNG if (tong[1] or tong[2] or tong[3]) else THONG_TIN,
        buoc="1.4, 3.8",
        tom_tat=(
            f"{tong[0]} chương trình: thiếu mã ngành {tong[1]}, thiếu cơ sở {tong[2]}, thiếu mã xét tuyển {tong[3]}. "
            "Thiếu mã ngành thì tiêu chí Ngành không chấm được; thiếu mã xét tuyển thì không nối được điểm chuẩn."
        ),
        cot=["Mã trường", "Năm", "Số chương trình", "Thiếu ngành", "Thiếu cơ sở", "Thiếu mã xét tuyển"],
        dong=co_van_de,
    )


def _ma_xet_tuyen_trung(du_lieu: dict) -> Muc:
    de_an = {da["id"]: da for da in du_lieu["de_an"]}
    dem = Counter(
        (ct["de_an_id"], ct["ma_xet_tuyen"].strip())
        for ct in du_lieu["chuong_trinh"]
        if (ct["ma_xet_tuyen"] or "").strip()
    )
    trung = sorted((k, n) for k, n in dem.items() if n > 1)
    dong = []
    for (de_an_id, ma), n in trung:
        da = de_an.get(de_an_id, {})
        dong.append([da.get("ma_truong", "?"), da.get("nam_tuyen_sinh", "?"), de_an_id, ma, n])
    return Muc(
        ma="ma_xet_tuyen_trung",
        tieu_de="Mã xét tuyển trùng trong cùng đề án",
        muc_do=CANH_BAO if trung else THONG_TIN,
        buoc="2.3",
        tom_tat=(
            f"{len(trung)} mã xét tuyển xuất hiện nhiều lần trong cùng đề án. "
            "Bộ import khớp chương trình theo mã xét tuyển + tên, cần kiểm tra các dòng này."
            if trung
            else "Không có mã xét tuyển trùng trong cùng đề án."
        ),
        cot=["Mã trường", "Năm", "Id đề án", "Mã xét tuyển", "Số lần"],
        dong=dong,
    )


def _truong_thieu_dia_diem(du_lieu: dict) -> Muc:
    co_de_an = {da["ma_truong"] for da in du_lieu["de_an"]}
    ten_tinh = {(t["ten_tinh"] or "").strip().lower() for t in du_lieu["tinh_thanh"]}
    dong = []
    for tr in du_lieu["truong"]:
        if tr["ma_truong"] not in co_de_an:
            continue
        thieu = []
        if not (tr["ma_tinh_thanh"] or "").strip():
            thieu.append("mã tỉnh")
        if not (tr["vung_mien"] or "").strip():
            thieu.append("vùng miền")
        ten = (tr["ten_tinh_thanh"] or "").strip()
        if not ten:
            thieu.append("tên tỉnh")
        elif ten.lower() not in ten_tinh:
            thieu.append(f"tên tỉnh '{ten}' không khớp dm_tinh_thanh")
        if thieu:
            dong.append([tr["ma_truong"], ", ".join(thieu)])
    return Muc(
        ma="truong_thieu_dia_diem",
        tieu_de="Trường có đề án nhưng thiếu thông tin địa điểm",
        muc_do=BO_SUNG if dong else THONG_TIN,
        buoc="3.1 (tiêu chí Vị trí)",
        tom_tat=f"{len(dong)}/{len(co_de_an)} trường có đề án thiếu hoặc sai thông tin tỉnh / vùng miền.",
        cot=["Mã trường", "Thiếu / sai"],
        dong=sorted(dong),
    )


def _co_so_doan_tinh(du_lieu: dict) -> Muc:
    ten_tinh = [t["ten_tinh"] for t in du_lieu["tinh_thanh"] if t["ten_tinh"]]
    khong_doan = []
    for cs in du_lieu["tru_so"]:
        noi_dung = f"{cs['ten_co_so'] or ''} {cs['dia_chi'] or ''}".lower()
        if not any(t.lower() in noi_dung for t in ten_tinh):
            khong_doan.append([cs["id"], cs["de_an_id"], cs["ten_co_so"] or "", cs["dia_chi"] or ""])
    tong = len(du_lieu["tru_so"])
    return Muc(
        ma="co_so_doan_tinh",
        tieu_de="Cơ sở đào tạo chưa suy được tỉnh từ tên / địa chỉ",
        muc_do=BO_SUNG if khong_doan else THONG_TIN,
        buoc="1.2, 1.4 (cột tinh_thanh_id mới)",
        tom_tat=(
            f"{tong - len(khong_doan)}/{tong} cơ sở có tên tỉnh trong tên hoặc địa chỉ (điền tự động được); "
            f"{len(khong_doan)} cơ sở phải chọn tỉnh tay."
        ),
        cot=["Id cơ sở", "Id đề án", "Tên cơ sở", "Địa chỉ"],
        dong=khong_doan,
    )


def _to_hop(du_lieu: dict, ma_mon: set[str]) -> list[Muc]:
    co_chi_tiet = {r["to_hop_id"] for r in du_lieu["to_hop_chi_tiet"]}
    dang_dung = [th for th in du_lieu["to_hop"] if th["trang_thai"] in (1, True, None)]
    thieu_chi_tiet = [th for th in dang_dung if th["id"] not in co_chi_tiet]
    loi_mon = []
    for th in dang_dung:
        ds = _ds_mon(th["ds_mon_hoc"])
        khong_co = [m for m in ds if m not in ma_mon]
        if not ds:
            loi_mon.append([th["ma_to_hop"], "ds_mon_hoc rỗng"])
        elif khong_co:
            loi_mon.append([th["ma_to_hop"], "mã môn không có trong dm_mon_hoc: " + ", ".join(khong_co)])
        elif len(ds) != 3:
            loi_mon.append([th["ma_to_hop"], f"có {len(ds)} môn (cần dựng tay vị trí tính điểm)"])
    co_nam = sum(1 for th in du_lieu["to_hop"] if th["nam_ap_dung_tu"] or th["nam_ap_dung_den"])
    return [
        Muc(
            ma="to_hop_chi_tiet",
            tieu_de="Tổ hợp đang dùng chưa có chi tiết môn",
            muc_do=BO_SUNG if thieu_chi_tiet else THONG_TIN,
            buoc="2.1 (dữ liệu nền file 03)",
            tom_tat=(
                f"{len(thieu_chi_tiet)}/{len(dang_dung)} tổ hợp đang dùng chưa có dòng trong dm_to_hop_mon_hoc_chi_tiet; "
                "migration 2.1 sẽ dựng từ ds_mon_hoc."
            ),
        ),
        Muc(
            ma="to_hop_ds_mon",
            tieu_de="Tổ hợp không dựng được chi tiết tự động",
            muc_do=CANH_BAO if loi_mon else THONG_TIN,
            buoc="2.1",
            tom_tat=f"{len(loi_mon)} tổ hợp có ds_mon_hoc rỗng, sai mã môn hoặc không đủ 3 môn.",
            cot=["Mã tổ hợp", "Vấn đề"],
            dong=sorted(loi_mon),
        ),
        Muc(
            ma="to_hop_nam_ap_dung",
            tieu_de="Năm áp dụng của tổ hợp",
            muc_do=THONG_TIN,
            buoc="5.1",
            tom_tat=(
                f"Bảng đã có cột nam_ap_dung_tu / nam_ap_dung_den; {co_nam}/{len(du_lieu['to_hop'])} tổ hợp có giá trị. "
                "Bước 5.1 chỉ cần dùng cột có sẵn, không phải thêm cột."
            ),
        ),
    ]


def _ngoai_ngu(du_lieu: dict) -> Muc:
    mon = [m for m in du_lieu["mon_hoc"] if (m["nhom_mon"] or "").strip() == "Ngoại ngữ"]
    return Muc(
        ma="nhom_ngoai_ngu",
        tieu_de="Nhóm môn 'Ngoại ngữ'",
        muc_do=THONG_TIN if mon else CHAN,
        buoc="3.1 (thay điểm môn ngoại ngữ bằng chứng chỉ)",
        tom_tat=(
            f"{len(mon)} môn thuộc nhóm 'Ngoại ngữ'."
            if mon
            else "Không có môn nào thuộc nhóm 'Ngoại ngữ': bộ tính không nhận ra môn ngoại ngữ."
        ),
        cot=["Mã môn", "Tên môn"],
        dong=sorted([m["ma_mon_hoc"] or m["ma_mon"] or "", m["ten_mon_hoc"] or ""] for m in mon),
    )


def _uu_tien(du_lieu: dict) -> list[Muc]:
    dong_dt = []
    lech = 0
    for dt in sorted(du_lieu["doi_tuong"], key=lambda r: str(r["ma_doi_tuong"])):
        ma = str(dt["ma_doi_tuong"] or "").strip()
        hien = _so(dt["diem_cong"])
        chuan = DIEM_UU_TIEN_THONG_TU.get(ma)
        if chuan is None:
            danh_gia = "không có trong UT1/UT2 của Thông tư, cần rà"
            lech += 1
        elif hien != chuan:
            danh_gia = f"lệch: Thông tư {chuan:g}"
            lech += 1
        else:
            danh_gia = "khớp"
        dong_dt.append([ma, dt["ten_doi_tuong"] or "", hien, dt["nam_ap_dung"], dt["trang_thai"], danh_gia])
    return [
        Muc(
            ma="doi_tuong_uu_tien",
            tieu_de="Điểm cộng đối tượng ưu tiên so với Thông tư 06/2026",
            muc_do=CANH_BAO if lech else THONG_TIN,
            buoc="5.2",
            tom_tat=f"{lech}/{len(dong_dt)} đối tượng lệch hoặc không có trong Thông tư (theo THIET_KE.md mục 7.5).",
            cot=["Mã", "Tên", "Điểm cộng", "Năm áp dụng", "Trạng thái", "Đối chiếu"],
            dong=dong_dt,
            ghi_chu="Chưa sửa gì; bước 5.2 cần chủ dự án duyệt bảng giá trị.",
        ),
        Muc(
            ma="khu_vuc_uu_tien",
            tieu_de="Điểm cộng khu vực ưu tiên",
            muc_do=THONG_TIN,
            buoc="5.1",
            tom_tat=f"{len(du_lieu['khu_vuc'])} khu vực; bảng đã có cột nam_ap_dung.",
            cot=["Mã", "Điểm cộng", "Năm áp dụng", "Trạng thái"],
            dong=[
                [kv["ma_khu_vuc"], _so(kv["diem_cong"]), kv["nam_ap_dung"], kv["trang_thai"]]
                for kv in sorted(du_lieu["khu_vuc"], key=lambda r: str(r["ma_khu_vuc"]))
            ],
        ),
    ]


def _phang(value) -> list:
    """Làm phẳng giá trị có thể là list lồng nhau (ví dụ vi_tri của tổ hợp: [["TOAN"], ["LY", "HOA"]])."""
    if isinstance(value, list):
        return [x for v in value for x in _phang(v)]
    return [value]


def _thu_thap_ma(node, theo_khoa: dict[str, set]) -> None:
    """Gom các mã mà file chuẩn tham chiếu, theo tên khóa JSON."""
    if isinstance(node, dict):
        for khoa, gia_tri in node.items():
            if khoa in theo_khoa:
                # vi_tri vừa là danh sách mã môn (tổ hợp riêng) vừa là số thứ tự (hệ số môn): chỉ lấy chuỗi.
                kieu = str if khoa == "vi_tri" else (str, int)
                theo_khoa[khoa].update(
                    str(x) for x in _phang(gia_tri) if isinstance(x, kieu) and str(x).strip()
                )
            _thu_thap_ma(gia_tri, theo_khoa)
    elif isinstance(node, list):
        for x in node:
            _thu_thap_ma(x, theo_khoa)


def _ma_file_mau(du_lieu: dict, file_mau: dict[str, dict], ma_mon: set[str]) -> list[Muc]:
    ma_to_hop = {th["ma_to_hop"] for th in du_lieu["to_hop"]}
    ma_tinh = {str(t["ma_tinh"]) for t in du_lieu["tinh_thanh"]}
    nhom = {
        "Môn học": ({"ma_mon", "ma_mon_thay_the", "vi_tri"}, ma_mon),
        "Tổ hợp": ({"to_hop", "ma_to_hop"}, ma_to_hop),
        "Bài thi": ({"ma_bai_thi"}, set(du_lieu["bai_thi"])),
        "Chứng chỉ": ({"ma_chung_chi"}, set(du_lieu["chung_chi"])),
        "Tỉnh": ({"ma_tinh"}, ma_tinh),
        "Ngành": ({"ma_nganh"}, set(du_lieu["nganh"])),
    }
    de_an = {(da["ma_truong"], da["nam_tuyen_sinh"]) for da in du_lieu["de_an"]}
    muc = []
    dong_thieu = []
    dong_de_an = []
    dong_to_hop_rieng = []
    for ten_file, doc in file_mau.items():
        ma_truong, nam = doc.get("ma_truong"), doc.get("nam_tuyen_sinh")
        dong_de_an.append([ten_file, ma_truong, nam, "có" if (ma_truong, nam) in de_an else "CHƯA CÓ"])
        rieng = {th.get("ma_to_hop") for th in doc.get("to_hop_rieng", [])}
        for ma in sorted(x for x in rieng if x):
            trang_thai = "đã có trong dm_to_hop_mon_hoc (sẽ đụng nếu không gắn tiền tố)" if ma in ma_to_hop else "chưa có"
            dong_to_hop_rieng.append([ten_file, ma, f"{ma_truong}-{ma}", trang_thai])
        for ten_nhom, (khoa, co_san) in nhom.items():
            theo_khoa = {k: set() for k in khoa}
            _thu_thap_ma(doc, theo_khoa)
            can = set().union(*theo_khoa.values())
            if ten_nhom == "Tổ hợp":
                can -= rieng
            thieu = sorted(can - co_san)
            if thieu:
                dong_thieu.append([ten_file, ten_nhom, len(thieu), ", ".join(thieu[:20])])
    muc.append(
        Muc(
            ma="file_mau_de_an",
            tieu_de="Đề án của file mẫu đã có trong CSDL",
            muc_do=CHAN if any(r[3] != "có" for r in dong_de_an) else THONG_TIN,
            buoc="2.3, 2.4 (nghiệm thu import)",
            tom_tat="Bộ import khớp đề án theo trường + năm của file mẫu.",
            cot=["File", "Mã trường", "Năm", "Đề án trong CSDL"],
            dong=dong_de_an,
        )
    )
    muc.append(
        Muc(
            ma="file_mau_ma_thieu",
            tieu_de="Mã trong file mẫu chưa có trong danh mục CSDL",
            muc_do=CHAN if dong_thieu else THONG_TIN,
            buoc="2.3 (import sẽ từ chối cả file)",
            tom_tat=(
                f"{len(dong_thieu)} nhóm mã thiếu; phải bổ sung danh mục trước khi import."
                if dong_thieu
                else "Mọi mã trong file mẫu đều có trong danh mục."
            ),
            cot=["File", "Nhóm", "Số mã thiếu", "Mã (tối đa 20)"],
            dong=dong_thieu,
        )
    )
    muc.append(
        Muc(
            ma="to_hop_rieng",
            tieu_de="Tổ hợp riêng của trường (quyết định gắn tiền tố mã trường)",
            muc_do=THONG_TIN,
            buoc="2.3",
            tom_tat="Mã dự kiến sau khi gắn tiền tố; mã gốc đã có trong danh mục chung thì sẽ đụng nếu không gắn.",
            cot=["File", "Mã trong file", "Mã sẽ lưu", "Danh mục hiện tại"],
            dong=dong_to_hop_rieng,
        )
    )
    tien_to = sorted(th["ma_to_hop"] for th in du_lieu["to_hop"] if "-" in (th["ma_to_hop"] or ""))
    muc.append(
        Muc(
            ma="to_hop_co_gach",
            tieu_de="Mã tổ hợp hiện có chứa dấu '-'",
            muc_do=CANH_BAO if tien_to else THONG_TIN,
            buoc="2.3",
            tom_tat=(
                f"{len(tien_to)} mã đã có dấu '-', có thể nhầm với quy ước tiền tố MA_TRUONG-MA_TO_HOP."
                if tien_to
                else "Không có mã tổ hợp nào chứa '-', quy ước tiền tố không bị nhầm."
            ),
            cot=["Mã tổ hợp"],
            dong=[[m] for m in tien_to],
        )
    )
    return muc


def phan_tich(du_lieu: dict, file_mau: dict[str, dict]) -> list[Muc]:
    """Chạy toàn bộ các kiểm tra trên dữ liệu đã thu thập, trả danh sách mục theo thứ tự in."""
    ma_mon = {m for r in du_lieu["mon_hoc"] for m in (r["ma_mon_hoc"], r["ma_mon"]) if m}
    return [
        _de_an_trung(du_lieu),
        _de_an_theo_nam(du_lieu),
        _chuong_trinh_thieu(du_lieu),
        _ma_xet_tuyen_trung(du_lieu),
        _truong_thieu_dia_diem(du_lieu),
        _co_so_doan_tinh(du_lieu),
        *_to_hop(du_lieu, ma_mon),
        _ngoai_ngu(du_lieu),
        *_uu_tien(du_lieu),
        *_ma_file_mau(du_lieu, file_mau, ma_mon),
    ]


# ---------------------------------------------------------------------------
# Xuất báo cáo
# ---------------------------------------------------------------------------


def _o(value) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:g}"
    return str(value).replace("|", "\\|").replace("\n", " ")


def xuat_markdown(muc: list[Muc], thoi_diem: datetime | None = None) -> str:
    thoi_diem = thoi_diem or datetime.now()
    dem = Counter(m.muc_do for m in muc)
    dong = [
        "# Báo cáo kiểm tra dữ liệu trước khi tích hợp đề án tuyển sinh",
        "",
        f"Thời điểm: {thoi_diem:%d/%m/%Y %H:%M}. Script chỉ đọc (bước 0.2, `KE_HOACH_TRIEN_KHAI.md`).",
        "",
        "| Mức độ | Số mục |",
        "|---|---|",
        *[f"| {md} | {dem.get(md, 0)} |" for md in (CHAN, BO_SUNG, CANH_BAO, THONG_TIN)],
        "",
        "## Tóm tắt",
        "",
        "| # | Mục | Mức độ | Bước | Tóm tắt |",
        "|---|---|---|---|---|",
    ]
    for i, m in enumerate(muc, 1):
        dong.append(f"| {i} | {_o(m.tieu_de)} | {m.muc_do} | {_o(m.buoc)} | {_o(m.tom_tat)} |")
    for i, m in enumerate(muc, 1):
        dong += ["", f"## {i}. {m.tieu_de}", "", f"**{m.muc_do}** · bước {m.buoc}", "", m.tom_tat]
        if m.ghi_chu:
            dong += ["", m.ghi_chu]
        if m.cot and m.dong:
            dong += ["", "| " + " | ".join(m.cot) + " |", "|" + "---|" * len(m.cot)]
            for r in m.dong[:SO_DONG_TOI_DA]:
                dong.append("| " + " | ".join(_o(x) for x in r) + " |")
            if len(m.dong) > SO_DONG_TOI_DA:
                dong.append(f"\n… và {len(m.dong) - SO_DONG_TOI_DA} dòng khác.")
    return "\n".join(dong) + "\n"


def main(argv: list[str]) -> int:
    db = SessionLocal()
    try:
        # Bảo đảm không ghi: transaction chỉ đọc, kết thúc bằng rollback.
        db.execute(text("SET SESSION TRANSACTION READ ONLY"))
        db.execute(text("START TRANSACTION READ ONLY"))
        du_lieu = thu_thap(db)
    finally:
        db.rollback()
        db.close()

    muc = phan_tich(du_lieu, doc_file_mau())
    bao_cao = xuat_markdown(muc)
    if len(argv) > 1:
        Path(argv[1]).write_text(bao_cao, encoding="utf-8")
        print(f"Đã ghi {argv[1]}")
    else:
        print(bao_cao)
    so_chan = sum(1 for m in muc if m.muc_do == CHAN)
    print(f"{so_chan} mục CHẶN.", file=sys.stderr)
    return 1 if so_chan else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
