from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.nguoi_dung import NguoiDung
from app.schemas.auth import AuthResponse, LoginRequest, NguoiDungPublic, RegisterRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    """Đăng ký tài khoản mới và cấp token đăng nhập. Từ chối nếu email hoặc số điện thoại đã được dùng."""
    email = payload.email.lower().strip()

    filters = [NguoiDung.email == email]
    if payload.so_dien_thoai:
        filters.append(NguoiDung.so_dien_thoai == payload.so_dien_thoai)

    existing = db.scalar(select(NguoiDung).where(or_(*filters)))
    if existing:
        if existing.email == email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã được sử dụng",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Số điện thoại đã được sử dụng",
        )

    user = NguoiDung(
        ho_ten=payload.ho_ten,
        email=email,
        so_dien_thoai=payload.so_dien_thoai,
        mat_khau=hash_password(payload.mat_khau),
        vai_tro=0,
        trang_thai=1,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    return AuthResponse(access_token=token, user=NguoiDungPublic.model_validate(user))


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    """Đăng nhập bằng email và mật khẩu, trả về token. Từ chối nếu sai thông tin hoặc tài khoản bị khóa."""
    email = payload.email.lower().strip()
    user = db.scalar(select(NguoiDung).where(NguoiDung.email == email))

    if user is None or not verify_password(payload.mat_khau, user.mat_khau):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không đúng",
        )
    if user.trang_thai != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị khóa",
        )

    token = create_access_token(user.id)
    return AuthResponse(access_token=token, user=NguoiDungPublic.model_validate(user))


@router.get("/me", response_model=NguoiDungPublic)
def me(current_user: NguoiDung = Depends(get_current_user)) -> NguoiDungPublic:
    """Trả về thông tin tài khoản đang đăng nhập."""
    return NguoiDungPublic.model_validate(current_user)
