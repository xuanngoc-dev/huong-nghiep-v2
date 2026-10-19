from pydantic import BaseModel


class TruongTuyenSinhTomTat(BaseModel):
    ten_tep: str
    ma_truong: str
    ten_truong: str
    loai_hinh: str | None = None
    nam_tuyen_sinh: int | None = None
    so_nganh: int
    so_phuong_thuc: int
    so_ban_ghi_phuong_thuc: int
    hop_le: bool
