"""Độ phủ dữ liệu xét tuyển theo năm (bước 5.5 KE_HOACH_TRIEN_KHAI.md). Chỉ quản trị viên.

Theo dõi tiến độ nhập liệu: số đề án theo trạng thái, tỷ lệ chương trình có mã ngành, điểm chuẩn, học phí, vị trí
(đúng cách bộ tính dùng các dữ liệu này) và các quy định chưa mô hình hóa ở lần import quy tắc gần nhất.
"""


from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, distinct, func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user
from app.core.thoi_gian import bay_gio
from app.db.session import get_db
from app.models.dats_chuong_trinh_dao_tao import DatsChuongTrinhDaoTao
from app.models.dats_hoc_phi import DatsHocPhi
from app.models.dats_tru_so import DatsTruSo
from app.models.dats_tuyen_sinh import DatsTuyenSinh
from app.models.dm_truong import DmTruong
from app.models.xt_cong_thuc import XtCongThuc
from app.models.xt_diem_chuan import XtDiemChuan
from app.models.xt_lich_su_import import XtLichSuImport
from app.schemas.xt_do_phu import XtDoPhuChiSo, XtDoPhuDeAn, XtDoPhuPage, XtDoPhuTong

router = APIRouter(prefix="/xet-tuyen/do-phu", tags=["xet-tuyen"], dependencies=[Depends(get_admin_user)])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _dem_theo_de_an(db: Session, ids: list[int], *dieu_kien, join=None) -> dict[int, int]:
    """Số chương trình (khác nhau) của từng đề án thỏa điều kiện."""
    stmt = select(DatsChuongTrinhDaoTao.de_an_id, func.count(distinct(DatsChuongTrinhDaoTao.id)))
    for bang, on in join or []:
        stmt = stmt.outerjoin(bang, on)
    stmt = stmt.where(DatsChuongTrinhDaoTao.de_an_id.in_(ids), *dieu_kien).group_by(DatsChuongTrinhDaoTao.de_an_id)
    return dict(db.execute(stmt).all())


def chi_so_theo_de_an(db: Session, de_an: list[DatsTuyenSinh]) -> dict[int, XtDoPhuChiSo]:
    ids = [d.id for d in de_an]
    if not ids:
        return {}
    tong = _dem_theo_de_an(db, ids)
    ma_nganh = _dem_theo_de_an(db, ids, DatsChuongTrinhDaoTao.nganh_dao_tao_id.is_not(None))
    hoc_phi = _dem_theo_de_an(
        db, ids, DatsHocPhi.id.is_not(None), join=[(DatsHocPhi, DatsHocPhi.de_an_chuong_trinh_id == DatsChuongTrinhDaoTao.id)]
    )
    # Bộ tính khớp điểm chuẩn theo (mã trường, mã xét tuyển), năm không sau năm tuyển sinh.
    diem_chuan = _dem_theo_de_an(
        db,
        ids,
        XtDiemChuan.id.is_not(None),
        join=[
            (DatsTuyenSinh, DatsTuyenSinh.id == DatsChuongTrinhDaoTao.de_an_id),
            (
                XtDiemChuan,
                and_(
                    XtDiemChuan.ma_truong == DatsTuyenSinh.ma_truong,
                    XtDiemChuan.ma_xet_tuyen == DatsChuongTrinhDaoTao.ma_xet_tuyen,
                    XtDiemChuan.nam_tuyen_sinh <= DatsTuyenSinh.nam_tuyen_sinh,
                ),
            ),
        ],
    )
    # Vị trí: tỉnh của cơ sở; chương trình không có thì dùng tỉnh của trường.
    co_so_co_tinh = _dem_theo_de_an(
        db, ids, DatsTruSo.tinh_thanh_id.is_not(None), join=[(DatsTruSo, DatsTruSo.id == DatsChuongTrinhDaoTao.co_so_id)]
    )
    truong_co_tinh = set(
        db.scalars(
            select(DmTruong.ma_truong).where(
                DmTruong.ma_truong.in_({d.ma_truong for d in de_an}),
                or_(
                    and_(DmTruong.ma_tinh_thanh.is_not(None), DmTruong.ma_tinh_thanh != ""),
                    and_(DmTruong.ten_tinh_thanh.is_not(None), DmTruong.ten_tinh_thanh != ""),
                ),
            )
        )
    )
    return {
        d.id: XtDoPhuChiSo(
            so_chuong_trinh=tong.get(d.id, 0),
            co_ma_nganh=ma_nganh.get(d.id, 0),
            co_diem_chuan=diem_chuan.get(d.id, 0),
            co_hoc_phi=hoc_phi.get(d.id, 0),
            co_vi_tri=tong.get(d.id, 0) if d.ma_truong in truong_co_tinh else co_so_co_tinh.get(d.id, 0),
        )
        for d in de_an
    }


def _lan_import_cuoi(db: Session, ids: list[int]) -> dict[int, XtLichSuImport]:
    if not ids:
        return {}
    cuoi = select(func.max(XtLichSuImport.id)).where(XtLichSuImport.de_an_id.in_(ids)).group_by(XtLichSuImport.de_an_id)
    return {x.de_an_id: x for x in db.scalars(select(XtLichSuImport).where(XtLichSuImport.id.in_(cuoi)))}


@router.get("", response_model=XtDoPhuPage)
def get_do_phu(
    nam: int | None = Query(default=None, ge=2000, le=2100, description="Mặc định năm tuyển sinh mới nhất có đề án"),
    q: str | None = Query(default=None, max_length=150, description="Tìm theo mã, tên trường"),
    trang_thai_xet_tuyen: int | None = Query(default=None, ge=0, le=2),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    db: Session = Depends(get_db),
) -> XtDoPhuPage:
    """Độ phủ dữ liệu xét tuyển của các đề án trong năm. `tong` tính trên mọi đề án của năm (không theo bộ lọc)."""
    if nam is None:
        nam = db.scalar(select(func.max(DatsTuyenSinh.nam_tuyen_sinh))) or bay_gio().year
    de_an_nam = list(
        db.scalars(select(DatsTuyenSinh).where(DatsTuyenSinh.nam_tuyen_sinh == nam).order_by(DatsTuyenSinh.ma_truong))
    )
    chi_so = chi_so_theo_de_an(db, de_an_nam)
    import_cuoi = _lan_import_cuoi(db, [d.id for d in de_an_nam])

    tong = XtDoPhuTong(so_de_an=len(de_an_nam), theo_trang_thai={"0": 0, "1": 0, "2": 0})
    for d in de_an_nam:
        tong.theo_trang_thai[str(d.trang_thai_xet_tuyen)] = tong.theo_trang_thai.get(str(d.trang_thai_xet_tuyen), 0) + 1
        for truong in XtDoPhuChiSo.model_fields:
            setattr(tong, truong, getattr(tong, truong) + getattr(chi_so[d.id], truong))
        lan = import_cuoi.get(d.id)
        tong.so_quy_dinh_chua_mo_hinh_hoa += len((lan.quy_dinh_chua_mo_hinh_hoa or []) if lan else [])

    ten_truong = dict(
        db.execute(
            select(DmTruong.ma_truong, DmTruong.ten_truong).where(DmTruong.ma_truong.in_({d.ma_truong for d in de_an_nam}))
        ).all()
    )
    loc = de_an_nam
    if trang_thai_xet_tuyen is not None:
        loc = [d for d in loc if d.trang_thai_xet_tuyen == trang_thai_xet_tuyen]
    if q and q.strip():
        tu_khoa = q.strip().lower()
        loc = [d for d in loc if tu_khoa in d.ma_truong.lower() or tu_khoa in (ten_truong.get(d.ma_truong) or "").lower()]
    trang = loc[(page - 1) * page_size : page * page_size]
    so_cong_thuc = dict(
        db.execute(
            select(XtCongThuc.de_an_id, func.count())
            .where(XtCongThuc.de_an_id.in_([d.id for d in trang]))
            .group_by(XtCongThuc.de_an_id)
        ).all()
    )
    items = []
    for d in trang:
        lan = import_cuoi.get(d.id)
        items.append(
            XtDoPhuDeAn(
                de_an_id=d.id,
                ma_truong=d.ma_truong,
                ten_truong=ten_truong.get(d.ma_truong),
                trang_thai_xet_tuyen=d.trang_thai_xet_tuyen,
                so_cong_thuc=so_cong_thuc.get(d.id, 0),
                lan_import_cuoi=lan.tao_luc if lan else None,
                quy_dinh_chua_mo_hinh_hoa=(lan.quy_dinh_chua_mo_hinh_hoa or []) if lan else [],
                **chi_so[d.id].model_dump(),
            )
        )
    return XtDoPhuPage(nam=nam, tong=tong, items=items, total=len(loc), page=page, page_size=page_size)
