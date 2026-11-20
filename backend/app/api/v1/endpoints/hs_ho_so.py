
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.thoi_gian import bay_gio
from app.db.session import get_db
from app.models.nguoi_dung import NguoiDung
from app.models.nguoi_dung_thong_tin import NguoiDungThongTin
from app.schemas.hs_ho_so import HoSoXetTuyenPublic, HoSoXetTuyenWrite
from app.services.ho_so_xet_tuyen import (
    DanhMucMa,
    HoSoXetTuyenError,
    doc_ho_so,
    ho_so_chinh,
    luu_ho_so,
    tu_trinh_do_hoc_van,
)
from app.services.xet_tuyen.chuyen_ho_so import DanhMucHoSo

# Hồ sơ xét tuyển (bảng hs_*) của thành viên: điểm từng môn, học bạ, bài thi, chứng chỉ, thành tích, nguyện vọng.
router = APIRouter(prefix="/ho-so-xet-tuyen", tags=["ho-so-xet-tuyen"])


@router.get("/cua-toi", response_model=HoSoXetTuyenPublic)
def get_ho_so_xet_tuyen(
    db: Session = Depends(get_db), user: NguoiDung = Depends(get_current_user)
) -> HoSoXetTuyenPublic:
    """Hồ sơ xét tuyển chính của tài khoản. Chưa có thì dựng từ hồ sơ năng lực cũ (`tu_du_lieu_cu = true`, chưa lưu)."""
    dm = DanhMucMa.tu_csdl(db)
    hs = ho_so_chinh(db, user.id)
    if hs is not None:
        return doc_ho_so(db, hs, dm)
    profile = db.scalar(select(NguoiDungThongTin).where(NguoiDungThongTin.nguoi_dung_id == user.id))
    payload = tu_trinh_do_hoc_van(profile, nam_tuyen_sinh=bay_gio().year, danh_muc=DanhMucHoSo.tu_csdl(db))
    # Bỏ mã ngoài danh mục để lưu lại được ngay.
    payload = payload.model_copy(
        update={
            "diem_mon": [d for d in payload.diem_mon if d.ma_mon in dm.mon],
            "chung_chi": [c for c in payload.chung_chi if c.ma_chung_chi in dm.chung_chi],
            "diem_bai_thi": [b for b in payload.diem_bai_thi if b.ma_bai_thi in dm.bai_thi],
            "thanh_tich": [t for t in payload.thanh_tich if t.ma_thanh_tich in dm.thanh_tich],
        }
    )
    return HoSoXetTuyenPublic(**payload.model_dump(), tu_du_lieu_cu=True)


@router.put("/cua-toi", response_model=HoSoXetTuyenPublic)
def put_ho_so_xet_tuyen(
    payload: HoSoXetTuyenWrite,
    db: Session = Depends(get_db),
    user: NguoiDung = Depends(get_current_user),
) -> HoSoXetTuyenPublic:
    """Ghi đè hồ sơ xét tuyển chính; đồng thời cập nhật hồ sơ năng lực cũ (JSON, khu vực, đối tượng, tỉnh) cho khớp."""
    dm = DanhMucMa.tu_csdl(db)
    try:
        hs = luu_ho_so(db, user.id, payload, dm)
        db.commit()
    except HoSoXetTuyenError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from None
    db.refresh(hs)
    return doc_ho_so(db, hs, dm)
