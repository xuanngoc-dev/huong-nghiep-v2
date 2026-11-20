from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_current_user
from app.db.session import get_db
from app.models.dm_thpt_xkld import (
    DmThptXkldChiPhi,
    DmThptXkldNhomNghe,
    DmThptXkldKenhKetNoi,
    DmThptXkldNgheCuThe,
    DmThptXkldThiTruong,
    DmThptXkldThuTuc,
)
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_thpt_xkld import (
    DmThptXkldDeleteMany,
    DmThptXkldThiTruongPage,
    DmThptXkldThiTruongPublic,
    DmThptXkldThiTruongWrite,
    KetQuaThemNhieu,
    KetQuaXoaNhieu,
)
from app.services.thpt_xkld import kiem_tra_nhom_nghe
from app.services.thpt_xkld import like_pattern as _like_pattern

router = APIRouter(prefix="/danh-muc/thpt-xkld/thi-truong", tags=["danh-muc"])

_BANG_CON = (DmThptXkldNgheCuThe, DmThptXkldChiPhi, DmThptXkldThuTuc, DmThptXkldKenhKetNoi)


def _get_or_400(db: Session, item_id: int) -> DmThptXkldThiTruong:
    """Lấy một thị trường XKLĐ theo id. Trả lỗi 400 kèm thông báo nếu không tồn tại."""
    item = db.get(DmThptXkldThiTruong, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy thị trường XKLĐ có id = {item_id}",
        )
    return item


def _to_public(item: DmThptXkldThiTruong, nhom: DmThptXkldNhomNghe | None) -> DmThptXkldThiTruongPublic:
    """Ghép thị trường với mã và tên nhóm nghề cha."""
    return DmThptXkldThiTruongPublic(
        id=item.id,
        thpt_xkld_nhom_nghe_id=item.thpt_xkld_nhom_nghe_id,
        ma_nhom=nhom.ma_nhom if nhom else None,
        ten_nhom=nhom.ten_nhom if nhom else None,
        ma_quoc_gia=item.ma_quoc_gia,
        ten_quoc_gia=item.ten_quoc_gia,
        loai_visa=item.loai_visa,
        dac_diem_thi_truong=item.dac_diem_thi_truong,
        thu_nhap_rieng_text=item.thu_nhap_rieng_text,
        thoi_han_hop_dong_nam=item.thoi_han_hop_dong_nam,
        thu_tu_hien_thi=item.thu_tu_hien_thi,
    )


def _co_du_lieu_con(db: Session, thi_truong_id: int) -> bool:
    return any(
        db.scalar(select(func.count()).select_from(model).where(model.thpt_xkld_thi_truong_id == thi_truong_id))
        for model in _BANG_CON
    )


@router.get("", response_model=DmThptXkldThiTruongPage)
def list_thpt_xkld_thi_truong(
    q: str | None = Query(default=None, max_length=255),
    thpt_xkld_nhom_nghe_id: int | None = Query(default=None, ge=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
) -> DmThptXkldThiTruongPage:
    """Lấy danh sách thị trường XKLĐ có phân trang, lọc theo từ khóa và nhóm nghề. Không cần đăng nhập."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmThptXkldThiTruong.ma_quoc_gia.like(pattern, escape="\\"),
                DmThptXkldThiTruong.ten_quoc_gia.like(pattern, escape="\\"),
                DmThptXkldNhomNghe.ten_nhom.like(pattern, escape="\\"),
            )
        )
    if thpt_xkld_nhom_nghe_id is not None:
        filters.append(DmThptXkldThiTruong.thpt_xkld_nhom_nghe_id == thpt_xkld_nhom_nghe_id)

    base = (
        select(DmThptXkldThiTruong, DmThptXkldNhomNghe)
        .join(DmThptXkldNhomNghe, DmThptXkldThiTruong.thpt_xkld_nhom_nghe_id == DmThptXkldNhomNghe.id)
        .where(*filters)
    )
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    rows = db.execute(
        base.order_by(
            DmThptXkldThiTruong.thpt_xkld_nhom_nghe_id.asc(),
            DmThptXkldThiTruong.thu_tu_hien_thi.asc(),
            DmThptXkldThiTruong.id.asc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmThptXkldThiTruongPage(
        items=[_to_public(item, nhom) for item, nhom in rows], total=total, page=page, page_size=page_size
    )


@router.get("/{item_id}", response_model=DmThptXkldThiTruongPublic)
def get_thpt_xkld_thi_truong(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmThptXkldThiTruongPublic:
    """Lấy chi tiết một thị trường XKLĐ theo id."""
    item = _get_or_400(db, item_id)
    return _to_public(item, db.get(DmThptXkldNhomNghe, item.thpt_xkld_nhom_nghe_id))


@router.post("/bulk", response_model=KetQuaThemNhieu, status_code=status.HTTP_201_CREATED)
def create_thpt_xkld_thi_truong_bulk(
    payload: list[DmThptXkldThiTruongWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaThemNhieu:
    """Thêm nhiều thị trường cùng lúc. Từ chối nếu có nhóm nghề không tồn tại."""
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách thị trường trống")
    if len(payload) > 500:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chỉ thêm tối đa 500 thị trường mỗi lần")
    kiem_tra_nhom_nghe(db, [item.thpt_xkld_nhom_nghe_id for item in payload])
    items = [DmThptXkldThiTruong(**item.model_dump()) for item in payload]
    db.add_all(items)
    db.commit()
    return KetQuaThemNhieu(created=len(items))


@router.post("", response_model=DmThptXkldThiTruongPublic, status_code=status.HTTP_201_CREATED)
def create_thpt_xkld_thi_truong(
    payload: DmThptXkldThiTruongWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThptXkldThiTruongPublic:
    """Thêm một thị trường vào nhóm nghề XKLĐ."""
    nhom = kiem_tra_nhom_nghe(db, [payload.thpt_xkld_nhom_nghe_id])[payload.thpt_xkld_nhom_nghe_id]
    item = DmThptXkldThiTruong(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return _to_public(item, nhom)


@router.put("/{item_id}", response_model=DmThptXkldThiTruongPublic)
def update_thpt_xkld_thi_truong(
    item_id: int,
    payload: DmThptXkldThiTruongWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThptXkldThiTruongPublic:
    """Cập nhật toàn bộ thông tin một thị trường. Không cho đổi nhóm nghề khi thị trường đã có dữ liệu con."""
    item = _get_or_400(db, item_id)
    nhom = kiem_tra_nhom_nghe(db, [payload.thpt_xkld_nhom_nghe_id])[payload.thpt_xkld_nhom_nghe_id]
    if payload.thpt_xkld_nhom_nghe_id != item.thpt_xkld_nhom_nghe_id and _co_du_lieu_con(db, item.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Thị trường {item.ten_quoc_gia} đã có nghề cụ thể, chi phí, thủ tục hoặc kênh kết nối; "
            "không thể chuyển sang nhóm nghề khác",
        )
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return _to_public(item, nhom)


@router.delete("", response_model=KetQuaXoaNhieu)
def delete_thpt_xkld_thi_truong_many(
    payload: DmThptXkldDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaXoaNhieu:
    """Xóa nhiều thị trường theo danh sách id; dữ liệu con riêng của thị trường bị xóa theo (CASCADE)."""
    items = db.scalars(select(DmThptXkldThiTruong).where(DmThptXkldThiTruong.id.in_(payload.ids))).all()
    for item in items:
        db.delete(item)
    db.commit()
    return KetQuaXoaNhieu(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_thpt_xkld_thi_truong(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> None:
    """Xóa một thị trường theo id; dữ liệu con riêng của thị trường bị xóa theo (CASCADE)."""
    db.delete(_get_or_400(db, item_id))
    db.commit()
