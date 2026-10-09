from fastapi import APIRouter, Depends, HTTPException, Query, status  # pyright: ignore[reportMissingImports]
from sqlalchemy import func, or_, select  # pyright: ignore[reportMissingImports]
from sqlalchemy.exc import IntegrityError  # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import Session  # pyright: ignore[reportMissingImports]

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.dm_phuong_thuc_tuyen_sinh import DmPhuongThucTuyenSinh
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_phuong_thuc_tuyen_sinh import (
    DmPhuongThucTuyenSinhBulkResult,
    DmPhuongThucTuyenSinhDeleteMany,
    DmPhuongThucTuyenSinhDeleteManyResult,
    DmPhuongThucTuyenSinhPage,
    DmPhuongThucTuyenSinhPublic,
    DmPhuongThucTuyenSinhWrite,
)

router = APIRouter(prefix="/danh-muc/phuong-thuc-tuyen-sinh", tags=["danh-muc"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _get_or_404(db: Session, item_id: int) -> DmPhuongThucTuyenSinh:
    """Lấy một bản ghi theo id. Trả lỗi 404 nếu không tồn tại."""
    item = db.get(DmPhuongThucTuyenSinh, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy phương thức tuyển sinh",
        )
    return item


@router.get("", response_model=DmPhuongThucTuyenSinhPage)
def list_phuong_thuc_tuyen_sinh(
    q: str | None = Query(default=None, max_length=255),
    trang_thai: int | None = Query(default=None, ge=0, le=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmPhuongThucTuyenSinhPage:
    """Lấy danh sách phương thức tuyển sinh có phân trang. Lọc theo từ khóa (tên, mã) và trạng thái."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmPhuongThucTuyenSinh.ten_phuong_thuc.like(pattern, escape="\\"),
                DmPhuongThucTuyenSinh.ma_phuong_thuc.like(pattern, escape="\\"),
            )
        )
    if trang_thai is not None:
        filters.append(DmPhuongThucTuyenSinh.trang_thai == trang_thai)

    count_stmt = select(func.count()).select_from(DmPhuongThucTuyenSinh)
    stmt = select(DmPhuongThucTuyenSinh)
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    items = db.scalars(
        stmt.order_by(DmPhuongThucTuyenSinh.ma_phuong_thuc.asc(), DmPhuongThucTuyenSinh.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmPhuongThucTuyenSinhPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{item_id}", response_model=DmPhuongThucTuyenSinhPublic)
def get_phuong_thuc_tuyen_sinh(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmPhuongThucTuyenSinh:
    """Lấy chi tiết một phương thức tuyển sinh theo id."""
    return _get_or_404(db, item_id)


@router.post("/bulk", response_model=DmPhuongThucTuyenSinhBulkResult, status_code=status.HTTP_201_CREATED)
def create_phuong_thuc_tuyen_sinh_bulk(
    payload: list[DmPhuongThucTuyenSinhWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmPhuongThucTuyenSinhBulkResult:
    """Thêm nhiều phương thức tuyển sinh cùng lúc. Từ chối nếu mã phương thức trùng trong dữ liệu gửi lên hoặc đã có trong hệ thống."""
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Danh sách phương thức tuyển sinh trống",
        )
    if len(payload) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ thêm tối đa 500 phương thức tuyển sinh mỗi lần",
        )

    codes = [item.ma_phuong_thuc for item in payload]
    seen: set[str] = set()
    duplicated: list[str] = []
    for code in codes:
        if code in seen and code not in duplicated:
            duplicated.append(code)
        seen.add(code)
    if duplicated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã phương thức bị trùng trong dữ liệu: {', '.join(duplicated)}",
        )

    existing = list(
        db.scalars(
            select(DmPhuongThucTuyenSinh.ma_phuong_thuc).where(
                DmPhuongThucTuyenSinh.ma_phuong_thuc.in_(codes)
            )
        ).all()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã phương thức đã tồn tại: {', '.join(existing)}",
        )

    items = [DmPhuongThucTuyenSinh(**item.model_dump()) for item in payload]
    db.add_all(items)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã phương thức đã tồn tại",
        ) from None
    return DmPhuongThucTuyenSinhBulkResult(created=len(items))


@router.post("", response_model=DmPhuongThucTuyenSinhPublic, status_code=status.HTTP_201_CREATED)
def create_phuong_thuc_tuyen_sinh(
    payload: DmPhuongThucTuyenSinhWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmPhuongThucTuyenSinh:
    """Thêm một phương thức tuyển sinh. Từ chối nếu mã phương thức đã tồn tại."""
    item = DmPhuongThucTuyenSinh(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã phương thức đã tồn tại",
        ) from None
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=DmPhuongThucTuyenSinhPublic)
def update_phuong_thuc_tuyen_sinh(
    item_id: int,
    payload: DmPhuongThucTuyenSinhWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmPhuongThucTuyenSinh:
    """Cập nhật toàn bộ thông tin một phương thức tuyển sinh theo id."""
    item = _get_or_404(db, item_id)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã phương thức đã tồn tại",
        ) from None
    db.refresh(item)
    return item


@router.delete("", response_model=DmPhuongThucTuyenSinhDeleteManyResult)
def delete_phuong_thuc_tuyen_sinh_many(
    payload: DmPhuongThucTuyenSinhDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmPhuongThucTuyenSinhDeleteManyResult:
    """Xóa nhiều phương thức tuyển sinh theo danh sách id."""
    items = db.scalars(
        select(DmPhuongThucTuyenSinh).where(DmPhuongThucTuyenSinh.id.in_(payload.ids))
    ).all()
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy phương thức tuyển sinh để xóa",
        )
    for item in items:
        db.delete(item)
    db.commit()
    return DmPhuongThucTuyenSinhDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_phuong_thuc_tuyen_sinh(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> None:
    """Xóa một phương thức tuyển sinh theo id."""
    item = _get_or_404(db, item_id)
    db.delete(item)
    db.commit()
