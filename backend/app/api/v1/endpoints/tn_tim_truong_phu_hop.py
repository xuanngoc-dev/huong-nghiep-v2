from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_optional_user
from app.api.v1.endpoints.dats_tuyen_sinh import list_truong_dao_tao
from app.db.session import get_db
from app.models.ht_cau_hinh_tra_cuu import HtCauHinhTraCuu
from app.models.nguoi_dung import NguoiDung
from app.models.tn_lich_su_tim_truong_phu_hop import TnLichSuTimTruongPhuHop
from app.schemas.tn_lich_su_tim_truong_phu_hop import (
    LuotTimTruong,
    TimTruongPhuHopRequest,
    TimTruongPhuHopResult,
)
from app.services.cau_hinh_tra_cuu import cau_hinh_dang_ap_dung

router = APIRouter(prefix="/tim-truong-phu-hop", tags=["tim-truong-phu-hop"])

_PHIEN_BAN_THUAT_TOAN = "loc-co-ban-v1"
# Số trường đầu tiên lưu lại trong du_lieu_ket_qua.
_SO_TRUONG_LUU = 50


def _da_dung_hom_nay(db: Session, tai_khoan_id: int) -> int:
    """Số lượt đã tính của tài khoản từ đầu ngày (theo giờ của database)."""
    return db.scalar(
        select(func.count())
        .select_from(TnLichSuTimTruongPhuHop)
        .where(
            TnLichSuTimTruongPhuHop.tai_khoan_id == tai_khoan_id,
            TnLichSuTimTruongPhuHop.da_tinh_luot == 1,
            TnLichSuTimTruongPhuHop.ngay_tao >= func.curdate(),
        )
    ) or 0


def _luot(db: Session, cau_hinh: HtCauHinhTraCuu, user: NguoiDung | None) -> LuotTimTruong:
    khach = cau_hinh.so_luot_tra_cuu_khach_ngay
    thanh_vien = cau_hinh.so_luot_tra_cuu_thanh_vien_ngay
    if user is None:
        return LuotTimTruong(
            la_thanh_vien=False,
            so_luot_ngay=khach,
            so_luot_khach_ngay=khach,
            so_luot_thanh_vien_ngay=thanh_vien,
        )
    da_dung = _da_dung_hom_nay(db, user.id)
    return LuotTimTruong(
        la_thanh_vien=True,
        so_luot_ngay=thanh_vien,
        so_luot_khach_ngay=khach,
        so_luot_thanh_vien_ngay=thanh_vien,
        da_dung=da_dung,
        con_lai=max(thanh_vien - da_dung, 0),
    )


def _ket_qua(db: Session, item: TnLichSuTimTruongPhuHop, user: NguoiDung) -> TimTruongPhuHopResult:
    return TimTruongPhuHopResult(
        lich_su_id=item.id,
        ma_yeu_cau=item.ma_yeu_cau,
        trang_thai_xu_ly=item.trang_thai_xu_ly,
        so_truong_tim_thay=item.so_truong_tim_thay,
        so_truong_phu_hop_so_bo=item.so_truong_phu_hop_so_bo,
        luot=_luot(db, cau_hinh_dang_ap_dung(db), user),
    )


def _dem_truong(db: Session, payload: TimTruongPhuHopRequest, loc: bool, page_size: int = 1):
    """Gọi lại truy vấn trường đào tạo dùng cho danh sách. loc=False thì bỏ mọi tiêu chí lọc."""
    tc = payload.tieu_chi_tim_kiem
    return list_truong_dao_tao(
        ma_nganh=payload.ma_nganh,
        q=tc.tu_khoa if loc else None,
        vung_mien=tc.khu_vuc if loc else None,
        loai_co_so=tc.loai_co_so if loc else None,
        ten_tinh_thanh=tc.tinh if loc else None,
        nam_tuyen_sinh=payload.nam_tuyen_sinh,
        sap_xep=tc.sap_xep if loc else "ten_asc",
        uu_tien_tinh=tc.uu_tien_tinh,
        uu_tien_khu_vuc=tc.uu_tien_khu_vuc,
        page=1,
        page_size=page_size,
        db=db,
    )


@router.get("/luot", response_model=LuotTimTruong)
def lay_luot_tim_truong(
    db: Session = Depends(get_db),
    user: NguoiDung | None = Depends(get_optional_user),
) -> LuotTimTruong:
    """Hạn mức tìm trường phù hợp trong ngày theo cấu hình đang áp dụng, kèm số lượt đã dùng nếu đã đăng nhập."""
    return _luot(db, cau_hinh_dang_ap_dung(db), user)


@router.post("", response_model=TimTruongPhuHopResult)
def tim_truong_phu_hop(
    payload: TimTruongPhuHopRequest,
    db: Session = Depends(get_db),
    user: NguoiDung = Depends(get_current_user),
) -> TimTruongPhuHopResult:
    """Ghi một lượt tìm trường phù hợp của thành viên vào tn_lich_su_tim_truong_phu_hop.

    Trừ một lượt khi tìm thành công; hết lượt trong ngày thì trả 429. Gửi lại cùng ma_yeu_cau
    thì trả về kết quả cũ, không trừ thêm lượt.
    """
    cu = db.scalar(select(TnLichSuTimTruongPhuHop).where(TnLichSuTimTruongPhuHop.ma_yeu_cau == payload.ma_yeu_cau))
    if cu is not None:
        if cu.tai_khoan_id != user.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Mã yêu cầu đã được sử dụng")
        return _ket_qua(db, cu, user)

    cau_hinh = cau_hinh_dang_ap_dung(db)
    if _da_dung_hom_nay(db, user.id) >= cau_hinh.so_luot_tra_cuu_thanh_vien_ngay:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Bạn đã dùng hết {cau_hinh.so_luot_tra_cuu_thanh_vien_ngay} lượt tìm trường phù hợp hôm nay",
        )

    item = TnLichSuTimTruongPhuHop(
        tai_khoan_id=user.id,
        ma_yeu_cau=payload.ma_yeu_cau,
        ma_nganh=payload.ma_nganh,
        nam_tuyen_sinh=payload.nam_tuyen_sinh,
        du_lieu_nang_luc=payload.du_lieu_nang_luc,
        du_lieu_tai_chinh=payload.du_lieu_tai_chinh,
        tieu_chi_tim_kiem=payload.tieu_chi_tim_kiem.model_dump(),
        loai_luot="mien_phi",
        phien_ban_thuat_toan=_PHIEN_BAN_THUAT_TOAN,
        trang_thai_xu_ly="dang_xu_ly",
    )
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        # Hai request cùng mã gửi đồng thời: lấy bản ghi đã được lưu trước.
        db.rollback()
        cu = db.scalar(
            select(TnLichSuTimTruongPhuHop).where(TnLichSuTimTruongPhuHop.ma_yeu_cau == payload.ma_yeu_cau)
        )
        if cu is None or cu.tai_khoan_id != user.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Mã yêu cầu đã được sử dụng") from None
        return _ket_qua(db, cu, user)
    db.refresh(item)

    try:
        tat_ca = _dem_truong(db, payload, loc=False)
        phu_hop = _dem_truong(db, payload, loc=True, page_size=_SO_TRUONG_LUU)
        item.so_truong_tim_thay = tat_ca.total
        item.so_truong_phu_hop_so_bo = phu_hop.total
        item.du_lieu_ket_qua = {
            "truong": [
                {"ma_truong": t.ma_truong, "ten_truong": t.ten_truong, "so_chuong_trinh": t.so_chuong_trinh}
                for t in phu_hop.items
            ]
        }
        item.trang_thai_xu_ly = "thanh_cong"
        item.da_tinh_luot = 1
    except Exception as exc:  # noqa: BLE001 - lưu lại lỗi để tra soát, không trừ lượt
        db.rollback()
        item = db.get(TnLichSuTimTruongPhuHop, item.id)
        item.trang_thai_xu_ly = "that_bai"
        item.thong_bao_loi = str(exc)[:2000]
    item.ngay_hoan_thanh = datetime.now()
    db.commit()
    db.refresh(item)
    if item.trang_thai_xu_ly == "that_bai":
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Không tìm được trường phù hợp")
    return _ket_qua(db, item, user)
