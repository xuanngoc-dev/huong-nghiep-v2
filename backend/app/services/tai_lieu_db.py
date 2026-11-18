"""Dữ liệu tuyển sinh cho chat lấy từ CSDL (CHAT_NGUON_DU_LIEU=database).

Mỗi đề án đã công bố (`dats_tuyen_sinh.trang_thai = da_cong_bo`) được dựng thành một "tài liệu" có đúng cấu trúc
file JSON trong TAI_LIEU_DIR: `{"truong": {...}, "danh_sach_nganh": [{..., "phuong_thuc_tuyen_sinh": [...]}]}`.
Nhờ vậy phần lập kế hoạch tra cứu, tìm kiếm và trả lời của chat (tra_cuu_tuyen_sinh, chat_stream) giữ nguyên.

Nguồn: dm_truong, dats_tru_so, dats_chuong_trinh_dao_tao (+ dm_nganh_dao_tao), dats_phuong_thuc
(+ dm_phuong_thuc_tuyen_sinh), dats_phuong_thuc_to_hop (+ dm_to_hop_mon_hoc), dats_dieu_kien_du_tuyen,
dats_tieu_chi_xet_tuyen, dats_diem_cong, dats_hoc_phi, điểm chuẩn xt_diem_chuan (các năm đến năm của đề án) và
quy đổi điểm: bảng xt_bang_quy_doi (bài thi / chứng chỉ → điểm), mốc dats_quy_doi_diem_trung_tuyen,
dats_quy_doi_nguong_dau_vao (điểm phương thức / tổ hợp này ↔ phương thức / tổ hợp khác).
"""

import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dats_chuong_trinh_dao_tao import DatsChuongTrinhDaoTao
from app.models.dats_diem_cong import DatsDiemCong
from app.models.dats_dieu_kien_du_tuyen import DatsDieuKienDuTuyen
from app.models.dats_hoc_phi import DatsHocPhi
from app.models.dats_phuong_thuc import DatsPhuongThuc
from app.models.dats_phuong_thuc_to_hop import DatsPhuongThucToHop
from app.models.dats_quy_doi_diem_trung_tuyen import DatsQuyDoiDiemTrungTuyen
from app.models.dats_quy_doi_nguong_dau_vao import DatsQuyDoiNguongDauVao
from app.models.dats_tieu_chi_xet_tuyen import DatsTieuChiXetTuyen
from app.models.dats_tru_so import DatsTruSo
from app.models.dats_tuyen_sinh import DatsTuyenSinh
from app.models.dm_bai_thi_danh_gia import DmBaiThiDanhGia
from app.models.dm_bang_cap_chung_chi import DmBangCapChungChi
from app.models.dm_mon_hoc import DmMonHoc
from app.models.dm_nganh_dao_tao import DmNganhDaoTao
from app.models.dm_phuong_thuc_tuyen_sinh import DmPhuongThucTuyenSinh
from app.models.dm_to_hop_mon_hoc import DmToHopMonHoc
from app.models.dm_truong import DmTruong
from app.models.xt_bang_quy_doi import XtBangQuyDoi, XtBangQuyDoiChiTiet
from app.models.xt_cong_thuc import XtCongThuc, XtCongThucThanhPhan
from app.models.xt_diem_chuan import XtDiemChuan

DA_CONG_BO = "da_cong_bo"


@dataclass
class TaiLieuCsdl:
    """Một đề án dựng thành tài liệu. `ten` dùng như tên file (đường dẫn nguồn /chat/nguon/{ten})."""

    ten: str
    cap_nhat: datetime
    du_lieu: dict


def _so(value):
    """Decimal → int (nếu tròn) hoặc float để ra JSON gọn."""
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    return value


def _json(value):
    """Cột JSON có thể trả về chuỗi JSON (tùy driver) hoặc chuỗi "null"."""
    if isinstance(value, str):
        try:
            return json.loads(value)
        except ValueError:
            return value
    return value


def _gon(data: dict) -> dict:
    """Bỏ khóa rỗng (None, "", [], {})."""
    return {k: v for k, v in data.items() if v is not None and v != "" and v != [] and v != {}}


def _chuoi_ghep(*phan) -> str | None:
    text = "; ".join(str(p).strip() for p in phan if p is not None and str(p).strip())
    return text or None


def _ds_ten_khac(truong: DmTruong | None) -> list[str]:
    if truong is None:
        return []
    ten = [truong.ten_viet_tat] if truong.ten_viet_tat else []
    khac = _json(truong.ten_goi_khac)
    if isinstance(khac, list):
        ten.extend(str(x) for x in khac if x)
    elif isinstance(khac, str) and khac:
        ten.extend(x.strip() for x in khac.split(",") if x.strip())
    return ten


def _dieu_kien(row: DatsDieuKienDuTuyen) -> dict:
    return _gon(
        {
            "ma": row.ma_dieu_kien,
            # Viết hoa như file JSON (vd. CHUNG_CHI_NGOAI_NGU) để bộ lọc phương thức nhận ra loại điều kiện.
            "loai": (row.loai_dieu_kien or "").upper() or None,
            "ten": row.ten_dieu_kien,
            "noi_dung": row.noi_dung_dieu_kien,
            "toan_tu": row.toan_tu_so_sanh,
            "gia_tri": _json(row.gia_tri_dieu_kien),
            "bat_buoc": row.bat_buoc,
            "minh_chung": row.minh_chung_can_nop,
        }
    )


def _tieu_chi(row: DatsTieuChiXetTuyen) -> str:
    gia_tri = _json(row.gia_tri_tieu_chi)
    nguong = f" {row.toan_tu_so_sanh} {json.dumps(gia_tri, ensure_ascii=False)}" if row.toan_tu_so_sanh and gia_tri else ""
    loai = f" ({row.loai_tieu_chi})" if row.loai_tieu_chi else ""
    return f"{row.ten_tieu_chi or row.ma_tieu_chi}{loai}{nguong}: {row.noi_dung_tieu_chi or ''}".rstrip(": ")


def _diem_cong(row: DatsDiemCong) -> dict:
    return _gon(
        {
            "loai": row.loai_diem_cong,
            "doi_tuong": row.doi_tuong_duoc_cong,
            "dieu_kien_ap_dung": row.dieu_kien_ap_dung,
            "diem_cong": _so(row.diem_cong),
            "thang_diem": _so(row.thang_diem),
            "muc_cong_toi_da": _so(row.muc_diem_cong_toi_da),
            "cong_don": row.co_cong_don,
            "quy_tac_ket_hop": row.quy_tac_ket_hop,
            "ghi_chu": row.ghi_chu,
        }
    )


def _hoc_phi(row: DatsHocPhi) -> dict:
    return _gon(
        {
            "nam_hoc": row.nam_hoc,
            "hoc_phi_tu": _so(row.hoc_phi_tu),
            "hoc_phi_den": _so(row.hoc_phi_den),
            "ghi_chu": row.ghi_chu,
        }
    )


def _ten_theo_id(db: Session, model, ids: set, ma: str, ten: str) -> dict[int, str]:
    """{id: "MA (Tên)"} của một bảng danh mục."""
    ids = ids - {None}
    if not ids:
        return {}
    return {
        r.id: f"{getattr(r, ma)} ({getattr(r, ten)})" if getattr(r, ma) else getattr(r, ten)
        for r in db.scalars(select(model).where(model.id.in_(ids)))
    }


def _bang_quy_doi(db: Session, de_an: DatsTuyenSinh) -> list[dict]:
    """Bảng quy đổi bài thi / chứng chỉ sang điểm (xt_bang_quy_doi) của đề án, kèm phương thức dùng bảng."""
    bang = list(db.scalars(select(XtBangQuyDoi).where(XtBangQuyDoi.de_an_id == de_an.id).order_by(XtBangQuyDoi.id)))
    if not bang:
        return []
    chi_tiet = defaultdict(list)
    for row in db.scalars(
        select(XtBangQuyDoiChiTiet)
        .where(XtBangQuyDoiChiTiet.bang_quy_doi_id.in_([b.id for b in bang]))
        .order_by(XtBangQuyDoiChiTiet.bang_quy_doi_id, XtBangQuyDoiChiTiet.diem_tu, XtBangQuyDoiChiTiet.id)
    ):
        chi_tiet[row.bang_quy_doi_id].append(row)
    tat_ca = [r for ds in chi_tiet.values() for r in ds]
    bai_thi = _ten_theo_id(db, DmBaiThiDanhGia, {r.bai_thi_id for r in tat_ca}, "ma_bai_thi", "ten_bai_thi")
    chung_chi = _ten_theo_id(db, DmBangCapChungChi, {r.chung_chi_id for r in tat_ca}, "ma_chung_chi", "ten_chung_chi")
    mon_hoc = _ten_theo_id(db, DmMonHoc, {r.mon_hoc_id for r in tat_ca}, "ma_mon_hoc", "ten_mon_hoc")
    # Phương thức dùng bảng: qua công thức (bảng quy đổi ngoại ngữ) hoặc thành phần công thức.
    phuong_thuc = defaultdict(set)
    cong_thuc = {c.id: c for c in db.scalars(select(XtCongThuc).where(XtCongThuc.de_an_id == de_an.id))}
    for c in cong_thuc.values():
        if c.bang_quy_doi_ngoai_ngu_id and c.ma_phuong_thuc_cua_bo:
            phuong_thuc[c.bang_quy_doi_ngoai_ngu_id].add(c.ma_phuong_thuc_cua_bo)
    if cong_thuc:
        for tp in db.scalars(
            select(XtCongThucThanhPhan).where(
                XtCongThucThanhPhan.cong_thuc_id.in_(cong_thuc), XtCongThucThanhPhan.bang_quy_doi_id.is_not(None)
            )
        ):
            if cong_thuc[tp.cong_thuc_id].ma_phuong_thuc_cua_bo:
                phuong_thuc[tp.bang_quy_doi_id].add(cong_thuc[tp.cong_thuc_id].ma_phuong_thuc_cua_bo)
    ket_qua = []
    for b in bang:
        rows = chi_tiet.get(b.id, [])
        ket_qua.append(
            _gon(
                {
                    "ma_bang": b.ma_bang,
                    "ten_bang": b.ten_bang,
                    "thang_diem_quy_doi": _so(b.thang_diem_dich),
                    "dung_cho_phuong_thuc": sorted(phuong_thuc.get(b.id, [])),
                    "ghi_chu": b.ghi_chu,
                    "cot": ["quy_doi_tu", "cap_do", "diem_tu", "diem_den", "diem_quy_doi", "he_so_noi_suy", "dat_nguong"],
                    "muc": [
                        [
                            bai_thi.get(r.bai_thi_id) or chung_chi.get(r.chung_chi_id) or mon_hoc.get(r.mon_hoc_id),
                            r.cap_do,
                            _so(r.diem_tu),
                            _so(r.diem_den),
                            _so(r.diem_quy_doi),
                            _so(r.he_so_noi_suy),
                            bool(r.dat_nguong),
                        ]
                        for r in rows
                    ],
                }
            )
        )
    return ket_qua


def _moc_quy_doi(db: Session, model, de_an: DatsTuyenSinh, ma_xet_tuyen: dict[int, str]) -> list[dict]:
    """Mốc quy đổi điểm giữa phương thức / tổ hợp (dats_quy_doi_diem_trung_tuyen, dats_quy_doi_nguong_dau_vao)."""
    rows = list(db.scalars(select(model).where(model.de_an_id == de_an.id).order_by(model.id)))
    if not rows:
        return []
    pt_ids = {r.phuong_thuc_nguon_id for r in rows} | {r.phuong_thuc_dich_id for r in rows}
    th_ids = {r.to_hop_nguon_id for r in rows} | {r.to_hop_dich_id for r in rows}
    pt = {
        p.id: p.ma_phuong_thuc
        for p in db.scalars(select(DmPhuongThucTuyenSinh).where(DmPhuongThucTuyenSinh.id.in_(pt_ids - {None})))
    }
    th = {t.id: t.ma_to_hop for t in db.scalars(select(DmToHopMonHoc).where(DmToHopMonHoc.id.in_(th_ids - {None})))}
    return [
        _gon(
            {
                "nam": r.nam_tuyen_sinh,
                "chuong_trinh": ma_xet_tuyen.get(r.de_an_chuong_trinh_id) if r.de_an_chuong_trinh_id else "Tất cả",
                "tu_phuong_thuc": pt.get(r.phuong_thuc_nguon_id),
                "tu_to_hop": th.get(r.to_hop_nguon_id),
                "sang_phuong_thuc": pt.get(r.phuong_thuc_dich_id),
                "sang_to_hop": th.get(r.to_hop_dich_id),
                "diem_moc_nguon": _so(r.diem_moc_nguon),
                "diem_moc_dich": _so(r.diem_moc_dich),
                "do_lech_diem": _so(r.do_lech_diem),
                "thang_diem_nguon": _so(r.thang_diem_nguon),
                "thang_diem_dich": _so(r.thang_diem_dich),
                "cach_quy_doi": r.cong_thuc_noi_suy,
                "dieu_kien_ap_dung": r.dieu_kien_ap_dung,
                "ghi_chu": r.ghi_chu,
            }
        )
        for r in rows
    ]


def dung_tai_lieu(db: Session, de_an: DatsTuyenSinh) -> dict:
    """Dựng dữ liệu một đề án theo cấu trúc file JSON tuyển sinh dùng cho chat."""
    truong = db.scalar(select(DmTruong).where(DmTruong.ma_truong == de_an.ma_truong))
    co_so = list(db.scalars(select(DatsTruSo).where(DatsTruSo.de_an_id == de_an.id).order_by(DatsTruSo.id)))
    ten_co_so = {c.id: c.ten_co_so for c in co_so}
    chuong_trinh = list(
        db.scalars(
            select(DatsChuongTrinhDaoTao)
            .where(DatsChuongTrinhDaoTao.de_an_id == de_an.id)
            .order_by(DatsChuongTrinhDaoTao.id)
        )
    )
    ct_ids = [c.id for c in chuong_trinh]
    nganh = {
        n.id: n
        for n in db.scalars(
            select(DmNganhDaoTao).where(DmNganhDaoTao.id.in_({c.nganh_dao_tao_id for c in chuong_trinh} - {None}))
        )
    }
    phuong_thuc = (
        list(
            db.scalars(
                select(DatsPhuongThuc)
                .where(DatsPhuongThuc.de_an_chuong_trinh_id.in_(ct_ids))
                .order_by(DatsPhuongThuc.de_an_chuong_trinh_id, DatsPhuongThuc.thu_tu_uu_tien, DatsPhuongThuc.id)
            )
        )
        if ct_ids
        else []
    )
    pt_ids = [p.id for p in phuong_thuc]
    dm_pt = {
        p.ma_phuong_thuc: p
        for p in db.scalars(
            select(DmPhuongThucTuyenSinh).where(
                DmPhuongThucTuyenSinh.ma_phuong_thuc.in_({p.ma_phuong_thuc_cua_bo for p in phuong_thuc} - {None})
            )
        )
    }
    to_hop_cua_pt = defaultdict(list)
    for row in (
        db.scalars(
            select(DatsPhuongThucToHop)
            .where(DatsPhuongThucToHop.de_an_phuong_thuc_id.in_(pt_ids))
            .order_by(DatsPhuongThucToHop.thu_tu_hien_thi)
        )
        if pt_ids
        else []
    ):
        to_hop_cua_pt[row.de_an_phuong_thuc_id].append(row.to_hop_id)
    to_hop = {
        t.id: t
        for t in db.scalars(
            select(DmToHopMonHoc).where(DmToHopMonHoc.id.in_({i for ds in to_hop_cua_pt.values() for i in ds}))
        )
    }

    dieu_kien = list(
        db.scalars(
            select(DatsDieuKienDuTuyen)
            .where(DatsDieuKienDuTuyen.de_an_id == de_an.id)
            .order_by(DatsDieuKienDuTuyen.thu_tu_kiem_tra, DatsDieuKienDuTuyen.id)
        )
    )
    tieu_chi = list(
        db.scalars(
            select(DatsTieuChiXetTuyen)
            .where(DatsTieuChiXetTuyen.de_an_id == de_an.id)
            .order_by(DatsTieuChiXetTuyen.thu_tu_ap_dung, DatsTieuChiXetTuyen.id)
        )
    )
    diem_cong = list(db.scalars(select(DatsDiemCong).where(DatsDiemCong.de_an_id == de_an.id).order_by(DatsDiemCong.id)))
    hoc_phi = list(db.scalars(select(DatsHocPhi).where(DatsHocPhi.de_an_id == de_an.id).order_by(DatsHocPhi.id)))
    # Điểm chuẩn các năm đến năm của đề án, mới nhất trước.
    diem_chuan = list(
        db.scalars(
            select(XtDiemChuan)
            .where(XtDiemChuan.ma_truong == de_an.ma_truong, XtDiemChuan.nam_tuyen_sinh <= de_an.nam_tuyen_sinh)
            .order_by(XtDiemChuan.nam_tuyen_sinh.desc(), XtDiemChuan.id)
        )
    )
    ma_to_hop = {t.id: t.ma_to_hop for t in to_hop.values()}
    thieu_to_hop = {d.to_hop_id for d in diem_chuan} - set(ma_to_hop) - {None}
    if thieu_to_hop:
        ma_to_hop.update(
            {t.id: t.ma_to_hop for t in db.scalars(select(DmToHopMonHoc).where(DmToHopMonHoc.id.in_(thieu_to_hop)))}
        )

    # Gom theo chương trình / phương thức. Bản ghi không gắn chương trình, phương thức là của cả đề án.
    dk_chung, dk_nganh, dk_pt = [], defaultdict(list), defaultdict(list)
    for row in dieu_kien:
        if row.de_an_phuong_thuc_id:
            dk_pt[row.de_an_phuong_thuc_id].append(_dieu_kien(row))
        elif row.de_an_chuong_trinh_id:
            dk_nganh[row.de_an_chuong_trinh_id].append(_dieu_kien(row))
        else:
            dk_chung.append(_dieu_kien(row))
    tc_chung, tc_nganh, tc_pt = [], defaultdict(list), defaultdict(list)
    for row in tieu_chi:
        if row.de_an_phuong_thuc_id:
            tc_pt[row.de_an_phuong_thuc_id].append(_tieu_chi(row))
        elif row.de_an_chuong_trinh_id:
            tc_nganh[row.de_an_chuong_trinh_id].append(_tieu_chi(row))
        else:
            tc_chung.append(_tieu_chi(row))
    dc_chung, dc_nganh, dc_pt = [], defaultdict(list), defaultdict(list)
    for row in diem_cong:
        if row.de_an_phuong_thuc_id:
            dc_pt[row.de_an_phuong_thuc_id].append(_diem_cong(row))
        elif row.de_an_chuong_trinh_id:
            dc_nganh[row.de_an_chuong_trinh_id].append(_diem_cong(row))
        else:
            dc_chung.append(_diem_cong(row))
    hp_chung, hp_nganh = [], defaultdict(list)
    for row in hoc_phi:
        (hp_nganh[row.de_an_chuong_trinh_id] if row.de_an_chuong_trinh_id else hp_chung).append(_hoc_phi(row))
    # Điểm chuẩn cùng năm đề án theo (mã xét tuyển, phương thức, tổ hợp); mọi năm theo mã xét tuyển.
    dc_cung_nam, dc_cac_nam = {}, defaultdict(list)
    for row in diem_chuan:
        if row.nam_tuyen_sinh == de_an.nam_tuyen_sinh:
            dc_cung_nam.setdefault((row.ma_xet_tuyen, row.ma_phuong_thuc_cua_bo, row.to_hop_id), row)
        dc_cac_nam[row.ma_xet_tuyen].append(
            _gon(
                {
                    "nam": row.nam_tuyen_sinh,
                    "ma_phuong_thuc": row.ma_phuong_thuc_cua_bo,
                    "to_hop": ma_to_hop.get(row.to_hop_id),
                    "diem_chuan": _so(row.diem_chuan),
                    "thang_diem": _so(row.thang_diem),
                    "tieu_chi_phu": row.tieu_chi_phu,
                    "ghi_chu": row.ghi_chu,
                }
            )
        )

    pt_cua_ct = defaultdict(list)
    for p in phuong_thuc:
        pt_cua_ct[p.de_an_chuong_trinh_id].append(p)

    def dung_phuong_thuc(ct: DatsChuongTrinhDaoTao, p: DatsPhuongThuc) -> dict:
        dm = dm_pt.get(p.ma_phuong_thuc_cua_bo)
        dc_pt_row = dc_cung_nam.get((ct.ma_xet_tuyen, p.ma_phuong_thuc_cua_bo, None))
        ds_to_hop = []
        for to_hop_id in to_hop_cua_pt.get(p.id, []):
            t = to_hop.get(to_hop_id)
            if t is None:
                continue
            dc_th = dc_cung_nam.get((ct.ma_xet_tuyen, p.ma_phuong_thuc_cua_bo, to_hop_id))
            ds_to_hop.append(
                _gon(
                    {
                        "ma_to_hop": t.ma_to_hop,
                        "ten_to_hop": t.ten_to_hop,
                        "danh_sach_mon": _json(t.ds_mon_hoc),
                        "diem_chuan": _so(dc_th.diem_chuan) if dc_th else None,
                    }
                )
            )
        if not ds_to_hop and isinstance(_json(p.to_hop_mon_hoc), list):
            # Chưa nối bảng tổ hợp: dùng danh sách mã tổ hợp lưu sẵn trong phương thức.
            ds_to_hop = [{"ma_to_hop": str(ma)} for ma in _json(p.to_hop_mon_hoc) if ma]
        dieu_kien_phu = list(dk_pt.get(p.id, []))
        for loai, gia_tri in (("DIEU_KIEN_CAN", p.dieu_kien_can), ("DIEU_KIEN_DU", p.dieu_kien_du)):
            if _json(gia_tri) not in (None, "", [], {}):
                dieu_kien_phu.append({"loai": loai, "gia_tri": _json(gia_tri)})
        return _gon(
            {
                "ma_phuong_thuc": p.ma_phuong_thuc_cua_bo or p.ma_phuong_thuc_cua_truong,
                "ten_phuong_thuc": p.ten_phuong_thuc_cua_truong or (dm.ten_phuong_thuc if dm else None),
                "loai_phuong_thuc": (dm.loai_phuong_thuc if dm else None) or p.ma_phuong_thuc_cua_truong,
                "nhom_phuong_thuc_truong": p.ma_phuong_thuc_cua_truong,
                "chi_tieu_phuong_thuc": p.chi_tieu_phuong_thuc,
                "diem_chuan": _so(p.diem_chuan) if p.diem_chuan is not None else (
                    _so(dc_pt_row.diem_chuan) if dc_pt_row else None
                ),
                "diem_san": _so(p.diem_san),
                "thang_diem": _so(p.thang_diem),
                "cong_thuc_tinh_diem": p.cong_thuc_tinh_diem,
                "dieu_kien_phu": dieu_kien_phu,
                "tieu_chi_dong_diem": tc_pt.get(p.id) or tc_nganh.get(ct.id) or tc_chung or None,
                "diem_cong_uu_tien": dc_pt.get(p.id) or dc_nganh.get(ct.id) or dc_chung or None,
                "to_hop_mon": ds_to_hop,
                "ghi_chu": _chuoi_ghep(p.ghi_chu, p.ghi_chu_chi_tieu, dc_pt_row.tieu_chi_phu if dc_pt_row else None),
            }
        )

    danh_sach_nganh = []
    for ct in chuong_trinh:
        n = nganh.get(ct.nganh_dao_tao_id)
        danh_sach_nganh.append(
            _gon(
                {
                    "ma_nganh": n.ma_nganh if n else None,
                    "ma_xet_tuyen": ct.ma_xet_tuyen,
                    "ten_nganh": (n.ten_nganh if n else None) or ct.ten_chuong_trinh,
                    "ten_chuong_trinh": ct.ten_chuong_trinh,
                    "chi_tieu_nganh": ct.chi_tieu_tuyen_sinh,
                    "co_so_dao_tao": ten_co_so.get(ct.co_so_id),
                    "thoi_gian_dao_tao_nam": _so(ct.thoi_gian_dao_tao_nam),
                    "ngon_ngu_dao_tao": ct.ngon_ngu_dao_tao,
                    "dieu_kien_nganh": dk_nganh.get(ct.id, []),
                    "hoc_phi": hp_nganh.get(ct.id) or hp_chung,
                    # Điểm chuẩn các năm (có năm) để tham khảo, tách khỏi điểm chuẩn của phương thức năm đề án.
                    "diem_chuan_cac_nam": dc_cac_nam.get(ct.ma_xet_tuyen, []),
                    "phuong_thuc_tuyen_sinh": [dung_phuong_thuc(ct, p) for p in pt_cua_ct.get(ct.id, [])],
                }
            )
        )
        # Bộ tìm kiếm cần các khóa danh sách này luôn có mặt.
        danh_sach_nganh[-1].setdefault("phuong_thuc_tuyen_sinh", [])
        danh_sach_nganh[-1].setdefault("dieu_kien_nganh", [])

    co_so_chinh = next((c for c in co_so if c.vai_tro == "chinh"), None)
    dia_chi = "; ".join(f"{c.ten_co_so}: {c.dia_chi}" for c in co_so if c.dia_chi) or (
        truong.dia_chi_tru_so if truong else None
    )
    thong_tin_truong = _gon(
        {
            "ma_truong": de_an.ma_truong,
            "ten_truong": (truong.ten_truong if truong else None) or de_an.ten_de_an or de_an.ma_truong,
            "loai_hinh": truong.loai_hinh if truong else None,
            "nam_tuyen_sinh": de_an.nam_tuyen_sinh,
            "ten_de_an": de_an.ten_de_an,
            "tong_chi_tieu": de_an.chi_tieu,
            "aliases": _ds_ten_khac(truong),
            "khu_vuc": truong.ten_tinh_thanh if truong else None,
            "dia_chi": dia_chi or (co_so_chinh.dia_chi if co_so_chinh else None),
            "website": (truong.website_tuyen_sinh or truong.website) if truong else None,
            "url_nguon": de_an.nguon_du_lieu_url,
            "dieu_kien_chung": dk_chung,
            "quy_doi_diem": _gon(
                {
                    "bang_quy_doi": _bang_quy_doi(db, de_an),
                    "moc_quy_doi_diem_trung_tuyen": _moc_quy_doi(
                        db, DatsQuyDoiDiemTrungTuyen, de_an, {c.id: c.ma_xet_tuyen for c in chuong_trinh}
                    ),
                    "moc_quy_doi_nguong_dau_vao": _moc_quy_doi(
                        db, DatsQuyDoiNguongDauVao, de_an, {c.id: c.ma_xet_tuyen for c in chuong_trinh}
                    ),
                }
            ),
        }
    )
    return {"truong": thong_tin_truong, "danh_sach_nganh": danh_sach_nganh}


def danh_muc_truong(db: Session) -> list[dict]:
    """Toàn bộ dm_truong (mã, tên, tên viết tắt / tên gọi khác) để chat nhận ra trường chưa có dữ liệu."""
    return [
        {"ma_truong": t.ma_truong, "ten_truong": t.ten_truong, "ten_khac": _ds_ten_khac(t)}
        for t in db.scalars(select(DmTruong).order_by(DmTruong.id))
        if t.ma_truong and t.ten_truong
    ]


def tai_lieu_tu_csdl(db: Session) -> list[TaiLieuCsdl]:
    """Các đề án đã công bố dựng thành tài liệu, theo mã trường rồi năm tuyển sinh."""
    ds = []
    for de_an in db.scalars(
        select(DatsTuyenSinh)
        .where(DatsTuyenSinh.trang_thai == DA_CONG_BO)
        .order_by(DatsTuyenSinh.ma_truong, DatsTuyenSinh.nam_tuyen_sinh, DatsTuyenSinh.id)
    ):
        cap_nhat = de_an.cap_nhat_luc or de_an.tao_luc or datetime.now()
        ds.append(
            TaiLieuCsdl(
                ten=f"{de_an.ma_truong}_{de_an.nam_tuyen_sinh}_de_an_{de_an.id}.json",
                # Cột thời gian lưu giờ máy chủ (không múi giờ): đổi sang UTC như ngày sửa file ở chế độ thư mục.
                cap_nhat=cap_nhat.astimezone(timezone.utc),
                du_lieu=dung_tai_lieu(db, de_an),
            )
        )
    return ds
