from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_current_user
from app.db.session import get_db
from app.models.dm_thpt_xkld import DmThptXkldNhomNghe, DmThptXkldKenhKetNoi, DmThptXkldThiTruong
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_thpt_xkld import (
    DmThptXkldDeleteMany,
    DmThptXkldKenhKetNoiPage,
    DmThptXkldKenhKetNoiPublic,
    DmThptXkldKenhKetNoiWrite,
    KetQuaThemNhieu,
    KetQuaXoaNhieu,
    LoaiKenhXkld,
)
from app.services.thpt_xkld import (
    danh_sach_con,
    kiem_tra_lien_ket,
    lay_lien_ket,
    loc_lien_ket,
    thong_tin_lien_ket,
)

router = APIRouter(prefix="/danh-muc/thpt-xkld/kenh-ket-noi", tags=["danh-muc"])


def _get_or_400(db: Session, item_id: int) -> DmThptXkldKenhKetNoi:
    """Lấy một kênh kết nối XKLĐ theo id. Trả lỗi 400 kèm thông báo nếu không tồn tại."""
    item = db.get(DmThptXkldKenhKetNoi, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy kênh kết nối XKLĐ có id = {item_id}",
        )
    return item


def _to_public(item: DmThptXkldKenhKetNoi, lien_ket: dict) -> DmThptXkldKenhKetNoiPublic:
    """Ghép bản ghi với mã, tên nhóm nghề và thị trường."""
    return DmThptXkldKenhKetNoiPublic(
        id=item.id,
        thpt_xkld_nhom_nghe_id=item.thpt_xkld_nhom_nghe_id,
        thpt_xkld_thi_truong_id=item.thpt_xkld_thi_truong_id,
        loai_kenh=item.loai_kenh,
        ten_kenh=item.ten_kenh,
        thong_tin_lien_he=item.thong_tin_lien_he,
        mo_ta_ho_tro=item.mo_ta_ho_tro,
        luu_y_tranh_rui_ro=item.luu_y_tranh_rui_ro,
        thu_tu_hien_thi=item.thu_tu_hien_thi,
        **lien_ket,
    )


@router.get("", response_model=DmThptXkldKenhKetNoiPage)
def list_thpt_xkld_kenh_ket_noi(
    q: str | None = Query(default=None, max_length=255),
    thpt_xkld_nhom_nghe_id: int | None = Query(default=None, ge=1),
    thpt_xkld_thi_truong_id: int | None = Query(default=None, ge=1),
    loai_kenh: LoaiKenhXkld | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
) -> DmThptXkldKenhKetNoiPage:
    """Lấy danh sách kênh kết nối XKLĐ có phân trang và bộ lọc, không cần đăng nhập."""
    filters = loc_lien_ket(
        DmThptXkldKenhKetNoi,
        [DmThptXkldKenhKetNoi.ten_kenh, DmThptXkldKenhKetNoi.thong_tin_lien_he],
        q,
        thpt_xkld_nhom_nghe_id,
        thpt_xkld_thi_truong_id,
    )
    if loai_kenh:
        filters.append(DmThptXkldKenhKetNoi.loai_kenh == loai_kenh)
    rows, total = danh_sach_con(
        db,
        DmThptXkldKenhKetNoi,
        filters,
        [
            DmThptXkldKenhKetNoi.thpt_xkld_nhom_nghe_id.asc(),
            # Dòng chung của nhóm nghề (không gắn thị trường) xếp trước.
            DmThptXkldThiTruong.thu_tu_hien_thi.is_(None).desc(),
            DmThptXkldThiTruong.thu_tu_hien_thi.asc(),
            DmThptXkldKenhKetNoi.thu_tu_hien_thi.asc(),
            DmThptXkldKenhKetNoi.id.asc(),
        ],
        page,
        page_size,
    )
    return DmThptXkldKenhKetNoiPage(
        items=[_to_public(item, thong_tin_lien_ket(nhom, tt)) for item, nhom, tt in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{item_id}", response_model=DmThptXkldKenhKetNoiPublic)
def get_thpt_xkld_kenh_ket_noi(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmThptXkldKenhKetNoiPublic:
    """Lấy chi tiết một kênh kết nối XKLĐ theo id."""
    item = _get_or_400(db, item_id)
    return _to_public(item, lay_lien_ket(db, item))


@router.post("/bulk", response_model=KetQuaThemNhieu, status_code=status.HTTP_201_CREATED)
def create_thpt_xkld_kenh_ket_noi_bulk(
    payload: list[DmThptXkldKenhKetNoiWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaThemNhieu:
    """Thêm nhiều kênh kết nối XKLĐ cùng lúc.

    Từ chối nếu nhóm nghề/thị trường không tồn tại hoặc thị trường không thuộc nhóm nghề.
    """
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách kênh kết nối XKLĐ trống")
    if len(payload) > 500:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chỉ thêm tối đa 500 bản ghi mỗi lần")
    kiem_tra_lien_ket(db, [(item.thpt_xkld_nhom_nghe_id, item.thpt_xkld_thi_truong_id) for item in payload])
    items = [DmThptXkldKenhKetNoi(**item.model_dump()) for item in payload]
    db.add_all(items)
    db.commit()
    return KetQuaThemNhieu(created=len(items))


@router.post("", response_model=DmThptXkldKenhKetNoiPublic, status_code=status.HTTP_201_CREATED)
def create_thpt_xkld_kenh_ket_noi(
    payload: DmThptXkldKenhKetNoiWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThptXkldKenhKetNoiPublic:
    """Thêm một kênh kết nối XKLĐ."""
    nhom, tt = _lien_ket_mot(db, payload)
    item = DmThptXkldKenhKetNoi(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return _to_public(item, thong_tin_lien_ket(nhom, tt))


@router.put("/{item_id}", response_model=DmThptXkldKenhKetNoiPublic)
def update_thpt_xkld_kenh_ket_noi(
    item_id: int,
    payload: DmThptXkldKenhKetNoiWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThptXkldKenhKetNoiPublic:
    """Cập nhật toàn bộ thông tin một kênh kết nối XKLĐ theo id."""
    item = _get_or_400(db, item_id)
    nhom, tt = _lien_ket_mot(db, payload)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return _to_public(item, thong_tin_lien_ket(nhom, tt))


@router.delete("", response_model=KetQuaXoaNhieu)
def delete_thpt_xkld_kenh_ket_noi_many(
    payload: DmThptXkldDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaXoaNhieu:
    """Xóa nhiều kênh kết nối XKLĐ theo danh sách id. Id không tồn tại thì bỏ qua."""
    items = db.scalars(select(DmThptXkldKenhKetNoi).where(DmThptXkldKenhKetNoi.id.in_(payload.ids))).all()
    for item in items:
        db.delete(item)
    db.commit()
    return KetQuaXoaNhieu(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_thpt_xkld_kenh_ket_noi(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> None:
    """Xóa một kênh kết nối XKLĐ theo id."""
    db.delete(_get_or_400(db, item_id))
    db.commit()


def _lien_ket_mot(
    db: Session, payload: DmThptXkldKenhKetNoiWrite
) -> tuple[DmThptXkldNhomNghe, DmThptXkldThiTruong | None]:
    """Kiểm tra liên kết của một bản ghi; trả về nhóm nghề và thị trường (nếu có)."""
    nhom_id, tt_id = payload.thpt_xkld_nhom_nghe_id, payload.thpt_xkld_thi_truong_id
    nhom_nghe, thi_truong = kiem_tra_lien_ket(db, [(nhom_id, tt_id)])
    return nhom_nghe[nhom_id], thi_truong.get(tt_id) if tt_id else None
