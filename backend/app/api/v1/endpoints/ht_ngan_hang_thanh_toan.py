from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, not_, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user
from app.db.session import get_db
from app.models.ht_ngan_hang_thanh_toan import HtNganHangThanhToan
from app.schemas.ht_ngan_hang_thanh_toan import (
    HtNganHangLuaChon,
    HtNganHangThanhToanDeleteMany,
    HtNganHangThanhToanDeleteManyResult,
    HtNganHangThanhToanPage,
    HtNganHangThanhToanPublic,
    HtNganHangThanhToanTrangThai,
    HtNganHangThanhToanWrite,
)

router = APIRouter(
    prefix="/he-thong/ngan-hang-thanh-toan",
    tags=["he-thong"],
    dependencies=[Depends(get_admin_user)],
)

_TRUNG_TAI_KHOAN = "Tài khoản này đã tồn tại ở cùng ngân hàng"


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _get_or_404(db: Session, item_id: int) -> HtNganHangThanhToan:
    """Lấy một bản ghi theo id. Trả lỗi 404 nếu không tồn tại."""
    item = db.get(HtNganHangThanhToan, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy ngân hàng thanh toán")
    return item


@router.get("", response_model=HtNganHangThanhToanPage)
def list_ngan_hang_thanh_toan(
    q: str | None = Query(default=None, max_length=255),
    ngan_hang: str | None = Query(default=None, max_length=50),
    co_logo: bool | None = Query(default=None),
    trang_thai: int | None = Query(default=None, ge=0, le=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> HtNganHangThanhToanPage:
    """Lấy danh sách ngân hàng thanh toán có phân trang.

    Lọc theo từ khóa (tên, viết tắt, số tài khoản, chủ tài khoản), ngân hàng (tên viết tắt),
    có/chưa có logo và trạng thái.
    """
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                HtNganHangThanhToan.ten_ngan_hang.like(pattern, escape="\\"),
                HtNganHangThanhToan.ten_ngan_hang_tieng_anh.like(pattern, escape="\\"),
                HtNganHangThanhToan.ten_ngan_hang_viet_tat.like(pattern, escape="\\"),
                HtNganHangThanhToan.so_tai_khoan.like(pattern, escape="\\"),
                HtNganHangThanhToan.chu_tai_khoan.like(pattern, escape="\\"),
            )
        )
    if ngan_hang and ngan_hang.strip():
        filters.append(HtNganHangThanhToan.ten_ngan_hang_viet_tat == ngan_hang.strip().upper())
    if co_logo is not None:
        co = and_(HtNganHangThanhToan.logo_ngan_hang.is_not(None), HtNganHangThanhToan.logo_ngan_hang != "")
        filters.append(co if co_logo else not_(co))
    if trang_thai is not None:
        filters.append(HtNganHangThanhToan.trang_thai == trang_thai)

    count_stmt = select(func.count()).select_from(HtNganHangThanhToan)
    stmt = select(HtNganHangThanhToan)
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    items = db.scalars(
        stmt.order_by(HtNganHangThanhToan.ten_ngan_hang_viet_tat.asc(), HtNganHangThanhToan.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return HtNganHangThanhToanPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/lua-chon", response_model=list[HtNganHangLuaChon])
def list_lua_chon_ngan_hang(db: Session = Depends(get_db)) -> list[HtNganHangLuaChon]:
    """Các ngân hàng (theo tên viết tắt) đang có trong bảng, dùng cho bộ lọc."""
    rows = db.execute(
        select(HtNganHangThanhToan.ten_ngan_hang_viet_tat, func.min(HtNganHangThanhToan.ten_ngan_hang))
        .group_by(HtNganHangThanhToan.ten_ngan_hang_viet_tat)
        .order_by(HtNganHangThanhToan.ten_ngan_hang_viet_tat.asc())
    ).all()
    return [HtNganHangLuaChon(ten_ngan_hang_viet_tat=ma, ten_ngan_hang=ten) for ma, ten in rows]


@router.get("/{item_id}", response_model=HtNganHangThanhToanPublic)
def get_ngan_hang_thanh_toan(item_id: int, db: Session = Depends(get_db)) -> HtNganHangThanhToan:
    """Lấy chi tiết một ngân hàng thanh toán theo id."""
    return _get_or_404(db, item_id)


@router.post("", response_model=HtNganHangThanhToanPublic, status_code=status.HTTP_201_CREATED)
def create_ngan_hang_thanh_toan(
    payload: HtNganHangThanhToanWrite,
    db: Session = Depends(get_db),
) -> HtNganHangThanhToan:
    """Thêm một tài khoản ngân hàng thanh toán. Từ chối nếu trùng số tài khoản ở cùng ngân hàng."""
    item = HtNganHangThanhToan(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_TRUNG_TAI_KHOAN) from None
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=HtNganHangThanhToanPublic)
def update_ngan_hang_thanh_toan(
    item_id: int,
    payload: HtNganHangThanhToanWrite,
    db: Session = Depends(get_db),
) -> HtNganHangThanhToan:
    """Cập nhật toàn bộ thông tin một ngân hàng thanh toán theo id."""
    item = _get_or_404(db, item_id)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_TRUNG_TAI_KHOAN) from None
    db.refresh(item)
    return item


@router.patch("/{item_id}/trang-thai", response_model=HtNganHangThanhToanPublic)
def update_trang_thai_ngan_hang_thanh_toan(
    item_id: int,
    payload: HtNganHangThanhToanTrangThai,
    db: Session = Depends(get_db),
) -> HtNganHangThanhToan:
    """Bật/tắt nhanh trạng thái hoạt động của một ngân hàng thanh toán."""
    item = _get_or_404(db, item_id)
    item.trang_thai = payload.trang_thai
    db.commit()
    db.refresh(item)
    return item


@router.delete("", response_model=HtNganHangThanhToanDeleteManyResult)
def delete_ngan_hang_thanh_toan_many(
    payload: HtNganHangThanhToanDeleteMany,
    db: Session = Depends(get_db),
) -> HtNganHangThanhToanDeleteManyResult:
    """Xóa nhiều ngân hàng thanh toán theo danh sách id."""
    items = db.scalars(select(HtNganHangThanhToan).where(HtNganHangThanhToan.id.in_(payload.ids))).all()
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy ngân hàng thanh toán để xóa",
        )
    for item in items:
        db.delete(item)
    db.commit()
    return HtNganHangThanhToanDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ngan_hang_thanh_toan(item_id: int, db: Session = Depends(get_db)) -> None:
    """Xóa một ngân hàng thanh toán theo id."""
    item = _get_or_404(db, item_id)
    db.delete(item)
    db.commit()
