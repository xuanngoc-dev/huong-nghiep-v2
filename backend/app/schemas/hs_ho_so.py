"""Hồ sơ xét tuyển (bảng hs_*), dạng gửi / nhận của API. Mọi tham chiếu danh mục dùng mã, không dùng id."""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def _ma(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip().upper()
    return cleaned or None


class _Khoi(BaseModel):
    model_config = ConfigDict(extra="forbid")


class KetQuaNamHocWrite(_Khoi):
    lop: int = Field(..., ge=10, le=12)
    diem_tb_chung: float | None = Field(default=None, ge=0, le=10)
    hoc_luc: int | None = Field(default=None, ge=1, le=4, description="4 Tốt/Giỏi, 3 Khá, 2 Đạt, 1 Chưa đạt")
    ren_luyen: int | None = Field(default=None, ge=1, le=4, description="4 Tốt, 3 Khá, 2 Đạt, 1 Chưa đạt")


class DiemMonWrite(_Khoi):
    ma_mon: str = Field(..., min_length=1, max_length=20)
    nguon_diem: Literal["THI_THPT", "HOC_BA"]
    lop: int = Field(default=0, ge=0, le=12, description="HOC_BA: 10/11/12; THI_THPT: 0")
    hoc_ky: int = Field(default=0, ge=0, le=2, description="0 = cả năm")
    diem: float = Field(..., ge=0, le=10)
    nam: int | None = Field(default=None, ge=2000, le=2100)
    la_du_kien: bool = False

    _chuan_ma = field_validator("ma_mon")(lambda cls, v: _ma(v))

    @model_validator(mode="after")
    def _lop_theo_nguon(self):
        if self.nguon_diem == "THI_THPT" and (self.lop or self.hoc_ky):
            raise ValueError("Điểm thi THPT không có lớp / học kỳ")
        if self.nguon_diem == "HOC_BA" and self.lop not in (10, 11, 12):
            raise ValueError("Điểm học bạ phải thuộc lớp 10, 11 hoặc 12")
        return self


class DiemBaiThiWrite(_Khoi):
    ma_bai_thi: str = Field(..., min_length=1, max_length=50)
    nam_thi: int = Field(..., ge=2000, le=2100)
    dot_thi: str | None = Field(default=None, max_length=30)
    ngay_thi: date | None = None
    diem: float = Field(..., ge=0)
    phan_tu_chon: str | None = Field(default=None, max_length=50)

    _chuan_ma = field_validator("ma_bai_thi")(lambda cls, v: _ma(v))


class ChungChiWrite(_Khoi):
    ma_chung_chi: str = Field(..., min_length=1, max_length=50)
    diem: float | None = Field(default=None, ge=0)
    cap_do: str | None = Field(default=None, max_length=30)
    ngay_cap: date | None = None
    ngay_het_han: date | None = None

    _chuan_ma = field_validator("ma_chung_chi")(lambda cls, v: _ma(v))

    @model_validator(mode="after")
    def _co_ket_qua(self):
        if self.diem is None and not self.cap_do:
            raise ValueError("Chứng chỉ phải có điểm hoặc cấp độ")
        return self


class ThanhTichWrite(_Khoi):
    ma_thanh_tich: str = Field(..., min_length=1, max_length=50)
    ma_mon: str | None = Field(default=None, max_length=20)
    linh_vuc: str | None = Field(default=None, max_length=150)
    muc_giai: Literal[1, 2, 3, 4, 9] = Field(..., description="1 Nhất, 2 Nhì, 3 Ba, 4 Khuyến khích, 9 tham gia")
    nam_dat_giai: int | None = Field(default=None, ge=2000, le=2100)
    lop: int | None = Field(default=None, ge=6, le=12)

    _chuan_ma = field_validator("ma_thanh_tich", "ma_mon")(lambda cls, v: _ma(v))


class MongMuonWrite(_Khoi):
    loai: Literal["NGANH", "NHOM_NGANH", "LINH_VUC", "TINH_THANH", "VUNG_MIEN", "LOAI_HINH_TRUONG"]
    gia_tri: str = Field(..., min_length=1, max_length=100)


class HoSoXetTuyenWrite(_Khoi):
    ten_ho_so: str | None = Field(default=None, max_length=150)
    nam_tot_nghiep: int | None = Field(default=None, ge=2000, le=2100)
    da_tot_nghiep: bool = True
    chuong_trinh_thpt: Literal["GDPT_2018", "GDPT_2006", "NUOC_NGOAI"] = "GDPT_2018"
    he_chuyen: bool = False
    ma_mon_chuyen: str | None = Field(default=None, max_length=20)
    ten_truong_thpt: str | None = Field(default=None, max_length=255)
    ma_tinh: str | None = Field(default=None, max_length=20)
    ma_khu_vuc_uu_tien: str | None = Field(default=None, max_length=20)
    ma_doi_tuong_uu_tien: str | None = Field(default=None, max_length=20)
    ngan_sach_hoc_phi_nam: float | None = Field(default=None, ge=0)
    ket_qua_nam_hoc: list[KetQuaNamHocWrite] = Field(default_factory=list, max_length=3)
    diem_mon: list[DiemMonWrite] = Field(default_factory=list, max_length=300)
    diem_bai_thi: list[DiemBaiThiWrite] = Field(default_factory=list, max_length=30)
    chung_chi: list[ChungChiWrite] = Field(default_factory=list, max_length=30)
    thanh_tich: list[ThanhTichWrite] = Field(default_factory=list, max_length=30)
    mong_muon: list[MongMuonWrite] = Field(default_factory=list, max_length=50)

    _chuan_ma = field_validator("ma_mon_chuyen")(lambda cls, v: _ma(v))

    @model_validator(mode="after")
    def _khong_trung(self):
        lop = [k.lop for k in self.ket_qua_nam_hoc]
        if len(set(lop)) != len(lop):
            raise ValueError("Kết quả năm học bị trùng lớp")
        khoa = [(d.nguon_diem, d.ma_mon, d.lop, d.hoc_ky) for d in self.diem_mon]
        if len(set(khoa)) != len(khoa):
            raise ValueError("Điểm môn bị trùng (cùng nguồn, môn, lớp, học kỳ)")
        mm = [(m.loai, m.gia_tri) for m in self.mong_muon]
        if len(set(mm)) != len(mm):
            raise ValueError("Mong muốn bị trùng")
        if self.he_chuyen is False:
            self.ma_mon_chuyen = None
        return self


class HoSoXetTuyenPublic(HoSoXetTuyenWrite):
    id: int | None = None
    la_ho_so_chinh: bool = True
    # True khi chưa có hồ sơ hs_*: dữ liệu dựng từ hồ sơ năng lực cũ, lưu (PUT) để tạo hồ sơ.
    tu_du_lieu_cu: bool = False
    cap_nhat_luc: datetime | None = None
