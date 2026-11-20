import logging
from dataclasses import asdict
from datetime import date, datetime, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_current_user, get_optional_user
from app.core.config import settings
from app.core.thoi_gian import bay_gio
from app.db.session import get_db
from app.models.dm_nganh_dao_tao import DmNganhDaoTao
from app.models.ht_cau_hinh_tra_cuu import HtCauHinhTraCuu
from app.models.nguoi_dung import NguoiDung
from app.models.nguoi_dung_thong_tin import NguoiDungThongTin
from app.models.tn_lich_su_tim_truong_phu_hop import TnLichSuTimTruongPhuHop
from app.schemas.tn_lich_su_tim_truong_phu_hop import (
    MA_THIET_BI_PATTERN,
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
from app.services.ho_so_xet_tuyen import DanhMucMa, doc_ho_so, ho_so_chinh
from app.services.xet_tuyen.chuyen_ho_so import DanhMucHoSo, tu_du_lieu_khach, tu_ho_so_hs, tu_ho_so_thanh_vien
from app.services.xet_tuyen.danh_gia import chay_danh_gia, co_de_an_dang_ap_dung

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tim-truong-phu-hop", tags=["tim-truong-phu-hop"])

_PHIEN_BAN_THUAT_TOAN = "loc-co-ban-v1"
# Lượt tìm có thêm kết quả của bộ tính xét tuyển (đề án "đang áp dụng").
PHIEN_BAN_XET_TUYEN = "xt-v1"
# Số trường đầu tiên lưu lại trong du_lieu_ket_qua.
_SO_TRUONG_LUU = 50


def _cua_nguoi_tim(user: NguoiDung | None, ma_thiet_bi: str | None):
    """Điều kiện chọn lượt của người đang tìm: thành viên theo tài khoản, khách theo mã thiết bị."""
    if user is not None:
        return TnLichSuTimTruongPhuHop.tai_khoan_id == user.id
    return (TnLichSuTimTruongPhuHop.tai_khoan_id.is_(None)) & (TnLichSuTimTruongPhuHop.ma_thiet_bi == ma_thiet_bi)


def _da_dung_hom_nay(db: Session, user: NguoiDung | None, ma_thiet_bi: str | None) -> int:
    """Số lượt miễn phí đã tính từ đầu ngày (theo giờ của database); lượt trừ vào lượt tra cứu đã mua không tính."""
    return db.scalar(
        select(func.count())
        .select_from(TnLichSuTimTruongPhuHop)
        .where(
            _cua_nguoi_tim(user, ma_thiet_bi),
            TnLichSuTimTruongPhuHop.da_tinh_luot == 1,
            TnLichSuTimTruongPhuHop.loai_luot == "mien_phi",
            TnLichSuTimTruongPhuHop.ngay_tao >= func.curdate(),
        )
    ) or 0


def _ho_so(db: Session, user: NguoiDung, khoa: bool = False) -> NguoiDungThongTin | None:
    stmt = select(NguoiDungThongTin).where(NguoiDungThongTin.nguoi_dung_id == user.id)
    return db.scalar(stmt.with_for_update() if khoa else stmt)


def _cong_luot_tra_cuu(db: Session, user: NguoiDung, so: int) -> None:
    """Cộng (hoặc trừ khi so < 0) lượt tra cứu đã mua của thành viên. Chưa commit."""
    ho_so = _ho_so(db, user, khoa=True)
    if ho_so is not None:
        ho_so.luot_tra_cuu = max((ho_so.luot_tra_cuu or 0) + so, 0)


def _la_cua_nguoi_tim(item: TnLichSuTimTruongPhuHop, user: NguoiDung | None, ma_thiet_bi: str | None) -> bool:
    if user is not None:
        return item.tai_khoan_id == user.id
    return item.tai_khoan_id is None and item.ma_thiet_bi == ma_thiet_bi


def _luot(
    db: Session, cau_hinh: HtCauHinhTraCuu, user: NguoiDung | None, ma_thiet_bi: str | None = None
) -> LuotTimTruong:
    khach = cau_hinh.so_luot_tra_cuu_khach_ngay
    thanh_vien = cau_hinh.so_luot_tra_cuu_thanh_vien_ngay
    ket_hop = settings.tim_truong_ket_hop_phuong_thuc
    if user is None:
        da_dung_khach = _da_dung_hom_nay(db, None, ma_thiet_bi) if ma_thiet_bi else None
        return LuotTimTruong(
            la_thanh_vien=False,
            so_luot_ngay=khach,
            so_luot_khach_ngay=khach,
            so_luot_thanh_vien_ngay=thanh_vien,
            da_dung=da_dung_khach,
            con_lai=max(khach - da_dung_khach, 0) if da_dung_khach is not None else None,
            ket_hop_phuong_thuc=ket_hop,
        )
    da_dung = _da_dung_hom_nay(db, user, None)
    ho_so = _ho_so(db, user)
    return LuotTimTruong(
        la_thanh_vien=True,
        so_luot_ngay=thanh_vien,
        so_luot_khach_ngay=khach,
        so_luot_thanh_vien_ngay=thanh_vien,
        da_dung=da_dung,
        con_lai=max(thanh_vien - da_dung, 0),
        luot_tra_cuu=(ho_so.luot_tra_cuu or 0) if ho_so is not None else 0,
        ket_hop_phuong_thuc=ket_hop,
    )


def _ket_qua(
    db: Session, item: TnLichSuTimTruongPhuHop, user: NguoiDung | None, ma_thiet_bi: str | None
) -> TimTruongPhuHopResult:
    return TimTruongPhuHopResult(
        lich_su_id=item.id,
        ma_yeu_cau=item.ma_yeu_cau,
        trang_thai_xu_ly=item.trang_thai_xu_ly,
        so_truong_tim_thay=item.so_truong_tim_thay,
        so_truong_phu_hop_so_bo=item.so_truong_phu_hop_so_bo,
        luot=_luot(db, cau_hinh_dang_ap_dung(db), user, ma_thiet_bi),
        lan_danh_gia_id=((item.du_lieu_ket_qua or {}).get("xet_tuyen") or {}).get("lan_danh_gia_id"),
    )


def _ho_so_xet_tuyen_hs(db: Session, user: NguoiDung, nam: int):
    """Hồ sơ xét tuyển hs_* chính của thành viên (đủ thông tin hơn JSON cũ); (None, None) nếu chưa có.

    Đọc trong savepoint riêng để CSDL chưa có bảng hs_* thì quay về dùng hồ sơ năng lực cũ.
    """
    try:
        with db.begin_nested():
            hs = ho_so_chinh(db, user.id)
            if hs is None:
                return None, None
            return tu_ho_so_hs(doc_ho_so(db, hs, DanhMucMa.tu_csdl(db)), nam_tuyen_sinh=nam), hs.id
    except Exception:  # noqa: BLE001 - thiếu bảng / dữ liệu lỗi: dùng hồ sơ năng lực cũ
        logger.exception("Không đọc được hồ sơ xét tuyển hs_* của người dùng %s", user.id)
        return None, None


def _danh_gia_xet_tuyen(
    db: Session, item: TnLichSuTimTruongPhuHop, payload: TimTruongPhuHopRequest, user: NguoiDung | None
) -> None:
    """Năm có đề án "đang áp dụng" thì chạy thêm bộ tính xét tuyển (xt-v1) cho chương trình của ngành đang tìm.

    Chạy trong savepoint riêng: lỗi ở đây chỉ ghi log, lượt tìm vẫn thành công với kết quả của thuật toán cũ.
    """
    nam = payload.nam_tuyen_sinh
    try:
        if not co_de_an_dang_ap_dung(db, nam):
            return
        ho_so_id = None
        ho_so_xt = None
        if user is not None:
            ho_so_xt, ho_so_id = _ho_so_xet_tuyen_hs(db, user, nam)
        with db.begin_nested():
            danh_muc = DanhMucHoSo.tu_csdl(db)
            # Thứ tự nguồn hồ sơ: hs_* của thành viên → hồ sơ năng lực cũ (JSON) → form của khách.
            if ho_so_xt is None and user is not None:
                ho_so = _ho_so(db, user)
                ho_so_xt = tu_ho_so_thanh_vien(
                    ho_so.trinh_do_hoc_van if ho_so else None,
                    nam_tuyen_sinh=nam,
                    danh_muc=danh_muc,
                    khu_vuc_uu_tien_id=ho_so.khu_vuc_uu_tien_id if ho_so else None,
                    doi_tuong_uu_tien_id=ho_so.doi_tuong_uu_tien_id if ho_so else None,
                    tinh_thanh_id=ho_so.tinh_thanh_id if ho_so else None,
                    kha_nang_tai_chinh=ho_so.kha_nang_tai_chinh if ho_so else None,
                )
            elif ho_so_xt is None:
                ho_so_xt = tu_du_lieu_khach(
                    payload.du_lieu_nang_luc, payload.du_lieu_tai_chinh, nam_tuyen_sinh=nam, danh_muc=danh_muc
                )
            ket_qua = chay_danh_gia(
                db,
                ho_so_xt,
                nam=nam,
                ma_nganh=payload.ma_nganh,
                nguoi_dung_id=user.id if user else None,
                ma_thiet_bi=payload.ma_thiet_bi,
                lich_su_tim_truong_id=item.id,
                ho_so_id=ho_so_id,
            )
    except Exception:  # noqa: BLE001 - bộ tính mới lỗi không được làm hỏng lượt tìm
        logger.exception("Không chạy được bộ tính xét tuyển cho lượt tìm %s", item.id)
        return
    if ket_qua is None:
        return
    item.phien_ban_thuat_toan = PHIEN_BAN_XET_TUYEN
    item.du_lieu_ket_qua = {**(item.du_lieu_ket_qua or {}), "xet_tuyen": asdict(ket_qua)}


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
    ma_thiet_bi: str | None = Query(default=None, pattern=MA_THIET_BI_PATTERN),
    db: Session = Depends(get_db),
    user: NguoiDung | None = Depends(get_optional_user),
) -> LuotTimTruong:
    """Hạn mức tìm trường phù hợp trong ngày theo cấu hình đang áp dụng, kèm số lượt đã dùng.

    Khách vãng lai gửi ma_thiet_bi để biết số lượt đã dùng trên thiết bị đó.
    """
    return _luot(db, cau_hinh_dang_ap_dung(db), user, ma_thiet_bi)


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
    page_size: int = Query(default=12, ge=1),
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
    user: NguoiDung | None = Depends(get_optional_user),
) -> TimTruongPhuHopResult:
    """Ghi một lượt tìm trường phù hợp vào tn_lich_su_tim_truong_phu_hop.

    Thành viên đếm lượt theo tài khoản. Khách vãng lai bắt buộc gửi ma_thiet_bi để đếm lượt theo thiết bị,
    kèm thông tin liên hệ nếu có. Dùng lượt miễn phí trong ngày trước; thành viên hết lượt miễn phí thì trừ 1
    lượt tra cứu đã mua (loai_luot = tra_phi), tìm lỗi thì hoàn lại. Hết cả hai thì trả 429.
    Gửi lại cùng ma_yeu_cau thì trả về kết quả cũ, không trừ thêm lượt.
    """
    ma_thiet_bi = payload.ma_thiet_bi
    if user is None and not ma_thiet_bi:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Thiếu mã thiết bị của khách")

    cu = db.scalar(select(TnLichSuTimTruongPhuHop).where(TnLichSuTimTruongPhuHop.ma_yeu_cau == payload.ma_yeu_cau))
    if cu is not None:
        if not _la_cua_nguoi_tim(cu, user, ma_thiet_bi):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Mã yêu cầu đã được sử dụng")
        return _ket_qua(db, cu, user, ma_thiet_bi)

    cau_hinh = cau_hinh_dang_ap_dung(db)
    toi_da = cau_hinh.so_luot_tra_cuu_thanh_vien_ngay if user else cau_hinh.so_luot_tra_cuu_khach_ngay
    loai_luot = "mien_phi"
    if _da_dung_hom_nay(db, user, ma_thiet_bi) >= toi_da:
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Bạn đã dùng hết {toi_da} lượt tìm trường phù hợp hôm nay",
            )
        # Hết lượt miễn phí: trừ lượt tra cứu đã mua (khóa dòng để hai request đồng thời không cùng trừ 1 lượt).
        ho_so = _ho_so(db, user, khoa=True)
        if ho_so is None or (ho_so.luot_tra_cuu or 0) <= 0:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Bạn đã dùng hết {toi_da} lượt miễn phí hôm nay và không còn lượt tra cứu. "
                "Vui lòng nạp thêm lượt tra cứu.",
            )
        ho_so.luot_tra_cuu -= 1
        loai_luot = "tra_phi"

    thong_tin_khach = None
    if user is None and payload.thong_tin_khach is not None:
        thong_tin_khach = payload.thong_tin_khach.model_dump(exclude_none=True) or None
    item = TnLichSuTimTruongPhuHop(
        tai_khoan_id=user.id if user else None,
        ma_thiet_bi=ma_thiet_bi,
        thong_tin_khach=thong_tin_khach,
        ma_yeu_cau=payload.ma_yeu_cau,
        ma_nganh=payload.ma_nganh,
        nam_tuyen_sinh=payload.nam_tuyen_sinh,
        du_lieu_nang_luc=payload.du_lieu_nang_luc,
        du_lieu_tai_chinh=payload.du_lieu_tai_chinh,
        tieu_chi_tim_kiem=payload.tieu_chi_tim_kiem.model_dump(),
        loai_luot=loai_luot,
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
        if cu is None or not _la_cua_nguoi_tim(cu, user, ma_thiet_bi):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Mã yêu cầu đã được sử dụng") from None
        return _ket_qua(db, cu, user, ma_thiet_bi)
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
        if item.loai_luot == "tra_phi" and user is not None:
            _cong_luot_tra_cuu(db, user, 1)
    if item.trang_thai_xu_ly == "thanh_cong":
        _danh_gia_xet_tuyen(db, item, payload, user)
    item.ngay_hoan_thanh = bay_gio()
    db.commit()
    db.refresh(item)
    if item.trang_thai_xu_ly == "that_bai":
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Không tìm được trường phù hợp")
    return _ket_qua(db, item, user, ma_thiet_bi)


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
    la_khach = item.tai_khoan_id is None
    if la_khach:
        # Khách không có tài khoản: hiển thị thông tin liên hệ khách tự nhập.
        khach = item.thong_tin_khach or {}
        ho_ten, email, so_dien_thoai = khach.get("ho_ten"), khach.get("email"), khach.get("so_dien_thoai")
    return model(
        **data,
        la_khach=la_khach,
        ho_ten=ho_ten,
        email=email,
        so_dien_thoai=so_dien_thoai,
        ten_nganh=ten_nganh,
    )


def _truong_khach(key: str):
    return func.json_unquote(func.json_extract(TnLichSuTimTruongPhuHop.thong_tin_khach, f"$.{key}"))


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
    doi_tuong: Literal["thanh-vien", "khach"] | None = Query(default=None),
    tu_ngay: date | None = Query(default=None),
    den_ngay: date | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),  # Quản trị: không giới hạn số dòng mỗi trang.
    db: Session = Depends(get_db),
) -> LichSuTimTruongQuanTriPage:
    """Lịch sử tìm trường phù hợp của mọi tài khoản, mới nhất trước.

    Lọc theo người dùng (tên, email, SĐT của tài khoản hoặc khách tự nhập), từ khóa (mã yêu cầu,
    mã/tên ngành), năm tuyển sinh, loại lượt, trạng thái xử lý, đã mở khóa báo cáo, thành viên/khách
    và khoảng ngày tạo.
    """
    filters = _dieu_kien_loc(q, nam_tuyen_sinh, loai_luot, trang_thai_xu_ly, da_mo_khoa, tu_ngay, den_ngay)
    if nguoi_dung and nguoi_dung.strip():
        pattern = _like_pattern(nguoi_dung.strip())
        filters.append(
            or_(
                NguoiDung.ho_ten.like(pattern, escape="\\"),
                NguoiDung.email.like(pattern, escape="\\"),
                NguoiDung.so_dien_thoai.like(pattern, escape="\\"),
                _truong_khach("ho_ten").like(pattern, escape="\\"),
                _truong_khach("email").like(pattern, escape="\\"),
                _truong_khach("so_dien_thoai").like(pattern, escape="\\"),
            )
        )
    if doi_tuong == "khach":
        filters.append(TnLichSuTimTruongPhuHop.tai_khoan_id.is_(None))
    elif doi_tuong == "thanh-vien":
        filters.append(TnLichSuTimTruongPhuHop.tai_khoan_id.is_not(None))

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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy lượt tìm trường có id = {item_id}",
        )
    return _quan_tri_public(row, chi_tiet=True)


@router.get("/cua-toi", response_model=LichSuTimTruongQuanTriPage)
def lich_su_tim_truong_cua_toi(
    q: str | None = Query(default=None, max_length=255),
    nam_tuyen_sinh: int | None = Query(default=None, ge=1990, le=2100),
    trang_thai_xu_ly: Literal["cho_xu_ly", "dang_xu_ly", "thanh_cong", "that_bai"] | None = Query(default=None),
    tu_ngay: date | None = Query(default=None),
    den_ngay: date | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy lượt tìm trường có id = {item_id}",
        )
    return _quan_tri_public(row, chi_tiet=True)
