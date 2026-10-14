from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.dm_truong_dai_hoc import DmTruongDaiHoc
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_truong_dai_hoc import (
    DmTruongDaiHocBulkResult,
    DmTruongDaiHocDeleteMany,
    DmTruongDaiHocDeleteManyResult,
    DmTruongDaiHocPage,
    DmTruongDaiHocPublic,
    DmTruongDaiHocWrite,
)

router = APIRouter(prefix="/danh-muc/truong-hoc", tags=["danh-muc"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _get_or_404(db: Session, item_id: int) -> DmTruongDaiHoc:
    """Lấy một bản ghi theo id. Trả lỗi 404 nếu không tồn tại."""
    item = db.get(DmTruongDaiHoc, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy trường đại học")
    return item


@router.get("", response_model=DmTruongDaiHocPage)
def list_truong_dai_hoc(
    q: str | None = Query(default=None, max_length=255),
    khu_vuc: str | None = Query(default=None, max_length=50),
    loai_hinh_dao_tao: str | None = Query(default=None, max_length=50),
    trang_thai: int | None = Query(default=None, ge=0, le=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmTruongDaiHocPage:
    """Lấy danh sách trường đại học có phân trang."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmTruongDaiHoc.ten_truong.like(pattern, escape="\\"),
                DmTruongDaiHoc.ma_truong.like(pattern, escape="\\"),
                DmTruongDaiHoc.ten_viet_tat.like(pattern, escape="\\"),
                DmTruongDaiHoc.ten_tieng_anh.like(pattern, escape="\\"),
            )
        )
    if khu_vuc and khu_vuc.strip():
        filters.append(DmTruongDaiHoc.khu_vuc.like(_like_pattern(khu_vuc.strip()), escape="\\"))
    if loai_hinh_dao_tao and loai_hinh_dao_tao.strip():
        filters.append(DmTruongDaiHoc.loai_hinh_dao_tao == loai_hinh_dao_tao.strip())
    if trang_thai is not None:
        filters.append(DmTruongDaiHoc.trang_thai == trang_thai)

    count_stmt = select(func.count()).select_from(DmTruongDaiHoc)
    stmt = select(DmTruongDaiHoc)
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    items = db.scalars(
        stmt.order_by(DmTruongDaiHoc.ten_truong.asc(), DmTruongDaiHoc.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmTruongDaiHocPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{item_id}", response_model=DmTruongDaiHocPublic)
def get_truong_dai_hoc(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmTruongDaiHoc:
    """Lấy chi tiết một trường đại học theo id."""
    return _get_or_404(db, item_id)


@router.post("/bulk", response_model=DmTruongDaiHocBulkResult, status_code=status.HTTP_201_CREATED)
def create_truong_dai_hoc_bulk(
    payload: list[DmTruongDaiHocWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmTruongDaiHocBulkResult:
    """Thêm nhiều trường đại học cùng lúc. Từ chối nếu mã trường trùng trong dữ liệu hoặc đã có trong hệ thống."""
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách trường đại học trống")
    if len(payload) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ thêm tối đa 500 trường đại học mỗi lần",
        )

    codes = [item.ma_truong for item in payload]
    seen: set[str] = set()
    duplicated: list[str] = []
    for code in codes:
        if code in seen and code not in duplicated:
            duplicated.append(code)
        seen.add(code)
    if duplicated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã trường bị trùng trong dữ liệu: {', '.join(duplicated)}",
        )

    existing = list(
        db.scalars(select(DmTruongDaiHoc.ma_truong).where(DmTruongDaiHoc.ma_truong.in_(codes))).all()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã trường đã tồn tại: {', '.join(existing)}",
        )

    items = [DmTruongDaiHoc(**item.model_dump()) for item in payload]
    db.add_all(items)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã trường đã tồn tại",
        ) from None
    return DmTruongDaiHocBulkResult(created=len(items))


@router.post("", response_model=DmTruongDaiHocPublic, status_code=status.HTTP_201_CREATED)
def create_truong_dai_hoc(
    payload: DmTruongDaiHocWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmTruongDaiHoc:
    """Thêm một trường đại học. Từ chối nếu mã trường đã tồn tại."""
    item = DmTruongDaiHoc(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã trường đã tồn tại",
        ) from None
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=DmTruongDaiHocPublic)
def update_truong_dai_hoc(
    item_id: int,
    payload: DmTruongDaiHocWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmTruongDaiHoc:
    """Cập nhật toàn bộ thông tin một trường đại học theo id."""
    item = _get_or_404(db, item_id)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã trường đã tồn tại",
        ) from None
    db.refresh(item)
    return item


@router.delete("", response_model=DmTruongDaiHocDeleteManyResult)
def delete_truong_dai_hoc_many(
    payload: DmTruongDaiHocDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmTruongDaiHocDeleteManyResult:
    """Xóa nhiều trường đại học theo danh sách id."""
    items = db.scalars(select(DmTruongDaiHoc).where(DmTruongDaiHoc.id.in_(payload.ids))).all()
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy trường đại học để xóa",
        )
    for item in items:
        db.delete(item)
    db.commit()
    return DmTruongDaiHocDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_truong_dai_hoc(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> None:
    """Xóa một trường đại học theo id."""
    item = _get_or_404(db, item_id)
    db.delete(item)
    db.commit()
