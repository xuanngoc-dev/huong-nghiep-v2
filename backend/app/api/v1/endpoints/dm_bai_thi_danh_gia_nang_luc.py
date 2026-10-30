from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.dm_bai_thi_danh_gia import DmBaiThiDanhGia
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_bai_thi_danh_gia_nang_luc import (
    DmBaiThiDanhGiaNangLucBulkResult,
    DmBaiThiDanhGiaNangLucDeleteMany,
    DmBaiThiDanhGiaNangLucDeleteManyResult,
    DmBaiThiDanhGiaNangLucPage,
    DmBaiThiDanhGiaNangLucPublic,
    DmBaiThiDanhGiaNangLucWrite,
    normalize_trang_thai,
)

router = APIRouter(prefix="/danh-muc/bai-thi-danh-gia-nang-luc", tags=["danh-muc"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _get_or_404(db: Session, item_id: int) -> DmBaiThiDanhGia:
    """Lấy một bản ghi theo id. Trả lỗi 404 nếu không tồn tại."""
    item = db.get(DmBaiThiDanhGia, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bài thi đánh giá năng lực",
        )
    return item


@router.get("", response_model=DmBaiThiDanhGiaNangLucPage)
def list_bai_thi_danh_gia_nang_luc(
    q: str | None = Query(default=None, max_length=255),
    trang_thai: str | None = Query(default=None, max_length=20),
    loai_chung_chi: str | None = Query(default=None, max_length=50),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmBaiThiDanhGiaNangLucPage:
    """Lấy danh sách bài thi đánh giá năng lực có phân trang."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmBaiThiDanhGia.ten_bai_thi.like(pattern, escape="\\"),
                DmBaiThiDanhGia.ma_bai_thi.like(pattern, escape="\\"),
                DmBaiThiDanhGia.ten_chi_tiet.like(pattern, escape="\\"),
                DmBaiThiDanhGia.linh_vuc.like(pattern, escape="\\"),
                DmBaiThiDanhGia.mon.like(pattern, escape="\\"),
                DmBaiThiDanhGia.ten_viet_tat.like(pattern, escape="\\"),
                DmBaiThiDanhGia.don_vi_to_chuc.like(pattern, escape="\\"),
                DmBaiThiDanhGia.loai_danh_gia.like(pattern, escape="\\"),
            )
        )
    if trang_thai and trang_thai.strip():
        filters.append(DmBaiThiDanhGia.trang_thai == (normalize_trang_thai(trang_thai) or trang_thai.strip()))
    if loai_chung_chi and loai_chung_chi.strip():
        filters.append(DmBaiThiDanhGia.loai_chung_chi == loai_chung_chi.strip().lower())

    count_stmt = select(func.count()).select_from(DmBaiThiDanhGia)
    stmt = select(DmBaiThiDanhGia)
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    items = db.scalars(
        stmt.order_by(DmBaiThiDanhGia.ma_bai_thi.asc(), DmBaiThiDanhGia.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmBaiThiDanhGiaNangLucPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{item_id}", response_model=DmBaiThiDanhGiaNangLucPublic)
def get_bai_thi_danh_gia_nang_luc(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmBaiThiDanhGia:
    """Lấy chi tiết một bài thi đánh giá năng lực theo id."""
    return _get_or_404(db, item_id)


@router.post("/bulk", response_model=DmBaiThiDanhGiaNangLucBulkResult, status_code=status.HTTP_201_CREATED)
def create_bai_thi_danh_gia_nang_luc_bulk(
    payload: list[DmBaiThiDanhGiaNangLucWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmBaiThiDanhGiaNangLucBulkResult:
    """Thêm nhiều bài thi đánh giá năng lực cùng lúc."""
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Danh sách bài thi đánh giá năng lực trống",
        )
    if len(payload) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ thêm tối đa 500 bài thi đánh giá năng lực mỗi lần",
        )

    codes = [item.ma_bai_thi for item in payload]
    seen: set[str] = set()
    duplicated: list[str] = []
    for code in codes:
        if code in seen and code not in duplicated:
            duplicated.append(code)
        seen.add(code)
    if duplicated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã bài thi bị trùng trong dữ liệu: {', '.join(duplicated)}",
        )

    existing = list(
        db.scalars(
            select(DmBaiThiDanhGia.ma_bai_thi).where(DmBaiThiDanhGia.ma_bai_thi.in_(codes))
        ).all()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã bài thi đã tồn tại: {', '.join(existing)}",
        )

    items = [DmBaiThiDanhGia(**item.model_dump()) for item in payload]
    db.add_all(items)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã bài thi đã tồn tại",
        ) from None
    return DmBaiThiDanhGiaNangLucBulkResult(created=len(items))


@router.post("", response_model=DmBaiThiDanhGiaNangLucPublic, status_code=status.HTTP_201_CREATED)
def create_bai_thi_danh_gia_nang_luc(
    payload: DmBaiThiDanhGiaNangLucWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmBaiThiDanhGia:
    """Thêm một bài thi đánh giá năng lực. Từ chối nếu mã đã tồn tại."""
    item = DmBaiThiDanhGia(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã bài thi đã tồn tại",
        ) from None
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=DmBaiThiDanhGiaNangLucPublic)
def update_bai_thi_danh_gia_nang_luc(
    item_id: int,
    payload: DmBaiThiDanhGiaNangLucWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmBaiThiDanhGia:
    """Cập nhật toàn bộ thông tin một bài thi đánh giá năng lực theo id."""
    item = _get_or_404(db, item_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã bài thi đã tồn tại",
        ) from None
    db.refresh(item)
    return item


@router.delete("", response_model=DmBaiThiDanhGiaNangLucDeleteManyResult)
def delete_bai_thi_danh_gia_nang_luc_many(
    payload: DmBaiThiDanhGiaNangLucDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmBaiThiDanhGiaNangLucDeleteManyResult:
    """Xóa nhiều bài thi đánh giá năng lực theo danh sách id."""
    items = db.scalars(select(DmBaiThiDanhGia).where(DmBaiThiDanhGia.id.in_(payload.ids))).all()
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bài thi đánh giá năng lực để xóa",
        )
    for item in items:
        db.delete(item)
    db.commit()
    return DmBaiThiDanhGiaNangLucDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bai_thi_danh_gia_nang_luc(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> None:
    """Xóa một bài thi đánh giá năng lực theo id."""
    item = _get_or_404(db, item_id)
    db.delete(item)
    db.commit()
