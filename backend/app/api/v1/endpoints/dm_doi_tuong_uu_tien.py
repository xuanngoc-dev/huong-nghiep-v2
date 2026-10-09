from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.dm_doi_tuong_uu_tien import DmDoiTuongUuTien
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_doi_tuong_uu_tien import (
    DmDoiTuongUuTienBulkResult,
    DmDoiTuongUuTienDeleteMany,
    DmDoiTuongUuTienDeleteManyResult,
    DmDoiTuongUuTienPage,
    DmDoiTuongUuTienPublic,
    DmDoiTuongUuTienWrite,
)

router = APIRouter(prefix="/danh-muc/doi-tuong-uu-tien", tags=["danh-muc"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _get_or_404(db: Session, item_id: int) -> DmDoiTuongUuTien:
    """Lấy một bản ghi theo id. Trả lỗi 404 nếu không tồn tại."""
    item = db.get(DmDoiTuongUuTien, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy đối tượng ưu tiên")
    return item


@router.get("", response_model=DmDoiTuongUuTienPage)
def list_doi_tuong_uu_tien(
    q: str | None = Query(default=None, max_length=150),
    trang_thai: int | None = Query(default=None, ge=0, le=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmDoiTuongUuTienPage:
    """Lấy danh sách đối tượng ưu tiên có phân trang. Lọc theo từ khóa (tên, mã) và trạng thái."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmDoiTuongUuTien.ten_doi_tuong.like(pattern, escape="\\"),
                DmDoiTuongUuTien.ma_doi_tuong.like(pattern, escape="\\"),
            )
        )
    if trang_thai is not None:
        filters.append(DmDoiTuongUuTien.trang_thai == trang_thai)

    count_stmt = select(func.count()).select_from(DmDoiTuongUuTien)
    stmt = select(DmDoiTuongUuTien)
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    items = db.scalars(
        stmt.order_by(DmDoiTuongUuTien.ma_doi_tuong.asc(), DmDoiTuongUuTien.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmDoiTuongUuTienPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{item_id}", response_model=DmDoiTuongUuTienPublic)
def get_doi_tuong_uu_tien(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmDoiTuongUuTien:
    """Lấy chi tiết một đối tượng ưu tiên theo id."""
    return _get_or_404(db, item_id)


@router.post("/bulk", response_model=DmDoiTuongUuTienBulkResult, status_code=status.HTTP_201_CREATED)
def create_doi_tuong_uu_tien_bulk(
    payload: list[DmDoiTuongUuTienWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmDoiTuongUuTienBulkResult:
    """Thêm nhiều đối tượng ưu tiên cùng lúc. Từ chối nếu mã đối tượng trùng trong dữ liệu gửi lên hoặc đã có trong hệ thống."""
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách đối tượng ưu tiên trống")
    if len(payload) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ thêm tối đa 500 đối tượng ưu tiên mỗi lần",
        )

    codes = [item.ma_doi_tuong for item in payload]
    seen: set[str] = set()
    duplicated: list[str] = []
    for code in codes:
        if code in seen and code not in duplicated:
            duplicated.append(code)
        seen.add(code)
    if duplicated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã đối tượng bị trùng trong dữ liệu: {', '.join(duplicated)}",
        )

    existing = list(
        db.scalars(
            select(DmDoiTuongUuTien.ma_doi_tuong).where(DmDoiTuongUuTien.ma_doi_tuong.in_(codes))
        ).all()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã đối tượng đã tồn tại: {', '.join(existing)}",
        )

    items = [DmDoiTuongUuTien(**item.model_dump()) for item in payload]
    db.add_all(items)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã đối tượng đã tồn tại",
        ) from None
    return DmDoiTuongUuTienBulkResult(created=len(items))


@router.post("", response_model=DmDoiTuongUuTienPublic, status_code=status.HTTP_201_CREATED)
def create_doi_tuong_uu_tien(
    payload: DmDoiTuongUuTienWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmDoiTuongUuTien:
    """Thêm một đối tượng ưu tiên. Từ chối nếu mã đối tượng đã tồn tại."""
    item = DmDoiTuongUuTien(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã đối tượng đã tồn tại",
        ) from None
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=DmDoiTuongUuTienPublic)
def update_doi_tuong_uu_tien(
    item_id: int,
    payload: DmDoiTuongUuTienWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmDoiTuongUuTien:
    """Cập nhật toàn bộ thông tin một đối tượng ưu tiên theo id."""
    item = _get_or_404(db, item_id)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã đối tượng đã tồn tại",
        ) from None
    db.refresh(item)
    return item


@router.delete("", response_model=DmDoiTuongUuTienDeleteManyResult)
def delete_doi_tuong_uu_tien_many(
    payload: DmDoiTuongUuTienDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmDoiTuongUuTienDeleteManyResult:
    """Xóa nhiều đối tượng ưu tiên theo danh sách id."""
    items = db.scalars(select(DmDoiTuongUuTien).where(DmDoiTuongUuTien.id.in_(payload.ids))).all()
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy đối tượng ưu tiên để xóa",
        )
    for item in items:
        db.delete(item)
    db.commit()
    return DmDoiTuongUuTienDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doi_tuong_uu_tien(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> None:
    """Xóa một đối tượng ưu tiên theo id."""
    item = _get_or_404(db, item_id)
    db.delete(item)
    db.commit()
