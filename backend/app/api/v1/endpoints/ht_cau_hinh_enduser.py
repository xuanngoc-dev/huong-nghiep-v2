from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user
from app.db.session import get_db
from app.models.ht_cau_hinh_enduser import HtCauHinhEnduser
from app.schemas.ht_cau_hinh_enduser import (
    HtCauHinhEnduserApDung,
    HtCauHinhEnduserDeleteMany,
    HtCauHinhEnduserDeleteManyResult,
    HtCauHinhEnduserPage,
    HtCauHinhEnduserPublic,
    HtCauHinhEnduserTrangThai,
    HtCauHinhEnduserWrite,
    KieuTraLoi,
)

router = APIRouter(
    prefix="/he-thong/cau-hinh-enduser",
    tags=["he-thong"],
    dependencies=[Depends(get_admin_user)],
)

# Trang làm trắc nghiệm (kể cả khách chưa đăng nhập) đọc cấu hình đang áp dụng.
# Phải include trước `router` để không bị `/{item_id}` bắt mất.
public_router = APIRouter(prefix="/he-thong/cau-hinh-enduser", tags=["he-thong"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _get_or_404(db: Session, item_id: int) -> HtCauHinhEnduser:
    """Lấy một bản ghi theo id. Trả lỗi 404 nếu không tồn tại."""
    item = db.get(HtCauHinhEnduser, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy cấu hình EndUser")
    return item


_PHAI_CON_MOT = "Phải còn ít nhất 1 cấu hình EndUser, không thể xóa hết"
_PHAI_CON_HOAT_DONG = "Phải còn ít nhất 1 cấu hình EndUser đang hoạt động"


def _dem_con_lai(db: Session, bo_ids: list[int], chi_hoat_dong: bool = False) -> int:
    """Đếm số cấu hình còn lại nếu bỏ đi các id cho trước (tuỳ chọn chỉ đếm bản ghi đang hoạt động)."""
    stmt = select(func.count()).select_from(HtCauHinhEnduser).where(HtCauHinhEnduser.id.not_in(bo_ids))
    if chi_hoat_dong:
        stmt = stmt.where(HtCauHinhEnduser.trang_thai == 1)
    return db.scalar(stmt) or 0


def _dam_bao_con_lai(db: Session, bo_ids: list[int]) -> None:
    """Chặn thao tác nếu sau khi bỏ các id này không còn bản ghi nào, hoặc không còn bản ghi hoạt động."""
    if _dem_con_lai(db, bo_ids) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_PHAI_CON_MOT)
    if _dem_con_lai(db, bo_ids, chi_hoat_dong=True) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_PHAI_CON_HOAT_DONG)


def _dam_bao_con_hoat_dong(db: Session, item: HtCauHinhEnduser, trang_thai_moi: int) -> None:
    """Chặn tắt bản ghi đang hoạt động cuối cùng."""
    if item.trang_thai == 1 and trang_thai_moi != 1 and _dem_con_lai(db, [item.id], chi_hoat_dong=True) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_PHAI_CON_HOAT_DONG)


@router.get("", response_model=HtCauHinhEnduserPage)
def list_cau_hinh_enduser(
    q: str | None = Query(default=None, max_length=255),
    kieu_tra_loi: KieuTraLoi | None = Query(default=None),
    trang_thai: int | None = Query(default=None, ge=0, le=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> HtCauHinhEnduserPage:
    """Lấy danh sách cấu hình EndUser có phân trang. Lọc theo từ khóa (tên, mô tả), kiểu trả lời và trạng thái."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                HtCauHinhEnduser.ten_cau_hinh.like(pattern, escape="\\"),
                HtCauHinhEnduser.mo_ta.like(pattern, escape="\\"),
            )
        )
    if kieu_tra_loi is not None:
        filters.append(HtCauHinhEnduser.kieu_tra_loi == kieu_tra_loi)
    if trang_thai is not None:
        filters.append(HtCauHinhEnduser.trang_thai == trang_thai)

    count_stmt = select(func.count()).select_from(HtCauHinhEnduser)
    stmt = select(HtCauHinhEnduser)
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    items = db.scalars(
        stmt.order_by(HtCauHinhEnduser.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return HtCauHinhEnduserPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{item_id}", response_model=HtCauHinhEnduserPublic)
def get_cau_hinh_enduser(item_id: int, db: Session = Depends(get_db)) -> HtCauHinhEnduser:
    """Lấy chi tiết một cấu hình EndUser theo id."""
    return _get_or_404(db, item_id)


@router.post("", response_model=HtCauHinhEnduserPublic, status_code=status.HTTP_201_CREATED)
def create_cau_hinh_enduser(
    payload: HtCauHinhEnduserWrite,
    db: Session = Depends(get_db),
) -> HtCauHinhEnduser:
    """Thêm một cấu hình EndUser."""
    item = HtCauHinhEnduser(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=HtCauHinhEnduserPublic)
def update_cau_hinh_enduser(
    item_id: int,
    payload: HtCauHinhEnduserWrite,
    db: Session = Depends(get_db),
) -> HtCauHinhEnduser:
    """Cập nhật thông tin một cấu hình EndUser theo id. Trường không gửi lên (vd. noi_dung_cau_hinh) được giữ nguyên."""
    item = _get_or_404(db, item_id)
    _dam_bao_con_hoat_dong(db, item, payload.trang_thai)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{item_id}/trang-thai", response_model=HtCauHinhEnduserPublic)
def update_trang_thai_cau_hinh_enduser(
    item_id: int,
    payload: HtCauHinhEnduserTrangThai,
    db: Session = Depends(get_db),
) -> HtCauHinhEnduser:
    """Bật/tắt nhanh trạng thái của một cấu hình EndUser."""
    item = _get_or_404(db, item_id)
    _dam_bao_con_hoat_dong(db, item, payload.trang_thai)
    item.trang_thai = payload.trang_thai
    db.commit()
    db.refresh(item)
    return item


@router.delete("", response_model=HtCauHinhEnduserDeleteManyResult)
def delete_cau_hinh_enduser_many(
    payload: HtCauHinhEnduserDeleteMany,
    db: Session = Depends(get_db),
) -> HtCauHinhEnduserDeleteManyResult:
    """Xóa nhiều cấu hình EndUser theo danh sách id."""
    items = db.scalars(select(HtCauHinhEnduser).where(HtCauHinhEnduser.id.in_(payload.ids))).all()
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy cấu hình EndUser để xóa")
    _dam_bao_con_lai(db, [item.id for item in items])
    for item in items:
        db.delete(item)
    db.commit()
    return HtCauHinhEnduserDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cau_hinh_enduser(item_id: int, db: Session = Depends(get_db)) -> None:
    """Xóa một cấu hình EndUser theo id."""
    item = _get_or_404(db, item_id)
    _dam_bao_con_lai(db, [item.id])
    db.delete(item)
    db.commit()


@public_router.get("/dang-ap-dung", response_model=HtCauHinhEnduserApDung)
def get_cau_hinh_enduser_dang_ap_dung(db: Session = Depends(get_db)) -> HtCauHinhEnduser:
    """Cấu hình EndUser đang áp dụng: bản ghi hoạt động được cập nhật gần nhất. Không cần đăng nhập."""
    item = db.scalars(
        select(HtCauHinhEnduser)
        .where(HtCauHinhEnduser.trang_thai == 1)
        .order_by(HtCauHinhEnduser.updated_at.desc(), HtCauHinhEnduser.id.desc())
        .limit(1)
    ).first()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chưa có cấu hình EndUser đang hoạt động")
    return item
