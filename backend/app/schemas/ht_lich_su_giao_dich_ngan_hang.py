from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WebhookGiaoDichNganHang(BaseModel):
    """Payload webhook biến động số dư (định dạng SePay)."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: int | str
    gateway: str | None = None
    transaction_date: datetime | None = Field(default=None, alias="transactionDate")
    account_number: str | None = Field(default=None, alias="accountNumber")
    sub_account: str | None = Field(default=None, alias="subAccount")
    code: str | None = None
    content: str | None = None
    transfer_type: Literal["in", "out"] = Field(..., alias="transferType")
    description: str | None = None
    transfer_amount: Decimal = Field(..., ge=0, alias="transferAmount")
    accumulated: Decimal | None = None
    reference_code: str | None = Field(default=None, alias="referenceCode")

    @field_validator("transaction_date", mode="before")
    @classmethod
    def parse_ngay(cls, value):
        # SePay gửi "YYYY-MM-DD HH:MM:SS"; chuỗi rỗng coi như không có.
        if value in (None, ""):
            return None
        return value

    @field_validator("gateway", "account_number", "sub_account", "code", "content", "description", "reference_code")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = str(value).strip()
        return cleaned or None


class WebhookKetQua(BaseModel):
    """Phản hồi cho cổng webhook: SePay coi success=true là đã nhận."""

    success: bool = True
    id: int | None = None
    trung_lap: bool = False
    trang_thai_doi_soat: int | None = None


class GiaoDichNganHangPublic(BaseModel):
    id: int
    ma_giao_dich_cong: str
    ngan_hang: str | None = None
    thoi_gian_giao_dich: datetime | None = None
    so_tai_khoan: str | None = None
    tai_khoan_phu: str | None = None
    ma_thanh_toan: str | None = None
    noi_dung: str | None = None
    loai_giao_dich: str
    mo_ta: str | None = None
    so_tien: int
    so_du_luy_ke: int | None = None
    ma_tham_chieu: str | None = None
    ngan_hang_thanh_toan_id: int | None = None
    lich_su_nap_tien_id: int | None = None
    ma_giao_dich_nap_tien: str | None = None
    trang_thai_doi_soat: int
    ghi_chu_doi_soat: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class GiaoDichNganHangPage(BaseModel):
    items: list[GiaoDichNganHangPublic]
    total: int
    page: int
    page_size: int
