from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_current_user
from app.db.session import get_db
from app.models.dm_thpt_xkld import DmThptXkldNhomNghe, DmThptXkldThiTruong, DmThptXkldThuTuc
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_thpt_xkld import (
    DmThptXkldDeleteMany,
    DmThptXkldThuTucPage,
    DmThptXkldThuTucPublic,
    DmThptXkldThuTucWrite,
    KetQuaThemNhieu,
    KetQuaXoaNhieu,
)
from app.services.thpt_xkld import (
    danh_sach_con,
    kiem_tra_lien_ket,
    lay_lien_ket,
    loc_lien_ket,
    thong_tin_lien_ket,
)

router = APIRouter(prefix="/danh-muc/thpt-xkld/thu-tuc", tags=["danh-muc"])


def _get_or_400(db: Session, item_id: int) -> DmThptXkldThuTuc:
    """Lấy một bước thủ tục XKLĐ theo id. Trả lỗi 400 kèm thông báo nếu không tồn tại."""
    item = db.get(DmThptXkldThuTuc, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy bước thủ tục XKLĐ có id = {item_id}",
        )
    return item


def _to_public(item: DmThptXkldThuTuc, lien_ket: dict) -> DmThptXkldThuTucPublic:
    """Ghép bản ghi với mã, tên nhóm nghề và thị trường."""
    return DmThptXkldThuTucPublic(
        id=item.id,
        thpt_xkld_nhom_nghe_id=item.thpt_xkld_nhom_nghe_id,
        thpt_xkld_thi_truong_id=item.thpt_xkld_thi_truong_id,
        buoc_so=item.buoc_so,
        ten_buoc=item.ten_buoc,
        mo_ta_thu_tuc=item.mo_ta_thu_tuc,
        giay_to_can_co=item.giay_to_can_co,
        thoi_gian_du_kien=item.thoi_gian_du_kien,
        **lien_ket,
    )


@router.get("", response_model=DmThptXkldThuTucPage)
def list_thpt_xkld_thu_tuc(
    q: str | None = Query(default=None, max_length=255),
    thpt_xkld_nhom_nghe_id: int | None = Query(default=None, ge=1),
    thpt_xkld_thi_truong_id: int | None = Query(default=None, ge=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
) -> DmThptXkldThuTucPage:
    """Lấy danh sách bước thủ tục XKLĐ có phân trang và bộ lọc, không cần đăng nhập."""
    filters = loc_lien_ket(
        DmThptXkldThuTuc,
        [DmThptXkldThuTuc.ten_buoc, DmThptXkldThuTuc.mo_ta_thu_tuc],
        q,
        thpt_xkld_nhom_nghe_id,
        thpt_xkld_thi_truong_id,
    )
    rows, total = danh_sach_con(
        db,
        DmThptXkldThuTuc,
        filters,
        [
            DmThptXkldThuTuc.thpt_xkld_nhom_nghe_id.asc(),
            # Dòng chung của nhóm nghề (không gắn thị trường) xếp trước.
            DmThptXkldThiTruong.thu_tu_hien_thi.is_(None).desc(),
            DmThptXkldThiTruong.thu_tu_hien_thi.asc(),
            DmThptXkldThuTuc.buoc_so.asc(),
            DmThptXkldThuTuc.id.asc(),
        ],
        page,
        page_size,
    )
    return DmThptXkldThuTucPage(
        items=[_to_public(item, thong_tin_lien_ket(nhom, tt)) for item, nhom, tt in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{item_id}", response_model=DmThptXkldThuTucPublic)
def get_thpt_xkld_thu_tuc(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmThptXkldThuTucPublic:
    """Lấy chi tiết một bước thủ tục XKLĐ theo id."""
    item = _get_or_400(db, item_id)
    return _to_public(item, lay_lien_ket(db, item))


@router.post("/bulk", response_model=KetQuaThemNhieu, status_code=status.HTTP_201_CREATED)
def create_thpt_xkld_thu_tuc_bulk(
    payload: list[DmThptXkldThuTucWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaThemNhieu:
    """Thêm nhiều bước thủ tục XKLĐ cùng lúc.

    Từ chối nếu nhóm nghề/thị trường không tồn tại hoặc thị trường không thuộc nhóm nghề.
    """
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách bước thủ tục XKLĐ trống")
    if len(payload) > 500:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chỉ thêm tối đa 500 bản ghi mỗi lần")
    kiem_tra_lien_ket(db, [(item.thpt_xkld_nhom_nghe_id, item.thpt_xkld_thi_truong_id) for item in payload])
    items = [DmThptXkldThuTuc(**item.model_dump()) for item in payload]
    db.add_all(items)
    db.commit()
    return KetQuaThemNhieu(created=len(items))


@router.post("", response_model=DmThptXkldThuTucPublic, status_code=status.HTTP_201_CREATED)
def create_thpt_xkld_thu_tuc(
    payload: DmThptXkldThuTucWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThptXkldThuTucPublic:
    """Thêm một bước thủ tục XKLĐ."""
    nhom, tt = _lien_ket_mot(db, payload)
    item = DmThptXkldThuTuc(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return _to_public(item, thong_tin_lien_ket(nhom, tt))


@router.put("/{item_id}", response_model=DmThptXkldThuTucPublic)
def update_thpt_xkld_thu_tuc(
    item_id: int,
    payload: DmThptXkldThuTucWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThptXkldThuTucPublic:
    """Cập nhật toàn bộ thông tin một bước thủ tục XKLĐ theo id."""
    item = _get_or_400(db, item_id)
    nhom, tt = _lien_ket_mot(db, payload)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return _to_public(item, thong_tin_lien_ket(nhom, tt))


@router.delete("", response_model=KetQuaXoaNhieu)
def delete_thpt_xkld_thu_tuc_many(
    payload: DmThptXkldDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaXoaNhieu:
    """Xóa nhiều bước thủ tục XKLĐ theo danh sách id. Id không tồn tại thì bỏ qua."""
    items = db.scalars(select(DmThptXkldThuTuc).where(DmThptXkldThuTuc.id.in_(payload.ids))).all()
    for item in items:
        db.delete(item)
    db.commit()
    return KetQuaXoaNhieu(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_thpt_xkld_thu_tuc(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> None:
    """Xóa một bước thủ tục XKLĐ theo id."""
    db.delete(_get_or_400(db, item_id))
    db.commit()


def _lien_ket_mot(
    db: Session, payload: DmThptXkldThuTucWrite
) -> tuple[DmThptXkldNhomNghe, DmThptXkldThiTruong | None]:
    """Kiểm tra liên kết của một bản ghi; trả về nhóm nghề và thị trường (nếu có)."""
    nhom_id, tt_id = payload.thpt_xkld_nhom_nghe_id, payload.thpt_xkld_thi_truong_id
    nhom_nghe, thi_truong = kiem_tra_lien_ket(db, [(nhom_id, tt_id)])
    return nhom_nghe[nhom_id], thi_truong.get(tt_id) if tt_id else None
