from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import case, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_current_user
from app.db.session import get_db
from app.models.dm_thcs_huong_di import DmThcsHuongDi, DmThcsUuNhuocDiem
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_thcs_huong_di import (
    DmThcsDeleteMany,
    DmThcsUuNhuocDiemPage,
    DmThcsUuNhuocDiemPublic,
    DmThcsUuNhuocDiemWrite,
    KetQuaThemNhieu,
    KetQuaXoaNhieu,
    LoaiUuNhuocDiem,
)
from app.services.thcs_huong_di import danh_sach_con, kiem_tra_huong_di, thong_tin_huong_di
from app.services.thcs_huong_di import like_pattern as _like_pattern

router = APIRouter(prefix="/danh-muc/thcs/uu-nhuoc-diem", tags=["danh-muc"])


def _get_or_400(db: Session, item_id: int) -> DmThcsUuNhuocDiem:
    """Lấy một ưu/nhược điểm theo id. Trả lỗi 400 kèm thông báo nếu không tồn tại."""
    item = db.get(DmThcsUuNhuocDiem, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy ưu/nhược điểm có id = {item_id}",
        )
    return item


def _to_public(item: DmThcsUuNhuocDiem, huong: DmThcsHuongDi | None) -> DmThcsUuNhuocDiemPublic:
    return DmThcsUuNhuocDiemPublic(
        id=item.id,
        thcs_huong_di_id=item.thcs_huong_di_id,
        **thong_tin_huong_di(huong),
        loai=item.loai,
        tieu_de=item.tieu_de,
        noi_dung_chi_tiet=item.noi_dung_chi_tiet,
        thu_tu_hien_thi=item.thu_tu_hien_thi,
    )


@router.get("", response_model=DmThcsUuNhuocDiemPage)
def list_thcs_uu_nhuoc_diem(
    q: str | None = Query(default=None, max_length=255),
    thcs_huong_di_id: int | None = Query(default=None, ge=1),
    loai: LoaiUuNhuocDiem | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
) -> DmThcsUuNhuocDiemPage:
    """Lấy danh sách ưu/nhược điểm có phân trang, lọc theo từ khóa, hướng đi, loại. Không cần đăng nhập."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmThcsUuNhuocDiem.tieu_de.like(pattern, escape="\\"),
                DmThcsUuNhuocDiem.noi_dung_chi_tiet.like(pattern, escape="\\"),
                DmThcsHuongDi.ten_huong.like(pattern, escape="\\"),
            )
        )
    if thcs_huong_di_id is not None:
        filters.append(DmThcsUuNhuocDiem.thcs_huong_di_id == thcs_huong_di_id)
    if loai is not None:
        filters.append(DmThcsUuNhuocDiem.loai == loai)

    rows, total = danh_sach_con(
        db,
        DmThcsUuNhuocDiem,
        filters,
        [
            DmThcsUuNhuocDiem.thcs_huong_di_id.asc(),
            # Ưu điểm trước nhược điểm (không dựa vào thứ tự ENUM của từng CSDL).
            case((DmThcsUuNhuocDiem.loai == "uu_diem", 0), else_=1),
            DmThcsUuNhuocDiem.thu_tu_hien_thi.asc(),
            DmThcsUuNhuocDiem.id.asc(),
        ],
        page,
        page_size,
    )
    return DmThcsUuNhuocDiemPage(
        items=[_to_public(item, huong) for item, huong in rows], total=total, page=page, page_size=page_size
    )


@router.get("/{item_id}", response_model=DmThcsUuNhuocDiemPublic)
def get_thcs_uu_nhuoc_diem(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmThcsUuNhuocDiemPublic:
    """Lấy chi tiết một ưu/nhược điểm theo id."""
    item = _get_or_400(db, item_id)
    return _to_public(item, db.get(DmThcsHuongDi, item.thcs_huong_di_id))


@router.post("/bulk", response_model=KetQuaThemNhieu, status_code=status.HTTP_201_CREATED)
def create_thcs_uu_nhuoc_diem_bulk(
    payload: list[DmThcsUuNhuocDiemWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaThemNhieu:
    """Thêm nhiều ưu/nhược điểm cùng lúc. Từ chối nếu có hướng đi không tồn tại."""
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách ưu/nhược điểm trống")
    if len(payload) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Chỉ thêm tối đa 500 ưu/nhược điểm mỗi lần"
        )
    kiem_tra_huong_di(db, [item.thcs_huong_di_id for item in payload])
    items = [DmThcsUuNhuocDiem(**item.model_dump()) for item in payload]
    db.add_all(items)
    db.commit()
    return KetQuaThemNhieu(created=len(items))


@router.post("", response_model=DmThcsUuNhuocDiemPublic, status_code=status.HTTP_201_CREATED)
def create_thcs_uu_nhuoc_diem(
    payload: DmThcsUuNhuocDiemWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThcsUuNhuocDiemPublic:
    """Thêm một ưu/nhược điểm cho hướng đi."""
    huong = kiem_tra_huong_di(db, [payload.thcs_huong_di_id])[payload.thcs_huong_di_id]
    item = DmThcsUuNhuocDiem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return _to_public(item, huong)


@router.put("/{item_id}", response_model=DmThcsUuNhuocDiemPublic)
def update_thcs_uu_nhuoc_diem(
    item_id: int,
    payload: DmThcsUuNhuocDiemWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThcsUuNhuocDiemPublic:
    """Cập nhật toàn bộ thông tin một ưu/nhược điểm."""
    item = _get_or_400(db, item_id)
    huong = kiem_tra_huong_di(db, [payload.thcs_huong_di_id])[payload.thcs_huong_di_id]
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return _to_public(item, huong)


@router.delete("", response_model=KetQuaXoaNhieu)
def delete_thcs_uu_nhuoc_diem_many(
    payload: DmThcsDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaXoaNhieu:
    """Xóa nhiều ưu/nhược điểm theo danh sách id. Id không tồn tại thì bỏ qua."""
    items = db.scalars(select(DmThcsUuNhuocDiem).where(DmThcsUuNhuocDiem.id.in_(payload.ids))).all()
    for item in items:
        db.delete(item)
    db.commit()
    return KetQuaXoaNhieu(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_thcs_uu_nhuoc_diem(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> None:
    """Xóa một ưu/nhược điểm theo id."""
    db.delete(_get_or_400(db, item_id))
    db.commit()
