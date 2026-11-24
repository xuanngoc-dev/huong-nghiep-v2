from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.tin_tuc import TinTucBaiViet, TinTucNhomTin
from app.schemas.tin_tuc import (
    TinTucBaiVietCongKhai,
    TinTucBaiVietCongKhaiChiTiet,
    TinTucBaiVietCongKhaiPage,
    TinTucNhomTinCongKhai,
)

# Trang tin tức cho khách: không cần đăng nhập. Chỉ bài đã xuất bản (trang_thai = 1) thuộc nhóm đang hiển thị.
router = APIRouter(prefix="/tin-tuc/cong-khai", tags=["tin-tuc"])

SO_BAI_LIEN_QUAN = 4


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _bai_hien_thi():
    """Truy vấn bài viết khách xem được, kèm nhóm tin."""
    return (
        select(TinTucBaiViet, TinTucNhomTin)
        .join(TinTucNhomTin, TinTucBaiViet.nhom_tin_tuc_id == TinTucNhomTin.id)
        .where(TinTucBaiViet.trang_thai == 1, TinTucNhomTin.trang_thai == 1)
    )


def _cot(item: TinTucBaiViet, nhom: TinTucNhomTin, schema: type) -> dict:
    cot = {ten: getattr(item, ten) for ten in schema.model_fields if hasattr(item, ten)}
    return {**cot, "ten_nhom": nhom.ten_nhom, "slug_nhom": nhom.slug}


@router.get("/nhom-tin", response_model=list[TinTucNhomTinCongKhai])
def list_nhom_tin_cong_khai(db: Session = Depends(get_db)) -> list[TinTucNhomTinCongKhai]:
    """Các nhóm tin đang hiển thị theo thứ tự, kèm số bài đã xuất bản. Không cần đăng nhập."""
    so_bai = func.count(TinTucBaiViet.id)
    rows = db.execute(
        select(TinTucNhomTin, so_bai)
        .outerjoin(
            TinTucBaiViet,
            (TinTucBaiViet.nhom_tin_tuc_id == TinTucNhomTin.id) & (TinTucBaiViet.trang_thai == 1),
        )
        .where(TinTucNhomTin.trang_thai == 1)
        .group_by(TinTucNhomTin.id)
        .order_by(TinTucNhomTin.thu_tu.asc(), TinTucNhomTin.id.asc())
    ).all()
    return [
        TinTucNhomTinCongKhai(
            id=nhom.id, ma_nhom=nhom.ma_nhom, ten_nhom=nhom.ten_nhom, slug=nhom.slug, mo_ta=nhom.mo_ta, so_bai_viet=so
        )
        for nhom, so in rows
    ]


@router.get("/bai-viet", response_model=TinTucBaiVietCongKhaiPage)
def list_bai_viet_cong_khai(
    q: str | None = Query(default=None, max_length=255),
    nhom: str | None = Query(default=None, max_length=255, description="Slug nhóm tin"),
    is_noi_bat: int | None = Query(default=None, ge=0, le=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=9, ge=1, le=50),
    db: Session = Depends(get_db),
) -> TinTucBaiVietCongKhaiPage:
    """Danh sách bài đã xuất bản, mới nhất trước; lọc theo từ khóa (tiêu đề, tóm tắt), slug nhóm tin, nổi bật.
    Không cần đăng nhập."""
    query = _bai_hien_thi()
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        query = query.where(
            or_(TinTucBaiViet.tieu_de.like(pattern, escape="\\"), TinTucBaiViet.tom_tat.like(pattern, escape="\\"))
        )
    if nhom:
        query = query.where(TinTucNhomTin.slug == nhom)
    if is_noi_bat is not None:
        query = query.where(TinTucBaiViet.is_noi_bat == is_noi_bat)

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    rows = db.execute(
        query.order_by(TinTucBaiViet.created_at.desc(), TinTucBaiViet.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return TinTucBaiVietCongKhaiPage(
        items=[TinTucBaiVietCongKhai(**_cot(item, n, TinTucBaiVietCongKhai)) for item, n in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/bai-viet/{slug}", response_model=TinTucBaiVietCongKhaiChiTiet)
def get_bai_viet_cong_khai(slug: str, db: Session = Depends(get_db)) -> TinTucBaiVietCongKhaiChiTiet:
    """Chi tiết một bài đã xuất bản theo slug (kèm bài cùng nhóm) và tăng lượt xem. Không cần đăng nhập.
    Bài không tồn tại, chưa xuất bản hoặc thuộc nhóm đang ẩn → 400."""
    row = db.execute(_bai_hien_thi().where(TinTucBaiViet.slug == slug)).first()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy bài viết có slug = {slug}",
        )
    item, nhom = row
    # Tăng bằng câu UPDATE để các lượt xem đồng thời không ghi đè nhau.
    db.execute(
        update(TinTucBaiViet).where(TinTucBaiViet.id == item.id).values(luot_xem=TinTucBaiViet.luot_xem + 1)
    )
    db.commit()
    db.refresh(item)

    lien_quan = db.execute(
        _bai_hien_thi()
        .where(TinTucBaiViet.nhom_tin_tuc_id == item.nhom_tin_tuc_id, TinTucBaiViet.id != item.id)
        .order_by(TinTucBaiViet.created_at.desc(), TinTucBaiViet.id.desc())
        .limit(SO_BAI_LIEN_QUAN)
    ).all()
    return TinTucBaiVietCongKhaiChiTiet(
        **_cot(item, nhom, TinTucBaiVietCongKhaiChiTiet),
        bai_lien_quan=[TinTucBaiVietCongKhai(**_cot(b, n, TinTucBaiVietCongKhai)) for b, n in lien_quan],
    )
