from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.dm_mon_hoc import DmMonHoc
from app.models.dm_to_hop_mon_hoc import DmToHopMonHoc
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_to_hop_mon_hoc import (
    DmToHopMonHocBulkResult,
    DmToHopMonHocDeleteMany,
    DmToHopMonHocDeleteManyResult,
    DmToHopMonHocPage,
    DmToHopMonHocPublic,
    DmToHopMonHocWrite,
)

router = APIRouter(prefix="/danh-muc/to-hop-mon-hoc", tags=["danh-muc"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _get_or_404(db: Session, item_id: int) -> DmToHopMonHoc:
    """Lấy một tổ hợp môn học theo id. Trả lỗi 404 nếu không tồn tại."""
    item = db.get(DmToHopMonHoc, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy tổ hợp môn học",
        )
    return item


def _ensure_mon_hoc_exists(db: Session, codes: list[str]) -> None:
    """Kiểm tra mọi mã trong danh sách môn học đều có trong danh mục môn học."""
    if not codes:
        return
    found = set(db.scalars(select(DmMonHoc.ma_mon_hoc).where(DmMonHoc.ma_mon_hoc.in_(codes))).all())
    missing = [code for code in codes if code not in found]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã môn học không tồn tại: {', '.join(missing)}",
        )


@router.get("", response_model=DmToHopMonHocPage)
def list_to_hop_mon_hoc(
    q: str | None = Query(default=None, max_length=150),
    trang_thai: int | None = Query(default=None, ge=0, le=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmToHopMonHocPage:
    """Lấy danh sách tổ hợp môn học có phân trang. Lọc theo từ khóa (tên, mã, mã môn) và trạng thái."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmToHopMonHoc.ten_to_hop.like(pattern, escape="\\"),
                DmToHopMonHoc.ma_to_hop.like(pattern, escape="\\"),
                cast(DmToHopMonHoc.ds_mon_hoc, String).like(pattern, escape="\\"),
            )
        )
    if trang_thai is not None:
        filters.append(DmToHopMonHoc.trang_thai == trang_thai)

    count_stmt = select(func.count()).select_from(DmToHopMonHoc)
    stmt = select(DmToHopMonHoc)
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    items = db.scalars(
        stmt.order_by(DmToHopMonHoc.ma_to_hop.asc(), DmToHopMonHoc.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmToHopMonHocPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{item_id}", response_model=DmToHopMonHocPublic)
def get_to_hop_mon_hoc(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmToHopMonHoc:
    """Lấy chi tiết một tổ hợp môn học theo id."""
    return _get_or_404(db, item_id)


@router.post("/bulk", response_model=DmToHopMonHocBulkResult, status_code=status.HTTP_201_CREATED)
def create_to_hop_mon_hoc_bulk(
    payload: list[DmToHopMonHocWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmToHopMonHocBulkResult:
    """Thêm nhiều tổ hợp cùng lúc. Từ chối nếu mã tổ hợp trùng hoặc mã môn học không có trong danh mục."""
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách tổ hợp môn học trống")
    if len(payload) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ thêm tối đa 500 tổ hợp môn học mỗi lần",
        )

    codes = [item.ma_to_hop for item in payload]
    seen: set[str] = set()
    duplicated: list[str] = []
    for code in codes:
        if code in seen and code not in duplicated:
            duplicated.append(code)
        seen.add(code)
    if duplicated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã tổ hợp bị trùng trong dữ liệu: {', '.join(duplicated)}",
        )

    existing = list(
        db.scalars(select(DmToHopMonHoc.ma_to_hop).where(DmToHopMonHoc.ma_to_hop.in_(codes))).all()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã tổ hợp đã tồn tại: {', '.join(existing)}",
        )

    subject_codes: list[str] = []
    subject_seen: set[str] = set()
    for item in payload:
        for code in item.ds_mon_hoc:
            if code not in subject_seen:
                subject_seen.add(code)
                subject_codes.append(code)
    _ensure_mon_hoc_exists(db, subject_codes)

    items = [DmToHopMonHoc(**item.model_dump()) for item in payload]
    db.add_all(items)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã tổ hợp đã tồn tại",
        ) from None
    return DmToHopMonHocBulkResult(created=len(items))


@router.post("", response_model=DmToHopMonHocPublic, status_code=status.HTTP_201_CREATED)
def create_to_hop_mon_hoc(
    payload: DmToHopMonHocWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmToHopMonHoc:
    """Thêm một tổ hợp môn học. Từ chối nếu mã tổ hợp đã tồn tại hoặc mã môn không có trong danh mục."""
    _ensure_mon_hoc_exists(db, payload.ds_mon_hoc)
    item = DmToHopMonHoc(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã tổ hợp đã tồn tại",
        ) from None
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=DmToHopMonHocPublic)
def update_to_hop_mon_hoc(
    item_id: int,
    payload: DmToHopMonHocWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmToHopMonHoc:
    """Cập nhật toàn bộ thông tin một tổ hợp môn học theo id."""
    item = _get_or_404(db, item_id)
    _ensure_mon_hoc_exists(db, payload.ds_mon_hoc)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã tổ hợp đã tồn tại",
        ) from None
    db.refresh(item)
    return item


@router.delete("", response_model=DmToHopMonHocDeleteManyResult)
def delete_to_hop_mon_hoc_many(
    payload: DmToHopMonHocDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmToHopMonHocDeleteManyResult:
    """Xóa nhiều tổ hợp môn học theo danh sách id."""
    items = db.scalars(select(DmToHopMonHoc).where(DmToHopMonHoc.id.in_(payload.ids))).all()
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy tổ hợp môn học để xóa",
        )
    for item in items:
        db.delete(item)
    db.commit()
    return DmToHopMonHocDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_to_hop_mon_hoc(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> None:
    """Xóa một tổ hợp môn học theo id."""
    item = _get_or_404(db, item_id)
    db.delete(item)
    db.commit()
