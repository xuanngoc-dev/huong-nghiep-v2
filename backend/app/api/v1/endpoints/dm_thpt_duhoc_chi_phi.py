from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_current_user
from app.db.session import get_db
from app.models.dm_thpt_duhoc import DmThptDuhocChiPhi, DmThptDuhocHuongDi, DmThptDuhocQuocGia
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_thpt_duhoc import (
    DmThptDuhocChiPhiPage,
    DmThptDuhocChiPhiPublic,
    DmThptDuhocChiPhiWrite,
    DmThptDuhocDeleteMany,
    KetQuaThemNhieu,
    KetQuaXoaNhieu,
    LoaiChiPhi,
)
from app.services.thpt_duhoc import (
    danh_sach_con,
    kiem_tra_lien_ket,
    lay_lien_ket,
    loc_lien_ket,
    thong_tin_lien_ket,
)

router = APIRouter(prefix="/danh-muc/thpt-du-hoc/chi-phi", tags=["danh-muc"])


def _get_or_400(db: Session, item_id: int) -> DmThptDuhocChiPhi:
    """Lấy một khoản chi phí du học theo id. Trả lỗi 400 kèm thông báo nếu không tồn tại."""
    item = db.get(DmThptDuhocChiPhi, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy khoản chi phí du học có id = {item_id}",
        )
    return item


def _to_public(item: DmThptDuhocChiPhi, lien_ket: dict) -> DmThptDuhocChiPhiPublic:
    """Ghép bản ghi với mã, tên hướng đi và quốc gia."""
    return DmThptDuhocChiPhiPublic(
        id=item.id,
        thpt_duhoc_huong_di_id=item.thpt_duhoc_huong_di_id,
        thpt_duhoc_quoc_gia_id=item.thpt_duhoc_quoc_gia_id,
        loai_chi_phi=item.loai_chi_phi,
        ten_khoan_chi=item.ten_khoan_chi,
        chi_phi_min=item.chi_phi_min,
        chi_phi_max=item.chi_phi_max,
        don_vi_tien=item.don_vi_tien,
        chi_phi_quy_doi_vnd_text=item.chi_phi_quy_doi_vnd_text,
        ghi_chu=item.ghi_chu,
        **lien_ket,
    )


@router.get("", response_model=DmThptDuhocChiPhiPage)
def list_thpt_duhoc_chi_phi(
    q: str | None = Query(default=None, max_length=255),
    thpt_duhoc_huong_di_id: int | None = Query(default=None, ge=1),
    thpt_duhoc_quoc_gia_id: int | None = Query(default=None, ge=1),
    loai_chi_phi: LoaiChiPhi | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
) -> DmThptDuhocChiPhiPage:
    """Lấy danh sách khoản chi phí du học có phân trang và bộ lọc, không cần đăng nhập."""
    filters = loc_lien_ket(
        DmThptDuhocChiPhi,
        [DmThptDuhocChiPhi.ten_khoan_chi],
        q,
        thpt_duhoc_huong_di_id,
        thpt_duhoc_quoc_gia_id,
    )
    if loai_chi_phi:
        filters.append(DmThptDuhocChiPhi.loai_chi_phi == loai_chi_phi)
    rows, total = danh_sach_con(
        db,
        DmThptDuhocChiPhi,
        filters,
        [
            DmThptDuhocChiPhi.thpt_duhoc_huong_di_id.asc(),
            # Dòng chung của hướng đi (không gắn quốc gia) xếp trước.
            DmThptDuhocQuocGia.thu_tu_hien_thi.is_(None).desc(),
            DmThptDuhocQuocGia.thu_tu_hien_thi.asc(),
            DmThptDuhocChiPhi.loai_chi_phi.asc(),
            DmThptDuhocChiPhi.id.asc(),
        ],
        page,
        page_size,
    )
    return DmThptDuhocChiPhiPage(
        items=[_to_public(item, thong_tin_lien_ket(huong, qg)) for item, huong, qg in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{item_id}", response_model=DmThptDuhocChiPhiPublic)
def get_thpt_duhoc_chi_phi(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmThptDuhocChiPhiPublic:
    """Lấy chi tiết một khoản chi phí du học theo id."""
    item = _get_or_400(db, item_id)
    return _to_public(item, lay_lien_ket(db, item))


@router.post("/bulk", response_model=KetQuaThemNhieu, status_code=status.HTTP_201_CREATED)
def create_thpt_duhoc_chi_phi_bulk(
    payload: list[DmThptDuhocChiPhiWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaThemNhieu:
    """Thêm nhiều khoản chi phí du học cùng lúc.

    Từ chối nếu hướng đi/quốc gia không tồn tại hoặc quốc gia không thuộc hướng đi.
    """
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách khoản chi phí du học trống")
    if len(payload) > 500:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chỉ thêm tối đa 500 bản ghi mỗi lần")
    kiem_tra_lien_ket(db, [(item.thpt_duhoc_huong_di_id, item.thpt_duhoc_quoc_gia_id) for item in payload])
    items = [DmThptDuhocChiPhi(**item.model_dump()) for item in payload]
    db.add_all(items)
    db.commit()
    return KetQuaThemNhieu(created=len(items))


@router.post("", response_model=DmThptDuhocChiPhiPublic, status_code=status.HTTP_201_CREATED)
def create_thpt_duhoc_chi_phi(
    payload: DmThptDuhocChiPhiWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThptDuhocChiPhiPublic:
    """Thêm một khoản chi phí du học."""
    huong, qg = _lien_ket_mot(db, payload)
    item = DmThptDuhocChiPhi(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return _to_public(item, thong_tin_lien_ket(huong, qg))


@router.put("/{item_id}", response_model=DmThptDuhocChiPhiPublic)
def update_thpt_duhoc_chi_phi(
    item_id: int,
    payload: DmThptDuhocChiPhiWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThptDuhocChiPhiPublic:
    """Cập nhật toàn bộ thông tin một khoản chi phí du học theo id."""
    item = _get_or_400(db, item_id)
    huong, qg = _lien_ket_mot(db, payload)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return _to_public(item, thong_tin_lien_ket(huong, qg))


@router.delete("", response_model=KetQuaXoaNhieu)
def delete_thpt_duhoc_chi_phi_many(
    payload: DmThptDuhocDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaXoaNhieu:
    """Xóa nhiều khoản chi phí du học theo danh sách id. Id không tồn tại thì bỏ qua."""
    items = db.scalars(select(DmThptDuhocChiPhi).where(DmThptDuhocChiPhi.id.in_(payload.ids))).all()
    for item in items:
        db.delete(item)
    db.commit()
    return KetQuaXoaNhieu(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_thpt_duhoc_chi_phi(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> None:
    """Xóa một khoản chi phí du học theo id."""
    db.delete(_get_or_400(db, item_id))
    db.commit()


def _lien_ket_mot(
    db: Session, payload: DmThptDuhocChiPhiWrite
) -> tuple[DmThptDuhocHuongDi, DmThptDuhocQuocGia | None]:
    """Kiểm tra liên kết của một bản ghi; trả về hướng đi và quốc gia (nếu có)."""
    huong_id, qg_id = payload.thpt_duhoc_huong_di_id, payload.thpt_duhoc_quoc_gia_id
    huong_di, quoc_gia = kiem_tra_lien_ket(db, [(huong_id, qg_id)])
    return huong_di[huong_id], quoc_gia.get(qg_id) if qg_id else None
