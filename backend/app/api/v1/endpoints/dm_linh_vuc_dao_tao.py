from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.dm_linh_vuc_dao_tao import DmLinhVucDaoTao
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_linh_vuc_dao_tao import (
    DmLinhVucDaoTaoBulkResult,
    DmLinhVucDaoTaoDeleteMany,
    DmLinhVucDaoTaoDeleteManyResult,
    DmLinhVucDaoTaoPage,
    DmLinhVucDaoTaoPublic,
    DmLinhVucDaoTaoWrite,
)

router = APIRouter(prefix="/danh-muc/linh-vuc-dao-tao", tags=["danh-muc"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _integrity_detail(exc: IntegrityError, duplicate: str, related: str) -> str:
    """Chọn thông báo khi ràng buộc CSDL bị vi phạm: mã trùng hoặc còn dữ liệu con."""
    text = str(getattr(exc, "orig", exc)).lower()
    if "foreign key" in text or "1451" in text or "1452" in text:
        return related
    return duplicate


def _get_or_404(db: Session, item_id: int) -> DmLinhVucDaoTao:
    """Lấy một lĩnh vực đào tạo theo id. Trả lỗi 404 nếu không tồn tại."""
    item = db.get(DmLinhVucDaoTao, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy lĩnh vực đào tạo")
    return item


@router.get("", response_model=DmLinhVucDaoTaoPage)
def list_linh_vuc_dao_tao(
    q: str | None = Query(default=None, max_length=255),
    trang_thai: int | None = Query(default=None, ge=0, le=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmLinhVucDaoTaoPage:
    """Lấy danh sách lĩnh vực đào tạo có phân trang. Lọc theo từ khóa (tên, mã, tên tiếng Anh) và trạng thái."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmLinhVucDaoTao.ten_linh_vuc.like(pattern, escape="\\"),
                DmLinhVucDaoTao.ma_linh_vuc.like(pattern, escape="\\"),
                DmLinhVucDaoTao.ten_tieng_anh.like(pattern, escape="\\"),
            )
        )
    if trang_thai is not None:
        filters.append(DmLinhVucDaoTao.trang_thai == trang_thai)

    count_stmt = select(func.count()).select_from(DmLinhVucDaoTao)
    stmt = select(DmLinhVucDaoTao)
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    items = db.scalars(
        stmt.order_by(DmLinhVucDaoTao.ma_linh_vuc.asc(), DmLinhVucDaoTao.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmLinhVucDaoTaoPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{item_id}", response_model=DmLinhVucDaoTaoPublic)
def get_linh_vuc_dao_tao(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmLinhVucDaoTao:
    """Lấy chi tiết một lĩnh vực đào tạo theo id."""
    return _get_or_404(db, item_id)


@router.post("/bulk", response_model=DmLinhVucDaoTaoBulkResult, status_code=status.HTTP_201_CREATED)
def create_linh_vuc_dao_tao_bulk(
    payload: list[DmLinhVucDaoTaoWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmLinhVucDaoTaoBulkResult:
    """Thêm nhiều lĩnh vực cùng lúc. Từ chối nếu mã lĩnh vực trùng trong dữ liệu gửi lên hoặc đã có trong hệ thống."""
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách lĩnh vực trống")
    if len(payload) > 500:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chỉ thêm tối đa 500 lĩnh vực mỗi lần")

    codes = [item.ma_linh_vuc for item in payload]
    seen: set[str] = set()
    duplicated: list[str] = []
    for code in codes:
        if code in seen and code not in duplicated:
            duplicated.append(code)
        seen.add(code)
    if duplicated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã lĩnh vực bị trùng trong dữ liệu: {', '.join(duplicated)}",
        )

    existing = list(
        db.scalars(select(DmLinhVucDaoTao.ma_linh_vuc).where(DmLinhVucDaoTao.ma_linh_vuc.in_(codes))).all()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã lĩnh vực đã tồn tại: {', '.join(existing)}",
        )

    items = [DmLinhVucDaoTao(**item.model_dump()) for item in payload]
    db.add_all(items)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_integrity_detail(exc, "Mã lĩnh vực đã tồn tại", "Không thể thêm lĩnh vực"),
        ) from None
    return DmLinhVucDaoTaoBulkResult(created=len(items))


@router.post("", response_model=DmLinhVucDaoTaoPublic, status_code=status.HTTP_201_CREATED)
def create_linh_vuc_dao_tao(
    payload: DmLinhVucDaoTaoWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmLinhVucDaoTao:
    """Thêm một lĩnh vực đào tạo. Từ chối nếu mã lĩnh vực đã tồn tại."""
    item = DmLinhVucDaoTao(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_integrity_detail(exc, "Mã lĩnh vực đã tồn tại", "Không thể thêm lĩnh vực"),
        ) from None
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=DmLinhVucDaoTaoPublic)
def update_linh_vuc_dao_tao(
    item_id: int,
    payload: DmLinhVucDaoTaoWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmLinhVucDaoTao:
    """Cập nhật toàn bộ thông tin một lĩnh vực đào tạo theo id."""
    item = _get_or_404(db, item_id)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_integrity_detail(exc, "Mã lĩnh vực đã tồn tại", "Không thể cập nhật lĩnh vực"),
        ) from None
    db.refresh(item)
    return item


@router.delete("", response_model=DmLinhVucDaoTaoDeleteManyResult)
def delete_linh_vuc_dao_tao_many(
    payload: DmLinhVucDaoTaoDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmLinhVucDaoTaoDeleteManyResult:
    """Xóa nhiều lĩnh vực đào tạo theo danh sách id. Từ chối nếu còn nhóm ngành thuộc các lĩnh vực đó."""
    items = db.scalars(select(DmLinhVucDaoTao).where(DmLinhVucDaoTao.id.in_(payload.ids))).all()
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy lĩnh vực đào tạo để xóa")
    for item in items:
        db.delete(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa vì còn nhóm ngành thuộc lĩnh vực này",
        ) from None
    return DmLinhVucDaoTaoDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_linh_vuc_dao_tao(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> None:
    """Xóa một lĩnh vực đào tạo theo id. Từ chối nếu còn nhóm ngành thuộc lĩnh vực đó."""
    item = _get_or_404(db, item_id)
    db.delete(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa vì còn nhóm ngành thuộc lĩnh vực này",
        ) from None
