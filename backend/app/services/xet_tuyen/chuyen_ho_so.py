"""Dựng hồ sơ xét tuyển từ dữ liệu hiện có (bước 3.3), để dùng bộ tính trước khi có bảng hs_* (giai đoạn 4).

Hai nguồn:
- Thành viên: JSON `nguoi_dung_thong_tin.trinh_do_hoc_van` cùng khu vực, đối tượng, tỉnh, khả năng tài chính.
- Khách: `du_lieu_nang_luc` / `du_lieu_tai_chinh` của form "Thông tin của bạn" (điểm thi thử theo khối, điểm
  trung bình từng năm, tỉnh, mức học phí).

Quy tắc chuyển đã chốt với chủ dự án (16/11/2026):
- Ngoại ngữ NN1 = Tiếng Anh (ANH), NN2 = Tiếng Pháp (PHAP).
- Học lực suy ra từ điểm trung bình cả năm: >= 8,0 Tốt; >= 6,5 Khá; >= 5,0 Đạt; còn lại Chưa đạt.
- Coi như học sinh tốt nghiệp THPT đúng năm tuyển sinh đang tìm.
Giả định thêm (ghi vào `gia_dinh` của kết quả để hiển thị): ngân sách theo mức tài chính, tỉnh của hồ sơ là tỉnh mong
muốn học, điểm môn của khách ước tính từ tổng điểm theo khối.
"""

from dataclasses import dataclass, field
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dm_doi_tuong_uu_tien import DmDoiTuongUuTien
from app.models.dm_khu_vuc_uu_tien import DmKhuVucUuTien
from app.models.dm_tinh_thanh import DmTinhThanh
from app.models.dm_to_hop_mon_hoc import DmToHopMonHoc
from app.services.xet_tuyen.mo_hinh import (
    BaiThiTinh,
    ChungChiTinh,
    HoSoXetTuyen,
    KetQuaNamHocTinh,
    ThanhTichTinh,
)

MON_NGOAI_NGU_CU = {"NN1": "ANH", "NN2": "PHAP"}
REN_LUYEN = {"Tốt": 4, "Khá": 3, "Trung bình": 2, "Đạt": 2, "Yếu": 1, "Chưa đạt": 1}
# Mức khả năng tài chính của hồ sơ → ngân sách học phí một năm (VNĐ).
NGAN_SACH_THEO_MUC = {"Thấp": 15_000_000, "Trung bình": 30_000_000, "Khá": 50_000_000, "Tốt": 100_000_000}
# Mức học phí khách chọn → cận trên (VNĐ/năm); None = không giới hạn.
NGAN_SACH_KHACH = {
    "duoi_15": 15_000_000,
    "15_30": 30_000_000,
    "30_50": 50_000_000,
    "50_100": 100_000_000,
    "tren_100": None,
}
_GIAI = [
    (1, ("nhất", "vàng", "1")),
    (2, ("nhì", "bạc", "2")),
    (3, ("ba", "đồng", "3")),
    (4, ("khuyến khích", "tư", "4")),
]
_LOP = (10, 11, 12)


@dataclass
class DanhMucHoSo:
    """Bảng tra id → mã dùng khi chuyển hồ sơ."""

    khu_vuc: dict[int, str] = field(default_factory=dict)
    doi_tuong: dict[int, str] = field(default_factory=dict)
    # id tỉnh → (mã tỉnh, vùng)
    tinh: dict[int, tuple[str, str | None]] = field(default_factory=dict)
    # Mã tổ hợp đúng 3 môn → danh sách mã môn (để ước tính điểm môn từ điểm theo khối của khách).
    to_hop_ba_mon: dict[str, list[str]] = field(default_factory=dict)

    @classmethod
    def tu_csdl(cls, db: Session) -> "DanhMucHoSo":
        return cls(
            khu_vuc=dict(db.execute(select(DmKhuVucUuTien.id, DmKhuVucUuTien.ma_khu_vuc)).all()),
            doi_tuong=dict(db.execute(select(DmDoiTuongUuTien.id, DmDoiTuongUuTien.ma_doi_tuong)).all()),
            tinh={
                tid: (ma, vung)
                for tid, ma, vung in db.execute(select(DmTinhThanh.id, DmTinhThanh.ma_tinh, DmTinhThanh.khu_vuc))
            },
            to_hop_ba_mon={
                ma: list(ds)
                for ma, ds in db.execute(select(DmToHopMonHoc.ma_to_hop, DmToHopMonHoc.ds_mon_hoc))
                if isinstance(ds, list) and len(ds) == 3
            },
        )


@dataclass
class KetQuaChuyenHoSo:
    ho_so: HoSoXetTuyen
    # Các giả định đã dùng, để giao diện nói rõ kết quả là ước tính ở điểm nào.
    gia_dinh: list[str] = field(default_factory=list)
    uoc_tinh: bool = False


def hoc_luc_tu_diem_tb(diem: float | None) -> int | None:
    """4 Tốt, 3 Khá, 2 Đạt, 1 Chưa đạt theo điểm trung bình cả năm."""
    if diem is None:
        return None
    if diem >= 8.0:
        return 4
    if diem >= 6.5:
        return 3
    if diem >= 5.0:
        return 2
    return 1


def _so(value) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(str(value).replace(",", "."))
    except ValueError:
        return None


def _ma_mon(ma: str) -> str:
    ma = str(ma).strip().upper()
    return MON_NGOAI_NGU_CU.get(ma, ma)


def _muc_giai(thanh_tich: str | None) -> int:
    """'Giải Nhì', 'Nhì', 'Huy chương Bạc', '2' → 2; không nhận ra thì coi là chỉ tham gia (9)."""
    chu = (thanh_tich or "").strip().lower()
    tu = chu.split()
    for muc, tu_khoa in _GIAI:
        if any((k in chu) if " " in k else (k in tu) for k in tu_khoa):
            return muc
    return 9


def _nam_hoc(hoc_luc_trung_binh: dict | None, hanh_kiem: dict | None) -> dict[int, KetQuaNamHocTinh]:
    ket_qua: dict[int, KetQuaNamHocTinh] = {}
    for lop in _LOP:
        tbc = _so((hoc_luc_trung_binh or {}).get(str(lop), (hoc_luc_trung_binh or {}).get(lop)))
        nhan = (hanh_kiem or {}).get(str(lop), (hanh_kiem or {}).get(lop))
        ren_luyen = REN_LUYEN.get(str(nhan).strip()) if nhan else None
        if tbc is not None or ren_luyen is not None:
            ket_qua[lop] = KetQuaNamHocTinh(tbc=tbc, hoc_luc=hoc_luc_tu_diem_tb(tbc), ren_luyen=ren_luyen)
    return ket_qua


def _hoc_ba(diem_trung_binh_hoc_ba: dict | None) -> dict[str, dict[int, float]]:
    """{lớp: {môn: điểm}} (hoặc dạng cũ {lớp: {hoc_luc: {môn: điểm}}}) → {môn: {lớp: điểm}}."""
    ket_qua: dict[str, dict[int, float]] = {}
    for lop_raw, khoi in (diem_trung_binh_hoc_ba or {}).items():
        if not isinstance(khoi, dict):
            continue
        if isinstance(khoi.get("hoc_luc"), dict):
            khoi = khoi["hoc_luc"]
        try:
            lop = int(lop_raw)
        except (TypeError, ValueError):
            continue
        for ma, diem in khoi.items():
            v = _so(diem)
            if v is not None:
                ket_qua.setdefault(_ma_mon(ma), {})[lop] = v
    return ket_qua


def _ngay(value) -> date | None:
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10]) if value else None
    except ValueError:
        return None


def tu_ho_so_thanh_vien(
    trinh_do_hoc_van: dict | None,
    *,
    nam_tuyen_sinh: int,
    danh_muc: DanhMucHoSo,
    khu_vuc_uu_tien_id: int | None = None,
    doi_tuong_uu_tien_id: int | None = None,
    tinh_thanh_id: int | None = None,
    kha_nang_tai_chinh: dict | None = None,
) -> KetQuaChuyenHoSo:
    """Hồ sơ xét tuyển từ hồ sơ năng lực của thành viên."""
    hv = trinh_do_hoc_van or {}
    gia_dinh = [f"Coi như tốt nghiệp THPT năm {nam_tuyen_sinh}", "Học lực suy ra từ điểm trung bình cả năm"]
    du_kien = (hv.get("diem_thi_thpt_quoc_gia") or {}).get("du_kien") or {}
    diem_thpt = {_ma_mon(ma): v for ma, diem in du_kien.items() if (v := _so(diem)) is not None}
    if any(str(ma).upper() in MON_NGOAI_NGU_CU for ma in du_kien):
        gia_dinh.append("Ngoại ngữ 1 tính là Tiếng Anh, ngoại ngữ 2 tính là Tiếng Pháp")

    chung_chi = []
    for c in hv.get("chung_chi_ngoai_ngu") or []:
        diem = _so(c.get("thanh_tich"))
        # Kết quả không phải số (N3, HSK4, B2...) là cấp độ.
        cap_do = None
        if diem is None and c.get("thanh_tich"):
            cap_do = str(c["thanh_tich"]).strip() or None
        chung_chi.append(ChungChiTinh(ma=str(c.get("ma", "")).upper(), diem=diem, cap_do=cap_do))
    bai_thi = []
    for b in hv.get("bai_thi_danh_gia_nang_luc") or []:
        ngay = _ngay(b.get("thoi_gian_cap"))
        bai_thi.append(
            BaiThiTinh(ma=str(b.get("ma", "")).upper(), diem=_so(b.get("thanh_tich")), nam=ngay.year if ngay else nam_tuyen_sinh)
        )
    thanh_tich = [
        ThanhTichTinh(ma=str(t.get("ma", "")).upper(), muc_giai=_muc_giai(t.get("thanh_tich")))
        for t in hv.get("thanh_tich_hoc_tap_nghien_cuu") or []
    ]

    muc_tai_chinh = (kha_nang_tai_chinh or {}).get("muc")
    ngan_sach = NGAN_SACH_THEO_MUC.get(muc_tai_chinh)
    if ngan_sach:
        gia_dinh.append(f"Ngân sách học phí khoảng {ngan_sach // 1_000_000} triệu/năm theo mức tài chính {muc_tai_chinh}")
    tinh = danh_muc.tinh.get(tinh_thanh_id) if tinh_thanh_id else None
    if tinh:
        gia_dinh.append("Ưu tiên trường ở tỉnh/thành trong hồ sơ")

    ho_so = HoSoXetTuyen(
        nam_tot_nghiep=nam_tuyen_sinh,
        da_tot_nghiep=True,
        khu_vuc=danh_muc.khu_vuc.get(khu_vuc_uu_tien_id) if khu_vuc_uu_tien_id else None,
        doi_tuong=danh_muc.doi_tuong.get(doi_tuong_uu_tien_id) if doi_tuong_uu_tien_id else None,
        ngan_sach=ngan_sach,
        mong_muon_tinh=[tinh[0]] if tinh else [],
        nam_hoc=_nam_hoc(hv.get("hoc_luc_trung_binh"), hv.get("hanh_kiem")),
        diem_thpt=diem_thpt,
        hoc_ba=_hoc_ba(hv.get("diem_trung_binh_hoc_ba")),
        bai_thi=bai_thi,
        chung_chi=chung_chi,
        thanh_tich=thanh_tich,
    )
    return KetQuaChuyenHoSo(ho_so=ho_so, gia_dinh=gia_dinh)


def tu_du_lieu_khach(
    du_lieu_nang_luc: dict | None,
    du_lieu_tai_chinh: dict | None,
    *,
    nam_tuyen_sinh: int,
    danh_muc: DanhMucHoSo,
) -> KetQuaChuyenHoSo:
    """Hồ sơ xét tuyển ước tính từ form của khách (chỉ có tổng điểm thi thử theo khối, không có điểm từng môn)."""
    nl = du_lieu_nang_luc or {}
    gia_dinh = [f"Coi như tốt nghiệp THPT năm {nam_tuyen_sinh}", "Học lực suy ra từ điểm trung bình cả năm"]
    # Điểm môn = tổng điểm khối / 3, môn có trong nhiều khối lấy trung bình.
    theo_mon: dict[str, list[float]] = {}
    for khoi, tong in (nl.get("diem_thi_thu") or {}).items():
        mon = danh_muc.to_hop_ba_mon.get(str(khoi).upper())
        v = _so(tong)
        if not mon or v is None:
            continue
        for ma in mon:
            theo_mon.setdefault(ma, []).append(v / 3)
    diem_thpt = {ma: round(sum(ds) / len(ds), 2) for ma, ds in theo_mon.items()}
    if diem_thpt:
        gia_dinh.append("Điểm từng môn ước tính từ tổng điểm thi thử theo khối")

    muc = (du_lieu_tai_chinh or {}).get("muc_hoc_phi")
    ngan_sach = NGAN_SACH_KHACH.get(muc)
    if ngan_sach:
        gia_dinh.append(f"Ngân sách học phí tối đa {ngan_sach // 1_000_000} triệu/năm")
    tinh_id = nl.get("tinh_thanh_id")
    tinh = danh_muc.tinh.get(tinh_id) if isinstance(tinh_id, int) else None
    if tinh:
        gia_dinh.append("Ưu tiên trường ở tỉnh/thành đã chọn")

    ho_so = HoSoXetTuyen(
        nam_tot_nghiep=nam_tuyen_sinh,
        da_tot_nghiep=True,
        ngan_sach=ngan_sach,
        mong_muon_tinh=[tinh[0]] if tinh else [],
        nam_hoc=_nam_hoc(nl.get("diem_trung_binh"), None),
        diem_thpt=diem_thpt,
    )
    return KetQuaChuyenHoSo(ho_so=ho_so, gia_dinh=gia_dinh, uoc_tinh=bool(diem_thpt))
