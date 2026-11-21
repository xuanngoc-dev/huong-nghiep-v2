from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, not_, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_current_user
from app.db.session import get_db
from app.models.dm_nhom_nghe_di_lam import DmNgheCuTheDiLam, DmNhomNgheDiLam
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_nhom_nghe_di_lam import (
    DmNgheCuTheDiLamDeleteMany,
    DmNgheCuTheDiLamPage,
    DmNgheCuTheDiLamPublic,
    DmNgheCuTheDiLamWrite,
    KetQuaThemNhieu,
    KetQuaXoaNhieu,
)

router = APIRouter(prefix="/danh-muc/nghe-cu-the-di-lam", tags=["danh-muc"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _get_or_400(db: Session, item_id: int) -> DmNgheCuTheDiLam:
    """Lấy một nghề cụ thể theo id. Trả lỗi 400 kèm thông báo nếu không tồn tại."""
    item = db.get(DmNgheCuTheDiLam, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy nghề cụ thể có id = {item_id}",
        )
    return item


def _ensure_nhom(db: Session, ids: list[int]) -> dict[int, DmNhomNgheDiLam]:
    """Kiểm tra mọi nhóm nghề trong danh sách đều tồn tại; trả về map id → nhóm."""
    unique = list(dict.fromkeys(ids))
    found = {
        nhom.id: nhom for nhom in db.scalars(select(DmNhomNgheDiLam).where(DmNhomNgheDiLam.id.in_(unique))).all()
    }
    missing = [str(nhom_id) for nhom_id in unique if nhom_id not in found]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy nhóm nghề đi làm có id = {', '.join(missing)}",
        )
    return found


def _to_public(item: DmNgheCuTheDiLam, nhom: DmNhomNgheDiLam | None) -> DmNgheCuTheDiLamPublic:
    """Ghép nghề cụ thể với mã và tên nhóm nghề cha."""
    return DmNgheCuTheDiLamPublic(
        id=item.id,
        nhom_nghe_di_lam_id=item.nhom_nghe_di_lam_id,
        ma_nhom=nhom.ma_nhom if nhom else None,
        ten_nhom=nhom.ten_nhom if nhom else None,
        ten_nghe=item.ten_nghe,
        mo_ta_ngan=item.mo_ta_ngan,
        yeu_cau_them=item.yeu_cau_them,
        yeu_cau_bang_cap=item.yeu_cau_bang_cap,
        bat_buoc_dao_tao_chinh_quy=item.bat_buoc_dao_tao_chinh_quy,
    )


@router.get("", response_model=DmNgheCuTheDiLamPage)
def list_nghe_cu_the_di_lam(
    q: str | None = Query(default=None, max_length=255),
    nhom_nghe_di_lam_id: int | None = Query(default=None, ge=1),
    co_bang_cap: int | None = Query(default=None, ge=0, le=1),
    chinh_quy: int | None = Query(default=None, ge=0, le=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
) -> DmNgheCuTheDiLamPage:
    """Lấy danh sách nghề cụ thể có phân trang, lọc theo từ khóa và nhóm nghề. Không cần đăng nhập.

    `co_bang_cap`: 1 = có yêu cầu bằng cấp bắt buộc, 0 = không. `chinh_quy`: 1 = bắt buộc đào tạo chính quy, 0 = không.
    """
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmNgheCuTheDiLam.ten_nghe.like(pattern, escape="\\"),
                DmNhomNgheDiLam.ten_nhom.like(pattern, escape="\\"),
                DmNhomNgheDiLam.ma_nhom.like(pattern, escape="\\"),
            )
        )
    if nhom_nghe_di_lam_id is not None:
        filters.append(DmNgheCuTheDiLam.nhom_nghe_di_lam_id == nhom_nghe_di_lam_id)
    if co_bang_cap is not None:
        co = and_(DmNgheCuTheDiLam.yeu_cau_bang_cap.is_not(None), DmNgheCuTheDiLam.yeu_cau_bang_cap != "")
        filters.append(co if co_bang_cap else not_(co))
    if chinh_quy is not None:
        bat_buoc = DmNgheCuTheDiLam.bat_buoc_dao_tao_chinh_quy == 1
        filters.append(bat_buoc if chinh_quy else or_(DmNgheCuTheDiLam.bat_buoc_dao_tao_chinh_quy.is_(None), not_(bat_buoc)))

    base = select(DmNgheCuTheDiLam, DmNhomNgheDiLam).join(
        DmNhomNgheDiLam, DmNgheCuTheDiLam.nhom_nghe_di_lam_id == DmNhomNgheDiLam.id
    ).where(*filters)
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    rows = db.execute(
        base.order_by(DmNhomNgheDiLam.ma_nhom.asc(), DmNgheCuTheDiLam.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmNgheCuTheDiLamPage(
        items=[_to_public(item, nhom) for item, nhom in rows], total=total, page=page, page_size=page_size
    )


@router.get("/{item_id}", response_model=DmNgheCuTheDiLamPublic)
def get_nghe_cu_the_di_lam(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmNgheCuTheDiLamPublic:
    """Lấy chi tiết một nghề cụ thể theo id."""
    item = _get_or_400(db, item_id)
    return _to_public(item, db.get(DmNhomNgheDiLam, item.nhom_nghe_di_lam_id))


@router.post("/bulk", response_model=KetQuaThemNhieu, status_code=status.HTTP_201_CREATED)
def create_nghe_cu_the_di_lam_bulk(
    payload: list[DmNgheCuTheDiLamWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaThemNhieu:
    """Thêm nhiều nghề cụ thể cùng lúc. Từ chối nếu có nhóm nghề không tồn tại."""
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách nghề cụ thể trống")
    if len(payload) > 500:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chỉ thêm tối đa 500 nghề mỗi lần")
    _ensure_nhom(db, [item.nhom_nghe_di_lam_id for item in payload])
    items = [DmNgheCuTheDiLam(**item.model_dump()) for item in payload]
    db.add_all(items)
    db.commit()
    return KetQuaThemNhieu(created=len(items))


@router.post("", response_model=DmNgheCuTheDiLamPublic, status_code=status.HTTP_201_CREATED)
def create_nghe_cu_the_di_lam(
    payload: DmNgheCuTheDiLamWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmNgheCuTheDiLamPublic:
    """Thêm một nghề cụ thể vào nhóm nghề."""
    nhom = _ensure_nhom(db, [payload.nhom_nghe_di_lam_id])[payload.nhom_nghe_di_lam_id]
    item = DmNgheCuTheDiLam(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return _to_public(item, nhom)


@router.put("/{item_id}", response_model=DmNgheCuTheDiLamPublic)
def update_nghe_cu_the_di_lam(
    item_id: int,
    payload: DmNgheCuTheDiLamWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmNgheCuTheDiLamPublic:
    """Cập nhật toàn bộ thông tin một nghề cụ thể theo id."""
    item = _get_or_400(db, item_id)
    nhom = _ensure_nhom(db, [payload.nhom_nghe_di_lam_id])[payload.nhom_nghe_di_lam_id]
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return _to_public(item, nhom)


@router.delete("", response_model=KetQuaXoaNhieu)
def delete_nghe_cu_the_di_lam_many(
    payload: DmNgheCuTheDiLamDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaXoaNhieu:
    """Xóa nhiều nghề cụ thể theo danh sách id. Id không tồn tại thì bỏ qua."""
    items = db.scalars(select(DmNgheCuTheDiLam).where(DmNgheCuTheDiLam.id.in_(payload.ids))).all()
    for item in items:
        db.delete(item)
    db.commit()
    return KetQuaXoaNhieu(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_nghe_cu_the_di_lam(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> None:
    """Xóa một nghề cụ thể theo id."""
    db.delete(_get_or_400(db, item_id))
    db.commit()
