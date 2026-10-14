from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.dm_chung_chi_ngoai_ngu import DmChungChiNgoaiNgu
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_chung_chi_ngoai_ngu import (
    DmChungChiNgoaiNguBulkResult,
    DmChungChiNgoaiNguDeleteMany,
    DmChungChiNgoaiNguDeleteManyResult,
    DmChungChiNgoaiNguPage,
    DmChungChiNgoaiNguPublic,
    DmChungChiNgoaiNguWrite,
)

router = APIRouter(prefix="/danh-muc/chung-chi-ngoai-ngu", tags=["danh-muc"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _get_or_404(db: Session, item_id: int) -> DmChungChiNgoaiNgu:
    """Lấy một bản ghi theo id. Trả lỗi 404 nếu không tồn tại."""
    item = db.get(DmChungChiNgoaiNgu, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy chứng chỉ ngoại ngữ",
        )
    return item


@router.get("", response_model=DmChungChiNgoaiNguPage)
def list_chung_chi_ngoai_ngu(
    q: str | None = Query(default=None, max_length=255),
    trang_thai: int | None = Query(default=None, ge=0, le=1),
    loai_chung_chi: str | None = Query(default=None, max_length=20),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmChungChiNgoaiNguPage:
    """Lấy danh sách chứng chỉ ngoại ngữ có phân trang."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmChungChiNgoaiNgu.ten_chung_chi.like(pattern, escape="\\"),
                DmChungChiNgoaiNgu.ma_chung_chi.like(pattern, escape="\\"),
                DmChungChiNgoaiNgu.ten_chi_tiet.like(pattern, escape="\\"),
                DmChungChiNgoaiNgu.linh_vuc.like(pattern, escape="\\"),
                DmChungChiNgoaiNgu.mon.like(pattern, escape="\\"),
            )
        )
    if trang_thai is not None:
        filters.append(DmChungChiNgoaiNgu.trang_thai == trang_thai)
    if loai_chung_chi and loai_chung_chi.strip():
        filters.append(DmChungChiNgoaiNgu.loai_chung_chi == loai_chung_chi.strip().lower())

    count_stmt = select(func.count()).select_from(DmChungChiNgoaiNgu)
    stmt = select(DmChungChiNgoaiNgu)
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    items = db.scalars(
        stmt.order_by(DmChungChiNgoaiNgu.ma_chung_chi.asc(), DmChungChiNgoaiNgu.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmChungChiNgoaiNguPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{item_id}", response_model=DmChungChiNgoaiNguPublic)
def get_chung_chi_ngoai_ngu(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmChungChiNgoaiNgu:
    """Lấy chi tiết một chứng chỉ ngoại ngữ theo id."""
    return _get_or_404(db, item_id)


@router.post("/bulk", response_model=DmChungChiNgoaiNguBulkResult, status_code=status.HTTP_201_CREATED)
def create_chung_chi_ngoai_ngu_bulk(
    payload: list[DmChungChiNgoaiNguWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmChungChiNgoaiNguBulkResult:
    """Thêm nhiều chứng chỉ ngoại ngữ cùng lúc."""
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Danh sách chứng chỉ ngoại ngữ trống",
        )
    if len(payload) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ thêm tối đa 500 chứng chỉ ngoại ngữ mỗi lần",
        )

    codes = [item.ma_chung_chi for item in payload]
    seen: set[str] = set()
    duplicated: list[str] = []
    for code in codes:
        if code in seen and code not in duplicated:
            duplicated.append(code)
        seen.add(code)
    if duplicated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã chứng chỉ bị trùng trong dữ liệu: {', '.join(duplicated)}",
        )

    existing = list(
        db.scalars(
            select(DmChungChiNgoaiNgu.ma_chung_chi).where(DmChungChiNgoaiNgu.ma_chung_chi.in_(codes))
        ).all()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã chứng chỉ đã tồn tại: {', '.join(existing)}",
        )

    items = [DmChungChiNgoaiNgu(**item.model_dump()) for item in payload]
    db.add_all(items)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã chứng chỉ đã tồn tại",
        ) from None
    return DmChungChiNgoaiNguBulkResult(created=len(items))


@router.post("", response_model=DmChungChiNgoaiNguPublic, status_code=status.HTTP_201_CREATED)
def create_chung_chi_ngoai_ngu(
    payload: DmChungChiNgoaiNguWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmChungChiNgoaiNgu:
    """Thêm một chứng chỉ ngoại ngữ. Từ chối nếu mã đã tồn tại."""
    item = DmChungChiNgoaiNgu(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã chứng chỉ đã tồn tại",
        ) from None
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=DmChungChiNgoaiNguPublic)
def update_chung_chi_ngoai_ngu(
    item_id: int,
    payload: DmChungChiNgoaiNguWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmChungChiNgoaiNgu:
    """Cập nhật toàn bộ thông tin một chứng chỉ ngoại ngữ theo id."""
    item = _get_or_404(db, item_id)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã chứng chỉ đã tồn tại",
        ) from None
    db.refresh(item)
    return item


@router.delete("", response_model=DmChungChiNgoaiNguDeleteManyResult)
def delete_chung_chi_ngoai_ngu_many(
    payload: DmChungChiNgoaiNguDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmChungChiNgoaiNguDeleteManyResult:
    """Xóa nhiều chứng chỉ ngoại ngữ theo danh sách id."""
    items = db.scalars(select(DmChungChiNgoaiNgu).where(DmChungChiNgoaiNgu.id.in_(payload.ids))).all()
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy chứng chỉ ngoại ngữ để xóa",
        )
    for item in items:
        db.delete(item)
    db.commit()
    return DmChungChiNgoaiNguDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chung_chi_ngoai_ngu(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> None:
    """Xóa một chứng chỉ ngoại ngữ theo id."""
    item = _get_or_404(db, item_id)
    db.delete(item)
    db.commit()
