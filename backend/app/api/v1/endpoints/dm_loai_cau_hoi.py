from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_current_user
from app.db.session import get_db
from app.models.dm_loai_cau_hoi import THU_TU_LOAI_CAU_HOI, DmLoaiCauHoi
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_loai_cau_hoi import (
    DmLoaiCauHoiAnhHuongXoa,
    DmLoaiCauHoiBulkResult,
    DmLoaiCauHoiDeleteMany,
    DmLoaiCauHoiDeleteManyResult,
    DmLoaiCauHoiPage,
    DmLoaiCauHoiPublic,
    DmLoaiCauHoiTrangThai,
    DmLoaiCauHoiTrangThaiMany,
    DmLoaiCauHoiTrangThaiManyResult,
    DmLoaiCauHoiWrite,
)
from app.services import xoa_trac_nghiem

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
    doi_tuong_ap_dung: int | None = Query(default=None, ge=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
) -> DmLoaiCauHoiPage:
    """Lấy danh sách loại câu hỏi có phân trang, sắp theo thứ tự ưu tiên.

    Lọc theo tên, trạng thái và đối tượng áp dụng (loại có chứa mã đó). Không cần đăng nhập.
    """
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(DmLoaiCauHoi.ten_loai_cau_hoi.like(pattern, escape="\\"))
    if trang_thai is not None:
        filters.append(DmLoaiCauHoi.trang_thai == trang_thai)
    if doi_tuong_ap_dung is not None:
        filters.append(func.json_contains(DmLoaiCauHoi.doi_tuong_ap_dung, str(doi_tuong_ap_dung)) == 1)

    count_stmt = select(func.count()).select_from(DmLoaiCauHoi)
    stmt = select(DmLoaiCauHoi)
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    items = db.scalars(
        stmt.order_by(*THU_TU_LOAI_CAU_HOI)
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
    """Thêm nhiều loại câu hỏi cùng lúc. Thứ tự ưu tiên được trùng (trùng thì loại tạo trước đứng trước)."""
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách loại câu hỏi trống")
    if len(payload) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ thêm tối đa 500 loại câu hỏi mỗi lần",
        )

    items = [DmLoaiCauHoi(**item.model_dump()) for item in payload]
    db.add_all(items)
    db.commit()
    return DmLoaiCauHoiBulkResult(created=len(items))


@router.post("", response_model=DmLoaiCauHoiPublic, status_code=status.HTTP_201_CREATED)
def create_loai_cau_hoi(
    payload: DmLoaiCauHoiWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmLoaiCauHoi:
    """Thêm một loại câu hỏi. Thứ tự ưu tiên được trùng với loại khác."""
    item = DmLoaiCauHoi(**payload.model_dump())
    db.add(item)
    db.commit()
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
    db.commit()
    db.refresh(item)
    return item


@router.patch("/trang-thai", response_model=DmLoaiCauHoiTrangThaiManyResult)
def update_trang_thai_loai_cau_hoi_many(
    payload: DmLoaiCauHoiTrangThaiMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmLoaiCauHoiTrangThaiManyResult:
    """Bật/tắt nhiều loại câu hỏi cùng lúc. Id không tồn tại thì bỏ qua."""
    items = db.scalars(select(DmLoaiCauHoi).where(DmLoaiCauHoi.id.in_(payload.ids))).all()
    for item in items:
        item.trang_thai = payload.trang_thai
    db.commit()
    return DmLoaiCauHoiTrangThaiManyResult(updated=len(items))


@router.patch("/{item_id}/trang-thai", response_model=DmLoaiCauHoiPublic)
def update_trang_thai_loai_cau_hoi(
    item_id: int,
    payload: DmLoaiCauHoiTrangThai,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmLoaiCauHoi:
    """Bật/tắt nhanh một loại câu hỏi, giữ nguyên các thông tin khác."""
    item = _get_or_400(db, item_id)
    item.trang_thai = payload.trang_thai
    db.commit()
    db.refresh(item)
    return item


def _chan_neu_con_lien_quan(db: Session, ids: list[int]) -> None:
    """Còn câu hỏi hoặc phiên khảo sát dùng loại này thì trả 400 nêu số lượng (xóa kèm bằng xoa_lien_quan=true)."""
    anh_huong = xoa_trac_nghiem.anh_huong_loai(db, ids)
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
    return DmLoaiCauHoiAnhHuongXoa(**xoa_trac_nghiem.anh_huong_loai(db, payload.ids))


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
        deleted = xoa_trac_nghiem.xoa_loai(db, payload.ids)
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
        xoa_trac_nghiem.xoa_loai(db, [item.id])
    else:
        _chan_neu_con_lien_quan(db, [item.id])
        db.delete(item)
    db.commit()
