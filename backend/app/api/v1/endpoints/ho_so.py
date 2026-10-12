from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.dm_doi_tuong_uu_tien import DmDoiTuongUuTien
from app.models.dm_khu_vuc_uu_tien import DmKhuVucUuTien
from app.models.dm_tinh_thanh import DmTinhThanh
from app.models.nguoi_dung import NguoiDung
from app.models.nguoi_dung_thong_tin import NguoiDungThongTin
from app.schemas.ho_so import HoSoPublic, HoSoWrite, KhaNangTaiChinh, SucKhoeTheChat, TrinhDoHocVan

router = APIRouter(prefix="/tai-khoan", tags=["tai-khoan"])


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
            }
        )
    return HoSoPublic.model_validate(payload)


@router.get("/ho-so", response_model=HoSoPublic)
def get_ho_so(
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user),
) -> HoSoPublic:
    """Lấy hồ sơ cá nhân của tài khoản đang đăng nhập."""
    profile = _get_profile(db, current_user.id)
    return _to_public(current_user, profile)


@router.put("/ho-so", response_model=HoSoPublic)
def update_ho_so(
    payload: HoSoWrite,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user),
) -> HoSoPublic:
    """Cập nhật họ tên, số điện thoại và thông tin cá nhân dùng cho phân tích hướng nghiệp."""
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

    if payload.tinh_thanh_id is not None:
        tinh = db.get(DmTinhThanh, payload.tinh_thanh_id)
        if tinh is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tỉnh thành không tồn tại",
            )
    if payload.khu_vuc_uu_tien_id is not None and db.get(DmKhuVucUuTien, payload.khu_vuc_uu_tien_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Khu vực ưu tiên không tồn tại",
        )
    if payload.doi_tuong_uu_tien_id is not None and db.get(DmDoiTuongUuTien, payload.doi_tuong_uu_tien_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Đối tượng ưu tiên không tồn tại",
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
    profile.trinh_do_hoc_van = _dump_block(payload.trinh_do_hoc_van)
    if "suc_khoe_the_chat" in payload.model_fields_set:
        profile.suc_khoe_the_chat = _dump_block(payload.suc_khoe_the_chat)
    if "kha_nang_tai_chinh" in payload.model_fields_set:
        profile.kha_nang_tai_chinh = _dump_block(payload.kha_nang_tai_chinh)

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
