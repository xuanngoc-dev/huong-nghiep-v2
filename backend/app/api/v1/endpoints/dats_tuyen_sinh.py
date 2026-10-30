from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.dats_tuyen_sinh import DatsTuyenSinh
from app.models.dm_truong import DmTruong
from app.models.nguoi_dung import NguoiDung
from app.schemas.dats_tuyen_sinh import (
    DatsImportRequest,
    DatsImportResult,
    DatsTuyenSinhBulkResult,
    DatsTuyenSinhDeleteMany,
    DatsTuyenSinhDeleteManyResult,
    DatsTuyenSinhPage,
    DatsTuyenSinhPublic,
    DatsTuyenSinhWrite,
)
from app.services.dats_import import DatsImportError, import_document

router = APIRouter(prefix="/de-an-tuyen-sinh", tags=["de-an-tuyen-sinh"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _to_public(item: DatsTuyenSinh, truong: DmTruong) -> DatsTuyenSinhPublic:
    """Ghép đề án với mã và tên trường để trả về cho client."""
    return DatsTuyenSinhPublic(
        id=item.id,
        truong_id=item.truong_id,
        ma_truong=truong.ma_truong,
        ten_truong=truong.ten_truong,
        nam_tuyen_sinh=item.nam_tuyen_sinh,
        chi_tieu=item.chi_tieu,
        ten_de_an=item.ten_de_an,
        hinh_thuc_dao_tao=item.hinh_thuc_dao_tao if isinstance(item.hinh_thuc_dao_tao, list) else None,
        gioi_thieu=item.gioi_thieu,
        ngay_cong_bo=item.ngay_cong_bo,
        nguon_du_lieu_url=item.nguon_du_lieu_url,
        trang_thai=item.trang_thai,
        ghi_chu=item.ghi_chu,
        tao_luc=item.tao_luc,
        cap_nhat_luc=item.cap_nhat_luc,
    )


def _ensure_truong(db: Session, ids: list[int]) -> None:
    """Kiểm tra mọi trường trong danh sách đều tồn tại."""
    unique = list(dict.fromkeys(ids))
    found = set(db.scalars(select(DmTruong.id).where(DmTruong.id.in_(unique))).all())
    missing = [str(item_id) for item_id in unique if item_id not in found]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trường học không tồn tại: {', '.join(missing)}",
        )


def _apply(item: DatsTuyenSinh, payload: DatsTuyenSinhWrite, *, creating: bool) -> None:
    """Gán dữ liệu form vào bản ghi và cập nhật mốc thời gian."""
    now = datetime.now()
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    if creating:
        item.tao_luc = now
    item.cap_nhat_luc = now


def _load_pair(db: Session, item_id: int) -> tuple[DatsTuyenSinh, DmTruong]:
    """Lấy một đề án kèm trường. Trả lỗi 404 nếu đề án không tồn tại."""
    row = db.execute(
        select(DatsTuyenSinh, DmTruong)
        .join(DmTruong, DatsTuyenSinh.truong_id == DmTruong.id)
        .where(DatsTuyenSinh.id == item_id)
    ).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy đề án tuyển sinh")
    return row[0], row[1]


@router.get("", response_model=DatsTuyenSinhPage)
def list_de_an(
    q: str | None = Query(default=None, max_length=255),
    trang_thai: str | None = Query(default=None, max_length=20),
    nam_tuyen_sinh: int | None = Query(default=None, ge=1990, le=2100),
    truong_id: int | None = Query(default=None, ge=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsTuyenSinhPage:
    """Lấy danh sách đề án tuyển sinh có phân trang. Lọc theo từ khóa, trường, năm và trạng thái."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DatsTuyenSinh.ten_de_an.like(pattern, escape="\\"),
                DmTruong.ten_truong.like(pattern, escape="\\"),
                DmTruong.ma_truong.like(pattern, escape="\\"),
                cast(DatsTuyenSinh.nam_tuyen_sinh, String).like(pattern, escape="\\"),
            )
        )
    if trang_thai and trang_thai.strip():
        filters.append(DatsTuyenSinh.trang_thai == trang_thai.strip())
    if nam_tuyen_sinh is not None:
        filters.append(DatsTuyenSinh.nam_tuyen_sinh == nam_tuyen_sinh)
    if truong_id is not None:
        filters.append(DatsTuyenSinh.truong_id == truong_id)

    joined = DatsTuyenSinh.__table__.join(DmTruong, DatsTuyenSinh.truong_id == DmTruong.id)
    count_stmt = select(func.count()).select_from(joined)
    stmt = select(DatsTuyenSinh, DmTruong).join(DmTruong, DatsTuyenSinh.truong_id == DmTruong.id)
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    rows = db.execute(
        stmt.order_by(
            DatsTuyenSinh.nam_tuyen_sinh.desc(),
            DmTruong.ten_truong.asc(),
            DatsTuyenSinh.id.desc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DatsTuyenSinhPage(
        items=[_to_public(item, truong) for item, truong in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{item_id}", response_model=DatsTuyenSinhPublic)
def get_de_an(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsTuyenSinhPublic:
    """Lấy chi tiết một đề án tuyển sinh theo id, kèm tên trường."""
    item, truong = _load_pair(db, item_id)
    return _to_public(item, truong)


@router.post("/bulk", response_model=DatsTuyenSinhBulkResult, status_code=status.HTTP_201_CREATED)
def create_de_an_bulk(
    payload: list[DatsTuyenSinhWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsTuyenSinhBulkResult:
    """Thêm nhiều đề án cùng lúc. Từ chối nếu trường học không tồn tại."""
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách đề án tuyển sinh trống")
    if len(payload) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ thêm tối đa 500 đề án tuyển sinh mỗi lần",
        )

    _ensure_truong(db, [item.truong_id for item in payload])
    items = []
    for data in payload:
        item = DatsTuyenSinh()
        _apply(item, data, creating=True)
        items.append(item)
    db.add_all(items)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không lưu được đề án tuyển sinh",
        ) from None
    return DatsTuyenSinhBulkResult(created=len(items))


@router.post("/import", response_model=DatsImportResult, status_code=status.HTTP_201_CREATED)
def import_de_an(
    payload: DatsImportRequest,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsImportResult:
    """Nhập một đề án và các bảng dats_ trong cùng file JSON."""
    try:
        de_an_id, counts = import_document(db, payload.truong_id, payload.nam_tuyen_sinh, payload.du_lieu)
        db.commit()
    except DatsImportError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from None
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không lưu được dữ liệu đề án",
        ) from None
    return DatsImportResult(de_an_id=de_an_id, counts=counts)


@router.post("", response_model=DatsTuyenSinhPublic, status_code=status.HTTP_201_CREATED)
def create_de_an(
    payload: DatsTuyenSinhWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsTuyenSinhPublic:
    """Thêm một đề án tuyển sinh. Từ chối nếu trường học không tồn tại."""
    _ensure_truong(db, [payload.truong_id])
    item = DatsTuyenSinh()
    _apply(item, payload, creating=True)
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không lưu được đề án tuyển sinh",
        ) from None
    db.refresh(item)
    truong = db.get(DmTruong, item.truong_id)
    return _to_public(item, truong)


@router.put("/{item_id}", response_model=DatsTuyenSinhPublic)
def update_de_an(
    item_id: int,
    payload: DatsTuyenSinhWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsTuyenSinhPublic:
    """Cập nhật toàn bộ thông tin một đề án tuyển sinh theo id."""
    item, _truong = _load_pair(db, item_id)
    _ensure_truong(db, [payload.truong_id])
    _apply(item, payload, creating=False)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không lưu được đề án tuyển sinh",
        ) from None
    db.refresh(item)
    truong = db.get(DmTruong, item.truong_id)
    return _to_public(item, truong)


@router.delete("", response_model=DatsTuyenSinhDeleteManyResult)
def delete_de_an_many(
    payload: DatsTuyenSinhDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsTuyenSinhDeleteManyResult:
    """Xóa nhiều đề án tuyển sinh theo danh sách id."""
    items = db.scalars(select(DatsTuyenSinh).where(DatsTuyenSinh.id.in_(payload.ids))).all()
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy đề án tuyển sinh để xóa",
        )
    for item in items:
        db.delete(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Đề án đang được sử dụng, không thể xóa",
        ) from None
    return DatsTuyenSinhDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_de_an(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> None:
    """Xóa một đề án tuyển sinh theo id."""
    item, _truong = _load_pair(db, item_id)
    db.delete(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Đề án đang được sử dụng, không thể xóa",
        ) from None
