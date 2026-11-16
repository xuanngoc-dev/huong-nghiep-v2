"""Thao tác chung trên quy tắc xét tuyển (xt_*) và học phí của đề án.

Xóa tường minh theo thứ tự phụ thuộc, không dựa vào ON DELETE CASCADE, để chạy đúng cả trên CSDL không bật khóa
ngoại (SQLite trong test). Hàm không commit.
"""

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models.dats_hoc_phi import DatsHocPhi
from app.models.xt_bang_quy_doi import XtBangQuyDoi, XtBangQuyDoiChiTiet
from app.models.xt_cong_thuc import XtCongThuc, XtCongThucHeSoMon, XtCongThucThanhPhan
from app.models.xt_dieu_kien import XtDiemCong, XtDieuKien, XtNhomDieuKien
from app.models.xt_lich_su_import import XtLichSuImport
from app.models.xt_phuong_an import XtPhuongAn

# Bảng trỏ trực tiếp tới chương trình đào tạo: (model, tên hiển thị khi báo lỗi).
_THAM_CHIEU_CHUONG_TRINH = [
    (XtPhuongAn, "phương án xét tuyển"),
    (XtNhomDieuKien, "nhóm điều kiện"),
    (DatsHocPhi, "dòng học phí"),
]


def delete_quy_tac_xet_tuyen(db: Session, de_an_ids: list[int], *, giu_lich_su: bool = False) -> dict[str, int]:
    """Xóa toàn bộ quy tắc xét tuyển và học phí của các đề án; trả số dòng đã xóa theo bảng.

    `giu_lich_su=True` khi import lại quy tắc: giữ nhật ký các lần import trước.
    """
    if not de_an_ids:
        return {}
    cong_thuc = select(XtCongThuc.id).where(XtCongThuc.de_an_id.in_(de_an_ids))
    nhom = select(XtNhomDieuKien.id).where(XtNhomDieuKien.de_an_id.in_(de_an_ids))
    bang_quy_doi = select(XtBangQuyDoi.id).where(XtBangQuyDoi.de_an_id.in_(de_an_ids))
    buoc = [
        (XtDieuKien, XtDieuKien.nhom_dieu_kien_id.in_(nhom)),
        (XtNhomDieuKien, XtNhomDieuKien.de_an_id.in_(de_an_ids)),
        (XtDiemCong, XtDiemCong.de_an_id.in_(de_an_ids)),
        (XtPhuongAn, XtPhuongAn.de_an_id.in_(de_an_ids)),
        (XtCongThucHeSoMon, XtCongThucHeSoMon.cong_thuc_id.in_(cong_thuc)),
        (XtCongThucThanhPhan, XtCongThucThanhPhan.cong_thuc_id.in_(cong_thuc)),
        (XtCongThuc, XtCongThuc.de_an_id.in_(de_an_ids)),
        (XtBangQuyDoiChiTiet, XtBangQuyDoiChiTiet.bang_quy_doi_id.in_(bang_quy_doi)),
        (XtBangQuyDoi, XtBangQuyDoi.de_an_id.in_(de_an_ids)),
        (DatsHocPhi, DatsHocPhi.de_an_id.in_(de_an_ids)),
    ]
    if not giu_lich_su:
        buoc.append((XtLichSuImport, XtLichSuImport.de_an_id.in_(de_an_ids)))
    da_xoa: dict[str, int] = {}
    for model, dieu_kien in buoc:
        so_dong = db.execute(delete(model).where(dieu_kien).execution_options(synchronize_session=False)).rowcount
        if so_dong:
            da_xoa[model.__tablename__] = so_dong
    return da_xoa


def dem_quy_tac_theo_chuong_trinh(db: Session, chuong_trinh_ids: list[int]) -> dict[int, list[str]]:
    """Với mỗi chương trình đang được quy tắc xét tuyển / học phí tham chiếu: danh sách mô tả "N <loại>"."""
    ket_qua: dict[int, list[str]] = {}
    if not chuong_trinh_ids:
        return ket_qua
    for model, ten in _THAM_CHIEU_CHUONG_TRINH:
        cot = model.__table__.c.de_an_chuong_trinh_id
        for ct_id, so in db.execute(
            select(cot, func.count()).where(cot.in_(chuong_trinh_ids)).group_by(cot)
        ):
            ket_qua.setdefault(ct_id, []).append(f"{so} {ten}")
    return ket_qua
