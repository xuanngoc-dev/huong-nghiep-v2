
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_current_user
from app.core.thoi_gian import bay_gio
from app.db.session import get_db
from app.models.dm_truong import DmTruong
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_truong import (
    DmTruongBulkResult,
    DmTruongDeleteMany,
    DmTruongDeleteManyResult,
    DmTruongPage,
    DmTruongPublic,
    DmTruongWrite,
)
from app.services.truong_hien_thi import loai_hien_thi

router = APIRouter(prefix="/danh-muc/truong-hoc", tags=["danh-muc"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _integrity_detail(exc: IntegrityError, *, deleting: bool = False) -> str:
    message = str(getattr(exc, "orig", "") or exc).lower()
    if deleting or "1451" in message:
        return "Không xóa được vì còn dữ liệu liên quan"
    if "truong_cha" in message:
        return "Trường trực thuộc không tồn tại"
    return "Mã trường đã tồn tại"


def _get_or_400(db: Session, item_id: int) -> DmTruong:
    """Lấy một bản ghi theo id. Trả lỗi 400 kèm thông báo nếu không tồn tại."""
    item = db.get(DmTruong, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy trường học có id = {item_id}",
        )
    return item


def _ensure_parent(db: Session, parent_id: int | None, item_id: int | None = None) -> None:
    if parent_id is None:
        return
    if item_id is not None and parent_id == item_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trường không thể trực thuộc chính nó",
        )
    if db.get(DmTruong, parent_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trường trực thuộc không tồn tại",
        )


@router.get("", response_model=DmTruongPage)
def list_truong(
    q: str | None = Query(default=None, max_length=255),
    vung_mien: str | None = Query(default=None, max_length=20),
    loai_hinh: str | None = Query(default=None, max_length=50),
    loai_co_so: str | None = Query(default=None, max_length=50),
    trang_thai_hoat_dong: str | None = Query(default=None, max_length=30),
    ngau_nhien: bool = Query(default=False),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
) -> DmTruongPage:
    """Lấy danh sách trường học từ dm_truong, có phân trang, không cần đăng nhập.

    `ngau_nhien` trả về theo thứ tự ngẫu nhiên.
    """
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmTruong.ten_truong.like(pattern, escape="\\"),
                DmTruong.ma_truong.like(pattern, escape="\\"),
                DmTruong.ten_viet_tat.like(pattern, escape="\\"),
                DmTruong.ten_tieng_anh.like(pattern, escape="\\"),
                DmTruong.ten_tinh_thanh.like(pattern, escape="\\"),
            )
        )
    if vung_mien and vung_mien.strip():
        filters.append(DmTruong.vung_mien.like(_like_pattern(vung_mien.strip()), escape="\\"))
    if loai_hinh and loai_hinh.strip():
        filters.append(DmTruong.loai_hinh == loai_hinh.strip())
    if loai_co_so and loai_co_so.strip():
        # Nhiều trường chưa khai báo loại cơ sở, nên lọc theo loại suy ra từ tên trường.
        filters.append(loai_hien_thi() == loai_co_so.strip())
    if trang_thai_hoat_dong and trang_thai_hoat_dong.strip():
        filters.append(DmTruong.trang_thai_hoat_dong == trang_thai_hoat_dong.strip())

    count_stmt = select(func.count()).select_from(DmTruong)
    stmt = select(DmTruong)
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    items = db.scalars(
        stmt.order_by(*([func.rand()] if ngau_nhien else [DmTruong.ten_truong.asc(), DmTruong.id.asc()]))
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmTruongPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{item_id}", response_model=DmTruongPublic)
def get_truong(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmTruong:
    """Lấy chi tiết một trường học theo id."""
    return _get_or_400(db, item_id)


@router.post("/bulk", response_model=DmTruongBulkResult, status_code=status.HTTP_201_CREATED)
def create_truong_bulk(
    payload: list[DmTruongWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmTruongBulkResult:
    """Thêm nhiều trường học cùng lúc. Mã đã có trong hệ thống thì ghi đè; trùng mã trong dữ liệu thì từ chối."""
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách trường học trống")
    if len(payload) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ thêm tối đa 500 trường học mỗi lần",
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

    existing_rows = db.scalars(select(DmTruong).where(DmTruong.ma_truong.in_(codes))).all()
    existing_by_ma = {row.ma_truong: row for row in existing_rows}

    parent_ids = {item.truong_cha_id for item in payload if item.truong_cha_id}
    if parent_ids:
        found = set(db.scalars(select(DmTruong.id).where(DmTruong.id.in_(parent_ids))).all())
        if parent_ids - found:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Trường trực thuộc không tồn tại",
            )

    now = bay_gio()
    created_items: list[DmTruong] = []
    updated = 0
    for data in payload:
        row = existing_by_ma.get(data.ma_truong)
        if row is None:
            created_items.append(DmTruong(**data.model_dump(), tao_luc=now, cap_nhat_luc=now))
            continue
        if data.truong_cha_id is not None and data.truong_cha_id == row.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Trường không thể trực thuộc chính nó",
            )
        for key, value in data.model_dump().items():
            setattr(row, key, value)
        row.cap_nhat_luc = now
        updated += 1

    if created_items:
        db.add_all(created_items)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_integrity_detail(exc)) from None
    return DmTruongBulkResult(created=len(created_items), updated=updated)


@router.post("", response_model=DmTruongPublic, status_code=status.HTTP_201_CREATED)
def create_truong(
    payload: DmTruongWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmTruong:
    """Thêm một trường học. Từ chối nếu mã trường đã tồn tại."""
    _ensure_parent(db, payload.truong_cha_id)
    now = bay_gio()
    item = DmTruong(**payload.model_dump(), tao_luc=now, cap_nhat_luc=now)
    db.add(item)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_integrity_detail(exc)) from None
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=DmTruongPublic)
def update_truong(
    item_id: int,
    payload: DmTruongWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmTruong:
    """Cập nhật toàn bộ thông tin một trường học theo id."""
    item = _get_or_400(db, item_id)
    _ensure_parent(db, payload.truong_cha_id, item_id)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    item.cap_nhat_luc = bay_gio()
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_integrity_detail(exc)) from None
    db.refresh(item)
    return item


@router.delete("", response_model=DmTruongDeleteManyResult)
def delete_truong_many(
    payload: DmTruongDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmTruongDeleteManyResult:
    """Xóa nhiều trường học theo danh sách id."""
    items = db.scalars(select(DmTruong).where(DmTruong.id.in_(payload.ids))).all()
    if not items:
        return DmTruongDeleteManyResult(deleted=0)
    for item in items:
        db.delete(item)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_integrity_detail(exc, deleting=True),
        ) from None
    return DmTruongDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_truong(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> None:
    """Xóa một trường học theo id."""
    item = _get_or_400(db, item_id)
    db.delete(item)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_integrity_detail(exc, deleting=True),
        ) from None
