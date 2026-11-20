from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_current_user
from app.db.session import get_db
from app.models.dm_thcs_huong_di import DmThcsTieuChi
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_thcs_huong_di import (
    DmThcsDeleteMany,
    DmThcsTieuChiPage,
    DmThcsTieuChiPublic,
    DmThcsTieuChiWrite,
    KetQuaThemNhieu,
    KetQuaXoaNhieu,
)
from app.services.thcs_huong_di import like_pattern as _like_pattern

router = APIRouter(prefix="/danh-muc/thcs/tieu-chi", tags=["danh-muc"])


def _get_or_400(db: Session, item_id: int) -> DmThcsTieuChi:
    """Lấy một tiêu chí THCS theo id. Trả lỗi 400 kèm thông báo nếu không tồn tại."""
    item = db.get(DmThcsTieuChi, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy tiêu chí THCS có id = {item_id}",
        )
    return item


def _loi_trung_ma() -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mã tiêu chí đã tồn tại")


@router.get("", response_model=DmThcsTieuChiPage)
def list_thcs_tieu_chi(
    q: str | None = Query(default=None, max_length=255),
    nhom_tieu_chi: str | None = Query(default=None, max_length=100),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
) -> DmThcsTieuChiPage:
    """Lấy danh sách tiêu chí THCS có phân trang, lọc theo từ khóa và nhóm tiêu chí. Không cần đăng nhập."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmThcsTieuChi.ma_tieu_chi.like(pattern, escape="\\"),
                DmThcsTieuChi.ten_tieu_chi.like(pattern, escape="\\"),
                DmThcsTieuChi.mo_ta_tieu_chi.like(pattern, escape="\\"),
            )
        )
    if nhom_tieu_chi and nhom_tieu_chi.strip():
        filters.append(DmThcsTieuChi.nhom_tieu_chi == nhom_tieu_chi.strip())

    total = db.scalar(select(func.count()).select_from(DmThcsTieuChi).where(*filters)) or 0
    items = db.scalars(
        select(DmThcsTieuChi)
        .where(*filters)
        .order_by(DmThcsTieuChi.thu_tu_hien_thi.asc(), DmThcsTieuChi.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmThcsTieuChiPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/nhom", response_model=list[str])
def list_thcs_nhom_tieu_chi(db: Session = Depends(get_db)) -> list[str]:
    """Các nhóm tiêu chí đang dùng (để gợi ý khi nhập và lọc). Không cần đăng nhập."""
    return list(
        db.scalars(
            select(DmThcsTieuChi.nhom_tieu_chi)
            .where(DmThcsTieuChi.nhom_tieu_chi.is_not(None))
            .distinct()
            .order_by(DmThcsTieuChi.nhom_tieu_chi.asc())
        ).all()
    )


@router.get("/{item_id}", response_model=DmThcsTieuChiPublic)
def get_thcs_tieu_chi(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmThcsTieuChi:
    """Lấy chi tiết một tiêu chí THCS theo id."""
    return _get_or_400(db, item_id)


@router.post("/bulk", response_model=KetQuaThemNhieu, status_code=status.HTTP_201_CREATED)
def create_thcs_tieu_chi_bulk(
    payload: list[DmThcsTieuChiWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaThemNhieu:
    """Thêm nhiều tiêu chí cùng lúc. Từ chối nếu mã trùng trong dữ liệu gửi lên hoặc đã có trong hệ thống."""
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
    existing = list(db.scalars(select(DmThcsTieuChi.ma_tieu_chi).where(DmThcsTieuChi.ma_tieu_chi.in_(codes))).all())
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã tiêu chí đã tồn tại: {', '.join(existing)}",
        )

    items = [DmThcsTieuChi(**item.model_dump()) for item in payload]
    db.add_all(items)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise _loi_trung_ma() from None
    return KetQuaThemNhieu(created=len(items))


@router.post("", response_model=DmThcsTieuChiPublic, status_code=status.HTTP_201_CREATED)
def create_thcs_tieu_chi(
    payload: DmThcsTieuChiWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThcsTieuChi:
    """Thêm một tiêu chí THCS. Từ chối nếu mã đã tồn tại."""
    item = DmThcsTieuChi(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise _loi_trung_ma() from None
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=DmThcsTieuChiPublic)
def update_thcs_tieu_chi(
    item_id: int,
    payload: DmThcsTieuChiWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThcsTieuChi:
    """Cập nhật toàn bộ thông tin một tiêu chí THCS theo id."""
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
def delete_thcs_tieu_chi_many(
    payload: DmThcsDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaXoaNhieu:
    """Xóa nhiều tiêu chí theo danh sách id; điểm phù hợp của các hướng đi với tiêu chí bị xóa theo."""
    items = db.scalars(select(DmThcsTieuChi).where(DmThcsTieuChi.id.in_(payload.ids))).all()
    for item in items:
        db.delete(item)
    db.commit()
    return KetQuaXoaNhieu(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_thcs_tieu_chi(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> None:
    """Xóa một tiêu chí theo id; điểm phù hợp của các hướng đi với tiêu chí bị xóa theo (CASCADE)."""
    db.delete(_get_or_400(db, item_id))
    db.commit()
