from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_current_user
from app.db.session import get_db
from app.models.dm_nhom_nghe_di_lam import DmTieuChiGoiY
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_nhom_nghe_di_lam import (
    DmTieuChiGoiYDeleteMany,
    DmTieuChiGoiYPage,
    DmTieuChiGoiYPublic,
    DmTieuChiGoiYWrite,
    KetQuaThemNhieu,
    KetQuaXoaNhieu,
)

router = APIRouter(prefix="/danh-muc/tieu-chi-goi-y", tags=["danh-muc"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _get_or_400(db: Session, item_id: int) -> DmTieuChiGoiY:
    """Lấy một tiêu chí gợi ý theo id. Trả lỗi 400 kèm thông báo nếu không tồn tại."""
    item = db.get(DmTieuChiGoiY, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy tiêu chí gợi ý có id = {item_id}",
        )
    return item


def _loi_trung_ma() -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mã tiêu chí đã tồn tại")


@router.get("", response_model=DmTieuChiGoiYPage)
def list_tieu_chi_goi_y(
    q: str | None = Query(default=None, max_length=255),
    nhom_tieu_chi: str | None = Query(default=None, max_length=100),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
) -> DmTieuChiGoiYPage:
    """Lấy danh sách tiêu chí gợi ý có phân trang, lọc theo từ khóa và nhóm tiêu chí. Không cần đăng nhập."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmTieuChiGoiY.ma_tieu_chi.like(pattern, escape="\\"),
                DmTieuChiGoiY.ten_tieu_chi.like(pattern, escape="\\"),
            )
        )
    if nhom_tieu_chi and nhom_tieu_chi.strip():
        filters.append(DmTieuChiGoiY.nhom_tieu_chi == nhom_tieu_chi.strip())

    total = db.scalar(select(func.count()).select_from(DmTieuChiGoiY).where(*filters)) or 0
    items = db.scalars(
        select(DmTieuChiGoiY)
        .where(*filters)
        .order_by(DmTieuChiGoiY.nhom_tieu_chi.asc(), DmTieuChiGoiY.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmTieuChiGoiYPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/nhom", response_model=list[str])
def list_nhom_tieu_chi(db: Session = Depends(get_db)) -> list[str]:
    """Danh sách các nhóm tiêu chí đang dùng (để chọn khi lọc/nhập). Không cần đăng nhập."""
    return list(
        db.scalars(
            select(DmTieuChiGoiY.nhom_tieu_chi)
            .where(DmTieuChiGoiY.nhom_tieu_chi.is_not(None))
            .distinct()
            .order_by(DmTieuChiGoiY.nhom_tieu_chi.asc())
        ).all()
    )


@router.get("/{item_id}", response_model=DmTieuChiGoiYPublic)
def get_tieu_chi_goi_y(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmTieuChiGoiY:
    """Lấy chi tiết một tiêu chí gợi ý theo id."""
    return _get_or_400(db, item_id)


@router.post("/bulk", response_model=KetQuaThemNhieu, status_code=status.HTTP_201_CREATED)
def create_tieu_chi_goi_y_bulk(
    payload: list[DmTieuChiGoiYWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaThemNhieu:
    """Thêm nhiều tiêu chí cùng lúc. Từ chối nếu mã tiêu chí trùng trong dữ liệu gửi lên hoặc đã có trong hệ thống."""
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách tiêu chí trống")
    if len(payload) > 500:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chỉ thêm tối đa 500 tiêu chí mỗi lần")

    codes = [item.ma_tieu_chi for item in payload]
    duplicated = sorted({code for code in codes if codes.count(code) > 1})
    if duplicated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã tiêu chí bị trùng trong dữ liệu: {', '.join(duplicated)}",
        )
    existing = list(db.scalars(select(DmTieuChiGoiY.ma_tieu_chi).where(DmTieuChiGoiY.ma_tieu_chi.in_(codes))).all())
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã tiêu chí đã tồn tại: {', '.join(existing)}",
        )

    items = [DmTieuChiGoiY(**item.model_dump()) for item in payload]
    db.add_all(items)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise _loi_trung_ma() from None
    return KetQuaThemNhieu(created=len(items))


@router.post("", response_model=DmTieuChiGoiYPublic, status_code=status.HTTP_201_CREATED)
def create_tieu_chi_goi_y(
    payload: DmTieuChiGoiYWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmTieuChiGoiY:
    """Thêm một tiêu chí gợi ý. Từ chối nếu mã tiêu chí đã tồn tại."""
    item = DmTieuChiGoiY(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise _loi_trung_ma() from None
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=DmTieuChiGoiYPublic)
def update_tieu_chi_goi_y(
    item_id: int,
    payload: DmTieuChiGoiYWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmTieuChiGoiY:
    """Cập nhật toàn bộ thông tin một tiêu chí gợi ý theo id."""
    item = _get_or_400(db, item_id)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise _loi_trung_ma() from None
    db.refresh(item)
    return item


@router.delete("", response_model=KetQuaXoaNhieu)
def delete_tieu_chi_goi_y_many(
    payload: DmTieuChiGoiYDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaXoaNhieu:
    """Xóa nhiều tiêu chí theo danh sách id; liên kết với nhóm nghề bị xóa theo (CASCADE)."""
    items = db.scalars(select(DmTieuChiGoiY).where(DmTieuChiGoiY.id.in_(payload.ids))).all()
    for item in items:
        db.delete(item)
    db.commit()
    return KetQuaXoaNhieu(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tieu_chi_goi_y(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> None:
    """Xóa một tiêu chí theo id; liên kết với nhóm nghề bị xóa theo (CASCADE)."""
    db.delete(_get_or_400(db, item_id))
    db.commit()
