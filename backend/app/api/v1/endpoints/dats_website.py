from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.dats_tuyen_sinh import DatsTuyenSinh
from app.models.dats_website import DatsWebsite
from app.models.dm_truong import DmTruong
from app.models.nguoi_dung import NguoiDung
from app.schemas.dats_website import (
    DatsWebsiteDeleteMany,
    DatsWebsiteDeleteManyResult,
    DatsWebsiteFields,
    DatsWebsiteImportRequest,
    DatsWebsiteImportResult,
    DatsWebsitePage,
    DatsWebsitePublic,
    DatsWebsiteWrite,
)

router = APIRouter(prefix="/website", tags=["website"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _to_public(item: DatsWebsite, de_an: DatsTuyenSinh, truong: DmTruong) -> DatsWebsitePublic:
    """Ghép website với đề án và trường để trả về cho client."""
    return DatsWebsitePublic(
        id=item.id,
        de_an_id=item.de_an_id,
        ten_de_an=de_an.ten_de_an,
        truong_id=truong.id,
        ma_truong=truong.ma_truong or "",
        ten_truong=truong.ten_truong,
        nam_tuyen_sinh=de_an.nam_tuyen_sinh,
        loai_website=item.loai_website,
        ten_trang=item.ten_trang,
        url=item.url,
        ghi_chu=item.ghi_chu,
    )


def _joined():
    return (
        select(DatsWebsite, DatsTuyenSinh, DmTruong)
        .join(DatsTuyenSinh, DatsWebsite.de_an_id == DatsTuyenSinh.id)
        .join(DmTruong, DatsTuyenSinh.ma_truong == DmTruong.ma_truong)
    )


def _load_row(db: Session, item_id: int):
    """Lấy một website kèm đề án và trường. Trả lỗi 404 nếu không có."""
    row = db.execute(_joined().where(DatsWebsite.id == item_id)).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy website")
    return row[0], row[1], row[2]


def _ensure_de_an(db: Session, de_an_id: int) -> DatsTuyenSinh:
    de_an = db.get(DatsTuyenSinh, de_an_id)
    if de_an is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Đề án tuyển sinh không tồn tại")
    return de_an


def _apply(item: DatsWebsite, de_an_id: int, payload: DatsWebsiteFields) -> None:
    """Gán dữ liệu vào bản ghi. de_an_id luôn lấy từ đề án đã chọn, không lấy từ JSON."""
    item.de_an_id = de_an_id
    for key, value in payload.model_dump().items():
        setattr(item, key, value)


@router.get("", response_model=DatsWebsitePage)
def list_website(
    q: str | None = Query(default=None, max_length=255),
    nam_tuyen_sinh: int | None = Query(default=None, ge=1990, le=2100),
    ma_truong: str | None = Query(default=None, max_length=20),
    de_an_id: int | None = Query(default=None, ge=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsWebsitePage:
    """Lấy danh sách website có phân trang. Lọc theo từ khóa, trường, năm và đề án."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DatsWebsite.ten_trang.like(pattern, escape="\\"),
                DatsWebsite.url.like(pattern, escape="\\"),
                DatsWebsite.loai_website.like(pattern, escape="\\"),
                DatsWebsite.ghi_chu.like(pattern, escape="\\"),
                DatsTuyenSinh.ten_de_an.like(pattern, escape="\\"),
                DmTruong.ten_truong.like(pattern, escape="\\"),
                DmTruong.ma_truong.like(pattern, escape="\\"),
                cast(DatsTuyenSinh.nam_tuyen_sinh, String).like(pattern, escape="\\"),
            )
        )
    if nam_tuyen_sinh is not None:
        filters.append(DatsTuyenSinh.nam_tuyen_sinh == nam_tuyen_sinh)
    if ma_truong and ma_truong.strip():
        filters.append(DatsTuyenSinh.ma_truong == ma_truong.strip())
    if de_an_id is not None:
        filters.append(DatsWebsite.de_an_id == de_an_id)

    joined = DatsWebsite.__table__.join(DatsTuyenSinh, DatsWebsite.de_an_id == DatsTuyenSinh.id).join(
        DmTruong, DatsTuyenSinh.ma_truong == DmTruong.ma_truong
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
            DatsWebsite.ten_trang.asc(),
            DatsWebsite.id.desc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DatsWebsitePage(
        items=[_to_public(item, de_an, truong) for item, de_an, truong in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{item_id}", response_model=DatsWebsitePublic)
def get_website(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsWebsitePublic:
    """Lấy chi tiết một website theo id."""
    return _to_public(*_load_row(db, item_id))


@router.post("/import", response_model=DatsWebsiteImportResult, status_code=status.HTTP_201_CREATED)
def import_website(
    payload: DatsWebsiteImportRequest,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsWebsiteImportResult:
    """Nhập một mảng website vào đúng đề án đã chọn. id trong JSON không được lưu."""
    _ensure_de_an(db, payload.de_an_id)
    items = []
    for data in payload.du_lieu:
        item = DatsWebsite()
        _apply(item, payload.de_an_id, data)
        items.append(item)
    db.add_all(items)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không lưu được website") from None
    return DatsWebsiteImportResult(created=len(items))


@router.post("", response_model=DatsWebsitePublic, status_code=status.HTTP_201_CREATED)
def create_website(
    payload: DatsWebsiteWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsWebsitePublic:
    """Thêm một website vào đề án đã chọn."""
    _ensure_de_an(db, payload.de_an_id)
    item = DatsWebsite()
    _apply(item, payload.de_an_id, payload)
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không lưu được website") from None
    db.refresh(item)
    return _to_public(*_load_row(db, item.id))


@router.put("/{item_id}", response_model=DatsWebsitePublic)
def update_website(
    item_id: int,
    payload: DatsWebsiteWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsWebsitePublic:
    """Cập nhật một website. Có thể chuyển sang đề án khác."""
    item, _de_an, _truong = _load_row(db, item_id)
    _ensure_de_an(db, payload.de_an_id)
    _apply(item, payload.de_an_id, payload)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không lưu được website") from None
    return _to_public(*_load_row(db, item_id))


@router.delete("", response_model=DatsWebsiteDeleteManyResult)
def delete_website_many(
    payload: DatsWebsiteDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsWebsiteDeleteManyResult:
    """Xóa nhiều website theo danh sách id."""
    items = db.scalars(select(DatsWebsite).where(DatsWebsite.id.in_(payload.ids))).all()
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy website để xóa")
    for item in items:
        db.delete(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Website đang được sử dụng, không thể xóa",
        ) from None
    return DatsWebsiteDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_website(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> None:
    """Xóa một website theo id."""
    item, _de_an, _truong = _load_row(db, item_id)
    db.delete(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Website đang được sử dụng, không thể xóa",
        ) from None
