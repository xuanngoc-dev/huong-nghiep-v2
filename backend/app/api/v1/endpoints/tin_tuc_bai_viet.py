from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user
from app.db.session import get_db
from app.models.tin_tuc import TinTucBaiViet, TinTucNhomTin
from app.schemas.tin_tuc import (
    KetQuaXoaNhieu,
    TinTucBaiVietDeleteMany,
    TinTucBaiVietHienThi,
    TinTucBaiVietPage,
    TinTucBaiVietPublic,
    TinTucBaiVietTomTat,
    TinTucBaiVietWrite,
)

# Quản trị bài viết tin tức: chỉ admin.
router = APIRouter(prefix="/tin-tuc/bai-viet", tags=["tin-tuc"], dependencies=[Depends(get_admin_user)])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _get_or_400(db: Session, item_id: int) -> TinTucBaiViet:
    """Lấy một bài viết theo id. Trả lỗi 400 kèm thông báo nếu không tồn tại."""
    item = db.get(TinTucBaiViet, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy bài viết có id = {item_id}",
        )
    return item


def _nhom_or_400(db: Session, nhom_id: int) -> TinTucNhomTin:
    nhom = db.get(TinTucNhomTin, nhom_id)
    if nhom is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy nhóm tin có id = {nhom_id}",
        )
    return nhom


def _kiem_tra_slug(db: Session, slug: str, bo_qua_id: int | None = None) -> None:
    query = select(TinTucBaiViet.id).where(TinTucBaiViet.slug == slug)
    if bo_qua_id is not None:
        query = query.where(TinTucBaiViet.id != bo_qua_id)
    if db.scalar(query) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Slug \"{slug}\" đã được dùng cho bài viết khác"
        )


def _cot(item: TinTucBaiViet, schema: type, nhom: TinTucNhomTin | None) -> dict:
    return {
        **{ten: getattr(item, ten) for ten in schema.model_fields if ten != "ten_nhom"},
        "ten_nhom": nhom.ten_nhom if nhom else None,
    }


def _to_public(item: TinTucBaiViet, nhom: TinTucNhomTin | None) -> TinTucBaiVietPublic:
    return TinTucBaiVietPublic(**_cot(item, TinTucBaiVietPublic, nhom))


@router.get("", response_model=TinTucBaiVietPage)
def list_bai_viet(
    q: str | None = Query(default=None, max_length=255),
    nhom_tin_tuc_id: int | None = Query(default=None, ge=1),
    trang_thai: int | None = Query(default=None, ge=0, le=1),
    is_noi_bat: int | None = Query(default=None, ge=0, le=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
) -> TinTucBaiVietPage:
    """Danh sách bài viết (không kèm nội dung), lọc theo từ khóa (tiêu đề, slug, tóm tắt, tác giả), nhóm tin,
    trạng thái, nổi bật; mới nhất trước."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                TinTucBaiViet.tieu_de.like(pattern, escape="\\"),
                TinTucBaiViet.slug.like(pattern, escape="\\"),
                TinTucBaiViet.tom_tat.like(pattern, escape="\\"),
                TinTucBaiViet.tac_gia.like(pattern, escape="\\"),
            )
        )
    if nhom_tin_tuc_id is not None:
        filters.append(TinTucBaiViet.nhom_tin_tuc_id == nhom_tin_tuc_id)
    if trang_thai is not None:
        filters.append(TinTucBaiViet.trang_thai == trang_thai)
    if is_noi_bat is not None:
        filters.append(TinTucBaiViet.is_noi_bat == is_noi_bat)

    total = db.scalar(select(func.count()).select_from(TinTucBaiViet).where(*filters)) or 0
    rows = db.execute(
        select(TinTucBaiViet, TinTucNhomTin)
        .join(TinTucNhomTin, TinTucBaiViet.nhom_tin_tuc_id == TinTucNhomTin.id)
        .where(*filters)
        .order_by(TinTucBaiViet.created_at.desc(), TinTucBaiViet.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return TinTucBaiVietPage(
        items=[TinTucBaiVietTomTat(**_cot(item, TinTucBaiVietTomTat, nhom)) for item, nhom in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{item_id}", response_model=TinTucBaiVietPublic)
def get_bai_viet(item_id: int, db: Session = Depends(get_db)) -> TinTucBaiVietPublic:
    """Chi tiết một bài viết (kèm nội dung HTML)."""
    item = _get_or_400(db, item_id)
    return _to_public(item, db.get(TinTucNhomTin, item.nhom_tin_tuc_id))


@router.post("", response_model=TinTucBaiVietPublic, status_code=status.HTTP_201_CREATED)
def create_bai_viet(payload: TinTucBaiVietWrite, db: Session = Depends(get_db)) -> TinTucBaiVietPublic:
    """Thêm bài viết. Slug bỏ trống thì tự sinh từ tiêu đề."""
    nhom = _nhom_or_400(db, payload.nhom_tin_tuc_id)
    _kiem_tra_slug(db, payload.slug)
    item = TinTucBaiViet(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return _to_public(item, nhom)


@router.put("/{item_id}", response_model=TinTucBaiVietPublic)
def update_bai_viet(item_id: int, payload: TinTucBaiVietWrite, db: Session = Depends(get_db)) -> TinTucBaiVietPublic:
    """Cập nhật toàn bộ thông tin một bài viết (lượt xem giữ nguyên)."""
    item = _get_or_400(db, item_id)
    nhom = _nhom_or_400(db, payload.nhom_tin_tuc_id)
    _kiem_tra_slug(db, payload.slug, bo_qua_id=item_id)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return _to_public(item, nhom)


@router.patch("/{item_id}/hien-thi", response_model=TinTucBaiVietPublic)
def update_hien_thi_bai_viet(
    item_id: int, payload: TinTucBaiVietHienThi, db: Session = Depends(get_db)
) -> TinTucBaiVietPublic:
    """Đổi nhanh trạng thái xuất bản và/hoặc nổi bật của một bài viết."""
    item = _get_or_400(db, item_id)
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return _to_public(item, db.get(TinTucNhomTin, item.nhom_tin_tuc_id))


@router.delete("", response_model=KetQuaXoaNhieu)
def delete_bai_viet_many(payload: TinTucBaiVietDeleteMany, db: Session = Depends(get_db)) -> KetQuaXoaNhieu:
    """Xóa nhiều bài viết theo danh sách id. Id không tồn tại thì bỏ qua."""
    items = db.scalars(select(TinTucBaiViet).where(TinTucBaiViet.id.in_(payload.ids))).all()
    for item in items:
        db.delete(item)
    db.commit()
    return KetQuaXoaNhieu(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bai_viet(item_id: int, db: Session = Depends(get_db)) -> None:
    """Xóa một bài viết theo id."""
    db.delete(_get_or_400(db, item_id))
    db.commit()
