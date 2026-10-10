from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.dm_linh_vuc_dao_tao import DmLinhVucDaoTao
from app.models.dm_nhom_nganh_dao_tao import DmNhomNganhDaoTao
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_nhom_nganh_dao_tao import (
    DmNhomNganhDaoTaoBulkResult,
    DmNhomNganhDaoTaoDeleteMany,
    DmNhomNganhDaoTaoDeleteManyResult,
    DmNhomNganhDaoTaoPage,
    DmNhomNganhDaoTaoPublic,
    DmNhomNganhDaoTaoWrite,
)

router = APIRouter(prefix="/danh-muc/nhom-nganh-dao-tao", tags=["danh-muc"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _ensure_linh_vuc(db: Session, codes: list[str]) -> None:
    """Kiểm tra mọi mã lĩnh vực trong danh sách đều tồn tại."""
    unique = list(dict.fromkeys(codes))
    found = set(
        db.scalars(select(DmLinhVucDaoTao.ma_linh_vuc).where(DmLinhVucDaoTao.ma_linh_vuc.in_(unique))).all()
    )
    missing = [code for code in unique if code not in found]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã lĩnh vực không tồn tại: {', '.join(missing)}",
        )


def _to_public(item: DmNhomNganhDaoTao, parent: DmLinhVucDaoTao) -> DmNhomNganhDaoTaoPublic:
    """Ghép nhóm ngành với tên và mã lĩnh vực cha để trả về cho client."""
    return DmNhomNganhDaoTaoPublic(
        id=item.id,
        ma_linh_vuc=item.ma_linh_vuc,
        ten_linh_vuc=parent.ten_linh_vuc,
        ma_nhom_nganh=item.ma_nhom_nganh,
        ten_nhom_nganh=item.ten_nhom_nganh,
        ten_tieng_anh=item.ten_tieng_anh,
        mo_ta=item.mo_ta,
        trang_thai=item.trang_thai,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _load_pair(db: Session, item_id: int) -> tuple[DmNhomNganhDaoTao, DmLinhVucDaoTao]:
    """Lấy một nhóm ngành kèm lĩnh vực cha. Trả lỗi 404 nếu nhóm ngành không tồn tại."""
    row = db.execute(
        select(DmNhomNganhDaoTao, DmLinhVucDaoTao)
        .join(DmLinhVucDaoTao, DmNhomNganhDaoTao.ma_linh_vuc == DmLinhVucDaoTao.ma_linh_vuc)
        .where(DmNhomNganhDaoTao.id == item_id)
    ).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy nhóm ngành đào tạo")
    return row[0], row[1]


@router.get("", response_model=DmNhomNganhDaoTaoPage)
def list_nhom_nganh_dao_tao(
    q: str | None = Query(default=None, max_length=255),
    trang_thai: int | None = Query(default=None, ge=0, le=1),
    ma_linh_vuc: str | None = Query(default=None, max_length=20),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmNhomNganhDaoTaoPage:
    """Lấy danh sách nhóm ngành có phân trang. Lọc theo từ khóa, trạng thái và lĩnh vực cha."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmNhomNganhDaoTao.ten_nhom_nganh.like(pattern, escape="\\"),
                DmNhomNganhDaoTao.ma_nhom_nganh.like(pattern, escape="\\"),
                DmNhomNganhDaoTao.ten_tieng_anh.like(pattern, escape="\\"),
                DmLinhVucDaoTao.ten_linh_vuc.like(pattern, escape="\\"),
                DmLinhVucDaoTao.ma_linh_vuc.like(pattern, escape="\\"),
            )
        )
    if trang_thai is not None:
        filters.append(DmNhomNganhDaoTao.trang_thai == trang_thai)
    if ma_linh_vuc and ma_linh_vuc.strip():
        filters.append(DmNhomNganhDaoTao.ma_linh_vuc == ma_linh_vuc.strip().upper())

    joined = DmNhomNganhDaoTao.__table__.join(
        DmLinhVucDaoTao, DmNhomNganhDaoTao.ma_linh_vuc == DmLinhVucDaoTao.ma_linh_vuc
    )
    count_stmt = select(func.count()).select_from(joined)
    stmt = select(DmNhomNganhDaoTao, DmLinhVucDaoTao).join(
        DmLinhVucDaoTao, DmNhomNganhDaoTao.ma_linh_vuc == DmLinhVucDaoTao.ma_linh_vuc
    )
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    rows = db.execute(
        stmt.order_by(DmNhomNganhDaoTao.ma_nhom_nganh.asc(), DmNhomNganhDaoTao.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmNhomNganhDaoTaoPage(
        items=[_to_public(item, parent) for item, parent in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{item_id}", response_model=DmNhomNganhDaoTaoPublic)
def get_nhom_nganh_dao_tao(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmNhomNganhDaoTaoPublic:
    """Lấy chi tiết một nhóm ngành đào tạo theo id, kèm tên lĩnh vực cha."""
    item, parent = _load_pair(db, item_id)
    return _to_public(item, parent)


@router.post("/bulk", response_model=DmNhomNganhDaoTaoBulkResult, status_code=status.HTTP_201_CREATED)
def create_nhom_nganh_dao_tao_bulk(
    payload: list[DmNhomNganhDaoTaoWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmNhomNganhDaoTaoBulkResult:
    """Thêm nhiều nhóm ngành cùng lúc. Từ chối nếu mã trùng hoặc lĩnh vực cha không tồn tại."""
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách nhóm ngành trống")
    if len(payload) > 500:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chỉ thêm tối đa 500 nhóm ngành mỗi lần")

    codes = [item.ma_nhom_nganh for item in payload]
    seen: set[str] = set()
    duplicated: list[str] = []
    for code in codes:
        if code in seen and code not in duplicated:
            duplicated.append(code)
        seen.add(code)
    if duplicated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã nhóm ngành bị trùng trong dữ liệu: {', '.join(duplicated)}",
        )

    existing = list(
        db.scalars(
            select(DmNhomNganhDaoTao.ma_nhom_nganh).where(DmNhomNganhDaoTao.ma_nhom_nganh.in_(codes))
        ).all()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã nhóm ngành đã tồn tại: {', '.join(existing)}",
        )

    _ensure_linh_vuc(db, [item.ma_linh_vuc for item in payload])
    items = [DmNhomNganhDaoTao(**item.model_dump()) for item in payload]
    db.add_all(items)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mã nhóm ngành đã tồn tại") from None
    return DmNhomNganhDaoTaoBulkResult(created=len(items))


@router.post("", response_model=DmNhomNganhDaoTaoPublic, status_code=status.HTTP_201_CREATED)
def create_nhom_nganh_dao_tao(
    payload: DmNhomNganhDaoTaoWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmNhomNganhDaoTaoPublic:
    """Thêm một nhóm ngành đào tạo. Từ chối nếu mã đã tồn tại hoặc lĩnh vực cha không tồn tại."""
    _ensure_linh_vuc(db, [payload.ma_linh_vuc])
    item = DmNhomNganhDaoTao(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mã nhóm ngành đã tồn tại") from None
    db.refresh(item)
    saved, parent = _load_pair(db, item.id)
    return _to_public(saved, parent)


@router.put("/{item_id}", response_model=DmNhomNganhDaoTaoPublic)
def update_nhom_nganh_dao_tao(
    item_id: int,
    payload: DmNhomNganhDaoTaoWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmNhomNganhDaoTaoPublic:
    """Cập nhật toàn bộ thông tin một nhóm ngành đào tạo theo id."""
    item, _parent = _load_pair(db, item_id)
    _ensure_linh_vuc(db, [payload.ma_linh_vuc])
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mã nhóm ngành đã tồn tại") from None
    db.refresh(item)
    saved, parent = _load_pair(db, item.id)
    return _to_public(saved, parent)


@router.delete("", response_model=DmNhomNganhDaoTaoDeleteManyResult)
def delete_nhom_nganh_dao_tao_many(
    payload: DmNhomNganhDaoTaoDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmNhomNganhDaoTaoDeleteManyResult:
    """Xóa nhiều nhóm ngành theo danh sách id. Từ chối nếu còn ngành thuộc các nhóm đó."""
    items = db.scalars(select(DmNhomNganhDaoTao).where(DmNhomNganhDaoTao.id.in_(payload.ids))).all()
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy nhóm ngành đào tạo để xóa")
    for item in items:
        db.delete(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa vì còn ngành thuộc nhóm này",
        ) from None
    return DmNhomNganhDaoTaoDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_nhom_nganh_dao_tao(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> None:
    """Xóa một nhóm ngành đào tạo theo id. Từ chối nếu còn ngành thuộc nhóm đó."""
    item, _parent = _load_pair(db, item_id)
    db.delete(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa vì còn ngành thuộc nhóm này",
        ) from None
