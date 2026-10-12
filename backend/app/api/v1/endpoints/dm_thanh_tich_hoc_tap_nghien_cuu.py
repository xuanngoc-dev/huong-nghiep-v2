from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.dm_thanh_tich_hoc_tap_nghien_cuu import DmThanhTichHocTapNghienCuu
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_thanh_tich_hoc_tap_nghien_cuu import (
    DmThanhTichHocTapNghienCuuBulkResult,
    DmThanhTichHocTapNghienCuuDeleteMany,
    DmThanhTichHocTapNghienCuuDeleteManyResult,
    DmThanhTichHocTapNghienCuuPage,
    DmThanhTichHocTapNghienCuuPublic,
    DmThanhTichHocTapNghienCuuWrite,
)

router = APIRouter(prefix="/danh-muc/thanh-tich-hoc-tap-nghien-cuu", tags=["danh-muc"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _get_or_404(db: Session, item_id: int) -> DmThanhTichHocTapNghienCuu:
    """Lấy một bản ghi theo id. Trả lỗi 404 nếu không tồn tại."""
    item = db.get(DmThanhTichHocTapNghienCuu, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thành tích học tập, nghiên cứu",
        )
    return item


@router.get("", response_model=DmThanhTichHocTapNghienCuuPage)
def list_thanh_tich_hoc_tap_nghien_cuu(
    q: str | None = Query(default=None, max_length=255),
    trang_thai: int | None = Query(default=None, ge=0, le=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmThanhTichHocTapNghienCuuPage:
    """Lấy danh sách thành tích học tập, nghiên cứu có phân trang."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmThanhTichHocTapNghienCuu.ten_thanh_tich.like(pattern, escape="\\"),
                DmThanhTichHocTapNghienCuu.ma_thanh_tich.like(pattern, escape="\\"),
                DmThanhTichHocTapNghienCuu.ten_chi_tiet.like(pattern, escape="\\"),
                DmThanhTichHocTapNghienCuu.linh_vuc.like(pattern, escape="\\"),
                DmThanhTichHocTapNghienCuu.mon.like(pattern, escape="\\"),
            )
        )
    if trang_thai is not None:
        filters.append(DmThanhTichHocTapNghienCuu.trang_thai == trang_thai)

    count_stmt = select(func.count()).select_from(DmThanhTichHocTapNghienCuu)
    stmt = select(DmThanhTichHocTapNghienCuu)
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    items = db.scalars(
        stmt.order_by(DmThanhTichHocTapNghienCuu.ma_thanh_tich.asc(), DmThanhTichHocTapNghienCuu.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmThanhTichHocTapNghienCuuPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{item_id}", response_model=DmThanhTichHocTapNghienCuuPublic)
def get_thanh_tich_hoc_tap_nghien_cuu(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmThanhTichHocTapNghienCuu:
    """Lấy chi tiết một thành tích học tập, nghiên cứu theo id."""
    return _get_or_404(db, item_id)


@router.post("/bulk", response_model=DmThanhTichHocTapNghienCuuBulkResult, status_code=status.HTTP_201_CREATED)
def create_thanh_tich_hoc_tap_nghien_cuu_bulk(
    payload: list[DmThanhTichHocTapNghienCuuWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmThanhTichHocTapNghienCuuBulkResult:
    """Thêm nhiều thành tích học tập, nghiên cứu cùng lúc."""
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Danh sách thành tích học tập, nghiên cứu trống",
        )
    if len(payload) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ thêm tối đa 500 thành tích học tập, nghiên cứu mỗi lần",
        )

    codes = [item.ma_thanh_tich for item in payload]
    seen: set[str] = set()
    duplicated: list[str] = []
    for code in codes:
        if code in seen and code not in duplicated:
            duplicated.append(code)
        seen.add(code)
    if duplicated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã thành tích bị trùng trong dữ liệu: {', '.join(duplicated)}",
        )

    existing = list(
        db.scalars(
            select(DmThanhTichHocTapNghienCuu.ma_thanh_tich).where(DmThanhTichHocTapNghienCuu.ma_thanh_tich.in_(codes))
        ).all()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã thành tích đã tồn tại: {', '.join(existing)}",
        )

    items = [DmThanhTichHocTapNghienCuu(**item.model_dump()) for item in payload]
    db.add_all(items)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã thành tích đã tồn tại",
        ) from None
    return DmThanhTichHocTapNghienCuuBulkResult(created=len(items))


@router.post("", response_model=DmThanhTichHocTapNghienCuuPublic, status_code=status.HTTP_201_CREATED)
def create_thanh_tich_hoc_tap_nghien_cuu(
    payload: DmThanhTichHocTapNghienCuuWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmThanhTichHocTapNghienCuu:
    """Thêm một thành tích học tập, nghiên cứu. Từ chối nếu mã đã tồn tại."""
    item = DmThanhTichHocTapNghienCuu(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã thành tích đã tồn tại",
        ) from None
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=DmThanhTichHocTapNghienCuuPublic)
def update_thanh_tich_hoc_tap_nghien_cuu(
    item_id: int,
    payload: DmThanhTichHocTapNghienCuuWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmThanhTichHocTapNghienCuu:
    """Cập nhật toàn bộ thông tin một thành tích học tập, nghiên cứu theo id."""
    item = _get_or_404(db, item_id)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã thành tích đã tồn tại",
        ) from None
    db.refresh(item)
    return item


@router.delete("", response_model=DmThanhTichHocTapNghienCuuDeleteManyResult)
def delete_thanh_tich_hoc_tap_nghien_cuu_many(
    payload: DmThanhTichHocTapNghienCuuDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmThanhTichHocTapNghienCuuDeleteManyResult:
    """Xóa nhiều thành tích học tập, nghiên cứu theo danh sách id."""
    items = db.scalars(select(DmThanhTichHocTapNghienCuu).where(DmThanhTichHocTapNghienCuu.id.in_(payload.ids))).all()
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thành tích học tập, nghiên cứu để xóa",
        )
    for item in items:
        db.delete(item)
    db.commit()
    return DmThanhTichHocTapNghienCuuDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_thanh_tich_hoc_tap_nghien_cuu(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> None:
    """Xóa một thành tích học tập, nghiên cứu theo id."""
    item = _get_or_404(db, item_id)
    db.delete(item)
    db.commit()
