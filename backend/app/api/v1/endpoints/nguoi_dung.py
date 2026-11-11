from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user
from app.core.security import hash_password
from app.db.session import get_db
from app.models.nguoi_dung import NguoiDung
from app.schemas.nguoi_dung import (
    NguoiDungAdminPublic,
    NguoiDungCreate,
    NguoiDungDeleteMany,
    NguoiDungDeleteManyResult,
    NguoiDungPage,
    NguoiDungUpdate,
)

router = APIRouter(
    prefix="/he-thong/nguoi-dung",
    tags=["he-thong"],
    dependencies=[Depends(get_admin_user)],
)


def _like_pattern(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _get_or_404(db: Session, item_id: int) -> NguoiDung:
    item = db.get(NguoiDung, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy tài khoản")
    return item


def _ensure_unique_contact(
    db: Session,
    *,
    email: str,
    so_dien_thoai: str | None,
    exclude_id: int | None = None,
) -> None:
    email = email.lower().strip()
    filters = [NguoiDung.email == email]
    if so_dien_thoai:
        filters.append(NguoiDung.so_dien_thoai == so_dien_thoai)

    stmt = select(NguoiDung).where(or_(*filters))
    if exclude_id is not None:
        stmt = stmt.where(NguoiDung.id != exclude_id)

    existing = db.scalar(stmt)
    if existing is None:
        return
    if existing.email == email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email đã được sử dụng")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Số điện thoại đã được sử dụng")


@router.get("", response_model=NguoiDungPage)
def list_nguoi_dung(
    q: str | None = Query(default=None, max_length=150),
    vai_tro: int | None = Query(default=None, ge=0, le=1),
    trang_thai: int | None = Query(default=None, ge=0, le=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> NguoiDungPage:
    """Danh sách tài khoản có phân trang. Lọc theo từ khóa, vai trò, trạng thái."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                NguoiDung.ho_ten.like(pattern, escape="\\"),
                NguoiDung.email.like(pattern, escape="\\"),
                NguoiDung.so_dien_thoai.like(pattern, escape="\\"),
            )
        )
    if vai_tro is not None:
        filters.append(NguoiDung.vai_tro == vai_tro)
    if trang_thai is not None:
        filters.append(NguoiDung.trang_thai == trang_thai)

    count_stmt = select(func.count()).select_from(NguoiDung)
    stmt = select(NguoiDung)
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    items = db.scalars(
        stmt.order_by(NguoiDung.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return NguoiDungPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{item_id}", response_model=NguoiDungAdminPublic)
def get_nguoi_dung(item_id: int, db: Session = Depends(get_db)) -> NguoiDung:
    return _get_or_404(db, item_id)


@router.post("", response_model=NguoiDungAdminPublic, status_code=status.HTTP_201_CREATED)
def create_nguoi_dung(payload: NguoiDungCreate, db: Session = Depends(get_db)) -> NguoiDung:
    email = payload.email.lower().strip()
    _ensure_unique_contact(db, email=email, so_dien_thoai=payload.so_dien_thoai)

    item = NguoiDung(
        ho_ten=payload.ho_ten,
        email=email,
        so_dien_thoai=payload.so_dien_thoai,
        mat_khau=hash_password(payload.mat_khau),
        vai_tro=payload.vai_tro,
        trang_thai=payload.trang_thai,
    )
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email hoặc số điện thoại đã được sử dụng",
        ) from None
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=NguoiDungAdminPublic)
def update_nguoi_dung(
    item_id: int,
    payload: NguoiDungUpdate,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_admin_user),
) -> NguoiDung:
    item = _get_or_404(db, item_id)
    email = payload.email.lower().strip()
    _ensure_unique_contact(
        db,
        email=email,
        so_dien_thoai=payload.so_dien_thoai,
        exclude_id=item.id,
    )

    if item.id == current_user.id:
        if payload.vai_tro != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể hạ quyền tài khoản đang đăng nhập",
            )
        if payload.trang_thai != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể khóa tài khoản đang đăng nhập",
            )

    item.ho_ten = payload.ho_ten
    item.email = email
    item.so_dien_thoai = payload.so_dien_thoai
    item.vai_tro = payload.vai_tro
    item.trang_thai = payload.trang_thai
    if payload.mat_khau:
        item.mat_khau = hash_password(payload.mat_khau)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email hoặc số điện thoại đã được sử dụng",
        ) from None
    db.refresh(item)
    return item


@router.delete("", response_model=NguoiDungDeleteManyResult)
def delete_nguoi_dung_many(
    payload: NguoiDungDeleteMany,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_admin_user),
) -> NguoiDungDeleteManyResult:
    if current_user.id in payload.ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa tài khoản đang đăng nhập",
        )

    items = db.scalars(select(NguoiDung).where(NguoiDung.id.in_(payload.ids))).all()
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy tài khoản để xóa",
        )
    for item in items:
        db.delete(item)
    db.commit()
    return NguoiDungDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_nguoi_dung(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_admin_user),
) -> None:
    if item_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa tài khoản đang đăng nhập",
        )
    item = _get_or_404(db, item_id)
    db.delete(item)
    db.commit()
