import hmac
import json
import logging
from typing import Literal

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user
from app.core.config import settings
from app.db.session import get_db
from app.models.ht_lich_su_giao_dich_ngan_hang import HtLichSuGiaoDichNganHang
from app.models.ht_lich_su_nap_tien import HtLichSuNapTien
from app.models.ht_ngan_hang_thanh_toan import HtNganHangThanhToan
from app.schemas.ht_lich_su_giao_dich_ngan_hang import (
    GiaoDichNganHangPage,
    GiaoDichNganHangPublic,
    WebhookGiaoDichNganHang,
    WebhookKetQua,
)
from app.services import nap_tien

logger = logging.getLogger(__name__)

# Admin xem biến động số dư các tài khoản ngân hàng.
router = APIRouter(
    prefix="/he-thong/giao-dich-ngan-hang",
    tags=["he-thong"],
    dependencies=[Depends(get_admin_user)],
)

# Cổng thanh toán (SePay) gọi vào, xác thực bằng API key trong header, không dùng token đăng nhập.
webhook_router = APIRouter(prefix="/webhook", tags=["webhook"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _kiem_tra_api_key(authorization: str | None) -> None:
    """Đặt WEBHOOK_NGAN_HANG_API_KEY thì header phải là "Apikey <khóa>" (SePay) hoặc "Bearer <khóa>".

    Để trống khóa thì bỏ qua xác thực (dùng cho hệ thống test). Môi trường thật phải đặt khóa,
    nếu không ai cũng gửi được giao dịch giả để được cộng số dư.
    """
    khoa = settings.webhook_ngan_hang_api_key
    if not khoa:
        logger.warning("Webhook ngân hàng đang KHÔNG xác thực (chưa đặt WEBHOOK_NGAN_HANG_API_KEY)")
        return
    kieu, _, gia_tri = (authorization or "").strip().partition(" ")
    if kieu.lower() not in ("apikey", "bearer") or not hmac.compare_digest(gia_tri.strip(), khoa):
        # Chỉ ghi kiểu header và độ dài để tra lỗi, không ghi khóa.
        logger.warning(
            "Webhook ngân hàng sai API key: có header=%s, kiểu=%r, độ dài nhận=%d, độ dài cấu hình=%d",
            authorization is not None,
            kieu[:20],
            len(gia_tri.strip()),
            len(khoa),
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key webhook không hợp lệ")


async def _doc_webhook(request: Request) -> WebhookGiaoDichNganHang:
    """Đọc payload webhook dạng JSON, multipart/form-data hoặc x-www-form-urlencoded (SePay cho chọn kiểu gửi).

    Header ghi là form nhưng thân là JSON (như lệnh curl mẫu của SePay) thì vẫn đọc theo JSON.
    """
    raw = await request.body()
    loai = request.headers.get("content-type", "").lower()
    data = None
    if "json" not in loai and ("multipart/form-data" in loai or "x-www-form-urlencoded" in loai):
        try:
            form = await request.form()
            data = {key: value for key, value in form.items() if isinstance(value, str)}
        except Exception:  # noqa: BLE001 - thân không phải form hợp lệ, thử JSON bên dưới
            data = None
    if not data:
        try:
            data = json.loads(raw or b"{}")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dữ liệu webhook không đúng định dạng JSON hoặc form",
            ) from None
    if not isinstance(data, dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dữ liệu webhook phải là một đối tượng")
    try:
        return WebhookGiaoDichNganHang.model_validate(data)
    except ValidationError as error:
        raise RequestValidationError(error.errors()) from None


@webhook_router.post("/giao-dich-ngan-hang", response_model=WebhookKetQua)
def nhan_webhook_giao_dich_ngan_hang(
    payload: WebhookGiaoDichNganHang = Depends(_doc_webhook),
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> WebhookKetQua:
    """Nhận webhook biến động số dư (SePay), lưu vào lịch sử giao dịch ngân hàng và tự đối soát nạp tiền.

    Tiền vào có mã giao dịch nạp tiền (DH + 6 ký tự) trong nội dung và đủ số tiền thì tự xác nhận và cộng số dư.
    Webhook gửi lại cùng `id` không bị lưu trùng. Nhận body JSON, multipart/form-data hoặc x-www-form-urlencoded.
    """
    _kiem_tra_api_key(authorization)
    ma_cong = str(payload.id)
    da_co = db.scalar(
        select(HtLichSuGiaoDichNganHang).where(HtLichSuGiaoDichNganHang.ma_giao_dich_cong == ma_cong)
    )
    if da_co is not None:
        return WebhookKetQua(id=da_co.id, trung_lap=True, trang_thai_doi_soat=da_co.trang_thai_doi_soat)

    ngan_hang_id = None
    if payload.account_number:
        ngan_hang_id = db.scalar(
            select(HtNganHangThanhToan.id)
            .where(HtNganHangThanhToan.so_tai_khoan == payload.account_number)
            .limit(1)
        )
    gd = HtLichSuGiaoDichNganHang(
        ma_giao_dich_cong=ma_cong,
        ngan_hang=payload.gateway,
        thoi_gian_giao_dich=payload.transaction_date,
        so_tai_khoan=payload.account_number,
        tai_khoan_phu=payload.sub_account,
        ma_thanh_toan=payload.code,
        noi_dung=payload.content,
        loai_giao_dich=payload.transfer_type,
        mo_ta=payload.description,
        so_tien=payload.transfer_amount,
        so_du_luy_ke=payload.accumulated,
        ma_tham_chieu=payload.reference_code,
        ngan_hang_thanh_toan_id=ngan_hang_id,
        du_lieu_goc=payload.model_dump(mode="json", by_alias=True),
    )
    db.add(gd)
    nap_tien.doi_soat(db, gd)
    try:
        db.commit()
    except IntegrityError:
        # Hai webhook cùng id đến gần như đồng thời: bản kia đã lưu.
        db.rollback()
        da_co = db.scalar(
            select(HtLichSuGiaoDichNganHang).where(HtLichSuGiaoDichNganHang.ma_giao_dich_cong == ma_cong)
        )
        return WebhookKetQua(
            id=da_co.id if da_co else None,
            trung_lap=True,
            trang_thai_doi_soat=da_co.trang_thai_doi_soat if da_co else None,
        )
    db.refresh(gd)
    logger.info("Webhook ngân hàng %s: %s %s, đối soát %s", ma_cong, gd.loai_giao_dich, gd.so_tien, gd.trang_thai_doi_soat)
    return WebhookKetQua(id=gd.id, trang_thai_doi_soat=gd.trang_thai_doi_soat)


@router.get("", response_model=GiaoDichNganHangPage)
def list_giao_dich_ngan_hang(
    q: str | None = Query(default=None, max_length=255),
    loai_giao_dich: Literal["in", "out"] | None = Query(default=None),
    trang_thai_doi_soat: int | None = Query(default=None, ge=0, le=3),
    so_tai_khoan: str | None = Query(default=None, max_length=50),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> GiaoDichNganHangPage:
    """Lịch sử giao dịch ngân hàng (tiền vào/ra), mới nhất trước.

    Lọc theo từ khóa (nội dung, mô tả, mã thanh toán, mã tham chiếu), loại, trạng thái đối soát và số tài khoản.
    """
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                HtLichSuGiaoDichNganHang.noi_dung.like(pattern, escape="\\"),
                HtLichSuGiaoDichNganHang.mo_ta.like(pattern, escape="\\"),
                HtLichSuGiaoDichNganHang.ma_thanh_toan.like(pattern, escape="\\"),
                HtLichSuGiaoDichNganHang.ma_tham_chieu.like(pattern, escape="\\"),
            )
        )
    if loai_giao_dich:
        filters.append(HtLichSuGiaoDichNganHang.loai_giao_dich == loai_giao_dich)
    if trang_thai_doi_soat is not None:
        filters.append(HtLichSuGiaoDichNganHang.trang_thai_doi_soat == trang_thai_doi_soat)
    if so_tai_khoan and so_tai_khoan.strip():
        filters.append(HtLichSuGiaoDichNganHang.so_tai_khoan == so_tai_khoan.strip())

    count_stmt = select(func.count()).select_from(HtLichSuGiaoDichNganHang)
    stmt = select(HtLichSuGiaoDichNganHang, HtLichSuNapTien.ma_giao_dich).outerjoin(
        HtLichSuNapTien, HtLichSuNapTien.id == HtLichSuGiaoDichNganHang.lich_su_nap_tien_id
    )
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)
    total = db.scalar(count_stmt) or 0
    rows = db.execute(
        stmt.order_by(
            HtLichSuGiaoDichNganHang.thoi_gian_giao_dich.desc(),
            HtLichSuGiaoDichNganHang.id.desc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    items = []
    for gd, ma_nap_tien in rows:
        item = GiaoDichNganHangPublic.model_validate(gd)
        item.ma_giao_dich_nap_tien = ma_nap_tien
        items.append(item)
    return GiaoDichNganHangPage(items=items, total=total, page=page, page_size=page_size)
