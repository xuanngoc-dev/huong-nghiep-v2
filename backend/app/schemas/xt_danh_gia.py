from datetime import datetime

from pydantic import BaseModel


class LanDanhGiaPublic(BaseModel):
    id: int
    nam_tuyen_sinh: int
    phien_ban_thuat_toan: str
    lich_su_tim_truong_id: int | None = None
    so_phuong_an: int
    so_chuong_trinh: int
    so_truong: int
    thoi_gian_tinh_ms: int | None = None
    # Giả định khi dựng hồ sơ (điểm ước tính, ngân sách...), để giao diện nói rõ kết quả là ước tính ở đâu.
    gia_dinh: list[str] = []
    tao_luc: datetime


class PhuongAnTomTat(BaseModel):
    ma_cong_thuc: str
    ten_cong_thuc: str
    ma_phuong_thuc: str
    kieu_tinh: str
    ma_to_hop: str | None = None


class DiemChuanThamChieu(BaseModel):
    diem: float
    thang_diem: float | None = None
    nam: int | None = None


class TieuChiPhuHop(BaseModel):
    """Điểm 0-100 từng tiêu chí; null = chưa có dữ liệu (không phải 0 điểm)."""

    kha_nang: float | None = None
    nganh: float | None = None
    hoc_phi: float | None = None
    vi_tri: float | None = None


class KhoangHocPhi(BaseModel):
    tu: float | None = None
    den: float | None = None


class KetQuaChuongTrinhPublic(BaseModel):
    thu_hang: int | None = None
    ma_truong: str
    ten_truong: str | None = None
    chuong_trinh_id: int
    ma_xet_tuyen: str | None = None
    ten_chuong_trinh: str
    phuong_an: PhuongAnTomTat
    diem_xet: float | None = None
    thang_diem: float | None = None
    diem_chuan: DiemChuanThamChieu | None = None
    chenh_lech_30: float | None = None
    la_xet_thang: bool
    # Phương án THU_CONG đủ điều kiện: "đủ điều kiện nộp hồ sơ, hệ thống chưa tính điểm".
    chua_tinh_diem: bool
    tieu_chi: TieuChiPhuHop
    diem_phu_hop: float | None = None
    xep_loai: str | None = None
    hoc_phi: KhoangHocPhi | None = None
    ten_tinh: str | None = None


class KetQuaChuongTrinhPage(BaseModel):
    items: list[KetQuaChuongTrinhPublic]
    total: int
    page: int
    page_size: int


class KetQuaTruongPublic(BaseModel):
    ma_truong: str
    ten_truong: str | None = None
    so_chuong_trinh: int
    so_da_cham: int
    so_phu_hop: int
    diem_cao_nhat: float | None = None
    # Trung bình điểm phù hợp của tối đa 3 chương trình tốt nhất của trường.
    diem_truong: float | None = None
    hang_tot_nhat: int


class PhuongAnKetQuaPublic(BaseModel):
    id: int
    ma_cong_thuc: str
    ten_cong_thuc: str
    ma_phuong_thuc: str
    kieu_tinh: str
    ma_to_hop: str | None = None
    thang_diem: float
    diem_goc: float | None = None
    tb_mon: float | None = None
    tong_thpt_to_hop: float | None = None
    diem_cong: float
    diem_uu_tien: float
    diem_xet: float | None = None
    dat_nguong: bool | None = None
    du_dieu_kien: bool
    ly_do_khong_dat: str | None = None
    diem_chuan: DiemChuanThamChieu | None = None
    chenh_lech_30: float | None = None
    chi_tiet: str | None = None
    la_tot_nhat: bool
