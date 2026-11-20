from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_current_user
from app.db.session import get_db
from app.models.dm_nhom_nghe_di_lam import DmNhomNgheDiLam
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_nhom_nghe_di_lam import (
    DmNhomNgheDiLamDeleteMany,
    DmNhomNgheDiLamPage,
    DmNhomNgheDiLamPublic,
    DmNhomNgheDiLamTrangThai,
    DmNhomNgheDiLamTrangThaiMany,
    DmNhomNgheDiLamWrite,
    KetQuaDoiTrangThaiNhieu,
    KetQuaThemNhieu,
    KetQuaXoaNhieu,
    LoaiHinhDauVao,
    NhomMucTieu,
)

router = APIRouter(prefix="/danh-muc/nhom-nghe-di-lam", tags=["danh-muc"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _get_or_400(db: Session, item_id: int) -> DmNhomNgheDiLam:
    """Lấy một nhóm nghề đi làm theo id. Trả lỗi 400 kèm thông báo nếu không tồn tại."""
    item = db.get(DmNhomNgheDiLam, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy nhóm nghề đi làm có id = {item_id}",
        )
    return item


def _loi_trung_ma() -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mã nhóm nghề đã tồn tại")


@router.get("", response_model=DmNhomNgheDiLamPage)
def list_nhom_nghe_di_lam(
    q: str | None = Query(default=None, max_length=255),
    trang_thai: int | None = Query(default=None, ge=0, le=1),
    loai_hinh_dau_vao: LoaiHinhDauVao | None = Query(default=None),
    nhom_muc_tieu: NhomMucTieu | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
) -> DmNhomNgheDiLamPage:
    """Lấy danh sách nhóm nghề đi làm có phân trang, không cần đăng nhập."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmNhomNgheDiLam.ma_nhom.like(pattern, escape="\\"),
                DmNhomNgheDiLam.ten_nhom.like(pattern, escape="\\"),
                DmNhomNgheDiLam.ma_holland.like(pattern, escape="\\"),
            )
        )
    if trang_thai is not None:
        filters.append(DmNhomNgheDiLam.trang_thai == trang_thai)
    if loai_hinh_dau_vao:
        filters.append(DmNhomNgheDiLam.loai_hinh_dau_vao == loai_hinh_dau_vao)
    if nhom_muc_tieu:
        filters.append(DmNhomNgheDiLam.nhom_muc_tieu == nhom_muc_tieu)

    total = db.scalar(select(func.count()).select_from(DmNhomNgheDiLam).where(*filters)) or 0
    items = db.scalars(
        select(DmNhomNgheDiLam)
        .where(*filters)
        .order_by(DmNhomNgheDiLam.ma_nhom.asc(), DmNhomNgheDiLam.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmNhomNgheDiLamPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{item_id}", response_model=DmNhomNgheDiLamPublic)
def get_nhom_nghe_di_lam(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmNhomNgheDiLam:
    """Lấy chi tiết một nhóm nghề đi làm theo id."""
    return _get_or_400(db, item_id)


@router.post("/bulk", response_model=KetQuaThemNhieu, status_code=status.HTTP_201_CREATED)
def create_nhom_nghe_di_lam_bulk(
    payload: list[DmNhomNgheDiLamWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaThemNhieu:
    """Thêm nhiều nhóm nghề cùng lúc. Từ chối nếu mã nhóm trùng trong dữ liệu gửi lên hoặc đã có trong hệ thống."""
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
    existing = list(db.scalars(select(DmNhomNgheDiLam.ma_nhom).where(DmNhomNgheDiLam.ma_nhom.in_(codes))).all())
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã nhóm nghề đã tồn tại: {', '.join(existing)}",
        )

    items = [DmNhomNgheDiLam(**item.model_dump()) for item in payload]
    db.add_all(items)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise _loi_trung_ma() from None
    return KetQuaThemNhieu(created=len(items))


@router.post("", response_model=DmNhomNgheDiLamPublic, status_code=status.HTTP_201_CREATED)
def create_nhom_nghe_di_lam(
    payload: DmNhomNgheDiLamWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmNhomNgheDiLam:
    """Thêm một nhóm nghề đi làm. Từ chối nếu mã nhóm đã tồn tại."""
    item = DmNhomNgheDiLam(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise _loi_trung_ma() from None
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=DmNhomNgheDiLamPublic)
def update_nhom_nghe_di_lam(
    item_id: int,
    payload: DmNhomNgheDiLamWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmNhomNgheDiLam:
    """Cập nhật toàn bộ thông tin một nhóm nghề đi làm theo id."""
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
def update_trang_thai_nhom_nghe_di_lam_many(
    payload: DmNhomNgheDiLamTrangThaiMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaDoiTrangThaiNhieu:
    """Bật/tắt nhiều nhóm nghề cùng lúc. Id không tồn tại thì bỏ qua."""
    items = db.scalars(select(DmNhomNgheDiLam).where(DmNhomNgheDiLam.id.in_(payload.ids))).all()
    for item in items:
        item.trang_thai = payload.trang_thai
    db.commit()
    return KetQuaDoiTrangThaiNhieu(updated=len(items))


@router.patch("/{item_id}/trang-thai", response_model=DmNhomNgheDiLamPublic)
def update_trang_thai_nhom_nghe_di_lam(
    item_id: int,
    payload: DmNhomNgheDiLamTrangThai,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmNhomNgheDiLam:
    """Bật/tắt nhanh một nhóm nghề, giữ nguyên các thông tin khác."""
    item = _get_or_400(db, item_id)
    item.trang_thai = payload.trang_thai
    db.commit()
    db.refresh(item)
    return item


@router.delete("", response_model=KetQuaXoaNhieu)
def delete_nhom_nghe_di_lam_many(
    payload: DmNhomNgheDiLamDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaXoaNhieu:
    """Xóa nhiều nhóm nghề theo danh sách id; nghề cụ thể và liên kết tiêu chí bị xóa theo (CASCADE)."""
    items = db.scalars(select(DmNhomNgheDiLam).where(DmNhomNgheDiLam.id.in_(payload.ids))).all()
    for item in items:
        db.delete(item)
    db.commit()
    return KetQuaXoaNhieu(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_nhom_nghe_di_lam(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> None:
    """Xóa một nhóm nghề theo id; nghề cụ thể và liên kết tiêu chí bị xóa theo (CASCADE)."""
    db.delete(_get_or_400(db, item_id))
    db.commit()
