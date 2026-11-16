import logging
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ValidationError
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import hash_password, verify_password
from app.db.session import get_db
from app.models.dm_doi_tuong_uu_tien import DmDoiTuongUuTien
from app.models.dm_khu_vuc_uu_tien import DmKhuVucUuTien
from app.models.dm_tinh_thanh import DmTinhThanh
from app.models.nguoi_dung import NguoiDung
from app.models.nguoi_dung_thong_tin import NguoiDungThongTin
from app.models.tn_lich_su_tim_truong_phu_hop import TnLichSuTimTruongPhuHop
from app.models.tn_phien_khao_sat import TnPhienKhaoSat
from app.schemas.auth import DoiMatKhauKetQua, DoiMatKhauRequest
from app.schemas.ho_so import (
    HoSoPublic,
    HoSoWrite,
    KhaNangTaiChinh,
    SucKhoeTheChat,
    SuDungTheoNgay,
    ThongKeSuDung,
    ThongTinCaNhanWrite,
    TrinhDoHocVan,
)

from app.services.ho_so_xet_tuyen import dong_bo_tu_json

router = APIRouter(prefix="/tai-khoan", tags=["tai-khoan"])
logger = logging.getLogger(__name__)


def _dong_bo_ho_so_xet_tuyen(db: Session, profile: NguoiDungThongTin) -> None:
    """Ghi song song: hồ sơ năng lực cũ vừa đổi thì cập nhật hồ sơ xét tuyển hs_* (nếu đã có) cho khớp.

    Chạy trong savepoint: lỗi (kể cả CSDL chưa có bảng hs_*) chỉ ghi log, việc lưu hồ sơ năng lực cũ vẫn thành công.
    """
    db.flush()
    try:
        with db.begin_nested():
            dong_bo_tu_json(db, profile, nam_tuyen_sinh=datetime.now().year)
    except Exception:  # noqa: BLE001 - đồng bộ phụ không được làm hỏng việc lưu hồ sơ chính
        logger.exception("Không đồng bộ được hồ sơ xét tuyển của người dùng %s", getattr(profile, "nguoi_dung_id", None))


def _get_profile(db: Session, user_id: int) -> NguoiDungThongTin | None:
    return db.scalar(select(NguoiDungThongTin).where(NguoiDungThongTin.nguoi_dung_id == user_id))


def _dump_block(value: BaseModel | None) -> dict | None:
    if value is None:
        return None
    data = value.model_dump(mode="json", exclude_none=True)
    return data or None


def _as_block(value: object, model: type[BaseModel]) -> BaseModel | None:
    if not isinstance(value, dict):
        return None
    try:
        parsed = model.model_validate(value)
    except ValidationError:
        return None
    dumped = _dump_block(parsed)
    if dumped is None:
        return None
    return model.model_validate(dumped)


def _to_public(user: NguoiDung, profile: NguoiDungThongTin | None) -> HoSoPublic:
    payload = {
        "nguoi_dung_id": user.id,
        "ho_ten": user.ho_ten,
        "email": user.email,
        "so_dien_thoai": user.so_dien_thoai,
        "gioi_tinh": None,
        "ngay_sinh": None,
        "dan_toc": None,
        "ton_giao": None,
        "tinh_thanh_id": None,
        "khu_vuc_uu_tien_id": None,
        "doi_tuong_uu_tien_id": None,
        "trinh_do_hoc_van": None,
        "suc_khoe_the_chat": None,
        "kha_nang_tai_chinh": None,
    }
    if profile is not None:
        payload.update(
            {
                "gioi_tinh": profile.gioi_tinh if profile.gioi_tinh in (1, 2, 3) else None,
                "ngay_sinh": profile.ngay_sinh,
                "dan_toc": profile.dan_toc,
                "ton_giao": profile.ton_giao,
                "tinh_thanh_id": profile.tinh_thanh_id,
                "khu_vuc_uu_tien_id": profile.khu_vuc_uu_tien_id,
                "doi_tuong_uu_tien_id": profile.doi_tuong_uu_tien_id,
                "trinh_do_hoc_van": _as_block(profile.trinh_do_hoc_van, TrinhDoHocVan),
                "suc_khoe_the_chat": _as_block(profile.suc_khoe_the_chat, SucKhoeTheChat),
                "kha_nang_tai_chinh": _as_block(profile.kha_nang_tai_chinh, KhaNangTaiChinh),
                "edu_coin": profile.edu_coin or 0,
                "xu_he_thong": profile.xu_he_thong or 0,
                "luot_tra_cuu": profile.luot_tra_cuu or 0,
                "luot_hoi_dap": profile.luot_hoi_dap or 0,
                "luot_khao_sat": profile.luot_khao_sat or 0,
                "co_mat_khau_thanh_toan": bool(profile.mat_khau_thanh_toan),
                "created_at": profile.created_at,
                "updated_at": profile.updated_at,
            }
        )
    return HoSoPublic.model_validate(payload)


@router.get("/ho-so", response_model=HoSoPublic)
def get_ho_so(
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user),
) -> HoSoPublic:
    """Lấy toàn bộ hồ sơ của tài khoản đang đăng nhập: thông tin cá nhân, hồ sơ năng lực, Edu coin và số lượt còn lại."""
    profile = _get_profile(db, current_user.id)
    return _to_public(current_user, profile)


def _gan_thong_tin_ca_nhan(db: Session, current_user: NguoiDung, payload: ThongTinCaNhanWrite) -> NguoiDungThongTin:
    """Kiểm tra và gán thông tin cá nhân vào tài khoản/hồ sơ (chưa commit). Trả về bản ghi hồ sơ."""
    if payload.so_dien_thoai:
        taken = db.scalar(
            select(NguoiDung.id).where(
                NguoiDung.so_dien_thoai == payload.so_dien_thoai,
                NguoiDung.id != current_user.id,
            )
        )
        if taken is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Số điện thoại đã được sử dụng",
            )

    if payload.tinh_thanh_id is not None and db.get(DmTinhThanh, payload.tinh_thanh_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy tỉnh thành có id = {payload.tinh_thanh_id}",
        )
    if payload.khu_vuc_uu_tien_id is not None and db.get(DmKhuVucUuTien, payload.khu_vuc_uu_tien_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy khu vực ưu tiên có id = {payload.khu_vuc_uu_tien_id}",
        )
    if payload.doi_tuong_uu_tien_id is not None and db.get(DmDoiTuongUuTien, payload.doi_tuong_uu_tien_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy đối tượng ưu tiên có id = {payload.doi_tuong_uu_tien_id}",
        )

    profile = _get_profile(db, current_user.id)
    if profile is None:
        profile = NguoiDungThongTin(nguoi_dung_id=current_user.id)
        db.add(profile)

    current_user.ho_ten = payload.ho_ten
    current_user.so_dien_thoai = payload.so_dien_thoai
    profile.gioi_tinh = payload.gioi_tinh
    profile.ngay_sinh = payload.ngay_sinh
    profile.dan_toc = payload.dan_toc
    profile.ton_giao = payload.ton_giao
    profile.tinh_thanh_id = payload.tinh_thanh_id
    profile.khu_vuc_uu_tien_id = payload.khu_vuc_uu_tien_id
    profile.doi_tuong_uu_tien_id = payload.doi_tuong_uu_tien_id
    return profile


def _luu(db: Session, current_user: NguoiDung, profile: NguoiDungThongTin) -> HoSoPublic:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Số điện thoại đã được sử dụng",
        ) from None

    db.refresh(current_user)
    db.refresh(profile)
    return _to_public(current_user, profile)


@router.put("/ho-so", response_model=HoSoPublic)
def update_ho_so(
    payload: HoSoWrite,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user),
) -> HoSoPublic:
    """Cập nhật toàn bộ hồ sơ: thông tin cá nhân và hồ sơ năng lực dùng cho phân tích hướng nghiệp."""
    profile = _gan_thong_tin_ca_nhan(db, current_user, payload)
    profile.trinh_do_hoc_van = _dump_block(payload.trinh_do_hoc_van)
    if "suc_khoe_the_chat" in payload.model_fields_set:
        profile.suc_khoe_the_chat = _dump_block(payload.suc_khoe_the_chat)
    if "kha_nang_tai_chinh" in payload.model_fields_set:
        profile.kha_nang_tai_chinh = _dump_block(payload.kha_nang_tai_chinh)
    _dong_bo_ho_so_xet_tuyen(db, profile)
    return _luu(db, current_user, profile)


@router.put("/thong-tin-ca-nhan", response_model=HoSoPublic)
def update_thong_tin_ca_nhan(
    payload: ThongTinCaNhanWrite,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user),
) -> HoSoPublic:
    """Chỉ cập nhật thông tin cá nhân (họ tên, liên hệ, nhân thân, diện ưu tiên); giữ nguyên hồ sơ năng lực."""
    profile = _gan_thong_tin_ca_nhan(db, current_user, payload)
    _dong_bo_ho_so_xet_tuyen(db, profile)
    return _luu(db, current_user, profile)


@router.post("/doi-mat-khau", response_model=DoiMatKhauKetQua)
def doi_mat_khau(
    payload: DoiMatKhauRequest,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user),
) -> DoiMatKhauKetQua:
    """Đổi mật khẩu đăng nhập của tài khoản đang đăng nhập; phải nhập đúng mật khẩu hiện tại."""
    if not verify_password(payload.mat_khau_cu, current_user.mat_khau):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mật khẩu hiện tại không đúng")
    if payload.mat_khau_moi == payload.mat_khau_cu:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu mới phải khác mật khẩu hiện tại",
        )
    current_user.mat_khau = hash_password(payload.mat_khau_moi)
    db.commit()
    return DoiMatKhauKetQua()


def _day_ngay(tu_ngay: date, so_ngay: int, dem: dict[str, dict[date, int]]) -> list[SuDungTheoNgay]:
    """Đủ từng ngày từ `tu_ngay` (ngày không dùng = 0) để biểu đồ không bị hụt cột."""
    return [
        SuDungTheoNgay(
            ngay=ngay,
            tim_truong=dem["tim_truong"].get(ngay, 0),
            khao_sat=dem["khao_sat"].get(ngay, 0),
        )
        for ngay in (tu_ngay + timedelta(days=i) for i in range(so_ngay))
    ]


@router.get("/thong-ke-su-dung", response_model=ThongKeSuDung)
def thong_ke_su_dung(
    so_ngay: int = Query(default=30, ge=7, le=90),
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user),
) -> ThongKeSuDung:
    """Số lượt tìm trường phù hợp (đã tính lượt) và phiên khảo sát theo ngày trong `so_ngay` ngày gần nhất."""
    tu_ngay = date.today() - timedelta(days=so_ngay - 1)

    ngay_tim = func.date(TnLichSuTimTruongPhuHop.ngay_tao)
    tim = db.execute(
        select(ngay_tim, TnLichSuTimTruongPhuHop.loai_luot, func.count())
        .where(
            TnLichSuTimTruongPhuHop.tai_khoan_id == current_user.id,
            TnLichSuTimTruongPhuHop.da_tinh_luot == 1,
            TnLichSuTimTruongPhuHop.ngay_tao >= tu_ngay,
        )
        .group_by(ngay_tim, TnLichSuTimTruongPhuHop.loai_luot)
    ).all()

    ngay_ks = func.date(TnPhienKhaoSat.created_at)
    khao_sat = db.execute(
        select(ngay_ks, func.count())
        .where(TnPhienKhaoSat.nguoi_khao_sat_id == current_user.id, TnPhienKhaoSat.created_at >= tu_ngay)
        .group_by(ngay_ks)
    ).all()

    dem: dict[str, dict[date, int]] = {"tim_truong": {}, "khao_sat": {}}
    theo_loai: dict[str, int] = {}
    for ngay, loai_luot, so in tim:
        dem["tim_truong"][ngay] = dem["tim_truong"].get(ngay, 0) + so
        theo_loai[loai_luot] = theo_loai.get(loai_luot, 0) + so
    for ngay, so in khao_sat:
        dem["khao_sat"][ngay] = so

    return ThongKeSuDung(
        so_ngay=so_ngay,
        theo_ngay=_day_ngay(tu_ngay, so_ngay, dem),
        tong_tim_truong=sum(dem["tim_truong"].values()),
        tim_truong_mien_phi=theo_loai.get("mien_phi", 0),
        tim_truong_tra_phi=theo_loai.get("tra_phi", 0),
        tong_khao_sat=sum(dem["khao_sat"].values()),
    )
