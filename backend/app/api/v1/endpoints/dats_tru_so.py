from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.dats_tru_so import DatsTruSo
from app.models.dats_tuyen_sinh import DatsTuyenSinh
from app.models.dm_truong import DmTruong
from app.models.nguoi_dung import NguoiDung
from app.schemas.dats_tru_so import (
    DatsTruSoDeleteMany,
    DatsTruSoDeleteManyResult,
    DatsTruSoFields,
    DatsTruSoImportRequest,
    DatsTruSoImportResult,
    DatsTruSoPage,
    DatsTruSoPublic,
    DatsTruSoWrite,
)

router = APIRouter(prefix="/tru-so", tags=["tru-so"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _to_public(item: DatsTruSo, de_an: DatsTuyenSinh, truong: DmTruong) -> DatsTruSoPublic:
    """Ghép trụ sở với đề án và trường để trả về cho client."""
    return DatsTruSoPublic(
        id=item.id,
        de_an_id=item.de_an_id,
        ten_de_an=de_an.ten_de_an,
        truong_id=de_an.truong_id,
        ma_truong=truong.ma_truong or "",
        ten_truong=truong.ten_truong,
        nam_tuyen_sinh=de_an.nam_tuyen_sinh,
        vai_tro=item.vai_tro,
        ten_co_so=item.ten_co_so,
        loai_co_so=item.loai_co_so,
        dia_chi=item.dia_chi,
        so_dien_thoai=item.so_dien_thoai,
        ghi_chu=item.ghi_chu,
    )


def _joined():
    return (
        select(DatsTruSo, DatsTuyenSinh, DmTruong)
        .join(DatsTuyenSinh, DatsTruSo.de_an_id == DatsTuyenSinh.id)
        .join(DmTruong, DatsTuyenSinh.truong_id == DmTruong.id)
    )


def _load_row(db: Session, item_id: int):
    """Lấy một trụ sở kèm đề án và trường. Trả lỗi 404 nếu không có."""
    row = db.execute(_joined().where(DatsTruSo.id == item_id)).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy trụ sở")
    return row[0], row[1], row[2]


def _ensure_de_an(db: Session, de_an_id: int) -> DatsTuyenSinh:
    de_an = db.get(DatsTuyenSinh, de_an_id)
    if de_an is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Đề án tuyển sinh không tồn tại")
    return de_an


def _apply(item: DatsTruSo, de_an_id: int, payload: DatsTruSoFields) -> None:
    """Gán dữ liệu vào bản ghi. de_an_id luôn lấy từ đề án đã chọn, không lấy từ JSON."""
    item.de_an_id = de_an_id
    for key, value in payload.model_dump().items():
        setattr(item, key, value)


@router.get("", response_model=DatsTruSoPage)
def list_tru_so(
    q: str | None = Query(default=None, max_length=255),
    nam_tuyen_sinh: int | None = Query(default=None, ge=1990, le=2100),
    truong_id: int | None = Query(default=None, ge=1),
    de_an_id: int | None = Query(default=None, ge=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsTruSoPage:
    """Lấy danh sách trụ sở có phân trang. Lọc theo từ khóa, trường, năm và đề án."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DatsTruSo.ten_co_so.like(pattern, escape="\\"),
                DatsTruSo.dia_chi.like(pattern, escape="\\"),
                DatsTruSo.so_dien_thoai.like(pattern, escape="\\"),
                DatsTruSo.vai_tro.like(pattern, escape="\\"),
                DatsTruSo.loai_co_so.like(pattern, escape="\\"),
                DatsTruSo.ghi_chu.like(pattern, escape="\\"),
                DatsTuyenSinh.ten_de_an.like(pattern, escape="\\"),
                DmTruong.ten_truong.like(pattern, escape="\\"),
                DmTruong.ma_truong.like(pattern, escape="\\"),
                cast(DatsTuyenSinh.nam_tuyen_sinh, String).like(pattern, escape="\\"),
            )
        )
    if nam_tuyen_sinh is not None:
        filters.append(DatsTuyenSinh.nam_tuyen_sinh == nam_tuyen_sinh)
    if truong_id is not None:
        filters.append(DatsTuyenSinh.truong_id == truong_id)
    if de_an_id is not None:
        filters.append(DatsTruSo.de_an_id == de_an_id)

    joined = DatsTruSo.__table__.join(DatsTuyenSinh, DatsTruSo.de_an_id == DatsTuyenSinh.id).join(
        DmTruong, DatsTuyenSinh.truong_id == DmTruong.id
    )
    count_stmt = select(func.count()).select_from(joined)
    stmt = _joined()
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    rows = db.execute(
        stmt.order_by(
            DatsTuyenSinh.nam_tuyen_sinh.desc(),
            DmTruong.ten_truong.asc(),
            DatsTruSo.ten_co_so.asc(),
            DatsTruSo.id.desc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DatsTruSoPage(
        items=[_to_public(item, de_an, truong) for item, de_an, truong in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{item_id}", response_model=DatsTruSoPublic)
def get_tru_so(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsTruSoPublic:
    """Lấy chi tiết một trụ sở theo id."""
    return _to_public(*_load_row(db, item_id))


@router.post("/import", response_model=DatsTruSoImportResult, status_code=status.HTTP_201_CREATED)
def import_tru_so(
    payload: DatsTruSoImportRequest,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsTruSoImportResult:
    """Nhập một mảng trụ sở vào đúng đề án đã chọn. id trong JSON không được lưu."""
    _ensure_de_an(db, payload.de_an_id)
    items = []
    for data in payload.du_lieu:
        item = DatsTruSo()
        _apply(item, payload.de_an_id, data)
        items.append(item)
    db.add_all(items)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không lưu được trụ sở") from None
    return DatsTruSoImportResult(created=len(items))


@router.post("", response_model=DatsTruSoPublic, status_code=status.HTTP_201_CREATED)
def create_tru_so(
    payload: DatsTruSoWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsTruSoPublic:
    """Thêm một trụ sở vào đề án đã chọn."""
    _ensure_de_an(db, payload.de_an_id)
    item = DatsTruSo()
    _apply(item, payload.de_an_id, payload)
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không lưu được trụ sở") from None
    db.refresh(item)
    return _to_public(*_load_row(db, item.id))


@router.put("/{item_id}", response_model=DatsTruSoPublic)
def update_tru_so(
    item_id: int,
    payload: DatsTruSoWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsTruSoPublic:
    """Cập nhật một trụ sở. Có thể chuyển sang đề án khác."""
    item, _de_an, _truong = _load_row(db, item_id)
    _ensure_de_an(db, payload.de_an_id)
    _apply(item, payload.de_an_id, payload)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không lưu được trụ sở") from None
    return _to_public(*_load_row(db, item_id))


@router.delete("", response_model=DatsTruSoDeleteManyResult)
def delete_tru_so_many(
    payload: DatsTruSoDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsTruSoDeleteManyResult:
    """Xóa nhiều trụ sở theo danh sách id."""
    items = db.scalars(select(DatsTruSo).where(DatsTruSo.id.in_(payload.ids))).all()
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy trụ sở để xóa")
    for item in items:
        db.delete(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trụ sở đang được sử dụng, không thể xóa",
        ) from None
    return DatsTruSoDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tru_so(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> None:
    """Xóa một trụ sở theo id."""
    item, _de_an, _truong = _load_row(db, item_id)
    db.delete(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trụ sở đang được sử dụng, không thể xóa",
        ) from None
