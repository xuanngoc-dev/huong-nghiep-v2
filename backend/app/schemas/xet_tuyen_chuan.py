"""Cấu trúc chuẩn quy tắc xét tuyển của một trường, một năm.

Khớp với docs/de-an-tuyen-sinh/chuan_du_lieu/de_an_xet_tuyen.schema.json (phiên bản 1.0): mỗi khối cấm khóa lạ
(`additionalProperties: false`), các điều kiện `allOf` / `oneOf` của schema viết thành `model_validator`.
Sửa schema JSON thì sửa cả file này.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ToanTu = Literal[">=", ">", "=", "<=", "<", "!="]
MaChiSo = Literal[
    "DA_TOT_NGHIEP_THPT",
    "NAM_TOT_NGHIEP",
    "HE_CHUYEN",
    "MON_CHUYEN",
    "TBC_LOP",
    "TBC_MIN_3_NAM",
    "HOC_LUC_LOP",
    "HOC_LUC_MIN_3_NAM",
    "REN_LUYEN_LOP",
    "REN_LUYEN_MIN_3_NAM",
    "DIEM_THI_THPT",
    "DIEM_HOC_BA_TB",
    "DIEM_BAI_THI",
    "DIEM_CHUNG_CHI",
    "CO_CHUNG_CHI",
    "THANH_TICH",
]


class _Khoi(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def _null_la_mac_dinh(cls, data):
        """Ô ghi null mà trường có giá trị mặc định (he_so_nhan, so_le_lam_tron, he_so_mon...) thì dùng mặc định."""
        if not isinstance(data, dict):
            return data
        return {
            k: v
            for k, v in data.items()
            if not (
                v is None
                and k in cls.model_fields
                and not cls.model_fields[k].is_required()
                and cls.model_fields[k].get_default(call_default_factory=True) is not None
            )
        }


class DeAnChuan(_Khoi):
    ten_de_an: str = Field(..., min_length=1)
    so_quyet_dinh: str | None = None
    ngay_cong_bo: str | None = None
    nguon_du_lieu_url: str | None = None
    ghi_chu: str | None = None


class CoSoChuan(_Khoi):
    ma_co_so: str = Field(..., min_length=1)
    ten_co_so: str = Field(..., min_length=1)
    # Trống: chương trình ở cơ sở này lấy tỉnh của trường khi chấm tiêu chí vị trí.
    ma_tinh: str | None = None
    dia_chi: str | None = None
    la_tru_so_chinh: bool = False


class ToHopRiengChuan(_Khoi):
    ma_to_hop: str = Field(..., min_length=1, max_length=20)
    ten_to_hop: str
    vi_tri: list[list[str]] = Field(..., min_length=1)

    @model_validator(mode="after")
    def _vi_tri_khong_rong(self):
        if any(not vi_tri for vi_tri in self.vi_tri):
            raise ValueError("mỗi vị trí phải có ít nhất một môn")
        return self


class MucQuyDoiChuan(_Khoi):
    ma_chung_chi: str | None = None
    ma_bai_thi: str | None = None
    ma_mon_thay_the: str | None = None
    cap_do: str | None = None
    diem_tu: float | None = None
    diem_den: float | None = None
    diem_quy_doi: float
    he_so_noi_suy: float = 0
    dat_nguong: bool = True

    @model_validator(mode="after")
    def _mot_nguon(self):
        if (self.ma_chung_chi is None) == (self.ma_bai_thi is None):
            raise ValueError("mỗi mức khai đúng một trong ma_chung_chi hoặc ma_bai_thi")
        return self


class BangQuyDoiChuan(_Khoi):
    ma_bang: str = Field(..., min_length=1, max_length=50)
    ten_bang: str
    thang_diem_dich: float = Field(..., gt=0)
    ghi_chu: str | None = None
    muc: list[MucQuyDoiChuan] = Field(..., min_length=1)


class DieuKienChuan(_Khoi):
    ma_chi_so: MaChiSo
    khoa: str = ""
    toan_tu: ToanTu
    gia_tri: float
    mo_ta: str | None = None


class NhomDieuKienChuan(_Khoi):
    ma_nhom: str = Field(..., min_length=1, max_length=50)
    ten_nhom: str = Field(..., min_length=1)
    mo_ta: str | None = None
    bat_buoc: bool = True
    ma_cong_thuc: str | None = None
    mot_trong: list[DieuKienChuan] = Field(..., min_length=1)


class HeSoMonChuan(_Khoi):
    ma_mon: str | None = None
    nhom_mon: str | None = None
    he_so: float = Field(..., gt=0)

    @model_validator(mode="after")
    def _mon_hoac_nhom(self):
        if (self.ma_mon is None) == (self.nhom_mon is None):
            raise ValueError("khai đúng một trong ma_mon hoặc nhom_mon")
        return self


class ThanhPhanChuan(_Khoi):
    vi_tri: int = Field(..., ge=1)
    ten_thanh_phan: str | None = None
    loai_nguon: Literal["BAI_THI", "CHUNG_CHI"]
    ma_bai_thi: str | None = None
    ma_bang_quy_doi: str | None = None
    ma_mon: str | None = None
    he_so: float = Field(default=1, gt=0)
    nam_thi_tu: int | None = None
    nam_thi_den: int | None = None
    yeu_cau_phan_tu_chon: str | None = None

    @model_validator(mode="after")
    def _theo_loai_nguon(self):
        if self.loai_nguon == "BAI_THI" and not self.ma_bai_thi:
            raise ValueError("thành phần BAI_THI phải có ma_bai_thi")
        if self.loai_nguon == "CHUNG_CHI" and not self.ma_bang_quy_doi:
            raise ValueError("thành phần CHUNG_CHI phải có ma_bang_quy_doi")
        return self


class CongThucChuan(_Khoi):
    ma_cong_thuc: str = Field(..., min_length=1, max_length=50)
    ten_cong_thuc: str = Field(..., min_length=1)
    # Không khai: "500" (Sử dụng phương thức khác).
    ma_phuong_thuc_cua_bo: str = "500"
    kieu_tinh: Literal["TO_HOP_MON", "THANH_PHAN", "CHI_DIEU_KIEN", "THU_CONG"]
    nguon_diem_mon: Literal["THI_THPT", "HOC_BA"] | None = None
    thay_ngoai_ngu: Literal["KHONG", "DUOC_PHEP", "BAT_BUOC"] = "KHONG"
    ma_bang_quy_doi_ngoai_ngu: str | None = None
    thang_diem: float = Field(..., gt=0)
    he_so_nhan: float = Field(default=1, gt=0)
    nguong_tb_mon: float | None = None
    nguong_thpt_to_hop: float | None = None
    diem_san: float | None = None
    ap_dung_diem_cong: bool = True
    ap_dung_uu_tien: bool = True
    ty_le_diem_cong_toi_da: float = Field(default=0.1, ge=0, le=1)
    so_le_lam_tron: int = Field(default=2, ge=0, le=4)
    mo_ta_cong_thuc: str | None = None
    dang_dung: bool = True
    ghi_chu: str | None = None
    he_so_mon: list[HeSoMonChuan] = []
    thanh_phan: list[ThanhPhanChuan] = []
    dieu_kien: list[NhomDieuKienChuan] = []

    @model_validator(mode="before")
    @classmethod
    def _bo_truong_khong_dung(cls, data):
        """nguon_diem_mon chỉ có nghĩa với TO_HOP_MON; CHI_DIEU_KIEN / THU_CONG không tự tính điểm nên thang_diem mặc định 30;
        ma_phuong_thuc_cua_bo trống thì là phương thức khác (500)."""
        if isinstance(data, dict):
            data = dict(data)
            if data.get("ma_phuong_thuc_cua_bo") == "":
                data.pop("ma_phuong_thuc_cua_bo")
            if data.get("kieu_tinh") != "TO_HOP_MON":
                data.pop("nguon_diem_mon", None)
            if data.get("kieu_tinh") in ("CHI_DIEU_KIEN", "THU_CONG") and data.get("thang_diem") is None:
                data["thang_diem"] = 30
        return data

    @model_validator(mode="after")
    def _theo_kieu_tinh(self):
        if self.kieu_tinh == "TO_HOP_MON" and self.nguon_diem_mon is None:
            raise ValueError("công thức TO_HOP_MON phải có nguon_diem_mon")
        if self.kieu_tinh == "THANH_PHAN" and not self.thanh_phan:
            raise ValueError("công thức THANH_PHAN phải có ít nhất một thanh_phan")
        # CHI_DIEU_KIEN / THU_CONG chưa có nhóm dieu_kien: không chặn import, bước kiểm tra nghiệp vụ cảnh báo
        # (bộ tính bỏ qua công thức không có nhóm điều kiện riêng nên không ai được xét đạt nhầm).
        if self.thay_ngoai_ngu != "KHONG" and not self.ma_bang_quy_doi_ngoai_ngu:
            raise ValueError("thay_ngoai_ngu khác KHONG thì phải có ma_bang_quy_doi_ngoai_ngu")
        return self


class DiemCongChuan(_Khoi):
    ma_cong_thuc: str | None = None
    loai_diem_cong: Literal["DIEM_THUONG", "DIEM_XET_THUONG", "DIEM_KHUYEN_KHICH"]
    nhom_cong: str = Field(..., min_length=1)
    ma_chi_so: MaChiSo
    khoa: str = ""
    toan_tu: ToanTu
    gia_tri: float
    diem_cong: float = Field(..., ge=0, le=3)
    mo_ta: str | None = None


class HocPhiChuan(_Khoi):
    nam_hoc: str | None = None
    hoc_phi_tu: float = Field(..., ge=0)
    hoc_phi_den: float | None = Field(default=None, ge=0)
    ghi_chu: str | None = None


class PhuongAnChuan(_Khoi):
    ma_cong_thuc: str
    to_hop: list[str] = []

    @model_validator(mode="after")
    def _to_hop_khong_lap(self):
        if len(set(self.to_hop)) != len(self.to_hop):
            raise ValueError("to_hop có mã bị lặp")
        return self


class ChuongTrinhChuan(_Khoi):
    ma_chuong_trinh: str = Field(..., min_length=1)
    ma_xet_tuyen: str = Field(..., min_length=1, max_length=20)
    ten_chuong_trinh: str = Field(..., min_length=1)
    ma_nganh: str | None = None
    ma_co_so: str | None = None
    loai_chuong_trinh: str | None = None
    chi_tieu: int | None = Field(default=None, ge=0)
    hoc_phi: HocPhiChuan | None = None
    phuong_an: list[PhuongAnChuan] = Field(..., min_length=1)
    dieu_kien_rieng: list[NhomDieuKienChuan] = []


class DiemChuanChuan(_Khoi):
    nam_tuyen_sinh: int
    ma_xet_tuyen: str
    ten_chuong_trinh: str | None = None
    ma_phuong_thuc_cua_bo: str | None = None
    ma_to_hop: str | None = None
    diem_chuan: float
    thang_diem: float = Field(..., gt=0)
    tieu_chi_phu: str | None = None
    nguon_du_lieu_url: str | None = None


class DeAnXetTuyenChuan(_Khoi):
    phien_ban: Literal["1.0"]
    ma_truong: str = Field(..., min_length=2, max_length=20)
    nam_tuyen_sinh: int = Field(..., ge=2020, le=2100)
    de_an: DeAnChuan
    co_so: list[CoSoChuan] = []
    to_hop_rieng: list[ToHopRiengChuan] = []
    bang_quy_doi: list[BangQuyDoiChuan] = []
    cong_thuc: list[CongThucChuan] = Field(..., min_length=1)
    dieu_kien_chung: list[NhomDieuKienChuan] = []
    diem_cong: list[DiemCongChuan] = []
    chuong_trinh: list[ChuongTrinhChuan] = Field(..., min_length=1)
    diem_chuan: list[DiemChuanChuan] = []
