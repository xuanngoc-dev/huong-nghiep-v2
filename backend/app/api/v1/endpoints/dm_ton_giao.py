from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.dm_ton_giao import DmTonGiao
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_ton_giao import (
    DmTonGiaoBulkResult,
    DmTonGiaoDeleteMany,
    DmTonGiaoDeleteManyResult,
    DmTonGiaoPage,
    DmTonGiaoPublic,
    DmTonGiaoWrite,
)

router = APIRouter(prefix="/danh-muc/ton-giao", tags=["danh-muc"])


def _like_pattern(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _get_or_404(db: Session, item_id: int) -> DmTonGiao:
    item = db.get(DmTonGiao, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy tôn giáo")
    return item


@router.get("", response_model=DmTonGiaoPage)
def list_ton_giao(
    q: str | None = Query(default=None, max_length=150),
    trang_thai: int | None = Query(default=None, ge=0, le=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmTonGiaoPage:
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmTonGiao.ten_ton_giao.like(pattern, escape="\\"),
                DmTonGiao.ma_ton_giao.like(pattern, escape="\\"),
            )
        )
    if trang_thai is not None:
        filters.append(DmTonGiao.trang_thai == trang_thai)

    count_stmt = select(func.count()).select_from(DmTonGiao)
    stmt = select(DmTonGiao)
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    items = db.scalars(
        stmt.order_by(DmTonGiao.ma_ton_giao.asc(), DmTonGiao.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmTonGiaoPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{item_id}", response_model=DmTonGiaoPublic)
def get_ton_giao(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmTonGiao:
    return _get_or_404(db, item_id)


@router.post("/bulk", response_model=DmTonGiaoBulkResult, status_code=status.HTTP_201_CREATED)
def create_ton_giao_bulk(
    payload: list[DmTonGiaoWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmTonGiaoBulkResult:
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách tôn giáo trống")
    if len(payload) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ thêm tối đa 500 tôn giáo mỗi lần",
        )

    codes = [item.ma_ton_giao for item in payload]
    seen: set[str] = set()
    duplicated: list[str] = []
    for code in codes:
        if code in seen and code not in duplicated:
            duplicated.append(code)
        seen.add(code)
    if duplicated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã tôn giáo bị trùng trong dữ liệu: {', '.join(duplicated)}",
        )

    existing = list(
        db.scalars(select(DmTonGiao.ma_ton_giao).where(DmTonGiao.ma_ton_giao.in_(codes))).all()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã tôn giáo đã tồn tại: {', '.join(existing)}",
        )

    items = [DmTonGiao(**item.model_dump()) for item in payload]
    db.add_all(items)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã tôn giáo đã tồn tại",
        ) from None
    return DmTonGiaoBulkResult(created=len(items))


@router.post("", response_model=DmTonGiaoPublic, status_code=status.HTTP_201_CREATED)
def create_ton_giao(
    payload: DmTonGiaoWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmTonGiao:
    item = DmTonGiao(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã tôn giáo đã tồn tại",
        ) from None
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=DmTonGiaoPublic)
def update_ton_giao(
    item_id: int,
    payload: DmTonGiaoWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmTonGiao:
    item = _get_or_404(db, item_id)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã tôn giáo đã tồn tại",
        ) from None
    db.refresh(item)
    return item


@router.delete("", response_model=DmTonGiaoDeleteManyResult)
def delete_ton_giao_many(
    payload: DmTonGiaoDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmTonGiaoDeleteManyResult:
    items = db.scalars(select(DmTonGiao).where(DmTonGiao.id.in_(payload.ids))).all()
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy tôn giáo để xóa",
        )
    for item in items:
        db.delete(item)
    db.commit()
    return DmTonGiaoDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ton_giao(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> None:
    item = _get_or_404(db, item_id)
    db.delete(item)
    db.commit()
