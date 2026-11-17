"""Xóa loại câu hỏi cùng dữ liệu liên quan: câu hỏi, đáp án và các phiên khảo sát có câu hỏi thuộc loại đó.

Phiên khảo sát bị xóa trọn (mọi câu trả lời của phiên, kể cả câu thuộc loại khác) vì phiên thiếu một phần câu hỏi
không còn cho kết quả đúng. Xóa theo thứ tự con trước cha, không dựa vào ON DELETE CASCADE của CSDL.
"""

from sqlalchemy import delete, distinct, func, or_, select
from sqlalchemy.orm import Session

from app.models.dm_loai_cau_hoi import DmLoaiCauHoi
from app.models.tn_cau_hoi_trac_nghiem import TnCauHoiTracNghiem
from app.models.tn_cau_tra_loi import TnCauTraLoi
from app.models.tn_chi_tiet_tra_loi import TnChiTietTraLoi
from app.models.tn_phien_khao_sat import TnPhienKhaoSat


def _cau_hoi_ids(db: Session, ids: list[int]) -> list[int]:
    return list(db.scalars(select(TnCauHoiTracNghiem.id).where(TnCauHoiTracNghiem.loai_cau_hoi_id.in_(ids))))


def _ssid_lien_quan(db: Session, ids: list[int], cau_hoi_ids: list[int]):
    """Câu lệnh chọn ssid các phiên có câu trả lời thuộc loại / câu hỏi sắp xóa."""
    dieu_kien = [TnChiTietTraLoi.loai_cau_hoi_id.in_(ids)]
    if cau_hoi_ids:
        dieu_kien.append(TnChiTietTraLoi.cau_hoi_id.in_(cau_hoi_ids))
    return select(distinct(TnChiTietTraLoi.ssid)).where(or_(*dieu_kien))


def anh_huong(db: Session, ids: list[int]) -> dict[str, int]:
    """Số bản ghi sẽ bị xóa theo các loại câu hỏi `ids` (id không tồn tại thì bỏ qua)."""
    ids = list(db.scalars(select(DmLoaiCauHoi.id).where(DmLoaiCauHoi.id.in_(ids))))
    if not ids:
        return {"so_loai": 0, "so_cau_hoi": 0, "so_dap_an": 0, "so_phien": 0}
    cau_hoi_ids = _cau_hoi_ids(db, ids)
    so_dap_an = (
        db.scalar(select(func.count()).select_from(TnCauTraLoi).where(TnCauTraLoi.cau_hoi_id.in_(cau_hoi_ids)))
        if cau_hoi_ids
        else 0
    )
    so_phien = db.scalar(select(func.count()).select_from(_ssid_lien_quan(db, ids, cau_hoi_ids).subquery()))
    return {"so_loai": len(ids), "so_cau_hoi": len(cau_hoi_ids), "so_dap_an": so_dap_an or 0, "so_phien": so_phien or 0}


def xoa(db: Session, ids: list[int]) -> int:
    """Xóa loại câu hỏi `ids` cùng câu hỏi, đáp án và phiên khảo sát liên quan. Trả số loại đã xóa; chưa commit."""
    items = list(db.scalars(select(DmLoaiCauHoi).where(DmLoaiCauHoi.id.in_(ids))))
    if not items:
        return 0
    ids = [item.id for item in items]
    cau_hoi_ids = _cau_hoi_ids(db, ids)
    ssids = list(db.scalars(_ssid_lien_quan(db, ids, cau_hoi_ids)))
    if ssids:
        db.execute(delete(TnChiTietTraLoi).where(TnChiTietTraLoi.ssid.in_(ssids)))
        db.execute(delete(TnPhienKhaoSat).where(TnPhienKhaoSat.ssid.in_(ssids)))
    if cau_hoi_ids:
        db.execute(delete(TnCauTraLoi).where(TnCauTraLoi.cau_hoi_id.in_(cau_hoi_ids)))
        db.execute(delete(TnCauHoiTracNghiem).where(TnCauHoiTracNghiem.id.in_(cau_hoi_ids)))
    db.execute(delete(DmLoaiCauHoi).where(DmLoaiCauHoi.id.in_(ids)))
    return len(ids)
