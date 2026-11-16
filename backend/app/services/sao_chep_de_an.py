"""Sao chép đề án tuyển sinh sang năm khác (bước 1.5 KE_HOACH_TRIEN_KHAI.md).

Chép đề án và mọi bảng dats_ con theo thứ tự phụ thuộc trong `dats_import._TABLES`, nối lại khóa ngoại
dats_ sang bản ghi mới. Chương trình mới tự điền `ma_xet_tuyen_nam_truoc` từ mã xét tuyển của bản gốc.
Hàm không commit; endpoint gọi commit sau khi chép xong.
"""

from datetime import datetime

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.dats_chuong_trinh_dao_tao import DatsChuongTrinhDaoTao
from app.models.dats_phuong_thuc import DatsPhuongThuc
from app.models.dats_tuyen_sinh import DatsTuyenSinh
from app.services.dats_import import _TABLES

# Khóa ngoại dats_ → bảng được trỏ tới; giá trị cũ được đổi sang id bản ghi mới.
_KHOA_NGOAI_DATS = {
    "de_an_id": "dats_tuyen_sinh",
    "de_an_chuong_trinh_id": "dats_chuong_trinh_dao_tao",
    "de_an_phuong_thuc_id": "dats_phuong_thuc",
    "doi_tuong_du_tuyen_id": "dats_doi_tuong_du_tuyen",
    "co_so_id": "dats_tru_so",
}
_BO_QUA = {"id", "tao_luc", "cap_nhat_luc"}


class SaoChepDeAnError(ValueError):
    """Không sao chép được đề án. Thông điệp dành cho người dùng."""


def ten_de_an_nam_moi(ten: str | None, nam_cu: int, nam_moi: int) -> str | None:
    """Đổi năm trong tên đề án (ví dụ "... năm 2026" → "... năm 2027"); tên không chứa năm thì giữ nguyên."""
    if not ten:
        return ten
    return ten.replace(str(nam_cu), str(nam_moi))


def _ban_sao(model, nguon, now: datetime) -> object:
    moi = model()
    for column in model.__table__.columns:
        if column.name in _BO_QUA:
            continue
        setattr(moi, column.name, getattr(nguon, column.name))
    for ten_cot in ("tao_luc", "cap_nhat_luc"):
        if ten_cot in model.__table__.columns:
            setattr(moi, ten_cot, now)
    return moi


def sao_chep_de_an(
    db: Session, de_an_id: int, nam_tuyen_sinh: int, ten_de_an: str | None = None
) -> tuple[DatsTuyenSinh, dict[str, int]]:
    """Tạo đề án năm `nam_tuyen_sinh` từ đề án `de_an_id`; trả đề án mới và số dòng đã chép theo bảng."""
    goc = db.get(DatsTuyenSinh, de_an_id)
    if goc is None:
        raise SaoChepDeAnError(f"Không tìm thấy đề án tuyển sinh có id = {de_an_id}")
    if nam_tuyen_sinh == goc.nam_tuyen_sinh:
        raise SaoChepDeAnError("Năm tuyển sinh mới phải khác năm của đề án gốc")
    da_co = db.scalar(
        select(DatsTuyenSinh.id).where(
            DatsTuyenSinh.ma_truong == goc.ma_truong, DatsTuyenSinh.nam_tuyen_sinh == nam_tuyen_sinh
        )
    )
    if da_co is not None:
        raise SaoChepDeAnError(
            f"Trường {goc.ma_truong} đã có đề án tuyển sinh năm {nam_tuyen_sinh} (id = {da_co})"
        )

    now = datetime.now()
    moi = _ban_sao(DatsTuyenSinh, goc, now)
    moi.nam_tuyen_sinh = nam_tuyen_sinh
    moi.ten_de_an = (ten_de_an or "").strip() or ten_de_an_nam_moi(goc.ten_de_an, goc.nam_tuyen_sinh, nam_tuyen_sinh)
    moi.de_an_nam_truoc_id = goc.id
    # Đề án mới chưa công bố và quy tắc xét tuyển phải chuẩn hóa lại cho năm mới.
    moi.ngay_cong_bo = None
    moi.trang_thai_xet_tuyen = 0
    db.add(moi)
    db.flush()

    doi_id: dict[str, dict[int, int]] = {"dats_tuyen_sinh": {goc.id: moi.id}}
    chuong_trinh_ids = list(
        db.scalars(select(DatsChuongTrinhDaoTao.id).where(DatsChuongTrinhDaoTao.de_an_id == goc.id))
    )
    phuong_thuc_ids = (
        list(
            db.scalars(
                select(DatsPhuongThuc.id).where(DatsPhuongThuc.de_an_chuong_trinh_id.in_(chuong_trinh_ids))
            )
        )
        if chuong_trinh_ids
        else []
    )
    so_dong: dict[str, int] = {"dats_tuyen_sinh": 1}
    for table, model, _kind in _TABLES:
        if table == "dats_tuyen_sinh":
            continue
        cols = model.__table__.c
        dieu_kien = []
        if "de_an_id" in cols:
            dieu_kien.append(cols.de_an_id == goc.id)
        if "de_an_chuong_trinh_id" in cols and chuong_trinh_ids:
            dieu_kien.append(cols.de_an_chuong_trinh_id.in_(chuong_trinh_ids))
        if "de_an_phuong_thuc_id" in cols and phuong_thuc_ids:
            dieu_kien.append(cols.de_an_phuong_thuc_id.in_(phuong_thuc_ids))
        if not dieu_kien:
            continue
        khoa_chinh = list(model.__table__.primary_key.columns)
        nguon = list(db.scalars(select(model).where(or_(*dieu_kien)).order_by(*khoa_chinh)))
        if not nguon:
            continue
        ban_sao = []
        for dong in nguon:
            ban = _ban_sao(model, dong, now)
            for ten_cot, bang_dich in _KHOA_NGOAI_DATS.items():
                if ten_cot not in cols:
                    continue
                cu = getattr(dong, ten_cot)
                # Khóa trỏ ra ngoài đề án gốc (dữ liệu lỗi) thì bỏ trống thay vì nối nhầm sang đề án cũ.
                setattr(ban, ten_cot, doi_id.get(bang_dich, {}).get(cu) if cu is not None else None)
            if "nam_tuyen_sinh" in cols and dong.nam_tuyen_sinh == goc.nam_tuyen_sinh:
                ban.nam_tuyen_sinh = nam_tuyen_sinh
            if table == "dats_chuong_trinh_dao_tao":
                ban.ma_xet_tuyen_nam_truoc = dong.ma_xet_tuyen
            ban_sao.append(ban)
        db.add_all(ban_sao)
        db.flush()
        # dats_phuong_thuc_to_hop dùng khóa chính ghép, không bảng nào trỏ tới nên không cần bảng đổi id.
        if "id" in cols:
            doi_id[table] = {dong.id: ban.id for dong, ban in zip(nguon, ban_sao, strict=True)}
        so_dong[table] = len(ban_sao)
    return moi, so_dong
