from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_current_user
from app.db.session import get_db
from app.models.dm_thpt_duhoc import (
    DmThptDuhocChiPhi,
    DmThptDuhocHuongDi,
    DmThptDuhocKenhKetNoi,
    DmThptDuhocNganh,
    DmThptDuhocQuocGia,
    DmThptDuhocThuTuc,
)
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_thpt_duhoc import (
    DmThptDuhocDeleteMany,
    DmThptDuhocQuocGiaPage,
    DmThptDuhocQuocGiaPublic,
    DmThptDuhocQuocGiaWrite,
    KetQuaThemNhieu,
    KetQuaXoaNhieu,
)
from app.services.thpt_duhoc import kiem_tra_huong_di
from app.services.thpt_duhoc import like_pattern as _like_pattern

router = APIRouter(prefix="/danh-muc/thpt-du-hoc/quoc-gia", tags=["danh-muc"])

_BANG_CON = (DmThptDuhocNganh, DmThptDuhocChiPhi, DmThptDuhocThuTuc, DmThptDuhocKenhKetNoi)


def _get_or_400(db: Session, item_id: int) -> DmThptDuhocQuocGia:
    """Lấy một quốc gia du học theo id. Trả lỗi 400 kèm thông báo nếu không tồn tại."""
    item = db.get(DmThptDuhocQuocGia, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy quốc gia du học có id = {item_id}",
        )
    return item


def _to_public(item: DmThptDuhocQuocGia, huong: DmThptDuhocHuongDi | None) -> DmThptDuhocQuocGiaPublic:
    """Ghép quốc gia với mã và tên hướng đi cha."""
    return DmThptDuhocQuocGiaPublic(
        id=item.id,
        thpt_duhoc_huong_di_id=item.thpt_duhoc_huong_di_id,
        ma_huong=huong.ma_huong if huong else None,
        ten_huong=huong.ten_huong if huong else None,
        ma_quoc_gia=item.ma_quoc_gia,
        ten_quoc_gia=item.ten_quoc_gia,
        dac_diem_noi_bat=item.dac_diem_noi_bat,
        yeu_cau_ngoai_ngu_rieng=item.yeu_cau_ngoai_ngu_rieng,
        co_hoi_viec_lam_visa=item.co_hoi_viec_lam_visa,
        thu_tu_hien_thi=item.thu_tu_hien_thi,
    )


def _co_du_lieu_con(db: Session, quoc_gia_id: int) -> bool:
    return any(
        db.scalar(select(func.count()).select_from(model).where(model.thpt_duhoc_quoc_gia_id == quoc_gia_id))
        for model in _BANG_CON
    )


@router.get("", response_model=DmThptDuhocQuocGiaPage)
def list_thpt_duhoc_quoc_gia(
    q: str | None = Query(default=None, max_length=255),
    thpt_duhoc_huong_di_id: int | None = Query(default=None, ge=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
) -> DmThptDuhocQuocGiaPage:
    """Lấy danh sách quốc gia du học có phân trang, lọc theo từ khóa và hướng đi. Không cần đăng nhập."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmThptDuhocQuocGia.ma_quoc_gia.like(pattern, escape="\\"),
                DmThptDuhocQuocGia.ten_quoc_gia.like(pattern, escape="\\"),
                DmThptDuhocHuongDi.ten_huong.like(pattern, escape="\\"),
            )
        )
    if thpt_duhoc_huong_di_id is not None:
        filters.append(DmThptDuhocQuocGia.thpt_duhoc_huong_di_id == thpt_duhoc_huong_di_id)

    base = (
        select(DmThptDuhocQuocGia, DmThptDuhocHuongDi)
        .join(DmThptDuhocHuongDi, DmThptDuhocQuocGia.thpt_duhoc_huong_di_id == DmThptDuhocHuongDi.id)
        .where(*filters)
    )
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    rows = db.execute(
        base.order_by(
            DmThptDuhocQuocGia.thpt_duhoc_huong_di_id.asc(),
            DmThptDuhocQuocGia.thu_tu_hien_thi.asc(),
            DmThptDuhocQuocGia.id.asc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmThptDuhocQuocGiaPage(
        items=[_to_public(item, huong) for item, huong in rows], total=total, page=page, page_size=page_size
    )


@router.get("/{item_id}", response_model=DmThptDuhocQuocGiaPublic)
def get_thpt_duhoc_quoc_gia(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmThptDuhocQuocGiaPublic:
    """Lấy chi tiết một quốc gia du học theo id."""
    item = _get_or_400(db, item_id)
    return _to_public(item, db.get(DmThptDuhocHuongDi, item.thpt_duhoc_huong_di_id))


@router.post("/bulk", response_model=KetQuaThemNhieu, status_code=status.HTTP_201_CREATED)
def create_thpt_duhoc_quoc_gia_bulk(
    payload: list[DmThptDuhocQuocGiaWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaThemNhieu:
    """Thêm nhiều quốc gia cùng lúc. Từ chối nếu có hướng đi không tồn tại."""
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách quốc gia trống")
    if len(payload) > 500:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chỉ thêm tối đa 500 quốc gia mỗi lần")
    kiem_tra_huong_di(db, [item.thpt_duhoc_huong_di_id for item in payload])
    items = [DmThptDuhocQuocGia(**item.model_dump()) for item in payload]
    db.add_all(items)
    db.commit()
    return KetQuaThemNhieu(created=len(items))


@router.post("", response_model=DmThptDuhocQuocGiaPublic, status_code=status.HTTP_201_CREATED)
def create_thpt_duhoc_quoc_gia(
    payload: DmThptDuhocQuocGiaWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThptDuhocQuocGiaPublic:
    """Thêm một quốc gia vào hướng đi du học."""
    huong = kiem_tra_huong_di(db, [payload.thpt_duhoc_huong_di_id])[payload.thpt_duhoc_huong_di_id]
    item = DmThptDuhocQuocGia(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return _to_public(item, huong)


@router.put("/{item_id}", response_model=DmThptDuhocQuocGiaPublic)
def update_thpt_duhoc_quoc_gia(
    item_id: int,
    payload: DmThptDuhocQuocGiaWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThptDuhocQuocGiaPublic:
    """Cập nhật toàn bộ thông tin một quốc gia. Không cho đổi hướng đi khi quốc gia đã có dữ liệu con."""
    item = _get_or_400(db, item_id)
    huong = kiem_tra_huong_di(db, [payload.thpt_duhoc_huong_di_id])[payload.thpt_duhoc_huong_di_id]
    if payload.thpt_duhoc_huong_di_id != item.thpt_duhoc_huong_di_id and _co_du_lieu_con(db, item.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Quốc gia {item.ten_quoc_gia} đã có ngành, chi phí, thủ tục hoặc kênh kết nối; "
            "không thể chuyển sang hướng đi khác",
        )
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return _to_public(item, huong)


@router.delete("", response_model=KetQuaXoaNhieu)
def delete_thpt_duhoc_quoc_gia_many(
    payload: DmThptDuhocDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaXoaNhieu:
    """Xóa nhiều quốc gia theo danh sách id; dữ liệu con riêng của quốc gia bị xóa theo (CASCADE)."""
    items = db.scalars(select(DmThptDuhocQuocGia).where(DmThptDuhocQuocGia.id.in_(payload.ids))).all()
    for item in items:
        db.delete(item)
    db.commit()
    return KetQuaXoaNhieu(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_thpt_duhoc_quoc_gia(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> None:
    """Xóa một quốc gia theo id; dữ liệu con riêng của quốc gia bị xóa theo (CASCADE)."""
    db.delete(_get_or_400(db, item_id))
    db.commit()
