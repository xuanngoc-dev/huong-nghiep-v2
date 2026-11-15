"""Tạo dữ liệu mẫu cho bảng ht_cau_hinh_goi_cuoc: 5 gói cho mỗi loại áp dụng.

Chạy từ thư mục backend (cần đã chạy migration tạo bảng):

    python -m app.scripts.tao_du_lieu_mau_goi_cuoc

Gói đã có mã trùng thì bỏ qua, nên chạy lại nhiều lần không sinh bản ghi trùng.
"""

from __future__ import annotations

import sys

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.ht_cau_hinh_goi_cuoc import HtCauHinhGoiCuoc

# (mã, tên, loại áp dụng, giá gốc, giá khuyến mãi, lượt gốc, lượt khuyến mãi, trạng thái, ghi chú)
GOI_CUOC_MAU = [
    ("TRA_CUU_5", "Gói tra cứu 5 lượt", "tra_cuu", 10000, None, 5, None, 1, "Gói dùng thử"),
    ("TRA_CUU_10", "Gói tra cứu 10 lượt", "tra_cuu", 20000, 15000, 10, None, 1, "Giảm giá 25%"),
    ("TRA_CUU_20", "Gói tra cứu 20 lượt", "tra_cuu", 35000, 35000, 20, 25, 1, "Tặng thêm 5 lượt"),
    ("TRA_CUU_50", "Gói tra cứu 50 lượt", "tra_cuu", 80000, 60000, 50, 60, 1, "Giảm giá và tặng thêm 10 lượt"),
    ("TRA_CUU_100", "Gói tra cứu 100 lượt", "tra_cuu", 150000, None, 100, None, 0, "Tạm ngừng bán"),
    ("KHAO_SAT_1", "Gói khảo sát 1 lượt", "khao_sat", 29000, None, 1, None, 1, "Một lần làm khảo sát kèm báo cáo"),
    ("KHAO_SAT_3", "Gói khảo sát 3 lượt", "khao_sat", 79000, 69000, 3, None, 1, "Giảm giá 10.000đ"),
    ("KHAO_SAT_5", "Gói khảo sát 5 lượt", "khao_sat", 125000, 99000, 5, 6, 1, "Giảm giá và tặng thêm 1 lượt"),
    ("KHAO_SAT_10", "Gói khảo sát 10 lượt", "khao_sat", 230000, 230000, 10, 12, 1, "Tặng thêm 2 lượt"),
    ("KHAO_SAT_LOP", "Gói khảo sát cho lớp học (40 lượt)", "khao_sat", 800000, 650000, 40, None, 1, "Dành cho giáo viên chủ nhiệm"),
    ("HOI_DAP_20", "Gói hỏi đáp 20 lượt", "hoi_dap", 15000, None, 20, None, 1, "Gói dùng thử"),
    ("HOI_DAP_50", "Gói hỏi đáp 50 lượt", "hoi_dap", 35000, 29000, 50, None, 1, "Giảm giá 6.000đ"),
    ("HOI_DAP_100", "Gói hỏi đáp 100 lượt", "hoi_dap", 60000, 60000, 100, 120, 1, "Tặng thêm 20 lượt"),
    ("HOI_DAP_200", "Gói hỏi đáp 200 lượt", "hoi_dap", 110000, 89000, 200, 250, 1, "Giảm giá và tặng thêm 50 lượt"),
    ("HOI_DAP_500", "Gói hỏi đáp 500 lượt", "hoi_dap", 250000, None, 500, None, 0, "Tạm ngừng bán"),
]


def main() -> int:
    with SessionLocal() as db:
        da_co = set(db.scalars(select(HtCauHinhGoiCuoc.ma_goi_cuoc)).all())
        them = 0
        for ma, ten, loai, gia_goc, gia_km, luot_goc, luot_km, trang_thai, ghi_chu in GOI_CUOC_MAU:
            if ma in da_co:
                print(f"Bỏ qua {ma}: đã có")
                continue
            db.add(
                HtCauHinhGoiCuoc(
                    ma_goi_cuoc=ma,
                    ten_goi_cuoc=ten,
                    loai_ap_dung=loai,
                    gia_goc=gia_goc,
                    gia_khuyen_mai=gia_km,
                    so_luot_nhan_duoc_goc=luot_goc,
                    so_luot_nhan_duoc_khuyen_mai=luot_km,
                    trang_thai=trang_thai,
                    ghi_chu=ghi_chu,
                )
            )
            them += 1
        db.commit()
    print(f"Đã thêm {them}/{len(GOI_CUOC_MAU)} gói cước mẫu")
    return 0


if __name__ == "__main__":
    sys.exit(main())
