from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ModelChat(BaseModel):
    id: str
    ten: str
    nha_cung_cap: str
    phi: bool
    mo_ta: str
    san_sang: bool
    provider: str = "gemini"


class TaiLieuItem(BaseModel):
    ten: str
    kich_thuoc: int
    cap_nhat: datetime


class TinNhan(BaseModel):
    vai_tro: Literal["user", "bot"]
    noi_dung: str = Field(min_length=1, max_length=4000)


class HoiChatRequest(BaseModel):
    cau_hoi: str = Field(min_length=1, max_length=4000)
    model_id: str = Field(min_length=1, max_length=80)
    lich_su: list[TinNhan] = Field(default_factory=list, max_length=20)


class HoiChatResponse(BaseModel):
    tra_loi: str
    model_id: str
    model_ten: str
    tai_lieu: list[str]
