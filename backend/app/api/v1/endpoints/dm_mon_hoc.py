from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.dm_mon_hoc import DmMonHoc
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_mon_hoc import (
    DmMonHocBulkResult,
    DmMonHocDeleteMany,
    DmMonHocDeleteManyResult,
    DmMonHocPage,
    DmMonHocPublic,
    DmMonHocWrite,
)

router = APIRouter(prefix="/danh-muc/mon-hoc", tags=["danh-muc"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _get_or_404(db: Session, item_id: int) -> DmMonHoc:
    """Lấy một môn học theo id. Trả lỗi 404 nếu không tồn tại."""
    item = db.get(DmMonHoc, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy môn học")
    return item


@router.get("", response_model=DmMonHocPage)
def list_mon_hoc(
    q: str | None = Query(default=None, max_length=150),
    trang_thai: int | None = Query(default=None, ge=0, le=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmMonHocPage:
    """Lấy danh sách môn học có phân trang. Lọc theo từ khóa (tên, mã, tên viết tắt, nhóm môn) và trạng thái."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmMonHoc.ten_mon_hoc.like(pattern, escape="\\"),
                DmMonHoc.ma_mon_hoc.like(pattern, escape="\\"),
                DmMonHoc.ten_viet_tat.like(pattern, escape="\\"),
                DmMonHoc.nhom_mon.like(pattern, escape="\\"),
            )
        )
    if trang_thai is not None:
        filters.append(DmMonHoc.trang_thai == trang_thai)

    count_stmt = select(func.count()).select_from(DmMonHoc)
    stmt = select(DmMonHoc)
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    items = db.scalars(
        stmt.order_by(DmMonHoc.ma_mon_hoc.asc(), DmMonHoc.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmMonHocPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{item_id}", response_model=DmMonHocPublic)
def get_mon_hoc(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmMonHoc:
    """Lấy chi tiết một môn học theo id."""
    return _get_or_404(db, item_id)


@router.post("/bulk", response_model=DmMonHocBulkResult, status_code=status.HTTP_201_CREATED)
def create_mon_hoc_bulk(
    payload: list[DmMonHocWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmMonHocBulkResult:
    """Thêm nhiều môn học cùng lúc. Từ chối nếu mã môn trùng trong dữ liệu gửi lên hoặc đã có trong hệ thống."""
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách môn học trống")
    if len(payload) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ thêm tối đa 500 môn học mỗi lần",
        )

    codes = [item.ma_mon_hoc for item in payload]
    seen: set[str] = set()
    duplicated: list[str] = []
    for code in codes:
        if code in seen and code not in duplicated:
            duplicated.append(code)
        seen.add(code)
    if duplicated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã môn học bị trùng trong dữ liệu: {', '.join(duplicated)}",
        )

    existing = list(
        db.scalars(select(DmMonHoc.ma_mon_hoc).where(DmMonHoc.ma_mon_hoc.in_(codes))).all()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã môn học đã tồn tại: {', '.join(existing)}",
        )

    items = [DmMonHoc(**item.model_dump()) for item in payload]
    db.add_all(items)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã môn học đã tồn tại",
        ) from None
    return DmMonHocBulkResult(created=len(items))


@router.post("", response_model=DmMonHocPublic, status_code=status.HTTP_201_CREATED)
def create_mon_hoc(
    payload: DmMonHocWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmMonHoc:
    """Thêm một môn học. Từ chối nếu mã môn đã tồn tại."""
    item = DmMonHoc(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã môn học đã tồn tại",
        ) from None
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=DmMonHocPublic)
def update_mon_hoc(
    item_id: int,
    payload: DmMonHocWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmMonHoc:
    """Cập nhật toàn bộ thông tin một môn học theo id."""
    item = _get_or_404(db, item_id)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã môn học đã tồn tại",
        ) from None
    db.refresh(item)
    return item


@router.delete("", response_model=DmMonHocDeleteManyResult)
def delete_mon_hoc_many(
    payload: DmMonHocDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmMonHocDeleteManyResult:
    """Xóa nhiều môn học theo danh sách id."""
    items = db.scalars(select(DmMonHoc).where(DmMonHoc.id.in_(payload.ids))).all()
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy môn học để xóa",
        )
    for item in items:
        db.delete(item)
    db.commit()
    return DmMonHocDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mon_hoc(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> None:
    """Xóa một môn học theo id."""
    item = _get_or_404(db, item_id)
    db.delete(item)
    db.commit()
