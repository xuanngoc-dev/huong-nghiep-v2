from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.dm_tinh_thanh import DmTinhThanh
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_tinh_thanh import (
    DmTinhThanhBulkResult,
    DmTinhThanhDeleteMany,
    DmTinhThanhDeleteManyResult,
    DmTinhThanhPage,
    DmTinhThanhPublic,
    DmTinhThanhWrite,
)

router = APIRouter(prefix="/danh-muc/tinh-thanh", tags=["danh-muc"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _get_or_404(db: Session, item_id: int) -> DmTinhThanh:
    """Lấy một bản ghi theo id. Trả lỗi 404 nếu không tồn tại."""
    item = db.get(DmTinhThanh, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy tỉnh thành")
    return item


@router.get("", response_model=DmTinhThanhPage)
def list_tinh_thanh(
    q: str | None = Query(default=None, max_length=150),
    khu_vuc: str | None = Query(default=None, max_length=100),
    trang_thai: int | None = Query(default=None, ge=0, le=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmTinhThanhPage:
    """Lấy danh sách tỉnh thành có phân trang. Lọc theo từ khóa (tên, mã), khu vực và trạng thái."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmTinhThanh.ten_tinh.like(pattern, escape="\\"),
                DmTinhThanh.ma_tinh.like(pattern, escape="\\"),
            )
        )
    if khu_vuc and khu_vuc.strip():
        filters.append(DmTinhThanh.khu_vuc == khu_vuc.strip())
    if trang_thai is not None:
        filters.append(DmTinhThanh.trang_thai == trang_thai)

    count_stmt = select(func.count()).select_from(DmTinhThanh)
    stmt = select(DmTinhThanh)
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    items = db.scalars(
        stmt.order_by(DmTinhThanh.ma_tinh.asc(), DmTinhThanh.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmTinhThanhPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{item_id}", response_model=DmTinhThanhPublic)
def get_tinh_thanh(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmTinhThanh:
    """Lấy chi tiết một tỉnh thành theo id."""
    return _get_or_404(db, item_id)


@router.post("/bulk", response_model=DmTinhThanhBulkResult, status_code=status.HTTP_201_CREATED)
def create_tinh_thanh_bulk(
    payload: list[DmTinhThanhWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmTinhThanhBulkResult:
    """Thêm nhiều tỉnh thành cùng lúc. Từ chối nếu mã tỉnh trùng trong dữ liệu gửi lên hoặc đã có trong hệ thống."""
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách tỉnh thành trống")
    if len(payload) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ thêm tối đa 500 tỉnh thành mỗi lần",
        )

    codes = [item.ma_tinh for item in payload]
    seen: set[str] = set()
    duplicated: list[str] = []
    for code in codes:
        if code in seen and code not in duplicated:
            duplicated.append(code)
        seen.add(code)
    if duplicated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã tỉnh bị trùng trong dữ liệu: {', '.join(duplicated)}",
        )

    existing = list(
        db.scalars(select(DmTinhThanh.ma_tinh).where(DmTinhThanh.ma_tinh.in_(codes))).all()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã tỉnh đã tồn tại: {', '.join(existing)}",
        )

    items = [DmTinhThanh(**item.model_dump()) for item in payload]
    db.add_all(items)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã tỉnh đã tồn tại",
        ) from None
    return DmTinhThanhBulkResult(created=len(items))


@router.post("", response_model=DmTinhThanhPublic, status_code=status.HTTP_201_CREATED)
def create_tinh_thanh(
    payload: DmTinhThanhWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmTinhThanh:
    """Thêm một tỉnh thành. Từ chối nếu mã tỉnh đã tồn tại."""
    item = DmTinhThanh(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã tỉnh đã tồn tại",
        ) from None
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=DmTinhThanhPublic)
def update_tinh_thanh(
    item_id: int,
    payload: DmTinhThanhWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmTinhThanh:
    """Cập nhật toàn bộ thông tin một tỉnh thành theo id."""
    item = _get_or_404(db, item_id)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã tỉnh đã tồn tại",
        ) from None
    db.refresh(item)
    return item


@router.delete("", response_model=DmTinhThanhDeleteManyResult)
def delete_tinh_thanh_many(
    payload: DmTinhThanhDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmTinhThanhDeleteManyResult:
    """Xóa nhiều tỉnh thành theo danh sách id."""
    items = db.scalars(select(DmTinhThanh).where(DmTinhThanh.id.in_(payload.ids))).all()
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy tỉnh thành để xóa",
        )
    for item in items:
        db.delete(item)
    db.commit()
    return DmTinhThanhDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tinh_thanh(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> None:
    """Xóa một tỉnh thành theo id."""
    item = _get_or_404(db, item_id)
    db.delete(item)
    db.commit()
