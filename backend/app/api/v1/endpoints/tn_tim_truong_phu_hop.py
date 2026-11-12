from datetime import date, datetime, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_current_user, get_optional_user
from app.core.config import settings
from app.db.session import get_db
from app.models.dm_nganh_dao_tao import DmNganhDaoTao
from app.models.ht_cau_hinh_tra_cuu import HtCauHinhTraCuu
from app.models.nguoi_dung import NguoiDung
from app.models.tn_lich_su_tim_truong_phu_hop import TnLichSuTimTruongPhuHop
from app.schemas.tn_lich_su_tim_truong_phu_hop import (
    LichSuTimTruongQuanTri,
    LichSuTimTruongQuanTriChiTiet,
    LichSuTimTruongQuanTriPage,
    LuotTimTruong,
    TimTruongPhuHopRequest,
    TimTruongPhuHopResult,
)
from app.schemas.dats_tuyen_sinh import TruongDaoTaoPage
from app.services.cau_hinh_tra_cuu import cau_hinh_dang_ap_dung
from app.services.tim_truong import truong_theo_nganh

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
    ket_hop = settings.tim_truong_ket_hop_phuong_thuc
    if user is None:
        return LuotTimTruong(
            la_thanh_vien=False,
            so_luot_ngay=khach,
            so_luot_khach_ngay=khach,
            so_luot_thanh_vien_ngay=thanh_vien,
            ket_hop_phuong_thuc=ket_hop,
        )
    da_dung = _da_dung_hom_nay(db, user.id)
    return LuotTimTruong(
        la_thanh_vien=True,
        so_luot_ngay=thanh_vien,
        so_luot_khach_ngay=khach,
        so_luot_thanh_vien_ngay=thanh_vien,
        da_dung=da_dung,
        con_lai=max(thanh_vien - da_dung, 0),
        ket_hop_phuong_thuc=ket_hop,
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
    """Cùng truy vấn với danh sách /tim-truong-phu-hop/truong. loc=False thì bỏ mọi tiêu chí lọc."""
    tc = payload.tieu_chi_tim_kiem
    return truong_theo_nganh(
        db,
        ma_nganh=payload.ma_nganh,
        nam_tuyen_sinh=payload.nam_tuyen_sinh,
        q=tc.tu_khoa if loc else None,
        vung_mien=tc.khu_vuc if loc else None,
        loai_co_so=tc.loai_co_so if loc else None,
        ten_tinh_thanh=tc.tinh if loc else None,
        sap_xep=tc.sap_xep if loc else "ten_asc",
        uu_tien_tinh=tc.uu_tien_tinh,
        uu_tien_khu_vuc=tc.uu_tien_khu_vuc,
        page=1,
        page_size=page_size,
    )


@router.get("/luot", response_model=LuotTimTruong)
def lay_luot_tim_truong(
    db: Session = Depends(get_db),
    user: NguoiDung | None = Depends(get_optional_user),
) -> LuotTimTruong:
    """Hạn mức tìm trường phù hợp trong ngày theo cấu hình đang áp dụng, kèm số lượt đã dùng nếu đã đăng nhập."""
    return _luot(db, cau_hinh_dang_ap_dung(db), user)


@router.get("/truong", response_model=TruongDaoTaoPage)
def danh_sach_truong_phu_hop(
    ma_nganh: str = Query(..., min_length=1, max_length=20),
    q: str | None = Query(default=None, max_length=255),
    vung_mien: str | None = Query(default=None, max_length=20),
    loai_co_so: str | None = Query(default=None, max_length=50),
    ten_tinh_thanh: str | None = Query(default=None, max_length=100),
    nam_tuyen_sinh: int | None = Query(default=None, ge=1990, le=2100),
    sap_xep: Literal["ten_asc", "ten_desc", "chi_tieu_desc", "chuong_trinh_desc", "gan_toi"] = Query(
        default="ten_asc"
    ),
    uu_tien_tinh: str | None = Query(default=None, max_length=100),
    uu_tien_khu_vuc: str | None = Query(default=None, max_length=20),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=100),
    db: Session = Depends(get_db),
) -> TruongDaoTaoPage:
    """Danh sách trường phù hợp của một ngành, lấy từ dm_nganh_hoc_theo_truong.

    Có kết hợp đề án/phương thức tuyển sinh hay không do cờ TIM_TRUONG_KET_HOP_PHUONG_THUC ở backend.
    Không trừ lượt; lượt chỉ tính khi gọi POST /tim-truong-phu-hop.
    """
    return truong_theo_nganh(
        db,
        ma_nganh=ma_nganh,
        nam_tuyen_sinh=nam_tuyen_sinh,
        q=q,
        vung_mien=vung_mien,
        loai_co_so=loai_co_so,
        ten_tinh_thanh=ten_tinh_thanh,
        sap_xep=sap_xep,
        uu_tien_tinh=uu_tien_tinh,
        uu_tien_khu_vuc=uu_tien_khu_vuc,
        page=page,
        page_size=page_size,
    )


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


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _cot_quan_tri():
    return (
        TnLichSuTimTruongPhuHop,
        NguoiDung.ho_ten,
        NguoiDung.email,
        NguoiDung.so_dien_thoai,
        DmNganhDaoTao.ten_nganh,
    )


def _ghep_quan_tri(stmt):
    return stmt.outerjoin(NguoiDung, NguoiDung.id == TnLichSuTimTruongPhuHop.tai_khoan_id).outerjoin(
        DmNganhDaoTao, DmNganhDaoTao.ma_nganh == TnLichSuTimTruongPhuHop.ma_nganh
    )


def _dieu_kien_loc(q, nam_tuyen_sinh, loai_luot, trang_thai_xu_ly, da_mo_khoa, tu_ngay, den_ngay) -> list:
    """Điều kiện lọc chung cho danh sách quản trị và danh sách của tôi."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                TnLichSuTimTruongPhuHop.ma_yeu_cau.like(pattern, escape="\\"),
                TnLichSuTimTruongPhuHop.ma_nganh.like(pattern, escape="\\"),
                DmNganhDaoTao.ten_nganh.like(pattern, escape="\\"),
            )
        )
    if nam_tuyen_sinh is not None:
        filters.append(TnLichSuTimTruongPhuHop.nam_tuyen_sinh == nam_tuyen_sinh)
    if loai_luot:
        filters.append(TnLichSuTimTruongPhuHop.loai_luot == loai_luot)
    if trang_thai_xu_ly:
        filters.append(TnLichSuTimTruongPhuHop.trang_thai_xu_ly == trang_thai_xu_ly)
    if da_mo_khoa is not None:
        filters.append(TnLichSuTimTruongPhuHop.da_mo_khoa_chuyen_sau == (1 if da_mo_khoa else 0))
    if tu_ngay:
        filters.append(TnLichSuTimTruongPhuHop.ngay_tao >= datetime.combine(tu_ngay, datetime.min.time()))
    if den_ngay:
        filters.append(
            TnLichSuTimTruongPhuHop.ngay_tao < datetime.combine(den_ngay + timedelta(days=1), datetime.min.time())
        )
    return filters


def _trang_lich_su(db: Session, filters: list, page: int, page_size: int) -> LichSuTimTruongQuanTriPage:
    total = db.scalar(
        _ghep_quan_tri(select(func.count()).select_from(TnLichSuTimTruongPhuHop)).where(*filters)
    ) or 0
    rows = db.execute(
        _ghep_quan_tri(select(*_cot_quan_tri()))
        .where(*filters)
        .order_by(TnLichSuTimTruongPhuHop.ngay_tao.desc(), TnLichSuTimTruongPhuHop.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return LichSuTimTruongQuanTriPage(
        items=[_quan_tri_public(row) for row in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


def _quan_tri_public(row, chi_tiet: bool = False):
    item, ho_ten, email, so_dien_thoai, ten_nganh = row
    model = LichSuTimTruongQuanTriChiTiet if chi_tiet else LichSuTimTruongQuanTri
    data = {c.name: getattr(item, c.name) for c in TnLichSuTimTruongPhuHop.__table__.columns}
    return model(**data, ho_ten=ho_ten, email=email, so_dien_thoai=so_dien_thoai, ten_nganh=ten_nganh)


@router.get(
    "/quan-tri",
    response_model=LichSuTimTruongQuanTriPage,
    dependencies=[Depends(get_admin_user)],
)
def danh_sach_lich_su_tim_truong(
    nguoi_dung: str | None = Query(default=None, max_length=255),
    q: str | None = Query(default=None, max_length=255),
    nam_tuyen_sinh: int | None = Query(default=None, ge=1990, le=2100),
    loai_luot: Literal["mien_phi", "tra_phi", "khuyen_mai"] | None = Query(default=None),
    trang_thai_xu_ly: Literal["cho_xu_ly", "dang_xu_ly", "thanh_cong", "that_bai"] | None = Query(default=None),
    da_mo_khoa: bool | None = Query(default=None),
    tu_ngay: date | None = Query(default=None),
    den_ngay: date | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
) -> LichSuTimTruongQuanTriPage:
    """Lịch sử tìm trường phù hợp của mọi tài khoản, mới nhất trước.

    Lọc theo người dùng (tên, email, SĐT), từ khóa (mã yêu cầu, mã/tên ngành), năm tuyển sinh,
    loại lượt, trạng thái xử lý, đã mở khóa báo cáo và khoảng ngày tạo.
    """
    filters = _dieu_kien_loc(q, nam_tuyen_sinh, loai_luot, trang_thai_xu_ly, da_mo_khoa, tu_ngay, den_ngay)
    if nguoi_dung and nguoi_dung.strip():
        pattern = _like_pattern(nguoi_dung.strip())
        filters.append(
            or_(
                NguoiDung.ho_ten.like(pattern, escape="\\"),
                NguoiDung.email.like(pattern, escape="\\"),
                NguoiDung.so_dien_thoai.like(pattern, escape="\\"),
            )
        )

    return _trang_lich_su(db, filters, page, page_size)


@router.get(
    "/quan-tri/{item_id}",
    response_model=LichSuTimTruongQuanTriChiTiet,
    dependencies=[Depends(get_admin_user)],
)
def chi_tiet_lich_su_tim_truong(item_id: int, db: Session = Depends(get_db)) -> LichSuTimTruongQuanTriChiTiet:
    """Chi tiết một lượt tìm trường: dữ liệu năng lực, tài chính, tiêu chí và kết quả."""
    row = db.execute(
        _ghep_quan_tri(select(*_cot_quan_tri())).where(TnLichSuTimTruongPhuHop.id == item_id)
    ).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy lượt tìm trường")
    return _quan_tri_public(row, chi_tiet=True)


@router.get("/cua-toi", response_model=LichSuTimTruongQuanTriPage)
def lich_su_tim_truong_cua_toi(
    q: str | None = Query(default=None, max_length=255),
    nam_tuyen_sinh: int | None = Query(default=None, ge=1990, le=2100),
    trang_thai_xu_ly: Literal["cho_xu_ly", "dang_xu_ly", "thanh_cong", "that_bai"] | None = Query(default=None),
    tu_ngay: date | None = Query(default=None),
    den_ngay: date | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    user: NguoiDung = Depends(get_current_user),
) -> LichSuTimTruongQuanTriPage:
    """Lịch sử tìm trường phù hợp của tài khoản đang đăng nhập, mới nhất trước."""
    filters = _dieu_kien_loc(q, nam_tuyen_sinh, None, trang_thai_xu_ly, None, tu_ngay, den_ngay)
    filters.append(TnLichSuTimTruongPhuHop.tai_khoan_id == user.id)
    return _trang_lich_su(db, filters, page, page_size)


@router.get("/cua-toi/{item_id}", response_model=LichSuTimTruongQuanTriChiTiet)
def chi_tiet_lich_su_tim_truong_cua_toi(
    item_id: int,
    db: Session = Depends(get_db),
    user: NguoiDung = Depends(get_current_user),
) -> LichSuTimTruongQuanTriChiTiet:
    """Chi tiết một lượt tìm trường của chính tài khoản đang đăng nhập."""
    row = db.execute(
        _ghep_quan_tri(select(*_cot_quan_tri())).where(
            TnLichSuTimTruongPhuHop.id == item_id,
            TnLichSuTimTruongPhuHop.tai_khoan_id == user.id,
        )
    ).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy lượt tìm trường")
    return _quan_tri_public(row, chi_tiet=True)
