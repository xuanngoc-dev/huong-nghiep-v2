from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user
from app.db.session import get_db
from app.models.ht_cau_hinh_tra_cuu import HtCauHinhTraCuu
from app.schemas.ht_cau_hinh_tra_cuu import (
    HtCauHinhTraCuuDeleteMany,
    HtCauHinhTraCuuDeleteManyResult,
    HtCauHinhTraCuuPage,
    HtCauHinhTraCuuPublic,
    HtCauHinhTraCuuTrangThai,
    HtCauHinhTraCuuWrite,
)

router = APIRouter(
    prefix="/he-thong/cau-hinh-tra-cuu",
    tags=["he-thong"],
    dependencies=[Depends(get_admin_user)],
)


def _get_or_404(db: Session, item_id: int) -> HtCauHinhTraCuu:
    """Lấy một cấu hình theo id. Trả lỗi 404 nếu không tồn tại."""
    item = db.get(HtCauHinhTraCuu, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy cấu hình tra cứu")
    return item


_PHAI_CO_AP_DUNG = "Hệ thống phải luôn có một cấu hình đang áp dụng. Hãy bật cấu hình khác trước"


def _con_ap_dung_ngoai(db: Session, ids: set[int]) -> bool:
    """Còn cấu hình đang áp dụng nào ngoài các id đang bị tắt/xóa hay không."""
    stmt = select(func.count()).select_from(HtCauHinhTraCuu).where(HtCauHinhTraCuu.trang_thai == 1)
    if ids:
        stmt = stmt.where(HtCauHinhTraCuu.id.not_in(ids))
    return (db.scalar(stmt) or 0) > 0


def _khong_duoc_ngung(db: Session, item: HtCauHinhTraCuu, trang_thai_moi: int) -> None:
    """Chặn tắt cấu hình đang áp dụng cuối cùng."""
    if item.trang_thai == 1 and trang_thai_moi != 1 and not _con_ap_dung_ngoai(db, {item.id}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_PHAI_CO_AP_DUNG)


def _chi_ap_dung(db: Session, item: HtCauHinhTraCuu) -> None:
    """Hệ thống chỉ dùng một cấu hình: bật cấu hình này thì tắt các cấu hình còn lại."""
    if item.trang_thai != 1:
        return
    db.execute(
        update(HtCauHinhTraCuu)
        .where(HtCauHinhTraCuu.id != item.id, HtCauHinhTraCuu.trang_thai == 1)
        .values(trang_thai=0)
    )


@router.get("", response_model=HtCauHinhTraCuuPage)
def list_cau_hinh_tra_cuu(
    trang_thai: int | None = Query(default=None, ge=0, le=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> HtCauHinhTraCuuPage:
    """Lấy danh sách cấu hình tra cứu, cấu hình đang áp dụng đứng đầu."""
    filters = []
    if trang_thai is not None:
        filters.append(HtCauHinhTraCuu.trang_thai == trang_thai)

    count_stmt = select(func.count()).select_from(HtCauHinhTraCuu)
    stmt = select(HtCauHinhTraCuu)
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    items = db.scalars(
        stmt.order_by(HtCauHinhTraCuu.trang_thai.desc(), HtCauHinhTraCuu.updated_at.desc(), HtCauHinhTraCuu.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return HtCauHinhTraCuuPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{item_id}", response_model=HtCauHinhTraCuuPublic)
def get_cau_hinh_tra_cuu(item_id: int, db: Session = Depends(get_db)) -> HtCauHinhTraCuu:
    """Lấy chi tiết một cấu hình tra cứu theo id."""
    return _get_or_404(db, item_id)


@router.post("", response_model=HtCauHinhTraCuuPublic, status_code=status.HTTP_201_CREATED)
def create_cau_hinh_tra_cuu(
    payload: HtCauHinhTraCuuWrite,
    db: Session = Depends(get_db),
) -> HtCauHinhTraCuu:
    """Thêm một cấu hình tra cứu. Nếu đặt đang áp dụng thì các cấu hình khác chuyển sang ngừng.

    Chưa có cấu hình nào đang áp dụng thì cấu hình mới được áp dụng luôn.
    """
    item = HtCauHinhTraCuu(**payload.model_dump())
    if not _con_ap_dung_ngoai(db, set()):
        item.trang_thai = 1
    db.add(item)
    db.flush()
    _chi_ap_dung(db, item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=HtCauHinhTraCuuPublic)
def update_cau_hinh_tra_cuu(
    item_id: int,
    payload: HtCauHinhTraCuuWrite,
    db: Session = Depends(get_db),
) -> HtCauHinhTraCuu:
    """Cập nhật toàn bộ một cấu hình tra cứu theo id."""
    item = _get_or_404(db, item_id)
    _khong_duoc_ngung(db, item, payload.trang_thai)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    _chi_ap_dung(db, item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{item_id}/trang-thai", response_model=HtCauHinhTraCuuPublic)
def update_trang_thai_cau_hinh_tra_cuu(
    item_id: int,
    payload: HtCauHinhTraCuuTrangThai,
    db: Session = Depends(get_db),
) -> HtCauHinhTraCuu:
    """Bật/tắt nhanh một cấu hình. Bật cấu hình này thì các cấu hình khác tự tắt."""
    item = _get_or_404(db, item_id)
    _khong_duoc_ngung(db, item, payload.trang_thai)
    item.trang_thai = payload.trang_thai
    _chi_ap_dung(db, item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("", response_model=HtCauHinhTraCuuDeleteManyResult)
def delete_cau_hinh_tra_cuu_many(
    payload: HtCauHinhTraCuuDeleteMany,
    db: Session = Depends(get_db),
) -> HtCauHinhTraCuuDeleteManyResult:
    """Xóa nhiều cấu hình tra cứu theo danh sách id."""
    items = db.scalars(select(HtCauHinhTraCuu).where(HtCauHinhTraCuu.id.in_(payload.ids))).all()
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy cấu hình tra cứu để xóa")
    ids = {item.id for item in items}
    if any(item.trang_thai == 1 for item in items) and not _con_ap_dung_ngoai(db, ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không thể xóa cấu hình đang áp dụng")
    for item in items:
        db.delete(item)
    db.commit()
    return HtCauHinhTraCuuDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cau_hinh_tra_cuu(item_id: int, db: Session = Depends(get_db)) -> None:
    """Xóa một cấu hình tra cứu theo id. Không cho xóa cấu hình đang áp dụng cuối cùng."""
    item = _get_or_404(db, item_id)
    if item.trang_thai == 1 and not _con_ap_dung_ngoai(db, {item.id}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không thể xóa cấu hình đang áp dụng")
    db.delete(item)
    db.commit()
