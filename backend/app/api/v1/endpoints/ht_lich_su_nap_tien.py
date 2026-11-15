from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_current_user
from app.db.session import get_db
from app.models.ht_cau_hinh_goi_cuoc import HtCauHinhGoiCuoc
from app.models.ht_lich_su_nap_tien import HtLichSuNapTien
from app.models.ht_ngan_hang_thanh_toan import HtNganHangThanhToan
from app.models.nguoi_dung import NguoiDung
from app.schemas.ht_cau_hinh_goi_cuoc import LoaiApDung
from app.schemas.ht_lich_su_nap_tien import (
    NapTienCapNhat,
    NapTienPage,
    NapTienPublic,
    NapTienQuanTri,
    NapTienQuanTriPage,
    NapTienTao,
    NapTienTuChoi,
    NapTienXacNhan,
)
from app.services import nap_tien

# Thành viên: tạo và xem giao dịch nạp tiền của chính mình.
member_router = APIRouter(
    prefix="/tai-khoan/nap-tien",
    tags=["tai-khoan"],
    dependencies=[Depends(get_current_user)],
)

# Admin: xem toàn bộ, xác nhận hoặc từ chối giao dịch.
router = APIRouter(
    prefix="/he-thong/lich-su-nap-tien",
    tags=["he-thong"],
    dependencies=[Depends(get_admin_user)],
)

# Bấm Đăng ký lại cùng gói trong khoảng này thì dùng lại giao dịch đang chờ, không sinh giao dịch mới.
_DUNG_LAI_TRONG = timedelta(hours=24)


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _get_or_400(db: Session, item_id: int, nguoi_dung_id: int | None = None) -> HtLichSuNapTien:
    """Lấy giao dịch theo id (giới hạn theo người nạp nếu truyền vào). Không có thì trả 400 kèm thông báo."""
    item = db.get(HtLichSuNapTien, item_id)
    if item is None or (nguoi_dung_id is not None and item.nguoi_dung_id != nguoi_dung_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy giao dịch nạp tiền có id = {item_id}",
        )
    return item


def _ngan_hang_dang_hoat_dong(db: Session, ngan_hang_id: int) -> HtNganHangThanhToan:
    ngan_hang = db.get(HtNganHangThanhToan, ngan_hang_id)
    if ngan_hang is None or ngan_hang.trang_thai != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy ngân hàng thanh toán đang hoạt động có id = {ngan_hang_id}",
        )
    return ngan_hang


def _gan_ngan_hang(giao_dich: HtLichSuNapTien, ngan_hang: HtNganHangThanhToan) -> None:
    giao_dich.ngan_hang_thanh_toan_id = ngan_hang.id
    giao_dich.ten_ngan_hang_viet_tat = ngan_hang.ten_ngan_hang_viet_tat
    giao_dich.so_tai_khoan_nhan = ngan_hang.so_tai_khoan
    giao_dich.chu_tai_khoan_nhan = ngan_hang.chu_tai_khoan


def _chi_khi_cho(giao_dich: HtLichSuNapTien) -> None:
    if giao_dich.trang_thai != nap_tien.CHO_THANH_TOAN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Giao dịch {giao_dich.ma_giao_dich} không ở trạng thái chờ thanh toán",
        )


# ---------- Thành viên ----------


@member_router.get("", response_model=NapTienPage)
def list_nap_tien_cua_toi(
    q: str | None = Query(default=None, max_length=255),
    trang_thai: int | None = Query(default=None, ge=0, le=3),
    loai_ap_dung: LoaiApDung | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    user: NguoiDung = Depends(get_current_user),
) -> NapTienPage:
    """Lịch sử nạp tiền của tài khoản đang đăng nhập, mới nhất trước. Lọc theo mã giao dịch/tên gói, trạng thái, loại."""
    filters = [HtLichSuNapTien.nguoi_dung_id == user.id]
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                HtLichSuNapTien.ma_giao_dich.like(pattern, escape="\\"),
                HtLichSuNapTien.ten_goi_cuoc.like(pattern, escape="\\"),
            )
        )
    if trang_thai is not None:
        filters.append(HtLichSuNapTien.trang_thai == trang_thai)
    if loai_ap_dung:
        filters.append(HtLichSuNapTien.loai_ap_dung == loai_ap_dung)

    total = db.scalar(select(func.count()).select_from(HtLichSuNapTien).where(*filters)) or 0
    items = db.scalars(
        select(HtLichSuNapTien)
        .where(*filters)
        .order_by(HtLichSuNapTien.created_at.desc(), HtLichSuNapTien.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return NapTienPage(items=items, total=total, page=page, page_size=page_size)


@member_router.post("", response_model=NapTienPublic, status_code=status.HTTP_201_CREATED)
def tao_nap_tien(
    payload: NapTienTao,
    db: Session = Depends(get_db),
    user: NguoiDung = Depends(get_current_user),
) -> HtLichSuNapTien:
    """Đăng ký gói cước: tạo giao dịch chờ thanh toán với mã giao dịch làm nội dung chuyển khoản.

    Đã có giao dịch đang chờ cùng gói trong 24 giờ thì dùng lại giao dịch đó.
    """
    goi = db.get(HtCauHinhGoiCuoc, payload.goi_cuoc_id)
    if goi is None or goi.trang_thai != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy gói cước đang bán có id = {payload.goi_cuoc_id}",
        )
    ngan_hang = _ngan_hang_dang_hoat_dong(db, payload.ngan_hang_thanh_toan_id) if payload.ngan_hang_thanh_toan_id else None

    gia = goi.gia_khuyen_mai if goi.gia_khuyen_mai is not None else goi.gia_goc
    so_luot = goi.so_luot_nhan_duoc_khuyen_mai if goi.so_luot_nhan_duoc_khuyen_mai is not None else goi.so_luot_nhan_duoc_goc

    giao_dich = db.scalar(
        select(HtLichSuNapTien)
        .where(
            HtLichSuNapTien.nguoi_dung_id == user.id,
            HtLichSuNapTien.goi_cuoc_dang_ky_id == goi.id,
            HtLichSuNapTien.trang_thai == nap_tien.CHO_THANH_TOAN,
            HtLichSuNapTien.so_tien_nap == gia,
            HtLichSuNapTien.so_luot_nhan_duoc == so_luot,
            HtLichSuNapTien.created_at >= datetime.now() - _DUNG_LAI_TRONG,
        )
        .order_by(HtLichSuNapTien.id.desc())
        .limit(1)
    )
    if giao_dich is None:
        ma = nap_tien.tao_ma_giao_dich(db)
        giao_dich = HtLichSuNapTien(
            ma_giao_dich=ma,
            nguoi_dung_id=user.id,
            goi_cuoc_dang_ky_id=goi.id,
            ma_goi_cuoc=goi.ma_goi_cuoc,
            ten_goi_cuoc=goi.ten_goi_cuoc,
            loai_ap_dung=goi.loai_ap_dung,
            so_luot_nhan_duoc=so_luot,
            so_tien_nap=gia,
            noi_dung_chuyen_khoan=ma,
            trang_thai=nap_tien.CHO_THANH_TOAN,
        )
        db.add(giao_dich)
    if ngan_hang is not None:
        _gan_ngan_hang(giao_dich, ngan_hang)
    db.commit()
    db.refresh(giao_dich)
    return giao_dich


@member_router.patch("/{item_id}", response_model=NapTienPublic)
def cap_nhat_nap_tien(
    item_id: int,
    payload: NapTienCapNhat,
    db: Session = Depends(get_db),
    user: NguoiDung = Depends(get_current_user),
) -> HtLichSuNapTien:
    """Đổi ngân hàng chuyển khoản hoặc báo đã chuyển khoản cho giao dịch đang chờ của mình."""
    giao_dich = _get_or_400(db, item_id, user.id)
    _chi_khi_cho(giao_dich)
    if payload.ngan_hang_thanh_toan_id is not None:
        _gan_ngan_hang(giao_dich, _ngan_hang_dang_hoat_dong(db, payload.ngan_hang_thanh_toan_id))
    if payload.da_chuyen_khoan and giao_dich.thoi_gian_thanh_toan is None:
        giao_dich.thoi_gian_thanh_toan = datetime.now()
    db.commit()
    db.refresh(giao_dich)
    return giao_dich


@member_router.post("/{item_id}/huy", response_model=NapTienPublic)
def huy_nap_tien(
    item_id: int,
    db: Session = Depends(get_db),
    user: NguoiDung = Depends(get_current_user),
) -> HtLichSuNapTien:
    """Hủy giao dịch đang chờ thanh toán của mình."""
    giao_dich = _get_or_400(db, item_id, user.id)
    _chi_khi_cho(giao_dich)
    giao_dich.trang_thai = nap_tien.DA_HUY
    db.commit()
    db.refresh(giao_dich)
    return giao_dich


# ---------- Admin ----------


def _quan_tri(giao_dich: HtLichSuNapTien, nguoi_dung: NguoiDung | None) -> NapTienQuanTri:
    data = NapTienQuanTri.model_validate(giao_dich)
    if nguoi_dung is not None:
        data.ho_ten = nguoi_dung.ho_ten
        data.email = nguoi_dung.email
    return data


@router.get("", response_model=NapTienQuanTriPage)
def list_lich_su_nap_tien(
    q: str | None = Query(default=None, max_length=255),
    trang_thai: int | None = Query(default=None, ge=0, le=3),
    loai_ap_dung: LoaiApDung | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> NapTienQuanTriPage:
    """Toàn bộ lịch sử nạp tiền, mới nhất trước.

    Lọc theo từ khóa (mã giao dịch, tên gói, mã tham chiếu, họ tên/email người nạp), trạng thái và loại.
    """
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                HtLichSuNapTien.ma_giao_dich.like(pattern, escape="\\"),
                HtLichSuNapTien.ten_goi_cuoc.like(pattern, escape="\\"),
                HtLichSuNapTien.ma_tham_chieu_ngan_hang.like(pattern, escape="\\"),
                NguoiDung.ho_ten.like(pattern, escape="\\"),
                NguoiDung.email.like(pattern, escape="\\"),
            )
        )
    if trang_thai is not None:
        filters.append(HtLichSuNapTien.trang_thai == trang_thai)
    if loai_ap_dung:
        filters.append(HtLichSuNapTien.loai_ap_dung == loai_ap_dung)

    base = select(HtLichSuNapTien, NguoiDung).outerjoin(NguoiDung, NguoiDung.id == HtLichSuNapTien.nguoi_dung_id)
    count_stmt = (
        select(func.count())
        .select_from(HtLichSuNapTien)
        .outerjoin(NguoiDung, NguoiDung.id == HtLichSuNapTien.nguoi_dung_id)
    )
    if filters:
        base = base.where(*filters)
        count_stmt = count_stmt.where(*filters)
    total = db.scalar(count_stmt) or 0
    rows = db.execute(
        base.order_by(HtLichSuNapTien.created_at.desc(), HtLichSuNapTien.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return NapTienQuanTriPage(
        items=[_quan_tri(giao_dich, nguoi_dung) for giao_dich, nguoi_dung in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/{item_id}/xac-nhan", response_model=NapTienQuanTri)
def xac_nhan_nap_tien(
    item_id: int,
    payload: NapTienXacNhan,
    db: Session = Depends(get_db),
    admin: NguoiDung = Depends(get_admin_user),
) -> NapTienQuanTri:
    """Xác nhận đã nhận tiền: chuyển sang thành công và cộng Edu coin/lượt cho người nạp."""
    giao_dich = db.scalar(select(HtLichSuNapTien).where(HtLichSuNapTien.id == item_id).with_for_update())
    if giao_dich is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy giao dịch nạp tiền có id = {item_id}",
        )
    nap_tien.xac_nhan_thanh_cong(
        db,
        giao_dich,
        so_tien_thuc_nhan=payload.so_tien_thuc_nhan,
        ma_tham_chieu=payload.ma_tham_chieu_ngan_hang,
        nguoi_xac_nhan_id=admin.id,
        ghi_chu=payload.ghi_chu,
    )
    db.commit()
    db.refresh(giao_dich)
    nguoi_dung = db.get(NguoiDung, giao_dich.nguoi_dung_id) if giao_dich.nguoi_dung_id else None
    return _quan_tri(giao_dich, nguoi_dung)


@router.post("/{item_id}/tu-choi", response_model=NapTienQuanTri)
def tu_choi_nap_tien(
    item_id: int,
    payload: NapTienTuChoi,
    db: Session = Depends(get_db),
    admin: NguoiDung = Depends(get_admin_user),
) -> NapTienQuanTri:
    """Từ chối giao dịch đang chờ (không nhận được tiền): chuyển sang thất bại, không cộng số dư."""
    giao_dich = _get_or_400(db, item_id)
    _chi_khi_cho(giao_dich)
    giao_dich.trang_thai = nap_tien.THAT_BAI
    giao_dich.ghi_chu = payload.ghi_chu
    giao_dich.thoi_gian_xac_nhan = datetime.now()
    giao_dich.nguoi_xac_nhan_id = admin.id
    db.commit()
    db.refresh(giao_dich)
    nguoi_dung = db.get(NguoiDung, giao_dich.nguoi_dung_id) if giao_dich.nguoi_dung_id else None
    return _quan_tri(giao_dich, nguoi_dung)
