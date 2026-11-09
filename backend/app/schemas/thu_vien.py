from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


LoaiThuVien = Literal["thu_muc", "hinh_anh", "video", "nen", "tep"]


class ThuVienItem(BaseModel):
    ten: str
    duong_dan_tuong_doi: str
    loai: LoaiThuVien
    la_thu_muc: bool = False
    kich_thuoc: int | None = None
    duong_dan: str | None = None
    cap_nhat: datetime


class ThuVienTuUrl(BaseModel):
    url: str = Field(min_length=8, max_length=2000)
    thu_muc: str = Field(default="", max_length=500)


class ThuVienTaoThuMuc(BaseModel):
    thu_muc: str = Field(default="", max_length=500)
    ten: str = Field(min_length=1, max_length=180)


class ThuVienDoiTen(BaseModel):
    duong_dan: str = Field(min_length=1, max_length=500)
    ten_moi: str = Field(min_length=1, max_length=180)


class ThuVienNen(BaseModel):
    thu_muc: str = Field(default="", max_length=500)
    danh_sach: list[str] = Field(min_length=1, max_length=200)
    ten_tep: str = Field(min_length=1, max_length=180)


class ThuVienGiaiNen(BaseModel):
    duong_dan: str = Field(min_length=1, max_length=500)


class ThuVienDat(BaseModel):
    danh_sach: list[str] = Field(min_length=1, max_length=200)
    thu_muc_dich: str = Field(default="", max_length=500)


class ThuVienXoaNhieu(BaseModel):
    danh_sach: list[str] = Field(min_length=1, max_length=200)


class ThuVienSoMuc(BaseModel):
    so_muc: int
