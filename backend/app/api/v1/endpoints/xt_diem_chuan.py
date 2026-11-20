
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import String, and_, cast, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user
from app.core.thoi_gian import bay_gio
from app.db.session import get_db
from app.models.dm_phuong_thuc_tuyen_sinh import DmPhuongThucTuyenSinh
from app.models.dm_to_hop_mon_hoc import DmToHopMonHoc
from app.models.dm_truong import DmTruong
from app.models.xt_diem_chuan import XtDiemChuan
from app.schemas.xt_diem_chuan import (
    XtDiemChuanBulkResult,
    XtDiemChuanDeleteMany,
    XtDiemChuanDeleteManyResult,
    XtDiemChuanPage,
    XtDiemChuanPublic,
    XtDiemChuanWrite,
)

router = APIRouter(prefix="/diem-chuan", tags=["diem-chuan"], dependencies=[Depends(get_admin_user)])

_TOI_DA_NHAP = 2000


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _get_or_400(db: Session, item_id: int) -> XtDiemChuan:
    """Lấy một bản ghi theo id. Trả lỗi 400 kèm thông báo nếu không tồn tại."""
    item = db.get(XtDiemChuan, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy điểm chuẩn có id = {item_id}",
        )
    return item


def _joined():
    return (
        select(XtDiemChuan, DmTruong.ten_truong, DmPhuongThucTuyenSinh.ten_phuong_thuc, DmToHopMonHoc.ma_to_hop)
        .outerjoin(DmTruong, XtDiemChuan.ma_truong == DmTruong.ma_truong)
        .outerjoin(DmPhuongThucTuyenSinh, XtDiemChuan.ma_phuong_thuc_cua_bo == DmPhuongThucTuyenSinh.ma_phuong_thuc)
        .outerjoin(DmToHopMonHoc, XtDiemChuan.to_hop_id == DmToHopMonHoc.id)
    )


def _to_public(item: XtDiemChuan, ten_truong, ten_phuong_thuc, ma_to_hop) -> XtDiemChuanPublic:
    return XtDiemChuanPublic(
        id=item.id,
        ma_truong=item.ma_truong,
        ten_truong=ten_truong,
        nam_tuyen_sinh=item.nam_tuyen_sinh,
        ma_xet_tuyen=item.ma_xet_tuyen,
        ten_chuong_trinh=item.ten_chuong_trinh,
        ma_phuong_thuc_cua_bo=item.ma_phuong_thuc_cua_bo,
        ten_phuong_thuc=ten_phuong_thuc,
        to_hop_id=item.to_hop_id,
        ma_to_hop=ma_to_hop,
        diem_chuan=float(item.diem_chuan),
        thang_diem=float(item.thang_diem),
        tieu_chi_phu=item.tieu_chi_phu,
        nguon_du_lieu_url=item.nguon_du_lieu_url,
        ghi_chu=item.ghi_chu,
        tao_luc=item.tao_luc,
        cap_nhat_luc=item.cap_nhat_luc,
    )


def _load_public(db: Session, item_id: int) -> XtDiemChuanPublic:
    return _to_public(*db.execute(_joined().where(XtDiemChuan.id == item_id)).one())


def _khoa(item) -> tuple:
    """Một dòng điểm chuẩn là duy nhất theo trường, năm, mã xét tuyển, phương thức và tổ hợp."""
    return (item.ma_truong, item.nam_tuyen_sinh, item.ma_xet_tuyen, item.ma_phuong_thuc_cua_bo, item.to_hop_id)


def _mo_ta_khoa(khoa: tuple) -> str:
    ma_truong, nam, ma_xet_tuyen, phuong_thuc, to_hop_id = khoa
    phan = [f"{ma_truong} năm {nam} mã {ma_xet_tuyen}"]
    phan.append(f"phương thức {phuong_thuc}" if phuong_thuc else "mọi phương thức")
    phan.append(f"tổ hợp id {to_hop_id}" if to_hop_id else "mọi tổ hợp")
    return ", ".join(phan)


def _thieu(ds: list, co: set) -> list:
    return sorted({value for value in ds if value is not None and value not in co}, key=str)


def _kiem_tra(db: Session, payload: list[XtDiemChuanWrite], bo_qua_id: int | None = None) -> None:
    """Trường, phương thức, tổ hợp phải có trong danh mục; không trùng trong danh sách và với CSDL."""
    ma_truong = [item.ma_truong for item in payload]
    co_truong = set(db.scalars(select(DmTruong.ma_truong).where(DmTruong.ma_truong.in_(set(ma_truong)))))
    if thieu := _thieu(ma_truong, co_truong):
        raise HTTPException(status_code=400, detail=f"Không tìm thấy trường có mã: {', '.join(thieu)}")
    phuong_thuc = [item.ma_phuong_thuc_cua_bo for item in payload]
    co_pt = set(
        db.scalars(
            select(DmPhuongThucTuyenSinh.ma_phuong_thuc).where(
                DmPhuongThucTuyenSinh.ma_phuong_thuc.in_({p for p in phuong_thuc if p})
            )
        )
    )
    if thieu := _thieu(phuong_thuc, co_pt):
        raise HTTPException(status_code=400, detail=f"Không tìm thấy phương thức có mã: {', '.join(thieu)}")
    to_hop = [item.to_hop_id for item in payload]
    co_th = set(db.scalars(select(DmToHopMonHoc.id).where(DmToHopMonHoc.id.in_({t for t in to_hop if t}))))
    if thieu := _thieu(to_hop, co_th):
        raise HTTPException(status_code=400, detail=f"Không tìm thấy tổ hợp có id: {', '.join(map(str, thieu))}")

    khoa = [_khoa(item) for item in payload]
    if trung := sorted({k for k in khoa if khoa.count(k) > 1}, key=str):
        raise HTTPException(
            status_code=400,
            detail="Danh sách có điểm chuẩn trùng: " + "; ".join(_mo_ta_khoa(k) for k in trung[:10]),
        )

    def bang(cot, value):
        return cot.is_(None) if value is None else cot == value

    dieu_kien = [
        and_(
            XtDiemChuan.ma_truong == k[0],
            XtDiemChuan.nam_tuyen_sinh == k[1],
            XtDiemChuan.ma_xet_tuyen == k[2],
            bang(XtDiemChuan.ma_phuong_thuc_cua_bo, k[3]),
            bang(XtDiemChuan.to_hop_id, k[4]),
        )
        for k in set(khoa)
    ]
    stmt = select(XtDiemChuan).where(or_(*dieu_kien))
    if bo_qua_id is not None:
        stmt = stmt.where(XtDiemChuan.id != bo_qua_id)
    da_co = db.scalars(stmt.limit(10)).all()
    if da_co:
        raise HTTPException(
            status_code=400,
            detail="Đã có điểm chuẩn: " + "; ".join(f"{_mo_ta_khoa(_khoa(i))} (id = {i.id})" for i in da_co),
        )


def _apply(item: XtDiemChuan, payload: XtDiemChuanWrite, *, creating: bool) -> None:
    now = bay_gio()
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    if creating:
        item.tao_luc = now
    item.cap_nhat_luc = now


def _commit(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Không lưu được điểm chuẩn") from None


@router.get("", response_model=XtDiemChuanPage)
def list_diem_chuan(
    q: str | None = Query(default=None, max_length=255),
    ma_truong: str | None = Query(default=None, max_length=20),
    nam_tuyen_sinh: int | None = Query(default=None, ge=1990, le=2100),
    ma_phuong_thuc_cua_bo: str | None = Query(default=None, max_length=20),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    db: Session = Depends(get_db),
) -> XtDiemChuanPage:
    """Danh sách điểm chuẩn có phân trang, lọc theo từ khóa, trường, năm và phương thức."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                XtDiemChuan.ma_xet_tuyen.like(pattern, escape="\\"),
                XtDiemChuan.ten_chuong_trinh.like(pattern, escape="\\"),
                XtDiemChuan.ma_truong.like(pattern, escape="\\"),
                DmTruong.ten_truong.like(pattern, escape="\\"),
                cast(XtDiemChuan.nam_tuyen_sinh, String).like(pattern, escape="\\"),
            )
        )
    if ma_truong and ma_truong.strip():
        filters.append(XtDiemChuan.ma_truong == ma_truong.strip())
    if nam_tuyen_sinh is not None:
        filters.append(XtDiemChuan.nam_tuyen_sinh == nam_tuyen_sinh)
    if ma_phuong_thuc_cua_bo and ma_phuong_thuc_cua_bo.strip():
        filters.append(XtDiemChuan.ma_phuong_thuc_cua_bo == ma_phuong_thuc_cua_bo.strip())

    stmt = _joined().where(*filters)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.execute(
        stmt.order_by(
            XtDiemChuan.nam_tuyen_sinh.desc(),
            XtDiemChuan.ma_truong.asc(),
            XtDiemChuan.ma_xet_tuyen.asc(),
            XtDiemChuan.id.asc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return XtDiemChuanPage(items=[_to_public(*row) for row in rows], total=total, page=page, page_size=page_size)


@router.get("/{item_id}", response_model=XtDiemChuanPublic)
def get_diem_chuan(item_id: int, db: Session = Depends(get_db)) -> XtDiemChuanPublic:
    """Chi tiết một dòng điểm chuẩn theo id."""
    _get_or_400(db, item_id)
    return _load_public(db, item_id)


@router.post("/bulk", response_model=XtDiemChuanBulkResult, status_code=status.HTTP_201_CREATED)
def create_diem_chuan_bulk(payload: list[XtDiemChuanWrite], db: Session = Depends(get_db)) -> XtDiemChuanBulkResult:
    """Nhập nhiều dòng điểm chuẩn trong một transaction; một dòng lỗi thì không lưu dòng nào."""
    if not payload:
        raise HTTPException(status_code=400, detail="Danh sách điểm chuẩn trống")
    if len(payload) > _TOI_DA_NHAP:
        raise HTTPException(status_code=400, detail=f"Chỉ nhập tối đa {_TOI_DA_NHAP} dòng điểm chuẩn mỗi lần")
    _kiem_tra(db, payload)
    items = []
    for data in payload:
        item = XtDiemChuan()
        _apply(item, data, creating=True)
        items.append(item)
    db.add_all(items)
    _commit(db)
    return XtDiemChuanBulkResult(created=len(items))


@router.post("", response_model=XtDiemChuanPublic, status_code=status.HTTP_201_CREATED)
def create_diem_chuan(payload: XtDiemChuanWrite, db: Session = Depends(get_db)) -> XtDiemChuanPublic:
    """Thêm một dòng điểm chuẩn."""
    _kiem_tra(db, [payload])
    item = XtDiemChuan()
    _apply(item, payload, creating=True)
    db.add(item)
    _commit(db)
    return _load_public(db, item.id)


@router.put("/{item_id}", response_model=XtDiemChuanPublic)
def update_diem_chuan(item_id: int, payload: XtDiemChuanWrite, db: Session = Depends(get_db)) -> XtDiemChuanPublic:
    """Cập nhật một dòng điểm chuẩn."""
    item = _get_or_400(db, item_id)
    _kiem_tra(db, [payload], bo_qua_id=item_id)
    _apply(item, payload, creating=False)
    _commit(db)
    return _load_public(db, item_id)


@router.delete("", response_model=XtDiemChuanDeleteManyResult)
def delete_diem_chuan_many(payload: XtDiemChuanDeleteMany, db: Session = Depends(get_db)) -> XtDiemChuanDeleteManyResult:
    """Xóa nhiều dòng điểm chuẩn theo id; id không tồn tại thì bỏ qua."""
    items = db.scalars(select(XtDiemChuan).where(XtDiemChuan.id.in_(payload.ids))).all()
    for item in items:
        db.delete(item)
    _commit(db)
    return XtDiemChuanDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_diem_chuan(item_id: int, db: Session = Depends(get_db)) -> None:
    """Xóa một dòng điểm chuẩn."""
    db.delete(_get_or_400(db, item_id))
    _commit(db)
