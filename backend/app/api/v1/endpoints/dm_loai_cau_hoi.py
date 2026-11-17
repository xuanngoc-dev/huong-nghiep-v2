from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_current_user
from app.db.session import get_db
from app.models.dm_loai_cau_hoi import DmLoaiCauHoi
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_loai_cau_hoi import (
    DmLoaiCauHoiAnhHuongXoa,
    DmLoaiCauHoiBulkResult,
    DmLoaiCauHoiDeleteMany,
    DmLoaiCauHoiDeleteManyResult,
    DmLoaiCauHoiPage,
    DmLoaiCauHoiPublic,
    DmLoaiCauHoiWrite,
)
from app.services import xoa_loai_cau_hoi

router = APIRouter(prefix="/danh-muc/loai-cau-hoi", tags=["danh-muc"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _get_or_400(db: Session, item_id: int) -> DmLoaiCauHoi:
    """Lấy một loại câu hỏi theo id. Trả lỗi 400 kèm thông báo nếu không tồn tại."""
    item = db.get(DmLoaiCauHoi, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy loại câu hỏi có id = {item_id}",
        )
    return item


@router.get("", response_model=DmLoaiCauHoiPage)
def list_loai_cau_hoi(
    q: str | None = Query(default=None, max_length=150),
    trang_thai: int | None = Query(default=None, ge=0, le=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> DmLoaiCauHoiPage:
    """Lấy danh sách loại câu hỏi có phân trang, sắp theo thứ tự ưu tiên. Lọc theo tên và trạng thái. Không cần đăng nhập."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(DmLoaiCauHoi.ten_loai_cau_hoi.like(pattern, escape="\\"))
    if trang_thai is not None:
        filters.append(DmLoaiCauHoi.trang_thai == trang_thai)

    count_stmt = select(func.count()).select_from(DmLoaiCauHoi)
    stmt = select(DmLoaiCauHoi)
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    items = db.scalars(
        stmt.order_by(DmLoaiCauHoi.thu_tu_uu_tien.asc(), DmLoaiCauHoi.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmLoaiCauHoiPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{item_id}", response_model=DmLoaiCauHoiPublic)
def get_loai_cau_hoi(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmLoaiCauHoi:
    """Lấy chi tiết một loại câu hỏi theo id."""
    return _get_or_400(db, item_id)


@router.post("/bulk", response_model=DmLoaiCauHoiBulkResult, status_code=status.HTTP_201_CREATED)
def create_loai_cau_hoi_bulk(
    payload: list[DmLoaiCauHoiWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmLoaiCauHoiBulkResult:
    """Thêm nhiều loại câu hỏi cùng lúc. Từ chối nếu thứ tự ưu tiên trùng trong dữ liệu hoặc đã có trong hệ thống."""
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách loại câu hỏi trống")
    if len(payload) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ thêm tối đa 500 loại câu hỏi mỗi lần",
        )

    orders = [item.thu_tu_uu_tien for item in payload]
    seen: set[int] = set()
    duplicated: list[str] = []
    for order in orders:
        if order in seen and str(order) not in duplicated:
            duplicated.append(str(order))
        seen.add(order)
    if duplicated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Thứ tự ưu tiên bị trùng trong dữ liệu: {', '.join(duplicated)}",
        )

    existing = list(
        db.scalars(select(DmLoaiCauHoi.thu_tu_uu_tien).where(DmLoaiCauHoi.thu_tu_uu_tien.in_(orders))).all()
    )
    if existing:
        joined = ", ".join(str(item) for item in existing)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Thứ tự ưu tiên đã tồn tại: {joined}",
        )

    items = [DmLoaiCauHoi(**item.model_dump()) for item in payload]
    db.add_all(items)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thứ tự ưu tiên đã tồn tại",
        ) from None
    return DmLoaiCauHoiBulkResult(created=len(items))


@router.post("", response_model=DmLoaiCauHoiPublic, status_code=status.HTTP_201_CREATED)
def create_loai_cau_hoi(
    payload: DmLoaiCauHoiWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmLoaiCauHoi:
    """Thêm một loại câu hỏi. Từ chối nếu thứ tự ưu tiên đã tồn tại."""
    item = DmLoaiCauHoi(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thứ tự ưu tiên đã tồn tại",
        ) from None
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=DmLoaiCauHoiPublic)
def update_loai_cau_hoi(
    item_id: int,
    payload: DmLoaiCauHoiWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmLoaiCauHoi:
    """Cập nhật toàn bộ thông tin một loại câu hỏi theo id."""
    item = _get_or_400(db, item_id)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thứ tự ưu tiên đã tồn tại",
        ) from None
    db.refresh(item)
    return item


def _chan_neu_con_lien_quan(db: Session, ids: list[int]) -> None:
    """Còn câu hỏi hoặc phiên khảo sát dùng loại này thì trả 400 nêu số lượng (xóa kèm bằng xoa_lien_quan=true)."""
    anh_huong = xoa_loai_cau_hoi.anh_huong(db, ids)
    if anh_huong["so_cau_hoi"] or anh_huong["so_phien"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Không thể xóa vì còn {anh_huong['so_cau_hoi']} câu hỏi và {anh_huong['so_phien']} phiên khảo sát "
                "liên quan; xác nhận xóa kèm dữ liệu liên quan để tiếp tục"
            ),
        )


@router.post("/anh-huong-xoa", response_model=DmLoaiCauHoiAnhHuongXoa)
def anh_huong_xoa_loai_cau_hoi(
    payload: DmLoaiCauHoiDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmLoaiCauHoiAnhHuongXoa:
    """Xem trước số câu hỏi, đáp án và phiên khảo sát sẽ bị xóa theo nếu xóa các loại câu hỏi này."""
    return DmLoaiCauHoiAnhHuongXoa(**xoa_loai_cau_hoi.anh_huong(db, payload.ids))


@router.delete("", response_model=DmLoaiCauHoiDeleteManyResult)
def delete_loai_cau_hoi_many(
    payload: DmLoaiCauHoiDeleteMany,
    xoa_lien_quan: bool = Query(default=False),
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmLoaiCauHoiDeleteManyResult:
    """Xóa nhiều loại câu hỏi theo danh sách id.

    `xoa_lien_quan=true`: xóa luôn câu hỏi, đáp án thuộc các loại này và các phiên khảo sát đã làm có câu hỏi thuộc
    loại này (xem trước số lượng bằng POST /anh-huong-xoa). Không bật mà còn dữ liệu liên quan thì trả 400.
    """
    if xoa_lien_quan:
        deleted = xoa_loai_cau_hoi.xoa(db, payload.ids)
        db.commit()
        return DmLoaiCauHoiDeleteManyResult(deleted=deleted)
    items = db.scalars(select(DmLoaiCauHoi).where(DmLoaiCauHoi.id.in_(payload.ids))).all()
    if not items:
        return DmLoaiCauHoiDeleteManyResult(deleted=0)
    _chan_neu_con_lien_quan(db, [item.id for item in items])
    for item in items:
        db.delete(item)
    db.commit()
    return DmLoaiCauHoiDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_loai_cau_hoi(
    item_id: int,
    xoa_lien_quan: bool = Query(default=False),
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> None:
    """Xóa một loại câu hỏi theo id; `xoa_lien_quan=true` xóa kèm câu hỏi, đáp án và phiên khảo sát liên quan."""
    item = _get_or_400(db, item_id)
    if xoa_lien_quan:
        xoa_loai_cau_hoi.xoa(db, [item.id])
    else:
        _chan_neu_con_lien_quan(db, [item.id])
        db.delete(item)
    db.commit()
