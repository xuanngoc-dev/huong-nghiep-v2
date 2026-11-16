from datetime import datetime
from typing import Any

from pydantic import BaseModel


class XtDoPhuChiSo(BaseModel):
    """Số chương trình có từng loại dữ liệu bộ tính cần (trên tổng số chương trình)."""

    so_chuong_trinh: int = 0
    co_ma_nganh: int = 0
    co_diem_chuan: int = 0
    co_hoc_phi: int = 0
    co_vi_tri: int = 0


class XtDoPhuDeAn(XtDoPhuChiSo):
    de_an_id: int
    ma_truong: str
    ten_truong: str | None = None
    trang_thai_xet_tuyen: int
    so_cong_thuc: int = 0
    lan_import_cuoi: datetime | None = None
    quy_dinh_chua_mo_hinh_hoa: list[dict[str, Any]] = []


class XtDoPhuTong(XtDoPhuChiSo):
    so_de_an: int = 0
    # Khóa "0" chưa chuẩn hóa, "1" thử nghiệm, "2" đang áp dụng.
    theo_trang_thai: dict[str, int] = {}
    so_quy_dinh_chua_mo_hinh_hoa: int = 0


class XtDoPhuPage(BaseModel):
    nam: int
    tong: XtDoPhuTong
    items: list[XtDoPhuDeAn]
    total: int
    page: int
    page_size: int
