from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_current_user
from app.db.session import get_db
from app.models.dm_thcs_huong_di import DmThcsHuongDi, DmThcsLoiKhuyenLuuY
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_thcs_huong_di import (
    DmThcsDeleteMany,
    DmThcsLoiKhuyenLuuYPage,
    DmThcsLoiKhuyenLuuYPublic,
    DmThcsLoiKhuyenLuuYWrite,
    DoiTuongNhanLuuY,
    KetQuaThemNhieu,
    KetQuaXoaNhieu,
)
from app.services.thcs_huong_di import danh_sach_con, kiem_tra_huong_di, thong_tin_huong_di
from app.services.thcs_huong_di import like_pattern as _like_pattern

router = APIRouter(prefix="/danh-muc/thcs/loi-khuyen-luu-y", tags=["danh-muc"])


def _get_or_400(db: Session, item_id: int) -> DmThcsLoiKhuyenLuuY:
    """Lấy một lời khuyên, lưu ý theo id. Trả lỗi 400 kèm thông báo nếu không tồn tại."""
    item = db.get(DmThcsLoiKhuyenLuuY, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy lời khuyên, lưu ý có id = {item_id}",
        )
    return item


def _to_public(item: DmThcsLoiKhuyenLuuY, huong: DmThcsHuongDi | None) -> DmThcsLoiKhuyenLuuYPublic:
    return DmThcsLoiKhuyenLuuYPublic(
        id=item.id,
        thcs_huong_di_id=item.thcs_huong_di_id,
        **thong_tin_huong_di(huong),
        doi_tuong_nhan=item.doi_tuong_nhan,
        noi_dung_luu_y=item.noi_dung_luu_y,
        thu_tu_hien_thi=item.thu_tu_hien_thi,
    )


@router.get("", response_model=DmThcsLoiKhuyenLuuYPage)
def list_thcs_loi_khuyen_luu_y(
    q: str | None = Query(default=None, max_length=255),
    thcs_huong_di_id: int | None = Query(default=None, ge=1),
    doi_tuong_nhan: DoiTuongNhanLuuY | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
) -> DmThcsLoiKhuyenLuuYPage:
    """Lấy danh sách lời khuyên, lưu ý có phân trang, lọc theo từ khóa, hướng đi, đối tượng. Không cần đăng nhập."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmThcsLoiKhuyenLuuY.noi_dung_luu_y.like(pattern, escape="\\"),
                DmThcsHuongDi.ten_huong.like(pattern, escape="\\"),
            )
        )
    if thcs_huong_di_id is not None:
        filters.append(DmThcsLoiKhuyenLuuY.thcs_huong_di_id == thcs_huong_di_id)
    if doi_tuong_nhan is not None:
        filters.append(DmThcsLoiKhuyenLuuY.doi_tuong_nhan == doi_tuong_nhan)

    rows, total = danh_sach_con(
        db,
        DmThcsLoiKhuyenLuuY,
        filters,
        [
            DmThcsLoiKhuyenLuuY.thcs_huong_di_id.asc(),
            DmThcsLoiKhuyenLuuY.thu_tu_hien_thi.asc(),
            DmThcsLoiKhuyenLuuY.id.asc(),
        ],
        page,
        page_size,
    )
    return DmThcsLoiKhuyenLuuYPage(
        items=[_to_public(item, huong) for item, huong in rows], total=total, page=page, page_size=page_size
    )


@router.get("/{item_id}", response_model=DmThcsLoiKhuyenLuuYPublic)
def get_thcs_loi_khuyen_luu_y(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmThcsLoiKhuyenLuuYPublic:
    """Lấy chi tiết một lời khuyên, lưu ý theo id."""
    item = _get_or_400(db, item_id)
    return _to_public(item, db.get(DmThcsHuongDi, item.thcs_huong_di_id))


@router.post("/bulk", response_model=KetQuaThemNhieu, status_code=status.HTTP_201_CREATED)
def create_thcs_loi_khuyen_luu_y_bulk(
    payload: list[DmThcsLoiKhuyenLuuYWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaThemNhieu:
    """Thêm nhiều lời khuyên, lưu ý cùng lúc. Từ chối nếu có hướng đi không tồn tại."""
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách lời khuyên, lưu ý trống")
    if len(payload) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Chỉ thêm tối đa 500 lời khuyên, lưu ý mỗi lần"
        )
    kiem_tra_huong_di(db, [item.thcs_huong_di_id for item in payload])
    items = [DmThcsLoiKhuyenLuuY(**item.model_dump()) for item in payload]
    db.add_all(items)
    db.commit()
    return KetQuaThemNhieu(created=len(items))


@router.post("", response_model=DmThcsLoiKhuyenLuuYPublic, status_code=status.HTTP_201_CREATED)
def create_thcs_loi_khuyen_luu_y(
    payload: DmThcsLoiKhuyenLuuYWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThcsLoiKhuyenLuuYPublic:
    """Thêm một lời khuyên, lưu ý cho hướng đi."""
    huong = kiem_tra_huong_di(db, [payload.thcs_huong_di_id])[payload.thcs_huong_di_id]
    item = DmThcsLoiKhuyenLuuY(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return _to_public(item, huong)


@router.put("/{item_id}", response_model=DmThcsLoiKhuyenLuuYPublic)
def update_thcs_loi_khuyen_luu_y(
    item_id: int,
    payload: DmThcsLoiKhuyenLuuYWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThcsLoiKhuyenLuuYPublic:
    """Cập nhật toàn bộ thông tin một lời khuyên, lưu ý."""
    item = _get_or_400(db, item_id)
    huong = kiem_tra_huong_di(db, [payload.thcs_huong_di_id])[payload.thcs_huong_di_id]
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return _to_public(item, huong)


@router.delete("", response_model=KetQuaXoaNhieu)
def delete_thcs_loi_khuyen_luu_y_many(
    payload: DmThcsDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaXoaNhieu:
    """Xóa nhiều lời khuyên, lưu ý theo danh sách id. Id không tồn tại thì bỏ qua."""
    items = db.scalars(select(DmThcsLoiKhuyenLuuY).where(DmThcsLoiKhuyenLuuY.id.in_(payload.ids))).all()
    for item in items:
        db.delete(item)
    db.commit()
    return KetQuaXoaNhieu(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_thcs_loi_khuyen_luu_y(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> None:
    """Xóa một lời khuyên, lưu ý theo id."""
    db.delete(_get_or_400(db, item_id))
    db.commit()
