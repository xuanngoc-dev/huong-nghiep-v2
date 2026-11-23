"""Bộ import quy tắc xét tuyển từ file JSON chuẩn, phần chuẩn bị (bước 2.3 KE_HOACH_TRIEN_KHAI.md).

`chuan_bi_nhap(du_lieu, danh_muc)` không đụng CSDL: kiểm tra file (cấu trúc, tham chiếu nội bộ, mã danh mục, giống
docs/de-an-tuyen-sinh/chuan_du_lieu/kiem_tra_de_an.py) rồi đổi mã sang id, trả `KeHoachNhap` gồm các dòng chờ ghi.
Có lỗi thì ném `XetTuyenImportError` kèm toàn bộ danh sách lỗi, không ghi gì.

- Tổ hợp riêng của trường được gắn tiền tố mã trường (K01 của BKA lưu thành BKA-K01) vì mã tổ hợp là duy nhất
  toàn hệ thống; phương án và điểm chuẩn tham chiếu K01 trong file được đổi theo.
- Chuẩn hóa từng phần: công thức THU_CONG (có điểm nhưng chưa tự tính được) và công thức chưa dùng vẫn được nạp;
  chúng cùng ghi chú "chưa đưa vào file" của đề án được gom vào `quy_dinh_chua_mo_hinh_hoa`.
- Không có logic theo mã trường: mọi trường dùng chung một cách đọc file.
"""

import json
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dm_bai_thi_danh_gia import DmBaiThiDanhGia
from app.models.dm_bang_cap_chung_chi import DmBangCapChungChi
from app.models.dm_mon_hoc import DmMonHoc
from app.models.dm_nganh_dao_tao import DmNganhDaoTao
from app.models.dm_phuong_thuc_tuyen_sinh import DmPhuongThucTuyenSinh
from app.models.dm_thanh_tich_hoc_tap_nghien_cuu import DmThanhTichHocTapNghienCuu
from app.models.dm_tinh_thanh import DmTinhThanh
from app.models.dm_to_hop_mon_hoc import DmToHopMonHoc
from app.models.dm_to_hop_mon_hoc_chi_tiet import DmToHopMonHocChiTiet
from app.models.dm_truong import DmTruong
from app.schemas.xet_tuyen_chuan import CongThucChuan, DeAnXetTuyenChuan, NhomDieuKienChuan
from app.services.xet_tuyen_chuan_hoa import chuan_hoa

NHOM_NGOAI_NGU = "Ngoại ngữ"
_DO_DAI_MA_TO_HOP = 20
# Chỉ số cần cột khoa và loại danh mục của khoa.
_KHOA_CHI_SO = {
    "MON_CHUYEN": "mon",
    "DIEM_THI_THPT": "mon",
    "DIEM_HOC_BA_TB": "mon",
    "DIEM_BAI_THI": "bai_thi",
    "DIEM_CHUNG_CHI": "chung_chi",
    "CO_CHUNG_CHI": "chung_chi",
    "THANH_TICH": "thanh_tich",
    "TBC_LOP": "lop",
    "HOC_LUC_LOP": "lop",
    "REN_LUYEN_LOP": "lop",
}
_TEN_DANH_MUC = {
    "truong": "trường",
    "tinh": "tỉnh/thành",
    "mon": "môn học",
    "to_hop": "tổ hợp",
    "bai_thi": "bài thi",
    "chung_chi": "chứng chỉ",
    "thanh_tich": "thành tích",
    "phuong_thuc": "phương thức của Bộ",
    "nganh": "ngành",
    "lop": "lớp",
}


class XetTuyenImportError(ValueError):
    """File quy tắc xét tuyển không nạp được; `loi` là danh sách lỗi dành cho người dùng."""

    def __init__(self, loi: list[str], canh_bao: list[str] | None = None):
        self.loi = loi
        self.canh_bao = canh_bao or []
        tom_tat = "; ".join(loi[:5]) + (f" và {len(loi) - 5} lỗi khác" if len(loi) > 5 else "")
        super().__init__(f"File quy tắc xét tuyển có {len(loi)} lỗi: {tom_tat}")


@dataclass
class DanhMucXetTuyen:
    """Bảng tra mã → id các danh mục mà file chuẩn tham chiếu."""

    truong: set[str] = field(default_factory=set)
    tinh: dict[str, int] = field(default_factory=dict)
    mon: dict[str, int] = field(default_factory=dict)
    nhom_mon: dict[str, str | None] = field(default_factory=dict)
    to_hop: dict[str, int] = field(default_factory=dict)
    # Mã tổ hợp → danh sách vị trí, mỗi vị trí là các mã môn thay thế nhau; thiếu = chưa có cấu trúc vị trí.
    vi_tri_to_hop: dict[str, list[list[str]]] = field(default_factory=dict)
    bai_thi: dict[str, int] = field(default_factory=dict)
    chung_chi: dict[str, int] = field(default_factory=dict)
    thanh_tich: set[str] = field(default_factory=set)
    phuong_thuc: set[str] = field(default_factory=set)
    nganh: dict[str, int] = field(default_factory=dict)
    lop: set[str] = field(default_factory=lambda: {"10", "11", "12"})

    @classmethod
    def tu_file(cls, path: str | Path) -> "DanhMucXetTuyen":
        """Đọc danh_muc_ma.json (dùng khi kiểm tra ngoài hệ thống và trong test); id là số thứ tự trong file."""
        dm = json.loads(Path(path).read_text(encoding="utf-8"))

        def theo_ma(khoa: str) -> dict[str, int]:
            return {x["ma"]: i for i, x in enumerate(dm.get(khoa, []), start=1)}

        return cls(
            truong={x["ma"] for x in dm.get("truong", [])},
            tinh=theo_ma("tinh_thanh"),
            mon=theo_ma("mon_hoc"),
            nhom_mon={x["ma"]: x.get("nhom") for x in dm.get("mon_hoc", [])},
            to_hop=theo_ma("to_hop"),
            vi_tri_to_hop={x["ma"]: x["vi_tri"] for x in dm.get("to_hop", []) if x.get("vi_tri")},
            bai_thi=theo_ma("bai_thi"),
            chung_chi=theo_ma("chung_chi"),
            thanh_tich={x["ma"] for x in dm.get("thanh_tich", [])},
            phuong_thuc={x["ma"] for x in dm.get("phuong_thuc_cua_bo", [])},
            nganh=theo_ma("nganh"),
        )

    @classmethod
    def tu_csdl(cls, db: Session) -> "DanhMucXetTuyen":
        """Đọc danh mục từ các bảng dm_*; vị trí môn của tổ hợp lấy từ dm_to_hop_mon_hoc_chi_tiet."""
        mon = {ma: (mid, nhom) for mid, ma, nhom in db.execute(select(DmMonHoc.id, DmMonHoc.ma_mon_hoc, DmMonHoc.nhom_mon))}
        ma_mon_theo_id = {mid: ma for ma, (mid, _nhom) in mon.items()}
        to_hop = dict(db.execute(select(DmToHopMonHoc.ma_to_hop, DmToHopMonHoc.id)).all())
        ma_to_hop_theo_id = {tid: ma for ma, tid in to_hop.items()}
        vi_tri: dict[str, dict[int, list[str]]] = {}
        for to_hop_id, mon_hoc_id, thu_tu in db.execute(
            select(DmToHopMonHocChiTiet.to_hop_id, DmToHopMonHocChiTiet.mon_hoc_id, DmToHopMonHocChiTiet.thu_tu_mon)
        ):
            if thu_tu is None or to_hop_id not in ma_to_hop_theo_id or mon_hoc_id not in ma_mon_theo_id:
                continue
            vi_tri.setdefault(ma_to_hop_theo_id[to_hop_id], {}).setdefault(thu_tu, []).append(
                ma_mon_theo_id[mon_hoc_id]
            )
        return cls(
            truong=set(db.scalars(select(DmTruong.ma_truong))),
            tinh=dict(db.execute(select(DmTinhThanh.ma_tinh, DmTinhThanh.id)).all()),
            mon={ma: mid for ma, (mid, _nhom) in mon.items()},
            nhom_mon={ma: nhom for ma, (_mid, nhom) in mon.items()},
            to_hop=to_hop,
            vi_tri_to_hop={ma: [ds for _thu_tu, ds in sorted(theo_thu_tu.items())] for ma, theo_thu_tu in vi_tri.items()},
            bai_thi=dict(db.execute(select(DmBaiThiDanhGia.ma_bai_thi, DmBaiThiDanhGia.id)).all()),
            chung_chi=dict(db.execute(select(DmBangCapChungChi.ma_chung_chi, DmBangCapChungChi.id)).all()),
            thanh_tich=set(db.scalars(select(DmThanhTichHocTapNghienCuu.ma_thanh_tich))),
            phuong_thuc=set(db.scalars(select(DmPhuongThucTuyenSinh.ma_phuong_thuc))),
            nganh=dict(db.execute(select(DmNganhDaoTao.ma_nganh, DmNganhDaoTao.id)).all()),
        )


@dataclass
class KeHoachNhap:
    """Các dòng chờ ghi. Tham chiếu giữa các khối trong file vẫn bằng mã (ma_cong_thuc, ma_chuong_trinh, ma_bang,
    ma_co_so, ma_to_hop); tham chiếu danh mục đã đổi sang id."""

    ma_truong: str
    nam_tuyen_sinh: int
    phien_ban: str
    de_an: dict
    co_so: list[dict] = field(default_factory=list)
    to_hop_rieng: list[dict] = field(default_factory=list)
    bang_quy_doi: list[dict] = field(default_factory=list)
    cong_thuc: list[dict] = field(default_factory=list)
    nhom_dieu_kien: list[dict] = field(default_factory=list)
    diem_cong: list[dict] = field(default_factory=list)
    chuong_trinh: list[dict] = field(default_factory=list)
    phuong_an: list[dict] = field(default_factory=list)
    diem_chuan: list[dict] = field(default_factory=list)
    quy_dinh_chua_mo_hinh_hoa: list[dict] = field(default_factory=list)
    canh_bao: list[str] = field(default_factory=list)

    def so_dong(self) -> dict[str, int]:
        """Số dòng sẽ ghi theo bảng đích."""
        return {
            "dats_tru_so": len(self.co_so),
            "dm_to_hop_mon_hoc": len(self.to_hop_rieng),
            "xt_bang_quy_doi": len(self.bang_quy_doi),
            "xt_bang_quy_doi_chi_tiet": sum(len(b["muc"]) for b in self.bang_quy_doi),
            "xt_cong_thuc": len(self.cong_thuc),
            "xt_cong_thuc_he_so_mon": sum(len(c["he_so_mon"]) for c in self.cong_thuc),
            "xt_cong_thuc_thanh_phan": sum(len(c["thanh_phan"]) for c in self.cong_thuc),
            "xt_nhom_dieu_kien": len(self.nhom_dieu_kien),
            "xt_dieu_kien": sum(len(n["dieu_kien"]) for n in self.nhom_dieu_kien),
            "xt_diem_cong": len(self.diem_cong),
            "dats_chuong_trinh_dao_tao": len(self.chuong_trinh),
            "dats_hoc_phi": sum(1 for c in self.chuong_trinh if c["hoc_phi"]),
            "xt_phuong_an": len(self.phuong_an),
            "xt_diem_chuan": len(self.diem_chuan),
        }


def _so(value) -> Decimal | None:
    """float trong JSON → Decimal giữ nguyên chữ số đã viết (1.33333333 không thành 1.3333333299999...)."""
    return None if value is None else Decimal(str(value))


def _ngay(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def doc_cau_truc(du_lieu, *, strict: bool = False) -> DeAnXetTuyenChuan:
    """Kiểm tra cấu trúc theo schema chuẩn; sai thì ném lỗi kèm đường dẫn tới từng chỗ sai."""
    try:
        return DeAnXetTuyenChuan.model_validate(du_lieu, strict=strict)
    except ValidationError as exc:
        loi = []
        for e in exc.errors():
            duong_dan = "/".join(str(p) for p in e["loc"]) or "(gốc)"
            loi.append(f"{duong_dan}: {e['msg']}{_gia_tri_nhan(e.get('input'))}")
        raise XetTuyenImportError(loi) from None


def _gia_tri_nhan(value) -> str:
    """Giá trị sai trong file (chỉ với giá trị đơn) để người nhập biết cần sửa gì; object/mảng thì bỏ qua."""
    if isinstance(value, dict | list):
        return ""
    text = json.dumps(value, ensure_ascii=False, default=str)
    return f" (nhận: {text[:80] + '…' if len(text) > 80 else text})"


def chuan_bi_nhap(du_lieu, dm: DanhMucXetTuyen, *, tu_dong_chuan_hoa: bool = True, noi_dung_da_duyet: bool = False) -> KeHoachNhap:
    """Kiểm tra file và đổi sang các dòng chờ ghi. Có lỗi thì ném XetTuyenImportError, không trả kế hoạch dở."""
    canh_bao_chuan_hoa, chua_mo_hinh_hoa = [], []
    if tu_dong_chuan_hoa:
        du_lieu, canh_bao_chuan_hoa, chua_mo_hinh_hoa = chuan_hoa(du_lieu, dm)
    doc = doc_cau_truc(du_lieu, strict=not tu_dong_chuan_hoa)
    loi: list[str] = []
    canh_bao: list[str] = list(canh_bao_chuan_hoa)
    # Bản CMS đã chốt vẫn phải ghi được nguyên vẹn; các so sánh nghiệp vụ chỉ còn là ghi chú.
    van_de_noi_dung = canh_bao if noi_dung_da_duyet else loi

    def co_ma(loai: str, ma, vi_tri: str) -> bool:
        if ma is None:
            return True
        if ma not in getattr(dm, loai):
            loi.append(f'{vi_tri}: mã "{ma}" không có trong danh mục {_TEN_DANH_MUC[loai]}')
            return False
        return True

    def trung(ds, khoa: str, ten: str) -> set:
        da_gap = set()
        for x in ds:
            ma = getattr(x, khoa)
            if ma in da_gap:
                loi.append(f'{ten}: mã "{ma}" bị trùng')
            da_gap.add(ma)
        return da_gap

    ma_truong = doc.ma_truong
    co_ma("truong", ma_truong, "ma_truong")
    ma_co_so = trung(doc.co_so, "ma_co_so", "co_so")
    trung(doc.bang_quy_doi, "ma_bang", "bang_quy_doi")
    trung(doc.cong_thuc, "ma_cong_thuc", "cong_thuc")
    trung(doc.chuong_trinh, "ma_chuong_trinh", "chuong_trinh")
    trung(doc.to_hop_rieng, "ma_to_hop", "to_hop_rieng")
    bang = {b.ma_bang: b for b in doc.bang_quy_doi}
    cong_thuc = {c.ma_cong_thuc: c for c in doc.cong_thuc}

    # Tổ hợp riêng: gắn tiền tố mã trường.
    ma_rieng = {t.ma_to_hop: f"{ma_truong}-{t.ma_to_hop}" for t in doc.to_hop_rieng}
    ma_rieng_da_gan_tien_to = {luu: goc for goc, luu in ma_rieng.items()} if not tu_dong_chuan_hoa else {}
    vi_tri_rieng = {t.ma_to_hop: t.vi_tri for t in doc.to_hop_rieng}
    for goc, moi in ma_rieng.items():
        if len(moi) > _DO_DAI_MA_TO_HOP:
            loi.append(f'to_hop_rieng {goc}: mã sau khi gắn tiền tố "{moi}" dài quá {_DO_DAI_MA_TO_HOP} ký tự')

    def ma_to_hop_luu(ma: str) -> str:
        return ma_rieng.get(ma, ma)

    def vi_tri_to_hop(ma: str):
        return vi_tri_rieng.get(ma) or dm.vi_tri_to_hop.get(ma)

    def kiem_chi_so(ma_chi_so: str, khoa: str, vi_tri: str) -> None:
        loai = _KHOA_CHI_SO.get(ma_chi_so)
        if loai and not khoa:
            loi.append(f"{vi_tri}: chỉ số {ma_chi_so} phải có khoa")
        elif not loai and khoa:
            loi.append(f'{vi_tri}: chỉ số {ma_chi_so} không dùng khoa (đang là "{khoa}")')
        elif loai:
            co_ma(loai, khoa, f"{vi_tri} / {ma_chi_so}")

    ke_hoach = KeHoachNhap(
        ma_truong=ma_truong,
        nam_tuyen_sinh=doc.nam_tuyen_sinh,
        phien_ban=doc.phien_ban,
        de_an={
            "ten_de_an": doc.de_an.ten_de_an,
            "so_quyet_dinh": doc.de_an.so_quyet_dinh,
            "ngay_cong_bo": None,
            "nguon_du_lieu_url": doc.de_an.nguon_du_lieu_url,
            "ghi_chu": doc.de_an.ghi_chu,
        },
        canh_bao=canh_bao,
    )
    try:
        ke_hoach.de_an["ngay_cong_bo"] = _ngay(doc.de_an.ngay_cong_bo)
    except ValueError:
        loi.append(f'de_an/ngay_cong_bo: "{doc.de_an.ngay_cong_bo}" không phải ngày dạng YYYY-MM-DD')

    for cs in doc.co_so:
        co_ma("tinh", cs.ma_tinh, f"co_so {cs.ma_co_so}")
        ke_hoach.co_so.append(
            {
                "ma_co_so": cs.ma_co_so,
                "ten_co_so": cs.ten_co_so,
                "tinh_thanh_id": dm.tinh.get(cs.ma_tinh),
                "dia_chi": cs.dia_chi,
                "vai_tro": "chinh" if cs.la_tru_so_chinh else "phu",
            }
        )

    for th in doc.to_hop_rieng:
        chi_tiet = []
        for thu_tu, cac_mon in enumerate(th.vi_tri, start=1):
            for ma_mon in cac_mon:
                if co_ma("mon", ma_mon, f"to_hop_rieng {th.ma_to_hop}"):
                    chi_tiet.append((dm.mon[ma_mon], thu_tu))
        ma_moi = ma_rieng[th.ma_to_hop]
        ke_hoach.to_hop_rieng.append(
            {
                "ma_to_hop": ma_moi,
                "ma_goc": th.ma_to_hop,
                "ten_to_hop": th.ten_to_hop,
                "ds_mon_hoc": list(dict.fromkeys(m for cac_mon in th.vi_tri for m in cac_mon)),
                "chi_tiet": chi_tiet,
                "to_hop_id": dm.to_hop.get(ma_moi),
            }
        )

    for b in doc.bang_quy_doi:
        muc = []
        for i, m in enumerate(b.muc, start=1):
            vt = f"bang_quy_doi {b.ma_bang} mức {i}"
            co_ma("chung_chi", m.ma_chung_chi, vt)
            co_ma("bai_thi", m.ma_bai_thi, vt)
            co_ma("mon", m.ma_mon_thay_the, vt)
            if m.diem_tu is not None and m.diem_den is not None and m.diem_tu > m.diem_den:
                van_de_noi_dung.append(f"{vt}: diem_tu lớn hơn diem_den")
            if m.he_so_noi_suy and m.diem_tu is None:
                loi.append(f"{vt}: có he_so_noi_suy thì phải có diem_tu")
            if m.diem_tu is None and m.diem_den is None and not m.cap_do:
                canh_bao.append(f"{vt}: không có khoảng điểm và không có cấp độ, mọi kết quả đều khớp")
            muc.append(
                {
                    "chung_chi_id": dm.chung_chi.get(m.ma_chung_chi) if m.ma_chung_chi else None,
                    "bai_thi_id": dm.bai_thi.get(m.ma_bai_thi) if m.ma_bai_thi else None,
                    "mon_hoc_id": dm.mon.get(m.ma_mon_thay_the) if m.ma_mon_thay_the else None,
                    "cap_do": m.cap_do,
                    "diem_tu": _so(m.diem_tu),
                    "diem_den": _so(m.diem_den),
                    "diem_quy_doi": _so(m.diem_quy_doi),
                    "he_so_noi_suy": _so(m.he_so_noi_suy),
                    "dat_nguong": m.dat_nguong,
                }
            )
        ke_hoach.bang_quy_doi.append(
            {
                "ma_bang": b.ma_bang,
                "ten_bang": b.ten_bang,
                "thang_diem_dich": _so(b.thang_diem_dich),
                "ghi_chu": b.ghi_chu,
                "muc": muc,
            }
        )

    def them_nhom(n: NhomDieuKienChuan, vi_tri: str, ma_cong_thuc: str | None, ma_chuong_trinh: str | None) -> None:
        dieu_kien = []
        for d in n.mot_trong:
            kiem_chi_so(d.ma_chi_so, d.khoa, f"{vi_tri} / nhóm {n.ma_nhom}")
            dieu_kien.append(
                {
                    "ma_chi_so": d.ma_chi_so,
                    "khoa": d.khoa,
                    "toan_tu": d.toan_tu,
                    "gia_tri_so": _so(d.gia_tri),
                    "mo_ta": d.mo_ta,
                }
            )
        ke_hoach.nhom_dieu_kien.append(
            {
                "ma_cong_thuc": ma_cong_thuc,
                "ma_chuong_trinh": ma_chuong_trinh,
                "ma_nhom": n.ma_nhom,
                "ten_nhom": n.ten_nhom,
                "mo_ta": n.mo_ta,
                "bat_buoc": n.bat_buoc,
                "dieu_kien": dieu_kien,
            }
        )

    for c in doc.cong_thuc:
        loi_tinh_diem = van_de_noi_dung if not tu_dong_chuan_hoa and c.dang_dung else canh_bao
        _cong_thuc(c, ke_hoach, bang, dm, co_ma, loi, loi_tinh_diem)
        for n in c.dieu_kien:
            if n.ma_cong_thuc is not None:
                loi.append(f"cong_thuc {c.ma_cong_thuc}: nhóm {n.ma_nhom} không được khai ma_cong_thuc ở vị trí này")
            them_nhom(n, f"cong_thuc {c.ma_cong_thuc}", c.ma_cong_thuc, None)

    for n in doc.dieu_kien_chung:
        if n.ma_cong_thuc is not None:
            loi.append(f"dieu_kien_chung: nhóm {n.ma_nhom} không được khai ma_cong_thuc ở vị trí này")
        them_nhom(n, "dieu_kien_chung", None, None)

    for i, d in enumerate(doc.diem_cong, start=1):
        vt = f"diem_cong dòng {i}"
        if d.ma_cong_thuc is not None and d.ma_cong_thuc not in cong_thuc:
            loi.append(f'{vt}: công thức "{d.ma_cong_thuc}" không tồn tại')
        kiem_chi_so(d.ma_chi_so, d.khoa, vt)
        ke_hoach.diem_cong.append(
            {
                "ma_cong_thuc": d.ma_cong_thuc,
                "loai_diem_cong": d.loai_diem_cong,
                "nhom_cong": d.nhom_cong,
                "ma_chi_so": d.ma_chi_so,
                "khoa": d.khoa,
                "toan_tu": d.toan_tu,
                "gia_tri_so": _so(d.gia_tri),
                "diem_cong": _so(d.diem_cong),
                "mo_ta": d.mo_ta,
            }
        )

    da_dung: set[str] = set()
    da_bao_thang: set[tuple[str, str]] = set()
    for ct in doc.chuong_trinh:
        vt = f"chuong_trinh {ct.ma_chuong_trinh}"
        if ct.ma_co_so is not None and ct.ma_co_so not in ma_co_so:
            loi.append(f'{vt}: cơ sở "{ct.ma_co_so}" không tồn tại')
        co_ma("nganh", ct.ma_nganh, vt)
        if ct.ma_nganh is None:
            canh_bao.append(f"{vt}: chưa có ma_nganh")
        hp = ct.hoc_phi
        if hp and hp.hoc_phi_den is not None and hp.hoc_phi_den < hp.hoc_phi_tu:
            van_de_noi_dung.append(f"{vt}: hoc_phi_den nhỏ hơn hoc_phi_tu")
        ke_hoach.chuong_trinh.append(
            {
                "ma_chuong_trinh": ct.ma_chuong_trinh,
                "ma_xet_tuyen": ct.ma_xet_tuyen,
                "ten_chuong_trinh": ct.ten_chuong_trinh,
                "nganh_dao_tao_id": dm.nganh.get(ct.ma_nganh) if ct.ma_nganh else None,
                "ma_co_so": ct.ma_co_so,
                "loai_chuong_trinh": ct.loai_chuong_trinh,
                "chi_tieu_tuyen_sinh": ct.chi_tieu,
                "hoc_phi": (
                    {
                        "nam_hoc": hp.nam_hoc,
                        "hoc_phi_tu": _so(hp.hoc_phi_tu),
                        "hoc_phi_den": _so(hp.hoc_phi_den),
                        "ghi_chu": hp.ghi_chu,
                    }
                    if hp
                    else None
                ),
            }
        )
        da_gap: set[str] = set()
        for pa in ct.phuong_an:
            ma = pa.ma_cong_thuc
            if ma not in cong_thuc:
                loi.append(f'{vt}: công thức "{ma}" không tồn tại')
                continue
            if ma in da_gap:
                loi.append(f'{vt}: công thức "{ma}" khai hai lần, hãy gộp tổ hợp vào một dòng')
            da_gap.add(ma)
            da_dung.add(ma)
            cthuc = cong_thuc[ma]
            phuong_an = {
                "ma_chuong_trinh": ct.ma_chuong_trinh,
                "ma_cong_thuc": ma,
                "ma_phuong_thuc_cua_truong": pa.ma_phuong_thuc_cua_truong,
            }
            if cthuc.kieu_tinh != "TO_HOP_MON":
                if pa.to_hop:
                    loi_to_hop = canh_bao if tu_dong_chuan_hoa else loi
                    loi_to_hop.append(f'{vt}: công thức "{ma}" không theo tổ hợp, để to_hop rỗng')
                ke_hoach.phuong_an.append({**phuong_an, "ma_to_hop": None, "to_hop_id": None})
                continue
            if not pa.to_hop:
                loi.append(f'{vt}: công thức "{ma}" kiểu TO_HOP_MON phải có to_hop')
            for ma_to_hop in pa.to_hop:
                th = ma_rieng_da_gan_tien_to.get(ma_to_hop, ma_to_hop)
                if th not in ma_rieng and th not in dm.to_hop:
                    loi.append(f'{vt}: tổ hợp "{th}" không có trong danh mục và không khai ở to_hop_rieng')
                    continue
                vi_tri = vi_tri_to_hop(th)
                if vi_tri is None:
                    loi.append(f'{vt}: tổ hợp "{th}" chưa có cấu trúc vị trí môn, hãy khai ở to_hop_rieng')
                    continue
                loi_thang_diem = van_de_noi_dung if not tu_dong_chuan_hoa and cthuc.dang_dung else canh_bao
                _kiem_he_so_to_hop(cthuc, th, vi_tri, dm, vt, loi, loi_thang_diem, da_bao_thang)
                ma_luu = ma_to_hop_luu(th)
                ke_hoach.phuong_an.append(
                    {**phuong_an, "ma_to_hop": ma_luu, "to_hop_id": dm.to_hop.get(ma_luu)}
                )
        for n in ct.dieu_kien_rieng:
            if n.ma_cong_thuc is not None and n.ma_cong_thuc not in cong_thuc:
                loi.append(f'{vt}: nhóm {n.ma_nhom} tham chiếu công thức không tồn tại "{n.ma_cong_thuc}"')
            them_nhom(n, vt, n.ma_cong_thuc, ct.ma_chuong_trinh)

    for ma in cong_thuc:
        if ma not in da_dung:
            canh_bao.append(f"cong_thuc {ma}: không có chương trình nào dùng")

    ma_xet_tuyen = {ct.ma_xet_tuyen for ct in doc.chuong_trinh}
    for i, d in enumerate(doc.diem_chuan, start=1):
        vt = f"diem_chuan dòng {i}"
        co_ma("phuong_thuc", d.ma_phuong_thuc_cua_bo, vt)
        ma_to_hop = ma_rieng_da_gan_tien_to.get(d.ma_to_hop, d.ma_to_hop)
        if ma_to_hop is not None and ma_to_hop not in ma_rieng:
            co_ma("to_hop", ma_to_hop, vt)
        if d.diem_chuan > d.thang_diem:
            van_de_noi_dung.append(f"{vt}: diem_chuan lớn hơn thang_diem")
        if d.nam_tuyen_sinh > doc.nam_tuyen_sinh:
            van_de_noi_dung.append(f"{vt}: năm điểm chuẩn lớn hơn năm của đề án")
        if d.ma_xet_tuyen not in ma_xet_tuyen:
            canh_bao.append(f'{vt}: mã xét tuyển "{d.ma_xet_tuyen}" không có trong đề án năm nay nên sẽ không được dùng')
        ma_luu = ma_to_hop_luu(ma_to_hop) if ma_to_hop else None
        ke_hoach.diem_chuan.append(
            {
                "nam_tuyen_sinh": d.nam_tuyen_sinh,
                "ma_xet_tuyen": d.ma_xet_tuyen,
                "ten_chuong_trinh": d.ten_chuong_trinh,
                "ma_phuong_thuc_cua_bo": d.ma_phuong_thuc_cua_bo,
                "ma_to_hop": ma_luu,
                "to_hop_id": dm.to_hop.get(ma_luu) if ma_luu else None,
                "diem_chuan": _so(d.diem_chuan),
                "thang_diem": _so(d.thang_diem),
                "tieu_chi_phu": d.tieu_chi_phu,
                "nguon_du_lieu_url": d.nguon_du_lieu_url,
            }
        )
    if not doc.diem_chuan:
        canh_bao.append("diem_chuan: chưa có điểm chuẩn năm trước, hệ thống sẽ không chấm được điểm phù hợp cho trường này")

    ke_hoach.quy_dinh_chua_mo_hinh_hoa = _quy_dinh_chua_mo_hinh_hoa(doc) + chua_mo_hinh_hoa
    if loi:
        raise XetTuyenImportError(loi, canh_bao)
    return ke_hoach


def _cong_thuc(c: CongThucChuan, ke_hoach: KeHoachNhap, bang: dict, dm: DanhMucXetTuyen, co_ma, loi, loi_tinh_diem) -> None:
    vt = f"cong_thuc {c.ma_cong_thuc}"
    co_ma("phuong_thuc", c.ma_phuong_thuc_cua_bo, vt)
    ma_bang_nn = c.ma_bang_quy_doi_ngoai_ngu
    if ma_bang_nn is not None and ma_bang_nn not in bang:
        loi.append(f'{vt}: bảng quy đổi ngoại ngữ "{ma_bang_nn}" không tồn tại')
    elif ma_bang_nn is not None and not any(m.ma_mon_thay_the for m in bang[ma_bang_nn].muc):
        loi.append(f'{vt}: bảng "{ma_bang_nn}" không có mức nào khai ma_mon_thay_the nên không thay được điểm môn ngoại ngữ')
    if c.kieu_tinh != "TO_HOP_MON" and c.he_so_mon:
        loi_tinh_diem.append(f"{vt}: he_so_mon chỉ có tác dụng với TO_HOP_MON")
    if c.kieu_tinh != "THANH_PHAN" and c.thanh_phan:
        loi_tinh_diem.append(f"{vt}: thanh_phan chỉ có tác dụng với THANH_PHAN")
    if c.kieu_tinh in ("CHI_DIEU_KIEN", "THU_CONG") and not c.dieu_kien:
        loi_tinh_diem.append(f"{vt}: {c.kieu_tinh} chưa có nhóm dieu_kien nên hệ thống chưa xét được phương thức này")

    he_so_mon = []
    for h in c.he_so_mon:
        co_ma("mon", h.ma_mon, f"{vt} / he_so_mon")
        he_so_mon.append(
            {"mon_hoc_id": dm.mon.get(h.ma_mon) if h.ma_mon else None, "nhom_mon": h.nhom_mon, "he_so": _so(h.he_so)}
        )
    thanh_phan = []
    for t in c.thanh_phan:
        co_ma("bai_thi", t.ma_bai_thi, f"{vt} / thanh_phan")
        co_ma("mon", t.ma_mon, f"{vt} / thanh_phan")
        if t.ma_bang_quy_doi is not None and t.ma_bang_quy_doi not in bang:
            loi.append(f'{vt}: thành phần vị trí {t.vi_tri} dùng bảng quy đổi không tồn tại "{t.ma_bang_quy_doi}"')
        thanh_phan.append(
            {
                "vi_tri": t.vi_tri,
                "ten_thanh_phan": t.ten_thanh_phan,
                "loai_nguon": t.loai_nguon,
                "bai_thi_id": dm.bai_thi.get(t.ma_bai_thi) if t.ma_bai_thi else None,
                "ma_bang_quy_doi": t.ma_bang_quy_doi,
                "mon_hoc_id": dm.mon.get(t.ma_mon) if t.ma_mon else None,
                "he_so": _so(t.he_so),
                "nam_thi_tu": t.nam_thi_tu,
                "nam_thi_den": t.nam_thi_den,
                "yeu_cau_phan_tu_chon": t.yeu_cau_phan_tu_chon,
            }
        )
    if c.kieu_tinh == "THANH_PHAN":
        # Điểm tối đa lý thuyết theo các thành phần phải bằng thang điểm.
        theo_vi_tri: dict[int, float] | None = {}
        for t in c.thanh_phan:
            toi_da = bang[t.ma_bang_quy_doi].thang_diem_dich if t.ma_bang_quy_doi in bang else None
            if toi_da is None:
                theo_vi_tri = None
                break
            theo_vi_tri[t.vi_tri] = max(theo_vi_tri.get(t.vi_tri, 0), toi_da * t.he_so)
        if theo_vi_tri:
            tong = sum(theo_vi_tri.values()) * c.he_so_nhan
            if abs(tong - c.thang_diem) > 0.01:
                loi_tinh_diem.append(f"{vt}: điểm tối đa theo các thành phần là {tong:.2f}, khác thang_diem {c.thang_diem:g}")

    ke_hoach.cong_thuc.append(
        {
            "ma_cong_thuc": c.ma_cong_thuc,
            "ten_cong_thuc": c.ten_cong_thuc,
            "ma_phuong_thuc_cua_bo": c.ma_phuong_thuc_cua_bo,
            "kieu_tinh": c.kieu_tinh,
            "nguon_diem_mon": c.nguon_diem_mon,
            "thay_ngoai_ngu": c.thay_ngoai_ngu,
            "ma_bang_quy_doi_ngoai_ngu": ma_bang_nn,
            "thang_diem": _so(c.thang_diem),
            "he_so_nhan": _so(c.he_so_nhan),
            "nguong_tb_mon": _so(c.nguong_tb_mon),
            "nguong_thpt_to_hop": _so(c.nguong_thpt_to_hop),
            "diem_san": _so(c.diem_san),
            "ap_dung_diem_cong": c.ap_dung_diem_cong,
            "ap_dung_uu_tien": c.ap_dung_uu_tien,
            "ty_le_diem_cong_toi_da": _so(c.ty_le_diem_cong_toi_da),
            "so_le_lam_tron": c.so_le_lam_tron,
            "mo_ta_cong_thuc": c.mo_ta_cong_thuc,
            "trang_thai": c.dang_dung,
            "ghi_chu": c.ghi_chu,
            "he_so_mon": he_so_mon,
            "thanh_phan": thanh_phan,
        }
    )


def _kiem_he_so_to_hop(
    c: CongThucChuan,
    ma_to_hop: str,
    vi_tri: list[list[str]],
    dm: DanhMucXetTuyen,
    vt: str,
    loi: list[str],
    loi_thang_diem: list[str],
    da_bao_thang: set[tuple[str, str]],
) -> None:
    """Môn thay thế nhau phải cùng hệ số; điểm tối đa theo hệ số phải bằng thang điểm của công thức."""
    he_so = {h.ma_mon: h.he_so for h in c.he_so_mon if h.ma_mon}
    he_so_nhom = {h.nhom_mon: h.he_so for h in c.he_so_mon if h.nhom_mon}

    def w(ma_mon: str) -> float:
        return he_so.get(ma_mon, he_so_nhom.get(dm.nhom_mon.get(ma_mon), 1))

    if c.thay_ngoai_ngu == "BAT_BUOC" and not any(
        dm.nhom_mon.get(m) == NHOM_NGOAI_NGU for cac_mon in vi_tri for m in cac_mon
    ):
        loi.append(f'{vt}: công thức "{c.ma_cong_thuc}" bắt buộc dùng chứng chỉ nhưng tổ hợp "{ma_to_hop}" không có môn ngoại ngữ')
    for cac_mon in vi_tri:
        if len({w(m) for m in cac_mon}) > 1:
            loi.append(
                f'{vt}: tổ hợp "{ma_to_hop}" có các môn thay thế nhau nhưng khác hệ số trong công thức "{c.ma_cong_thuc}"'
            )
    tong = sum(max(w(m) for m in cac_mon) for cac_mon in vi_tri) * 10 * c.he_so_nhan
    if abs(tong - c.thang_diem) > 0.01 and (c.ma_cong_thuc, ma_to_hop) not in da_bao_thang:
        da_bao_thang.add((c.ma_cong_thuc, ma_to_hop))
        loi_thang_diem.append(
            f"cong_thuc {c.ma_cong_thuc} với tổ hợp {ma_to_hop}: điểm tối đa theo hệ số là {tong:.2f}, "
            f"khác thang_diem {c.thang_diem:g}"
        )


def _quy_dinh_chua_mo_hinh_hoa(doc: DeAnXetTuyenChuan) -> list[dict]:
    """Phần đề án chưa tính được: ghi chú của người nhập, công thức THU_CONG, công thức chưa dùng."""
    ds = []
    if doc.de_an.ghi_chu:
        ds.append({"loai": "GHI_CHU_DE_AN", "ma": None, "mo_ta": doc.de_an.ghi_chu})
    for c in doc.cong_thuc:
        if c.kieu_tinh == "THU_CONG":
            mo_ta = c.ten_cong_thuc + (f": {c.mo_ta_cong_thuc}" if c.mo_ta_cong_thuc else "")
            ds.append({"loai": "CONG_THUC_THU_CONG", "ma": c.ma_cong_thuc, "mo_ta": mo_ta})
        if not c.dang_dung:
            mo_ta = c.ten_cong_thuc + (f" ({c.ghi_chu})" if c.ghi_chu else "")
            ds.append({"loai": "CONG_THUC_CHUA_DUNG", "ma": c.ma_cong_thuc, "mo_ta": mo_ta})
    return ds
