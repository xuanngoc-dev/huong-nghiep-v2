from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_current_user
from app.db.session import get_db
from app.models.dm_thpt_duhoc import DmThptDuhocHuongDi, DmThptDuhocKenhKetNoi, DmThptDuhocQuocGia
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_thpt_duhoc import (
    DmThptDuhocDeleteMany,
    DmThptDuhocKenhKetNoiPage,
    DmThptDuhocKenhKetNoiPublic,
    DmThptDuhocKenhKetNoiWrite,
    KetQuaThemNhieu,
    KetQuaXoaNhieu,
    LoaiKenh,
)
from app.services.thpt_duhoc import (
    danh_sach_con,
    kiem_tra_lien_ket,
    lay_lien_ket,
    loc_lien_ket,
    thong_tin_lien_ket,
)

router = APIRouter(prefix="/danh-muc/thpt-du-hoc/kenh-ket-noi", tags=["danh-muc"])


def _get_or_400(db: Session, item_id: int) -> DmThptDuhocKenhKetNoi:
    """Lấy một kênh kết nối du học theo id. Trả lỗi 400 kèm thông báo nếu không tồn tại."""
    item = db.get(DmThptDuhocKenhKetNoi, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy kênh kết nối du học có id = {item_id}",
        )
    return item


def _to_public(item: DmThptDuhocKenhKetNoi, lien_ket: dict) -> DmThptDuhocKenhKetNoiPublic:
    """Ghép bản ghi với mã, tên hướng đi và quốc gia."""
    return DmThptDuhocKenhKetNoiPublic(
        id=item.id,
        thpt_duhoc_huong_di_id=item.thpt_duhoc_huong_di_id,
        thpt_duhoc_quoc_gia_id=item.thpt_duhoc_quoc_gia_id,
        loai_kenh=item.loai_kenh,
        ten_kenh=item.ten_kenh,
        thong_tin_lien_he=item.thong_tin_lien_he,
        mo_ta_ho_tro=item.mo_ta_ho_tro,
        luu_y_khi_ket_noi=item.luu_y_khi_ket_noi,
        thu_tu_hien_thi=item.thu_tu_hien_thi,
        **lien_ket,
    )


@router.get("", response_model=DmThptDuhocKenhKetNoiPage)
def list_thpt_duhoc_kenh_ket_noi(
    q: str | None = Query(default=None, max_length=255),
    thpt_duhoc_huong_di_id: int | None = Query(default=None, ge=1),
    thpt_duhoc_quoc_gia_id: int | None = Query(default=None, ge=1),
    loai_kenh: LoaiKenh | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
) -> DmThptDuhocKenhKetNoiPage:
    """Lấy danh sách kênh kết nối du học có phân trang và bộ lọc, không cần đăng nhập."""
    filters = loc_lien_ket(
        DmThptDuhocKenhKetNoi,
        [DmThptDuhocKenhKetNoi.ten_kenh, DmThptDuhocKenhKetNoi.thong_tin_lien_he],
        q,
        thpt_duhoc_huong_di_id,
        thpt_duhoc_quoc_gia_id,
    )
    if loai_kenh:
        filters.append(DmThptDuhocKenhKetNoi.loai_kenh == loai_kenh)
    rows, total = danh_sach_con(
        db,
        DmThptDuhocKenhKetNoi,
        filters,
        [
            DmThptDuhocKenhKetNoi.thpt_duhoc_huong_di_id.asc(),
            # Dòng chung của hướng đi (không gắn quốc gia) xếp trước.
            DmThptDuhocQuocGia.thu_tu_hien_thi.is_(None).desc(),
            DmThptDuhocQuocGia.thu_tu_hien_thi.asc(),
            DmThptDuhocKenhKetNoi.thu_tu_hien_thi.asc(),
            DmThptDuhocKenhKetNoi.id.asc(),
        ],
        page,
        page_size,
    )
    return DmThptDuhocKenhKetNoiPage(
        items=[_to_public(item, thong_tin_lien_ket(huong, qg)) for item, huong, qg in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{item_id}", response_model=DmThptDuhocKenhKetNoiPublic)
def get_thpt_duhoc_kenh_ket_noi(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmThptDuhocKenhKetNoiPublic:
    """Lấy chi tiết một kênh kết nối du học theo id."""
    item = _get_or_400(db, item_id)
    return _to_public(item, lay_lien_ket(db, item))


@router.post("/bulk", response_model=KetQuaThemNhieu, status_code=status.HTTP_201_CREATED)
def create_thpt_duhoc_kenh_ket_noi_bulk(
    payload: list[DmThptDuhocKenhKetNoiWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaThemNhieu:
    """Thêm nhiều kênh kết nối du học cùng lúc.

    Từ chối nếu hướng đi/quốc gia không tồn tại hoặc quốc gia không thuộc hướng đi.
    """
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách kênh kết nối du học trống")
    if len(payload) > 500:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chỉ thêm tối đa 500 bản ghi mỗi lần")
    kiem_tra_lien_ket(db, [(item.thpt_duhoc_huong_di_id, item.thpt_duhoc_quoc_gia_id) for item in payload])
    items = [DmThptDuhocKenhKetNoi(**item.model_dump()) for item in payload]
    db.add_all(items)
    db.commit()
    return KetQuaThemNhieu(created=len(items))


@router.post("", response_model=DmThptDuhocKenhKetNoiPublic, status_code=status.HTTP_201_CREATED)
def create_thpt_duhoc_kenh_ket_noi(
    payload: DmThptDuhocKenhKetNoiWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThptDuhocKenhKetNoiPublic:
    """Thêm một kênh kết nối du học."""
    huong, qg = _lien_ket_mot(db, payload)
    item = DmThptDuhocKenhKetNoi(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return _to_public(item, thong_tin_lien_ket(huong, qg))


@router.put("/{item_id}", response_model=DmThptDuhocKenhKetNoiPublic)
def update_thpt_duhoc_kenh_ket_noi(
    item_id: int,
    payload: DmThptDuhocKenhKetNoiWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThptDuhocKenhKetNoiPublic:
    """Cập nhật toàn bộ thông tin một kênh kết nối du học theo id."""
    item = _get_or_400(db, item_id)
    huong, qg = _lien_ket_mot(db, payload)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return _to_public(item, thong_tin_lien_ket(huong, qg))


@router.delete("", response_model=KetQuaXoaNhieu)
def delete_thpt_duhoc_kenh_ket_noi_many(
    payload: DmThptDuhocDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaXoaNhieu:
    """Xóa nhiều kênh kết nối du học theo danh sách id. Id không tồn tại thì bỏ qua."""
    items = db.scalars(select(DmThptDuhocKenhKetNoi).where(DmThptDuhocKenhKetNoi.id.in_(payload.ids))).all()
    for item in items:
        db.delete(item)
    db.commit()
    return KetQuaXoaNhieu(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_thpt_duhoc_kenh_ket_noi(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> None:
    """Xóa một kênh kết nối du học theo id."""
    db.delete(_get_or_400(db, item_id))
    db.commit()


def _lien_ket_mot(
    db: Session, payload: DmThptDuhocKenhKetNoiWrite
) -> tuple[DmThptDuhocHuongDi, DmThptDuhocQuocGia | None]:
    """Kiểm tra liên kết của một bản ghi; trả về hướng đi và quốc gia (nếu có)."""
    huong_id, qg_id = payload.thpt_duhoc_huong_di_id, payload.thpt_duhoc_quoc_gia_id
    huong_di, quoc_gia = kiem_tra_lien_ket(db, [(huong_id, qg_id)])
    return huong_di[huong_id], quoc_gia.get(qg_id) if qg_id else None
