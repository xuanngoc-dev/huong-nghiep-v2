from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.dm_chuyen_nganh import DmChuyenNganh
from app.models.dm_nganh_dao_tao import DmNganhDaoTao
from app.models.dm_nhom_tinh_cach_holland import DmNhomTinhCachHolland
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_chuyen_nganh import (
    DmChuyenNganhBulkResult,
    DmChuyenNganhDeleteMany,
    DmChuyenNganhDeleteManyResult,
    DmChuyenNganhPage,
    DmChuyenNganhPublic,
    DmChuyenNganhWrite,
)

router = APIRouter(prefix="/danh-muc/chuyen-nganh", tags=["danh-muc"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _ensure_nganh(db: Session, codes: list[str]) -> None:
    """Kiểm tra mọi mã ngành trong danh sách đều tồn tại."""
    unique = list(dict.fromkeys(codes))
    found = set(db.scalars(select(DmNganhDaoTao.ma_nganh).where(DmNganhDaoTao.ma_nganh.in_(unique))).all())
    missing = [code for code in unique if code not in found]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã ngành không tồn tại: {', '.join(missing)}",
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


def _to_public(item: DmChuyenNganh, parent: DmNganhDaoTao) -> DmChuyenNganhPublic:
    """Ghép chuyên ngành với tên và mã ngành cha để trả về cho client."""
    return DmChuyenNganhPublic(
        id=item.id,
        ma_nganh=item.ma_nganh,
        ten_nganh=parent.ten_nganh,
        ten_chuyen_nganh=item.ten_chuyen_nganh,
        ma_chuyen_nganh=item.ma_chuyen_nganh,
        ten_tieng_anh=item.ten_tieng_anh,
        mo_ta=item.mo_ta,
        ma_holand=item.ma_holand,
        trang_thai=item.trang_thai,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _load_pair(db: Session, item_id: int) -> tuple[DmChuyenNganh, DmNganhDaoTao]:
    """Lấy một chuyên ngành kèm ngành cha. Trả lỗi 404 nếu chuyên ngành không tồn tại."""
    row = db.execute(
        select(DmChuyenNganh, DmNganhDaoTao)
        .join(DmNganhDaoTao, DmChuyenNganh.ma_nganh == DmNganhDaoTao.ma_nganh)
        .where(DmChuyenNganh.id == item_id)
    ).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy chuyên ngành")
    return row[0], row[1]


@router.get("", response_model=DmChuyenNganhPage)
def list_chuyen_nganh(
    q: str | None = Query(default=None, max_length=255),
    trang_thai: int | None = Query(default=None, ge=0, le=1),
    ma_nganh: str | None = Query(default=None, max_length=20),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmChuyenNganhPage:
    """Lấy danh sách chuyên ngành có phân trang. Lọc theo từ khóa, trạng thái và ngành cha."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmChuyenNganh.ten_chuyen_nganh.like(pattern, escape="\\"),
                DmChuyenNganh.ma_chuyen_nganh.like(pattern, escape="\\"),
                DmChuyenNganh.ten_tieng_anh.like(pattern, escape="\\"),
                cast(DmChuyenNganh.ma_holand, String).like(pattern, escape="\\"),
                DmNganhDaoTao.ten_nganh.like(pattern, escape="\\"),
                DmNganhDaoTao.ma_nganh.like(pattern, escape="\\"),
            )
        )
    if trang_thai is not None:
        filters.append(DmChuyenNganh.trang_thai == trang_thai)
    if ma_nganh and ma_nganh.strip():
        filters.append(DmChuyenNganh.ma_nganh == ma_nganh.strip().upper())

    joined = DmChuyenNganh.__table__.join(DmNganhDaoTao, DmChuyenNganh.ma_nganh == DmNganhDaoTao.ma_nganh)
    count_stmt = select(func.count()).select_from(joined)
    stmt = select(DmChuyenNganh, DmNganhDaoTao).join(
        DmNganhDaoTao, DmChuyenNganh.ma_nganh == DmNganhDaoTao.ma_nganh
    )
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    rows = db.execute(
        stmt.order_by(DmChuyenNganh.ma_chuyen_nganh.asc(), DmChuyenNganh.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmChuyenNganhPage(
        items=[_to_public(item, parent) for item, parent in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{item_id}", response_model=DmChuyenNganhPublic)
def get_chuyen_nganh(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmChuyenNganhPublic:
    """Lấy chi tiết một chuyên ngành theo id, kèm tên ngành cha."""
    item, parent = _load_pair(db, item_id)
    return _to_public(item, parent)


@router.post("/bulk", response_model=DmChuyenNganhBulkResult, status_code=status.HTTP_201_CREATED)
def create_chuyen_nganh_bulk(
    payload: list[DmChuyenNganhWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmChuyenNganhBulkResult:
    """Thêm nhiều chuyên ngành cùng lúc. Từ chối nếu mã trùng, ngành cha hoặc mã Holland không tồn tại."""
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách chuyên ngành trống")
    if len(payload) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ thêm tối đa 500 chuyên ngành mỗi lần",
        )

    codes = [item.ma_chuyen_nganh for item in payload]
    seen: set[str] = set()
    duplicated: list[str] = []
    for code in codes:
        if code in seen and code not in duplicated:
            duplicated.append(code)
        seen.add(code)
    if duplicated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã chuyên ngành bị trùng trong dữ liệu: {', '.join(duplicated)}",
        )

    existing = list(
        db.scalars(select(DmChuyenNganh.ma_chuyen_nganh).where(DmChuyenNganh.ma_chuyen_nganh.in_(codes))).all()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã chuyên ngành đã tồn tại: {', '.join(existing)}",
        )

    _ensure_nganh(db, [item.ma_nganh for item in payload])
    _ensure_holland(db, [item.ma_holand for item in payload])
    items = [DmChuyenNganh(**item.model_dump()) for item in payload]
    db.add_all(items)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mã chuyên ngành đã tồn tại") from None
    return DmChuyenNganhBulkResult(created=len(items))


@router.post("", response_model=DmChuyenNganhPublic, status_code=status.HTTP_201_CREATED)
def create_chuyen_nganh(
    payload: DmChuyenNganhWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmChuyenNganhPublic:
    """Thêm một chuyên ngành. Từ chối nếu mã đã tồn tại, ngành cha hoặc mã Holland không tồn tại."""
    _ensure_nganh(db, [payload.ma_nganh])
    _ensure_holland(db, [payload.ma_holand])
    item = DmChuyenNganh(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mã chuyên ngành đã tồn tại") from None
    db.refresh(item)
    saved, parent = _load_pair(db, item.id)
    return _to_public(saved, parent)


@router.put("/{item_id}", response_model=DmChuyenNganhPublic)
def update_chuyen_nganh(
    item_id: int,
    payload: DmChuyenNganhWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmChuyenNganhPublic:
    """Cập nhật toàn bộ thông tin một chuyên ngành theo id."""
    item, _parent = _load_pair(db, item_id)
    _ensure_nganh(db, [payload.ma_nganh])
    _ensure_holland(db, [payload.ma_holand])
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mã chuyên ngành đã tồn tại") from None
    db.refresh(item)
    saved, parent = _load_pair(db, item.id)
    return _to_public(saved, parent)


@router.delete("", response_model=DmChuyenNganhDeleteManyResult)
def delete_chuyen_nganh_many(
    payload: DmChuyenNganhDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmChuyenNganhDeleteManyResult:
    """Xóa nhiều chuyên ngành theo danh sách id."""
    items = db.scalars(select(DmChuyenNganh).where(DmChuyenNganh.id.in_(payload.ids))).all()
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy chuyên ngành để xóa")
    for item in items:
        db.delete(item)
    db.commit()
    return DmChuyenNganhDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chuyen_nganh(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> None:
    """Xóa một chuyên ngành theo id."""
    item, _parent = _load_pair(db, item_id)
    db.delete(item)
    db.commit()
