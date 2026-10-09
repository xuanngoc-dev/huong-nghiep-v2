from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.dm_khu_vuc_uu_tien import DmKhuVucUuTien
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_khu_vuc_uu_tien import (
    DmKhuVucUuTienBulkResult,
    DmKhuVucUuTienDeleteMany,
    DmKhuVucUuTienDeleteManyResult,
    DmKhuVucUuTienPage,
    DmKhuVucUuTienPublic,
    DmKhuVucUuTienWrite,
)

router = APIRouter(prefix="/danh-muc/khu-vuc-uu-tien", tags=["danh-muc"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _get_or_404(db: Session, item_id: int) -> DmKhuVucUuTien:
    """Lấy một bản ghi theo id. Trả lỗi 404 nếu không tồn tại."""
    item = db.get(DmKhuVucUuTien, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy khu vực ưu tiên")
    return item


@router.get("", response_model=DmKhuVucUuTienPage)
def list_khu_vuc_uu_tien(
    q: str | None = Query(default=None, max_length=150),
    trang_thai: int | None = Query(default=None, ge=0, le=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmKhuVucUuTienPage:
    """Lấy danh sách khu vực ưu tiên có phân trang. Lọc theo từ khóa (tên, mã) và trạng thái."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmKhuVucUuTien.ten_khu_vuc.like(pattern, escape="\\"),
                DmKhuVucUuTien.ma_khu_vuc.like(pattern, escape="\\"),
            )
        )
    if trang_thai is not None:
        filters.append(DmKhuVucUuTien.trang_thai == trang_thai)

    count_stmt = select(func.count()).select_from(DmKhuVucUuTien)
    stmt = select(DmKhuVucUuTien)
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    items = db.scalars(
        stmt.order_by(DmKhuVucUuTien.ma_khu_vuc.asc(), DmKhuVucUuTien.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmKhuVucUuTienPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{item_id}", response_model=DmKhuVucUuTienPublic)
def get_khu_vuc_uu_tien(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmKhuVucUuTien:
    """Lấy chi tiết một khu vực ưu tiên theo id."""
    return _get_or_404(db, item_id)


@router.post("/bulk", response_model=DmKhuVucUuTienBulkResult, status_code=status.HTTP_201_CREATED)
def create_khu_vuc_uu_tien_bulk(
    payload: list[DmKhuVucUuTienWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmKhuVucUuTienBulkResult:
    """Thêm nhiều khu vực ưu tiên cùng lúc. Từ chối nếu mã khu vực trùng trong dữ liệu gửi lên hoặc đã có trong hệ thống."""
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách khu vực ưu tiên trống")
    if len(payload) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ thêm tối đa 500 khu vực ưu tiên mỗi lần",
        )

    codes = [item.ma_khu_vuc for item in payload]
    seen: set[str] = set()
    duplicated: list[str] = []
    for code in codes:
        if code in seen and code not in duplicated:
            duplicated.append(code)
        seen.add(code)
    if duplicated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã khu vực bị trùng trong dữ liệu: {', '.join(duplicated)}",
        )

    existing = list(
        db.scalars(select(DmKhuVucUuTien.ma_khu_vuc).where(DmKhuVucUuTien.ma_khu_vuc.in_(codes))).all()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã khu vực đã tồn tại: {', '.join(existing)}",
        )

    items = [DmKhuVucUuTien(**item.model_dump()) for item in payload]
    db.add_all(items)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã khu vực đã tồn tại",
        ) from None
    return DmKhuVucUuTienBulkResult(created=len(items))


@router.post("", response_model=DmKhuVucUuTienPublic, status_code=status.HTTP_201_CREATED)
def create_khu_vuc_uu_tien(
    payload: DmKhuVucUuTienWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmKhuVucUuTien:
    """Thêm một khu vực ưu tiên. Từ chối nếu mã khu vực đã tồn tại."""
    item = DmKhuVucUuTien(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã khu vực đã tồn tại",
        ) from None
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=DmKhuVucUuTienPublic)
def update_khu_vuc_uu_tien(
    item_id: int,
    payload: DmKhuVucUuTienWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmKhuVucUuTien:
    """Cập nhật toàn bộ thông tin một khu vực ưu tiên theo id."""
    item = _get_or_404(db, item_id)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã khu vực đã tồn tại",
        ) from None
    db.refresh(item)
    return item


@router.delete("", response_model=DmKhuVucUuTienDeleteManyResult)
def delete_khu_vuc_uu_tien_many(
    payload: DmKhuVucUuTienDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmKhuVucUuTienDeleteManyResult:
    """Xóa nhiều khu vực ưu tiên theo danh sách id."""
    items = db.scalars(select(DmKhuVucUuTien).where(DmKhuVucUuTien.id.in_(payload.ids))).all()
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy khu vực ưu tiên để xóa",
        )
    for item in items:
        db.delete(item)
    db.commit()
    return DmKhuVucUuTienDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_khu_vuc_uu_tien(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> None:
    """Xóa một khu vực ưu tiên theo id."""
    item = _get_or_404(db, item_id)
    db.delete(item)
    db.commit()
