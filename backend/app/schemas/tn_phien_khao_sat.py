from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.dm_loai_cau_hoi import TieuDeCauTraLoi
from app.schemas.dm_nhom_nghe_di_lam import DmNhomNgheDiLamPublic


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


class TnPhienLoaiCauHoiPublic(BaseModel):
    """Loại câu hỏi có trong phiên: cách hiển thị câu trả lời khi làm bài."""

    id: int
    ten_loai_cau_hoi: str
    # diem_so: bảng chọn mức theo danh_sach_tieu_de_cau_tra_loi; tinh_huong: chọn phương án của từng câu.
    loai_tra_loi: str
    danh_sach_tieu_de_cau_tra_loi: list[TieuDeCauTraLoi] | None = None


class TnPhienLamBaiPublic(BaseModel):
    ssid: str
    ma_giao_dich: str | None
    cau_hoi: list[TnPhienCauHoiPublic]
    # Theo thứ tự làm bài; frontend lấy kiểu trả lời của loại đang làm từ đây.
    loai_cau_hoi: list[TnPhienLoaiCauHoiPublic] = []


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
    mo_ta: str | None = None
    muc_luong_tham_khao: list[dict] | None = None
    thoi_gian_dao_tao: str | None = None
    hinh_anh_mo_ta: str | None = None
    chi_tiet: str | None = None


class TnPhienNganhPhuHopPublic(BaseModel):
    ssid: str
    ma_giao_dich: str | None
    da_xong: bool
    ma_noi_bat: str
    buoc: list[TnPhienBuocPublic]
    nhom: list[TnPhienDiemHolland]
    nganh: list[TnPhienNganhPhuHopItem]


class TnPhienNhomNgheItem(DmNhomNgheDiLamPublic):
    """Nhóm nghề đi làm khớp mã Holland nổi bật; `diem_khop` càng cao càng phù hợp."""

    diem_khop: int
    ma_khop: list[str]


class TnPhienNhomNghePhuHopPublic(BaseModel):
    ssid: str
    ma_giao_dich: str | None
    da_xong: bool
    ma_noi_bat: str
    buoc: list[TnPhienBuocPublic]
    nhom: list[TnPhienDiemHolland]
    nhom_nghe: list[TnPhienNhomNgheItem]


class TnPhienKhaoSatPublic(BaseModel):
    id: int
    ssid: str
    nguoi_khao_sat_id: int | None
    ma_giao_dich: str
    dinh_huong: int | None = None
    loai_cau_hoi_id: int
    so_cau_hoi: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TnPhienLichSuItem(BaseModel):
    id: int
    ssid: str
    ma_giao_dich: str | None
    so_cau_hoi: int
    so_da_tra_loi: int
    da_xong: bool
    loai_cau_hoi_id_tiep: int | None = None
    ma_noi_bat: str
    # Mã định hướng khi làm bài (app/constants/doi_tuong_ap_dung.py); phiên cũ chưa lưu thì null.
    dinh_huong: int | None = None
    created_at: datetime


class TnPhienLichSuPage(BaseModel):
    items: list[TnPhienLichSuItem]
    total: int
    page: int
    page_size: int


class TnPhienQuanTriItem(TnPhienLichSuItem):
    # Phiên của khách (chưa đăng nhập) không có người tham gia.
    nguoi_khao_sat_id: int | None = None
    ho_ten: str | None = None
    email: str | None = None
    so_dien_thoai: str | None = None


class TnPhienQuanTriPage(BaseModel):
    items: list[TnPhienQuanTriItem]
    total: int
    page: int
    page_size: int


class TnPhienDeleteMany(BaseModel):
    ids: list[int] = Field(..., min_length=1, max_length=500)


class TnPhienDeleteManyResult(BaseModel):
    deleted: int
