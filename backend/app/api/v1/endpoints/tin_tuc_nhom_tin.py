from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user
from app.db.session import get_db
from app.models.tin_tuc import TinTucBaiViet, TinTucNhomTin
from app.schemas.tin_tuc import (
    KetQuaXoaNhieu,
    TinTucNhomTinDeleteMany,
    TinTucNhomTinPage,
    TinTucNhomTinPublic,
    TinTucNhomTinWrite,
)

# Quản trị nhóm tin tức (chuyên mục): chỉ admin.
router = APIRouter(prefix="/tin-tuc/nhom-tin", tags=["tin-tuc"], dependencies=[Depends(get_admin_user)])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _get_or_400(db: Session, item_id: int) -> TinTucNhomTin:
    """Lấy một nhóm tin theo id. Trả lỗi 400 kèm thông báo nếu không tồn tại."""
    item = db.get(TinTucNhomTin, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy nhóm tin có id = {item_id}",
        )
    return item


def _dem_bai_viet(db: Session, ids: list[int]) -> dict[int, int]:
    """Số bài viết (mọi trạng thái) của từng nhóm tin."""
    if not ids:
        return {}
    rows = db.execute(
        select(TinTucBaiViet.nhom_tin_tuc_id, func.count())
        .where(TinTucBaiViet.nhom_tin_tuc_id.in_(ids))
        .group_by(TinTucBaiViet.nhom_tin_tuc_id)
    ).all()
    return dict(rows)


def _to_public(item: TinTucNhomTin, so_bai_viet: int) -> TinTucNhomTinPublic:
    return TinTucNhomTinPublic(
        **{ten: getattr(item, ten) for ten in TinTucNhomTinPublic.model_fields if ten != "so_bai_viet"},
        so_bai_viet=so_bai_viet,
    )


def _kiem_tra_trung(db: Session, payload: TinTucNhomTinWrite, bo_qua_id: int | None = None) -> None:
    """Mã nhóm và slug không được trùng với nhóm tin khác."""
    for cot, gia_tri, nhan in (
        (TinTucNhomTin.ma_nhom, payload.ma_nhom, "Mã nhóm"),
        (TinTucNhomTin.slug, payload.slug, "Slug"),
    ):
        query = select(TinTucNhomTin.id).where(cot == gia_tri)
        if bo_qua_id is not None:
            query = query.where(TinTucNhomTin.id != bo_qua_id)
        if db.scalar(query) is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"{nhan} \"{gia_tri}\" đã được dùng cho nhóm tin khác"
            )


@router.get("", response_model=TinTucNhomTinPage)
def list_nhom_tin(
    q: str | None = Query(default=None, max_length=255),
    trang_thai: int | None = Query(default=None, ge=0, le=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
) -> TinTucNhomTinPage:
    """Danh sách nhóm tin có phân trang, lọc theo từ khóa (mã, tên, slug) và trạng thái; xếp theo thứ tự hiển thị."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                TinTucNhomTin.ma_nhom.like(pattern, escape="\\"),
                TinTucNhomTin.ten_nhom.like(pattern, escape="\\"),
                TinTucNhomTin.slug.like(pattern, escape="\\"),
            )
        )
    if trang_thai is not None:
        filters.append(TinTucNhomTin.trang_thai == trang_thai)

    total = db.scalar(select(func.count()).select_from(TinTucNhomTin).where(*filters)) or 0
    items = db.scalars(
        select(TinTucNhomTin)
        .where(*filters)
        .order_by(TinTucNhomTin.thu_tu.asc(), TinTucNhomTin.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    so_bai = _dem_bai_viet(db, [item.id for item in items])
    return TinTucNhomTinPage(
        items=[_to_public(item, so_bai.get(item.id, 0)) for item in items], total=total, page=page, page_size=page_size
    )


@router.get("/{item_id}", response_model=TinTucNhomTinPublic)
def get_nhom_tin(item_id: int, db: Session = Depends(get_db)) -> TinTucNhomTinPublic:
    """Chi tiết một nhóm tin theo id."""
    item = _get_or_400(db, item_id)
    return _to_public(item, _dem_bai_viet(db, [item.id]).get(item.id, 0))


@router.post("", response_model=TinTucNhomTinPublic, status_code=status.HTTP_201_CREATED)
def create_nhom_tin(payload: TinTucNhomTinWrite, db: Session = Depends(get_db)) -> TinTucNhomTinPublic:
    """Thêm nhóm tin. Slug bỏ trống thì tự sinh từ tên nhóm."""
    _kiem_tra_trung(db, payload)
    item = TinTucNhomTin(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return _to_public(item, 0)


@router.put("/{item_id}", response_model=TinTucNhomTinPublic)
def update_nhom_tin(item_id: int, payload: TinTucNhomTinWrite, db: Session = Depends(get_db)) -> TinTucNhomTinPublic:
    """Cập nhật toàn bộ thông tin một nhóm tin."""
    item = _get_or_400(db, item_id)
    _kiem_tra_trung(db, payload, bo_qua_id=item_id)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return _to_public(item, _dem_bai_viet(db, [item.id]).get(item.id, 0))


def _chan_xoa_khi_con_bai(db: Session, items: list[TinTucNhomTin]) -> None:
    """Không xóa nhóm còn bài viết (khóa ngoại RESTRICT): báo rõ nhóm nào còn bao nhiêu bài."""
    so_bai = _dem_bai_viet(db, [item.id for item in items])
    con_bai = [f"{item.ten_nhom} ({so_bai[item.id]} bài)" for item in items if so_bai.get(item.id)]
    if con_bai:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không xóa được nhóm tin còn bài viết: {', '.join(con_bai)}. Hãy chuyển hoặc xóa bài viết trước.",
        )


@router.delete("", response_model=KetQuaXoaNhieu)
def delete_nhom_tin_many(payload: TinTucNhomTinDeleteMany, db: Session = Depends(get_db)) -> KetQuaXoaNhieu:
    """Xóa nhiều nhóm tin theo danh sách id. Id không tồn tại thì bỏ qua; có nhóm còn bài viết thì không xóa nhóm nào."""
    items = list(db.scalars(select(TinTucNhomTin).where(TinTucNhomTin.id.in_(payload.ids))).all())
    _chan_xoa_khi_con_bai(db, items)
    for item in items:
        db.delete(item)
    db.commit()
    return KetQuaXoaNhieu(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_nhom_tin(item_id: int, db: Session = Depends(get_db)) -> None:
    """Xóa một nhóm tin theo id (chỉ khi nhóm không còn bài viết)."""
    item = _get_or_400(db, item_id)
    _chan_xoa_khi_con_bai(db, [item])
    db.delete(item)
    db.commit()
