from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.dm_nganh_dao_tao import DmNganhDaoTao
from app.models.dm_nhom_nganh_dao_tao import DmNhomNganhDaoTao
from app.models.dm_nhom_tinh_cach_holland import DmNhomTinhCachHolland
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_nganh_dao_tao import (
    DmNganhDaoTaoBulkResult,
    DmNganhDaoTaoDeleteMany,
    DmNganhDaoTaoDeleteManyResult,
    DmNganhDaoTaoPage,
    DmNganhDaoTaoPublic,
    DmNganhDaoTaoWrite,
)

router = APIRouter(prefix="/danh-muc/nganh-dao-tao", tags=["danh-muc"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _ensure_nhom_nganh(db: Session, codes: list[str]) -> None:
    """Kiểm tra mọi mã nhóm ngành trong danh sách đều tồn tại."""
    unique = list(dict.fromkeys(codes))
    found = set(
        db.scalars(
            select(DmNhomNganhDaoTao.ma_nhom_nganh).where(DmNhomNganhDaoTao.ma_nhom_nganh.in_(unique))
        ).all()
    )
    missing = [code for code in unique if code not in found]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã nhóm ngành không tồn tại: {', '.join(missing)}",
        )


def _ensure_holland(db: Session, groups: list[list[str] | None]) -> None:
    """Kiểm tra mọi mã Holland đều có trong danh mục nhóm tính cách Holland."""
    codes: list[str] = []
    for group in groups:
        if group:
            codes.extend(group)
    unique = list(dict.fromkeys(codes))
    if not unique:
        return
    found = set(
        db.scalars(select(DmNhomTinhCachHolland.ma_nhom).where(DmNhomTinhCachHolland.ma_nhom.in_(unique))).all()
    )
    missing = [code for code in unique if code not in found]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã Holland không tồn tại: {', '.join(missing)}",
        )


def _to_public(item: DmNganhDaoTao, parent: DmNhomNganhDaoTao) -> DmNganhDaoTaoPublic:
    """Ghép ngành với tên và mã nhóm ngành cha để trả về cho client."""
    return DmNganhDaoTaoPublic(
        id=item.id,
        ma_nhom_nganh=item.ma_nhom_nganh,
        ten_nhom_nganh=parent.ten_nhom_nganh,
        ma_nganh=item.ma_nganh,
        ten_nganh=item.ten_nganh,
        ten_tieng_anh=item.ten_tieng_anh,
        trinh_do=item.trinh_do,
        ma_holand=item.ma_holand,
        mo_ta=item.mo_ta,
        trang_thai=item.trang_thai,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _load_pair(db: Session, item_id: int) -> tuple[DmNganhDaoTao, DmNhomNganhDaoTao]:
    """Lấy một ngành kèm nhóm ngành cha. Trả lỗi 404 nếu ngành không tồn tại."""
    row = db.execute(
        select(DmNganhDaoTao, DmNhomNganhDaoTao)
        .join(DmNhomNganhDaoTao, DmNganhDaoTao.ma_nhom_nganh == DmNhomNganhDaoTao.ma_nhom_nganh)
        .where(DmNganhDaoTao.id == item_id)
    ).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy ngành đào tạo")
    return row[0], row[1]


@router.get("", response_model=DmNganhDaoTaoPage)
def list_nganh_dao_tao(
    q: str | None = Query(default=None, max_length=255),
    trang_thai: int | None = Query(default=None, ge=0, le=1),
    ma_nhom_nganh: str | None = Query(default=None, max_length=20),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmNganhDaoTaoPage:
    """Lấy danh sách ngành đào tạo có phân trang. Lọc theo từ khóa, trạng thái và nhóm ngành cha."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmNganhDaoTao.ten_nganh.like(pattern, escape="\\"),
                DmNganhDaoTao.ma_nganh.like(pattern, escape="\\"),
                DmNganhDaoTao.ten_tieng_anh.like(pattern, escape="\\"),
                DmNganhDaoTao.trinh_do.like(pattern, escape="\\"),
                cast(DmNganhDaoTao.ma_holand, String).like(pattern, escape="\\"),
                DmNhomNganhDaoTao.ten_nhom_nganh.like(pattern, escape="\\"),
                DmNhomNganhDaoTao.ma_nhom_nganh.like(pattern, escape="\\"),
            )
        )
    if trang_thai is not None:
        filters.append(DmNganhDaoTao.trang_thai == trang_thai)
    if ma_nhom_nganh and ma_nhom_nganh.strip():
        filters.append(DmNganhDaoTao.ma_nhom_nganh == ma_nhom_nganh.strip().upper())

    joined = DmNganhDaoTao.__table__.join(
        DmNhomNganhDaoTao, DmNganhDaoTao.ma_nhom_nganh == DmNhomNganhDaoTao.ma_nhom_nganh
    )
    count_stmt = select(func.count()).select_from(joined)
    stmt = select(DmNganhDaoTao, DmNhomNganhDaoTao).join(
        DmNhomNganhDaoTao, DmNganhDaoTao.ma_nhom_nganh == DmNhomNganhDaoTao.ma_nhom_nganh
    )
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    rows = db.execute(
        stmt.order_by(DmNganhDaoTao.ma_nganh.asc(), DmNganhDaoTao.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmNganhDaoTaoPage(
        items=[_to_public(item, parent) for item, parent in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{item_id}", response_model=DmNganhDaoTaoPublic)
def get_nganh_dao_tao(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmNganhDaoTaoPublic:
    """Lấy chi tiết một ngành đào tạo theo id, kèm tên nhóm ngành cha."""
    item, parent = _load_pair(db, item_id)
    return _to_public(item, parent)


@router.post("/bulk", response_model=DmNganhDaoTaoBulkResult, status_code=status.HTTP_201_CREATED)
def create_nganh_dao_tao_bulk(
    payload: list[DmNganhDaoTaoWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmNganhDaoTaoBulkResult:
    """Thêm nhiều ngành cùng lúc. Từ chối nếu mã trùng, nhóm ngành cha hoặc mã Holland không tồn tại."""
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách ngành trống")
    if len(payload) > 500:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chỉ thêm tối đa 500 ngành mỗi lần")

    codes = [item.ma_nganh for item in payload]
    seen: set[str] = set()
    duplicated: list[str] = []
    for code in codes:
        if code in seen and code not in duplicated:
            duplicated.append(code)
        seen.add(code)
    if duplicated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã ngành bị trùng trong dữ liệu: {', '.join(duplicated)}",
        )

    existing = list(db.scalars(select(DmNganhDaoTao.ma_nganh).where(DmNganhDaoTao.ma_nganh.in_(codes))).all())
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã ngành đã tồn tại: {', '.join(existing)}",
        )

    _ensure_nhom_nganh(db, [item.ma_nhom_nganh for item in payload])
    _ensure_holland(db, [item.ma_holand for item in payload])
    items = [DmNganhDaoTao(**item.model_dump()) for item in payload]
    db.add_all(items)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mã ngành đã tồn tại") from None
    return DmNganhDaoTaoBulkResult(created=len(items))


@router.post("", response_model=DmNganhDaoTaoPublic, status_code=status.HTTP_201_CREATED)
def create_nganh_dao_tao(
    payload: DmNganhDaoTaoWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmNganhDaoTaoPublic:
    """Thêm một ngành đào tạo. Từ chối nếu mã đã tồn tại, nhóm ngành cha hoặc mã Holland không tồn tại."""
    _ensure_nhom_nganh(db, [payload.ma_nhom_nganh])
    _ensure_holland(db, [payload.ma_holand])
    item = DmNganhDaoTao(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mã ngành đã tồn tại") from None
    db.refresh(item)
    saved, parent = _load_pair(db, item.id)
    return _to_public(saved, parent)


@router.put("/{item_id}", response_model=DmNganhDaoTaoPublic)
def update_nganh_dao_tao(
    item_id: int,
    payload: DmNganhDaoTaoWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmNganhDaoTaoPublic:
    """Cập nhật toàn bộ thông tin một ngành đào tạo theo id."""
    item, _parent = _load_pair(db, item_id)
    _ensure_nhom_nganh(db, [payload.ma_nhom_nganh])
    _ensure_holland(db, [payload.ma_holand])
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mã ngành đã tồn tại") from None
    db.refresh(item)
    saved, parent = _load_pair(db, item.id)
    return _to_public(saved, parent)


@router.delete("", response_model=DmNganhDaoTaoDeleteManyResult)
def delete_nganh_dao_tao_many(
    payload: DmNganhDaoTaoDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmNganhDaoTaoDeleteManyResult:
    """Xóa nhiều ngành theo danh sách id. Từ chối nếu còn chuyên ngành thuộc các ngành đó."""
    items = db.scalars(select(DmNganhDaoTao).where(DmNganhDaoTao.id.in_(payload.ids))).all()
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy ngành đào tạo để xóa")
    for item in items:
        db.delete(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa vì còn chuyên ngành thuộc ngành này",
        ) from None
    return DmNganhDaoTaoDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_nganh_dao_tao(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> None:
    """Xóa một ngành đào tạo theo id. Từ chối nếu còn chuyên ngành thuộc ngành đó."""
    item, _parent = _load_pair(db, item_id)
    db.delete(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa vì còn chuyên ngành thuộc ngành này",
        ) from None
