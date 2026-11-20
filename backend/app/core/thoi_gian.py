"""Thời gian theo múi giờ hệ thống (`TIMEZONE` trong .env, mặc định Asia/Ho_Chi_Minh = UTC+7).

Cột DateTime trong CSDL lưu giờ theo múi giờ này, không kèm offset. Dùng `bay_gio()` / `hom_nay()` thay cho
`datetime.now()` / `date.today()` (vốn theo múi giờ của máy chạy server, trong Docker thường là UTC).
"""

from datetime import date, datetime
from zoneinfo import ZoneInfo

from app.core.config import settings

MUI_GIO = ZoneInfo(settings.timezone)


def bay_gio() -> datetime:
    """Thời điểm hiện tại theo múi giờ hệ thống, không kèm tzinfo (đúng kiểu cột DateTime)."""
    return datetime.now(MUI_GIO).replace(tzinfo=None)


def hom_nay() -> date:
    """Ngày hiện tại theo múi giờ hệ thống."""
    return datetime.now(MUI_GIO).date()


def tu_timestamp(timestamp: float) -> datetime:
    """Đổi Unix timestamp (vd. ngày sửa file) sang giờ hệ thống, không kèm tzinfo."""
    return datetime.fromtimestamp(timestamp, MUI_GIO).replace(tzinfo=None)


def gan_mui_gio(thoi_diem: datetime | None) -> datetime | None:
    """Gắn múi giờ hệ thống cho giá trị đọc từ CSDL (không kèm tzinfo) để trả ra kèm offset."""
    return thoi_diem.replace(tzinfo=MUI_GIO) if thoi_diem else None


def offset_mysql() -> str:
    """Offset hiện tại của múi giờ dạng '+07:00' cho `SET time_zone` (MySQL thường chưa nạp bảng tên múi giờ)."""
    offset = datetime.now(MUI_GIO).strftime("%z")
    return f"{offset[:3]}:{offset[3:]}"
