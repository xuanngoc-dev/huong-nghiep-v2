from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_current_user
from app.db.session import get_db
from app.models.dm_thpt_duhoc import DmThptDuhocHuongDi, DmThptDuhocQuocGia, DmThptDuhocThuTuc
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_thpt_duhoc import (
    DmThptDuhocDeleteMany,
    DmThptDuhocThuTucPage,
    DmThptDuhocThuTucPublic,
    DmThptDuhocThuTucWrite,
    KetQuaThemNhieu,
    KetQuaXoaNhieu,
)
from app.services.thpt_duhoc import (
    danh_sach_con,
    kiem_tra_lien_ket,
    lay_lien_ket,
    loc_lien_ket,
    thong_tin_lien_ket,
)

router = APIRouter(prefix="/danh-muc/thpt-du-hoc/thu-tuc", tags=["danh-muc"])


def _get_or_400(db: Session, item_id: int) -> DmThptDuhocThuTuc:
    """Lấy một bước thủ tục du học theo id. Trả lỗi 400 kèm thông báo nếu không tồn tại."""
    item = db.get(DmThptDuhocThuTuc, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy bước thủ tục du học có id = {item_id}",
        )
    return item


def _to_public(item: DmThptDuhocThuTuc, lien_ket: dict) -> DmThptDuhocThuTucPublic:
    """Ghép bản ghi với mã, tên hướng đi và quốc gia."""
    return DmThptDuhocThuTucPublic(
        id=item.id,
        thpt_duhoc_huong_di_id=item.thpt_duhoc_huong_di_id,
        thpt_duhoc_quoc_gia_id=item.thpt_duhoc_quoc_gia_id,
        buoc_so=item.buoc_so,
        ten_buoc=item.ten_buoc,
        mo_ta_thu_tuc=item.mo_ta_thu_tuc,
        giay_to_can_co=item.giay_to_can_co,
        thoi_gian_du_kien=item.thoi_gian_du_kien,
        **lien_ket,
    )


@router.get("", response_model=DmThptDuhocThuTucPage)
def list_thpt_duhoc_thu_tuc(
    q: str | None = Query(default=None, max_length=255),
    thpt_duhoc_huong_di_id: int | None = Query(default=None, ge=1),
    thpt_duhoc_quoc_gia_id: int | None = Query(default=None, ge=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
) -> DmThptDuhocThuTucPage:
    """Lấy danh sách bước thủ tục du học có phân trang và bộ lọc, không cần đăng nhập."""
    filters = loc_lien_ket(
        DmThptDuhocThuTuc,
        [DmThptDuhocThuTuc.ten_buoc, DmThptDuhocThuTuc.mo_ta_thu_tuc],
        q,
        thpt_duhoc_huong_di_id,
        thpt_duhoc_quoc_gia_id,
    )
    rows, total = danh_sach_con(
        db,
        DmThptDuhocThuTuc,
        filters,
        [
            DmThptDuhocThuTuc.thpt_duhoc_huong_di_id.asc(),
            # Dòng chung của hướng đi (không gắn quốc gia) xếp trước.
            DmThptDuhocQuocGia.thu_tu_hien_thi.is_(None).desc(),
            DmThptDuhocQuocGia.thu_tu_hien_thi.asc(),
            DmThptDuhocThuTuc.buoc_so.asc(),
            DmThptDuhocThuTuc.id.asc(),
        ],
        page,
        page_size,
    )
    return DmThptDuhocThuTucPage(
        items=[_to_public(item, thong_tin_lien_ket(huong, qg)) for item, huong, qg in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{item_id}", response_model=DmThptDuhocThuTucPublic)
def get_thpt_duhoc_thu_tuc(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmThptDuhocThuTucPublic:
    """Lấy chi tiết một bước thủ tục du học theo id."""
    item = _get_or_400(db, item_id)
    return _to_public(item, lay_lien_ket(db, item))


@router.post("/bulk", response_model=KetQuaThemNhieu, status_code=status.HTTP_201_CREATED)
def create_thpt_duhoc_thu_tuc_bulk(
    payload: list[DmThptDuhocThuTucWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaThemNhieu:
    """Thêm nhiều bước thủ tục du học cùng lúc.

    Từ chối nếu hướng đi/quốc gia không tồn tại hoặc quốc gia không thuộc hướng đi.
    """
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách bước thủ tục du học trống")
    if len(payload) > 500:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chỉ thêm tối đa 500 bản ghi mỗi lần")
    kiem_tra_lien_ket(db, [(item.thpt_duhoc_huong_di_id, item.thpt_duhoc_quoc_gia_id) for item in payload])
    items = [DmThptDuhocThuTuc(**item.model_dump()) for item in payload]
    db.add_all(items)
    db.commit()
    return KetQuaThemNhieu(created=len(items))


@router.post("", response_model=DmThptDuhocThuTucPublic, status_code=status.HTTP_201_CREATED)
def create_thpt_duhoc_thu_tuc(
    payload: DmThptDuhocThuTucWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThptDuhocThuTucPublic:
    """Thêm một bước thủ tục du học."""
    huong, qg = _lien_ket_mot(db, payload)
    item = DmThptDuhocThuTuc(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return _to_public(item, thong_tin_lien_ket(huong, qg))


@router.put("/{item_id}", response_model=DmThptDuhocThuTucPublic)
def update_thpt_duhoc_thu_tuc(
    item_id: int,
    payload: DmThptDuhocThuTucWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThptDuhocThuTucPublic:
    """Cập nhật toàn bộ thông tin một bước thủ tục du học theo id."""
    item = _get_or_400(db, item_id)
    huong, qg = _lien_ket_mot(db, payload)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return _to_public(item, thong_tin_lien_ket(huong, qg))


@router.delete("", response_model=KetQuaXoaNhieu)
def delete_thpt_duhoc_thu_tuc_many(
    payload: DmThptDuhocDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaXoaNhieu:
    """Xóa nhiều bước thủ tục du học theo danh sách id. Id không tồn tại thì bỏ qua."""
    items = db.scalars(select(DmThptDuhocThuTuc).where(DmThptDuhocThuTuc.id.in_(payload.ids))).all()
    for item in items:
        db.delete(item)
    db.commit()
    return KetQuaXoaNhieu(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_thpt_duhoc_thu_tuc(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> None:
    """Xóa một bước thủ tục du học theo id."""
    db.delete(_get_or_400(db, item_id))
    db.commit()


def _lien_ket_mot(
    db: Session, payload: DmThptDuhocThuTucWrite
) -> tuple[DmThptDuhocHuongDi, DmThptDuhocQuocGia | None]:
    """Kiểm tra liên kết của một bản ghi; trả về hướng đi và quốc gia (nếu có)."""
    huong_id, qg_id = payload.thpt_duhoc_huong_di_id, payload.thpt_duhoc_quoc_gia_id
    huong_di, quoc_gia = kiem_tra_lien_ket(db, [(huong_id, qg_id)])
    return huong_di[huong_id], quoc_gia.get(qg_id) if qg_id else None
