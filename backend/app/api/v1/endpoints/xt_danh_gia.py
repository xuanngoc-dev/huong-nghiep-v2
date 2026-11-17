from types import SimpleNamespace

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_optional_user, la_quan_tri
from app.db.session import get_db
from app.models.dats_chuong_trinh_dao_tao import DatsChuongTrinhDaoTao
from app.models.dats_hoc_phi import DatsHocPhi
from app.models.dats_tru_so import DatsTruSo
from app.models.dm_tinh_thanh import DmTinhThanh
from app.models.dm_to_hop_mon_hoc import DmToHopMonHoc
from app.models.dm_truong import DmTruong
from app.models.nguoi_dung import NguoiDung
from app.models.xt_cong_thuc import XtCongThuc
from app.models.xt_ket_qua import XtKetQuaChuongTrinh, XtKetQuaPhuongAn, XtLanDanhGia
from app.schemas.tn_lich_su_tim_truong_phu_hop import MA_THIET_BI_PATTERN
from app.schemas.xt_danh_gia import (
    DiemChuanThamChieu,
    KetQuaChuongTrinhPage,
    KetQuaChuongTrinhPublic,
    KetQuaTruongPublic,
    KhoangHocPhi,
    LanDanhGiaPublic,
    PhuongAnKetQuaPublic,
    PhuongAnTomTat,
    TieuChiPhuHop,
)
from app.services.xet_tuyen.bo_tinh import theo_truong

# Kết quả đánh giá xét tuyển (bước 3.6). Thành viên xem lần của mình, khách gửi đúng ma_thiet_bi, quản trị viên xem tất cả.
router = APIRouter(prefix="/xet-tuyen/danh-gia", tags=["xet-tuyen"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _f(value) -> float | None:
    return None if value is None else float(value)


def _lan_duoc_xem(db: Session, lan_id: int, user: NguoiDung | None, ma_thiet_bi: str | None) -> XtLanDanhGia:
    """Lấy lần đánh giá nếu người gọi được xem: không có thì 400, không phải của mình thì 403."""
    lan = db.get(XtLanDanhGia, lan_id)
    if lan is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Không tìm thấy lần đánh giá có id = {lan_id}"
        )
    if la_quan_tri(user):
        return lan
    if user is not None:
        duoc_xem = lan.nguoi_dung_id == user.id
    else:
        duoc_xem = lan.nguoi_dung_id is None and bool(ma_thiet_bi) and lan.ma_thiet_bi == ma_thiet_bi
    if not duoc_xem:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền xem lần đánh giá này")
    return lan


def _diem_chuan(diem, thang, nam) -> DiemChuanThamChieu | None:
    return None if diem is None else DiemChuanThamChieu(diem=float(diem), thang_diem=_f(thang), nam=nam)


@router.get("/{lan_id}", response_model=LanDanhGiaPublic)
def get_lan_danh_gia(
    lan_id: int,
    ma_thiet_bi: str | None = Query(default=None, pattern=MA_THIET_BI_PATTERN),
    db: Session = Depends(get_db),
    user: NguoiDung | None = Depends(get_optional_user),
) -> LanDanhGiaPublic:
    """Thông tin một lần đánh giá: số phương án, chương trình, trường và các giả định khi dựng hồ sơ."""
    lan = _lan_duoc_xem(db, lan_id, user, ma_thiet_bi)
    so_truong = db.scalar(
        select(func.count(func.distinct(XtKetQuaChuongTrinh.ma_truong))).where(XtKetQuaChuongTrinh.lan_danh_gia_id == lan.id)
    ) or 0
    return LanDanhGiaPublic(
        id=lan.id,
        nam_tuyen_sinh=lan.nam_tuyen_sinh,
        phien_ban_thuat_toan=lan.phien_ban_thuat_toan,
        lich_su_tim_truong_id=lan.lich_su_tim_truong_id,
        so_phuong_an=lan.so_phuong_an,
        so_chuong_trinh=lan.so_chuong_trinh,
        so_truong=so_truong,
        thoi_gian_tinh_ms=lan.thoi_gian_tinh_ms,
        gia_dinh=lan.gia_dinh or [],
        tao_luc=lan.tao_luc,
    )


@router.get("/{lan_id}/chuong-trinh", response_model=KetQuaChuongTrinhPage)
def list_ket_qua_chuong_trinh(
    lan_id: int,
    ma_thiet_bi: str | None = Query(default=None, pattern=MA_THIET_BI_PATTERN),
    q: str | None = Query(default=None, max_length=255),
    ma_truong: str | None = Query(default=None, max_length=20),
    ma_tinh: str | None = Query(default=None, max_length=20),
    xep_loai: str | None = Query(default=None, max_length=50),
    chenh_tu: float | None = Query(default=None, ge=-30, le=30),
    hoc_phi_den: float | None = Query(default=None, ge=0),
    ma_phuong_thuc: str | None = Query(default=None, max_length=20),
    ma_to_hop: str | None = Query(default=None, max_length=20),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    db: Session = Depends(get_db),
    user: NguoiDung | None = Depends(get_optional_user),
) -> KetQuaChuongTrinhPage:
    """Chương trình đã xếp hạng (1 = phù hợp nhất) theo phương án tốt nhất, có lọc và phân trang.

    `ma_phuong_thuc` / `ma_to_hop`: giữ chương trình có ít nhất một phương án đủ điều kiện theo phương thức / tổ hợp
    đó; thứ hạng và điểm phù hợp vẫn là của phương án tốt nhất.
    """
    lan = _lan_duoc_xem(db, lan_id, user, ma_thiet_bi)
    hoc_phi = (
        select(
            DatsHocPhi.de_an_chuong_trinh_id.label("ct_id"),
            func.min(DatsHocPhi.hoc_phi_tu).label("tu"),
            func.max(DatsHocPhi.hoc_phi_den).label("den"),
        )
        .group_by(DatsHocPhi.de_an_chuong_trinh_id)
        .subquery()
    )
    stmt = (
        select(
            XtKetQuaChuongTrinh,
            XtKetQuaPhuongAn,
            XtCongThuc,
            DatsChuongTrinhDaoTao,
            DmTruong.ten_truong,
            DmToHopMonHoc.ma_to_hop,
            DmTinhThanh.ten_tinh,
            hoc_phi.c.tu,
            hoc_phi.c.den,
        )
        .join(XtKetQuaPhuongAn, XtKetQuaChuongTrinh.ket_qua_phuong_an_id == XtKetQuaPhuongAn.id)
        .join(XtCongThuc, XtKetQuaPhuongAn.cong_thuc_id == XtCongThuc.id)
        .join(DatsChuongTrinhDaoTao, XtKetQuaChuongTrinh.de_an_chuong_trinh_id == DatsChuongTrinhDaoTao.id)
        .outerjoin(DmTruong, XtKetQuaChuongTrinh.ma_truong == DmTruong.ma_truong)
        .outerjoin(DmToHopMonHoc, XtKetQuaPhuongAn.to_hop_id == DmToHopMonHoc.id)
        .outerjoin(DatsTruSo, DatsChuongTrinhDaoTao.co_so_id == DatsTruSo.id)
        .outerjoin(DmTinhThanh, DatsTruSo.tinh_thanh_id == DmTinhThanh.id)
        .outerjoin(hoc_phi, hoc_phi.c.ct_id == DatsChuongTrinhDaoTao.id)
        .where(XtKetQuaChuongTrinh.lan_danh_gia_id == lan.id)
    )
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        stmt = stmt.where(
            or_(
                DatsChuongTrinhDaoTao.ten_chuong_trinh.like(pattern, escape="\\"),
                DatsChuongTrinhDaoTao.ma_xet_tuyen.like(pattern, escape="\\"),
                DmTruong.ten_truong.like(pattern, escape="\\"),
                XtKetQuaChuongTrinh.ma_truong.like(pattern, escape="\\"),
            )
        )
    if ma_truong and ma_truong.strip():
        stmt = stmt.where(XtKetQuaChuongTrinh.ma_truong == ma_truong.strip())
    if ma_tinh and ma_tinh.strip():
        stmt = stmt.where(DmTinhThanh.ma_tinh == ma_tinh.strip())
    if xep_loai and xep_loai.strip():
        stmt = stmt.where(XtKetQuaChuongTrinh.xep_loai == xep_loai.strip())
    if chenh_tu is not None:
        stmt = stmt.where(XtKetQuaChuongTrinh.chenh_lech_30 >= chenh_tu)
    if hoc_phi_den is not None:
        stmt = stmt.where(hoc_phi.c.tu <= hoc_phi_den)
    if (ma_phuong_thuc and ma_phuong_thuc.strip()) or (ma_to_hop and ma_to_hop.strip()):
        khop = (
            select(XtKetQuaPhuongAn.de_an_chuong_trinh_id)
            .join(XtCongThuc, XtKetQuaPhuongAn.cong_thuc_id == XtCongThuc.id)
            .outerjoin(DmToHopMonHoc, XtKetQuaPhuongAn.to_hop_id == DmToHopMonHoc.id)
            .where(XtKetQuaPhuongAn.lan_danh_gia_id == lan.id, XtKetQuaPhuongAn.du_dieu_kien.is_(True))
        )
        if ma_phuong_thuc and ma_phuong_thuc.strip():
            khop = khop.where(XtCongThuc.ma_phuong_thuc_cua_bo == ma_phuong_thuc.strip())
        if ma_to_hop and ma_to_hop.strip():
            khop = khop.where(DmToHopMonHoc.ma_to_hop == ma_to_hop.strip())
        stmt = stmt.where(XtKetQuaChuongTrinh.de_an_chuong_trinh_id.in_(khop))

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.execute(
        stmt.order_by(XtKetQuaChuongTrinh.thu_hang, XtKetQuaChuongTrinh.id).offset((page - 1) * page_size).limit(page_size)
    ).all()
    items = [
        KetQuaChuongTrinhPublic(
            thu_hang=r.thu_hang,
            ma_truong=r.ma_truong,
            ten_truong=ten_truong,
            chuong_trinh_id=ctr.id,
            ma_xet_tuyen=ctr.ma_xet_tuyen,
            ten_chuong_trinh=ctr.ten_chuong_trinh,
            phuong_an=PhuongAnTomTat(
                ma_cong_thuc=ct.ma_cong_thuc,
                ten_cong_thuc=ct.ten_cong_thuc,
                ma_phuong_thuc=ct.ma_phuong_thuc_cua_bo,
                kieu_tinh=pa.kieu_tinh,
                ma_to_hop=ma_th,
            ),
            diem_xet=_f(r.diem_xet),
            thang_diem=_f(r.thang_diem),
            diem_chuan=_diem_chuan(pa.diem_chuan_tham_chieu, pa.thang_diem_chuan, pa.nam_diem_chuan),
            chenh_lech_30=_f(r.chenh_lech_30),
            la_xet_thang=bool(r.la_xet_thang),
            chua_tinh_diem=pa.kieu_tinh == "THU_CONG",
            tieu_chi=TieuChiPhuHop(
                kha_nang=_f(r.diem_kha_nang),
                nganh=_f(r.diem_nganh),
                hoc_phi=_f(r.diem_hoc_phi),
                vi_tri=_f(r.diem_vi_tri),
            ),
            diem_phu_hop=_f(r.diem_phu_hop),
            xep_loai=r.xep_loai,
            hoc_phi=KhoangHocPhi(tu=_f(hp_tu), den=_f(hp_den)) if hp_tu is not None or hp_den is not None else None,
            ten_tinh=ten_tinh,
        )
        for r, pa, ct, ctr, ten_truong, ma_th, ten_tinh, hp_tu, hp_den in rows
    ]
    return KetQuaChuongTrinhPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{lan_id}/truong", response_model=list[KetQuaTruongPublic])
def list_ket_qua_truong(
    lan_id: int,
    ma_thiet_bi: str | None = Query(default=None, pattern=MA_THIET_BI_PATTERN),
    db: Session = Depends(get_db),
    user: NguoiDung | None = Depends(get_optional_user),
) -> list[KetQuaTruongPublic]:
    """Xếp hạng trường: điểm trường = trung bình điểm phù hợp của tối đa 3 chương trình tốt nhất."""
    lan = _lan_duoc_xem(db, lan_id, user, ma_thiet_bi)
    dong = [
        SimpleNamespace(ma_truong=ma, thu_hang=hang, diem_phu_hop=_f(diem))
        for ma, hang, diem in db.execute(
            select(XtKetQuaChuongTrinh.ma_truong, XtKetQuaChuongTrinh.thu_hang, XtKetQuaChuongTrinh.diem_phu_hop)
            .where(XtKetQuaChuongTrinh.lan_danh_gia_id == lan.id)
            .order_by(XtKetQuaChuongTrinh.thu_hang)
        )
    ]
    ten = dict(
        db.execute(
            select(DmTruong.ma_truong, DmTruong.ten_truong).where(DmTruong.ma_truong.in_({d.ma_truong for d in dong}))
        ).all()
    )
    return [
        KetQuaTruongPublic(
            ma_truong=t.ma_truong,
            ten_truong=ten.get(t.ma_truong),
            so_chuong_trinh=t.so_chuong_trinh,
            so_da_cham=t.so_da_cham,
            so_phu_hop=t.so_phu_hop,
            diem_cao_nhat=t.diem_cao_nhat,
            diem_truong=t.diem_truong,
            hang_tot_nhat=t.hang_tot_nhat,
        )
        for t in theo_truong(dong)
    ]


@router.get("/{lan_id}/chuong-trinh/{chuong_trinh_id}/phuong-an", response_model=list[PhuongAnKetQuaPublic])
def list_phuong_an_chuong_trinh(
    lan_id: int,
    chuong_trinh_id: int,
    ma_thiet_bi: str | None = Query(default=None, pattern=MA_THIET_BI_PATTERN),
    db: Session = Depends(get_db),
    user: NguoiDung | None = Depends(get_optional_user),
) -> list[PhuongAnKetQuaPublic]:
    """Mọi phương án học sinh tính được của một chương trình (gồm cả không đạt, kèm lý do); phương án tốt nhất trước."""
    lan = _lan_duoc_xem(db, lan_id, user, ma_thiet_bi)
    tot_nhat = db.scalar(
        select(XtKetQuaChuongTrinh.ket_qua_phuong_an_id).where(
            XtKetQuaChuongTrinh.lan_danh_gia_id == lan.id, XtKetQuaChuongTrinh.de_an_chuong_trinh_id == chuong_trinh_id
        )
    )
    rows = db.execute(
        select(XtKetQuaPhuongAn, XtCongThuc, DmToHopMonHoc.ma_to_hop)
        .join(XtCongThuc, XtKetQuaPhuongAn.cong_thuc_id == XtCongThuc.id)
        .outerjoin(DmToHopMonHoc, XtKetQuaPhuongAn.to_hop_id == DmToHopMonHoc.id)
        .where(XtKetQuaPhuongAn.lan_danh_gia_id == lan.id, XtKetQuaPhuongAn.de_an_chuong_trinh_id == chuong_trinh_id)
        .order_by(XtKetQuaPhuongAn.id)
    ).all()
    ket_qua = [
        PhuongAnKetQuaPublic(
            id=pa.id,
            ma_cong_thuc=ct.ma_cong_thuc,
            ten_cong_thuc=ct.ten_cong_thuc,
            ma_phuong_thuc=ct.ma_phuong_thuc_cua_bo,
            kieu_tinh=pa.kieu_tinh,
            ma_to_hop=ma_th,
            thang_diem=float(pa.thang_diem),
            diem_goc=_f(pa.diem_goc),
            tb_mon=_f(pa.tb_mon),
            tong_thpt_to_hop=_f(pa.tong_thpt_to_hop),
            diem_cong=float(pa.diem_cong),
            diem_uu_tien=float(pa.diem_uu_tien),
            diem_xet=_f(pa.diem_xet),
            dat_nguong=pa.dat_nguong,
            du_dieu_kien=bool(pa.du_dieu_kien),
            ly_do_khong_dat=pa.ly_do_khong_dat,
            diem_chuan=_diem_chuan(pa.diem_chuan_tham_chieu, pa.thang_diem_chuan, pa.nam_diem_chuan),
            chenh_lech_30=_f(pa.chenh_lech_30),
            chi_tiet=pa.chi_tiet,
            la_tot_nhat=pa.id == tot_nhat,
        )
        for pa, ct, ma_th in rows
    ]
    ket_qua.sort(key=lambda p: not p.la_tot_nhat)
    return ket_qua
