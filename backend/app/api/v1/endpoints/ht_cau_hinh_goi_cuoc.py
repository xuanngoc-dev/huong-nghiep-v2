from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user
from app.db.session import get_db
from app.models.ht_cau_hinh_goi_cuoc import HtCauHinhGoiCuoc
from app.schemas.ht_cau_hinh_goi_cuoc import (
    HtCauHinhGoiCuocDeleteMany,
    HtCauHinhGoiCuocDeleteManyResult,
    HtCauHinhGoiCuocPage,
    HtCauHinhGoiCuocPublic,
    HtCauHinhGoiCuocTrangThai,
    HtCauHinhGoiCuocWrite,
    LoaiApDung,
)

router = APIRouter(
    prefix="/he-thong/cau-hinh-goi-cuoc",
    tags=["he-thong"],
    dependencies=[Depends(get_admin_user)],
)

_TRUNG_MA = "Mã gói cước đã tồn tại"


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _get_or_400(db: Session, item_id: int) -> HtCauHinhGoiCuoc:
    """Lấy một bản ghi theo id. Trả lỗi 400 kèm thông báo nếu không tồn tại."""
    item = db.get(HtCauHinhGoiCuoc, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy gói cước có id = {item_id}",
        )
    return item


@router.get("", response_model=HtCauHinhGoiCuocPage)
def list_cau_hinh_goi_cuoc(
    q: str | None = Query(default=None, max_length=255),
    loai_ap_dung: LoaiApDung | None = Query(default=None),
    trang_thai: int | None = Query(default=None, ge=0, le=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> HtCauHinhGoiCuocPage:
    """Lấy danh sách gói cước có phân trang. Lọc theo từ khóa (mã, tên, ghi chú), loại áp dụng và trạng thái."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                HtCauHinhGoiCuoc.ma_goi_cuoc.like(pattern, escape="\\"),
                HtCauHinhGoiCuoc.ten_goi_cuoc.like(pattern, escape="\\"),
                HtCauHinhGoiCuoc.ghi_chu.like(pattern, escape="\\"),
            )
        )
    if loai_ap_dung:
        filters.append(HtCauHinhGoiCuoc.loai_ap_dung == loai_ap_dung)
    if trang_thai is not None:
        filters.append(HtCauHinhGoiCuoc.trang_thai == trang_thai)

    count_stmt = select(func.count()).select_from(HtCauHinhGoiCuoc)
    stmt = select(HtCauHinhGoiCuoc)
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    items = db.scalars(
        stmt.order_by(
            HtCauHinhGoiCuoc.loai_ap_dung.asc(),
            HtCauHinhGoiCuoc.gia_goc.asc(),
            HtCauHinhGoiCuoc.id.asc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return HtCauHinhGoiCuocPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{item_id}", response_model=HtCauHinhGoiCuocPublic)
def get_cau_hinh_goi_cuoc(item_id: int, db: Session = Depends(get_db)) -> HtCauHinhGoiCuoc:
    """Lấy chi tiết một gói cước theo id."""
    return _get_or_400(db, item_id)


@router.post("", response_model=HtCauHinhGoiCuocPublic, status_code=status.HTTP_201_CREATED)
def create_cau_hinh_goi_cuoc(
    payload: HtCauHinhGoiCuocWrite,
    db: Session = Depends(get_db),
) -> HtCauHinhGoiCuoc:
    """Thêm một gói cước. Từ chối nếu trùng mã gói cước."""
    item = HtCauHinhGoiCuoc(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_TRUNG_MA) from None
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=HtCauHinhGoiCuocPublic)
def update_cau_hinh_goi_cuoc(
    item_id: int,
    payload: HtCauHinhGoiCuocWrite,
    db: Session = Depends(get_db),
) -> HtCauHinhGoiCuoc:
    """Cập nhật toàn bộ thông tin một gói cước theo id."""
    item = _get_or_400(db, item_id)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_TRUNG_MA) from None
    db.refresh(item)
    return item


@router.patch("/{item_id}/trang-thai", response_model=HtCauHinhGoiCuocPublic)
def update_trang_thai_cau_hinh_goi_cuoc(
    item_id: int,
    payload: HtCauHinhGoiCuocTrangThai,
    db: Session = Depends(get_db),
) -> HtCauHinhGoiCuoc:
    """Bật/tắt nhanh trạng thái hoạt động của một gói cước."""
    item = _get_or_400(db, item_id)
    item.trang_thai = payload.trang_thai
    db.commit()
    db.refresh(item)
    return item


@router.delete("", response_model=HtCauHinhGoiCuocDeleteManyResult)
def delete_cau_hinh_goi_cuoc_many(
    payload: HtCauHinhGoiCuocDeleteMany,
    db: Session = Depends(get_db),
) -> HtCauHinhGoiCuocDeleteManyResult:
    """Xóa nhiều gói cước theo danh sách id."""
    items = db.scalars(select(HtCauHinhGoiCuoc).where(HtCauHinhGoiCuoc.id.in_(payload.ids))).all()
    if not items:
        return HtCauHinhGoiCuocDeleteManyResult(deleted=0)
    for item in items:
        db.delete(item)
    db.commit()
    return HtCauHinhGoiCuocDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cau_hinh_goi_cuoc(item_id: int, db: Session = Depends(get_db)) -> None:
    """Xóa một gói cước theo id."""
    item = _get_or_400(db, item_id)
    db.delete(item)
    db.commit()
