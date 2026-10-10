from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.dm_nhom_tinh_cach_holland import DmNhomTinhCachHolland
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_nhom_tinh_cach_holland import (
    DmNhomTinhCachHollandBulkResult,
    DmNhomTinhCachHollandDeleteMany,
    DmNhomTinhCachHollandDeleteManyResult,
    DmNhomTinhCachHollandPage,
    DmNhomTinhCachHollandPublic,
    DmNhomTinhCachHollandWrite,
)

router = APIRouter(prefix="/danh-muc/nhom-tinh-cach-holland", tags=["danh-muc"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _get_or_404(db: Session, item_id: int) -> DmNhomTinhCachHolland:
    """Lấy một nhóm tính cách Holland theo id. Trả lỗi 404 nếu không tồn tại."""
    item = db.get(DmNhomTinhCachHolland, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy nhóm tính cách Holland",
        )
    return item


@router.get("", response_model=DmNhomTinhCachHollandPage)
def list_nhom_tinh_cach_holland(
    q: str | None = Query(default=None, max_length=150),
    trang_thai: int | None = Query(default=None, ge=0, le=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmNhomTinhCachHollandPage:
    """Lấy danh sách nhóm Holland có phân trang. Lọc theo từ khóa (tên, mã, tên tiếng Anh) và trạng thái."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmNhomTinhCachHolland.ten_nhom.like(pattern, escape="\\"),
                DmNhomTinhCachHolland.ma_nhom.like(pattern, escape="\\"),
                DmNhomTinhCachHolland.ten_tieng_anh.like(pattern, escape="\\"),
            )
        )
    if trang_thai is not None:
        filters.append(DmNhomTinhCachHolland.trang_thai == trang_thai)

    count_stmt = select(func.count()).select_from(DmNhomTinhCachHolland)
    stmt = select(DmNhomTinhCachHolland)
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    items = db.scalars(
        stmt.order_by(DmNhomTinhCachHolland.ma_nhom.asc(), DmNhomTinhCachHolland.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmNhomTinhCachHollandPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{item_id}", response_model=DmNhomTinhCachHollandPublic)
def get_nhom_tinh_cach_holland(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmNhomTinhCachHolland:
    """Lấy chi tiết một nhóm tính cách Holland theo id."""
    return _get_or_404(db, item_id)


@router.post("/bulk", response_model=DmNhomTinhCachHollandBulkResult, status_code=status.HTTP_201_CREATED)
def create_nhom_tinh_cach_holland_bulk(
    payload: list[DmNhomTinhCachHollandWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmNhomTinhCachHollandBulkResult:
    """Thêm nhiều nhóm Holland cùng lúc. Từ chối nếu mã nhóm trùng trong dữ liệu gửi lên hoặc đã có trong hệ thống."""
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách nhóm Holland trống")
    if len(payload) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ thêm tối đa 500 nhóm mỗi lần",
        )

    codes = [item.ma_nhom for item in payload]
    seen: set[str] = set()
    duplicated: list[str] = []
    for code in codes:
        if code in seen and code not in duplicated:
            duplicated.append(code)
        seen.add(code)
    if duplicated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã nhóm bị trùng trong dữ liệu: {', '.join(duplicated)}",
        )

    existing = list(
        db.scalars(
            select(DmNhomTinhCachHolland.ma_nhom).where(DmNhomTinhCachHolland.ma_nhom.in_(codes))
        ).all()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã nhóm đã tồn tại: {', '.join(existing)}",
        )

    items = [DmNhomTinhCachHolland(**item.model_dump()) for item in payload]
    db.add_all(items)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã nhóm đã tồn tại",
        ) from None
    return DmNhomTinhCachHollandBulkResult(created=len(items))


@router.post("", response_model=DmNhomTinhCachHollandPublic, status_code=status.HTTP_201_CREATED)
def create_nhom_tinh_cach_holland(
    payload: DmNhomTinhCachHollandWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmNhomTinhCachHolland:
    """Thêm một nhóm tính cách Holland. Từ chối nếu mã nhóm đã tồn tại."""
    item = DmNhomTinhCachHolland(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã nhóm đã tồn tại",
        ) from None
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=DmNhomTinhCachHollandPublic)
def update_nhom_tinh_cach_holland(
    item_id: int,
    payload: DmNhomTinhCachHollandWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmNhomTinhCachHolland:
    """Cập nhật toàn bộ thông tin một nhóm tính cách Holland theo id."""
    item = _get_or_404(db, item_id)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã nhóm đã tồn tại",
        ) from None
    db.refresh(item)
    return item


@router.delete("", response_model=DmNhomTinhCachHollandDeleteManyResult)
def delete_nhom_tinh_cach_holland_many(
    payload: DmNhomTinhCachHollandDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmNhomTinhCachHollandDeleteManyResult:
    """Xóa nhiều nhóm tính cách Holland theo danh sách id."""
    items = db.scalars(
        select(DmNhomTinhCachHolland).where(DmNhomTinhCachHolland.id.in_(payload.ids))
    ).all()
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy nhóm tính cách Holland để xóa",
        )
    for item in items:
        db.delete(item)
    db.commit()
    return DmNhomTinhCachHollandDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_nhom_tinh_cach_holland(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> None:
    """Xóa một nhóm tính cách Holland theo id."""
    item = _get_or_404(db, item_id)
    db.delete(item)
    db.commit()
