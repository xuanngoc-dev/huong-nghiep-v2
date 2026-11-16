"""Nghiệp vụ nạp tiền: sinh mã giao dịch, xác nhận giao dịch, cộng số dư và đối soát giao dịch ngân hàng."""

from __future__ import annotations

import re
import secrets
from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.ht_lich_su_giao_dich_ngan_hang import HtLichSuGiaoDichNganHang
from app.models.ht_lich_su_nap_tien import HtLichSuNapTien
from app.models.nguoi_dung_thong_tin import NguoiDungThongTin

# Mã giao dịch 8 ký tự, ví dụ DH4K9F7Q: tiền tố DH + 4 ký tự thời gian + 2 ký tự ngẫu nhiên.
# - Thời gian: số phút tính từ 01/01/2026, viết hệ 32 (4 ký tự, quay vòng sau khoảng 2 năm).
# - Ngẫu nhiên: 1024 tổ hợp mỗi phút, sinh xong vẫn kiểm tra trùng trong DB.
# Chỉ gồm chữ in hoa/số và bỏ ký tự dễ nhầm (0/O, 1/I) để ngân hàng không cắt bỏ, người dùng không gõ nhầm.
TIEN_TO_MA_GIAO_DICH = "DH"
_KY_TU_MA = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
_SO_KY_TU_THOI_GIAN = 4
_SO_KY_TU_NGAU_NHIEN = 2
_MOC_THOI_GIAN = datetime(2026, 1, 1)
# Tìm chồng lấn (lookahead): chuỗi "DH" ngẫu nhiên trong tên người chuyển không nuốt mất mã thật phía sau.
_MAU_MA = re.compile(
    rf"(?=({TIEN_TO_MA_GIAO_DICH}[{_KY_TU_MA}]{{{_SO_KY_TU_THOI_GIAN + _SO_KY_TU_NGAU_NHIEN}}}))"
)

# Trạng thái ht_lich_su_nap_tien
CHO_THANH_TOAN = 0
THANH_CONG = 1
DA_HUY = 2
THAT_BAI = 3

# Trạng thái đối soát ht_lich_su_giao_dich_ngan_hang
CHUA_KHOP = 0
DA_KHOP = 1
TIEN_RA = 2
THIEU_TIEN = 3

# loai_ap_dung của gói cước -> cột số dư trong nguoi_dung_thong_tin
TRUONG_SO_DU = {
    "edu_coin": "edu_coin",
    "tra_cuu": "luot_tra_cuu",
    "hoi_dap": "luot_hoi_dap",
    "khao_sat": "luot_khao_sat",
}


def _he_32(so: int, do_dai: int) -> str:
    """Viết số nguyên không âm sang hệ 32 bằng bảng ký tự mã, đủ `do_dai` ký tự (cắt phần cao nếu dài hơn)."""
    ky_tu = []
    for _ in range(do_dai):
        so, du = divmod(so, len(_KY_TU_MA))
        ky_tu.append(_KY_TU_MA[du])
    return "".join(reversed(ky_tu))


def tao_ma_giao_dich(db: Session, thoi_diem: datetime | None = None) -> str:
    """Sinh mã giao dịch chưa dùng, ví dụ DH4K9F7Q."""
    phut = int(((thoi_diem or datetime.now()) - _MOC_THOI_GIAN).total_seconds() // 60)
    phan_thoi_gian = _he_32(max(phut, 0), _SO_KY_TU_THOI_GIAN)
    for _ in range(20):
        ngau_nhien = "".join(secrets.choice(_KY_TU_MA) for _ in range(_SO_KY_TU_NGAU_NHIEN))
        ma = TIEN_TO_MA_GIAO_DICH + phan_thoi_gian + ngau_nhien
        if db.scalar(select(HtLichSuNapTien.id).where(HtLichSuNapTien.ma_giao_dich == ma)) is None:
            return ma
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Không sinh được mã giao dịch")


def _rut_gon(text: str | None) -> str:
    """Viết hoa và chỉ giữ chữ/số để so khớp mã trong nội dung chuyển khoản."""
    return re.sub(r"[^0-9A-Z]", "", (text or "").upper())


def tim_ma_giao_dich(*van_ban: str | None) -> list[str]:
    """Tìm các mã giao dịch có trong nội dung chuyển khoản (bỏ khoảng trắng/ký tự đặc biệt ngân hàng chèn vào)."""
    ket_qua: list[str] = []
    for text in van_ban:
        if not text:
            continue
        gon = _rut_gon(text)
        for ma in _MAU_MA.findall(gon):
            if ma not in ket_qua:
                ket_qua.append(ma)
    return ket_qua


def cong_so_du(db: Session, giao_dich: HtLichSuNapTien) -> None:
    """Cộng Edu coin/lượt của giao dịch vào hồ sơ người nạp (tạo hồ sơ nếu chưa có)."""
    truong = TRUONG_SO_DU.get(giao_dich.loai_ap_dung)
    if truong is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Loại áp dụng {giao_dich.loai_ap_dung} không cộng được số dư",
        )
    if giao_dich.nguoi_dung_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Giao dịch {giao_dich.ma_giao_dich} không còn tài khoản người nạp",
        )
    ho_so = db.scalar(
        select(NguoiDungThongTin)
        .where(NguoiDungThongTin.nguoi_dung_id == giao_dich.nguoi_dung_id)
        .with_for_update()
    )
    if ho_so is None:
        ho_so = NguoiDungThongTin(nguoi_dung_id=giao_dich.nguoi_dung_id)
        db.add(ho_so)
        db.flush()
    setattr(ho_so, truong, (getattr(ho_so, truong) or 0) + (giao_dich.so_luot_nhan_duoc or 0))


def xac_nhan_thanh_cong(
    db: Session,
    giao_dich: HtLichSuNapTien,
    *,
    so_tien_thuc_nhan: Decimal | int | None = None,
    ma_tham_chieu: str | None = None,
    nguoi_xac_nhan_id: int | None = None,
    ghi_chu: str | None = None,
) -> HtLichSuNapTien:
    """Chuyển giao dịch đang chờ sang thành công và cộng số dư. Chưa commit."""
    if giao_dich.trang_thai != CHO_THANH_TOAN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Giao dịch {giao_dich.ma_giao_dich} không ở trạng thái chờ thanh toán",
        )
    giao_dich.trang_thai = THANH_CONG
    giao_dich.so_tien_thuc_nhan = so_tien_thuc_nhan if so_tien_thuc_nhan is not None else giao_dich.so_tien_nap
    if ma_tham_chieu:
        giao_dich.ma_tham_chieu_ngan_hang = ma_tham_chieu
    giao_dich.thoi_gian_xac_nhan = datetime.now()
    giao_dich.nguoi_xac_nhan_id = nguoi_xac_nhan_id
    if ghi_chu:
        giao_dich.ghi_chu = ghi_chu
    cong_so_du(db, giao_dich)
    return giao_dich


def doi_soat(db: Session, gd_ngan_hang: HtLichSuGiaoDichNganHang) -> None:
    """Đối soát một khoản tiền vào với giao dịch nạp tiền có mã trong nội dung. Chưa commit.

    Đủ tiền thì xác nhận và cộng số dư; thiếu tiền thì chỉ ghi nhận để admin xử lý.
    """
    if gd_ngan_hang.loai_giao_dich != "in":
        gd_ngan_hang.trang_thai_doi_soat = TIEN_RA
        return

    cac_ma = tim_ma_giao_dich(gd_ngan_hang.ma_thanh_toan, gd_ngan_hang.noi_dung)
    if not cac_ma:
        gd_ngan_hang.trang_thai_doi_soat = CHUA_KHOP
        gd_ngan_hang.ghi_chu_doi_soat = "Nội dung không có mã giao dịch nạp tiền"
        return

    giao_dich = db.scalar(
        select(HtLichSuNapTien)
        .where(HtLichSuNapTien.ma_giao_dich.in_(cac_ma))
        .order_by(HtLichSuNapTien.trang_thai.asc(), HtLichSuNapTien.id.desc())
        .limit(1)
        .with_for_update()
    )
    if giao_dich is None:
        gd_ngan_hang.trang_thai_doi_soat = CHUA_KHOP
        gd_ngan_hang.ghi_chu_doi_soat = f"Không tìm thấy giao dịch nạp tiền có mã = {', '.join(cac_ma)}"
        return

    gd_ngan_hang.lich_su_nap_tien_id = giao_dich.id
    if giao_dich.trang_thai != CHO_THANH_TOAN:
        gd_ngan_hang.trang_thai_doi_soat = CHUA_KHOP
        gd_ngan_hang.ghi_chu_doi_soat = (
            f"Giao dịch {giao_dich.ma_giao_dich} không ở trạng thái chờ thanh toán (trạng thái {giao_dich.trang_thai})"
        )
        return

    so_tien = Decimal(gd_ngan_hang.so_tien or 0)
    if so_tien < Decimal(giao_dich.so_tien_nap):
        gd_ngan_hang.trang_thai_doi_soat = THIEU_TIEN
        gd_ngan_hang.ghi_chu_doi_soat = (
            f"Nhận {so_tien:,.0f}đ, thiếu so với {Decimal(giao_dich.so_tien_nap):,.0f}đ của {giao_dich.ma_giao_dich}"
        )
        giao_dich.so_tien_thuc_nhan = so_tien
        giao_dich.ma_tham_chieu_ngan_hang = gd_ngan_hang.ma_tham_chieu
        return

    if giao_dich.thoi_gian_thanh_toan is None:
        giao_dich.thoi_gian_thanh_toan = gd_ngan_hang.thoi_gian_giao_dich
    xac_nhan_thanh_cong(
        db,
        giao_dich,
        so_tien_thuc_nhan=so_tien,
        ma_tham_chieu=gd_ngan_hang.ma_tham_chieu,
        ghi_chu="Tự động xác nhận qua webhook ngân hàng",
    )
    gd_ngan_hang.trang_thai_doi_soat = DA_KHOP
    gd_ngan_hang.ghi_chu_doi_soat = f"Đã cộng cho giao dịch {giao_dich.ma_giao_dich}"


def kiem_tra_thanh_toan(db: Session, giao_dich: HtLichSuNapTien) -> bool:
    """Tìm khoản tiền vào chưa đối soát khớp giao dịch nạp tiền đang chờ; khớp thì xác nhận và cộng số dư. Chưa commit.

    Khớp khi: loai_giao_dich = in, số tiền bằng đúng số tiền nạp, cột noi_dung chứa mã giao dịch (có thể dính chuỗi
    khác trước/sau, ví dụ "123DH4K9F7Q" hay "DH4K9F7Q DEF") và khoản tiền chưa được dùng cho giao dịch khác. Chỉ xét khoản tiền ghi nhận từ lúc tạo giao dịch (trước đó mã chưa tồn tại).
    """
    if giao_dich.trang_thai != CHO_THANH_TOAN:
        return False
    filters = [
        HtLichSuGiaoDichNganHang.loai_giao_dich == "in",
        HtLichSuGiaoDichNganHang.so_tien == giao_dich.so_tien_nap,
        HtLichSuGiaoDichNganHang.trang_thai_doi_soat != DA_KHOP,
        or_(
            HtLichSuGiaoDichNganHang.lich_su_nap_tien_id.is_(None),
            HtLichSuGiaoDichNganHang.lich_su_nap_tien_id == giao_dich.id,
        ),
    ]
    if giao_dich.created_at is not None:
        filters.append(HtLichSuGiaoDichNganHang.created_at >= giao_dich.created_at)
    ung_vien = db.scalars(
        select(HtLichSuGiaoDichNganHang)
        .where(*filters)
        .order_by(HtLichSuGiaoDichNganHang.id.asc())
        .limit(50)
        .with_for_update()
    ).all()
    # So khớp chuỗi con sau khi bỏ khoảng trắng/ký tự đặc biệt (không dùng LIKE) vì ngân hàng có thể chèn
    # khoảng trắng vào giữa mã.
    ma = _rut_gon(giao_dich.ma_giao_dich)
    gd_ngan_hang = next((gd for gd in ung_vien if ma and ma in _rut_gon(gd.noi_dung)), None)
    if gd_ngan_hang is None:
        return False

    if giao_dich.thoi_gian_thanh_toan is None:
        giao_dich.thoi_gian_thanh_toan = gd_ngan_hang.thoi_gian_giao_dich
    xac_nhan_thanh_cong(
        db,
        giao_dich,
        so_tien_thuc_nhan=Decimal(gd_ngan_hang.so_tien),
        ma_tham_chieu=gd_ngan_hang.ma_tham_chieu,
        ghi_chu="Tự động xác nhận khi kiểm tra thanh toán",
    )
    gd_ngan_hang.lich_su_nap_tien_id = giao_dich.id
    gd_ngan_hang.trang_thai_doi_soat = DA_KHOP
    gd_ngan_hang.ghi_chu_doi_soat = f"Đã cộng cho giao dịch {giao_dich.ma_giao_dich}"
    return True
