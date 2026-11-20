from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_current_user
from app.db.session import get_db
from app.models.dm_thpt_xkld import DmThptXkldNhomNghe
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_thpt_xkld import (
    DmThptXkldDeleteMany,
    DmThptXkldNhomNghePage,
    DmThptXkldNhomNghePublic,
    DmThptXkldNhomNgheTrangThai,
    DmThptXkldNhomNgheTrangThaiMany,
    DmThptXkldNhomNgheWrite,
    KetQuaDoiTrangThaiNhieu,
    KetQuaThemNhieu,
    KetQuaXoaNhieu,
)
from app.services.thpt_xkld import like_pattern as _like_pattern

router = APIRouter(prefix="/danh-muc/thpt-xkld/nhom-nghe", tags=["danh-muc"])


def _get_or_400(db: Session, item_id: int) -> DmThptXkldNhomNghe:
    """Lấy một nhóm nghề XKLĐ theo id. Trả lỗi 400 kèm thông báo nếu không tồn tại."""
    item = db.get(DmThptXkldNhomNghe, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy nhóm nghề XKLĐ có id = {item_id}",
        )
    return item


def _loi_trung_ma() -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mã nhóm nghề đã tồn tại")


@router.get("", response_model=DmThptXkldNhomNghePage)
def list_thpt_xkld_nhom_nghe(
    q: str | None = Query(default=None, max_length=255),
    trang_thai: int | None = Query(default=None, ge=0, le=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
) -> DmThptXkldNhomNghePage:
    """Lấy danh sách nhóm nghề XKLĐ có phân trang, không cần đăng nhập."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmThptXkldNhomNghe.ma_nhom.like(pattern, escape="\\"),
                DmThptXkldNhomNghe.ten_nhom.like(pattern, escape="\\"),
            )
        )
    if trang_thai is not None:
        filters.append(DmThptXkldNhomNghe.trang_thai == trang_thai)

    total = db.scalar(select(func.count()).select_from(DmThptXkldNhomNghe).where(*filters)) or 0
    items = db.scalars(
        select(DmThptXkldNhomNghe)
        .where(*filters)
        .order_by(DmThptXkldNhomNghe.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmThptXkldNhomNghePage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{item_id}", response_model=DmThptXkldNhomNghePublic)
def get_thpt_xkld_nhom_nghe(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmThptXkldNhomNghe:
    """Lấy chi tiết một nhóm nghề XKLĐ theo id."""
    return _get_or_400(db, item_id)


@router.post("/bulk", response_model=KetQuaThemNhieu, status_code=status.HTTP_201_CREATED)
def create_thpt_xkld_nhom_nghe_bulk(
    payload: list[DmThptXkldNhomNgheWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaThemNhieu:
    """Thêm nhiều nhóm nghề cùng lúc. Từ chối nếu mã trùng trong dữ liệu gửi lên hoặc đã có trong hệ thống."""
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách nhóm nghề trống")
    if len(payload) > 500:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chỉ thêm tối đa 500 nhóm nghề mỗi lần")

    codes = [item.ma_nhom for item in payload]
    duplicated = sorted({code for code in codes if codes.count(code) > 1})
    if duplicated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã nhóm nghề bị trùng trong dữ liệu: {', '.join(duplicated)}",
        )
    existing = list(
        db.scalars(select(DmThptXkldNhomNghe.ma_nhom).where(DmThptXkldNhomNghe.ma_nhom.in_(codes))).all()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã nhóm nghề đã tồn tại: {', '.join(existing)}",
        )

    items = [DmThptXkldNhomNghe(**item.model_dump()) for item in payload]
    db.add_all(items)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise _loi_trung_ma() from None
    return KetQuaThemNhieu(created=len(items))


@router.post("", response_model=DmThptXkldNhomNghePublic, status_code=status.HTTP_201_CREATED)
def create_thpt_xkld_nhom_nghe(
    payload: DmThptXkldNhomNgheWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThptXkldNhomNghe:
    """Thêm một nhóm nghề XKLĐ. Từ chối nếu mã đã tồn tại."""
    item = DmThptXkldNhomNghe(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise _loi_trung_ma() from None
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=DmThptXkldNhomNghePublic)
def update_thpt_xkld_nhom_nghe(
    item_id: int,
    payload: DmThptXkldNhomNgheWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThptXkldNhomNghe:
    """Cập nhật toàn bộ thông tin một nhóm nghề XKLĐ theo id."""
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


@router.patch("/trang-thai", response_model=KetQuaDoiTrangThaiNhieu)
def update_trang_thai_thpt_xkld_nhom_nghe_many(
    payload: DmThptXkldNhomNgheTrangThaiMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaDoiTrangThaiNhieu:
    """Bật/tắt nhiều nhóm nghề cùng lúc. Id không tồn tại thì bỏ qua."""
    items = db.scalars(select(DmThptXkldNhomNghe).where(DmThptXkldNhomNghe.id.in_(payload.ids))).all()
    for item in items:
        item.trang_thai = payload.trang_thai
    db.commit()
    return KetQuaDoiTrangThaiNhieu(updated=len(items))


@router.patch("/{item_id}/trang-thai", response_model=DmThptXkldNhomNghePublic)
def update_trang_thai_thpt_xkld_nhom_nghe(
    item_id: int,
    payload: DmThptXkldNhomNgheTrangThai,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThptXkldNhomNghe:
    """Bật/tắt nhanh một nhóm nghề, giữ nguyên các thông tin khác."""
    item = _get_or_400(db, item_id)
    item.trang_thai = payload.trang_thai
    db.commit()
    db.refresh(item)
    return item


@router.delete("", response_model=KetQuaXoaNhieu)
def delete_thpt_xkld_nhom_nghe_many(
    payload: DmThptXkldDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaXoaNhieu:
    """Xóa nhiều nhóm nghề theo danh sách id; thị trường, nghề cụ thể, chi phí, thủ tục, kênh kết nối bị xóa theo."""
    items = db.scalars(select(DmThptXkldNhomNghe).where(DmThptXkldNhomNghe.id.in_(payload.ids))).all()
    for item in items:
        db.delete(item)
    db.commit()
    return KetQuaXoaNhieu(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_thpt_xkld_nhom_nghe(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> None:
    """Xóa một nhóm nghề theo id; thị trường, nghề cụ thể, chi phí, thủ tục, kênh kết nối bị xóa theo (CASCADE)."""
    db.delete(_get_or_400(db, item_id))
    db.commit()
