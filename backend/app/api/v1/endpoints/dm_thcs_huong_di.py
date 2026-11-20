from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_current_user
from app.db.session import get_db
from app.models.dm_thcs_huong_di import DmThcsHuongDi
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_thcs_huong_di import (
    DmThcsDeleteMany,
    DmThcsHuongDiPage,
    DmThcsHuongDiPublic,
    DmThcsHuongDiTrangThai,
    DmThcsHuongDiTrangThaiMany,
    DmThcsHuongDiWrite,
    KetQuaDoiTrangThaiNhieu,
    KetQuaThemNhieu,
    KetQuaXoaNhieu,
    MucDoApLucHocTap,
)
from app.services.thcs_huong_di import like_pattern as _like_pattern

router = APIRouter(prefix="/danh-muc/thcs/huong-di", tags=["danh-muc"])


def _get_or_400(db: Session, item_id: int) -> DmThcsHuongDi:
    """Lấy một hướng đi THCS theo id. Trả lỗi 400 kèm thông báo nếu không tồn tại."""
    item = db.get(DmThcsHuongDi, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy hướng đi THCS có id = {item_id}",
        )
    return item


def _loi_trung_ma() -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mã hướng đi đã tồn tại")


@router.get("", response_model=DmThcsHuongDiPage)
def list_thcs_huong_di(
    q: str | None = Query(default=None, max_length=255),
    trang_thai: int | None = Query(default=None, ge=0, le=1),
    muc_do_ap_luc_hoc_tap: MucDoApLucHocTap | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
) -> DmThcsHuongDiPage:
    """Lấy danh sách hướng đi sau THCS có phân trang, không cần đăng nhập."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmThcsHuongDi.ma_huong.like(pattern, escape="\\"),
                DmThcsHuongDi.ten_huong.like(pattern, escape="\\"),
                DmThcsHuongDi.ma_holland.like(pattern, escape="\\"),
            )
        )
    if trang_thai is not None:
        filters.append(DmThcsHuongDi.trang_thai == trang_thai)
    if muc_do_ap_luc_hoc_tap is not None:
        filters.append(DmThcsHuongDi.muc_do_ap_luc_hoc_tap == muc_do_ap_luc_hoc_tap)

    total = db.scalar(select(func.count()).select_from(DmThcsHuongDi).where(*filters)) or 0
    items = db.scalars(
        select(DmThcsHuongDi)
        .where(*filters)
        .order_by(DmThcsHuongDi.thu_tu_hien_thi.asc(), DmThcsHuongDi.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmThcsHuongDiPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{item_id}", response_model=DmThcsHuongDiPublic)
def get_thcs_huong_di(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmThcsHuongDi:
    """Lấy chi tiết một hướng đi THCS theo id."""
    return _get_or_400(db, item_id)


@router.post("/bulk", response_model=KetQuaThemNhieu, status_code=status.HTTP_201_CREATED)
def create_thcs_huong_di_bulk(
    payload: list[DmThcsHuongDiWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaThemNhieu:
    """Thêm nhiều hướng đi cùng lúc. Từ chối nếu mã trùng trong dữ liệu gửi lên hoặc đã có trong hệ thống."""
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách hướng đi trống")
    if len(payload) > 500:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chỉ thêm tối đa 500 hướng đi mỗi lần")

    codes = [item.ma_huong for item in payload]
    duplicated = sorted({code for code in codes if codes.count(code) > 1})
    if duplicated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã hướng đi bị trùng trong dữ liệu: {', '.join(duplicated)}",
        )
    existing = list(db.scalars(select(DmThcsHuongDi.ma_huong).where(DmThcsHuongDi.ma_huong.in_(codes))).all())
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã hướng đi đã tồn tại: {', '.join(existing)}",
        )

    items = [DmThcsHuongDi(**item.model_dump()) for item in payload]
    db.add_all(items)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise _loi_trung_ma() from None
    return KetQuaThemNhieu(created=len(items))


@router.post("", response_model=DmThcsHuongDiPublic, status_code=status.HTTP_201_CREATED)
def create_thcs_huong_di(
    payload: DmThcsHuongDiWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThcsHuongDi:
    """Thêm một hướng đi THCS. Từ chối nếu mã đã tồn tại."""
    item = DmThcsHuongDi(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise _loi_trung_ma() from None
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=DmThcsHuongDiPublic)
def update_thcs_huong_di(
    item_id: int,
    payload: DmThcsHuongDiWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThcsHuongDi:
    """Cập nhật toàn bộ thông tin một hướng đi THCS theo id."""
    item = _get_or_400(db, item_id)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise _loi_trung_ma() from None
    db.refresh(item)
    return item


@router.patch("/trang-thai", response_model=KetQuaDoiTrangThaiNhieu)
def update_trang_thai_thcs_huong_di_many(
    payload: DmThcsHuongDiTrangThaiMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaDoiTrangThaiNhieu:
    """Bật/tắt nhiều hướng đi cùng lúc. Id không tồn tại thì bỏ qua."""
    items = db.scalars(select(DmThcsHuongDi).where(DmThcsHuongDi.id.in_(payload.ids))).all()
    for item in items:
        item.trang_thai = payload.trang_thai
    db.commit()
    return KetQuaDoiTrangThaiNhieu(updated=len(items))


@router.patch("/{item_id}/trang-thai", response_model=DmThcsHuongDiPublic)
def update_trang_thai_thcs_huong_di(
    item_id: int,
    payload: DmThcsHuongDiTrangThai,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThcsHuongDi:
    """Bật/tắt nhanh một hướng đi, giữ nguyên các thông tin khác."""
    item = _get_or_400(db, item_id)
    item.trang_thai = payload.trang_thai
    db.commit()
    db.refresh(item)
    return item


@router.delete("", response_model=KetQuaXoaNhieu)
def delete_thcs_huong_di_many(
    payload: DmThcsDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaXoaNhieu:
    """Xóa nhiều hướng đi theo danh sách id; ưu/nhược điểm, điểm tiêu chí, lời khuyên bị xóa theo."""
    items = db.scalars(select(DmThcsHuongDi).where(DmThcsHuongDi.id.in_(payload.ids))).all()
    for item in items:
        db.delete(item)
    db.commit()
    return KetQuaXoaNhieu(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_thcs_huong_di(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> None:
    """Xóa một hướng đi theo id; ưu/nhược điểm, điểm tiêu chí, lời khuyên bị xóa theo (CASCADE)."""
    db.delete(_get_or_400(db, item_id))
    db.commit()
