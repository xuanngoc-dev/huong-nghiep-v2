from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.dm_dan_toc import DmDanToc
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_dan_toc import (
    DmDanTocBulkResult,
    DmDanTocDeleteMany,
    DmDanTocDeleteManyResult,
    DmDanTocPage,
    DmDanTocPublic,
    DmDanTocWrite,
)

router = APIRouter(prefix="/danh-muc/dan-toc", tags=["danh-muc"])


def _like_pattern(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _get_or_404(db: Session, item_id: int) -> DmDanToc:
    item = db.get(DmDanToc, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy dân tộc")
    return item


@router.get("", response_model=DmDanTocPage)
def list_dan_toc(
    q: str | None = Query(default=None, max_length=150),
    trang_thai: int | None = Query(default=None, ge=0, le=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmDanTocPage:
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmDanToc.ten_dan_toc.like(pattern, escape="\\"),
                DmDanToc.ma_dan_toc.like(pattern, escape="\\"),
                DmDanToc.ten_goi_khac.like(pattern, escape="\\"),
            )
        )
    if trang_thai is not None:
        filters.append(DmDanToc.trang_thai == trang_thai)

    count_stmt = select(func.count()).select_from(DmDanToc)
    stmt = select(DmDanToc)
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    items = db.scalars(
        stmt.order_by(DmDanToc.ma_dan_toc.asc(), DmDanToc.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmDanTocPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{item_id}", response_model=DmDanTocPublic)
def get_dan_toc(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmDanToc:
    return _get_or_404(db, item_id)


@router.post("/bulk", response_model=DmDanTocBulkResult, status_code=status.HTTP_201_CREATED)
def create_dan_toc_bulk(
    payload: list[DmDanTocWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmDanTocBulkResult:
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách dân tộc trống")
    if len(payload) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ thêm tối đa 500 dân tộc mỗi lần",
        )

    codes = [item.ma_dan_toc for item in payload]
    seen: set[str] = set()
    duplicated: list[str] = []
    for code in codes:
        if code in seen and code not in duplicated:
            duplicated.append(code)
        seen.add(code)
    if duplicated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã dân tộc bị trùng trong dữ liệu: {', '.join(duplicated)}",
        )

    existing = list(
        db.scalars(select(DmDanToc.ma_dan_toc).where(DmDanToc.ma_dan_toc.in_(codes))).all()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã dân tộc đã tồn tại: {', '.join(existing)}",
        )

    items = [DmDanToc(**item.model_dump()) for item in payload]
    db.add_all(items)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã dân tộc đã tồn tại",
        ) from None
    return DmDanTocBulkResult(created=len(items))


@router.post("", response_model=DmDanTocPublic, status_code=status.HTTP_201_CREATED)
def create_dan_toc(
    payload: DmDanTocWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmDanToc:
    item = DmDanToc(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã dân tộc đã tồn tại",
        ) from None
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=DmDanTocPublic)
def update_dan_toc(
    item_id: int,
    payload: DmDanTocWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmDanToc:
    item = _get_or_404(db, item_id)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã dân tộc đã tồn tại",
        ) from None
    db.refresh(item)
    return item


@router.delete("", response_model=DmDanTocDeleteManyResult)
def delete_dan_toc_many(
    payload: DmDanTocDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmDanTocDeleteManyResult:
    items = db.scalars(select(DmDanToc).where(DmDanToc.id.in_(payload.ids))).all()
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy dân tộc để xóa",
        )
    for item in items:
        db.delete(item)
    db.commit()
    return DmDanTocDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dan_toc(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> None:
    item = _get_or_404(db, item_id)
    db.delete(item)
    db.commit()
