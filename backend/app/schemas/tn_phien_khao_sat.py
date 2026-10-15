from datetime import datetime

from pydantic import BaseModel, Field


class TnPhienCauTraLoiPublic(BaseModel):
    id: int
    noi_dung_cau_tra_loi: str
    diem: int


class TnPhienCauHoiPublic(BaseModel):
    id: int
    loai_cau_hoi_id: int
    ten_loai_cau_hoi: str
    noi_dung_cau_hoi: str
    cau_tra_loi_id: int | None
    cau_tra_loi: list[TnPhienCauTraLoiPublic]


class TnPhienLamBaiPublic(BaseModel):
    ssid: str
    ma_giao_dich: str | None
    cau_hoi: list[TnPhienCauHoiPublic]


class TnPhienTraLoiWrite(BaseModel):
    cau_tra_loi_id: int = Field(..., ge=1)


class TnPhienBuocPublic(BaseModel):
    id: int
    ten: str


class TnPhienDiemHolland(BaseModel):
    ma_nhom: str
    ten_nhom: str
    mo_ta: str | None = None
    diem: int


class TnPhienKetQuaPublic(BaseModel):
    ssid: str
    ma_giao_dich: str | None
    so_cau_hoi: int
    so_da_tra_loi: int
    ma_noi_bat: str
    buoc: list[TnPhienBuocPublic]
    nhom: list[TnPhienDiemHolland]


class TnPhienNganhPhuHopItem(BaseModel):
    ma_nganh: str
    ten_nganh: str
    ma_nhom_nganh: str
    ten_nhom_nganh: str
    ma_holand: list[str]


class TnPhienNganhPhuHopPublic(BaseModel):
    ssid: str
    ma_giao_dich: str | None
    da_xong: bool
    ma_noi_bat: str
    buoc: list[TnPhienBuocPublic]
    nhom: list[TnPhienDiemHolland]
    nganh: list[TnPhienNganhPhuHopItem]


class TnPhienKhaoSatPublic(BaseModel):
    id: int
    ssid: str
    nguoi_khao_sat_id: int | None
    ma_giao_dich: str
    loai_cau_hoi_id: int
    so_cau_hoi: int
    created_at: datetime

    model_config = {"from_attributes": True}
